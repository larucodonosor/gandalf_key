import sys
import os
import subprocess
import platform
import requests
from tkinter import messagebox
import network_utils
import logging

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.1.0"

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
    # Despliega el aviso imperativo en la UI informando al usuario del reinicio inminente.
    messagebox.showinfo(
        "Actualización Obligatoria de Seguridad",
        f"Se ha detectado e instalado de forma automática la versión {new_version} de Gandalf.\n\n"
        "Para mantener tu equipo protegido el sistema se reiniciará inmediatamente.",
    )
    # Una vez que el usuario cierra el Pop-up (aceptando los hechos), muta el ejecutable
    apply_update()

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
        exe_path = os.path.join(_BASE_DIR, f"gandalf{suffix}")

    update_exe_path = os.path.join(_BASE_DIR, f"gandalf_update{suffix}")

    if current_os == "Windows":
        bat_path = os.path.join(_BASE_DIR, "update.bat")
        # El script de Windows
        bat_content = f"""@echo off
        timeout /t 2 /nobreak > nul
        del "{exe_path}"
        ren "{update_exe_path}" "{exe_path}"
        start "" "{exe_path}"
        del "%~f0"
        """
        with open(bat_path, "w", encoding="utf-8") as f:
            f.write(bat_content)

        logger.info("Script puente Windows (update.bat) generado. Ejecutando actualización...")
        subprocess.Popen(["cmd.exe", "/c", bat_path], cwd=_BASE_DIR)
    else:
        # Lógica para Linux/macOS (.sh)
        sh_path = os.path.join(_BASE_DIR, "update.sh")
        sh_content = f"""#!/bin/bash
        sleep 2
        rm "{exe_path}"
        mv "{update_exe_path}" "{exe_path}"
        chmod +x "{exe_path}"
        ./"{exe_path}" &
        rm "$0"
        """
        with open(sh_path, "w", encoding='utf-8') as f:
            f.write(sh_content)

        logger.info("Script puente Unix (update.sh) generado. Ejecutando mutación...")
        subprocess.Popen(["sh", sh_path],cwd=_BASE_DIR)

    # Cierra el Gandalf actual inmediatamente
    sys.exit()