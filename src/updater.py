import sys
import os
import subprocess
import platform
import requests
import interface
import network_utils
import logging

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.0.0"

GITHUB_USER = "larucodonosor"
GITHUB_REPO = "Gandalf_key"

# Estandariza las rutas para desarrollo y producción
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_version(version_str):
    # Limpia caracteres como 'v' y convierte '1.1.0' en una tupla (1, 1, 0) para comparar.
    return tuple(map(int, version_str.lower().replace("v", "").split(".")))

def check_for_updates_silently(root_window=None):
    # Consulta la API de GitHub de forma segura. Si detecta una versión superior,
    # lanza un pop-up informativo en la UI principal y ejecuta la mutación.
    url = f"https://api.github.com/repos/{GITHUB_USER}/{GITHUB_REPO}/releases/latest"

    def fetch_release():
        return requests.get(url, timeout=15)

    try:
        logger.info("Comprobando actualizaciones en el repositorio remoto de GitHub...")
        response = network_utils.retry_request(fetch_release)
        if response.status_code != 200:
            logger.warning(f"No se pudo consultar la API de GitHub. Status code: {response.status_code}")
            return

        data = response.json()
        remote_version_str = data.get("tag_name", "1.0.0")

        if parse_version(remote_version_str) > parse_version(CURRENT_VERSION):
            logger.warning(f"¡Nueva versión de seguridad detectada en GitHub: {remote_version_str}!")

            # Busca el binario (.exe o .zip) en los assets
            assets = data.get("assets", [])
            download_url = None
            target_name = "gandalf_update.exe" if platform.system() == "Windows" else "gandalf_update"

            for asset in assets:
                # Modifica según el formato exacto, (.zip o .exe)
                if asset.get("name", "").endswith((".exe", ".zip")):
                    download_url = asset.get("browser_download_url")
                    if asset.get("name", "").endswith(".zip"):
                        target_name = "gandalf_update.zip"
                    break

            if not download_url:
                logger.error("Se encontró una nueva release pero no contiene assets binarios válidos.")
                return

            # Descarga el payload en segundo plano
            success = download_new_version(download_url, target_name)

            if success:
                # INYECCIÓN SEGURA DEL POP-UP EN EL HILO DE TKINTER
                if root_window:
                    root_window.after(0, lambda: show_update_notification(remote_version_str))
        else:
            logger.info("Gandalf se encuentra actualizado en su última versión de producción.")

    except Exception as e:
        logger.error(f"Error durante el chequeo automático de versión: {e}")

def show_update_notification(new_version):
    from gui_components import DarkNotificationPopup

    # Define el contenido específico para el éxito de la actualización
    heading = "¡Búnker Fortificado con Éxito!"
    description = (
        f"Se ha descargado e inyectado la versión {new_version}.\n\n"
        "Para aplicar las actualizaciones contra amenazas,\n"
        "Gandalf se reiniciará de forma inmediata."
    )

    # Llama a la plantilla unificada y le pasa la acción final
    popup = DarkNotificationPopup(
        interface.window,
        title="Gandalf Security — Actualización del Sistema",
        heading=heading,
        description=description,
        button_text="Reiniciar Centinela ⚡",
        callback_action=apply_update  # Pasamos la función como variable SIN paréntesis
    )
    popup.show()

def download_new_version(url, target_name):
    target_path = os.path.join(_BASE_DIR, target_name)
    # Baja el nuevo .exe de GitHub
    def fetch_stream():
        return requests.get(url, stream=True, timeout=20)

    try:
        logger.info(f"Iniciando descarga segura de la actualización desde: {url}")
        response = network_utils.retry_request(fetch_stream)

        # Cuando retry_request garantiza un canal limpio (200), graba
        with open(target_path, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)

        logger.info(f"Actualización descargada y guardada con éxito en: {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error crítico en la descarga tras agotar reintentos: {e}")
        return False

def apply_update():
    current_os = platform.system()  # Retorna 'Windows', 'Linux' o 'Darwin' (macOS)
    suffix = ".exe" if current_os == "Windows" else ""

    if getattr(sys, 'frozen', False):
        exe_path = os.path.abspath(sys.executable)
    else:
        exe_path = os.path.join(_BASE_DIR, f"gandalf_key{suffix}")

    exe_name = os.path.basename(exe_path)
    update_exe_path = os.path.join(_BASE_DIR, f"gandalf_update{suffix}")

    if current_os == "Windows":
        bat_path = os.path.join(_BASE_DIR, "update.bat")
        # El script de Windows
        bat_content = f"""@echo off
setlocal disabledelayedexpansion
set _MEIPASS=
timeout /t 3 /nobreak > nul
        
:loop
taskkill /f /im "Gandalf_key.exe" >nul 2>&1
del "{exe_path}" >nul 2>&1
if exist "{exe_path}" (
    timeout /t 1 /nobreak > nul
    goto loop
)
ren "{update_exe_path}" "{exe_name}"
timeout /t 1 /nobreak > nul
start "" "{exe_path}"
del "%~f0" & exit
"""
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        logger.info("Lanzando mutación desvinculada a través del kernel...")

        # Usa 'start' nativo de cmd para romper la herencia de variables de entorno
        subprocess.Popen(
            f'cmd.exe /c start "" "{bat_path}"',
            shell=True,
            creationflags=subprocess.CREATE_NEW_CONSOLE | subprocess.DETACHED_PROCESS
        )

        # Cierra Gandalf inmediatamente
        sys.exit(0)
    else:
        # Lógica para Linux/macOS (.sh)
        sh_path = os.path.join(_BASE_DIR, "update.sh")
        sh_content = f"""#!/bin/bash
sleep 2
rm "{exe_path}"
mv "{update_exe_path}" "{exe_path}"
chmod +x "{exe_path}"
./"{exe_name}" &
rm "$0"
"""
        with open(sh_path, "w", encoding='utf-8') as f:
            f.write(sh_content)

        logger.info("Script puente Unix (update.sh) generado. Ejecutando mutación...")
        subprocess.Popen(["sh", sh_path],cwd=_BASE_DIR)
        # Cierra el Gandalf actual inmediatamente
        sys.exit(0)