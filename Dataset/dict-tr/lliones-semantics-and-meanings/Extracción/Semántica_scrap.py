import requests
from bs4 import BeautifulSoup
import json

# Lista de IDs no secuenciales
ids = [20, 2, 42, 55, 105, 18, 66, 32, 89, 40, 106, 73, 22, 14, 74, 49, 34, 101, 16, 47, 107, 36, 64, 90, 7, 26, 9, 84, 80, 92, 100, 68, 37]

# URL base
url_base = "https://www.pallabreirulliones.com/traductor/familias/{}?idioma=leones"

# Encabezados
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Resultados
familias = []

for fam_id in ids:
    url = url_base.format(fam_id)
    print(f"Procesando ID {fam_id}: {url}")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Error en ID {fam_id}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")
    
    # Buscar el contenedor principal
    well = soup.select_one("div.col-lg-9 > div.well")
    if not well:
        print(f"No se encontró contenido para ID {fam_id}")
        continue

    # Título dentro de h2 > strong
    titulo_tag = well.select_one("h2.color_texto_idioma strong")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else f"Sin título ({fam_id})"

    # Subtítulo: h3 (puede haber más de uno, aunque normalmente uno)
    subtitulos = [h3.get_text(strip=True) for h3 in well.find_all("h3")]

    # Vocabulario: todos los <b>
    vocabulario = [b.get_text(strip=True) for b in well.find_all("b")]

    familias.append({
        "id": fam_id,
        "titulo": titulo,
        "subtitulos": subtitulos,
        "vocabulario": vocabulario
    })

# Guardar en JSON
with open("familias_leonesas.json", "w", encoding="utf-8") as f_json:
    json.dump(familias, f_json, ensure_ascii=False, indent=4)

print("Extracción completada. Archivo guardado como familias_leonesas.json")
