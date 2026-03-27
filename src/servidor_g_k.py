from flask import Flask, request, jsonify
from flask_cors import CORS
import vigilancia  # Tu módulo de análisis
import alertas
import seguridad
import firewall_rules
app = Flask(__name__)
CORS(app)  # Esto permite que Chrome hable con Python


@app.route('/analizar', methods=['POST'])
def analizar():
    datos = request.json
    url = datos.get("url")

    print(f"📡 Recibida URL desde el navegador: {url}")

    # Aquí llamamos a tu lógica de siempre
    resultado, informe = vigilancia.analizar_url(url)

    # Peligro
    if resultado == "BLOQUEAR":
        print(f"🚨 ¡AMENAZA DETECTADA!: {url}")
        # Aquí dispararíamos el pop-up de seguridad.py
        alertas.lanzar_alerta_telegram(f"💀 BLOQUEO DESDE EXTENSIÓN: {url}\n{informe}")
        # Lanzamos el pop-up que ya programaste
        seguridad.advertencia_visual(url, nivel="BLOQUEAR")

    # Alerta
    elif resultado == "DESCONOCIDO":
        alertas.lanzar_alerta_telegram(f"❓ SITIO SOSPECHOSO: {url}\n{informe}")
        if firewall_rules.contexto_navegador():
            seguridad.advertencia_visual(url, nivel="AVISO")

        # 3. OK (Para pruebas)
    else:
        alertas.lanzar_alerta_telegram(f"👍 SITIO SEGURO: {url}")

    return jsonify({"status": "recibido", "resultado": resultado})


