import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import security

# Carga el archivo .env
load_dotenv()

# CONFIGURACIÓN
TOKEN = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID_TELEGRAM")
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

bot = telebot.TeleBot(TOKEN)

# UTILIDADES
def ofuscar_mensaje(texto, clave=13):
    resultado = ""
    for letra in texto:
        resultado += chr(ord(letra) ^ clave)
    return resultado

def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_secreto = ofuscar_mensaje(mensaje, 13)
    linea = f"[{fecha_hora}] {mensaje_secreto}\n"
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)


# CONSULTA A VIRUSTOTAL
def check_virustotal(file_path):
    # Envía el archivo o su hash a VirusTotal para analizar.
    if not VT_API_KEY:
        return "ERROR", "No API Key configured"

    url = "https://www.virustotal.com/api/v3/files"
    files = {"file": open(file_path, "rb")}
    headers = {"x-apikey": VT_API_KEY}

    try:
        # Nota al futuro: implementar primero chequeo de HASH para ahorrar tiempo/cuota
        response = requests.post(url, files=files, headers=headers, timeout=15)
        if response.status_code == 200:
            analysis_id = response.json()["data"]["id"]
            return "ANALYZING", f"ID: {analysis_id}"
        return "FAILED", f"Status: {response.status_code}"
    except Exception as e:
        return "ERROR", str(e)

def gritar_al_mundo(mensaje, nivel='INFO'):
    # Recibe un mensaje y un NIVEL de gravedad.
    # Niveles: INFO (solo log), ALERTA (consola), CRITICO (servidor)
    PROCEDIMIENTOS = {
        "INFO": "ℹ️ INFO",
        "ALERTA": "⚠️ ATENCIÓN",
        "CRITICO": "🚨 EMERGENCIA CRÍTICA",
        "DEBUG": "🔍 DEPURACIÓN"
    }
    # 1. Siempre registra en el log
    registrar_log(f"[{nivel}] {mensaje}")

    # 2. FILTRADO INTELIGENTE:
    if nivel in ["ALERTA", "CRITICO", "DEBUG"]:
        prefijo = PROCEDIMIENTOS.get(nivel, "SISTEMA")
        print(f"{prefijo}: {mensaje}")

    if nivel == "CRITICO":
        bot.send_message(CHAT_ID, f"🚨 **GANDALF CRITICAL ALERT**\n\n{mensaje}", parse_mode="Markdown")

def request_remote_authorization(file_name, temp_path):
    # Envía un mensaje con botones interactivos a Telegram.
    # El archivo ya está "secuestrado" en quarantine por watchdog.
    markup = InlineKeyboardMarkup()

    # Crea los botones con 'callback_data' para registrar la selección.
    btn_quarantine = InlineKeyboardButton("☣️ Quarantine", callback_data=f"quar_{file_name}")
    btn_allow = InlineKeyboardButton("✅ Allow & Restore", callback_data=f"allow_{file_name}")

    markup.add(btn_quarantine, btn_allow)

    text = (
        f"🛡️ **GANDALF INTERCEPTION**\n\n"
        f"Suspicious file detected in Downloads: `{file_name}`\n"
        f"Status: **Locked in Quarantine**\n\n"
        f"What should I do?"
    )

    bot.send_message(CHAT_ID, text, reply_markup=markup, parse_mode="Markdown")

# MANEJADOR DE RESPUESTAS (CALLBACKS)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    # Gandalf recibe la orden desde telegram.
    action, filename = call.data.split("_")
    # Busca el archivo en la carpeta temporal de espera
    temp_path = os.path.join("quarantine", f"WAITING_{filename}")

    if action == "quar":
        # Mover a cuarentena definitiva (quitar prefijo WAITING_)
        final_path = os.path.join("quarantine", filename)
        if os.path.exists(temp_path):
            os.rename(temp_path, final_path)
            bot.edit_message_text(f"☣ `{filename}` secured in permanent quarantine.", CHAT_ID, call.message.message_id)

    elif action == "allow":
        # Restaurar a descargas usando la función de seguridad
        if os.path.exists(temp_path):
            success = security.restore_from_quarantine(temp_path, filename)
            if success:
                bot.edit_message_text(f"`{filename}` restored to Downloads.", CHAT_ID, call.message.message_id)
            else:
                bot.send_message(CHAT_ID, " Error restoring file.")

# Función para arrancar el bot en main
def start_bot_polling():
    print("📡 Telegram Bot is listening for your commands...")
    bot.infinity_polling()

