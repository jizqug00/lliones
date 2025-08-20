import os
import re
import json
import unicodedata
from pathlib import Path
from typing import List

# ========== CONFIG ==========
IN_DIR    = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt_clean"
OUT_JSON  = r"C:\Users\usuario\Desktop\Corpus\Documentos\corpus_asturlliones_chunks.json"

# Objetivo aproximado de tokens por chunk (palabras)
TARGET_TOKENS     = 150
HARD_MAX_TOKENS   = 250   # nunca superar este techo
SENTENCE_SOFT_MAX = 100   # si una frase sola supera esto, intentaremos subdividirla

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

# ------------- segmentación -------------
def count_tokens(text: str) -> int:
    # Aproximación: tokens = palabras separadas por espacios
    return len(re.findall(r"\S+", text, flags=re.UNICODE))

def split_paragraphs(text: str) -> List[str]:
    """
    Divide por doble salto (\n\n+) — esto ya cubre ".\n\n".
    Conserva el punto final con el párrafo anterior.
    """
    text = re.sub(r"\n{3,}", "\n\n", text)
    parts = [p.strip() for p in re.split(r"\n\s*\n", text) if p.strip()]
    return parts

def split_sentences(paragraph: str) -> List[str]:
    """
    Divide un párrafo en frases por signos fuertes. Conserva el delimitador con la frase.
    """
    tmp = re.sub(r"\s*\n\s*", " ", paragraph.strip())
    pieces = re.split(r"(?<=[\.\?!¡¿])\s+", tmp)
    return [p.strip() for p in pieces if p.strip()]

def smart_chunk(paragraphs: List[str],
                target_tokens: int = TARGET_TOKENS,
                hard_max: int = HARD_MAX_TOKENS) -> List[str]:
    """
    Agrupa párrafos en bloques ~target_tokens.
    Si un párrafo excede hard_max, lo parte por frases; si una frase sigue enorme,
    intenta cortar por comas/;/: y, en último caso, por nº de tokens.
    """
    chunks = []
    cur: List[str] = []
    cur_tok = 0

    def flush():
        nonlocal cur, cur_tok
        if cur:
            chunks.append("\n\n".join(cur).strip())
            cur, cur_tok = [], 0

    for para in paragraphs:
        ptok = count_tokens(para)

        if ptok > hard_max:
            # cerrar bloque actual si tiene algo
            flush()
            # subdividir el párrafo grande
            sents = split_sentences(para)
            buff: List[str] = []
            btok = 0
            for s in sents:
                stok = count_tokens(s)
                if stok > hard_max:
                    # cortar por comas/;/: cerca del tamaño objetivo
                    parts = re.split(r"(?<=[,;:])\s+", s)
                    sbuf, sbtok = [], 0
                    for piece in parts:
                        pt = count_tokens(piece)
                        if sbtok + pt <= hard_max:
                            sbuf.append(piece)
                            sbtok += pt
                        else:
                            if sbuf:
                                chunks.append(" ".join(sbuf).strip())
                                sbuf, sbtok = [piece], pt
                            else:
                                # corte duro por tokens
                                words = piece.split()
                                while words:
                                    take = []
                                    while words and len(take) < hard_max:
                                        take.append(words.pop(0))
                                    chunks.append(" ".join(take))
                    if sbuf:
                        chunks.append(" ".join(sbuf).strip())
                    buff, btok = [], 0
                else:
                    if btok + stok <= hard_max:
                        buff.append(s)
                        btok += stok
                    else:
                        chunks.append(" ".join(buff).strip())
                        buff, btok = [s], stok
            if buff:
                chunks.append(" ".join(buff).strip())
            continue

        # si cabe en el bloque actual
        if cur_tok + ptok <= target_tokens or not cur:
            cur.append(para)
            cur_tok += ptok
        else:
            flush()
            cur.append(para)
            cur_tok = ptok

    flush()
    return [c.strip() for c in chunks if c.strip()]

# ------------- principal -------------
def build_json_flat(in_dir: str, out_json: str):
    in_path = Path(in_dir)
    out_path = Path(out_json)
    out_path.parent.mkdir(parents=True, exist_ok=True)

    records = []
    missing_authors = []

    for p in sorted(in_path.glob("*.txt")):
        raw = p.read_text(encoding="utf-8", errors="ignore").strip()
        if not raw:
            continue

        titulo = file_title(p.name)
        autor  = match_author_for_title(titulo)
        if not autor:
            missing_authors.append(p.name)

        paras  = split_paragraphs(raw)
        chunks = smart_chunk(paras, TARGET_TOKENS, HARD_MAX_TOKENS)

        meta = {"titulo": titulo, "autor": autor or ""}

        for chunk in chunks:
            records.append({"metadatos": meta, "text": chunk})

    # Guarda como un JSON (array de objetos), cada objeto = 1 chunk independiente
    with out_path.open("w", encoding="utf-8") as f:
        json.dump(records, f, ensure_ascii=False, indent=2)

    if missing_authors:
        print("⚠ No se encontró autor para (revisa el título del archivo):")
        for name in missing_authors:
            print("  -", name)
    else:
        print("✔ Todos los títulos encontraron autor.")
    print(f"✔ JSON generado en: {out_json}")

if __name__ == "__main__":
    build_json_flat(IN_DIR, OUT_JSON)
