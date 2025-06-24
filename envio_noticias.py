import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import google.generativeai as genai
import requests
import traceback
from bs4 import BeautifulSoup

# Configuración general
DESTINATARIOS = "cjescobar37@gmail.com"
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
fecha_actual = datetime.now().strftime('%d/%m/%Y')
ASUNTO = f"Resumen Diario de Noticias - {fecha_actual}"

# Claves/API tokens
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
GNEWS_API_KEY = os.environ.get("GNEWS_API_KEY")
OPENWEATHER_KEY = os.environ.get("OPENWEATHER_KEY")

# Verificación inicial
print("🔐 Verificando claves:")
errores = []
for clave in ["EMAIL_PASSWORD", "GEMINI_API_KEY", "NEWS_API_KEY", "GNEWS_API_KEY", "OPENWEATHER_KEY"]:
    estado = "✅" if os.environ.get(clave) else "❌ FALTA"
    print(f"{clave}: {estado}")
    if not os.environ.get(clave):
        errores.append(f"❌ {clave} no definida.")

# Configurar Gemini
if not GEMINI_API_KEY:
    print("❌ Falta GEMINI_API_KEY"); exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# Noticias nacionales
def obtener_noticias():
    print("📰 Obteniendo noticias desde GNews...")
    if not GNEWS_API_KEY:
        return "No se pudo obtener noticias (falta GNEWS_API_KEY)."
    try:
        url = f"https://gnews.io/api/v4/top-headlines?lang=es&country=ar&max=5&token={GNEWS_API_KEY}"
        resp = requests.get(url)
        print("🔍 Status GNews:", resp.status_code)
        if resp.status_code != 200:
            return "No se pudo obtener noticias."
        data = resp.json().get("articles", [])
        if not data:
            return "No se encontraron noticias recientes."
        return "\n".join(f"- {a['title']} ({a['source']['name']})" for a in data)
    except Exception as e:
        errores.append("❌ Error al obtener noticias: " + str(e))
        return "No se pudieron obtener noticias."

# Clima
def obtener_clima():
    print("🌤️ Obteniendo clima...")
    if not OPENWEATHER_KEY:
        errores.append("❌ Falta OPENWEATHER_KEY")
        return "No se pudo obtener clima."
    try:
        params = {'q': 'Santa Rosa,AR', 'units': 'metric', 'appid': OPENWEATHER_KEY, 'lang': 'es'}
        resp = requests.get("https://api.openweathermap.org/data/2.5/weather", params=params)
        print("🔍 Status clima:", resp.status_code)
        if resp.status_code != 200:
            errores.append(f"❌ Error HTTP {resp.status_code} al obtener clima.")
            return "No se pudo obtener clima."
        r = resp.json()
        t = r["main"]
        w = r["weather"][0]
        return f"{t['temp']}°C, {w['description']}. Máx: {t['temp_max']}°C; Mín: {t['temp_min']}°C."
    except Exception as e:
        errores.append("❌ Error al obtener clima: " + str(e))
        return "No se pudo obtener clima."

# Dólar blue
def obtener_dolar():
    print("💰 Obteniendo cotización del dólar...")
    try:
        resp = requests.get("https://api.bluelytics.com.ar/v2/latest")
        print("🔍 Status dólar:", resp.status_code)
        if resp.status_code != 200:
            errores.append(f"❌ Error HTTP {resp.status_code} al obtener dólar.")
            return "No se pudo obtener dólar."
        data = resp.json()
        blue = data["blue"]
        return f"Blue compra: ${blue['value_buy']}, venta: ${blue['value_sell']}."
    except Exception as e:
        errores.append("❌ Error al obtener dólar: " + str(e))
        return "No se pudo obtener dólar."

# Eventos culturales locales (scraping)
def obtener_eventos_locales():
    print("🎭 Buscando eventos culturales locales (scraping)...")
    try:
        eventos = []

        # Telón Pampeano
        url_tp = "https://www.telonpampeano.com.ar/musica"
        resp_tp = requests.get(url_tp)
        soup_tp = BeautifulSoup(resp_tp.text, "html.parser")
        notas = soup_tp.find_all("div", class_="article")[:5]
        for nota in notas:
            titulo = nota.find("h2").text.strip()
            link = nota.find("a")["href"]
            eventos.append(f"- {titulo} ({link})")

        # Agenda Pampeana
        url_ap = "https://www.agendapampeana.com/"
        resp_ap = requests.get(url_ap)
        soup_ap = BeautifulSoup(resp_ap.text, "html.parser")
        entradas = soup_ap.select(".entry-title a")[:5]
        for entrada in entradas:
            titulo = entrada.text.strip()
            link = entrada["href"]
            eventos.append(f"- {titulo} ({link})")

        if not eventos:
            return "No se encontraron eventos culturales locales recientes."
        return "\n".join(eventos)
    except Exception as e:
        errores.append("❌ Error en scraping de eventos locales: " + str(e))
        return "No se pudieron obtener eventos culturales locales."

# Recolectar datos
noticias = obtener_noticias()
clima = obtener_clima()
dolar = obtener_dolar()
eventos = obtener_eventos_locales()

# Prompt para Gemini
prompt = f"""
Redactá un boletín informativo para hoy ({fecha_actual}), con tono periodístico, basado estrictamente en estos datos verificados:

CLIMA: {clima}
DÓLAR BLUE: {dolar}

NOTICIAS NACIONALES:
{noticias}

EVENTOS EN SANTA ROSA (culturales):
{eventos}

Estructura:
## 🗞️ Boletín Informativo Diario - {fecha_actual}
📍 LOCALES – Clima y eventos
🇦🇷 NACIONALES – Noticias
Terminá con “Este boletín es generado automáticamente.”
"""

# Generar boletín
def generar_bozon():
    print("✍️ Generando boletín con Gemini...")
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        resultado = model.generate_content(prompt)
        return resultado.text.strip()
    except Exception as e:
        errores.append("❌ Error al generar resumen con Gemini: " + str(e))
        return "No se pudo generar el resumen."

resumen = generar_bozon()

# Agregar errores al resumen si existen
if errores:
    resumen += "\n\n---\n🛑 Errores detectados:\n" + "\n".join(errores)

print("📰 Resumen generado:\n", resumen)

# Envío por email
html = resumen.replace("\n\n", "</p><p>").replace("\n", "<br>")
body = f"""<html><body><p>{html}</p><hr><p>Este boletín es generado automáticamente.</p></body></html>"""
msg = MIMEText(body, "html", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = DESTINATARIOS

try:
    print("📤 Enviando email...")
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as s:
        s.login(REMITENTE, CLAVE_APP)
        s.send_message(msg)
    print("✅ Email enviado.")
except Exception as e:
    print("❌ Error al enviar email:", e)
    errores.append("❌ Error al enviar el email: " + str(e))
