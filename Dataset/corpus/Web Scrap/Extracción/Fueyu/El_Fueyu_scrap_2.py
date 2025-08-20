import os
import json
from bs4 import BeautifulSoup

def extraer_noticias_desde_html(html_content):
    soup = BeautifulSoup(html_content, 'html.parser')
    noticias = []

    # Buscar bloques de noticias por el estilo: texto centrado y fuerte con <span class="Estilo3">
    bloques = soup.find_all('span', class_='Estilo3')
    
    for bloque in bloques:
        titulo = bloque.get_text(strip=True)
        contenido = []

        # Ir al padre <p> y seguir extrayendo párrafos hermanos hasta encontrar '-----' o final
        p = bloque.find_parent('p')
        if not p:
            continue
        siguiente = p.find_next_sibling()
        while siguiente:
            if siguiente.name == 'p':
                texto = siguiente.get_text(strip=True)
                if '-----' in texto:
                    break
                contenido.append(texto)
            siguiente = siguiente.find_next_sibling()

        noticias.append({
            'titulo': titulo,
            'contenido': '\n'.join(contenido)
        })

    return noticias

def procesar_archivos_html(directorio):
    todas_las_noticias = []

    for nombre_archivo in os.listdir(directorio):
        if nombre_archivo.endswith('.html'):
            ruta = os.path.join(directorio, nombre_archivo)
            with open(ruta, 'r', encoding='utf-8') as archivo:
                html_content = archivo.read()
                noticias = extraer_noticias_desde_html(html_content)
                todas_las_noticias.extend(noticias)

    return todas_las_noticias

if __name__ == "__main__":
    directorio_html = "paginas"
    noticias = procesar_archivos_html(directorio_html)

    with open("noticias_el_fueyu_2.json", "w", encoding="utf-8") as json_file:
        json.dump(noticias, json_file, ensure_ascii=False, indent=2)

    print(f"Se guardaron {len(noticias)} noticias en noticias.json")
