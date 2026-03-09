import requests
import os
from datetime import datetime
from dotenv import load_dotenv

# Cargamos el archivo .env
load_dotenv()

def ofuscar_mensaje(texto, clave=13):
    resultado = ""
    for letra in texto:
        resultado += chr(ord(letra) ^ clave)
    return resultado

TELEGRAM_TOKEN = os.getenv("TOKEN_TELEGRAM")
CHAT_ID_PROPIO = os.getenv("CHAT_ID_TELEGRAM")

def lanzar_alerta_telegram(mensaje):
    exito = False
    url = "https://api.telegram.org/bot" + TELEGRAM_TOKEN + '/sendMessage'
    # mensaje_secreto = ofuscar_mensaje(mensaje, 32)
    datos = {"chat_id": CHAT_ID_PROPIO, "text": "🛡️ GANDALF NOTIFICA:\n\n" + mensaje}
    try:
        print(f"🚀 Iniciando protocolo de red para: {mensaje}...")
        respuesta = requests.post(url, json=datos, timeout=10)
        if respuesta.status_code != 200:
            registrar_log("Error API Telegram: " + str(respuesta.status_code))
    except Exception as e:
        registrar_log("📡 Fallo de red Telegram:" + str(e))

def gritar_al_mundo(mensaje, nivel='INFO'):
    # Ahora recibe un mensaje y un NIVEL de gravedad.
    #Niveles: INFO (solo log), ALERTA (consola), CRITICO (servidor)
    #Definimos el diccionario --> Clave(nivel de alerta) | Valor(el prefijo que mostramos)
    PROCEDIMIENTOS = {
        "INFO": "ℹ️ INFO",
        "ALERTA": "⚠️ ATENCIÓN",
        "CRITICO": "🚨 EMERGENCIA CRÍTICA",
        "DEBUG": "🔍 DEPURACIÓN"  # ¡Podemos añadir niveles nuevos sin tocar el código de abajo!
    }
    # 1. Siempre registramos en el log
    registrar_log(f"[{nivel}] {mensaje}")

    # 2. FILTRADO INTELIGENTE:
    # Solo imprimimos en pantalla si es algo importante (ALERTA o superior)
    # o si estamos en modo DEBUG.
    if nivel in ["ALERTA", "CRITICO", "DEBUG"]:
        prefijo = PROCEDIMIENTOS.get(nivel, "🤖 SISTEMA")
        print(f"{prefijo}: {mensaje}")

    if nivel == "CRITICO":
        lanzar_alerta_telegram(mensaje)

def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_secreto = ofuscar_mensaje(mensaje, 13)
    linea = f"[{fecha_hora}] {mensaje_secreto}\n"
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)