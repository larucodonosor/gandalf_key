import base64
import pygetwindow as gw
import requests
import keyring
import alerts
import logging

logger = logging.getLogger(__name__)

pending_actions = {}

API_KEY = keyring.get_password('Gandalf_Guard', "VT_API_KEY")

def analyze_url(url):
    if not API_KEY:
        logger.warning("Intento de analizar URL sin API KEY.")
        return "ERROR", "No se encontró la API Key en el archivo .env"
    # VirusTotal necesita la URL en formato base64
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {
        "accept": "application/json",
        "x-apikey": API_KEY
    }

    try:
        response = requests.get(endpoint, headers=headers, timeout=10)

        # Si la URL es nueva y VT no la tiene, se solicita un escaneo
        if response.status_code == 404:
            return "DESCONOCIDO", "URL no analizada previamente. ¡Hulle insensato!"

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
        logger.error(f"Error en analyze_url: {e}")
        return "ERROR", f"Error de conexión: {str(e)}"


def get_brownser_url():
    # Detecta si hay una URL en el título de la ventana activa.
    try:
        active_window = gw.getActiveWindow()
        if active_window:
            title = active_window.title
            # Busca patrones típicos de URLs en el título
            if "http" in title.lower() or "www." in title.lower():
                palabras = title.split()
                for p in palabras:
                    if "http" in p.lower() or "www." in p.lower():
                        return p
    except Exception:
        pass
    return None

