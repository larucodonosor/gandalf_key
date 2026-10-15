from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import vigilance
import alerts
import security
import firewall_rules
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Esto permite que Chrome hable con Python

def dispatch_security_action(url, result, report):

    # Función llamada directamente por el centinela nativo en segundo plano.
    logger.info(f"Procesando acción de seguridad: {url} -> {result}")

    # Peligro
    if result == "BLOQUEAR":
        logger.warning(f"🚨 ¡AMENAZA DETECTADA!: {url}")
        # Avisa desde Telegram
        alerts.light_the_beacons(f"💀 BLOQUEO DESDE EXTENSIÓN: {url}\n{report}", severity='CRITICO')
        # Lanza el pop-up
        popup_thread = threading.Thread(
            target=security.visual_warning,
            args=(url,),
            kwargs={"severity": "BLOQUEAR"},
            daemon=True
        )
        popup_thread.start()

    # Alerta
    elif result == "DESCONOCIDO":
        alerts.light_the_beacons(f" SITIO SOSPECHOSO: {url}\n{report}", severity='CRITICO')
        if firewall_rules.is_browser_in_focus():
            popup_thread = threading.Thread(
                target=security.visual_warning,
                args=(url,),
                kwargs={"severity": "AVISO"},
                daemon=True
            )
            popup_thread.start()

        # 3. OK
    else:
        logger.info(f"Sitio verificado y limpio: {url}")

@app.route('/analizar', methods=['POST'])
def analyze():

    # Ruta HTTP auxiliar mantenida por si algún componente secundario la usa.
    data = request.json or {}
    url = data.get("url")

    if not url:
        return jsonify({"status": "error", "message": "No URL provided"}), 400

    result, report = vigilance.analyze_url(url)
    dispatch_security_action(url, result, report)

    return jsonify({"status": "recibido", "resultado": result})


