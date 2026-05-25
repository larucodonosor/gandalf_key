import pystray
from PIL import Image, ImageDraw
import os
import sys
import ctypes

def set_app_id():
    myappid = 'mi.proyecto.gandalf.v1' # Un nombre único
    ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(myappid)

set_app_id()

# Referencia para mantener el icono
icon_instance = None

# Asegura las rutas de los iconos tante en desarrollo como en producción
def get_resource_path(relative_path):
    if getattr(sys, 'frozen', False):
        base_path = sys._MEIPASS
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_path, relative_path)

def toggle_panel(icon, item):
    import interface
    # state() dice si la ventana está visible, (normal) u oculta (withdrawn)
    if interface.window.state() == 'normal':
        interface.hide_window()
    else:
        interface.show_window()

def start_tray():
    global icon_instance

    icon_path = get_resource_path(os.path.join("src", "img", "gandalf_grey.ico"))

    try:
        image = Image.open(icon_path)
    except:
        # Si falla la carga del icono, (círculo verde) que indica que el sistema está activo.
        image = Image.new('RGBA', (64, 64), color=(255, 255, 255,0))

        draw = ImageDraw.Draw(image)

        # 3. Dibuja el círculo verde con 'ellipse'
        # Las coordenadas del cuadrado que lo contiene son [x0, y0, x1, y1]
        # EL diseño tiene un margen de 4 píxeles para que no toque los bordes
        green_color = (0, 200, 0, 255)  # Un verde suave
        draw.ellipse([4, 4, 60, 60], fill=green_color, outline=(0, 100, 0, 255), width=2)

    # El menú usa la función toogle y la aplica al icono
    menu = pystray.Menu(
        pystray.MenuItem("Panel Gandalf 🛡️", toggle_panel, default=True)
    )

    icon_instance = pystray.Icon("Gandalf", image, "Gandalf Security (Protección Activa)", menu)
    icon_instance.run()