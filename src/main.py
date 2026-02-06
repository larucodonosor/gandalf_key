import json
import os
from src.scanner import mapear_carpeta
from datetime import datetime


def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_hora}] {mensaje}\n"

    # Asegúrate de que la carpeta logs existe o créala
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)

def ejecutar_gandalf():
    ruta = "./"
    archivo_memoria = "estado_base.json"

    # 1. Escaneo actual
    estado_actual = mapear_carpeta(ruta)

    # 2. Intentar cargar la memoria del pasado
    if not os.path.exists(archivo_memoria):
        # Si NO existe, guardamos la primera "foto" y salimos
        with open(archivo_memoria, "w") as f:
            json.dump(estado_actual, f)
        print("📸 Primera firma guardada. Sistema listo.")
        return

    # 3. Si existe, leemos y comparamos
    with open(archivo_memoria, "r") as f:
        memoria_pasada = json.load(f)

    # 4. El Gran Comparador (Tu lógica de seguridad)
    for archivo, datos_actuales in estado_actual.items():
        if archivo not in memoria_pasada:
            print(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}")
        elif (datos_actuales["hash"] != memoria_pasada[archivo]["hash"]) or \
         (datos_actuales["tamano"] != memoria_pasada[archivo]["tamano"]):
            print(f"🚨 ALERTA: {archivo} HA SIDO MODIFICADO!")
            registrar_log(f'Modificación detectada en: {archivo}')
        else:
            print(f"✅ {archivo}: OK")


if __name__ == "__main__":
    ejecutar_gandalf()