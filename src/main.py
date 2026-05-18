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
import backup_scheduler
import integrity_utils
import scanner
import logger_manager
from server_g_k import app as server_app
import updater
import logging

logger = logging.getLogger(__name__)

WAIT_TIME = 30

def execute_gandalf():
    paths_to_scan = ["./", "./src"]
    memory_file = "base_memory.json"
    # 1. Escaneo actual
    current_state = {}

    # 2. Recorre cada ruta de la lista
    for path in paths_to_scan:
        # Escanea UNA carpeta y guarda el resultado temporalmente
        scan_result = scanner.map_folder(path)
        if scan_result is not None:
            for file, data in scan_result.items():
                # Add to state if it's a "treasure" or general file
                if backup_manager.is_treasure_extension(file):
                    current_state[file] = data

            # Mezcla lo que acaba de encontrar con el diccionario general
            current_state.update(scan_result)

    # 3. Intenta cargar la memoria del pasado
    if not os.path.exists(memory_file):
        # Si NO existe, guarda la primera copia y sale
        with open(memory_file, "w") as f:
            json.dump(current_state, f)
        return

    # 5. El Gran Comparador (La lógica de seguridad)
    try:
    # 5.1. Si existe, lee y compara
        with open(memory_file, "r") as f:
            past_memory = json.load(f)
        for file, current_data in current_state.items():
            if file not in past_memory:
                alerts.light_the_beacons(f" NUEVO ARCHIVO DETECTADO: {file}", severity='INFO')
                #Pasa por rayos X
                is_secure, dna_message = integrity_utils.validate_dna(file)

                if not is_secure:
                    logger.info(dna_message)
                    alerts.light_the_beacons(f'BLOQUEO DE EMERGENCIA: {file} por camuflaje de ADN', severity='CRITICO')

                #BLOQUEO: Lo mueve a cuarentena y lo borra del sitio original
                    os.makedirs('quarantine', exist_ok=True)
                    blocking_destiny = os.path.join("quarantine", f"BLOQUEADO_{os.path.basename(file)}")
                    shutil.move(file, blocking_destiny)  # 'move' lo quita de donde estaba
                    print(f" Archivo neutralizado y movido a cuarentena.")

                    continue

            # Mira el HASH
            elif current_data["hash"] != past_memory[file]["hash"]:
                base_name = os.path.basename(file)

                # 1. Registro y grito (llama a alerts.py)

                logger.warning(f'Modificación detectada en: {file}')
                alerts.light_the_beacons(f"¡INTRUSO! El archivo {base_name} ha sido modificado.", severity='CRITICO')

                # 2. Protocolo de Decisión (Aquí está la clave)
                if os.path.isfile("DESARROLLO.txt"):
                    # Si es desarrollo, actualiza la bóveda
                    vault_path = os.path.join(".gandalf_vault", base_name)
                    shutil.copy2(file, vault_path)
                else:
                    # 1. Mueve a cuarentena preventiva
                    os.makedirs('quarantine', exist_ok=True)
                    temp_path = os.path.join("quarantine", f"WAITING_{base_name}")
                    shutil.copy2(file, temp_path)  # Copia para analizar

                    # 2. Registra en la memoria de alertas (PENDING ACTIONS)
                    alerts.pending_actions[alerts.CHAT_ID] = {
                        "source": "LOCAL",
                        "filename": base_name,
                        "hash": current_data["hash"],  # Guarda la huella original
                        "temp_path": temp_path,
                        "original_path": file
                    }

                    # 3. Lanza la petición al usuario
                    alerts.request_remote_authorization(base_name, temp_path)

            elif (current_data["size"] == past_memory[file]["size"]) and \
             (current_data["modified_at"] == past_memory[file]["modified_at"]):

                # CHEQUEO DE ADN SECRETO

                if current_data.get("dna_sample") != past_memory[file].get("dna_sample"):
                    alerts.light_the_beacons(f"🚨 ¡ALERTA DE SUPLANTACIÓN! El ADN en la posición secreta ha cambiado en {file}", severity='CRITICO')
                  # Aquí dispara la cuarentena
                else:
                    continue

        # 5.2 Segundo Comparador: Detecta archivos borrados
        for old_file in past_memory:
            if old_file not in current_state:
                alerts.light_the_beacons(f"💀 ¡ALERTA! Archivo ELIMINADO: {old_file}", severity='ALERTA')
                logger.critical(f"Archivo desaparecido: {old_file}")

                security.restore_file(old_file)

    except Exception as e:
        logger.error(f"🕵️‍♂️ Gandalf ha detectado una perturbación en la Fuerza: {e}")
        logger.error(f"Error en el escaneo: {e}")

    # 6. Actualiza la memoria
    with open(memory_file, "w") as f:
        json.dump(current_state, f, indent=4)  # El indent=4 lo hace legible

# Vigila los dispositivos del sistema
def infinite_surveillance_loop():
    global known_usbs
    while True:
        execute_gandalf()

        current_usbs = security.obtain_removable_units()
        # ... Lógica de comparación de USBs
        # ¿Hay alguno más?
        if len(current_usbs) > len(known_usbs):
            nuevos = [u for u in current_usbs if u not in known_usbs]
            alerts.light_the_beacons(f"⚠️ ¡OJO! Nuevo hardware detectado: {nuevos}")
            known_usbs = current_usbs  # Actualiza la memoria

        # ¿Falta alguno?
        elif len(current_usbs) < len(known_usbs):
            alerts.light_the_beacons("ℹ️ Dispositivo extraído.")
            known_usbs = current_usbs

        sys.stdout.write(". ")
        sys.stdout.flush()
        time.sleep(WAIT_TIME)

if __name__ == "__main__":
    print(f"🛡️ Gandalf v{updater.CURRENT_VERSION} iniciando guardia...")

    config = logger_manager.load_config()
    # Supongamos que le pasamos 7 días de retención
    logger_manager.setup_logger(days_to_keep=7)

    # 1. Hilo de telegram (Polling)
    # daemon=True para que se cierre si se cierra el programa principal
    threading.Thread(target=alerts.start_bot_polling, daemon=True).start()
    # logger.info("Servicio de alertas (Telegram) iniciado.")
    # 2. Hilo de vigilancia de descargas (Watchdog)
    import downloads_guard
    threading.Thread(target=downloads_guard.start_downloads_guard, daemon=True).start()
    # logger.info("Guardia de descargas activada.")
    # 3. Activa el servidor Flask
    threading.Thread(target=lambda: server_app.run(port=5000, use_reloader=False), daemon=True).start()
    # logger.info("Servidor API interno escuchando en puerto 5000.")
    # 2.Inicia variable
    known_usbs = security.obtain_removable_units()

    # 3. Lanza el bucle de vigilancia en su Hilo (Daemon)
    threading.Thread(target=infinite_surveillance_loop, daemon=True).start()

    # 4. Inicia la bandeja
    threading.Thread(target=tray_icon.start_tray, daemon=True).start()

    # 5. INTERFAZ (HILO PRINCIPAL)
    # Con ventana.withdraw() en interface.py, no sale la ventana al arrancar.
    interface.window.mainloop()

    # 6. Lanza los backups periodizados
    backup_scheduler.run_in_background()

