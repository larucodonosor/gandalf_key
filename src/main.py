import json
import os
import shutil
from src.scanner import mapear_carpeta
from datetime import datetime


def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    linea = f"[{fecha_hora}] {mensaje}\n"

    # Asegúrate de que la carpeta logs existe o créala
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)

def ejecutar_gandalf():
    ruta = ["./", "./src"]
    archivo_memoria = "estado_base.json"

    # ... rutas, memoria ...
    cont_ok = 0
    cont_nuevos = 0
    cont_alertas = 0

    # 1. Escaneo actual
    estado_actual = {}

    # 2. Recorremos cada ruta de nuestra lista
    for r in ruta:
        # Escaneamos UNA carpeta y guardamos el resultado temporalmente
        resultado_carpeta = mapear_carpeta(r)

        # Mezclamos lo que acabamos de encontrar con nuestro diccionario general
        estado_actual.update(resultado_carpeta)

    # 3. Intentar cargar la memoria del pasado
    if not os.path.exists(archivo_memoria):
        # Si NO existe, guardamos la primera "foto" y salimos
        with open(archivo_memoria, "w") as f:
            json.dump(estado_actual, f)
        print("📸 Primera firma guardada. Sistema listo.")
        return

    # 4. Si existe, leemos y comparamos
    with open(archivo_memoria, "r") as f:
        memoria_pasada = json.load(f)

    # 5. El Gran Comparador (Tu lógica de seguridad)
    for archivo, datos_actuales in estado_actual.items():
        if archivo not in memoria_pasada:
            cont_nuevos += 1
            print(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}")
        elif (datos_actuales["hash"] != memoria_pasada[archivo]["hash"]) or \
         (datos_actuales["tamano"] != memoria_pasada[archivo]["tamano"]):
            cont_alertas += 1
            print(f"🚨 ALERTA: {archivo} HA SIDO MODIFICADO!")

            # 1. Creamos la carpeta de seguridad si no existe
            os.makedirs('quarantine', exist_ok=True)

            # 2. Preparamos el nombre del archivo de "evidencia"
            # Usamos basename para sacar solo el nombre (ej: "main.py") sin toda la ruta C:/...
            nombre_base = os.path.basename(archivo)
            ruta_destino = os.path.join("quarantine", f"MODIFICADO_{nombre_base}")

            # 3. ¡A CUARENTENA! Copiamos el archivo físico
            shutil.copy(archivo, ruta_destino)

            registrar_log(f'Modificación detectada en: {archivo}')
        else:
            cont_ok += 1
            print(f"✅ {archivo}: OK")

    # --- NUEVO REPORTE FINAL ---
    print("-" * 30)
    print(f"📊 RESUMEN DEL ESCÁNER:")
    print(f"✅ Correctos: {cont_ok}")
    print(f"🆕 Nuevos:    {cont_nuevos}")
    print(f"🚨 Alertas:   {cont_alertas}")
    print("-" * 30)

    # 6. Actualizamos la memoria para la próxima vez
    with open(archivo_memoria, "w") as f:
        json.dump(estado_actual, f, indent=4)  # El indent=4 lo hace legible

        print("\n💾 Memoria actualizada.")

if __name__ == "__main__":
    ejecutar_gandalf()