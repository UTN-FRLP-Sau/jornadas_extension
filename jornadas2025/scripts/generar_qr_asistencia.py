import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap
import csv

def transformar_codigo_charla_a_nombre_charla(codigo_charla):
    """
    Transforma un código de charla en el nombre legible de la charla, 
    buscando en el archivo CSV de referencias.
    """
    ruta_csv = os.path.join(os.path.dirname(__file__), '..', 'inscripciones', 'tabla-de-referencias.csv')
    try:
        with open(ruta_csv, encoding='utf-8') as archivo:
            lector = csv.reader(archivo, delimiter=';')
            for fila in lector:
                if len(fila) < 3:
                    continue
                codigo, nombre, _ = fila
                if codigo.strip() == codigo_charla:
                    return nombre.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_csv}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return codigo_charla

def ajustar_texto(texto, fuente_path, box_width, box_height, font_size):
    """
    Ajusta el texto para que entre en un recuadro con tamaño de fuente fijo.
    Si el texto no cabe, ajusta el ancho de línea manteniendo el tamaño de fuente.
    """
    try:
        font = ImageFont.truetype(fuente_path, font_size)
    except:
        font = ImageFont.load_default()
    
    # Ajusta el ancho de línea para que el texto quepa
    wrap_width = 30  # Valor inicial
    lines = textwrap.wrap(texto, width=wrap_width)
    
    # Calcula dimensiones del texto
    total_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] + 10 for line in lines])
    max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
    
    # Ajusta el ancho de línea si es necesario
    while (total_height > box_height or max_line_width > box_width) and wrap_width > 10:
        wrap_width -= 1
        lines = textwrap.wrap(texto, width=wrap_width)
        total_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] + 10 for line in lines])
        max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])

    return lines, font

def generar_qr_asistencia(info, codigo_charla):
    """
    Genera un QR con la info de la inscripcion y un texto personalizado con tamaño de fuente fijo.
    """
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'template.jpg')
        template = Image.open(template_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró el archivo template.jpg en el directorio")

    # Generar QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(info)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")

    if not isinstance(img_qr, Image.Image):
        img_qr = img_qr.get_image()

    img_qr = img_qr.resize((700, 700), Image.Resampling.LANCZOS)
    qr_position = (100, 700)
    template.paste(img_qr, qr_position)

    # Obtengo nombre de la charla
    nombre_charla = transformar_codigo_charla_a_nombre_charla(codigo_charla)
    texto_final = f"QR de asistencia a:\n{nombre_charla}"

    draw = ImageDraw.Draw(template)
    text_config = {
        'position': (90, 300),
        'box_size': (720, 420),
        'font_size': 55,
        'color': (44, 78, 254)
    }

    # Configura fuente
    fuente_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Planc-wfx', 'Planc-Bold.otf')
    
    # Ajusta texto con tamaño de fuente fijo
    lines, font = ajustar_texto(
        texto_final, 
        fuente_path, 
        text_config['box_size'][0], 
        text_config['box_size'][1],
        text_config['font_size']
    )

    x, y = text_config['position']
    box_width, box_height = text_config['box_size']
    
    # Dibuja recuadro rojo (solo para DEBUG)
    '''draw.rectangle(
        [text_config['position'], 
        (text_config['position'][0] + text_config['box_size'][0],
         text_config['position'][1] + text_config['box_size'][1])],
        outline="red",
        width=3
    )'''

    # Posicionamiento del texto
    y_start = y
    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_position = x + (box_width - text_width) // 2
        draw.text((x_position, y_start), line, font=font, fill=text_config['color'])
        y_start += text_height + 10

    # Guarda el resultado
    output_path = os.path.join(os.path.dirname(__file__), 'qr_generado.png')
    template.save(output_path)
    return output_path

if __name__ == '__main__':
    info_ejemplo = "m-09;311;4423"
    path = generar_qr_asistencia(info_ejemplo, codigo_charla="m-09")
    print(f"QR generado en: {path}")