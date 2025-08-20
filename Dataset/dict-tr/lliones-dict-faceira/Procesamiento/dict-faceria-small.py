import json
import random

# Cargar el archivo del diccionario procesado
with open('diccionario_leones_procesado_2Column.json', 'r', encoding='utf-8') as f:
    data = json.load(f)

# Pools de preguntas
preguntas_acepciones = [
    "¿Qué significa el término leonés {palabra}?",
    "¿Cuál es el significado de la palabra leonesa {palabra}?",
    "¿Qué quiere decir el vocablo leonés {palabra}?",
    "¿A qué se refiere la palabra leonesa {palabra}?",
    "Explícame el significado de la palabra leonesa {palabra}.",
]

preguntas_sinonimos = [
    "¿Cuáles son los sinónimos de {palabra} en leonés?",
    "Dime otras palabras que signifiquen lo mismo que {palabra} en leonés.",
    "¿Existen sinónimos para {palabra} dentro del leonés?",
    "¿Qué términos leoneses comparten significado con {palabra}?"
]

preguntas_antonimos = [
    "¿Cuáles son los antónimos de {palabra} en leonés?",
    "Dime palabras que signifiquen lo contrario que {palabra} en leonés.",
    "¿Tiene antónimos {palabra} dentro del vocabulario leonés?",
    "¿Qué términos leoneses expresan lo opuesto a {palabra}?"
]

preguntas_referencias = [
    "¿A qué palabras leonesas está relacionada {palabra}?",
    "¿Con qué otras palabras leonesas se relaciona {palabra}?",
    "¿Qué referencias leonesas tiene {palabra}?",
    "¿Qué otras palabras del leones se relacionan con {palabra}?"
]

preguntas_familias = [
    "¿A qué familia semántica pertenece {palabra}?",
    "¿De qué campo es {palabra}?",
    "¿Con qué área del conocimiento se relaciona {palabra}?",
    "¿Qué familia semántica describe {palabra}?"
]

preguntas_dichos = [
    "¿Qué dichos o refránes leoneses incluyen la palabra {palabra}?",
    "¿Me puedes decir refranes leoneses con la palabra {palabra}?",
    "¿Existe algún dicho leonés relacionado con {palabra}?",
    "¿Qué refranes leoneses contiene la entrada de {palabra}?"
]

preguntas_inversas = [
    "¿Cómo se dice en leonés la palabra española {contenido}?",
    "¿Qué palabra leonesa corresponde a la española {contenido}?",
    "¿Cuál sería el equivalente leonés de la palabra española {contenido}?",
    "¿Qué vocablo se usa en leonés para decir la palabra española {contenido}?"
]

# Pools de respuestas (plantillas)
respuestas_acepciones = [
    "La palabra leonesa {palabra} significa {contenido}.",
    "{palabra} es un término leonés que significa {contenido}.",
    "En el leonés, la palabra {palabra} se entiende como {contenido}.",
    "{palabra} es una palabra del leonés que se refiere a {contenido}.",
    "En leonés, {palabra} se refiere a {contenido}.",
    "La palabra leonesa {palabra} expresa {contenido}.",
    "El término leonés {palabra} hace referencia a {contenido}.",
]

respuestas_sinonimos = [
    "En el leonés, los sinónimos de la palabra {palabra} son: {contenido}.",
    "Entre los sinónimos de {palabra} en el dialecto leonés se encuentran: {contenido}.",
    "Dentro del vocabulario leonés, {palabra} puede sustituirse por: {contenido}."
]

respuestas_antonimos = [
    "En el leonés, los antónimos de la palabra {palabra} son: {contenido}.",
    "Entre los antónimos de {palabra} en el idioma leonés se incluyen: {contenido}.",
    "En el léxico leonés, los términos contrarios a {palabra} son: {contenido}."
]

respuestas_referencias = [
    "Está relacionada con las siguientes palabras {contenido}.",
    "Se vincula con {contenido}.",
    "Hace referencia a {contenido}."
]

respuestas_familias = [
    "{palabra} pertenece al campo de {contenido}.",
    "La familia semántica de {palabra} es {contenido}.",
    "Se relaciona con el área de {contenido}."
]

respuestas_dichos = [
    "Un dicho con la palabra {palabra} es {contenido}.",
    "Existe el refrán {contenido}.",
    "{contenido} es un dicho en el que aparece {palabra}.",
    "Se dice {contenido}."
]

respuestas_inversas = [
    "La traducción de {contenido} al leonés es {palabra}.",
    "{palabra} es como se dice {contenido} en leonés.",
    "En leonés, se traduce {contenido} como {palabra}.",
    "El equivalente en leonés de {contenido} es {palabra}."
]

