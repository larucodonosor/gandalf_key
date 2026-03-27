import pygetwindow as gw

NAVEGADORES = ["chrome", "firefox", "edge", "brave", "opera", "safari"]

def contexto_navegador():
    # Verifica si el usuario está en el navegador para activar el procedimiento correspondiente.
    ventana = gw.getActiveWindow()

    if not ventana:
        return False

    titulo = ventana.title.lower()
    return any(nav in titulo for nav in NAVEGADORES)
