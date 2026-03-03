import requests
from datetime import datetime

def ofuscar_mensaje(texto, clave=13):
    resultado = ""
    for letra in texto:
        resultado += chr(ord(letra) ^ clave)
    return resultado

def gritar_al_mundo(mensaje, nivel='INFO'):
    # Ahora recibe un mensaje y un NIVEL de gravedad.
    #Niveles: INFO (solo log), ALERTA (consola), CRITICO (servidor)
    # 1. Siempre registramos en el log
    registrar_log(f"[{nivel}] {mensaje}")

    if nivel == "INFO":
        print(f"ℹ️ {mensaje}")

    elif nivel == "ALERTA":
        print(f"⚠️ ATENCIÓN: {mensaje}")

    elif nivel == "CRITICO":
        print(f"🚨 ¡EMERGENCIA CRÍTICA!: {mensaje}")
        # Solo en nivel CRÍTICO hacemos el envío real a la web
        url = "https://httpbin.org/post"
        mensaje_secreto = ofuscar_mensaje(mensaje, 32)
        datos = {"alerta": mensaje_secreto, "emisor": "Gandalf"}
        try:
            print(f"Enviando alerta: {mensaje}...")
            respuesta = requests.post(url, json=datos, timeout=10)
            if respuesta.status_code == 200:
                print("🌐 ¡Conexión exitosa!")
            else:
                print(f"❌ Error en el servidor: {respuesta.status_code}")
        except Exception as e:
            print(f"📡 Error de red: {e}")

def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_secreto = ofuscar_mensaje(mensaje, 13)
    linea = f"[{fecha_hora}] {mensaje_secreto}\n"
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)