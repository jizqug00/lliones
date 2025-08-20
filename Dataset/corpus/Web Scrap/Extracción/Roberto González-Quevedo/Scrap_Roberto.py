import requests
from bs4 import BeautifulSoup
import json
import time
from urllib.parse import urlparse

BASE_URL = "https://www.diariodeleon.es/autores/roberto-gonzalez-quevedo/"
ARTICLE_SELECTOR = "h2.c-article__title a"
ARTICLE_BODY_SELECTOR = "div.c-detail__body p"
HEADERS = {
    "User-Agent": "Mozilla/5.0"
}

def get_article_links_from_page(url):
    try:
        response = requests.get(url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        links = [
            a['href'] for a in soup.select(ARTICLE_SELECTOR)
            if a['href'].endswith(".html")
        ]
        return links
    except Exception as e:
        print(f"Error al procesar {url}: {e}")
        return []

def get_article_text(article_url):
    try:
        response = requests.get(article_url, headers=HEADERS)
        soup = BeautifulSoup(response.text, 'html.parser')
        paragraphs = soup.select(ARTICLE_BODY_SELECTOR)
        cleaned_paragraphs = []
        for p in paragraphs:
            text = p.get_text(strip=True)
            # Excluir líneas de metadatos
            if text.startswith("Creado:") or text.startswith("Actualizado:"):
                continue
            cleaned_paragraphs.append(text)
        return "".join(cleaned_paragraphs)  # Sin saltos de línea
    except Exception as e:
        print(f"Error al obtener contenido de {article_url}: {e}")
        return ""

def extract_slug_from_url(url):
    path = urlparse(url).path
    return path.strip("/").split("/")[-1].replace(".html", "")

def main():
    all_articles = {}
    for i in range(1, 14):
        page_url = BASE_URL if i == 1 else f"{BASE_URL}{i}/"
        print(f"Procesando página: {page_url}")
        article_links = get_article_links_from_page(page_url)

        for link in article_links:
            print(f"   Obteniendo artículo: {link}")
            article_text = get_article_text(link)
            if article_text:
                slug = extract_slug_from_url(link)
                all_articles[link] = {
                    "titulo": slug,
                    "contenido": article_text
                }

    with open("articulos_gonzalez_quevedo_3.json", "w", encoding="utf-8") as f:
        json.dump(all_articles, f, ensure_ascii=False, indent=2)

    print("Scraping finalizado. Archivo JSON guardado.")

if __name__ == "__main__":
    main()
