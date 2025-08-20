"""
Extrae texto de PDFs con 1 o 2 columnas de forma robusta (sin LAParams).
- Detecta el canal entre columnas y corta la página en izquierda/derecha.
- Si no hay dos columnas claras, lee la página completa como 1 columna.
- Deduplica bloques repetidos (misma caja y mismo texto).
- Procesa todos los PDFs de una carpeta de entrada y guarda .txt en la de salida.

Requisitos:
    pip install pymupdf
"""

import os
import fitz  # PyMuPDF
from typing import List, Tuple

# --------------------------- CONFIGURACIÓN ---------------------------

CARPETA_PDF = r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\2Column"
CARPETA_TXT = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt\2Column_PyMuPDF"

# Ancho del "gutter" (canal entre columnas) en puntos PDF (prueba 12–24 si hace falta)
GUTTER = 16

# Cuántos candidatos de corte probamos cerca del centro (proporciones del ancho)
CANDIDATOS_REL = [0.44, 0.47, 0.50, 0.53, 0.56]

# Si la columna derecha o izquierda tiene menos de este % de palabras respecto a la otra,
# se asume que realmente es 1 columna (evita cortar portadas, resúmenes, etc.)
UMBRAL_MIN_PROP = 0.12

# Redondeo de coordenadas para “agrupar” bloques en deduplicación
ROUND_BBOX = 1  # 1 = décima de punto; sube a 2 si tu maquetado vibra mucho

# --------------------------------------------------------------------

def round_rect(r: fitz.Rect, nd: int = 1) -> Tuple[float, float, float, float]:
    return (round(r.x0, nd), round(r.y0, nd), round(r.x1, nd), round(r.y1, nd))

def contar_palabras_clip(page: fitz.Page, clip: fitz.Rect) -> int:
    # Cuenta palabras (o fragmentos) dentro de un recorte para estimar densidad
    # Usamos blocks -> líneas -> textos para que sea rápido y estable
    blocks = page.get_text("blocks", clip=clip)
    total = 0
    for b in blocks:
        txt = (b[4] or "").strip()
        if txt:
            total += len(txt.split())
    return total

def elegir_corte(page: fitz.Page, gutter: int, candidatos_rel: List[float]) -> Tuple[float, fitz.Rect, fitz.Rect]:
    """Busca el corte con menos “texto” (el canal). Devuelve xmid y los rects izq/der."""
    W, H = page.rect.width, page.rect.height
    mejor_x = W * 0.5
    mejor_score = None

    for rel in candidatos_rel:
        xmid = W * rel
        left = fitz.Rect(0, 0, xmid - gutter/2, H)
        right = fitz.Rect(xmid + gutter/2, 0, W, H)
        # Score = cantidad de texto dentro del “canal” (franja central)
        canal = fitz.Rect(xmid - gutter/2, 0, xmid + gutter/2, H)
        score = contar_palabras_clip(page, canal)
        if mejor_score is None or score < mejor_score:
            mejor_score, mejor_x = score, xmid

    xmid = mejor_x
    left = fitz.Rect(0, 0, xmid - gutter/2, H)
    right = fitz.Rect(xmid + gutter/2, 0, W, H)
    return xmid, left, right

def extraer_por_bloques_sin_duplicados(page: fitz.Page, clip: fitz.Rect = None) -> List[str]:
    """
    Extrae texto por bloques, ordenando arriba->abajo, izquierda->derecha,
    y deduplicando por (texto, bbox redondeada).
    """
    blocks = page.get_text("blocks", clip=clip)
    # blocks: [x0, y0, x1, y1, text, block_no, block_type, ...]
    # Orden natural: primero por y, luego por x (ambos redondeados para estabilidad)
    blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))

    vistos = set()
    textos = []
    for b in blocks:
        x0, y0, x1, y1, text, *_ = b
        if not text:
            continue
        txt = text.strip()
        if not txt:
            continue
        key = (txt, round_rect(fitz.Rect(x0, y0, x1, y1), ROUND_BBOX))
        if key in vistos:
            continue
        vistos.add(key)
        textos.append(txt)
    return textos

def procesar_pdf(pdf_path: str, txt_path: str) -> None:
    doc = fitz.open(pdf_path)
    total = len(doc)
    os.makedirs(os.path.dirname(txt_path), exist_ok=True)
    with open(txt_path, "w", encoding="utf-8") as out:
        for i, page in enumerate(doc, 1):
            print(f"{os.path.basename(pdf_path)} - Página {i}/{total}")
            # Intento de 2 columnas
            _, left_rect, right_rect = elegir_corte(page, GUTTER, CANDIDATOS_REL)
            left_words = contar_palabras_clip(page, left_rect)
            right_words = contar_palabras_clip(page, right_rect)

            # Si una de las "columnas" casi no tiene texto, lo tratamos como 1 columna
            es_dos_columnas = True
            if left_words == 0 and right_words == 0:
                es_dos_columnas = False
            else:
                # Evita falsos positivos de “2 columnas”
                if left_words == 0 or right_words == 0:
                    es_dos_columnas = False
                else:
                    menor = min(left_words, right_words)
                    mayor = max(left_words, right_words)
                    if menor / max(mayor, 1) < UMBRAL_MIN_PROP:
                        es_dos_columnas = False

            pagina_lineas = []
            if es_dos_columnas:
                # Izquierda primero, luego derecha
                pagina_lineas.extend(extraer_por_bloques_sin_duplicados(page, left_rect))
                pagina_lineas.extend(extraer_por_bloques_sin_duplicados(page, right_rect))
            else:
                # 1 columna
                pagina_lineas.extend(extraer_por_bloques_sin_duplicados(page))

            if pagina_lineas:
                out.write("\n".join(pagina_lineas) + "\n\n")
    doc.close()
    print(f"✅ Guardado: {txt_path}")

def procesar_carpeta(carpeta_pdf: str, carpeta_txt: str) -> None:
    os.makedirs(carpeta_txt, exist_ok=True)
    for nombre in os.listdir(carpeta_pdf):
        if not nombre.lower().endswith(".pdf"):
            continue
        ruta_pdf = os.path.join(carpeta_pdf, nombre)
        ruta_txt = os.path.join(carpeta_txt, os.path.splitext(nombre)[0] + ".txt")
        procesar_pdf(ruta_pdf, ruta_txt)

if __name__ == "__main__":
    procesar_carpeta(CARPETA_PDF, CARPETA_TXT)
