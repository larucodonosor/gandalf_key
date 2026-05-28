import sys
import os
import subprocess
import platform
import requests
import network_utils
import logging

logger = logging.getLogger(__name__)

CURRENT_VERSION = "1.0.0"

# Estandariza las rutas para desarrollo y producción
if getattr(sys, 'frozen', False):
    _BASE_DIR = os.path.dirname(sys.executable)
else:
    _BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

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
        logger.error(f"Error crítico insalvable en la descarga tras agotar reintentos: {e}")
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
        bat_content = f"""
        @echo off
        timeout /t 2 /nobreak > nul
        del "{exe_path}"
        ren "{update_exe_path}" "{exe_path}"
        start "" "{exe_path}"
        del "%~f0"
        """
        with open("bat_path", "w", encoding="utf-8") as f:
            f.write(bat_content)

        logger.info("Script puente Windows (update.bat) generado. Ejecutando actualización...")
        subprocess.Popen(["cmd.exe", "/c", bat_path], cwd=_BASE_DIR)
    else:
        # Lógica para Linux/macOS (.sh)
        sh_path = os.path.join(_BASE_DIR, "update.sh")
        sh_content = f"""
        #!/bin/bash
        sleep 2
        rm "{exe_path}"
        mv "{update_exe_path}" "{exe_path}"
        chmod +x "{exe_path}"
        ./"{exe_path}" &
        rm "$0"
        """
        with open("update.sh", "w", encoding='utf-8') as f:
            f.write(sh_content)

        logger.info("Script puente Unix (update.sh) generado. Ejecutando mutación...")
        subprocess.Popen(["sh", sh_path],cwd=_BASE_DIR)

    # Cierra el Gandalf actual inmediatamente
    sys.exit()