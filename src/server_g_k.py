from flask import Flask, request, jsonify
from flask_cors import CORS
import vigilance  # Tu módulo de análisis
import alerts
import security
import firewall_rules

app = Flask(__name__)
CORS(app)  # Esto permite que Chrome hable con Python


@app.route('/analizar', methods=['POST'])
def analyze():
    data = request.json
    url = data.get("url")

    print(f" Recibida URL desde el navegador: {url}")

    result, report = vigilance.analyze_url(url)

    # Peligro
    if result == "BLOQUEAR":
        print(f"🚨 ¡AMENAZA DETECTADA!: {url}")
        # Aquí dispara el pop-up de security.py
        alerts.light_the_beacons(f"💀 BLOQUEO DESDE EXTENSIÓN: {url}\n{report}")
        # Lanza el pop-up
        security.visual_warning(url, severity="BLOQUEAR")

    # Alerta
    elif result == "DESCONOCIDO":
        alerts.light_the_beacons(f" SITIO SOSPECHOSO: {url}\n{report}")
        if firewall_rules.is_browser_in_focus():
            security.visual_warning(url, severity="AVISO")

        # 3. OK
    else:
        alerts.light_the_beacons(f" SITIO SEGURO: {url}")

    return jsonify({"status": "recibido", "resultado": result})


