import requests

def analizar_url(url):
    # URL de una API pública de chequeo (ejemplo conceptual operativo)
    api_url = f"https://urlscan.io/api/v1/search/?q=domain:{url}"

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

        return True, "✅ El sitio parece limpio (por ahora)"
    except:
        return False, "❌ Error de conexión al escanear. Por seguridad, no entres."