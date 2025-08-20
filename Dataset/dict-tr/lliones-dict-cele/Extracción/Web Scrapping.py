import requests
from bs4 import BeautifulSoup
import json
import urllib3
import os

# Desactivar advertencias por verificación SSL deshabilitada
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

# URL base
base_url = "https://lla.unileon.es/srv/fetch//1746000299336?id="

# Rango de IDs a consultar
start_id = 100001
end_id = 116076 

def extraer_info(html):
    soup = BeautifulSoup(html, "html.parser")

    # Obtener palabra
    palabra_tag = soup.find("header", class_="f")
    if not palabra_tag:
        return None
    palabra = palabra_tag.text.strip()

    # Obtener definiciones
    definiciones = [
        def_tag.get_text(separator=" ", strip=True)
        for def_tag in soup.find_all("def")
    ]

    return {
        "palabra": palabra,
        "definiciones": definiciones
    }

# Lista de resultados
palabras = []

for i in range(start_id, end_id):
    doc_id = f"EC{i}"
    url = base_url + doc_id

    try:
        print(f"Descargando {url}...")
        response = requests.get(url, verify=False, timeout=10)
        response.encoding = 'utf-8'
        response.raise_for_status()
        info = extraer_info(response.text)
        if info:
            palabras.append(info)
        else:
            print(f"Contenido no válido para {url}")
    except Exception as e:
        print(f"Error al procesar {url}: {e}")

# Guardar en la misma ruta del script
script_dir = os.path.dirname(os.path.abspath(__file__))
output_path = os.path.join(script_dir, "diccionario_sin_zonas.json")

# Guardar como JSON
with open(output_path, "w", encoding="utf-8") as f:
    json.dump(palabras, f, ensure_ascii=False, indent=2)

print(f"Archivo guardado en: {output_path}")
