import fitz  # PyMuPDF
import os
from collections import defaultdict

def _round_rect(r, nd=1):
    # Redondea bbox para agrupar bloques "idénticos"
    return (round(r.x0, nd), round(r.y0, nd), round(r.x1, nd), round(r.y1, nd))

def pdf_a_txt_bloques_sin_duplicados(pdf_path, output_txt, start_page=1, end_page=None, nd=1):
    """
    - Extrae por bloques (lectura natural: de arriba -> abajo, izquierda -> derecha).
    - Deduplica bloques por (texto, bbox redondeado).
    """
    doc = fitz.open(pdf_path)
    total = len(doc)
    if end_page is None or end_page > total:
        end_page = total

    with open(output_txt, "w", encoding="utf-8") as out:
        for pno in range(start_page-1, end_page):
            page = doc[pno]
            print(f"{os.path.basename(pdf_path)} - Página {pno+1}/{total}")
            # "blocks" = [x0,y0,x1,y1, text, block_no, block_type, ...]
            blocks = page.get_text("blocks")
            # Orden natural
            blocks.sort(key=lambda b: (round(b[1], 1), round(b[0], 1)))

            vistos = set()
            pagina_txt = []

            for b in blocks:
                x0, y0, x1, y1, text, *_ = b
                if not text or not text.strip():
                    continue
                key = (text.strip(), _round_rect(fitz.Rect(x0, y0, x1, y1), nd))
                if key in vistos:
                    continue
                vistos.add(key)
                pagina_txt.append(text.strip())

            if pagina_txt:
                out.write("\n".join(pagina_txt) + "\n\n")

    doc.close()
    print(f"✅ Guardado: {output_txt}")

# Ejemplo:
#pdf_a_txt_bloques_sin_duplicados(r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\plumber\Solombras_Nuesos_Valles.pdf", r"C:\Users\usuario\Desktop\Corpus\Documentos\txt\_Solombras_Nuesos_Valles.txt")
#pdf_a_txt_bloques_sin_duplicados(r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\plumber\Cartas_Fichu_Correspondencia_Eva.pdf", r"C:\Users\usuario\Desktop\Corpus\Documentos\txt\Cartas_Fichu_Correspondencia_Eva.txt")
pdf_a_txt_bloques_sin_duplicados(r"C:\Users\usuario\Desktop\Corpus\Documentos\pdf\plumber\Cousas_Ca_Trones_Poesia_Cuentos.pdf", r"C:\Users\usuario\Desktop\Corpus\Documentos\txt\Cousas_Ca_Trones_Poesia_Cuentos.txt")
