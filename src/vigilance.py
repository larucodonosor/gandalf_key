import base64
import sys
import time
import subprocess
import threading
import requests
import keyring
import alerts
import firefox_reader
import logging

logger = logging.getLogger(__name__)

pending_actions = {}
API_KEY = keyring.get_password('Gandalf_Guard', "VT_API_KEY")

def analyze_url(url):
    # Evalúa la peligrosidad de la URL.

    try:
        if not API_KEY:
            logger.warning("Intento de analizar URL sin API KEY.")
            return "ERROR", "No se encontró la API Key en el archivo .env"
            # VirusTotal necesita la URL en formato base64 sin relleno '='
        url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

        endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
        headers = {
            "accept": "application/json",
            "x-apikey": API_KEY
        }

        response = requests.get(endpoint, headers=headers, timeout=10)

        # Si la URL es nueva y VT no la tiene, se solicita un escaneo
        if response.status_code == 404:
            return "DESCONOCIDO", "URL no analizada previamente. ¡Huye insensato!"

        if response.status_code != 200:
            logger.warning(f"VirusTotal respondió con un estado inesperado: {response.status_code}")
            return "ERROR", f"Error de plataforma externa (Código {response.status_code})"

        data = response.json()
        # Saca las estadísticas de los 70 antivirus
        stats = data['data']['attributes']['last_analysis_stats']

        malicious = stats['malicious']
        suspicious = stats['suspicious']

        if malicious > 3:
            alerts.light_the_beacons(f"URL Maliciosa detectada: {url}", severity="CRITICO")
            return "BLOQUEAR", f"¡PELIGRO! {malicious} motores lo marcan como virus."
        elif malicious > 0 or suspicious > 0:
            return "DESCONOCIDO", f"Aviso: {malicious + suspicious} alertas detectadas."
        else:
            return "SEGURO", "Limpio. 70 antivirus dicen que es seguro."

    except Exception as e:
        logger.error(f"Error analizando URL: {e}")
        return "DESCONOCIDO", str(e)

def get_browser_url():
    # Obtiene la URL o dirección activa desde el sistema operativo sin extensiones.
    os_name = sys.platform

    # 1. WINDOWS: Lectura directa del control de la barra de direcciones
    if os_name.startswith("win"):
        try:
            import uiautomation as auto
            import psutil

            window = auto.GetForegroundControl()
            if not window:
                return None

            try:
                proc_name = psutil.Process(window.ProcessId).name().lower()
            except Exception:
                proc_name = ""

            target_browsers = {
                "chrome.exe", "msedge.exe", "firefox.exe",
                "brave.exe", "opera.exe"
            }
            if proc_name not in target_browsers:
                return None

            # CASO ESPECÍFICO DE FIREFOX
            if proc_name == "firefox.exe":
                url = firefox_reader.get_firefox_url(window)
                if url:
                    clean_url = url.strip()
                    return clean_url if clean_url.startswith("http") else f"https://{clean_url}"
            # CASO GENERAL CHROMIUM (Chrome, Edge, Brave, Opera)
            else:
                try:
                    toolbar = window.ToolBarControl(searchDepth=6)
                    if toolbar.Exists(0, 0):
                        edit = toolbar.EditControl(searchDepth=3)
                        # Extracción del valor
                        if edit.Exists(0, 0):
                            val = None
                            try:
                                val = edit.GetValuePattern().Value
                            except Exception:
                                pass
                            if not val:
                                try:
                                    val = edit.GetLegacyIAccessiblePattern().Value
                                except Exception:
                                    pass
                            if val and ("." in val):
                                clean_val = val.strip()
                                return clean_val if clean_val.startswith("http") else f"https://{clean_val}"
                except Exception:
                    pass

                # Fallback por título si la lectura de barra no se completa
                raw_title = window.Name or ""
                clean_title = raw_title.replace(" - Google Chrome", "").replace(" - Microsoft Edge", "").strip()
                if clean_title:
                    for part in clean_title.split():
                        if "." in part and not part.endswith((".py", ".sh", ".txt", ".exe")):
                            return f"https://{part}" if not part.startswith("http") else part
        except Exception:
            pass

    # 2. MACOS: Consulta nativa al proceso activo en primer plano
    elif os_name == "darwin":
        script = '''
            tell application "System Events"
            set frontApp to name of first application process whose frontmost is true
            end tell
            if frontApp is "Google Chrome" or frontApp is "Brave Browser" or frontApp is "Microsoft Edge" then
            tell application frontApp to return URL of active tab of front window
            else if frontApp is "Safari" then
            tell application "Safari" to return URL of front document
            end if
            return ""
            '''
        try:
            res = subprocess.check_output(["osascript", "-e", script], text=True).strip()
            if res:
                return res
        except Exception:
            pass

    # 3. LINUX: Lectura de la ventana en foco mediante el servidor gráfico
    elif os_name.startswith("linux"):
        try:
            out = subprocess.check_output(
                ["xdotool", "getactivewindow", "getwindowname"],
                text=True
            ).strip()
            for part in out.split():
                if "." in part and not part.endswith((".py", ".sh", ".txt")):
                    return f"https://{part}" if not part.startswith("http") else part
        except Exception:
            pass
        return None

def start_browser_sentinel(callback_on_threat):

    # Centinela continuo, corre en su propio hilo y analiza URLs nuevas.
    last_url = ""

    def sentinel_loop():
        nonlocal last_url
        while True:
            current_url = get_browser_url()
            if current_url and current_url != last_url:
                last_url = current_url
                logger.info(f"Nueva URL detectada: {current_url}")

                # Ejecuta el análisis de VirusTotal
                result, report = analyze_url(current_url)
                if result in ("BLOQUEAR", "DESCONOCIDO"):
                    callback_on_threat(current_url, result, report)
            time.sleep(0.5)

    thread = threading.Thread(target=sentinel_loop, daemon=True)
    thread.start()

