import json
import re
import random

# Cargar el archivo JSON de familias leonesas
with open('familias_leonesas.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

questions_answers = []

# Plantillas para preguntas semánticas
plantillas_semantica = [
    "¿A qué familia semántica pertenece la palabra {leones}?",
    "¿Con qué grupo de palabras relacionadas se asocia {leones}?",
    "¿Cuál es el campo semántico de {leones}?",
    "¿Qué otras palabras se relacionan con {leones} en su uso?",
    "¿A qué categoría semántica corresponde {leones}?",
    "¿De qué campo léxico forma parte {leones}?"
]

# Plantillas para preguntas de significado
plantillas_significado = [
    "¿Qué significa {leones} en leonés?",
    "¿A qué se refiere {leones} en leonés?",
    "¿Cuál es el significado de la palabra leonesa {leones}?",
    "¿Cómo se interpreta {leones} en leonés?",
    "¿Qué quiere expresar {leones} en leonés?",
    "¿Qué significa la palabra leonesa {leones}?",
    "¿Podrías explicarme el significado de la palabra leonesa {leones}?",
    "¿A qué se refiere el término leonés {leones}?",
    "¿Qué quiere decir exactamente {leones} en el contexto del leonés?",
    "¿Qué expresa en leonés la palabra {leones}?",
    "¿Cómo se entiende en leonés la palabra {leones}?"
]

# NUEVAS: Plantillas para preguntas del español al leonés
plantillas_inversas = [
    "¿Cómo se dice {castellano} en leonés?",
    "¿Cuál es la traducción de {castellano} al leonés?",
    "¿Qué palabra leonesa significa {castellano}?",
    "¿Cómo se expresa {castellano} en leonés?",
    "¿Qué término leonés corresponde a {castellano}?",
    "¿Cuál es el equivalente leonés de {castellano}?"
]

# Respuestas semánticas
respuestas_semantica = [
    "La palabra {leones} pertenece a la familia semántica de {titulo}.",
    "{leones} forma parte del campo semántico relacionado con {titulo}.",
    "Semánticamente, {leones} se asocia con el tema de {titulo}.",
    "Se clasifica dentro de la familia léxica de {titulo}.",
    "{leones} está dentro del conjunto de palabras relacionadas con {titulo}.",
    "{leones} pertenece al campo de {titulo}."
]

respuestas_significado = [
    "{leones} es una palabra leonesa que significa {castellano}.",
    "El significado de {leones} es {castellano}.",
    "En castellano, {leones} se entiende como {castellano}.",
    "La palabra {leones} quiere decir {castellano}.",
    "{leones} equivale a {castellano} en castellano.",
    "{leones} se usa para referirse a {castellano}.",
    "Con {leones} se expresa la idea de {castellano}.",
    "{leones} hace referencia a {castellano}.",
    "{leones} puede entenderse como {castellano}.",
    "{leones} vendría a significar {castellano}."
]


# Respuestas inversas (castellano → leonés)
respuestas_inversas = [
    "En leonés, {castellano} se dice {leones}.",
    "La palabra leonesa para {castellano} es {leones}.",
    "{leones} es la traducción leonesa de {castellano}.",
    "El equivalente en leonés de {castellano} es {leones}.",
    "{castellano} se traduce al leonés como {leones}.",
    "Para decir {castellano} en leonés, se usa {leones}."
]

def minuscula_inicial(texto):
    return texto[0].lower() + texto[1:] if texto else texto


for entry in data:
    titulo = minuscula_inicial(entry["titulo"])
    subtitulo = entry["subtitulos"]
    vocabulario = entry["vocabulario"]

    for item in vocabulario:
        if " / " not in item:
            continue  # Saltar si el formato es inválido
        leones_word, castellano_word = item.split(" / ", 1)

        leones_word = minuscula_inicial(re.sub(r"\s*[mf]\.$", "", leones_word.strip()))
        castellano_word = minuscula_inicial(re.sub(r"\s*[mf]\.$", "", castellano_word.strip()))
        
        leones_word = re.sub(r',(?=\S)', ', ', leones_word)
        castellano_word = re.sub(r',(?=\S)', ', ', castellano_word)

        # Semántica
        pregunta_sem = random.choice(plantillas_semantica).format(leones=leones_word)
        respuesta_sem = random.choice(respuestas_semantica).format(leones=leones_word, titulo=titulo)

        # Significado
        pregunta_sig = random.choice(plantillas_significado).format(leones=leones_word)
        respuesta_sig = random.choice(respuestas_significado).format(leones=leones_word, castellano=castellano_word)

        respuesta_sem = respuesta_sem[0].upper() + respuesta_sem[1:]
        respuesta_sig = respuesta_sig[0].upper() + respuesta_sig[1:]
        questions_answers.extend([
            {"input": pregunta_sig, "output": respuesta_sig}
        ])

        # Si castellano_word es solo una palabra, crear pregunta inversa
        if len(castellano_word.split()) <= 4:
            pregunta_inv = random.choice(plantillas_inversas).format(castellano=castellano_word)
            respuesta_inv = random.choice(respuestas_inversas).format(castellano=castellano_word, leones=leones_word)
            respuesta_inv = respuesta_inv[0].upper() + respuesta_inv[1:]
            questions_answers.append({"input": pregunta_inv, "output": respuesta_inv})

# Guardar el dataset generado
output_file = 'datasets/lliones-semantics-and-meanings__.json'
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(questions_answers, outfile, ensure_ascii=False, indent=4)

print(f"El archivo JSON se ha guardado correctamente en '{output_file}'")
