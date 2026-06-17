import os
import shutil
import psutil
import sys
from tkinter import messagebox
import tkinter as tk
import pyautogui
import time
import ctypes
import logging

logger = logging.getLogger(__name__)

# Estandariza las rutas para desarrollo y producción
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

VAULT_DIR = os.path.join(_BASE_DIR, ".gandalf_vault")

def secure_vault(paths):
    # Revisa las carpetas y protege los archivos .py que no estén en la bóveda.
    os.makedirs(VAULT_DIR, exist_ok=True)
    for p in paths:
        if not os.path.exists(p):
            continue
        for f in os.listdir(p):
            full_path = os.path.join(p, f)
            if os.path.isfile(full_path) and f.endswith(".py"):
                destiny_path = os.path.join(".gandalf_vault", f)
                if not os.path.exists(destiny_path):
                    shutil.copy2(full_path, destiny_path)
                    logger.info(f" Copia de seguridad inicial: {f}")

def restore_file(affected_path):
    vault_path = os.path.join(VAULT_DIR, os.path.basename(affected_path))
    if os.path.exists(vault_path):
        logger.info(f" Iniciando autocuración para: {affected_path}")
        try:
            shutil.copy2(vault_path, affected_path)
            logger.info(f" Archivo restaurado con éxito desde la bóveda.")
            return True
        except Exception as e:
            logger.error(f"Fallo crítico en el proceso físico de autocuración: {e}")
            return False
    else:
        logger.warning(f"⚠ No hay copia de seguridad en la bóveda para {affected_path}")
        return False
# PROTECCIÓN USB
def obtain_removable_units():
    units = {}
    os_type = sys.platform
    for partition in psutil.disk_partitions():
        # En Windows, los USB suelen aparecer como 'removable'
        if 'removable' in partition.opts or 'cdrom' in partition.opts:
            drive_letter = partition.device  # Ej: 'D:\\'

            # OBTENCIÓN DE LA HUELLA DACTILAR ÚNICA
            if os_type.startswith("win"):
                try:
                    volume_serial = ctypes.c_ulong()
                    # Llama a la API de Windows para sacar el número de serie real del hardware
                    ctypes.windll.kernel32.GetVolumeInformationW(
                        ctypes.c_wchar_p(drive_letter), None, 0,
                        ctypes.byref(volume_serial), None, None, None, 0
                    )
                    # Convierte el número a una cadena hexadecimal única (ej: 'A1B2C3D4')
                    hardware_id = f"USB_SERIAL_{hex(volume_serial.value).upper()[2:]}"
                except Exception:
                    hardware_id = "UNKNOWN_WINDOWS_DEVICE"

            elif os_type.startswith("linux"):
                try:
                    hardware_id = os.path.basename(os.path.realpath(drive_letter))
                except Exception:
                    hardware_id = "GENERIC_LINUX_USB"
            elif os_type.startswith("darwin"):  # macOS
                hardware_id = drive_letter.replace("/Volumes/", "MAC_USB_")
            else:
                hardware_id = "GENERIC_USB_ID"

            units[drive_letter] = hardware_id

    return units

# AVISOS DEL SISTEMA
def visual_warning(url, severity= "BLOQUEAR"):

    if severity == "BLOQUEAR":
        box_title = "🛡️ BLOQUEO DE SEGURIDAD - GANDALF"
        box_message = f" Este sitio es PELIGROSO:\n\n{url}\n\n¿Quieres que Gandalf bloquee el acceso y te saque de aquí?"

        try:
            # Configura verify_integrity la interfaz de Tkinter
            root = tk.Tk()
            root.withdraw()
            root.attributes("-topmost", True) # Esto hace que salga por encima de todo

            # askyesno: Si dice SI (quiere que le saque), ejecutamos pyautogui
            get_me_out = messagebox.askyesno(box_title, box_message, master=root)
            if get_me_out:
                root.destroy()
                time.sleep(0.2)
                pyautogui.hotkey('alt', 'left')
                return False  # No es seguro seguir, la acción de seguridad se activó
            root.destroy()
            return False
        except Exception as e:
            logger.error(f"Error en la llamada gráfica de advertencia: {e}")
            return False

    return True # Es seguro o el usuario asume el riesgo

def restore_from_quarantine(temp_path, original_name):
    try:
        user_profile = os.path.expanduser('~')

        # Verificación de la carpeta de Descargas independiente del idioma
        potential_download_dirs = [
            os.path.join(user_profile, 'Downloads'),
            os.path.join(user_profile, 'Descargas'),
            os.path.join(user_profile, 'OneDrive', 'Downloads'),
            os.path.join(user_profile, 'OneDrive', 'Descargas')
        ]

        dest_dir = potential_download_dirs[0]
        for path in potential_download_dirs:
            if os.path.exists(path):
                dest_dir = path
                break
        dest = os.path.join(dest_dir, original_name)
        shutil.move(temp_path, dest)
        logger.info(f"Archivo sacado de cuarentena y devuelto a: {dest}")
        return True
    except Exception as e:
        logger.error(f"Error al restaurar el archivo: {e}")
        return False