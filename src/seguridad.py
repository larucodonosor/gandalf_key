import os
import shutil
import psutil
from tkinter import messagebox
import tkinter as tk
import pyautogui

def asegurar_boveda(rutas):
    """Revisa las carpetas y protege los archivos .py que no estén en la bóveda."""
    os.makedirs(".gandalf_vault", exist_ok=True)
    for r in rutas:
        if not os.path.exists(r): continue
        for f in os.listdir(r):
            ruta_completa = os.path.join(r, f)
            if os.path.isfile(ruta_completa) and f.endswith(".py"):
                ruta_destino = os.path.join(".gandalf_vault", f)
                if not os.path.exists(ruta_destino):
                    shutil.copy2(ruta_completa, ruta_destino)
                    print(f"📦 Copia de seguridad inicial: {f}")

def restaurar_archivo(ruta_afectada):
    ruta_vault = os.path.join(".gandalf_vault", os.path.basename(ruta_afectada))
    if os.path.exists(ruta_vault):
        print(f"🩹 Iniciando autocuración para: {ruta_afectada}")
        shutil.copy2(ruta_vault, ruta_afectada)
        print(f"✨ Archivo restaurado con éxito desde la bóveda.")
        return True
    else:
        print(f"⚠️ No hay copia de seguridad en la bóveda para {ruta_afectada}")
        return False

def obtener_unidades_removibles():
    unidades = []
    for particion in psutil.disk_partitions():
        # En Windows, los USB suelen aparecer como 'removable'
        if 'removable' in particion.opts or 'cdrom' in particion.opts:
            unidades.append(particion.device)
    return unidades

def advertencia_visual(url, nivel= "BLOQUEAR"):
    # Configuramos la interfaz de Tkinter
    root = tk.Tk()
    root.withdraw()
    root.attributes("-topmost", True) # Esto hace que salga por encima de todo

    if nivel == "BLOQUEAR":
        titulo_box = "🛡️ BLOQUEO DE SEGURIDAD - GANDALF"
        mensaje_box = f"Lara, este sitio es PELIGROSO:\n\n{url}\n\n¿Quieres que Gandalf bloquee el acceso y te saque de aquí?"
        # askyesno: Si dice SI (quiere que le saque), ejecutamos pyautogui
        sacar_de_aqui = messagebox.askyesno(titulo_box, mensaje_box, master=root)
        if sacar_de_aqui:
            pyautogui.hotkey('alt', 'left')
            root.destroy()
            return False  # No es seguro seguir, la acción de seguridad se activó

    root.destroy()
    return True # Es seguro o el usuario asume el riesgo