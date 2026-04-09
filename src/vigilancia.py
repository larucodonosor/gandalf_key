import requests
import os
import base64
import pygetwindow as gw
from dotenv import load_dotenv


load_dotenv()
API_KEY = os.getenv("VIRUSTOTAL_API_KEY")

def analizar_url(url):
    if not API_KEY:
        return "ERROR", "No se encontró la API Key en el archivo .env"
    # VirusTotal necesita la URL en formato base64
    url_id = base64.urlsafe_b64encode(url.encode()).decode().strip("=")

    endpoint = f"https://www.virustotal.com/api/v3/urls/{url_id}"
    headers = {
        "accept": "application/json",
        "x-apikey": API_KEY
    }

    try:
        respuesta = requests.get(endpoint, headers=headers)

        # Si la URL es nueva y VT no la tiene, hay que pedirle que la escanee
        if respuesta.status_code == 404:
            return "DESCONOCIDO", "URL no analizada previamente. ¡Cuidado!"

        datos = respuesta.json()

        # Sacamos las estadísticas de los 70 antivirus
        stats = datos['data']['attributes']['last_analysis_stats']
        maliciosos = stats['malicious']
        sospechosos = stats['suspicious']

        if maliciosos > 3:
            return "BLOQUEAR", f"¡PELIGRO! {maliciosos} motores lo marcan como virus."
        elif maliciosos > 0 or sospechosos > 0:
            return "DESCONOCIDO", f"Aviso: {maliciosos + sospechosos} alertas detectadas."
        else:
            return "SEGURO", "Limpio. 70 antivirus dicen que es seguro."

    except Exception as e:
        return "ERROR", f"Error de conexión: {str(e)}"


def obtener_url_del_navegador():
    """Detecta si hay una URL en el título de la ventana activa."""
    try:
        ventana_activa = gw.getActiveWindow()
        if ventana_activa:
            titulo = ventana_activa.title
            # Buscamos patrones típicos de URLs en el título
            if "http" in titulo.lower() or "www." in titulo.lower():
                palabras = titulo.split()
                for p in palabras:
                    if "http" in p.lower() or "www." in p.lower():
                        return p
    except:
        pass
    return None

