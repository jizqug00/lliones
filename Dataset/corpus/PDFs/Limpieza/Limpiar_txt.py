# limpiar_carpeta_txt_v3_fix.py
# Limpieza robusta para TXT de corpus (asturleonés / leonés)

import re
from pathlib import Path

# ====== RUTAS (ajústalas) ======
CARPETA_IN  = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt\2Column_PyMuPDF"
CARPETA_OUT = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt_clean"
ENCODING    = "utf-8"

# ====== PARÁMETROS ======
MIN_BLANKS_BEFORE_TITLE = 1   # "\n\nTítulo" => 1 línea en blanco antes del título
TITLE_MAX_WORDS  = 8
TITLE_MAX_CHARS  = 70

HEADWORDS = {
    "introducción","presentación","prólogo","prólogu","resumen","abstract",
    "conclusiones","conclusión","apéndice","bibliografía","agradecimientos",
    "entamu"
}

LAT = r"A-Za-zÀ-ÖØ-öø-ÿĀ-ſ"  # letras latinas extendidas

# ---------- UTILIDADES ----------
def dehyphenate_linebreaks(text: str) -> str:
    text = text.replace("\u00ad", "").replace("\u2010", "-").replace("\u2011", "-")
    return re.sub(rf"([{LAT}0-9])[­\-]\s*\n\s*([{LAT}])", r"\1\2", text)

def remove_brackets(text: str) -> str:
    for _ in range(3):
        text = re.sub(r"\([^)]*\)", "", text, flags=re.DOTALL)
        text = re.sub(r"\[[^\]]*\]", "", text, flags=re.DOTALL)
    text = re.sub(r"\[\s*…\s*\]", "", text)
    return text

def remove_star_blocks(text: str) -> str:
    # * ... hasta '.\n' (o '.' al final de archivo)
    pat = re.compile(r"(?ms)^\s*\*[ \t].*?(?:\.(?=\s*\n)|\.\s*$)")
    prev = None
    while prev != text:
        prev = text
        text = re.sub(pat, "\n", text)
    return text

def remove_page_markers_and_meta(text: str) -> str:
    # Primero limpiamos paginación y metadatos (antes de tocar notas numeradas)
    rules = [
        r"(?m)^\s*[—–\-]*\s*\d+\s*[—–\-]*\s*$",          # — 7 — / - 12 -
        r"(?m)^\s*[\d\s\|/\\\-–—]+\s*$",                 # 46|47 / 12-13 / 24
        r"(?mi)^(?=.*\b(ISSN|DOI|RFA|páx\.|págs?\.|http|www))\s*.+$",
        r"(?mi)^\s*(©|\(c\)|creative commons|cc by|orcid|doi:).*$",
    ]
    for p in rules:
        text = re.sub(p, "", text)
    # Líneas con " … - 25" (borra la línea entera)
    text = re.sub(r"(?m)^[^\n]*\s[—\-–]\s*\d+\s*$", "", text)
    return text

def remove_numbered_blocks(text: str) -> str:
    """
    Notas/referencias que empiezan con número y **texto en la misma línea**,
    hasta el primer '.\\n' (admite varias líneas intermedias).
    - Importante: usamos [ \\t]+ (no \\s+) tras el número, y exigimos [^\\n] a continuación.
    """
    pat = re.compile(r"(?ms)^[ \t]*\d+[ \t]+[^\n].*?(?:\.(?=\s*\n)|\.\s*$)")
    prev = None
    while prev != text:
        prev = text
        text = re.sub(pat, "\n", text)
    return text

def remove_all_numbers(text: str) -> str:
    # Ordinales
    text = re.sub(r"\b\d+[ºª]\b", "", text)
    text = re.sub(r"\b\d+\.\s*[ºª]\b", "", text)
    # Años 1200–2099
    text = re.sub(r"\b(1[2-9]\d{2}|20\d{2})\b", "", text)
    # Números sueltos 1–6 cifras
    text = re.sub(r"\b\d{1,6}\b", "", text)
    # Dígitos pegados (incl. superíndices)
    text = re.sub(rf"(?<=[{LAT}])[\d¹²³⁴⁵⁶⁷⁸⁹]+", "", text)
    # Formatos con separadores
    text = re.sub(r"\b\d{1,3}(?:[.,]\d{3})+(?:[.,]\d+)?\b", "", text)
    return text

