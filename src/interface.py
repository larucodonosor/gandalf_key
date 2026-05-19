import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import os
import time
import keyring
from config_controller import ConfigController
import vigilance
import working_mode_ctrl

# LÓGICA DE OCULTAR/MOSTRAR
def hide_window():
    window.withdraw()

def show_window():
    # Llama al icono de la bandeja
    window.deiconify()
    window.attributes("-topmost", True)


def abrir_configuracion_modular(seccion_id):

    # Pide la contraseña maestra antes de permitir el acceso a cualquier sección del panel de configuración.

    # 1. Recupera la contraseña real guardada en el llavero seguro
    master_key_real = keyring.get_password("Gandalf_Guard", "MASTER_KEY")

    # 2. Crea una pequeña ventana pop-up temporal para pedir la clave
    prompt = tk.Toplevel()
    prompt.title("Verificación de Seguridad")
    prompt.geometry("300x150")
    prompt.resizable(False, False)
    prompt.grab_set()  # Bloquea la ventana principal hasta que responda

    tk.Label(prompt, text="Introduce la Master Key de Gandalf:", font=("Arial", 10, "bold")).pack(pady=15)
    entry_verificar = tk.Entry(prompt, show="🫧", width=25)
    entry_verificar.pack()

    def comprobar_clave():
        if entry_verificar.get() == master_key_real:
            prompt.destroy()
            # Caso éxito, lanza el controlador pasándole la sección exacta
            # Cierra la app de fondo si hace falta, o lo abre como Toplevel
            config_app = ConfigController(is_setup_wizard=False, seccion_inicial=seccion_id)
            config_app.mainloop()
        else:
            messagebox.showerror("Acceso Denegado", "Contraseña incorrecta. Intruso detectado.")
            prompt.destroy()

    tk.Button(prompt, text="Verificar 🛡️", command=comprobar_clave).pack(pady=15)


def desplegar_menu_config(boton_origen):
    # Crea y despliega el menú contextual justo debajo del engranaje
    menu_contextual = tk.Menu(window, tearoff=0)

    # Añadimos las opciones mapeadas a los IDs de nuestros archivos modulares
    menu_contextual.add_command(label="📊 Configurar Backups y Logs", command=lambda: abrir_configuracion_modular(3))
    menu_contextual.add_command(label="🔑 Claves de APIs y Cloud", command=lambda: abrir_configuracion_modular(2))
    menu_contextual.add_separator()
    menu_contextual.add_command(label="🛡️ Cambiar Master Key", command=lambda: abrir_configuracion_modular(1))

    # Calculamos la posición del botón en la pantalla para que el menú flote justo debajo
    x = boton_origen.winfo_rootx()
    y = boton_origen.winfo_rooty() + boton_origen.winfo_height()

    menu_contextual.post(x, y)

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

def show_mouse_menu(event):
    mouse_menu = tk.Menu(window, tearoff=0)
    mouse_menu.add_command(label="Cortar", command=lambda: window.focus_get().event_generate('<<Cut>>'))
    mouse_menu.add_command(label="Copiar", command=lambda: window.focus_get().event_generate('<<Copy>>'))
    mouse_menu.add_command(label="Pegar", command=lambda: window.focus_get().event_generate('<<Paste>>'))

    mouse_menu.tk_popup(event.x_root, event.y_root)

def manual_analysis():
    url = url_entry.get()
    if not url or url == 'Introduce URL sospechosa...':
        messagebox.showerror("Atención", "Debes pegar la URL que quieres analizar.")
        return
    run_analysis(url, modo="Manual")
    # La url desaparece al terminar el proceso
    url_entry.delete(0, tk.END)
    # Devuelve el foco para que aparezca el placeholder
    window.focus()

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
window.geometry("650x500")
# Icono
icon_path = os.path.join(os.path.dirname(__file__), "img", "gandalf_grey.ico")
try:
    window.iconbitmap(icon_path)
except:
    pass

canvas = tk.Canvas(window, width=650, height=500, highlightthickness=0)
canvas.pack(fill="both", expand=True)
img_fondo_pil = gandalf_gradient(650, 500)
img_fondo = ImageTk.PhotoImage(img_fondo_pil)
canvas.create_image(0, 0, anchor="nw", image=img_fondo)

canvas.create_text(325, 90, text="CENTINELA GANDALF", font=('Yu Gothic UI', 22, 'bold'), fill="#400835")
# Entrada de URL
url_entry = tk.Entry(window, width=40, font=('Verdana', 11), borderwidth=0,
                       highlightthickness=1, highlightbackground="#bdc3c7", fg='#95a5a6')
url_entry.insert(0, 'Introduce URL sospechosa...')
url_entry.bind('<FocusIn>', on_entry_click)
url_entry.bind('<FocusOut>', on_focusout)
url_entry.bind('<Button-3>', show_mouse_menu)
canvas.create_window(325, 150, window=url_entry, height=35)

# Botón
button_analize = tk.Button(window, text="Analizar Ahora", command=manual_analysis, bg="#231053", fg="white", font=('Verdana', 10, 'bold'),
padx=15, borderwidth=2, cursor="hand2")
canvas.create_window(325, 220, window=button_analize)

# Resultado
result_text_id = canvas.create_text(325, 270, text="Esperando URL...", font=("Verdana", 10, 'bold'), width=450, fill="#400835")

# Botón modo trabajo
btn_work_mode = tk.Button(
    window,
    text="🚫 WORK",
    bg="#b90113",
    fg="white",
font=('Verdana', 10, 'bold'),
    padx=20,
    pady=5,
    borderwidth=1,
    relief="flat",
    cursor="hand2"
)
btn_work_mode.config(command=lambda: working_mode_ctrl.toggle_work_mode(btn_work_mode))
canvas.create_window(325, 470, window=btn_work_mode)

# 7. Botón config (Esquina Superior Derecha)
btn_engranaje = tk.Button(
    window,
    text="Config ⚙",
    font=("Arial", 9, 'bold'),
    bd=0,
    bg="#34495e",
    fg="#ecf0f1",
    activebackground="#2c3e50",
    activeforeground="#deff9a",
    cursor="hand2",
    relief="flat",
    padx=6,
    pady=2
)
btn_engranaje.config(command=lambda: Comic_Dropdown_Call(btn_engranaje))
canvas.create_window(595, 25, window=btn_engranaje)

def Comic_Dropdown_Call(btn):
    # Envoltura rápida para coordinar con la función desplegar_menu_config
    desplegar_menu_config(btn)


window.protocol("WM_DELETE_WINDOW", hide_window)
window.withdraw()
