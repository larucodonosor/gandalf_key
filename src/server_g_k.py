from flask import Flask, request, jsonify
from flask_cors import CORS
import threading
import vigilance  # Tu módulo de análisis
import alerts
import security
import firewall_rules
import logging

logger = logging.getLogger(__name__)

app = Flask(__name__)
CORS(app)  # Esto permite que Chrome hable con Python


@app.route('/analizar', methods=['POST'])
def analyze():
    data = request.json
    url = data.get("url")

    logger.info(f" Recibida URL desde el navegador: {url}")

    result, report = vigilance.analyze_url(url)

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
        alerts.light_the_beacons(f" SITIO SOSPECHOSO: {url}\n{report}")
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

    return jsonify({"status": "recibido", "resultado": result})


