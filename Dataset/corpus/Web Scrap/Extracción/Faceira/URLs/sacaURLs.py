import re

def extraer_urls_de_html(archivo):
    with open(archivo, 'r', encoding='utf-8') as f:
        contenido = f.read()

    patron = r'<h3 class="elementor-post__title">\s*<a href="([^"]+)"'
    urls = re.findall(patron, contenido)
    return urls

if __name__ == "__main__":
    archivo_txt = "data.txt"
    urls_extraidas = extraer_urls_de_html(archivo_txt)

    with open("URLs.txt", "w", encoding="utf-8") as f_out:
        for url in urls_extraidas:
            f_out.write(f'"{url}",\n')
