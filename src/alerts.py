pending_actions = {}
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import requests
import os
from datetime import datetime
from dotenv import load_dotenv
import security
import integrity_utils
import network_utils

# Carga el archivo .env
load_dotenv()

# CONFIGURACIÓN
TOKEN = os.getenv("TOKEN_TELEGRAM")
CHAT_ID = os.getenv("CHAT_ID_TELEGRAM")
VT_API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

bot = telebot.TeleBot(TOKEN)

# UTILIDADES
def obfuscate_message(text, key=13):
    result = ""
    for letter in text:
        result += chr(ord(letter) ^ key)
    return result

def log_activity(message):
    date_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    secret_message = obfuscate_message(message, 13)
    line = f"[{date_time}] {secret_message}\n"
    with open("logs/historial.log", "a", encoding="utf-8") as file:
        file.write(line)

# CONSULTA A VIRUSTOTAL
def check_virustotal(file_path):
    # Envía el archivo o su hash a VirusTotal para analizar.
    if not VT_API_KEY:
        return "ERROR", "No API Key configured"

    url = "https://www.virustotal.com/api/v3/files"
    files = {"file": open(file_path, "rb")}
    headers = {"x-apikey": VT_API_KEY}

    try:
        with open(file_path, "rb") as f:
            files = {"file": f}
            response = network_utils.retry_request(lambda: requests.post(url, files=files, headers=headers, timeout=15))

        # Nota al futuro: implementar primero chequeo de HASH para ahorrar tiempo/cuota
        if response.status_code == 200:
            analysis_id = response.json()["data"]["id"]
            return "ANALYZING", f"ID: {analysis_id}"
        return "FAILED", f"Status: {response.status_code}"
    except Exception as e:
        return "ERROR", str(e)

def light_the_beacons(message, severity='INFO'):
    # Recibe un mensaje y un NIVEL de gravedad.
    # Niveles: INFO (solo log), ALERTA (consola), CRITICO (servidor)
    PROCEDURES = {
        "INFO": "ℹ️ INFO",
        "ALERTA": "⚠️ ATENCIÓN",
        "CRITICO": "🚨 EMERGENCIA CRÍTICA",
        "DEBUG": "🔍 DEPURACIÓN"
    }
    # 1. Siempre registra en el log
    log_activity(f"[{severity}] {message}")

    # 2. FILTRADO INTELIGENTE:
    if severity in ["ALERTA", "CRITICO", "DEBUG"]:
        prefix = PROCEDURES.get(severity, "SISTEMA")
        print(f"{prefix}: {message}")

    if severity == "CRITICO":
        network_utils.retry_request(
            lambda: bot.send_message(CHAT_ID, f"🚨 **GANDALF CRITICAL ALERT**\n\n{message}", parse_mode="Markdown"))

def request_remote_authorization(file_name, temp_path):
    # Envía un mensaje con botones interactivos a Telegram.
    # El archivo ya está "inhabilitado" en quarantine por watchdog.
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
    network_utils.retry_request(lambda: bot.send_message(CHAT_ID, text, reply_markup=markup, parse_mode="Markdown"))

def request_work_mode_verification():
    # Crea el diálogo  y botones de telegram para aceptar o no la solicitud de Working Mode
    markup = InlineKeyboardMarkup()
    btn_yes = InlineKeyboardButton("YES, it's me", callback_data="work_yes")
    btn_no = InlineKeyboardButton("NO, Block!", callback_data="work_no")
    markup.add(btn_yes, btn_no)

    bot.send_message(CHAT_ID, "WORK MODE REQUESTED!!!\nVerify identity to pause guard:", reply_markup=markup,
                     parse_mode="Markdown")

# MANEJADOR DE RESPUESTAS (CALLBACKS)
@bot.callback_query_handler(func=lambda call: True)
def handle_query(call):
    #importación local, solo se activa si se pulsa el boton correspondiente
    import working_mode_ctrl as wmc

    # Separación de la data
    datos = call.data.split("_")
    action = datos[0]
    info = datos[1]

    if action == "work":
        if info == "yes":
            wmc.update_work_mode_status(True)
            bot.edit_message_text("Work Mode ON", CHAT_ID, call.message.message_id)
        else:
            wmc.update_work_mode_status(False)
            bot.edit_message_text("Work Mode DENIED", CHAT_ID, call.message.message_id)

    elif action == "quar" or action == "allow":
        filename = info
        temp_path = os.path.join("quarantine", f"WAITING_{filename}")

        if action == "quar":
            if os.path.exists(temp_path):
                os.rename(temp_path, os.path.join("quarantine", filename))
                bot.edit_message_text(f"☣ `{filename}` Quarantined", CHAT_ID, call.message.message_id)

        elif action == "allow":
            # if os.path.exists(temp_path):
                # if security.restore_from_quarantine(temp_path, filename):
                    # bot.edit_message_text(f"`{filename}` Restored", CHAT_ID, call.message.message_id)
            # 1. Recupera los datos del diccionario global
            chat_id = call.message.chat.id
            action_data = pending_actions.get(chat_id)

            if not action_data:
                bot.edit_message_text("❌ Error: Acción no encontrada.", CHAT_ID, call.message.message_id)
                return

            # 2. VERIFICACIÓN CRÍTICA DE INTEGRIDAD
            # Usa el hash que se guardó al detectar el incidente
            if not integrity_utils.verify_integrity(action_data["temp_path"], action_data["hash"]):
                light_the_beacons("🚨 ¡INTENTO DE MANIPULACIÓN DETECTADO!", severity="CRITICO")
                bot.edit_message_text("❌ Error: El archivo ha sido manipulado. Abortando.", CHAT_ID,
                                      call.message.message_id)
                return

            # 3. LÓGICA DE RESTAURACIÓN SEGÚN ORIGEN
            success = False
            if action_data["source"] == "LOCAL":
                # Restaurar desde quarantine
                success = security.restore_from_quarantine(action_data["temp_path"], action_data["filename"])

            elif action_data["source"] == "CLOUD":
                # Restaurar desde Drive (necesitas importar cloud_vault)
                import cloud_vault
                success = cloud_vault.download_and_decrypt(action_data["file_id"], action_data["original_path"])

            # 4. Finalización
            if success:
                bot.edit_message_text(f"✅ `{action_data['filename']}` Restaurado con éxito.", CHAT_ID,
                                      call.message.message_id)
                pending_actions.pop(chat_id)  # Limpia el registro
            else:
                bot.edit_message_text(f"❌ Error al restaurar `{action_data['filename']}`", CHAT_ID,
                                      call.message.message_id)


# Función para arrancar el bot en main
def start_bot_polling():
    print("Telegram Bot is listening for your commands...")
    bot.infinity_polling()

