import os
import sys
import random
import ctypes
import tkinter as tk
from PIL import Image, ImageDraw, ImageFilter

def set_app_id(app_id="gandalf_key"):
    # Registra el ID de aplicación explícito en Windows para agrupar icono y barra de tareas.
    try:
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID(app_id)
    except Exception:
        pass

def get_resource_path(relative_path):
    # Resuelve la ruta absoluta compatible con el entorno de desarrollo y con PyInstaller (.exe).
    if getattr(sys, 'frozen', False):
        base_path = getattr(sys, '_MEIPASS', os.path.dirname(sys.executable))
    else:
        base_path = os.path.dirname(os.path.abspath(__file__))

    # Si se busca dentro de 'img' y la carpeta base no la contiene directamente
    target = os.path.join(base_path, relative_path)
    if not os.path.exists(target):
        # Comprueba si está en src/img o en la raíz del proyecto
        parent_dir = os.path.dirname(base_path)
        alt_target = os.path.join(parent_dir, relative_path)
        if os.path.exists(alt_target):
            return alt_target
    return target

def gandalf_gradient(width, height):
    # Definición de los colores
    colors = [
        (178, 206, 247), (136, 247, 181), (253, 253, 37, 186),
        (255, 186, 21, 222), (245, 195, 195), (221, 182, 247)
    ]
    img = Image.new('RGB', (width, height), colors[0][:3])

    for color in colors[1:]:
        layer = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(layer)
        for _ in range(9):
            radio = random.randint(30, 140)  # nosec
            x, y = random.randint(0, width), random.randint(0, height)  # nosec
            rgb = color[:3]
            alpha_val = color[3] if len(color) > 3 else 30
            draw.ellipse([x - radio, y - radio, x + radio, y + radio], fill=(*rgb, alpha_val))
        layer = layer.filter(ImageFilter.GaussianBlur(40))
        img.paste(layer, (0, 0), layer)
    return img

def deploy_context_menu(window):
    def deploy_menu(event):
        widget_under_mouse = window.winfo_containing(event.x_root, event.y_root)

        # Verifica que sea una caja de texto válida (Entry)
        if isinstance(widget_under_mouse, tk.Entry):
            # Fuerza el foco en ella para asegurar la acción
            widget_under_mouse.focus_set()
            # Crea el menú dinámico usando el widget padre que disparó el evento
            mouse_menu = tk.Menu(window, tearoff=0)

            mouse_menu.add_command(label="Cortar", command=lambda: widget_under_mouse.event_generate('<<Cut>>'))
            mouse_menu.add_command(label="Copiar", command=lambda: widget_under_mouse.event_generate('<<Copy>>'))
            mouse_menu.add_command(label="Pegar", command=lambda: widget_under_mouse.event_generate('<<Paste>>'))

            # Lo despliega exactamente donde el usuario hizo clic con el ratón
            mouse_menu.tk_popup(event.x_root, event.y_root)

    # Vincula el evento del Botón 3 del ratón (Clic derecho en Windows)
    window.bind_all('<Button-3>', deploy_menu)