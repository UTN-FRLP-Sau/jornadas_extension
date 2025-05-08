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
                if len(fila) < 2:
                    continue
                codigo, nombre = fila
                if codigo.strip() == codigo_charla:
                    return nombre.strip()
    except FileNotFoundError:
        print(f"Archivo no encontrado: {ruta_csv}")
    except Exception as e:
        print(f"Error al leer el archivo CSV: {e}")
    return codigo_charla

def ajustar_texto(texto, fuente_path, box_width, box_height, font_size):
    """
    Ajusta el texto para que entre en un recuadro, aumentando el tamaño de fuente hasta que encaje.
    Si una palabra no cabe en la línea, se mueve automáticamente a la siguiente línea.
    """
    font = ImageFont.truetype(fuente_path, font_size)
    lines = textwrap.wrap(texto, width=40)  # Ajuste inicial con tamaño de fuente
    total_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] + 10 for line in lines])
    max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])
    
    # Si el texto no cabe, reducimos el tamaño de la fuente
    while total_height > box_height or max_line_width > box_width:
        font_size -= 2  # Reducimos el tamaño de la fuente
        if font_size < 10:  # Para evitar que el tamaño de la fuente sea demasiado pequeño
            break
        font = ImageFont.truetype(fuente_path, font_size)
        lines = textwrap.wrap(texto, width=40)
        total_height = sum([font.getbbox(line)[3] - font.getbbox(line)[1] + 10 for line in lines])
        max_line_width = max([font.getbbox(line)[2] - font.getbbox(line)[0] for line in lines])

    return lines, font

def generar_qr_asistencia(info, codigo_charla):
    """
    Genera un certificado con QR y texto personalizado.
    """
    try:
        template_path = os.path.join(os.path.dirname(__file__), 'template.jpg')
        certificado = Image.open(template_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró el archivo template.jpg en el directorio")

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
    certificado.paste(img_qr, qr_position)

    nombre_charla = transformar_codigo_charla_a_nombre_charla(codigo_charla)
    texto_final = f"QR de asistencia a:\n{nombre_charla}"

    draw = ImageDraw.Draw(certificado)
    text_config = {
        'position': (90, 300),
        'box_size': (720, 420),
        'font_size': 90,
        'color': (44, 78, 254)
    }

    fuente_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Planc-wfx', 'Planc-Bold.otf')
    try:
        _ = ImageFont.truetype(fuente_path, text_config['font_size'])
    except Exception as e:
        print(f"No se pudo cargar la fuente personalizada: {e}")
        fuente_path = None

    # Si la fuente se carga correctamente, ajusta el texto con la fuente personalizada
    if fuente_path:
        lines, font_ajustada = ajustar_texto(texto_final, fuente_path, text_config['box_size'][0], text_config['box_size'][1], text_config['font_size'])
    else:
        font_ajustada = ImageFont.load_default()
        lines = textwrap.wrap(texto_final, width=40)

    x, y = text_config['position']
    box_width, box_height = text_config['box_size']
    total_height = sum([font_ajustada.getbbox(line)[3] - font_ajustada.getbbox(line)[1] + 10 for line in lines])
    y_start = y

    # Visualizar el box de texto con un borde (para debug)
    draw.rectangle(
        [text_config['position'], 
        (text_config['position'][0] + text_config['box_size'][0],
        text_config['position'][1] + text_config['box_size'][1])],
        outline="red",
        width=3
    )

    for line in lines:
        bbox = font_ajustada.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_position = x + (box_width - text_width) // 2
        draw.text((x_position, y_start), line, font=font_ajustada, fill=text_config['color'])
        y_start += text_height + 10

    output_path = os.path.join(os.path.dirname(__file__), 'certificado_generado.png')
    certificado.save(output_path)
    return output_path

if __name__ == '__main__':
    info_ejemplo = "c01;311;4423"
    path = generar_qr_asistencia(info_ejemplo, codigo_charla="ma-01")
    print(f"Certificado generado en: {path}")