# Pool de conectores
conectores = [
    " Otra acepción es ",
    " Asimismo, puede referirse a",
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

def minuscula_inicial(texto):
    return texto[0].lower() + texto[1:] if texto else texto

# Generar pares input-output
pares_input_output = []

for entrada in data:
    palabra =  minuscula_inicial(entrada["palabra"])
    acepciones = list(set(entrada.get("acepciones", [])))

    if acepciones:
        if len(acepciones) == 1:
            contenido =  minuscula_inicial(acepciones[0])
            # Pregunta directa
            pregunta = random.choice(preguntas_acepciones).format(palabra=palabra)
            respuesta = random.choice(respuestas_acepciones).format(palabra=palabra, contenido=contenido)
            respuesta = respuesta[0].upper() + respuesta[1:]
            pares_input_output.append({"input": pregunta, "output": respuesta})

            # Pregunta inversa solo si es una sola palabra (sin espacios)
            if " " not in contenido.strip():
                pregunta_inversa = random.choice(preguntas_inversas).format(contenido=contenido)
                respuesta_inversa = random.choice(respuestas_inversas).format(palabra=palabra, contenido=contenido)
                respuesta_inversa = respuesta_inversa[0].upper() + respuesta_inversa[1:]
                pares_input_output.append({"input": pregunta_inversa, "output": respuesta_inversa})
        else:
            frases_formateadas = []
            for i, definicion in enumerate(acepciones):
                if i == 0:
                    frase = random.choice(respuestas_acepciones).format(
                        palabra=palabra, contenido=minuscula_inicial(definicion))
                else:
                    conector = random.choice(conectores)
                    frase = conector + minuscula_inicial(definicion)
                frases_formateadas.append(frase)

            respuesta = "".join(frases_formateadas)

            pregunta = random.choice(preguntas_acepciones).format(palabra=palabra)
            
            respuesta = respuesta[0].upper() + respuesta[1:]
            pares_input_output.append({"input": pregunta, "output": respuesta})
            
    # Sinónimos
    sinonimos = sorted(set(entrada.get("sinonimos", [])))
    if sinonimos:
        contenido = ", ".join(sinonimos)
        pregunta = random.choice(preguntas_sinonimos).format(palabra=palabra)
        respuesta = random.choice(respuestas_sinonimos).format(palabra=palabra, contenido=contenido)
        respuesta = respuesta[0].upper() + respuesta[1:]
        pares_input_output.append({"input": pregunta, "output": respuesta})

    # Antónimos
    antonimos = sorted(set(entrada.get("antonimos", [])))
    if antonimos:
        contenido = ", ".join(antonimos)
        pregunta = random.choice(preguntas_antonimos).format(palabra=palabra)
        respuesta = random.choice(respuestas_antonimos).format(palabra=palabra, contenido=contenido)
        respuesta = respuesta[0].upper() + respuesta[1:]
        pares_input_output.append({"input": pregunta, "output": respuesta})

    # Referencias
    referencias = sorted(set(entrada.get("referencias", [])))
    if referencias:
        contenido = ", ".join(referencias)
        pregunta = random.choice(preguntas_referencias).format(palabra=palabra)
        respuesta = random.choice(respuestas_referencias).format(palabra=palabra, contenido=contenido)
        respuesta = respuesta[0].upper() + respuesta[1:]
        pares_input_output.append({"input": pregunta, "output": respuesta})

    # Familias semánticas
    #familias = sorted(set(entrada.get("familias_semanticas", [])))
    #if familias:
    #    contenido = ", ".join(familias)
    #    pregunta = random.choice(preguntas_familias).format(palabra=palabra)
    #    respuesta = random.choice(respuestas_familias).format(palabra=palabra, contenido=contenido)
    #    pares_input_output.append({"input": pregunta, "output": respuesta})

    # Dichos o refranes
    dichos = list(set(entrada.get("dichos", [])))
    if dichos:
        pregunta = random.choice(preguntas_dichos).format(palabra=palabra)
        
        if len(dichos) == 1:
            contenido = minuscula_inicial(dichos[0])
            respuesta = random.choice(respuestas_dichos).format(palabra=palabra, contenido=contenido)
        else:
            random.shuffle(dichos)
            frases_formateadas = []
            for i, dicho in enumerate(dichos):
                frase = random.choice(respuestas_dichos).format(palabra=palabra, contenido=minuscula_inicial(dicho))
                if i > 0:
                    conector = random.choice(conectores)
                    frase = conector + frase[0].lower() + frase[1:]
                frases_formateadas.append(frase)
            contenido = "".join(frases_formateadas)
            respuesta = contenido
            
        respuesta = respuesta[0].upper() + respuesta[1:]
        pares_input_output.append({"input": pregunta, "output": respuesta})

# Guardar los pares input-output en un archivo JSON
with open("lliones-dict-faceira-small_2Column.json", "w", encoding="utf-8") as f:
    json.dump(pares_input_output, f, ensure_ascii=False, indent=2)

print("✅ Pares input-output generados correctamente en formato JSON.")