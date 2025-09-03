import os
import re
import json
import unicodedata
from pathlib import Path
from typing import List

# ========== CONFIG ==========
IN_DIR    = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt_clean"
OUT_JSON  = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones_sentences.json"

# Umbrales
HARD_MAX_TOKENS   = 50   # si una frase supera esto, la partimos
MIN_SENT_TOKENS   = 4     # si una frase tiene <= 3 tokens, se une con la siguiente

# Tu lista de pares titulo-autor (tal cual la has dado)
RAW_TITLE_AUTHOR = [
    "Al outru llau de la raya-Lliteratura popular oral de Llión y Zamora.txt - Nicolás Bartolomé Pérez",
    "Caldu de berzas ya outras comedias - Francisco González-Banfi González",
    "Cartas al fichu Correspondencia d’Eva González - Eva González",
    "Cordillera Asturllionesa - David Gallinar Cañedo",
    "Cousas d´en Ca Trones - Guadalupe Lorenzana",
    "El Llumbreiru - Furmientu",
    "El Color - Juan Abad",
    "Estudiu histórico-etimolóxicu de la toponimia mayor del términu municipal d’Ordás - Fernando Álvarez-Balbuena García",
    "Las figuras de las cantaderas y de la sotadera nas antiguas fiestas de l'Asunción de la ciudá de Llión - Nicolás Bartolomé Pérez",
    "Cuentos en dialecto leonés - C. A. Bardón",
    "Llingua y lliteratura en Llion - Nicolás Bartolomé Pérez",
    "Los rexímenes xurídico-lingüísticos del asturllionés - Nicolás Bartolomé Pérez",
    "Pizarro al amo - Iván Cuevas",
    "L’universu míticu de los Llioneses - Nicolás Bartolomé Pérez",
    "Mitoloxia popular del Reinu de Llión - Nicolás Bartolomé Pérez",
    "Na frontera del asturllionés y el gallegoportugués - Fernando Álvarez-Balbuena García",
    "La Fueya Rota - Xairu López",
    "Los Reis de Llión.txt - Ricardo Chao Prieto",
    "Solombras de los Nuesos Valles - Silvia Aller González",
]
# ===========================

# -------- utilidades de normalización --------
LAT = r"A-Za-zÀ-ÖØ-öø-ÿĀ-ſ"  # letras latinas extendidas

def nfc(s: str) -> str:
    return unicodedata.normalize("NFC", s)

def normalize_quotes_and_hyphens(s: str) -> str:
    repl = {
        "’": "'", "´": "'", "‘": "'", "“": '"', "”": '"',
        "–": "-", "—": "-", "−": "-",
        "\xa0": " ",
    }
    for a, b in repl.items():
        s = s.replace(a, b)
    s = re.sub(r"\s*-\s*", "-", s)      # " A - B " -> "A-B"
    s = re.sub(r"\s{2,}", " ", s).strip()
    return s

def strip_txt(s: str) -> str:
    return re.sub(r"\.txt\s*$", "", s, flags=re.IGNORECASE)

def norm_title_key(s: str) -> str:
    s = nfc(s)
    s = strip_txt(s)
    s = normalize_quotes_and_hyphens(s)
    return s.lower()

def build_title_author_map(rows: List[str]) -> dict:
    mapping = {}
    for row in rows:
        if " - " in row:
            t, a = row.split(" - ", 1)
        else:
            parts = row.rsplit("-", 1)
            t = parts[0].strip()
            a = parts[1].strip() if len(parts) > 1 else ""
        mapping[norm_title_key(t)] = a.strip()
    return mapping

TITLE2AUTHOR = build_title_author_map(RAW_TITLE_AUTHOR)

def file_title(file_name: str) -> str:
    base = os.path.splitext(file_name)[0]
    return nfc(normalize_quotes_and_hyphens(base))

def match_author_for_title(title: str) -> str:
    return TITLE2AUTHOR.get(norm_title_key(title), "")

# -------- helpers de texto --------
def count_tokens(text: str) -> int:
    # tokens ≈ palabras separadas por espacios
    return len(re.findall(r"\S+", text, flags=re.UNICODE))

