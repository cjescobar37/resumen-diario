import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime, timedelta
import google.generativeai as genai
import requests
import traceback

# 📤 Configuración del correo
DESTINATARIOS = "cjescobar37@gmail.com"
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
fecha_actual = datetime.now().strftime('%d/%m/%Y')
ASUNTO = f"Resumen Diario de Noticias - {fecha_actual}"

# 🔑 API Keys
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
NEWS_API_KEY = os.environ.get("NEWS_API_KEY")
EVENTBRITE_TOKEN = os.environ.get("EVENTBRITE_TOKEN")

# ✅ Verificar API de Gemini
if not GEMINI_API_KEY:
    print("❌ No se encontró la API Key de Gemini.")
    exit(1)
genai.configure(api_key=GEMINI_API_KEY)

# 📰 Obtener noticias desde NewsAPI
def obtener_noticias():
    if not NEWS_API_KEY:
        return "No se pudo acceder a noticias reales (falta clave API)."

    try:
        url = f"https://newsapi.org/v2/top-headlines?country=ar&pageSize=5&apiKey={NEWS_API_KEY}"
        response = requests.get(url)
        noticias = response.json().get("articles", [])
        resultado = ""
        for noticia in noticias:
            resultado += f"- {noticia['title']} ({noticia['source']['name']})\n"
        return resultado.strip()
    except Exception as e:
        print("❌ Error al obtener noticias:", e)
        return "No se pudieron obtener noticias reales."

# 🎭 Obtener eventos culturales desde Eventbrite
def obtener_eventos_locales():
    if not EVENTBRITE_TOKEN:
        return "No se pudo acceder a eventos porque falta la clave de Eventbrite."

    try:
        hoy = datetime.now().isoformat()
        dentro_90_dias = (datetime.now() + timedelta(days=90)).isoformat()
        url = "https://www.eventbriteapi.com/v3/events/search/"
        params = {
            "location.address": "Santa Rosa, La Pampa, Argentina",
            "location.within": "20km",
            "start_date.range_start": hoy,
            "start_date.range_end": dentro_90_dias,
            "sort_by": "date",
            "expand": "venue"
        }

        headers = {
            "Authorization": f"Bearer {EVENTBRITE_TOKEN}"
        }

        response = requests.get(url, headers=headers, params=params)
        eventos = response.json().get("events", [])

        if not eventos:
            return "No se registran eventos para hoy ni en los próximos días."

        resultado = ""
        for e in eventos[:5]:  # Primeros 5 eventos
            nombre = e.get("name", {}).get("text", "Sin nombre")
            lugar = e.get("venue", {}).get("address", {}).get("localized_address_display", "Lugar no disponible")
            fecha = e.get("start", {}).get("local", "Fecha no disponible")
            precio = "Consultar"
            entradas = e.get("url", "Sin enlace")
            resultado += f"- {nombre} 📍 {lugar} 📅 {fecha[:10]} 🕓 {fecha[11:16]} 🎟️ {precio} 🔗 {entradas}\n"

        return resultado.strip()
    except Exception as e:
        print("❌ Error al obtener eventos:", e)
        return "No se pudieron obtener eventos locales."

# 📦 Combinar datos reales y generar prompt para Gemini
noticias_arg = obtener_noticias()
eventos_locales = obtener_eventos_locales()

prompt = f"""
Hoy es {fecha_actual}.

🔹 Estas son algunas noticias nacionales actuales extraídas de medios reales:
{noticias_arg}

🔹 Estos son eventos culturales en Santa Rosa:
{eventos_locales}

Generá un boletín informativo diario con el siguiente formato y estilo periodístico, con prioridad en eventos de Santa Rosa (La Pampa) y noticias nacionales relevantes para Argentina. El contenido debe ser preciso, claro y dividido por secciones.

Estructura:
## 🗞️ Boletín Informativo Diario - {fecha_actual}

📍 LOCALES | Santa Rosa, La Pampa
🎭 Eventos culturales:
- Si hay eventos hoy, listarlos con: nombre, lugar, fecha, hora, precio y si hay entradas online o anticipadas.
- Si no hay eventos hoy, buscá eventos destacados dentro de los próximos 90 días y listalos ordenados por fecha. Si aún no hay, escribir: “No se registran eventos para hoy ni en los próximos días.”
📰 Noticias relevantes: clima, obras públicas, visitas oficiales, emergencias, etc.

🇦🇷 NACIONALES
⚽ Deportes (River Plate + otro deporte importante)
💻 Tecnología e informática nacional
💹 Inversiones: dólar, mercado financiero, fintech (usar datos simulados si no hay reales)
🏛️ Política/Economía: resumen breve si hay novedades
🎶 Música / espectáculos: eventos o lanzamientos de interés general

🌍 INTERNACIONALES
🚀 Innovaciones tecnológicas con utilidad para Argentina
🌐 Noticias globales importantes (máx 3 titulares)

Terminá con una nota aclaratoria: “Este boletín es generado automáticamente.”

Usá un tono informativo, claro y ordenado.
"""

# 🤖 Obtener el resumen generado
def obtener_resumen():
    try:
        model = genai.GenerativeModel("gemini-1.5-flash")
        response = model.generate_content(prompt)
        return response.text.strip()
    except Exception as e:
        print("❌ Error al generar el resumen con Gemini:")
        traceback.print_exc()
        return "No se pudo generar el resumen."

resumen = obtener_resumen()
print("\n📰 Resumen generado:\n")
print(resumen)

# 📧 Preparar contenido HTML
resumen_html = resumen.replace('\n\n', '</p><p>').replace('\n', '<br>')

html_template = f"""
<html>
<head>
  <meta charset="UTF-8" />
  <style>
    body {{
      font-family: Arial, sans-serif;
      background-color: #f9f9f9;
      color: #333;
      padding: 20px;
    }}
    .container {{
      max-width: 700px;
      background-color: #fff;
      margin: auto;
      padding: 30px;
      border-radius: 8px;
      box-shadow: 0 0 10px rgba(0,0,0,0.1);
    }}
    h1 {{
      color: #2c3e50;
      border-bottom: 3px solid #2980b9;
      padding-bottom: 10px;
    }}
    p, li {{
      line-height: 1.5;
      font-size: 14px;
    }}
    .footer {{
      font-size: 12px;
      color: #999;
      margin-top: 40px;
      border-top: 1px solid #eee;
      padding-top: 10px;
      text-align: center;
    }}
  </style>
</head>
<body>
  <div class="container">
    <h1>🗞️ Boletín Informativo Diario - {fecha_actual}</h1>
    <p>{resumen_html}</p>
    <div class="footer">
      <p>Este boletín es generado automáticamente.</p>
    </div>
  </div>
</body>
</html>
"""

# 📤 Enviar email
msg = MIMEText(html_template, "html", "utf-8")
msg["Subject"] = ASUNTO
msg["From"] = REMITENTE
msg["To"] = DESTINATARIOS

try:
    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as server:
        server.login(REMITENTE, CLAVE_APP)
        server.sendmail(REMITENTE, DESTINATARIOS, msg.as_string())
    print("✅ Correo enviado con éxito.")
except Exception as e:
    print(f"❌ Error al enviar correo: {e}")

