import json
import os
import requests
import shutil
import time
from scanner import mapear_carpeta, validar_adn
from datetime import datetime


TIEMPO_ESPERA = 30

def ofuscar_mensaje(texto, clave=13):
    resultado = ""
    for letra in texto:
        resultado += chr(ord(letra) ^ clave)
    return resultado

def gritar_al_mundo(mensaje):
    url = " https://httpbin.org/post"
    # Ofuscamos el grito para que nadie lo lea por el camino
    mensaje_secreto = ofuscar_mensaje(mensaje, 32)
    datos = {"alerta": mensaje_secreto, "emisor": "Gandalf"}

    try:
        print(f"Enviando alerta: {mensaje}...")
        respuesta = requests.post(url, json=datos, timeout=10)
        print(f"Estado recibido: {respuesta.status_code}")

        if respuesta.status_code == 200:
            print("🌐 ¡Conexión exitosa!")
            print("Servidor recibió:", respuesta.json()["json"])
        else:
            print(f"❌ Error en el servidor: {respuesta.status_code}")
    except Exception as e:
        print(f"📡 Error de red: {e}")

def registrar_log(mensaje):
    fecha_hora = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    mensaje_secreto = ofuscar_mensaje(mensaje, 13)
    linea = f"[{fecha_hora}] {mensaje_secreto}\n"

    # Asegúrate de que la carpeta logs existe o créala
    with open("logs/historial.log", "a", encoding="utf-8") as archivo:
        archivo.write(linea)

def ejecutar_gandalf():
    ruta = ["./", "./src"]
    archivo_memoria = "estado_base.json"
    EXTENSIONES_IGNORAR = [".log", ".tmp", ".json"]
    ARCHIVOS_IGNORAR = ["config.ini"]

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

        # Aplicamos el filtrado de archivos
        estado_filtrado = {}
        for archivo, datos in estado_actual.items():
            es_ignorado = False

          # Comprobamos si termina en alguna extensión prohibida
            for ext in EXTENSIONES_IGNORAR:
                if archivo.endswith(ext):
                    es_ignorado = True

          # Comprobamos si el nombre exacto está en la lista negra
            if os.path.basename(archivo) in ARCHIVOS_IGNORAR:
                es_ignorado = True

            if not es_ignorado:
                estado_filtrado[archivo] = datos

    # 3. Intentar cargar la memoria del pasado
    if not os.path.exists(archivo_memoria):
        # Si NO existe, guardamos la primera "foto" y salimos
        with open(archivo_memoria, "w") as f:
            json.dump(estado_filtrado, f)
        print("📸 Primera firma guardada. Sistema listo.")
        return

    # 5. El Gran Comparador (Tu lógica de seguridad)
    try:
    # 5.1. Si existe, leemos y comparamos
        with open(archivo_memoria, "r") as f:
            memoria_pasada = json.load(f)
        for archivo, datos_actuales in estado_filtrado.items():
            if archivo not in memoria_pasada:
                cont_nuevos += 1
                print(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}")
                #Pasar por rayos X
                es_seguro, mensaje_adn = validar_adn(archivo)

                if not es_seguro:
                    print(f'🚨 {mensaje_adn}')
                    registrar_log(mensaje_adn)
                    gritar_al_mundo(f'BLOQUEO DE EMERGENCIA: {archivo} por camuflaje de ADN')

                #BLOQUEO: Lo movemos a cuarentena y lo borramos del sitio original
                    os.makedirs('quarantine', exist_ok=True)
                    destino_bloqueo = os.path.join("quarantine", f"BLOQUEADO_{os.path.basename(archivo)}")
                    shutil.move(archivo, destino_bloqueo)  # 'move' lo quita de donde estaba
                    print(f"🔒 Archivo neutralizado y movido a cuarentena.")

                    continue
                else:
                    print(f"✅ ADN Verificado para {os.path.basename(archivo)}")
            elif (datos_actuales["tamano"] == memoria_pasada[archivo]["tamano"]) and \
             (datos_actuales["modificado"] == memoria_pasada[archivo]["modificado"]):
                cont_ok += 1
                # Si coinciden, ni siquiera comparamos el HASH. ¡Ahorramos CPU!
                print(f"✅ {os.path.basename(archivo)}: OK (Rápido)")
                continue

            #Si lo anterior falla, miramos el HASH para confirmar
            elif datos_actuales["hash"] != memoria_pasada[archivo]["hash"]:
                cont_alertas += 1
                print(f"🚨 ALERTA: {archivo} HA SIDO MODIFICADO!")

                # 1. Creamos la carpeta de seguridad si no existe
                os.makedirs('quarantine', exist_ok=True)

                # 2. Preparamos el nombre del archivo de "evidencia"
                # Usamos basename para sacar solo el nombre (ej: "main.py") sin toda la ruta C:/...
                nombre_base = os.path.basename(archivo)
                partes = nombre_base.rsplit(".", 1)
                nombre_sin_ext = partes[0]
                extension = partes[1] if len(partes) > 1 else ""
                clave_secreta = 4 << 3
                nombre_disfrazado = ofuscar_mensaje(nombre_sin_ext, clave_secreta)
                nombre_final = f"MOD_{nombre_disfrazado}.{extension}"
                ruta_destino = os.path.join("quarantine", f"MODIFICADO_{nombre_final}")

                # 3. ¡A CUARENTENA! Copiamos el archivo físico
                shutil.copy(archivo, ruta_destino)

                registrar_log(f'Modificación detectada en: {archivo}')
                gritar_al_mundo(f"¡INTRUSO! El archivo {nombre_base} ha sido alterado.")
            else:
                    cont_ok += 1
            print(f"✅ {archivo}: OK")

        # 5.2 Segundo Comparador: Detectar archivos borrados
        for archivo_viejo in memoria_pasada:
            if archivo_viejo not in estado_filtrado:
                cont_alertas += 1
                print(f"💀 ¡ALERTA! Archivo ELIMINADO: {archivo_viejo}")
                registrar_log(f"Archivo desaparecido: {archivo_viejo}")
    except Exception as e:
        print(f"🕵️‍♂️ Gandalf detectó una perturbación en la Fuerza: {e}")
        registrar_log(f"Error en el escaneo: {e}")

    # --- NUEVO REPORTE FINAL ---
    print("-" * 30)
    print(f"📊 RESUMEN DEL ESCÁNER:")
    print(f"✅ Correctos: {cont_ok}")
    print(f"🆕 Nuevos:    {cont_nuevos}")
    print(f"🚨 Alertas:   {cont_alertas}")
    print("-" * 30)
    # 6. Actualizamos la memoria para la próxima vez
    with open(archivo_memoria, "w") as f:
        json.dump(estado_filtrado, f, indent=4)  # El indent=4 lo hace legible

        print("\n💾 Memoria actualizada.")

if __name__ == "__main__":
    while True:
        ejecutar_gandalf()
        print("\n[💤] Gandalf está descansando... Próximo escaneo en 30 segundos.")
        time.sleep(TIEMPO_ESPERA)  # El programa se "congela" aquí 30 segundos ejecutar_gandalf()