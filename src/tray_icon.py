import pystray
from PIL import Image, ImageDraw
import os

# referencia para mantener el icono
icono_instancia = None

def toggle_panel(icon, item):
    import interfaz
    # state() dice si la ventana está visible, (normal) u oculta (withdrawn)
    if interfaz.ventana.state() == 'normal':
        interfaz.ocultar_ventana()
    else:
        interfaz.mostrar_ventana()


def iniciar_bandeja():
    global icono_instancia

    ruta_ico = os.path.join(os.path.dirname(__file__), "img", "gandalf_grey.ico")

    try:
        imagen = Image.open(ruta_ico)
    except:
        # Si fallala carga del icono, un círculo verde indica que el sistema está activo.
        imagen = Image.new('RGBA', (64, 64), color=(255, 255, 255,0))

        dibujo = ImageDraw.Draw(imagen)

        # 3. Dibuja el círculo verde con 'ellipse'
        # Las coordenadas del cuadrado que lo contiene son [x0, y0, x1, y1]
        # EL diseño tiene un margen de 4 píxeles para que no toque los bordes
        color_verde = (0, 200, 0, 255)  # Un verde suave
        dibujo.ellipse([4, 4, 60, 60], fill=color_verde, outline=(0, 100, 0, 255), width=2)

    # El menú usa la función toogle y a aplicarla al icono
    menu = pystray.Menu(
        pystray.MenuItem("Panel Gandalf 🛡️", toggle_panel, default=True)
    )

    icono_instancia = pystray.Icon("Gandalf", imagen, "Gandalf Security (Protección Activa)", menu)

    print("🛡️ Gandalf se muestra en la bandeja del sistema.")
    icono_instancia.run()