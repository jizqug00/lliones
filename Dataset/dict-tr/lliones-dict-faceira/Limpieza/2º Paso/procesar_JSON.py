import json
import re

# Cargar el archivo
with open('diccionario_limpio_2Column.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Diccionario de familias semánticas
familias = {
    "AGR.": "Agricultura",
    "ANAT.": "Anatomía",
    "ARQUIT.": "Arquitectura",
    "ASTROL.": "Astroloxía / Astrología",
    "ASTRON.": "Astronomía",
    "BIOL.": "Bioloxía / Biología",
    "BOT.": "Botánica",
    "CONSTR.": "Construcción",
    "CONSU.": "Dereitu consuetudinariu / Derecho consuetudinario",
    "DEP.": "Deportes",
    "DER.": "Dereitu / Derecho",
    "ENTOM.": "Entomoloxía / Entomología",
    "FILOS.": "Filosofía",
    "FÍS.": "Física",
    "GAN.": "Ganadería",
    "GASTR.": "Gastronomía",
    "ICT.": "Ictioloxía / Ictiología",
    "INFORM.": "Informática",
    "LING.": "Lingüística",
    "MAT.": "Matemáticas",
    "MED.": "Medicina",
    "MIL.": "Militar",
    "MIN.": "Minería / Mineraloxía / Mineralogía",
    "MIT.": "Mitoloxía / Mitología",
    "MÚS.": "Música",
    "METEO.": "Meteoroloxía / Meteorología",
    "ORNIT.": "Ornitoloxía / Ornitología",
    "POL.": "Política",
    "QUÍM.": "Química",
    "REL.": "Relixón / Religión",
    "TEC.": "Tecnoloxía / Tecnología",
    "TELECOM.": "Telecomunicaciones",
    "ZOOL.": "Zooloxía / Zoología"
}

# Compilar patrón para familias semánticas (respetando puntos)
familia_pattern = re.compile(r'(' + '|'.join(re.escape(k) for k in familias.keys()) + r')', re.IGNORECASE)

# Patrón para refranes (mejorado para capturar también los que no están en línea nueva)
import re

refran_pattern = re.compile(
    r'(?:\|\|\s|\|\s\||\|\s\s\|)\s*((?:.|\n)*?\.(?:\s|\n)+(?:.|\n)*?\.(?:\s|\n|$))',
    re.DOTALL
)


def limpiar_familias(texto):
    for abrev, familia in familias.items():
        if abrev in texto:
            texto = texto.replace(abrev, '')
    return texto.strip()

def procesar_definicion(definicion):
    resultado = {
        "acepciones": [],
        "sinonimos": [],
        "antonimos": [],
        "referencias": [],
        "familias_semanticas": [],
        "dichos": []
    }

    familias_detectadas = set()
    acepciones = []

    # Extraer sinónimos
    match_vs = re.search(r"VS\. ([^\.]+)", definicion)
    if match_vs:
        resultado["sinonimos"] = [s.strip() for s in match_vs.group(1).split(",")]

    # Extraer antónimos
    match_an = re.search(r"\sAN\. ([^\.]+)", definicion)
    if match_an:
        resultado["antonimos"] = [a.strip() for a in match_an.group(1).split(",")]

    # Extraer referencias (V. y RE.)
    match_v = re.findall(r"\b(V\.|RE\.) ([^\.\/]+)", definicion)
    if match_v:
        resultado["referencias"] = [v[1].strip() for v in match_v]

    # Extraer refranes
    refranes = refran_pattern.findall(definicion)
    refranes_limpios = [limpiar_familias(r.replace('\n', ' ')).strip(" .") for r in refranes if r.strip()]
    resultado["dichos"] = refranes_limpios

    # Eliminar etiquetas y refranes del texto
    # Eliminar etiquetas y su texto hasta el primer punto
    definicion = re.sub(r"\s(VS\.|AN\.|OB\.|RE\.|V\.)\s.*?\.", "", definicion)
    definicion = refran_pattern.sub('', definicion)

    # Separar acepciones si hay numeración
    partes = re.split(r"\s*(\d+\.)\s*", definicion)
    if len(partes) > 1:
        i = 1
        while i < len(partes) - 1:
            texto = partes[i + 1].strip().strip(".")
            if texto:
                acepciones.append(texto)
            i += 2
    else:
        acepciones = [definicion.strip().strip(".")]

    # Extraer familias semánticas y limpiarlas de las acepciones
    acepciones_limpias = []
    for acepcion in acepciones:
        detected_familias = familia_pattern.findall(acepcion)
        for abreviatura in detected_familias:
            familias_detectadas.add(familias[abreviatura.upper()])
            acepcion = acepcion.replace(abreviatura, '').strip()
        acepciones_limpias.append(acepcion)

    # Eliminar duplicados
    resultado["acepciones"] = list(dict.fromkeys([re.sub(r'\s+', ' ', a).strip() for a in acepciones_limpias]))
    resultado["familias_semanticas"] = sorted(familias_detectadas)

    return resultado

# Procesar todo
resultado_final = []
for entrada in data:
    palabra = entrada["palabra"]
    definicion = entrada["definicion"]
    procesada = procesar_definicion(definicion)
    resultado_final.append({
        "palabra": palabra,
        **procesada
    })

# Guardar
with open('diccionario_leones_procesado_2Column.json', 'w', encoding='utf-8') as f:
    json.dump(resultado_final, f, ensure_ascii=False, indent=2)

print("✅ Diccionario procesado con refranes mejor detectados y sin familias semánticas en ellos.")
