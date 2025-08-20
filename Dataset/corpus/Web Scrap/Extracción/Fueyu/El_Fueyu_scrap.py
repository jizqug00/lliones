import os
import json
from bs4 import BeautifulSoup

# Ruta a la carpeta que contiene los archivos HTML
carpeta = 'paginas'
# Lista de archivos que se analizarán
ids = [1, 5, 6, 7, 8, 9, 10, 11]
archivos = [f'noticias{i}.html' for i in ids]

noticias = []

for archivo in archivos:
    ruta = os.path.join(carpeta, archivo)
    with open(ruta, 'r', encoding='utf-8') as f:
        soup = BeautifulSoup(f, 'html.parser')
        
        # Cada noticia está dentro de una tabla con ancho 380
        tablas_noticia = soup.find_all('table', width='380')
        for tabla in tablas_noticia:
            # Título está en el primer <strong> dentro de la tabla
            titulo_tag = tabla.find('strong')
            titulo = titulo_tag.get_text(strip=True) if titulo_tag else "Sin título"
            
            # Contenido son los <p class="txtnuevas">
            contenido_parrafos = tabla.find_all('p', class_='txtnuevas')
            contenido = '\n'.join(p.get_text(strip=True) for p in contenido_parrafos if p.get_text(strip=True))
            
            noticias.append({
                'titulo': titulo,
                'contenido': contenido
            })

# Guardar en JSON
with open('noticias_el_fueyu_1.json', 'w', encoding='utf-8') as json_file:
    json.dump(noticias, json_file, ensure_ascii=False, indent=2)

print(f"Se han extraído {len(noticias)} noticias y guardado en noticias.json.")
