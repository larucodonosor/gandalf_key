import json
import os
import shutil
import time
import sys
import keyring
import threading
import tray_icon
import alerts
import security
import backup_manager
import backup_scheduler
import integrity_utils
import devices
import usb_manager
import logger_manager
import config_manager
from server_g_k import app as server_app
import updater
import logging

logger = logging.getLogger(__name__)

WAIT_TIME = 60

if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

MEMORY_FILE = os.path.join(_BASE_DIR, "base_memory.json")

def execute_gandalf():
    try:
        # 1. Carga los archivos usando el recolector dinámico
        paths_to_scan = backup_manager.gather_all_treasures_from_config()
    except Exception as e:
        logger.error(f"No se pudo cargar la configuración de carpetas protegidas: {e}")
        return

    current_state = {}

    # Determina las rutas absolutas de sus propios archivos de monitorización
    my_memory_path = os.path.abspath(MEMORY_FILE)
    my_config_path = os.path.abspath(config_manager.get_secure_config_path())
    my_logs_dir = os.path.abspath("logs")

    # 2. Recorre los archivos que nos ha devuelto el escáner
    for file_path in paths_to_scan:
        abs_file_path = os.path.abspath(file_path)

        # Filtros de exclusión para archivos críticos del sistema de Gandalf
        if abs_file_path == my_memory_path or abs_file_path == my_config_path or abs_file_path.startswith(my_logs_dir):
            continue
        if os.path.basename(file_path).startswith("~$"):
            continue

        # Usa el validador de extensiones dinámico
        if backup_manager.is_treasure_extension(file_path):
            try:
                # Calcula el tamaño y la fecha de modificación para el estado actual
                file_size = os.path.getsize(file_path)
                file_mtime = os.path.getmtime(file_path)
                file_hash = backup_manager.get_file_hash(file_path)  # generador de hash

                current_state[file_path] = {
                    "size": file_size,
                    "modified_at": file_mtime,
                    "hash": file_hash
                }
            except Exception:
                continue  # Si un archivo está bloqueado por el SO, pasa al siguiente

    # 3. Intenta cargar la memoria del pasado
    if not os.path.exists(MEMORY_FILE):
        with open(MEMORY_FILE, "w", encoding="utf-8") as f:
            json.dump(current_state, f, indent=4, ensure_ascii=False)
        return

    # 5. El Gran Comparador (La lógica de seguridad)
    try:
    # 5.1. Si existe, lee y compara
        with open(MEMORY_FILE, "r", encoding="utf-8", errors="replace") as f:
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
                    logger.warning(f" Archivo neutralizado y movido a cuarentena.")
                    continue

            # Mira el HASH
            elif current_data["hash"] != past_memory[file]["hash"]:
                base_name = os.path.basename(file)

                # 1. Registro y grito (llama a alerts.py)
                logger.warning(f'Modificación detectada en: {file}')
                alerts.light_the_beacons(f"¡INTRUSO! El archivo {base_name} ha sido modificado.", severity='CRITICO')

                # 2. Protocolo de Decisión
                try:
                    user_config = config_manager.load_config()
                    # Busca si está activo. Si no encuentra la clave, por defecto asumimos False (Modo Seguro activo)
                    work_mode_active = user_config.get("security", {}).get("work_mode", False)
                except Exception:
                    work_mode_active = False

                if work_mode_active:
                    # 🛠️ MODO TRABAJO ON: No molesta al usuario.
                    # Copia el cambio directamente a la bóveda local o actualiza la copia
                    vault_path = os.path.join(".gandalf_vault", base_name)
                    shutil.copy2(file, vault_path)
                    logger.info(f"💾 Work Mode Activo: {base_name} actualizado en la bóveda local automáticamente.")
                else:
                    # 1. Mueve a cuarentena preventiva
                    os.makedirs('quarantine', exist_ok=True)
                    temp_path = os.path.join("quarantine", f"WAITING_{base_name}")
                    shutil.copy2(file, temp_path)  # Copia para analizar

                    if len(base_name) > 60:
                        name, ext = os.path.splitext(base_name)
                        short_name = f"{name[:55]}{ext}"
                    else:
                        short_name = base_name

                    # 2. Registra en la memoria de alertas (PENDING ACTIONS)
                    alerts.pending_actions[short_name] = {
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

    # 6. Actualiza la memoria
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(current_state, f, indent=4, ensure_ascii=False)  # El indent=4 lo hace legible

# Vigila los dispositivos del sistema
def infinite_surveillance_loop():
    global known_usbs
    while True:
        execute_gandalf()

        current_usbs = security.obtain_removable_units()
        # Comprueba si hay alguna clave nueva en los USB detectados
        for drive_letter, hardware_id in current_usbs.items():
            if drive_letter not in known_usbs:

                # COMPROBACIÓN: ¿Este ID de serie está autorizado en el JSON?
                if not devices.is_usb_authorized(hardware_id):
                    alerts.light_the_beacons(
                        f"⚠ ¡ATAQUE FÍSICO! Dispositivo no autorizado con ID {hardware_id} en {drive_letter}",
                        severity='CRITICO')
                    # Le pasamos el ID real al bot para que lo registre si confías
                    alerts.request_usb_authorization(drive_letter, hardware_id)
                else:
                    logger.info(f"🔌 USB verificado por número de serie: {hardware_id}")

        known_usbs = current_usbs

        time.sleep(WAIT_TIME)

# Consulta la disponibilidad de actualizaciones al arrancar y luego cada 24 horas.
def infinite_updater_loop(root_window):
    while True:
        # Pasa la referencia de la ventana gráfica para que el Pop-up se ejecute en el hilo visual
        updater.check_for_updates_silently(root_window)
        # Duerme 24 horas (60s * 60m * 24h)
        time.sleep(86400)

if __name__ == "__main__":
    print(f"🛡️ Gandalf v{updater.CURRENT_VERSION} iniciando guardia...")

    try:
        user_config = config_manager.load_config()
        retention_days = user_config.get("backup", {}).get("retention_days", 7)
    except Exception:
        retention_days = 7

    logger_manager.setup_logger(days_to_keep=retention_days)

    has_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
    if not has_key:
        logger.info("Primera ejecución detectada. Lanzando Asistente de Configuración Independiente...")

        # Importa
        from config_controller import ConfigController

        # Inicializa el asistente en el hilo principal
        wizard = ConfigController(is_setup_wizard=True)

        # Fuerza a Windows a poner el asistente al frente
        wizard.deiconify()
        wizard.lift()
        wizard.attributes("-topmost", True)
        wizard.attributes("-topmost", False)

        # El programa se DETIENE aquí hasta que el usuario le dé a "Finalizar Instalación".
        wizard.mainloop()

        print("✅ Asistente completado con éxito. Inicializando motores principales...")

        # ARRANQUE REAL POST-CONFIGURACIÓN

    # 1. Intenta registrar el ejecutable en el arranque de Windows de forma silenciosa
    try:
        if getattr(sys, 'frozen', False):
            import winreg

            exe_path = os.path.abspath(sys.executable)
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, r"Software\Microsoft\Windows\CurrentVersion\Run", 0,
                                 winreg.KEY_SET_VALUE)
            winreg.SetValueEx(key, "Gandalf_key", 0, winreg.REG_SZ, f'"{exe_path}"')
            winreg.CloseKey(key)
    except Exception:
        pass

    # 2. Hilo de telegram (Polling) daemon=True para que se cierre si se cierra el programa principal
    token_telegram = keyring.get_password("Gandalf_Guard", "TELEGRAM_TOKEN")
    if token_telegram:
        threading.Thread(target=alerts.start_bot_polling, daemon=True).start()

    # 3. Hilo de vigilancia de descargas (Watchdog)
    import downloads_guard
    threading.Thread(target=downloads_guard.start_downloads_guard, daemon=True).start()

    # 4. Activa el servidor Flask
    threading.Thread(target=lambda: server_app.run(port=5000, use_reloader=False), daemon=True).start()

    # 5.Inicia variable
    known_usbs = security.obtain_removable_units()

    # 6. Lanza el bucle de vigilancia en su Hilo (Daemon)
    threading.Thread(target=infinite_surveillance_loop, daemon=True).start()

    # 7. Lanza los backups periodizados
    backup_scheduler.run_in_background()

    # 8. Inicia la bandeja
    threading.Thread(target=tray_icon.start_tray, daemon=True).start()

    # 9. Encendidio de la vigilancia pasiva de hardware
    import interface
    usb_manager.start_passive_surveillance(interface.window)

    # 10. Actualizador automatizado
    threading.Thread(target=infinite_updater_loop, args=(interface.window,), daemon=True).start()

    # 11. INTERFAZ (HILO PRINCIPAL) Con ventana.withdraw() en interface.py, no sale la ventana al arrancar.
    interface.window.mainloop()


