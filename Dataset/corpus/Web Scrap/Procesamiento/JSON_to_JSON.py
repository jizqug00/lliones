# concatena_fuentes_a_corpus_y_exporta_nuevos_SENTENCES.py
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict

# ====== RUTAS (AJUSTA) ======
BASE_JSON       = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones_sentences.json"  # JSON base (sentences)
OUT_JSON        = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones.json"            # base + añadidos
OUT_ADDED_JSON  = r"C:\Users\usuario\Desktop\Corpus\Documentos\nuevos_registros_fuentes.json"       # SOLO añadidos

ARTICULOS_GQ = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\articulos_gonzalez_quevedo.json"
LEYENDAS     = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\leyendas_leonesas.json"
FUEYU_1      = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias_el_fueyu_1.json"
FUEYU_2      = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias_el_fueyu_2.json"
NOTICIAS     = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias.json"

# ====== SEGMENTACIÓN (FRÁSES) ======
HARD_MAX_SENT_TOKENS = 50   # techo duro por frase tras limpieza
MIN_SENT_TOKENS      = 4    # si una frase tiene ≤ 3 tokens, se une con la siguiente

LAT = r"A-Za-zÀ-ÖØ-öø-ÿĀ-ſ"  # letras latinas extendidas

# ====== UTILIDADES ======
def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def normalize_punct_spacing(s: str) -> str:
    # Asegura espacio tras coma/; si falta
    s = re.sub(r",(?=\S)", ", ", s)
    s = re.sub(r";(?=\S)", "; ", s)
    return s

def clean_text_basic(text: str) -> str:
    """Quita URLs, emails, ()[], normaliza espacios y evita \\n \\t en salida (NO cambia l.l)."""
    text = nfc(text).replace("\xa0", " ")
    # URLs y correos
    text = re.sub(r"https?://\S+|www\.\S+", "", text, flags=re.IGNORECASE)
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", text)
    # Paréntesis/corchetes (varias pasadas simples)
    for _ in range(3):
        text = re.sub(r"\([^()]*\)", "", text, flags=re.DOTALL)
        text = re.sub(r"\[[^\[\]]*\]", "", text, flags=re.DOTALL)
    # Espaciado tras , ;
    text = normalize_punct_spacing(text)
    # Quita saltos/tabs y colapsa espacios
    text = text.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    text = re.sub(r"\s{2,}", " ", text)
    return text.strip()

def count_tokens(s: str) -> int:
    return len(re.findall(r"\S+", s, flags=re.UNICODE))

def split_sentences_robust(text: str) -> List[str]:
    """
    Divide en frases usando . ? ! como finales de frase SOLO si hay ≥2 letras antes del signo.
    Permite cierres como ” » ' ) ] después del signo. Une frases cortas y trocea largas.
    """
    # Normaliza y prepara
    t = text.replace("…", ".")
    t = re.sub(r"\s{2,}", " ", t).strip()

    # Captura frases con ≥2 letras antes del signo final [.?!] + posibles cierres de comillas
    pattern = re.compile(
        rf"""(?P<sent>.*?
              [{LAT}]{{2}}           # al menos 2 letras antes del signo
              [\.!?]                 # signo final
              (?:["»'\)\]]*)         # cierres opcionales
             )
             (?=\s+|$)               # seguido de espacio(s) o fin
        """,
        re.VERBOSE
    )

    sents: List[str] = []
    pos = 0
    for m in pattern.finditer(t):
        s = m.group("sent").strip()
        if s:
            sents.append(s)
        pos = m.end()
    tail = t[pos:].strip()
    if tail:
        sents.append(tail)

    # Une frases demasiado cortas con la siguiente
    merged: List[str] = []
    i = 0
    while i < len(sents):
        s = sents[i]
        if count_tokens(s) < MIN_SENT_TOKENS and i + 1 < len(sents):
            s = f"{s} {sents[i+1]}"
            i += 2
        else:
            i += 1
        merged.append(s.strip())

    # Subdivide las muy largas por , ; : y, si hace falta, por nº de tokens
    final: List[str] = []
    for s in merged:
        if count_tokens(s) <= HARD_MAX_SENT_TOKENS:
            final.append(s)
        else:
            parts = re.split(r"(?<=[,;:])\s+", s)
            buf, btok = [], 0
            for piece in parts:
                pt = count_tokens(piece)
                if btok + pt <= HARD_MAX_SENT_TOKENS:
                    buf.append(piece); btok += pt
                else:
                    if buf:
                        final.append(" ".join(buf).strip())
                        buf, btok = [piece], pt
                    else:
                        # Corte duro por tokens
                        words = piece.split()
                        while words:
                            take = []
                            while words and len(take) < HARD_MAX_SENT_TOKENS:
                                take.append(words.pop(0))
                            final.append(" ".join(take))
            if buf:
                final.append(" ".join(buf).strip())

    # Sin \n ni \t y espacios colapsados
    final = [re.sub(r"\s{2,}", " ", s.replace("\n", " ").replace("\t", " ")).strip()
             for s in final if s.strip()]
    return final

