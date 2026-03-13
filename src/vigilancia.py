import requests

def analizar_url(url):
    # Normalizamos el enlace
    url_limpia = url.lower().strip()

    # Nuestra lista de "malos conocidos"
    LISTA_NEGRA = [
        "https://www.google.com/url?sa=E&source=gmail&q=pago-pablo.com",
        "ganancia-facil.net",
        "actualiza-tu-password.io",
        "bit.ly/premio-seguro"
        ]

    for sitio_maligno in LISTA_NEGRA:
        if sitio_maligno in url.lower():
            return False, "⚠️ SITIO DETECTADO EN LISTA NEGRA DE PHISHING"

    return True, "✅ El sitio parece limpio (por ahora)"