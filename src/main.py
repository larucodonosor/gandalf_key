import json
import os
import shutil
import time
import sys
import threading
import tray_icon
import alerts
import security
import interface
import backup_manager
from datetime import datetime
from scanner import mapear_carpeta, validar_adn
from server_g_k import app as server_app

TIEMPO_ESPERA = 30

def ejecutar_gandalf():
    ruta = ["./", "./src"]
    archivo_memoria = "estado_base.json"
    # 1. Escaneo actual
    estado_actual = {}

    # 2. Recorre cada ruta de la lista
    for r in ruta:
        # Escanea UNA carpeta y guarda el resultado temporalmente
        resultado = mapear_carpeta(r)
        for archivo, datos in resultado.items():
            # Solo si es un "tesoro", lo añadimos al estado_actual
            if backup_manager.is_treasure_extension(archivo):
                estado_actual[archivo] = datos
        # Mezcla lo que acaba de encontrar con el diccionario general
        estado_actual.update(resultado)

    # 3. Intenta cargar la memoria del pasado
    if not os.path.exists(archivo_memoria):
        # Si NO existe, guarda la primera copia y sale
        with open(archivo_memoria, "w") as f:
            json.dump(estado_actual, f)
        return

    # 5. El Gran Comparador (La lógica de seguridad)
    try:
    # 5.1. Si existe, lee y compara
        with open(archivo_memoria, "r") as f:
            memoria_pasada = json.load(f)
        for archivo, datos_actuales in estado_actual.items():
            if archivo not in memoria_pasada:
                alerts.gritar_al_mundo(f" NUEVO ARCHIVO DETECTADO: {archivo}", nivel='INFO')
                #Pasa por rayos X
                es_seguro, mensaje_adn = validar_adn(archivo)

                if not es_seguro:
                    alerts.registrar_log(mensaje_adn)
                    alerts.gritar_al_mundo(f'BLOQUEO DE EMERGENCIA: {archivo} por camuflaje de ADN', nivel='CRITICO')

                #BLOQUEO: Lo mueve a cuarentena y lo borra del sitio original
                    os.makedirs('quarantine', exist_ok=True)
                    destino_bloqueo = os.path.join("quarantine", f"BLOQUEADO_{os.path.basename(archivo)}")
                    shutil.move(archivo, destino_bloqueo)  # 'move' lo quita de donde estaba
                    print(f" Archivo neutralizado y movido a cuarentena.")

                    continue

            # Mira el HASH
            elif datos_actuales["hash"] != memoria_pasada[archivo]["hash"]:
                nombre_base = os.path.basename(archivo)

                # 1. Registro y grito (llama a alerts.py)

                alerts.registrar_log(f'Modificación detectada en: {archivo}')
                alerts.gritar_al_mundo(f"¡INTRUSO! El archivo {nombre_base} ha sido modificado.", nivel='CRITICO')

                # 2. Protocolo de Decisión (Aquí está la clave)
                if os.path.isfile("DESARROLLO.txt"):
                    # Si es desarrollo, actualiza la bóveda
                    ruta_vault = os.path.join(".gandalf_vault", nombre_base)
                    shutil.copy2(archivo, ruta_vault)
                else:
                    # Si es ataque, llama a security.py
                    security.restaurar_archivo(archivo)

            elif (datos_actuales["tamano"] == memoria_pasada[archivo]["tamano"]) and \
             (datos_actuales["modificado"] == memoria_pasada[archivo]["modificado"]):

                # CHEQUEO DE ADN SECRETO

                if datos_actuales["adn_muestra"] != memoria_pasada[archivo].get("adn_muestra"):
                    alerts.gritar_al_mundo(f"🚨 ¡ALERTA DE SUPLANTACIÓN! El ADN en la posición secreta ha cambiado en {archivo}", nivel='CRITICO')
                  # Aquí dispara la cuarentena
                else:
                    continue

        # 5.2 Segundo Comparador: Detecta archivos borrados
        for archivo_viejo in memoria_pasada:
            if archivo_viejo not in estado_actual:
                alerts.gritar_al_mundo(f"💀 ¡ALERTA! Archivo ELIMINADO: {archivo_viejo}", nivel='ALERTA')
                alerts.registrar_log(f"Archivo desaparecido: {archivo_viejo}")

                security.restaurar_archivo(archivo_viejo)

    except Exception as e:
        print(f"🕵️‍♂️ Gandalf detected a disturbance in the Force: {e}")
        alerts.registrar_log(f"Error en el escaneo: {e}")

    # 6. Actualiza la memoria
    with open(archivo_memoria, "w") as f:
        json.dump(estado_actual, f, indent=4)  # El indent=4 lo hace legible

        # INTEGRACIÓN DEL BACKUP

        today = datetime.today().weekday()
        if today in [1, 4]:
            print(" Es día de Backup. Iniciando...")
            # Pasa la lista de archivos validados
            backup_manager.run_scheduled_backup(list(estado_actual.keys()))
        else:
            print(f" Hoy es día {today}, no toca backup (Martes=1, Viernes=4).")

# Vigila los dispositivos del sistema
def bucle_infinito_vigilancia():
    global usbs_conocidos
    while True:
        ejecutar_gandalf()

        usbs_actuales = security.obtener_unidades_removibles()
        # ... Lógica de comparación de USBs
        # ¿Hay alguno más?
        if len(usbs_actuales) > len(usbs_conocidos):
            nuevos = [u for u in usbs_actuales if u not in usbs_conocidos]
            alerts.gritar_al_mundo(f"⚠️ ¡OJO! Nuevo hardware detectado: {nuevos}")
            usbs_conocidos = usbs_actuales  # Actualiza la memoria

        # ¿Falta alguno?
        elif len(usbs_actuales) < len(usbs_conocidos):
            alerts.gritar_al_mundo("ℹ️ Dispositivo extraído.")
            usbs_conocidos = usbs_actuales

        sys.stdout.write(". ")
        sys.stdout.flush()
        time.sleep(TIEMPO_ESPERA)

if __name__ == "__main__":
    print("🛡️ Gandalf ha iniciado su guardia silenciosa...")

    # 1. Hilo de telegram (Polling)
    # daemon=True para que se cierre si se cierra el programa principal
    threading.Thread(target=alerts.start_bot_polling, daemon=True).start()

    # 2. Hilo de vigilancia de descargas (Watchdog)
    import downloads_guard

    threading.Thread(target=downloads_guard.iniciar_vigilancia_descargas, daemon=True).start()

    # 3. Activa el servidor Flask
    threading.Thread(target=lambda: server_app.run(port=5000, use_reloader=False), daemon=True).start()

    # 2.Inicia variable
    usbs_conocidos = security.obtener_unidades_removibles()

    # 3. Lanza el bucle de vigilancia en su Hilo (Daemon)
    threading.Thread(target=bucle_infinito_vigilancia, daemon=True).start()

    # 4. Inicia la bandeja
    threading.Thread(target=tray_icon.iniciar_bandeja, daemon=True).start()

    # 5. INTERFAZ (HILO PRINCIPAL)
    # Con ventana.withdraw() en interface.py, no sale la ventana al arrancar.
    interface.ventana.mainloop()

