import os
import smtplib
from email.mime.text import MIMEText
from datetime import datetime
import google.generativeai as genai
import traceback

# 📤 Configuración del correo
DESTINATARIOS = ["cjescobar37@gmail.com"]
REMITENTE = "polyescseguridad@gmail.com"
CLAVE_APP = os.environ.get("EMAIL_PASSWORD")
fecha_actual = datetime.now().strftime('%d/%m/%Y')
ASUNTO = f"Resumen Diario de Noticias - {fecha_actual}"

# 🧠 Configuración de Gemini
GEMINI_API_KEY = os.environ.get("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    print("❌ No se encontró la API Key de Gemini.")
    exit(1)

genai.configure(api_key=GEMINI_API_KEY)

# 🧾 Prompt con fecha interpolada usando format()
prompt = """
Generá un boletín informativo diario con fecha {fecha} con el siguiente formato y estilo periodístico, con prioridad en eventos de Santa Rosa (La Pampa) y noticias nacionales relevantes para Argentina. Si no hay eventos locales para hoy, buscá en el calendario hasta los próximos 3 meses. El contenido debe ser preciso, claro y dividido por secciones.

Estructura:
## 🗞️ Boletín Informativo Diario - {fecha}

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
""".format(fecha=fecha_actual)

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

# ✉️ Preparar y enviar email con plantilla HTML y estilos básicos
# Preparar el contenido HTML del resumen para evitar problemas con backslash en f-string
resumen_html = resumen.replace('\n\n', '</p><p>').replace('\n', '<br>')

html_template = """
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
    h2 {{
      color: #2980b9;
      margin-top: 30px;
      border-bottom: 1px solid #ccc;
      padding-bottom: 6px;
    }}
    p, li {{
      line-height: 1.5;
      font-size: 14px;
    }}
    ul {{
      padding-left: 20px;
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
    <h1>🗞️ Boletín Informativo Diario - {fecha}</h1>
    <div>
      <p>{contenido}</p>
    </div>
    <div class="footer">
      <p>Este boletín es generado automáticamente.</p>
    </div>
  </div>
</body>
</html>
""".format(fecha=fecha_actual, contenido=resumen_html)

msg = MIMEText(html_template, "html", "utf-8")
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
