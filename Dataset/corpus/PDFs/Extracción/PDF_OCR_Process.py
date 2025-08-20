import os
from pdf2image import convert_from_path
import pytesseract

# --- Configuración Tesseract (ajusta si es necesario) ---
os.environ.setdefault('TESSDATA_PREFIX', r"C:/Program Files/Tesseract-OCR/tessdata")
pytesseract.pytesseract.tesseract_cmd = r"C:/Program Files/Tesseract-OCR/tesseract.exe"

# --- (Opcional) OpenCV para preprocesar ---
try:
    import cv2
    import numpy as np
    OPENCV_OK = True
except Exception:
    OPENCV_OK = False

def _preprocesar_pil(pil_img):
    """Binariza + corrige inclinación (deskew) de forma simple."""
    if not OPENCV_OK:
        return pil_img  # sin cambios si no hay OpenCV
    # PIL -> OpenCV
    img = cv2.cvtColor(np.array(pil_img), cv2.COLOR_RGB2BGR)
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Binariza (Otsu)
    thr = cv2.threshold(gray, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)[1]
    # Deskew aproximado
    coords = np.column_stack(np.where(thr < 255))
    if coords.size:
        angle = cv2.minAreaRect(coords)[-1]
        if angle < -45:
            angle = -(90 + angle)
        else:
            angle = -angle
        (h, w) = thr.shape
        M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
        thr = cv2.warpAffine(thr, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    # OpenCV -> PIL
    from PIL import Image
    return Image.fromarray(thr)

def extraer_texto_pdf_escaneado(
    pdf_path,
    output_txt="salida.txt",
    poppler_path=r"C:/poppler/Library/bin",
    start_page=1,
    end_page=None,
    dpi=300,
    lang="spa",           # para asturleonés: prueba "spa+glg+por" si hay mezcla
    ocr_config="--oem 1 --psm 6",
    preprocesar=True
):
    """
    Convierte PDF escaneado a TXT mediante OCR.
    - Procesa página a página (menos RAM).
    - start_page/end_page son 1-indexadas e INCLUSIVAS.
    - lang puede ser, p.ej., 'spa' o 'spa+glg+por'.
    - ocr_config: ajusta motor (OEM) y modo de segmentación (PSM).
    """
    from pdf2image.pdf2image import pdfinfo_from_path

    # Info de páginas
    info = pdfinfo_from_path(pdf_path, poppler_path=poppler_path)
    total_pag = int(info.get("Pages", 0))
    if total_pag == 0:
        raise ValueError("No se pudo determinar el número de páginas del PDF.")

    if end_page is None or end_page > total_pag:
        end_page = total_pag
    if start_page < 1 or start_page > end_page:
        raise ValueError(f"Rango de páginas inválido: {start_page}-{end_page} (total: {total_pag})")

    print(f"Procesando '{os.path.basename(pdf_path)}' páginas {start_page}-{end_page} de {total_pag}…")

    with open(output_txt, "w", encoding="utf-8") as f:
        # Procesa de forma incremental para reducir memoria
        for page_num in range(start_page, end_page + 1):
            print(f"  · Página {page_num}/{total_pag}")
            # convert_from_path permite pedir un rango estrecho
            imgs = convert_from_path(
                pdf_path,
                dpi=dpi,
                first_page=page_num,
                last_page=page_num,
                poppler_path=poppler_path
            )
            if not imgs:
                continue
            img = imgs[0]
            if preprocesar:
                img = _preprocesar_pil(img)

            texto = pytesseract.image_to_string(img, lang=lang, config=ocr_config)
            f.write(texto.strip() + "\n\n")

    print(f"Texto guardado en: {output_txt}")


# ------------------
# Ejemplos de uso:
# ------------------

# 1) Todo el PDF, sin preprocesado (si no tienes OpenCV):
# extraer_texto_pdf_escaneado("Lleon_ou_Llion.pdf", "Lleon_ou_Llion.txt", preprocesar=False)

# 2) Rango de páginas (de la 3 a la 10) con preprocesado:
# extraer_texto_pdf_escaneado("Lleon_ou_Llion.pdf", "Lleon_ou_Llion_p3-10.txt", start_page=3, end_page=10)

# 3) Mezcla de idiomas cercanos (puede ayudar en asturleonés):
# extraer_texto_pdf_escaneado("Lleon_ou_Llion.pdf", "Lleon_ou_Llion_multilang.txt", lang="spa+glg+por")

# 4) Procesamiento de carpeta entera

carpeta_pdf = r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\ocr"
carpeta_txt = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt"

for archivo in os.listdir(carpeta_pdf):
    if archivo.lower().endswith(".pdf"):
        ruta_pdf = os.path.join(carpeta_pdf, archivo)
        nombre_txt = os.path.splitext(archivo)[0] + ".txt"
        ruta_txt = os.path.join(carpeta_txt, nombre_txt)
        extraer_texto_pdf_escaneado(ruta_pdf, ruta_txt, lang="spa+glg+por")