import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.graphics.barcode import code128
from reportlab.lib.utils import ImageReader
import io

# Configuración de página
st.set_page_config(page_title="Generador de Etiquetas", layout="centered")

def draw_frentes(c, page_items, logo_bytes):
    logo = ImageReader(logo_bytes)
    margin = 1.0 * cm
    et_width = 3.0 * cm
    et_height = 8.0 * cm
    cols = 6 # Etiquetas que entran a lo ancho en A4 con 1cm margen
    
    for index, item in enumerate(page_items):
        col = index % cols
        row = index // cols
        x = margin + (col * et_width)
        y = A4[1] - margin - ((row + 1) * et_height)
        
        c.setLineWidth(0.1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, et_width, et_height)
        
        c.saveState()
        c.translate(x + et_width/2, y + et_height/2)
        c.rotate(90)
        c.drawImage(logo, -3.5*cm, -1.2*cm, width=7*cm, height=2.4*cm, preserveAspectRatio=True, mask='auto')
        c.restoreState()

def draw_dorsos(c, page_items):
    margin = 1.0 * cm
    et_width = 3.0 * cm
    et_height = 8.0 * cm
    cols = 6
    
    for index, item in enumerate(page_items):
        col_normal = index % cols
        col_espejo = (cols - 1) - col_normal 
        row = index // cols
        x = margin + (col_espejo * et_width)
        y = A4[1] - margin - ((row + 1) * et_height)
        
        c.setLineWidth(0.1)
        c.setStrokeColorRGB(0.8, 0.8, 0.8)
        c.rect(x, y, et_width, et_height)
        
        c.setFillColorRGB(0, 0, 0)
        c.setFont("Helvetica-Bold", 7)
        articulo = str(item.get('Articulo', ''))[:18]
        c.drawCentredString(x + et_width/2, y + et_height - 0.7*cm, articulo.upper())

        # Recuadros estéticos
        c.setLineWidth(0.5)
        c.setStrokeColorRGB(0, 0, 0)
        c.roundRect(x + 0.3*cm, y + et_height - 2.1*cm, et_width - 0.6*cm, 1.1*cm, 0.1*cm)
        c.setFont("Helvetica", 7)
        c.drawCentredString(x + et_width/2, y + et_height - 1.4*cm, "TALLE")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + et_width/2, y + et_height - 1.9*cm, str(item.get('Talle', '')))

        c.roundRect(x + 0.3*cm, y + et_height - 5.2*cm, et_width - 0.6*cm, 2.8*cm, 0.1*cm)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + et_width/2, y + et_height - 2.8*cm, "PRECIO LISTA")
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + et_width/2, y + et_height - 3.3*cm, f"${item.get('Precio Normal', 0)}")
        
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + et_width/2, y + et_height - 4.1*cm, "PRECIO EFECTIVO")
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + et_width/2, y + et_height - 4.8*cm, f"${item.get('Precio Contado', 0)}")

        # Código de barras
        codigo = str(item.get('Codigo', '0000'))
        c.setFont("Courier", 7)
        c.drawCentredString(x + et_width/2, y + 1.8*cm, codigo)
        try:
            bc = code128.Code128(codigo, barHeight=0.7*cm, barWidth=0.7)
            bc.drawOn(c, x + (et_width - bc.width)/2, y + 0.8*cm)
        except:
            pass

st.title("Generador de Etiquetas para Local de Ropa")
st.write("Subí tu Excel y tu Logo para generar el PDF listo para imprimir.")

col1, col2 = st.columns(2)
with col1:
    excel_file = st.file_uploader("1. Archivo Excel (.xlsx)", type=["xlsx"])
with col2:
    logo_file = st.file_uploader("2. Logo de la tienda (PNG/JPG)", type=["png", "jpg", "jpeg"])

if excel_file and logo_file:
    if st.button("🚀 Generar PDF de Etiquetas"):
        df = pd.read_excel(excel_file).fillna("")
        items = []
        for _, row in df.iterrows():
            cant = int(row['Cantidad']) if row['Cantidad'] != "" else 1
            for _ in range(cant):
                items.append(row.to_dict())

        output = io.BytesIO()
        c = canvas.Canvas(output, pagesize=A4)
        
        et_per_page = 18 # 3 columnas x 6 filas
        for i in range(0, len(items), et_per_page):
            page_items = items[i:i + et_per_page]
            draw_frentes(c, page_items, logo_file)
            c.showPage()
            draw_dorsos(c, page_items)
            c.showPage()
        
        c.save()
        pdf_data = output.getvalue()
        
        st.success("¡PDF generado correctamente!")
        st.download_button(
            label="📥 Descargar PDF para Imprimir",
            data=pdf_data,
            file_name="etiquetas_alabama.pdf",
            mime="application/pdf"
        )