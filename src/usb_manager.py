import os
import platform
import threading
import sys
import time
import security
import devices
import alerts
import logging

logger = logging.getLogger(__name__)

def eject_device(drive_letter):
    # Expulsa de forma segura un dispositivo de almacenamiento en distintos Sistemas Operativos.
    # Acepta formatos tipo 'D:\\' (Windows) o rutas de montaje (Linux/Mac).

    system_os = platform.system()
    logger.info(f"Iniciando protocolo de expulsión en: {system_os}")

    try:
        if system_os == "Windows":
            # Extrae solo la letra de la unidad (ej: 'D:\\' -> 'D')
            letter = drive_letter[0]
            # Usa un comando nativo de Windows (mountvol)
            # Intenta desmontar el dispositivo de forma segura
            # Este script de una línea le dice a Windows que ejecute el verbo nativo de "Expulsar"
            # sobre la unidad física, cortando el bus de datos por completo.
            powershell_cmd = (
                f'powershell -Command "'
                f'$drive = Get-WmiObject Win32_Volume | Where-Object {{ $_.DriveLetter -eq \'{letter}:\' }}; '
                f'if ($drive) {{ (New-Object -ComObject Shell.Application).Namespace(17).ParseName(\'{letter}:\').InvokeVerb(\'Eject\') }}'
                f'"'
            )

            # Ejecuta de forma silenciosa
            os.system(powershell_cmd)
            logger.warning(f"Dispositivo {letter}: expulsado lógicamente.")

        elif system_os == "Linux":
            # Linux desmonta las unidades con 'umount' o 'eject'
            os.system(f'eject "{drive_letter}"')
            logger.warning(f"Dispositivo {drive_letter} expulsado lógicamente.")

        elif system_os == "Darwin":  # 'Darwin' = núcleo de macOS
            # Mac usa diskutil unmount
            os.system(f'diskutil unmountDisk "{drive_letter}"')
            logger.warning(f"Dispositivo {drive_letter} expulsado lógicamente.")

        else:
            logger.error(f"Sistema operativo no soportado para la expulsión automatizada: {system_os}")

    except Exception as e:
        logger.error(f"Fallo crítico al intentar expulsar el hardware en {system_os}: {e}")

def execute_gandalf_usb_customs():
    # Procesa en el milisegundo exacto la inserción comparando la huella digital del chip contra la base de datos.

    global known_usbs
    try:
        current_usbs = security.obtain_removable_units()

        for drive_letter, hardware_id in current_usbs.items():
            if drive_letter not in known_usbs:
                if not devices.is_usb_authorized(hardware_id):
                    alerts.light_the_beacons(
                        f"⚠ ¡ATAQUE FÍSICO! Dispositivo no autorizado con ID {hardware_id} en {drive_letter}",
                        severity='CRITICO'
                    )
                    alerts.request_usb_authorization(drive_letter, hardware_id)
                else:
                    logger.info(f"USB verificado por número de serie: {hardware_id}")

        known_usbs = current_usbs
    except Exception as e:
        logger.error(f"Error en la aduana de USB: {e}")

def trigger_alert():
    # Llama a la acción cuando se detecta un cambio físico, se ejecuta en un hilo separado.
    threading.Thread(target=execute_gandalf_usb_customs(), daemon=True).start()

# ADAPTADOR PARA WINDOWS
def listen_windows_events(hwnd, msg, wparam, lparam):
    # Escucha los eventos de hardware inyectados en la ventana de Tkinter.
    # 0x8000 = WM_DEVICECHANGE (Cambio en los dispositivos)
    # 0x8004 = DBT_DEVICEARRIVAL (Un dispositivo ha conectado físicamente)
    if msg == 0x8000 and wparam == 0x8004:
        logger.info("[Windows Event] ¡Corriente detectada en puerto USB!")
        trigger_alert()
    return None

# ADAPTADOR PARA UNIX (Linux 🐧/ macOS🍏)
def _unix_passive_surveillance():
    # Bucle pasivo ultra-ligero de eventos para entornos Unix.
    global  known_usbs
    while True:
        time.sleep(2)
        current_usbs = security.obtain_removable_units()
        if len(current_usbs) > len(known_usbs):
            logger.info("[Unix Event] ¡Corriente detectada en puerto USB!")
            trigger_alert()
        known_usbs = current_usbs

def start_passive_surveillance(root_window=None):
    # Arranca el motor de escucha reactiva según el Sistema Operativo.
    global known_usbs
    os_type = sys.platform

    known_usbs = security.obtain_removable_units() # Estado inicial para evitar falsos positivos
    if os_type.startswith("win") and root_window:
        try:
            import win32con  # pywin32 intercepta las señales de las ventanas
            # Hooking: Le dice a la ventana de Tkinter que escuche los mensajes de Windows
            root_window.bind_all("<DeviceChange>", lambda e: trigger_alert())
            logger.info("🛡️ Centinela de hardware Windows acoplado a Tkinter con éxito.")
        except Exception:
            # Hilo ligero alternativo
            logger.warning("Falta pywin32. Activando centinela por pooling alternativo.")
            threading.Thread(target=_unix_passive_surveillance, daemon=True).start()

    elif os_type.startswith("linux") or os_type.startswith("darwin"):
        logger.info("🛡️ Inicializando centinela pasivo para entornos Unix.")
        threading.Thread(target=_unix_passive_surveillance, daemon=True).start()

