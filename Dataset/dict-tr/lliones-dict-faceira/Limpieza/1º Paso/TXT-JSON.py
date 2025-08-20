import re
import json

# Cargar el diccionario como texto
with open("diccionario_limpio_O.txt", "r", encoding="utf-8") as f:
    texto = f.read()

# Lista de abreviaturas (más largas primero para evitar que 'm.' capture antes que 'm. y f.')
abreviaturas = [
    "\[ks\]", "\|\|", "\| \|", "loc\\. prep\\.", "m\\. y f\\.", "loc\\.",  # más largas primero
    "adv\\.", "apóc\\.", "art\\.", "aum\\.", "adx\\.", "cond\\.", "con\\.", "contr\\.",
    "dem\\.", "dim\\.", "excl\\.", "f\\.", "fam\\.", "fig\\.", "imp\\.", "indef\\.",
    "interr\\.", "interx\\.", "m\\.", "n\\.", "num\\.", "part\\.", "per\\.", "pl\\.",
    "pos\\.", "prep\\.", "pro\\.", "prnl\\.", "rel\\.", "sing\\.", "v\\.", "t\\."
]
abreviatura_regex = r"(?<!\w)(?:" + "|".join(abreviaturas) + r")(?!\w)"

abreviaturas_ = [
    "\[ks\]", "loc\\. prep\\.", "m\\. y f\\.", "loc\\.",  # más largas primero
    "adv\\.", "apóc\\.", "art\\.", "aum\\.", "adx\\.", "cond\\.", "con\\.", "contr\\.",
    "dem\\.", "dim\\.", "excl\\.", "f\\.", "fam\\.", "fig\\.", "imp\\.", "indef\\.",
    "interr\\.", "interx\\.", "m\\.", "n\\.", "num\\.", "part\\.", "per\\.", "pl\\.",
    "pos\\.", "prep\\.", "pro\\.", "prnl\\.", "rel\\.", "sing\\.", "v\\.", "t\\."
]
abreviatura_regex_ = r"(?<!\w)(?:" + "|".join(abreviaturas_) + r")(?!\w)"


# Regex para entrada: palabra + abreviatura
entrada_regex = re.compile(
    rf"^([a-zA-ZáéíóúÁÉÍÓÚñÑ'?,\-]+(?:, *-[a-zA-Záéíóúñ]+)?)\s+({abreviatura_regex})", 
    re.MULTILINE
)

# Expandidor de variantes tipo 'cuartu, -ta'
def expandir_variantes(palabra):
    match = re.match(r"^([a-zA-ZáéíóúÁÉÍÓÚñÑ]+),\s*-([a-zA-ZáéíóúÁÉÍÓÚñÑ]+)$", palabra.strip())
    if match:
        base, terminacion = match.groups()
        if len(terminacion) > 2:
            return [base]
        if base[-1] in "aeiouáéíóú":
            nueva = base[:-2] + terminacion
        else:
            nueva = base[:-1] + terminacion
        return [base, nueva]
    return [palabra.strip()]

# Buscar todas las coincidencias
coincidencias = list(entrada_regex.finditer(texto))
resultados = []

for i, match in enumerate(coincidencias):
    palabra_raw = match.group(1).strip().replace("1", "'").replace("2", "?")
    inicio = match.end()
    fin = coincidencias[i + 1].start() if i + 1 < len(coincidencias) else len(texto)
    definicion = texto[inicio:fin].strip().replace("\n", " ")

    # Filtrar definiciones inválidas
    if definicion.startswith("V.") and len(definicion.split()) <= 3:
        continue

    letra_actual = palabra_raw[0].lower()
    if i + 1 < len(coincidencias):
        siguiente_letra = coincidencias[i + 1].group(1).strip()[0].lower()
        if ord(siguiente_letra) > ord(letra_actual) + 1:
            continue

    palabra_raw = re.sub(r"[!?']", "", palabra_raw).strip()
    palabras = expandir_variantes(palabra_raw)
    
    # Eliminar abreviaturas gramaticales de la definición (solo si están aisladas)
    definicion = re.sub(abreviatura_regex_, "", definicion).strip()
    definicion = re.sub(r'\s+', ' ', definicion)  # Limpiar espacios extra

    # Reemplazar " - " y " -." por la palabra correspondiente
    for palabra in palabras:
        definicion = re.sub(r"\s-\s", f" {palabra} ", definicion)
        definicion = re.sub(r"\s-\.", f" {palabra}.", definicion)
        definicion = re.sub(r"\s-\,", f" {palabra}.", definicion)
        definicion = re.sub(r"\s-\!", f" {palabra}.", definicion)
        resultados.append({
            "palabra": palabra,
            "definicion": definicion
        })

# Guardar JSON
with open("diccionario_limpio.json", "w", encoding="utf-8") as f:
    json.dump(resultados, f, ensure_ascii=False, indent=2)

print(f"✅ Se han procesado {len(resultados)} entradas limpias (sin abreviaturas gramaticales, y las secuencias ' - ' reemplazadas por la palabra correspondiente).")
