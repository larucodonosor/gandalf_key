import json
import os
from src.scanner import mapear_carpeta


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
    for archivo, hash_actual in estado_actual.items():
        if archivo not in memoria_pasada:
            print(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}")
        elif hash_actual != memoria_pasada[archivo]:
            print(f"🚨 ALERTA: {archivo} HA SIDO MODIFICADO!")
        else:
            print(f"✅ {archivo}: OK")


if __name__ == "__main__":
    ejecutar_gandalf()