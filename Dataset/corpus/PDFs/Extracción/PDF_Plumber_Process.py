import os
import pdfplumber

def pdf_a_txt(pdf_path, txt_path, start_page=1, end_page=None):
    """
    Extrae texto de un PDF entre las páginas indicadas (incluidas).
    - start_page: número de página inicial (1-indexado).
    - end_page: número de página final (1-indexado). Si es None, extrae hasta el final.
    """
    with pdfplumber.open(pdf_path) as pdf, open(txt_path, "w", encoding="utf-8") as f:
        total_paginas = len(pdf.pages)

        if end_page is None or end_page > total_paginas:
            end_page = total_paginas

        for i in range(start_page - 1, end_page):
            page = pdf.pages[i]
            print(f"{os.path.basename(pdf_path)} - Procesando página {i+1}/{total_paginas}…")
            texto = page.extract_text()
            if texto:
                f.write(texto)
                f.write("\n\n")

    print(f"Texto guardado en: {txt_path}")


# Carpetas de entrada y salida
carpeta_pdf = r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\plumber"
carpeta_txt = r"C:\Users\usuario\Desktop\Corpus\Documentos\txt"

# Procesar todos los PDFs en la carpeta
for archivo in os.listdir(carpeta_pdf):
    if archivo.lower().endswith(".pdf"):
        ruta_pdf = os.path.join(carpeta_pdf, archivo)
        nombre_txt = os.path.splitext(archivo)[0] + ".txt"
        ruta_txt = os.path.join(carpeta_txt, nombre_txt)

        pdf_a_txt(ruta_pdf, ruta_txt)

# pdf_a_txt(r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\Lleon_ou_Llion.pdf", "salida2.txt")
