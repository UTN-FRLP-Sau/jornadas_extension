import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generar_certificado_con_qr(info):
    """
    Genera un certificado con QR y texto personalizado.
    
    Args:
        info (str): Datos para el QR
    """
    try:
        # Carga la plantilla base
        template_path = os.path.join(os.path.dirname(__file__), 'template.png')
        certificado = Image.open(template_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró el archivo template.png en el directorio")
    
    # Genera el QR
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_L,
        box_size=10,
        border=4,
    )
    qr.add_data(info)
    qr.make(fit=True)
    img_qr = qr.make_image(fill_color="black", back_color="white")
    
    # Convierte a PIL Image si es necesario
    if not isinstance(img_qr, Image.Image):
        img_qr = img_qr.get_image()
    
    # Redimensiona el QR
    qr_size = (600, 600)
    img_qr = img_qr.resize(qr_size, Image.Resampling.LANCZOS)
    
    # Posicion del QR
    qr_position = (250, 750)
    certificado.paste(img_qr, qr_position)
    
    # titulo
    texto = "Este es tu QR de asistencia!"

    # configuracion de texto
    draw = ImageDraw.Draw(certificado)
    text_config = {
        'position': (300, 200),  # (x, y)
        'box_size': (500, 500),   # (width, height)
        'font_size': 80,
        'color': 'black'
    }

    # Intenta cargar fuente personalizada o usar default
    try:
        font = ImageFont.truetype("arial.ttf", text_config['font_size'])
    except:
        font = ImageFont.load_default()

    # Ajusta texto al tamaño de caja
    lines = textwrap.wrap(texto, width=20)
    
    # Calcular posicion vertical inicial
    x, y = text_config['position']
    box_width, box_height = text_config['box_size']
    total_text_height = sum([font.getbbox(line)[3] for line in lines])
    y_start = y + (box_height - total_text_height) // 2
    
    # Dibuja cada linea de texto
    for line in lines:
        bbox = font.getbbox(line)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        x_position = x + (box_width - text_width) // 2
        draw.text((x_position, y_start), line, font=font, fill=text_config['color'])
        y_start += text_height + 20
    
    # ruta de salida dentro de la funcion
    output_path = os.path.join(os.path.dirname(__file__), 'certificado_generado.png')
    
    # Guarda el certificado
    certificado.save(output_path)
    return output_path

# para probar la funcion
if __name__ == '__main__':
    # Ejemplo de uso
    info_ejemplo = "c01;311;4423"
    
    # Generar certificado con QR
    path = generar_certificado_con_qr(info_ejemplo)
    print(f"Certificado generado en: {path}")
