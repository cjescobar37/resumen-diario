import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import google.generativeai as genai
import requests
import traceback

# Configuración del correo
DESTINATARIOS = "cjescobar37@gmail.com"
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
fecha_actual = datetime.now().strftime('%d/%m/%Y')
ASUNTO = f"Resumen Diario de Noticias - {fecha_actual}"

# Claves/API tokens
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
EVENTBRITE_TOKEN = os.environ.get("EVENTBRITE_TOKEN")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY")

# Verificación Gemini
if not GEMINI_API_KEY:
    print("❌ Falta GEMINI_API_KEY"); exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# 1️⃣ Noticias nacionales (NewsAPI)
def obtener_noticias():
    if not NEWS_API_KEY:
        return "No se pudieron obtener noticias (falta NEWS_API_KEY)."
    try:
        url = f"https://newsapi.org/v2/top-headlines?country=ar&apiKey={NEWS_API_KEY}&pageSize=5"
        data = requests.get(url).json().get("articles", [])
        return "\n".join(f"- {a['title']} ({a['source']['name']})" for a in data)
    except Exception as e:
        print("Error noticias:", e)
        return "No se pudieron obtener noticias."

# 2️⃣ Clima local (OpenWeatherMap)
def obtener_clima():
    if not OPENWEATHER_KEY:
        return "No se pudo obtener clima (falta OPENWEATHER_KEY)."
    try:
        params = {'q': 'Santa Rosa,Argentina', 'units': 'metric', 'appid': OPENWEATHER_KEY}
        r = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params).json()
        t = r["main"]
        w = r["weather"][0]
        return f"{t['temp']}°C, {w['description']}. Máx: {t['temp_max']}°C; Mín: {t['temp_min']}°C."
    except Exception as e:
        print("Error clima:", e)
        return "No se pudo obtener clima."

# 3️⃣ Dólar blue (Bluelytics)
def obtener_dolar():
    try:
        data = requests.get("https://api.bluelytics.com.ar/v2/latest").json()
        blue = data["blue"]
        return f"Blue compra: ${blue['value_buy']}, venta: ${blue['value_sell']}."
    except Exception as e:
        print("Error dólar:", e)
        return "No se pudo obtener dólar."

# 4️⃣ Eventos (Eventbrite)
def obtener_eventos():
    if not EVENTBRITE_TOKEN:
        return "No se pudieron obtener eventos (falta EVENTBRITE_TOKEN)."
    try:
        ahora = datetime.now().isoformat()
        fin = (datetime.now() + timedelta(days=90)).isoformat()
        resp = requests.get(
            "https://www.eventbriteapi.com/v3/events/search/",
            headers={"Authorization": f"Bearer {EVENTBRITE_TOKEN}"},
            params={
                "location.address": "Santa Rosa, La Pampa, Argentina",
                "start_date.range_start": ahora,
                "start_date.range_end": fin,
                "sort_by": "date",
                "expand": "venue"
            }
        ).json().get("events", [])
        if not resp:
            return "No se registran eventos en los próximos 90 días."
        lines = []
        for e in resp[:5]:
            name = e["name"]["text"]
            loc = e["venue"]["address"]["localized_address_display"]
            dt = e["start"]["local"]
            lines.append(f"- {name} en {loc}, {dt[:10]} a las {dt[11:16]}")
        return "\n".join(lines)
    except Exception as e:
        print("Error eventos:", e)
        return "No se pudieron obtener eventos."

# Recolectar datos
noticias = obtener_noticias()
clima = obtener_clima()
dolar = obtener_dolar()
eventos = obtener_eventos()

# Prompt a Gemini solo para redactar
prompt = f"""
Redactá un boletín informativo para hoy ({fecha_actual}), con tono periodístico, basado estrictamente en estos datos verificados:

CLIMA: {clima}
DÓLAR BLUE: {dolar}

NOTICIAS NACIONALES:
{noticias}

EVENTOS EN SANTA ROSA (próximos 90 días):
{eventos}

Estructura:
## 🗞️ Boletín Informativo Diario - {fecha_actual}
📍 LOCALES – Clima y eventos
🇦🇷 NACIONALES – Noticias
Terminá con “Este boletín es generado automáticamente.”
"""

def generar_bozon():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        return model.generate_content(prompt).text.strip()
    except Exception as e:
        print("Error Gemini:", traceback.format_exc())
        return "No se pudo generar el resumen."

resumen = generar_bozon()
print(resumen)

# Envío por email
html = resumen.replace("\n\n", "</p><p>").replace("\n", "<br>")
body = f"""<html><body><p>{html}</p><hr><p>Este boletín es generado automáticamente.</p></body></html>"""
msg = MIMEText(body, "html", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = DESTINATARIOS

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(REMITENTE, CLAVE_APP)
        s.send_message(msg)
    print("✅ Email enviado.")
except Exception as e:
    print("❌ Error al enviar email:", e)


