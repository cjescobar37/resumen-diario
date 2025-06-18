import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import google.generativeai as genai
import traceback

# 📤 Configuración del correo
DESTINATARIOS = ["cjescobar37@gmail.com", "cristian.escobar@bancodelapampa.com.ar"]
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
ASUNTO = f"Resumen Diario de Noticias - {datetime.now().strftime('%d/%m/%Y')}"

# 🧠 Configuración de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ No se encontró la API Key de Gemini.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# 🧾 Prompt
prompt = """
Generame un resumen diario de noticias separadas por secciones, con prioridad a Argentina y especialmente a Santa Rosa (La Pampa), con un estilo de boletín diario informativo, claro y concreto.

Quiero que organices el contenido en 3 grandes bloques:

📍 LOCALES (Santa Rosa, La Pampa)
- Incluir eventos culturales importantes del día o semana: shows, bandas en vivo, obras de teatro, festivales, exposiciones, ferias, actividades públicas o gratuitas.
- Para cada evento indicá: nombre, lugar, fecha, hora, precio y si hay venta anticipada o entradas online.
- También incluí noticias relevantes de Santa Rosa o La Pampa si las hay (clima extremo, obras, transporte, sucesos importantes, visitas destacadas, etc.).

🇦🇷 NACIONALES (Argentina)
- Deportes: novedades de River Plate con prioridad, y cualquier suceso deportivo nacional relevante.
- Tecnología/Informática: innovaciones, lanzamientos o desarrollos argentinos destacados.
- Inversiones en Argentina: qué conviene seguir hoy (dólar, bonos, acciones, fintech, etc.).
- Breve resumen político/económico si hay algo importante hoy.
- Música argentina o espectáculos nacionales de interés general.

🌍 INTERNACIONALES
- Foco en innovaciones tecnológicas, nuevos inventos, avances científicos o ideas aplicables a la realidad argentina en informática o sistemas.
- También incluí 2 o 3 titulares globales relevantes de política, conflictos o economía si vale la pena saber.
- Muy breve y útil.
"""

# 🎯 Obtener el resumen desde Gemini
def obtener_resumen():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Error al generar el resumen con Gemini:")
        traceback.print_exc()
        return "No se pudo generar el resumen."

# ✨ Obtener resumen
resumen = obtener_resumen()
print("\n📰 Resumen generado:\n")
print(resumen)

# ✉️ Preparar y enviar email
msg = MIMEText(resumen, "plain", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = ", ".join(DESTINATARIOS)

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(REMITENTE, CLAVE_APP)
        server.sendmail(REMITENTE, DESTINATARIOS, msg.as_string())
    print("✅ Correo enviado con éxito.")
except Exception as e:
    print(f"❌ Error al enviar correo: {e}")
