import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap


import qrcode
from PIL import Image, ImageDraw, ImageFont
import textwrap


def generar_certificado(dni, apellido, nombre_charla, template_path, output_path,
                        font_path="arial.ttf", text_position=(300, 100),
                        text_box_size=(600, 200), font_size=75):

    # Generar contenido del QR
    qr_data = f"{dni}-{apellido}"
    qr_img = qrcode.make(qr_data)
    qr_img = qr_img.resize((600, 600))  # tamaño del QR
    
    # Cargar template
    template = Image.open(template_path).convert("RGB")
    # Obtener dimensiones del template
    template_width, template_height = template.size
    # Ajustar posición del QR si es necesario
    qr_position = (template_width // 2 - qr_img.size[0] // 2, (template_height - qr_img.size[1])//2+100)
    
    # Pegar QR en el template
    template.paste(qr_img, qr_position)

    # Preparar fuente y dibujo
    draw = ImageDraw.Draw(template)
    font = ImageFont.truetype(font_path, font_size)

    # Ajustar texto al tamaño de caja
    max_width, max_height = text_box_size


    # Probar tamaños de fuente desde grande a menor hasta que entre
    max_font_size = 60
    min_font_size = 10
    final_font = None
    final_lines = []

    for font_size in range(max_font_size, min_font_size - 1, -1):
        font = ImageFont.truetype(font_path, font_size)
        lines = textwrap.wrap(nombre_charla, width=40)

        # Medir si cada línea entra en ancho, y el total en alto
        fits = True
        total_height = 0
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_height = bbox[3] - bbox[1]
            if line_width > text_box["width"]:
                fits = False
                break
            total_height += line_height + 5
        if fits and total_height <= text_box["height"]:
            final_font = font
            final_lines = lines
            break

    # Dibujar el texto centrado verticalmente
    if final_font:
        y = text_box["y"] + (text_box["height"] - total_height) // 2
        for line in final_lines:
            bbox = draw.textbbox((0, 0), line, font=final_font)
            line_width = bbox[2] - bbox[0]
            x = text_box["x"] + (text_box["width"] - line_width) // 2
            draw.text((x, y), line, font=final_font, fill="black")
            y += bbox[3] - bbox[1] + 5

     # Guardar imagen final
    template.save(output_path)



generar_certificado(
    dni="12345678",
    apellido="Pérez",
    nombre_charla="Introducción a la Ingeniería Civil: desafíos del siglo XXI",
    template_path="template.png",
    output_path="cert_final.png",
    # Ajustalo según tu sistema
    font_path="C:/Users/Usuario/Desktop/GitHub/cneisi/src/static/fonts/Planc_wfx/Planc-SemiBold.otf",
)
