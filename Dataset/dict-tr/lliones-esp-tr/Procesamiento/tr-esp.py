import json
import random

# Cargar el archivo JSON de expresiones leonesas
with open('expresiones_leonesas.json', 'r', encoding='utf-8') as file:
    data = json.load(file)

# Lista donde se almacenarán las preguntas, respuestas y traducción
questions_answers = []

# Plantillas de frases para traducción ESP → LEO
plantillas_esp_leo = [
    "¿Cómo se diría {frase} en leonés?",
    "¿Me traduces {frase} al leonés?",
    "¿Sabes cómo se dice {frase} en leonés?",
    "¿Podrías decirme cómo se dice {frase} en leonés?",
    "¿Qué palabra usan en leonés para decir {frase}?",
    "¿Cómo se traduce {frase} al leonés?",
    "¿Puedes pasarme {frase} al leonés?",
    "Quiero saber cómo se dice {frase} en leonés",
    "¿Cuál sería la forma leonesa de decir {frase}?"
]

# Plantillas de frases para traducción LEO → ESP
plantillas_leo_esp = [
    "¿Qué quiere decir {frase} en español?",
    "¿Sabes cómo se traduce {frase} al español?",
    "¿Cómo diríamos {frase} en español?",
    "¿Cuál es el significado de {frase} en español?",
    "¿Puedes decirme qué quiere decir {frase} en español?",
    "¿Cómo se entiende {frase} en español?",
    "¿Me puedes traducir {frase} al español?",
    "¿Qué significa exactamente {frase} en español?",
    "¿Cómo se dice {frase} en español?"
]


plantillas_resp_esp_leo = [
    "En leonés se diría {traduccion}.",
    "{traduccion} es la forma leonesa.",
    "Se traduce como {traduccion} en leonés.",
    "En idioma leonés se dice {traduccion}.",
    "{traduccion} es la manera correcta en leonés.",
    "Diríamos simplemente {traduccion} en leonés.",
    "Eso en leonés sería {traduccion}.",
    "La traducción al leonés sería {traduccion}.",
    "En leonés usarías la palabra {traduccion}."
]

plantillas_resp_leo_esp = [
    "En español eso significa {traduccion}.",
    "Lo traducimos al español como {traduccion}.",
    "{traduccion} sería su equivalente en español.",
    "En español diríamos {traduccion}.",
    "La forma en español es {traduccion}.",
    "{traduccion} es lo que quiere decir en español.",
    "Esa palabra significa {traduccion} en español.",
    "La traducción al español sería {traduccion}.",
    "Eso en español se dice {traduccion}.",
    "Simplemente se dice {traduccion} en español."
]


# Procesar cada expresión para formular preguntas y respuestas
for item in data:
    frase_español = item['castellano'].lower()
    frase_leones = item['leones'].lower()

    # Traducción de Castellano a Leonés
    pregunta_esp_leo = {
        "input": random.choice(plantillas_esp_leo).format(frase=frase_español).capitalize(),
        "output": random.choice(plantillas_resp_esp_leo).format(traduccion=frase_leones).capitalize()
    }

    pregunta_leo_esp = {
        "input": random.choice(plantillas_leo_esp).format(frase=frase_leones).capitalize(),
        "output": random.choice(plantillas_resp_leo_esp).format(traduccion=frase_español).capitalize()
    }

    # Añadir a la lista
    questions_answers.append(pregunta_esp_leo)
    questions_answers.append(pregunta_leo_esp)

# Guardar el nuevo archivo JSON con las preguntas y respuestas
output_file = 'datasets/lliones-esp-tr.json'
with open(output_file, 'w', encoding='utf-8') as outfile:
    json.dump(questions_answers, outfile, ensure_ascii=False, indent=4)

print(f"El archivo JSON se ha guardado correctamente en '{output_file}'")
