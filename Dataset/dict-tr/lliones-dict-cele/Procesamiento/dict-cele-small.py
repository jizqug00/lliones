import json
import re
import random

# Cargar datos originales
with open("diccionario_sin_zonas.json", "r", encoding="utf-8") as f:
    datos = json.load(f)

pares = []

# Plantillas para las preguntas
plantillas_pregunta = [
    "¿Qué significa el término leonés {palabra}?",
    "¿Cuál es el significado de la palabra leonesa {palabra}?",
    "¿Qué quiere decir el vocablo leonés {palabra}?",
    "¿A qué se refiere la palabra leonesa {palabra}?",
    "Explícame el significado de la palabra leonesa {palabra}.",
]

# Plantillas para las respuestas
plantillas_respuesta = [
    "La palabra leonesa {palabra} significa {definicion}.",
    "{palabra} es un término leonés que significa {definicion}.",
    "En el leonés, la palabra {palabra} se entiende como {definicion}.",
    "{palabra} es una palabra del leonés que se refiere a {definicion}.",
    "En leonés, {palabra} se refiere a {definicion}.",
    "La palabra leonesa {palabra} expresa {definicion}.",
    "El término leonés {palabra} hace referencia a {definicion}.",
]

# Generar preguntas y respuestas inversas estilo "castellano -> leonés"
preguntas_inversas = [
    "¿Cómo se traduce {castellano} al leonés?",
    "¿Cuál es la palabra en leonés para decir {castellano}?",
    "¿Cómo se dice {castellano} en leonés?",
    "¿Qué palabra en leonés significa {castellano}?"
]

respuestas_inversas = [
    "Se traduce como {leones}.",
    "En leonés se dice {leones}.",
    "La palabra en leonés es {leones}.",
    "{castellano} en leonés se dice {leones}."
]

# Conectores suaves para unir frases
conectores = [
    " Otra acepción es ",
    " Asimismo, ",
    " En otro sentido, ",
    " Asimismo, indica ",
    " También puede significar ",
    " Igualmente, puede referirse a ",
    " Además, puede indicar ",
    " En algunos contextos, significa ",
    " Otra interpretación posible es ",
    " Igualmente, puede expresar ",
    " También puede significar ",
]

def expandir_variantes(palabra):
    palabra_limpia = re.sub(r"\s*\(.*?\)", "", palabra).strip()
    match = re.match(r"^(\w+)(\w),\s*-(\w+)$", palabra_limpia)
    if match:
        raiz = match.group(1)
        suf1 = match.group(2)
        suf2 = match.group(3)
        return [raiz + suf1, raiz + suf2]
    return [palabra_limpia]

def expandir_definicion_genero(definicion):
    def reemplazo(match):
        base = match.group(1)
        if base.endswith("o"):
            base_fem = base[:-1] + "a"
            return f"{base}, {base_fem}"
        else:
            return match.group(0)
    return re.sub(r"\b(\w+),\s*-a\b", reemplazo, definicion)

def limpiar_definicion(definicion):
    definicion = re.sub(r"^\d+\.\s*", "", definicion).strip()
    definicion = expandir_definicion_genero(definicion)

    formas_figurado = ["de forma figurada", "de manera figurada", "usado figuradamente", "en sentido figurado"]
    definicion = re.sub(
        r"\b[Ff]igurado[,;]?\b", 
        lambda _: random.choice(formas_figurado), 
        definicion
    )

    return definicion

def minuscula_inicial(texto):
    return texto[0].lower() + texto[1:] if texto else texto


def es_definicion_valida(definicion):
    """
    Devuelve False si la definición es vacía o solo contiene un número, un punto, o ambos.
    """
    return not re.match(r"^\s*(\d+\.?|\.?)\s*$", definicion)


for entrada in datos:
    palabras = expandir_variantes(entrada["palabra"])
    definiciones_crudas = entrada.get("definiciones", [])
    definiciones_filtradas = [d for d in definiciones_crudas[:5] if es_definicion_valida(d)]
    definiciones_limpias = [minuscula_inicial(limpiar_definicion(d).strip()) for d in definiciones_filtradas]

    if not definiciones_limpias:
        continue

    for palabra in palabras:
        pregunta = random.choice(plantillas_pregunta).format(palabra=palabra)

        if len(definiciones_limpias) == 1:
            definicion = definiciones_limpias[0]
            respuesta = random.choice(plantillas_respuesta).format(palabra=palabra, definicion=definicion)
            
            if len(definicion.split()) <= 2 and ',' not in definicion:
                pregunta_inversa = random.choice(preguntas_inversas).format(castellano=definicion)
                respuesta_inversa = random.choice(respuestas_inversas).format(castellano=definicion, leones=palabra)
                respuesta_inversa = respuesta_inversa[0].upper() + respuesta_inversa[1:]
                pares.append({
                    "input": pregunta_inversa,
                    "output": respuesta_inversa
                })

        else:
            respuestas_formateadas = []
            for i, definicion in enumerate(definiciones_limpias):
                if i == 0:
                    frase = random.choice(plantillas_respuesta).format(definicion=minuscula_inicial(definicion), palabra=minuscula_inicial(palabra))
                else:
                    conector = random.choice(conectores)
                    frase = conector + minuscula_inicial(definicion)
                respuestas_formateadas.append(frase)

            respuesta = "".join(respuestas_formateadas)
            
            if len(respuesta) > 200:
                respuestas_formateadas = []
                definiciones_reducidas = definiciones_limpias[:4]  # Limitar a 3 acepciones

                for i, definicion in enumerate(definiciones_limpias):
                    if i == 0:
                        frase = random.choice(plantillas_respuesta).format(definicion=minuscula_inicial(definicion), palabra=minuscula_inicial(palabra))
                    else:
                        conector = random.choice(conectores)
                        frase = conector + minuscula_inicial(definicion)
                    respuestas_formateadas.append(frase)

                respuesta = "".join(respuestas_formateadas)
                
            if len(respuesta) > 200:
                respuestas_formateadas = []
                definiciones_reducidas = definiciones_limpias[:3]  # Limitar a 3 acepciones

                for i, definicion in enumerate(definiciones_limpias):
                    if i == 0:
                        frase = random.choice(plantillas_respuesta).format(definicion=minuscula_inicial(definicion), palabra=minuscula_inicial(palabra))
                    else:
                        conector = random.choice(conectores)
                        frase = conector + minuscula_inicial(definicion)
                    respuestas_formateadas.append(frase)

                respuesta = "".join(respuestas_formateadas)

        respuesta = respuesta[0].upper() + respuesta[1:]
        pares.append({
            "input": pregunta,
            "output": respuesta
        })

# Guardar el nuevo dataset
with open("datasets/lliones-dict-cele-small.json", "w", encoding="utf-8") as f:
    json.dump(pares, f, ensure_ascii=False, indent=2)
    print("done")
