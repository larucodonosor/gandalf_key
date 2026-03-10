import json
import os
import shutil
import time
import sys
import alertas
from scanner import mapear_carpeta, validar_adn
from alertas import gritar_al_mundo, registrar_log
from seguridad import restaurar_archivo


TIEMPO_ESPERA = 30

def ejecutar_gandalf():
    ruta = ["./", "./src"]
    archivo_memoria = "estado_base.json"
    EXTENSIONES_IGNORAR = [".log", ".tmp", ".json"]
    ARCHIVOS_IGNORAR = ["config.ini", "DESARROLLO.txt"]

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
        # print("📸 Primera firma guardada. Sistema listo.")
        return

    # 5. El Gran Comparador (Tu lógica de seguridad)
    try:
    # 5.1. Si existe, leemos y comparamos
        with open(archivo_memoria, "r") as f:
            memoria_pasada = json.load(f)
        for archivo, datos_actuales in estado_filtrado.items():
            if archivo not in memoria_pasada:
                cont_nuevos += 1
                gritar_al_mundo(f"🆕 NUEVO ARCHIVO DETECTADO: {archivo}", nivel='INFO')
                #Pasar por rayos X
                es_seguro, mensaje_adn = validar_adn(archivo)

                if not es_seguro:
                    # print(f'🚨 {mensaje_adn}')
                    registrar_log(mensaje_adn)
                    gritar_al_mundo(f'BLOQUEO DE EMERGENCIA: {archivo} por camuflaje de ADN', nivel='CRITICO')

                #BLOQUEO: Lo movemos a cuarentena y lo borramos del sitio original
                    os.makedirs('quarantine', exist_ok=True)
                    destino_bloqueo = os.path.join("quarantine", f"BLOQUEADO_{os.path.basename(archivo)}")
                    shutil.move(archivo, destino_bloqueo)  # 'move' lo quita de donde estaba
                    print(f"🔒 Archivo neutralizado y movido a cuarentena.")

                    continue
                # else:
                    # print(f"✅ ADN Verificado para {os.path.basename(archivo)}")
            # Miramos el HASH
            elif datos_actuales["hash"] != memoria_pasada[archivo]["hash"]:
                cont_alertas += 1
                nombre_base = os.path.basename(archivo)
                # print(f"🚨 ALERTA: {nombre_base} HA SIDO MODIFICADO!")

                # 1. Registro y grito (llamamos a alertas.py)

                registrar_log(f'Modificación detectada en: {archivo}')
                gritar_al_mundo(f"¡INTRUSO! El archivo {nombre_base} ha sido alterado.", nivel='CRITICO')

                # 2. Protocolo de Decisión (Aquí está la clave)
                if os.path.isfile("DESARROLLO.txt"):
                    # Si es desarrollo, actualizamos la bóveda
                    ruta_vault = os.path.join(".gandalf_vault", nombre_base)
                    shutil.copy2(archivo, ruta_vault)
                    # print(f"🛠️ MODO DESARROLLO: Bóveda actualizada para {nombre_base}")
                else:
                    # Si es ataque, llamamos al especialista (seguridad.py)
                    restaurar_archivo(archivo)

            elif (datos_actuales["tamano"] == memoria_pasada[archivo]["tamano"]) and \
             (datos_actuales["modificado"] == memoria_pasada[archivo]["modificado"]):

                # CHEQUEO DE ADN SECRETO

                if datos_actuales["adn_muestra"] != memoria_pasada[archivo].get("adn_muestra"):
                    cont_alertas += 1
                    gritar_al_mundo(f"🚨 ¡ALERTA DE SUPLANTACIÓN! El ADN en la posición secreta ha cambiado en {archivo}", nivel='CRITICO')
                  # Aquí dispararíamos la cuarentena...
                else:
                    cont_ok += 1
                    # print(f"✅ {os.path.basename(archivo)}: OK (ADN Verificado)")
                    continue

            else:
                    cont_ok += 1
                    # print(f"✅ {archivo}: OK")

        # 5.2 Segundo Comparador: Detectar archivos borrados
        for archivo_viejo in memoria_pasada:
            if archivo_viejo not in estado_filtrado:
                cont_alertas += 1
                gritar_al_mundo(f"💀 ¡ALERTA! Archivo ELIMINADO: {archivo_viejo}", nivel='ALERTA')
                registrar_log(f"Archivo desaparecido: {archivo_viejo}")

                restaurar_archivo(archivo_viejo)

    except Exception as e:
        print(f"🕵️‍♂️ Gandalf detectó una perturbación en la Fuerza: {e}")
        registrar_log(f"Error en el escaneo: {e}")

        # --- NUEVO REPORTE FINAL ---
    # print("-" * 30)
    # print(f"📊 RESUMEN DEL ESCÁNER:")
    # print(f"✅ Correctos: {cont_ok}")
    # print(f"🆕 Nuevos:    {cont_nuevos}")
    # print(f"🚨 Alertas:   {cont_alertas}")
    # print("-" * 30)
    # 6. Actualizamos la memoria para la próxima vez
    with open(archivo_memoria, "w") as f:
        json.dump(estado_filtrado, f, indent=4)  # El indent=4 lo hace legible

        # print("\n💾 Memoria actualizada.")

if __name__ == "__main__":
    print("🛡️ Gandalf ha iniciado su guardia silenciosa...")
    while True:
        # 1. EJECUTAR EL ESCANEO DE SEGURIDAD
        ejecutar_gandalf()

        # 2. ESCUCHA ACTIVA: Gandalf revisa su Telegram
        orden = alertas.leer_mensajes()

        if orden == "/status":
            alertas.lanzar_alerta_telegram("✅ Sistema Operativo. Los archivos están a salvo, Lara.")

        # FEEDBACK VISUAL Y DESCANSO
        sys.stdout.write(". ")
        sys.stdout.flush()

        time.sleep(TIEMPO_ESPERA)  # El programa se "congela" aquí 30 segundos ejecutar_gandalf()