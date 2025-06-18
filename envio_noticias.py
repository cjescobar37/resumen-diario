import os
import smtplib
import openai
from email.mime.text import MIMEText
from datetime import datetime

# 📤 Configuración del correo
DESTINATARIOS = ["cjescobar37@gmail.com", "cristian.escobar@bancodelapampa.com.ar"]
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
ASUNTO = f"Resumen Diario de Noticias - {datetime.now().strftime('%d/%m/%Y')}"

# 🧠 Configuración de OpenAI
OPENAI_API_KEY = os.environ.get("OPENAI_API_KEY")
openai.api_key = OPENAI_API_KEY

# 🧾 Prompt para ChatGPT
prompt = """
Generame un resumen diario de noticias separadas por secciones, con prioridad a Argentina y especialmente a Santa Rosa (La Pampa), con un estilo de boletín diario informativo, claro y concreto.

Quiero que organices el contenido en 3 grandes bloques:

---

📍 LOCALES (Santa Rosa, La Pampa)
- Incluir eventos culturales importantes del día o semana: shows, bandas en vivo, obras de teatro, festivales, exposiciones, ferias, actividades públicas o gratuitas.
- Para cada evento indicá: nombre, lugar, fecha, hora, precio y si hay venta anticipada o entradas online.
- También incluí noticias relevantes de Santa Rosa o La Pampa si las hay (clima extremo, obras, transporte, sucesos importantes, visitas destacadas, etc.).

---

🇦🇷 NACIONALES (Argentina)
- Deportes: novedades de River Plate con prioridad, y cualquier suceso deportivo nacional relevante.
- Tecnología/Informática: innovaciones, lanzamientos o desarrollos argentinos destacados.
- Inversiones en Argentina: qué conviene seguir hoy (dólar, bonos, acciones, fintech, etc.).
- Breve resumen político/económico si hay algo importante hoy.
- Música argentina o espectáculos nacionales de interés general.

---

🌍 INTERNACIONALES
- Foco en innovaciones tecnológicas, nuevos inventos, avances científicos o ideas aplicables a la realidad argentina en informática o sistemas.
- También incluí 2 o 3 titulares globales relevantes de política, conflictos o economía si vale la pena saber.
- Muy breve y útil.

---

El resultado debe ser ordenado, simple de leer, como si fuera un informe que quiero recibir todas las mañanas. Sé claro, escueto y útil.
"""

# 🎯 Obtener respuesta de OpenAI, probando primero con GPT-4 y luego con GPT-3.5 si hay error
def obtener_resumen():
    try:
        print("Intentando con GPT-4...")
        respuesta = openai.ChatCompletion.create(
            model="gpt-4",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=1500,
            temperature=0.7,
        )
        return respuesta["choices"][0]["message"]["content"]
    except Exception as e:
        print(f"GPT-4 falló: {e}")
        try:
            print("Reintentando con GPT-3.5...")
            respuesta = openai.ChatCompletion.create(
                model="gpt-3.5-turbo",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.7,
            )
            return respuesta["choices"][0]["message"]["content"]
        except Exception as e2:
            return f"Error al obtener resumen con GPT-3.5 también: {e2}"

# Obtener el resumen
resumen = obtener_resumen()

# ✉️ Enviar el correo
msg = MIMEText(resumen, "plain", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = ", ".join(DESTINATARIOS)

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(REMITENTE, CLAVE_APP)
        server.sendmail(REMITENTE, DESTINATARIOS, msg.as_string())
    print("Correo enviado con éxito.")
except Exception as e:
    print(f"Error al enviar correo: {e}")
