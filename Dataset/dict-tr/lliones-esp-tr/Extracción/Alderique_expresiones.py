import requests
from bs4 import BeautifulSoup
import json
import re

# URL de la página
url = "https://www.lengualeonesa.eu/lliones/Espresiones"

# Realizar la solicitud HTTP
response = requests.get(url)
response.raise_for_status()  # Asegura que la solicitud fue exitosa

# Analizar el contenido HTML
soup = BeautifulSoup(response.text, "html.parser")

# Identificar las tablas que contienen las expresiones
# Según la estructura proporcionada, las tablas están dentro de divs específicos
# Aquí seleccionamos todas las tablas dentro de la sección principal
tables = soup.select("#gpx_content div table")

expresiones = []

for table in tables:
    # Iterar sobre las filas de la tabla
    for row in table.find_all("tr"):
        cells = row.find_all("td")
        if len(cells) == 2:
            # Extraer y limpiar el texto de cada celda
            leones = cells[0].get_text(separator=" ", strip=True)
            castellano = cells[1].get_text(separator=" ", strip=True)

            # Eliminar etiquetas HTML residuales y caracteres no deseados
            leones = re.sub(r'\s+', ' ', leones)  # Reemplaza múltiples espacios por uno solo
            castellano = re.sub(r'\s+', ' ', castellano)

            # Agregar la expresión al listado
            expresiones.append({
                "leones": leones,
                "castellano": castellano
            })

# Guardar las expresiones en un archivo JSON
with open("expresiones_leonesas.json", "w", encoding="utf-8") as f:
    json.dump(expresiones, f, ensure_ascii=False, indent=2)

print("Extracción completada. Datos guardados en 'expresiones_leonesas.json'.")
