# Jornadas 2025 - Envío de Correos con QR de Asistencia

Este proyecto está diseñado para gestionar el envío de correos electrónicos con códigos QR de asistencia para inscriptos a charlas y actividades en el marco de las Jornadas 2025.

## 📁 Estructura del Proyecto

jornadas2025/
│
├── actividades/ # contiene el template html de las inscripciones a las charlas de cada departamento
├── css/ # estilos
├── fonts/ # contiene fuentes personalizadas
├── home/ # Contiene el template HTML de la página principal
├── img/ # logos, graficos, fotos de disertantes y sponsors
├── inscripciones/ # carpeta con csv de inscripciones organizados por departamento o tipo de charla
│   └── sistemas/
        ...    └── /originales/ # csv originales sin procesar
               │             └── /s-01.csv
               │             ...
        ...    └── /procesadas/ # contiene sub carpeta por cada charla
                    └── /s-01/ # csv depurados por el script limpiar y csv con informe de errores de los registros de inscripciones
                    ...      └── s-01.csv # csv limpio
                    ...      └── errores.csv # registros que no pasaron la limpieza
        ...         ...      └── dominios.csv # conteo de dominios de correos 
        
        
├── js/ # java script para el home y templates de la carpeta actividades
├── scripts/ # Scripts para limpieza, generación de QR y envío de correos
       └── logs/  # Registro de envíos exitosos o con error
---

## 🧩 Scripts

### 1. `limpieza.py`

- **Objetivo:**  
  Normaliza y depura los archivos CSV de inscripciones.
  
- **Qué hace:**  
  - Elimina registros inválidos o incompletos.
  - Genera un nuevo archivo CSV limpio por charla.
  - Genera un archivo CSV con los registros que contenian errores y otro con un agrupamiento y conteo de dominios de correos
  - La re ejecución del script sobrescribe todos los archivos generados en la última ejecución.
---

### 2. `generar_qr_asistencia.py`

- **Objetivo:**  
  Generar un código QR con los datos de la charla dada y lo coloca sobre una template de imagen.

- **Qué hace:**  
  - Parte de un imagen como template
  - Agrega un título con el nombre de la charla.
  - Inserta el código QR con la información del asistente y el codigo de charla.

---

### 3. `enviar_correos.py`

- **Objetivo:**  
  Enviar correos electrónicos con el QR de asistencia a los inscriptos en cada charla.

- **Cómo funciona:**  
  - Recorre los archivos CSV ya procesados y limpios.
  - Por cada inscripción, genera y adjunta un QR de asistencia personalizado.
  - **Registra los envíos en `logs/enviar_correos.log`** con estado `ÉXITO` o `ERROR`.

- **Evita envíos duplicados:**  
  - Antes de enviar un correo, verifica si ya fue enviado correctamente anteriormente.
  - Si encuentra un registro exitoso para ese correo y charla, lo saltea.
  - Si el envío anterior falló o es la primera vez, intenta enviar nuevamente.

- **Reintentos seguros:**  
  - Permite relanzar el script múltiples veces para completar envíos fallidos o nuevos registros.

- **Reenvio a todos:**
  - Cuenta con una FLAG llamada REINTENTAR_TODOS, que permite ejecutar el script sin la validación de si se está enviando el correo por primera vez o no. 
  - Esto permite hacer un reenvio masivo sin necesidad de borrar el historial del log.

---

## 🛠️ Requisitos

- Python 3.8+
- Bibliotecas:
  - `pandas`
  - `qrcode`
  - `smtplib`
  - `python-dotenv`
  - `Jinja2`
  
## Ejecución del Proyecto

A continuación, se detallan los pasos para ejecutar este proyecto localmente:

1.  **Crear Entorno Virtual (Recomendación)**

    Para evitar conflictos con otras instalaciones de Python en tu sistema. Puedes crear un entorno virtual utilizando `venv` (para Python 3) o `virtualenv`.

    **Ejemplo usando `venv`:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # En Linux/macOS
    .\venv\Scripts\activate  # En Windows
    ```

2.  **Instalación de Dependencias**

    Instalar todas las dependencias necesarias con el siguiente comando:

    ```bash
    pip install -r requirements.txt
    ```
3.  **Crear .env** 
    Crea un .env con las credenciales del correo electrónico a utilizar en el script de envio de correos

4.  **Ejecución Local**

    Para ejecutar el proyecto localmente, puedes utilizar el servidor HTTP simple de Python. Abre una terminal en la raíz del proyecto y ejecuta el siguiente comando:

    ```bash
    python -m http.server 8000
    ```

    Esto iniciará un servidor web local en la dirección `http://localhost:8000`.

## Guía para Limpieza de datos y Envío de mails:

1. **Crear Carpetas para los csv de las inscripciones**
   - Dentro de jornadas2025 crear una carpeta que se llame 'inscripciones'
   - Dentro de 'inscripciones' crear una carpeta por cada depto o tipo de charla (sistemas,basicas,magistral, etc.)
   - Dentro de cada una de esas carpetas crear una carpeta que se llame 'originales'. Allí se deberán guardar los csv de las inscripciones a procesar. Los csv guardados deberán tener como nombre un código de charla a elección propia, por ejemplo: s-01.csv(para la charla 1 de sistemas),cm-01(para la charla 1 de magistral), etc.
   - Dentro de la carpeta 'inscripciones' crear un archivo csv 'tabla-de-referencias.csv' que contenga: codigo de charla, nombre de charla y aula. Deberá rellenarse con la info correspondiente a cada charla. Este archivo será necesario para obtener el nombre de las charlas y nombre de aula, a partir del código de charla.
   - Nota: Tener cuidado con la consistencia de los nombres. Los nombres de los csv originales deben coincidir con los codigos de las charlas definidos en 'tabla-de-referencias.csv'.

2. **Limpieza de datos**
   - Para depurar los csv de inscripciones, ejecutar el script 'limpieza.py'. Esto normalizará los datos y filtrará registros con errores.
   - Los resultados de la limpieza se guardaran en la carpeta 'procesadas' que se genera automáticamente dentro de la carpeta de cada charla.
   - Se van a generar 3 archivos csv: uno con los registros que tuvieron errores y no pasaron el filtro, otro con un conteo de dominios de correos electrónicos, y el último será el csv ya depurado y que se usará para armar los mails y generar los QR.

3. **Envío de mails**
   - Para hacer el envio de mails es requisito previo haber generado los csv ya depurados con el script de 'limpieza.py'.
   - Ejecutar el script 'envio_de_correos.py'
   - Al ejecutarlo se enviarán los correos con los QR generados para cada inscripción y se guardará un registro del envio (ya sea exitoso o fallido) en 'scripts/logs/lenviar_correos.log'.
   - En caso de re ejecutar el script, los correos se enviaran solo a los envío fallidos registrados en el log, y a aquellos nuevos registros que hayan sido agregados en los csv depurados (si es que se agregaron nuevos registros desde la última ejecución)
   - Para hacer un re envío masivo a todos sin validación de los logs, activar la FLAG 'REINTENTAR_TODOS' cambiandola a 'True'


