import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.graphics.barcode import code128
from reportlab.lib.utils import ImageReader
import os

# --- CONFIGURACIÓN ---
FILE_EXCEL = "etiquetas.xlsx"
FILE_LOGO = "logo.png" 
FILE_OUTPUT = "PDF_etiquetas.pdf"

PAGE_WIDTH, PAGE_HEIGHT = A4
MARGIN = 1.0 * cm
ET_WIDTH = 3.0 * cm
ET_HEIGHT = 8.0 * cm

COLS = int((PAGE_WIDTH - 2 * MARGIN) // ET_WIDTH)
ROWS = int((PAGE_HEIGHT - 2 * MARGIN) // ET_HEIGHT)
ET_PER_PAGE = COLS * ROWS

def generate_pdf():
    try:
        df = pd.read_excel(FILE_EXCEL)
        df = df.fillna("")
    except Exception as e:
        print(f"Error al leer Excel: {e}")
        return

    items = []
    for _, row in df.iterrows():
        try:
            cant = int(row['Cantidad']) if row['Cantidad'] != "" else 1
            for _ in range(cant):
                items.append(row)
        except:
            continue

    c = canvas.Canvas(FILE_OUTPUT, pagesize=A4)
    
    for i in range(0, len(items), ET_PER_PAGE):
        page_items = items[i:i + ET_PER_PAGE]
        draw_frentes(c, page_items)
        c.showPage()
        draw_dorsos(c, page_items)
        c.showPage()

    c.save()
    print(f"Generado con éxito.")

def draw_frentes(c, page_items):
    for index, item in enumerate(page_items):
        col = index % COLS
        row = index // COLS
        x = MARGIN + (col * ET_WIDTH)
        y = PAGE_HEIGHT - MARGIN - ((row + 1) * ET_HEIGHT)
        
        c.setLineWidth(0.1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, ET_WIDTH, ET_HEIGHT)
        
        if os.path.exists(FILE_LOGO):
            logo = ImageReader(FILE_LOGO)
            c.saveState()
            c.translate(x + ET_WIDTH/2, y + ET_HEIGHT/2)
            c.rotate(90)
            c.drawImage(logo, -3.5*cm, -1.2*cm, width=7*cm, height=2.4*cm, 
                        preserveAspectRatio=True, mask='auto')
            c.restoreState()

def draw_dorsos(c, page_items):
    for index, item in enumerate(page_items):
        col_normal = index % COLS
        col_espejo = (COLS - 1) - col_normal 
        row = index // COLS
        x = MARGIN + (col_espejo * ET_WIDTH)
        y = PAGE_HEIGHT - MARGIN - ((row + 1) * ET_HEIGHT)
        
        c.setLineWidth(0.1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, ET_WIDTH, ET_HEIGHT)
        
        c.setFillColorRGB(0, 0, 0)
        
        # 1. ARTICULO
        c.setFont("Helvetica-Bold", 6)
        articulo = str(item['Articulo'])[:18]
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 0.7*cm, articulo.upper())

        # 2. RECUADRO TALLE
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)
        c.roundRect(x + 0.3*cm, y + ET_HEIGHT - 2.1*cm, ET_WIDTH - 0.6*cm, 1.1*cm, 0.1*cm)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 1.4*cm, "TALLE")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 1.9*cm, str(item['Talle']))

        # 3. RECUADRO PRECIOS
        c.roundRect(x + 0.3*cm, y + ET_HEIGHT - 5.2*cm, ET_WIDTH - 0.6*cm, 2.8*cm, 0.1*cm)
        
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 2.8*cm, "PRECIO LISTA")
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 3.3*cm, f"${item['Precio Normal']}")
        
        # Línea divisoria suave entre precios
        c.setLineWidth(0.2)
        c.line(x + 0.5*cm, y + ET_HEIGHT - 3.6*cm, x + ET_WIDTH - 0.5*cm, y + ET_HEIGHT - 3.6*cm)

        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 4.1*cm, "PRECIO EFECTIVO")
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + ET_WIDTH/2, y + ET_HEIGHT - 4.8*cm, f"${item['Precio Contado']}")

        # 4. CODIGO ALFANUMERICO
        c.setFont("Courier", 7)
        c.drawCentredString(x + ET_WIDTH/2, y + 1.8*cm, str(item['Codigo']))

        # 5. CODIGO DE BARRAS
        try:
            codigo_str = str(item['Codigo'])
            bc = code128.Code128(codigo_str, barHeight=0.7*cm, barWidth=0.7)
            bc_width = bc.width
            bc.drawOn(c, x + (ET_WIDTH - bc_width)/2, y + 0.8*cm)
        except:
            c.setFont("Helvetica", 5)
            c.drawCentredString(x + ET_WIDTH/2, y + 1*cm, "ERROR BARCODE")

if __name__ == "__main__":
    generate_pdf()