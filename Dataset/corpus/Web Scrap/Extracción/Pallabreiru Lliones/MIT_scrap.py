import requests
from bs4 import BeautifulSoup
import json

# Rango de páginas
start = 15
end = 37

# URL base
url_base = "https://www.pallabreirulliones.com/traductor/mitologia/{}?idioma=leones"

# Encabezados
headers = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64)"
}

# Almacenamiento
leyendas = []

for i in range(start, end + 1):
    url = url_base.format(i)
    print(f"Extrayendo página {i}: {url}")
    response = requests.get(url, headers=headers)
    response.encoding = 'utf-8'

    if response.status_code != 200:
        print(f"Error al acceder a la página {i}")
        continue

    soup = BeautifulSoup(response.text, "html.parser")

    # Extraer título
    titulo_tag = soup.select_one("div.container-fluid div.well div.row div.col-lg-12 h3.color_texto_idioma strong")
    titulo = titulo_tag.get_text(strip=True) if titulo_tag else f"Sin título ({i})"

    # Extraer contenido
    parrafos = soup.select("div#desc_mitologia p")
    descripcion = "\n".join(p.get_text(strip=True) for p in parrafos)

    leyendas.append({
        "titulo": titulo,
        "descripcion": descripcion
    })

# Guardar en archivo de texto
with open("leyendas_leonesas.txt", "w", encoding="utf-8") as f_txt:
    for leyenda in leyendas:
        f_txt.write(f"TÍTULO: {leyenda['titulo']}\n")
        f_txt.write(f"DESCRIPCIÓN:\n{leyenda['descripcion']}\n")
        f_txt.write("="*80 + "\n")

# Guardar en archivo JSON
with open("leyendas_leonesas.json", "w", encoding="utf-8") as f_json:
    json.dump(leyendas, f_json, ensure_ascii=False, indent=4)

print("Extracción completada. Archivos guardados como leyendas_leonesas.txt y leyendas_leonesas.json")
