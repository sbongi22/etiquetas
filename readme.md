Generador de Etiquetas

Este proyecto es un script de Python diseñado para automatizar la creación de etiquetas de ropa de 8x3 cm. Está optimizado para imprimir en hojas A4 y permite generar de forma masiva etiquetas con frente (logo) y dorso (datos del producto y código de barras) leyendo la información directamente desde un archivo Excel.

Qué hace el programa
Frente: Coloca el logo de la tienda (logo.png) rotado 90° para aprovechar el formato vertical de la etiqueta.

Dorso: Organiza la información en bloques visuales (Talle, Precio de Lista y Precio Efectivo) usando recuadros para que quede más prolijo.

Códigos de Barras: Genera automáticamente códigos de barras Code128 a partir del código alfanumérico de cada prenda.

Impresión Doble Faz: El script genera una página de frentes y una de dorsos. La página de dorsos está "espejada" para que, al dar vuelta la hoja manualmente en la impresora, cada dorso coincida exactamente con su frente.

Cómo usarlo
1. Requisitos
Necesitás tener instalado Python y las siguientes librerías:
pip install reportlab pandas openpyxl python-barcode Pillow

2. Archivos necesarios
logo.png: El logo de tu local.

etiquetas.xlsx: El archivo con los datos de las prendas.

3. Formato del Excel
El archivo de Excel debe tener estas columnas (respetar mayúsculas y minúsculas):

Articulo: Nombre de la prenda.

Talle: S, M, L, XL, etc.

Precio Contado: El precio con descuento.

Precio Normal: El precio de lista.

Codigo: El código alfanumérico (ej: RB-001).

Cantidad: Cuántas etiquetas querés de esa prenda.

4. Ejecución
Cargá los datos en el Excel y ejecutá el script:
python generador_etiquetas.py

Esto te va a dejar un archivo llamado PDF_etiqueras.pdf listo para mandar a la impresora.

Importante: En la configuración de impresión, seleccionar siempre "Tamaño real" o "Escala 100%". No usar "Ajustar a página" porque se desfasan las medidas.