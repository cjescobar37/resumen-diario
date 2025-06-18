import smtplib
from email.mime.text import MIMEText
from datetime import datetime

# Parámetros
DESTINATARIOS = ["cjescobar37@gmail.com", "cristian.escobar@bancodelapampa.com.ar"]
REMITENTE = "polyescseguridad@gmail.com"
import os
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
ASUNTO = f"Resumen Diario de Noticias - {datetime.now().strftime('%d/%m/%Y')}"

# Contenido del resumen (simulado)
resumen = """
📰 Resumen Diario de Noticias - Argentina, Santa Rosa (La Pampa) y el Mundo

🇦🇷 Argentina:
- Política: El Gobierno debate nuevas medidas fiscales.
- Tecnología: Una startup argentina crea un sensor IoT para el agro.
- Inversiones: Dólar MEP sube a $1240. Bonos en alza.
- Deportes: River venció 2-1 a San Lorenzo y lidera.
- Música: Wos anuncia show en Rosario.
- Eventos en Santa Rosa: Feria del Libro en el CMC (18 al 22 junio), obra "La Mentira" en Teatro Español.

🌎 Internacional:
- Apple lanza iOS 19 con funciones de IA.
- Elon Musk presenta robot humanoide de Tesla.
- Bitcoin rebota a USD 68.000.
"""

# Crear email
msg = MIMEText(resumen, "plain", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = ", ".join(DESTINATARIOS)

# Enviar
try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 487) as server:
        server.login(REMITENTE, CLAVE_APP)
        server.sendmail(REMITENTE, DESTINATARIOS, msg.as_string())
    print("Correo enviado con éxito.")
except Exception as e:
    print(f"Error al enviar correo: {e}")
