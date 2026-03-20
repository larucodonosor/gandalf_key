import requests

def analizar_url(url):
    url_limpia = url.lower().strip()

    # --- LISTA BLANCA (Whitelist) ---
    sitios_confianza = ["google", "github", "microsoft", "linkedin", "gmail"]
    for sitio in sitios_confianza:
        if sitio in url_limpia:
            print(f"✅ GANDALF: {url_limpia} es de confianza (basado en {sitio})")
            return True, f"😇 Confianza verificada: {sitio} es un entorno seguro."
    # URL de una API pública de chequeo (ejemplo conceptual operativo)
    dominio_api = url_limpia.replace("https://", "").replace("http://", "").split("/")[0]
    api_url = f"https://urlscan.io/api/v1/search/?q=domain:{dominio_api}"

    try:
        # Implementamos timeout para que si el servidor no responde en x tiempo, Gandalf no quede 'colgado'
        respuesta = requests.get(api_url, timeout=5)
        # Convertimos la respuesta (JSON) en un Diccionario de Python
        datos = respuesta.json()

        # LÓGICA DE PRODUCTO:
        # Nivel Crítico: Bloqueo seguro
        # Si la API encuentra resultados, miramos el 'veredicto'
        if datos.get("total", 0) > 0:
            # Si hay historial de ataques en esa URL
            return "BLOQUEAR", f"⚠️ AMENAZA CRÍTICA: este dominio tiene antecedentes de ataques."

        if datos.get("total") == 0:
            return "DESCONOCIDO", f"❓ PRECAUCIÓN: No he encontrado información global sobre este sitio{dominio_api}. Procede con cuidado."

        return True, f"✅ El sitio {dominio_api} parece limpio (según historial global)."
    except:
        return False, "❌ Error de conexión al escanear. Por seguridad, no entres."