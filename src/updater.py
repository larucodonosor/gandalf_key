import sys
import subprocess
import platform
import requests
import network_utils

CURRENT_VERSION = "1.0.0"

def download_new_version(url, target_name):
    # Baja el nuevo .exe de GitHub
    def code_download():
        response = requests.get(url, stream=True, timeout=20)
        response.raise_for_status()
        with open(target_name, "wb") as f:
            for chunk in response.iter_content(chunk_size=8192):
                f.write(chunk)
        return True

    try:
        # Usa retry_request
        return network_utils.retry_request(code_download)
    except Exception as e:
        print(f"Error crítico en la descarga tras reintentos: {e}")
        return False

def apply_update():
    current_os = platform.system()  # Retorna 'Windows', 'Linux' o 'Darwin' (macOS)
    suffix = ".exe" if current_os == "Windows" else ""
    exe_name = f"gandalf{suffix}"
    update_exe = f"gandalf_update{suffix}"

    if current_os == "Windows":
        # El script de Windows
        bat_content = f"""
        @echo off
        timeout /t 2 /nobreak > nul
        del "{exe_name}"
        ren "{update_exe}" "{exe_name}"
        start "" "{exe_name}"
        del "%~f0"
        """
        with open("update.bat", "w") as f: f.write(bat_content)
        subprocess.Popen(["update.bat"], shell=True)
    else:
        # Lógica para Linux/macOS (.sh)
        sh_content = f"""
        #!/bin/bash
        sleep 2
        rm "{exe_name}"
        mv "{update_exe}" "{exe_name}"
        chmod +x "{exe_name}"
        ./"{exe_name}" &
        rm "$0"
        """
        with open("update.sh", "w") as f: f.write(sh_content)
        subprocess.Popen(["sh", "update.sh"])

    # Cierra el Gandalf actual inmediatamente
    sys.exit()