def titlecase_from_slug(slug: str) -> str:
    s = slug.replace("-", " ").replace("_", " ")
    s = re.sub(r"\s{2,}", " ", s).strip()
    return " ".join(w[:1].upper() + w[1:] if w else w for w in s.split(" "))

def drop_sentences_with_phrases(text: str, phrases_ci: List[str]) -> str:
    """Elimina frases completas que contengan cualquiera de las frases indicadas (case-insensitive)."""
    sents = split_sentences_robust(text)
    keep = []
    for sent in sents:
        low = sent.lower()
        if any(ph.lower() in low for ph in phrases_ci):
            continue
        keep.append(sent)
    return " ".join(keep).strip()

# ====== TRANSFORMADORES DE FUENTE → RECORDS (A FRASES) ======
def records_articulos_gq(path: str) -> List[Dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    for url, item in data.items():
        titulo_slug = item.get("titulo", "").strip()
        contenido   = item.get("contenido", "").strip()
        if not contenido:
            continue
        titulo = titlecase_from_slug(titulo_slug) if titulo_slug else titlecase_from_slug(Path(url).stem)
        texto  = clean_text_basic(contenido)
        sents  = split_sentences_robust(texto)
        meta   = {"title": titulo, "author": "Roberto González-Quevedo"}
        out.extend({"metadata": meta, "text": s} for s in sents)
    return out

def records_leyendas(path: str) -> List[Dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    items = data.values() if isinstance(data, dict) else data
    for it in items:
        titulo = it.get("titulo", "").strip()
        desc   = it.get("descripcion", "").strip()
        if not titulo or not desc:
            continue
        texto  = clean_text_basic(desc)
        sents  = split_sentences_robust(texto)
        meta   = {"title": titulo, "author": "Pallabreiru Lliones"}
        out.extend({"metadata": meta, "text": s} for s in sents)
    return out

def records_fueyu(path: str, extra_filter=False) -> List[Dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    items = data.values() if isinstance(data, dict) else data
    for it in items:
        titulo = it.get("titulo", "").strip()
        cont   = it.get("contenido", "").strip()
        if not titulo or not cont:
            continue
        texto = clean_text_basic(cont)
        if extra_filter:
            texto = drop_sentences_with_phrases(
                texto,
                phrases_ci=["Diario de León", "Crónica El Mundo", "La Crónica El Mundo"]
            )
            texto = clean_text_basic(texto)
        sents = split_sentences_robust(texto)
        meta  = {"title": titulo, "author": "El Fueyu"}
        out.extend({"metadata": meta, "text": s} for s in sents)
    return out

def records_noticias_faceira(path: str) -> List[Dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out: List[Dict] = []
    items = data.values() if isinstance(data, dict) else data
    for it in items:
        if not isinstance(it, dict):
            continue
        titulo = (it.get("titulo") or "").strip()
        cont   = (it.get("contenido") or "").strip()
        if not titulo or not cont:
            continue
        texto = clean_text_basic(cont)
        sents = split_sentences_robust(texto)
        meta  = {"title": titulo, "author": "Faceira"}
        out.extend({"metadata": meta, "text": s} for s in sents)
        # si prefieres lista explícita:
        # out.extend([{"metadata": meta, "text": s} for s in sents])
    return out

# ====== MAIN ======
def main():
    # 1) Carga base (si existe)
    base = []
    base_path = Path(BASE_JSON)
    if base_path.exists():
        base = json.loads(base_path.read_text(encoding="utf-8"))
        if not isinstance(base, list):
            raise ValueError("El JSON base no es un array de objetos.")
    else:
        print("⚠ Aviso: JSON base no existe; se creará desde cero.")

    # 2) Genera añadidos (y guárdalos también por separado)
    added = []
    added += records_articulos_gq(ARTICULOS_GQ)
    added += records_leyendas(LEYENDAS)
    added += records_fueyu(FUEYU_1, extra_filter=False)
    added += records_fueyu(FUEYU_2, extra_filter=True)   # con filtro de frases
    added += records_noticias_faceira(NOTICIAS)

    # 2a) Guarda SOLO añadidos
    Path(OUT_ADDED_JSON).write_text(json.dumps(added, ensure_ascii=False, indent=2), encoding="utf-8")

    # 3) Concatena con base y guarda OUT_JSON
    total_before = len(base)
    base.extend(added)
    total_after = len(base)

    Path(OUT_JSON).write_text(json.dumps(base, ensure_ascii=False, indent=2), encoding="utf-8")

    print(f"✔ Añadidos generados: {len(added)} objetos")
    print(f"✔ Guardado SOLO añadidos en: {OUT_ADDED_JSON}")
    print(f"✔ Base tenía: {total_before} objetos")
    print(f"✔ Total tras concatenar: {total_after} objetos")
    print(f"✔ Guardado base+añadidos en: {OUT_JSON}")

if __name__ == "__main__":
    main()
