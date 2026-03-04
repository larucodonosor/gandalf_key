import requests
from datetime import datetime

def ofuscar_mensaje(texto, clave=13):
    resultado = ""
    for letra in texto:
        resultado += chr(ord(letra) ^ clave)
    return resultado

def lanzar_alerta_web(mensaje):
    url = "https://httpbin.org/post"
    mensaje_secreto = ofuscar_mensaje(mensaje, 32)
    datos = {"alerta": mensaje_secreto, "emisor": "Gandalf"}
    try:
        print(f"🚀 Iniciando protocolo de red para: {mensaje}...")
        respuesta = requests.post(url, json=datos, timeout=10)
        if respuesta.status_code == 200:
            print("🌐 ¡Conexión exitosa con el servidor de seguridad!")
        else:
            print(f"❌ Error en el servidor: {respuesta.status_code}")
    except Exception as e:
        print(f"📡 Error de red: {e}")

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

    # 2. Buscamos el prefijo en el manual
    # Si el nivel no existe, usamos "SISTEMA" por defecto
    prefijo = PROCEDIMIENTOS.get(nivel, "🤖 SISTEMA")

    print(f"{prefijo}: {mensaje}")

    if nivel == "CRITICO":
        lanzar_alerta_web(mensaje)

def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_secreto = ofuscar_mensaje(mensaje, 13)
    linea = f"[{fecha_hora}] {mensaje_secreto}\n"
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)