def normalize_whitespace(s: str) -> str:
    # quita tabs/newlines y colapsa espacios -> así no aparecen \n ni \t en JSON
    s = s.replace("\r\n", " ").replace("\r", " ").replace("\n", " ").replace("\t", " ")
    s = re.sub(r"\s{2,}", " ", s)
    return s.strip()

def split_sentences_robust(text: str) -> List[str]:
    """
    Divide en frases usando . ? ! como finales de frase SOLO si hay ≥2 letras antes del signo.
    Permite cierres como ” » ' ) ] después del signo.
    Evita cortar 'D.' (de 'Don'), etc. (1 letra + punto).
    También une frases demasiado cortas con la siguiente y trocea las muy largas.
    """
    # Normaliza: fuera saltos/tabs, elipsis → punto, colapsa espacios
    t = text.replace("…", ".")
    t = t.replace("\r\n", "\n").replace("\r", "\n")
    t = re.sub(r"[ \t]*\n[ \t]*", " ", t)
    t = re.sub(r"\s{2,}", " ", t).strip()

    # Patrón de frase: cualquier cosa mínima hasta un final válido:
    #   - al menos 2 letras antes del signo final
    #   - signo final [.?!]
    #   - opcionales cierres de comillas/paréntesis
    # seguido de espacio(s) o final de texto (lookahead de anchura fija)
    pattern = re.compile(
        rf"""(?P<sent>.*?               # contenido mínimo
              [{LAT}]{{2}}              # ≥2 letras antes del final
              [\.!?]                    # signo final
              (?:["»'\)\]]*)            # cierres opcionales
             )
             (?=\s+|$)                  # y luego espacio(s) o fin de texto
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
    # Añade posible resto (si no terminó en signo final "válido")
    tail = t[pos:].strip()
    if tail:
        sents.append(tail)

    # Une frases demasiado cortas con la siguiente
    merged: List[str] = []
    i = 0
    while i < len(sents):
        s = sents[i]
        if len(re.findall(r"\S+", s)) < MIN_SENT_TOKENS and i + 1 < len(sents):
            s = f"{s} {sents[i+1]}"
            i += 2
        else:
            i += 1
        merged.append(s.strip())

    # Subdivide las muy largas por , ; : y, en último caso, por nº de tokens
    final: List[str] = []
    for s in merged:
        if len(re.findall(r"\S+", s)) <= HARD_MAX_TOKENS:
            final.append(s)
        else:
            parts = re.split(r"(?<=[,;:])\s+", s)
            buf, btok = [], 0
            for piece in parts:
                pt = len(re.findall(r"\S+", piece))
                if btok + pt <= HARD_MAX_TOKENS:
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
                            while words and len(take) < HARD_MAX_TOKENS:
                                take.append(words.pop(0))
                            final.append(" ".join(take))
            if buf:
                final.append(" ".join(buf).strip())

    # Normaliza espacios y elimina \n \t (no deben aparecer en JSON)
    final = [re.sub(r"\s{2,}", " ", s.replace("\n", " ").replace("\t", " ")).strip()
             for s in final if s.strip()]
    return final


# ------------- principal -------------
def build_json_sentences(in_dir: str, out_json: str):
    in_path = Path(in_dir)
    out_path = Path(out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    missing_authors = []

    for p in sorted(in_path.glob("*.txt")):
        raw = p.read_text(encoding="utf-8", errors="ignore")
        if not raw or not raw.strip():
            continue

        title = file_title(p.name)
        author = match_author_for_title(title)
        if not author:
            missing_authors.append(p.name)

        sentences = split_sentences_robust(raw)

        meta = {"title": title, "author": author or ""}

        for s in sentences:
            records.append({"metadata": meta, "text": s})

    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    if missing_authors:
        print("⚠ No se encontró author para (revisa el título del archivo):")
        for name in missing_authors:
            print("  -", name)
    else:
        print("✔ Todos los títulos encontraron author.")
    print(f"✔ JSON generado en: {out_json}")

if __name__ == "__main__":
    build_json_sentences(IN_DIR, OUT_JSON)
