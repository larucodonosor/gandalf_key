import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import os
import time
import vigilance
import working_mode_ctrl

# LÓGICA DE OCULTAR/MOSTRAR
def hide_window():
    window.withdraw()

def show_window():
    # Llama al icono de la bandeja
    window.deiconify()
    window.attributes("-topmost", True)

# LÓGICA DE DISEÑO
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
            radio = random.randint(30, 140)
            x, y = random.randint(0, width), random.randint(0, height)
            rgb = color[:3]
            alpha_val = color[3] if len(color) > 3 else 30
            draw.ellipse([x - radio, y - radio, x + radio, y + radio], fill=(*rgb, alpha_val))
        layer = layer.filter(ImageFilter.GaussianBlur(40))
        img.paste(layer, (0, 0), layer)
    return img


# LÓGICA DE CONTROL (Placeholder y Funciones)
def on_entry_click(event):
    if url_entry.get() == 'Introduce URL sospechosa...':
        url_entry.delete(0, tk.END)
        url_entry.config(fg='#2c3e50')


def on_focusout(event):
    if url_entry.get() == '':
        url_entry.insert(0, 'Introduce URL sospechosa...')
        url_entry.config(fg='#95a5a6')


def manual_analysis():
    url = url_entry.get()
    if not url or url == 'Introduce URL sospechosa...':
        messagebox.showerror("Atención", "Debes pegar la URL que quieres analizar.")
        return
    run_analysis(url, modo="Manual")


def run_analysis(url, modo="Auto"):
    result, report = vigilance.analyze_url(url)

    color = "#1e6e06"  # Verde
    prefix = "✓ SEGURO"

    if result == "BLOQUEAR":
        color = "#b90113"  # Rojo
        prefix = "💀 PELIGRO"
    elif result == "DESCONOCIDO":
        color = "#8e3a00"  # Naranja
        prefix = "⚠️ AVISO"

    menssage = f"{modo}-Scan: {prefix}\n{report}"
    canvas.itemconfig(result_text_id, text=menssage, fill=color)


# VIGILANCIA EN SEGUNDO PLANO
def background_monitor():
    last_url = ""
    while True:
        detected_url = vigilance.get_brownser_url()
        if detected_url and detected_url != last_url:
            last_url = detected_url
            # Actualiza la interfaz de forma segura
            window.after(0, lambda u=detected_url: run_analysis(u, modo="Auto"))
        time.sleep(3)


# CONFIGURACIÓN DE LA VENTANA
window = tk.Tk()
window.title("Gandalf Security Panel 🛡️")
window.geometry("550x500")

# Botón modo trabajo
btn_work_mode = tk.Button(
    window,
    text="🚫 WORK",
    bg="red",
    fg="white",
    command=lambda: working_mode_ctrl.toggle_work_mode(btn_work_mode)
)
btn_work_mode.pack(pady=10)

# Icono
icon_path = os.path.join(os.path.dirname(__file__), "img", "gandalf_grey.ico")
try:
    window.iconbitmap(icon_path)
except:
    pass

canvas = tk.Canvas(window, width=550, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)

img_fondo_pil = gandalf_gradient(550, 500)
img_fondo = ImageTk.PhotoImage(img_fondo_pil)
canvas.create_image(0, 0, anchor="nw", image=img_fondo)

canvas.create_text(250, 60, text="CENTINELA GANDALF", font=('Yu Gothic UI', 22, 'bold'), fill="#2c3e50")

# Entrada de URL
url_entry = tk.Entry(window, width=40, font=('Verdana', 11), borderwidth=0,
                       highlightthickness=1, highlightbackground="#bdc3c7", fg='#95a5a6')
url_entry.insert(0, 'Introduce URL sospechosa...')
url_entry.bind('<FocusIn>', on_entry_click)
url_entry.bind('<FocusOut>', on_focusout)
canvas.create_window(250, 140, window=url_entry, height=35)

# Botón
button_analize = tk.Button(window, text="Analizar Ahora", command=manual_analysis,
                           bg="#162683", fg="white", font=('Verdana', 10, 'bold'),
                           padx=15, borderwidth=2, cursor="hand2")
canvas.create_window(250, 210, window=button_analize)

# Resultado
result_text_id = canvas.create_text(250, 290, text="Esperando URL...",
                                  font=("Verdana", 10, 'bold'), width=450, fill="#2c3e50")

window.protocol("WM_DELETE_WINDOW", hide_window)
window.withdraw()
