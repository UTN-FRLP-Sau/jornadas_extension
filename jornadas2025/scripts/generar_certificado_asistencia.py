import os
import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap

def generar_certificado_con_qr(info, nombre_charla):
    """
    Genera un certificado con QR y texto personalizado.
    
    Args:
        info (str): Datos para el QR
    """
    try:
        # Carga la plantilla base
        template_path = os.path.join(os.path.dirname(__file__), 'template.jpg')
        certificado = Image.open(template_path).convert("RGB")
    except FileNotFoundError:
        raise FileNotFoundError("No se encontró el archivo template.jpg en el directorio")
    
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
    qr_size = (700, 700)
    img_qr = img_qr.resize(qr_size, Image.Resampling.LANCZOS)
    
    # Posicion del QR
    qr_position = (100, 700)
    certificado.paste(img_qr, qr_position)
    
    # titulo
    texto = f"QR de asistencia a:\n\n\n{nombre_charla}"


    # configuracion de texto
    draw = ImageDraw.Draw(certificado)
    text_config = {
        'position': (200, 150),  # (x, y)
        'box_size': (500, 500),   # (width, height)
        'font_size': 60,
        'color': (44, 78, 254)  # Azul personalizado
    }

   # Ruta absoluta a la fuente, partiendo desde el archivo actual (tu_script.py)
    fuente_path = os.path.join(os.path.dirname(__file__), '..', 'fonts', 'Planc-wfx', 'Planc-Bold.otf')

    try:
        font = ImageFont.truetype(fuente_path, text_config['font_size'])
    except Exception as e:
        print(f"No se pudo cargar la fuente personalizada: {e}")
        font = ImageFont.load_default()

    # Ajusta texto al tamaño de caja
    lines = texto.split('\n')
    
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
    path = generar_certificado_con_qr(info_ejemplo,nombre_charla="Charla de Ejemplo")
    print(f"Certificado generado en: {path}")
