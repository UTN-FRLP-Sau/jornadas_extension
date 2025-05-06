from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.image import MIMEImage
from smtplib import SMTP
from jinja2 import Template
import pandas as pd
import qrcode
#from certificado import generar_certificado

# Alias
# Alias de correo, normalemnte es el mismo que el smtp_user
alias = 'jornadas@frlp.utn.edu.ar'
# el correo que usas para enviar los mensajes
smtp_user = 'jornadas@frlp.utn.edu.ar'
smtp_pass = 'J0rn4d45_2023$$__'  # password de la cuenta de correo


# Taplate en html, usando jinja2
asunto = 'QR - Economía y Desarrollo'
archivo_template = 'template.html'


def envio_correo(i, j, nombre, apellido, correo):
    msg['To'] = '%s' % (correo)
    try:
        smtp.sendmail(msg['From'], msg['To'], msg.as_string())
        s = (i, j, nombre, apellido, 'ok', correo)
    except:
        smtp.close()
        k = 0
        s = 'Error, reintentar'
        print(i, correo)
        exit()
    return (s)


# Obtencion de las lista de destinatarios y archivos
# Deben estar todos dentro de la misma carpeta
#registros = pd.read_excel('data1.xlsx', engine='openpyxl')

# para testear, sobreescribe la lista registros por un dado
# comentar para enviar el correo a los desinatarios
# armar el diccionario con las columnas de CSV
dic= {
    'correo':'jorge.ronconi@gmail.com',
    'dni': 12345678,
    'legajo': 23364,
    'Nombre': 'Jorge',
    'charla': 'Economía y Desarrollo',
    'apellido': 'Ronconi',
    }
registros=pd.DataFrame(dic,index=[0])

# Crear una instancia del servidor para envio de correo (hacerlo una sola vez)
smtp = SMTP("smtp.office365.com", 587)

i = 0  # contador de registros
j = len(registros)  # cantidad de registros
k = 0  # contador de envios por ciclo
k_max = 10  # maximo de envios por ciclo

while i < j:
    if k == 0:
        print('abrir coneccion')
        # Iniciar sesión en el servidor (si es necesario):
        smtp.connect("smtp.office365.com", 587)
        smtp.ehlo()
        smtp.starttls()
        # Tu usuario y tu contraseña
        smtp.login(smtp_user, smtp_pass)

    k = k+1
    # apellido, nombre = str(registros.loc[i, 'nombre']).split(',')
    nombre = str(registros.loc[i, 'Nombre']).title().strip()
    # apellido = str(registros.loc[i, 'Apellido']).upper().strip()
    apellido = ''

    dni = int(registros.loc[i, 'dni'])
    charla = str(registros.loc[i, 'charla']).upper().strip()
    correo = str(registros.loc[i, 'correo']).lower().strip()

    img = qrcode.make("{}-{}".format(charla, dni))
    img.save('qr.png')

    # Si tiene mas de un correo, tomamos los 2 y enviamos a ambos el mensaje
    # En el caso de q uno este vacio no se envia nada
    msg = MIMEMultipart()
    msg['Subject'] = asunto
    msg['From'] = alias
    # Armado del mensjae con jinga desde el template
    temp = open(archivo_template, encoding="utf-8").read()
    dic = {
        'nombre': nombre,
        # 'apellido': apellido
    }
    mensage = Template(temp).render(dic)

    # Esta es la parte textual:
    part = MIMEText(mensage, 'html')
    msg.attach(part)

    # Esta es la imagen a embeber
    fp = open('qr.png', 'rb')
    flayer = MIMEImage(fp.read())
    fp.close()
    # fp = open('template/QR.png', 'rb')
    # qr = MIMEImage(fp.read())
    # fp.close()
    # Define the image's ID as referenced above
    flayer.add_header('Content-ID', '<qr_entrada>')
    # qr.add_header('Content-ID', '<qr>')
    # msg.attach(qr)
    msg.attach(flayer)

    # Esta es la parte binaria (puede ser cualquier extensión):
    # archivo='becaypf.png'
    # part = MIMEApplication(open("%s" %(archivo),"rb").read())
    # part.add_header('Content-Disposition', 'attachment', filename="BecaYPF.png")
    # msg.attach(part)
    # Enviar el mail (o los mails) a grupos especificos
    s1 = envio_correo(i, j, nombre, apellido, correo)
    print(s1)

    # Cada 10 correos, reinicia la coneccion al SMTP
    if k == k_max:
        print('cerrar coneccion')
        smtp.close()
        k = 0
    elif i == j-1:
        print('cerrar coneccion')
        smtp.close()
        k = 0
    i = i+1
