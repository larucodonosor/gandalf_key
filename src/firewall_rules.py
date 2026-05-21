import pygetwindow as gw

BROWSERS = ["chrome", "firefox", "edge", "brave", "opera", "safari"]

def is_browser_in_focus():
    # Verifica si el usuario está en el navegador para activar el procedimiento correspondiente.
    try:
        active_window = gw.getActiveWindow()

        if not active_window or active_window.title is None:
            return False

        window_title = active_window.title.lower()
        return any(browser in window_title for browser in BROWSERS)

    except Exception as e:
        return False
