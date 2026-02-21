import streamlit as st
import pandas as pd
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
from reportlab.lib.units import cm
from reportlab.graphics.barcode import code128
from reportlab.lib.utils import ImageReader
from reportlab.pdfbase.pdfmetrics import stringWidth
import io
import base64

st.set_page_config(page_title="Generador de Etiquetas", layout="centered")

def normalizar_columnas(df):
    df.columns = df.columns.str.strip().str.lower()
    reemplazos = {'á': 'a', 'é': 'e', 'í': 'i', 'ó': 'o', 'ú': 'u'}
    for k, v in reemplazos.items():
        df.columns = df.columns.str.replace(k, v)
    return df

def draw_wrapped_text(c, texto, x_centrado, y_start, max_width):
    font_name = "Helvetica-Bold"
    font_size = 4
    c.setFont(font_name, font_size)
    
    palabras = texto.split()
    lineas = []
    linea_actual = ""
    
    for palabra in palabras:
        test_linea = linea_actual + (" " if linea_actual else "") + palabra
        if stringWidth(test_linea, font_name, font_size) <= max_width:
            linea_actual = test_linea
        else:
            lineas.append(linea_actual)
            linea_actual = palabra
    lineas.append(linea_actual)
    
    y = y_start
    for linea in lineas[:2]:
        c.drawCentredString(x_centrado, y, linea)
        y -= 0.25 * cm 

def draw_etiqueta_logic(c, x, y, item, logo_bytes, modo, rotar):
    et_w, et_h = 3*cm, 8*cm
    c.setLineWidth(0.1)
    c.setStrokeColorRGB(0.8, 0.8, 0.8)
    c.rect(x, y, et_w, et_h)

    if modo == "frente" and logo_bytes:
        logo = ImageReader(logo_bytes)
        c.saveState()
        c.translate(x + et_w/2, y + et_h/2)
        if rotar: c.rotate(90)
        c.drawImage(logo, -3.5*cm if rotar else -1.3*cm, -1.2*cm if rotar else -1.2*cm, 
                    width=7*cm if rotar else 2.6*cm, height=2.4*cm, preserveAspectRatio=True, mask='auto')
        c.restoreState()
    
    elif modo == "dorso":
        c.setFillColorRGB(0, 0, 0)
        
        # Articulo en dos renglones maximo
        articulo_texto = str(item.get('articulo', '')).upper()
        draw_wrapped_text(c, articulo_texto, x + 1.5*cm, y + 7.4*cm, et_w - 0.4*cm)

        # Talle
        c.setStrokeColorRGB(0, 0, 0)
        c.roundRect(x + 0.3*cm, y + 5.8*cm, 2.4*cm, 1.1*cm, 0.1*cm)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + 1.5*cm, y + 6.5*cm, "TALLE")
        c.setFont("Helvetica-Bold", 10)
        c.drawCentredString(x + 1.5*cm, y + 6.0*cm, str(item.get('talle', '')))
        
        # Precios
        c.roundRect(x + 0.3*cm, y + 2.7*cm, 2.4*cm, 2.8*cm, 0.1*cm)
        c.setFont("Helvetica", 6)
        c.drawCentredString(x + 1.5*cm, y + 5.1*cm, "PRECIO LISTA")
        c.setFont("Helvetica-Bold", 9)
        c.drawCentredString(x + 1.5*cm, y + 4.6*cm, f"${item.get('precio normal', 0)}")
        c.setFont("Helvetica-Bold", 6)
        c.drawCentredString(x + 1.5*cm, y + 3.8*cm, "PRECIO EFECTIVO")
        c.setFont("Helvetica-Bold", 13)
        c.drawCentredString(x + 1.5*cm, y + 3.1*cm, f"${item.get('precio contado', 0)}")
        
        # 
        cod = str(item.get('codigo', '000'))
        c.setFont("Courier", 7)
        c.drawCentredString(x + 1.5*cm, y + 1.7*cm, cod)
        try:
            bc = code128.Code128(cod, barHeight=0.7*cm, barWidth=0.7)
            bc.drawOn(c, x + (3*cm - bc.width)/2, y + 0.7*cm)
        except: pass

def get_pdf_bytes(df, logo_file, rotar):
    items = []
    for _, row in df.iterrows():
        try:
            for _ in range(int(row.get('cantidad', 1))): items.append(row.to_dict())
        except: pass
    
    out = io.BytesIO()
    c = canvas.Canvas(out, pagesize=A4)
    for i in range(0, len(items), 18):
        p_items = items[i:i+18]
        for idx, it in enumerate(p_items):
            draw_etiqueta_logic(c, 1*cm + (idx%6)*3*cm, A4[1]-1*cm-((idx//6)+1)*8*cm, it, logo_file, "frente", rotar)
        c.showPage()
        for idx, it in enumerate(p_items):
            col_esp = 5 - (idx%6)
            draw_etiqueta_logic(c, 1*cm + col_esp*3*cm, A4[1]-1*cm-((idx//6)+1)*8*cm, it, None, "dorso", False)
        c.showPage()
    c.save()
    return out.getvalue()

def get_pdf_preview(item, logo_file, rotar):
    buf = io.BytesIO()
    c = canvas.Canvas(buf, pagesize=(3*cm, 8*cm))
    draw_etiqueta_logic(c, 0, 0, item, logo_file, "frente", rotar)
    c.showPage()
    draw_etiqueta_logic(c, 0, 0, item, None, "dorso", False)
    c.save()
    return buf.getvalue()

# Interfaz
st.title("Generador de Etiquetas")
st.write("Cargá tus archivos para generar el PDF de impresión en tamaño A44")

ej_df = pd.DataFrame({'Articulo':['Campera de Cuero Negra'],'Talle':['XL'],'Precio Contado':[85000],'Precio Normal':[98000],'Codigo':['CC-001'],'Cantidad':[1]})
buf_ex = io.BytesIO()
with pd.ExcelWriter(buf_ex, engine='openpyxl') as w: ej_df.to_excel(w, index=False)
st.download_button("Descargar planilla de ejemplo", buf_ex.getvalue(), "ejemplo_etiquetas.xlsx")

col_a, col_b = st.columns(2)
with col_a:
    excel_file = st.file_uploader("Subir archivo Excel", type=["xlsx"])
with col_b:
    logo_file = st.file_uploader("Subir logo del local", type=["png","jpg","jpeg"])

if excel_file and logo_file:
    df = normalizar_columnas(pd.read_excel(excel_file).fillna(""))
    st.write("---")
    st.write("**Previsualizacion de etiqueta**")
    rotar_logo = st.checkbox("Rotar logo 90°", value=True)

    pdf_preview = get_pdf_preview(df.iloc[0].to_dict(), logo_file, rotar_logo)
    base64_pdf = base64.b64encode(pdf_preview).decode('utf-8')
    pdf_display = f'<iframe src="data:application/pdf;base64,{base64_pdf}" width="100%" height="400" type="application/pdf"></iframe>'
    st.markdown(pdf_display, unsafe_allow_html=True)
    
    st.write(" ") 
    pdf_final = get_pdf_bytes(df, logo_file, rotar_logo)
    st.download_button(
        label="Descargar PDF",
        data=pdf_final,
        file_name="etiquetas.pdf",
        mime="application/pdf"
    )