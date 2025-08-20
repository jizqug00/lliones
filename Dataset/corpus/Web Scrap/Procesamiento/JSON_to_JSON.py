# concatena_fuentes_a_corpus_y_exporta_nuevos.py
import json
import re
import unicodedata
from pathlib import Path
from typing import List, Dict

# ====== RUTAS (AJUSTA) ======
BASE_JSON   = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones_chunks.json"        # JSON base ya creado
OUT_JSON    = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones.json"        # base + añadidos
OUT_ADDED_JSON = r"C:\Users\usuario\Desktop\Corpus\Documentos\nuevos_registros_fuentes.json"       # SOLO añadidos (para revisión)

ARTICULOS_GQ = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\articulos_gonzalez_quevedo.json"
LEYENDAS     = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\leyendas_leonesas.json"
FUEYU_1      = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias_el_fueyu_1.json"
FUEYU_2      = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias_el_fueyu_2.json"
NOTICIAS     = r"C:\Users\usuario\Desktop\Corpus\Documentos\json\noticias.json"

# ====== SEGMENTACIÓN ======
TARGET_TOKENS    = 150   # objetivo aprox. por chunk
HARD_MAX_TOKENS  = 250   # techo duro por chunk

# ====== UTILIDADES ======
def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def clean_text_basic(text: str) -> str:
    """Quita URLs, emails, ()[], normaliza espacios/saltos."""
    text = nfc(text).replace("\xa0", " ")
    text = re.sub(r"https?://\S+|www\.\S+", "", text, flags=re.IGNORECASE)  # URLs
    text = re.sub(r"[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Za-z]{2,}", "", text)  # emails
    for _ in range(3):  # () y []
        text = re.sub(r"\([^()]*\)", "", text, flags=re.DOTALL)
        text = re.sub(r"\[[^\[\]]*\]", "", text, flags=re.DOTALL)
    text = re.sub(r"[ \t]+", " ", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    return text.strip()

def sentence_split(s: str) -> List[str]:
    s = re.sub(r"\s*\n\s*", " ", s.strip())
    parts = re.split(r"(?<=[\.\?!¡¿])\s+", s)
    return [p.strip() for p in parts if p.strip()]

def count_tokens(s: str) -> int:
    return len(re.findall(r"\S+", s, flags=re.UNICODE))

def split_paragraphs(text: str) -> List[str]:
    text = re.sub(r"\n{3,}", "\n\n", text)
    return [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]

def smart_chunk(paragraphs: List[str], target=TARGET_TOKENS, hard_max=HARD_MAX_TOKENS) -> List[str]:
    chunks, cur, cur_tok = [], [], 0
    def flush():
        nonlocal cur, cur_tok
        if cur:
            chunks.append("\n\n".join(cur).strip())
            cur, cur_tok = [], 0
    for para in paragraphs:
        ptok = count_tokens(para)
        if ptok > hard_max:
            flush()
            sents = sentence_split(para)
            buf, btok = [], 0
            for s in sents:
                stok = count_tokens(s)
                if stok > hard_max:
                    parts = re.split(r"(?<=[,;:])\s+", s)
                    sbuf, sbtok = [], 0
                    for piece in parts:
                        pt = count_tokens(piece)
                        if sbtok + pt <= hard_max:
                            sbuf.append(piece); sbtok += pt
                        else:
                            if sbuf:
                                chunks.append(" ".join(sbuf).strip()); sbuf, sbtok = [piece], pt
                            else:
                                words = piece.split()
                                while words:
                                    take = []
                                    while words and len(take) < hard_max:
                                        take.append(words.pop(0))
                                    chunks.append(" ".join(take))
                    if sbuf:
                        chunks.append(" ".join(sbuf).strip())
                    buf, btok = [], 0
                else:
                    if btok + stok <= hard_max:
                        buf.append(s); btok += stok
                    else:
                        chunks.append(" ".join(buf).strip()); buf, btok = [s], stok
            if buf:
                chunks.append(" ".join(buf).strip())
            continue
        if cur_tok + ptok <= target or not cur:
            cur.append(para); cur_tok += ptok
        else:
            flush(); cur.append(para); cur_tok = ptok
    flush()
    return [c for c in chunks if c]

def titlecase_from_slug(slug: str) -> str:
    s = slug.replace("-", " ").replace("_", " ")
    s = re.sub(r"\s{2,}", " ", s).strip()
    return " ".join(w[:1].upper() + w[1:] if w else w for w in s.split(" "))

def drop_sentences_with_phrases(text: str, phrases_ci: List[str]) -> str:
    sents = sentence_split(text)
    keep = []
    for sent in sents:
        low = sent.lower()
        if any(ph.lower() in low for ph in phrases_ci):
            continue
        keep.append(sent)
    return " ".join(keep).strip()

# ====== TRANSFORMADORES DE FUENTE → RECORDS ======
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
        chunks = smart_chunk(split_paragraphs(texto))
        meta   = {"titulo": titulo, "autor": "Roberto González-Quevedo"}
        out.extend({"metadatos": meta, "text": c} for c in chunks)
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
        chunks = smart_chunk(split_paragraphs(texto))
        meta   = {"titulo": titulo, "autor": "Pallabreiru Lliones"}
        out.extend({"metadatos": meta, "text": c} for c in chunks)
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
        chunks = smart_chunk(split_paragraphs(texto))
        meta   = {"titulo": titulo, "autor": "El Fueyu"}
        out.extend({"metadatos": meta, "text": c} for c in chunks)
    return out

def records_noticias_faceira(path: str) -> List[Dict]:
    data = json.loads(Path(path).read_text(encoding="utf-8"))
    out = []
    items = data.values() if isinstance(data, dict) else data
    for it in items:
        titulo = it.get("titulo", "").strip()
        cont   = it.get("contenido", "").strip()
        if not titulo or not cont:
            continue
        texto  = clean_text_basic(cont)
        chunks = smart_chunk(split_paragraphs(texto))
        meta   = {"titulo": titulo, "autor": "Faceira"}
        out.extend({"metadatos": meta, "text": c} for c in chunks)
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

    # 2a) Guarda SOLO añadidos en OUT_ADDED_JSON
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