def looks_title_like(s: str) -> bool:
    if len(s) > TITLE_MAX_CHARS or s.endswith("."):
        return False
    tokens = [t for t in re.split(r"\s+", s) if t]
    if len(tokens) <= 1:
        return s.strip("«»\"'¡!?.:;—–-").lower() in HEADWORDS
    if len(tokens) <= TITLE_MAX_WORDS:
        if re.search(r"(^|[\s—\-:])([ivxlcdmIVXLCDM]+)([\s—\-:]|$)", s):
            return True
        joiners = {"de","del","la","el","los","las","y","a","en","por","con","da","do","das","dos","di","du"}
        sig = [t for t in tokens if t.lower() not in joiners]
        if sig:
            cap = sum(1 for t in sig if t[:1].isupper())
            if cap / len(sig) >= 0.6:
                return True
        letters = re.findall(rf"[{LAT}]", s)
        uppers  = [c for c in letters if c.upper() == c and c.lower() != c]
        if letters and len(uppers)/len(letters) >= 0.6:
            return True
    return False

def remove_titles_with_context(text: str) -> str:
    """
    Elimina líneas que 'parecen título' SOLO si están precedidas
    por ≥ MIN_BLANKS_BEFORE_TITLE líneas en blanco (p. ej., \\n\\nTítulo).
    """
    lines = text.splitlines()
    out = []
    blank_streak = 0

    for ln in lines:
        s = ln.strip()

        if s == "":
            out.append(ln)
            blank_streak += 1
            continue

        should_remove = False

        if re.fullmatch(r"(?i)\s*entamu(\s+[ivxlcdm]+)?\s*", s):
            should_remove = True
        elif looks_title_like(s):
            should_remove = True
        else:
            letters = re.findall(rf"[{LAT}]", s)
            uppers  = [c for c in letters if c.upper() == c and c.lower() != c]
            if letters and len(uppers)/len(letters) >= 0.6 and re.search(r"\b\d+\s*$", s):
                should_remove = True

        if should_remove and blank_streak >= MIN_BLANKS_BEFORE_TITLE:
            # borrar título
            pass
        else:
            out.append(ln)

        blank_streak = 0

    return "\n".join(out)

def strip_dialogue_speaker_prefix(text: str) -> str:
    # Quita nombre de personaje al inicio de línea seguido de — / - / :
    pat = re.compile(rf"(?m)^\s*[«“\"'(\[]*[{LAT}][{LAT}\.'’´`\-·]*\s*[—\-:]\s*")
    return re.sub(pat, "", text)

def normalize_punct_and_space(text: str) -> str:
    text = text.replace("…", ".")
    text = re.sub(r"\.{2,}", ".", text)
    text = re.sub(r"([!?])\1+", r"\1", text)
    text = re.sub(r"\s+([,;:.!?])", r"\1", text)
    text = re.sub(r"[ \t]{2,}", " ", text)
    text = re.sub(r"[ \t]+\n", "\n", text)
    text = re.sub(r"\n{3,}", "\n\n", text)
    return text.strip()

# ---------- PIPELINE ----------
def clean_text(raw: str) -> str:
    t = raw.replace("\r\n", "\n").replace("\r", "\n")

    # 1) Cortes por guion
    t = dehyphenate_linebreaks(t)

    # 2) Cabeceras/pies/meta (antes de tocar notas numeradas)
    t = remove_page_markers_and_meta(t)

    # 3) Bloques (* ... y n ... hasta '.\n')
    t = remove_star_blocks(t)
    t = remove_numbered_blocks(t)

    # 4) Paréntesis/corchetes
    t = remove_brackets(t)

    # 5) Números (años, sueltos, pegados)
    t = remove_all_numbers(t)

    # 6) Títulos SOLO si hay ≥1 línea en blanco antes
    t = remove_titles_with_context(t)

    # 7) Si queda línea terminada en guion (paginación rota), elimínala
    t = re.sub(r"(?m)^[^\n]*[—\-–]\s*$", "", t)

    # 8) Diálogos: quitar “nombre—”
    t = strip_dialogue_speaker_prefix(t)

    # 9) Normalización final
    t = normalize_punct_and_space(t)
    return t + "\n"

# ---------- LOTE POR CARPETA ----------
def process_folder(in_dir: str, out_dir: str) -> None:
    in_path  = Path(in_dir)
    out_path = Path(out_dir)
    out_path.mkdir(parents=True, exist_ok=True)
    for p in sorted(in_path.glob("*.txt")):
        raw = p.read_text(encoding=ENCODING, errors="ignore")
        cleaned = clean_text(raw)
        (out_path / p.name).write_text(cleaned, encoding=ENCODING)
        print(f"✔ {p.name} → limpio")

# --------- EJECUCIÓN ---------
if __name__ == "__main__":
    process_folder(CARPETA_IN, CARPETA_OUT)
