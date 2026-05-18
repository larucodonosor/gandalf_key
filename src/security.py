import os
import shutil
import psutil
from tkinter import messagebox
import tkinter as tk
import pyautogui
import time
import logging

logger = logging.getLogger(__name__)

def secure_vault(paths):
    # Revisa las carpetas y protege los archivos .py que no estén en la bóveda.
    os.makedirs(".gandalf_vault", exist_ok=True)
    for p in paths:
        if not os.path.exists(p): continue
        for f in os.listdir(p):
            full_path = os.path.join(p, f)
            if os.path.isfile(full_path) and f.endswith(".py"):
                destiny_path = os.path.join(".gandalf_vault", f)
                if not os.path.exists(destiny_path):
                    shutil.copy2(full_path, destiny_path)
                    logger.info(f" Copia de seguridad inicial: {f}")

def restore_file(affected_path):
    vault_path = os.path.join(".gandalf_vault", os.path.basename(affected_path))
    if os.path.exists(vault_path):
        logger.info(f" Iniciando autocuración para: {affected_path}")
        shutil.copy2(vault_path, affected_path)
        logger.info(f" Archivo restaurado con éxito desde la bóveda.")
        return True
    else:
        logger.warning(f"⚠ No hay copia de seguridad en la bóveda para {affected_path}")
        return False
# PROTECCIÓN USB
def obtain_removable_units():
    units = []
    for partition in psutil.disk_partitions():
        # En Windows, los USB suelen aparecer como 'removable'
        if 'removable' in partition.opts or 'cdrom' in partition.opts:
            units.append(partition.device)
    return units

# AVISOS DEL SISTEMA
def visual_warning(url, severity= "BLOQUEAR"):
    # Configura verify_integrity la interfaz de Tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # Esto hace que salga por encima de todo

    if severity == "BLOQUEAR":
        box_title = "🛡️ BLOQUEO DE SEGURIDAD - GANDALF"
        box_message = f" Este sitio es PELIGROSO:\n\n{url}\n\n¿Quieres que Gandalf bloquee el acceso y te saque de aquí?"
        # askyesno: Si dice SI (quiere que le saque), ejecutamos pyautogui
        get_me_out = messagebox.askyesno(box_title, box_message, master=root)
        if get_me_out:
            root.destroy()
            time.sleep(0.2)
            pyautogui.hotkey('alt', 'left')
            return False  # No es seguro seguir, la acción de seguridad se activó
        root.destroy()
        return False
    root.destroy()
    return True # Es seguro o el usuario asume el riesgo

def restore_from_quarantine(temp_path, original_name):
    import shutil
    try:
        dest = os.path.join(os.path.expanduser('~'), 'Downloads', original_name)
        shutil.move(temp_path, dest)
        return True
    except Exception as e:
        logger.error(f"Error al restaurar el archivo: {e}")
        return False