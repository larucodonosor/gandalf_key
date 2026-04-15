import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import os
import threading
import time
import vigilancia  # Asegúrate de que vigilancia.py está en la misma carpeta

# --- LÓGICA DE OCULTAR/MOSTRAR ---
def ocultar_ventana():
    ventana.withdraw()

def mostrar_ventana():
    # Llama al icono de la bandeja
    ventana.deiconify()
    ventana.attributes("-topmost", True)

# --- LÓGICA DE DISEÑO ---
def degradar_gandalf(ancho, alto):
    # Definimos colores simples (R, G, B) para evitar errores de tuplas
    colores = [
        (178, 206, 247), (136, 247, 181), (253, 253, 37, 186),
        (255, 186, 21, 222), (245, 195, 195), (221, 182, 247)
    ]
    img = Image.new('RGB', (ancho, alto), colores[0][:3])

    for color in colores[1:]:
        capa = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        dibujo = ImageDraw.Draw(capa)
        for _ in range(9):
            radio = random.randint(30, 140)
            x, y = random.randint(0, ancho), random.randint(0, alto)
            # Aquí está el truco: nos aseguramos de que sea (R, G, B, A)
            rgb = color[:3]
            alfa_val = color[3] if len(color) > 3 else 30
            # color_con_alfa = (color[0], color[1], color[2], 30)
            dibujo.ellipse([x - radio, y - radio, x + radio, y + radio], fill=(*rgb, alfa_val))
        capa = capa.filter(ImageFilter.GaussianBlur(40))
        img.paste(capa, (0, 0), capa)
    return img


# --- LÓGICA DE CONTROL (Placeholder y Funciones) ---
def on_entry_click(event):
    if entrada_url.get() == 'Introduce URL sospechosa...':
        entrada_url.delete(0, tk.END)
        entrada_url.config(fg='#2c3e50')


def on_focusout(event):
    if entrada_url.get() == '':
        entrada_url.insert(0, 'Introduce URL sospechosa...')
        entrada_url.config(fg='#95a5a6')


def analizar_manual():
    url = entrada_url.get()
    if not url or url == 'Introduce URL sospechosa...':
        messagebox.showerror("Atención", "Debes pegar la URL que quieres analizar.")
        return
    ejecutar_analisis(url, modo="Manual")


def ejecutar_analisis(url, modo="Auto"):
    resultado, informe = vigilancia.analizar_url(url)

    color = "#1e6e06"  # Verde
    prefijo = "✓ SEGURO"

    if resultado == "BLOQUEAR":
        color = "#b90113"  # Rojo
        prefijo = "💀 PELIGRO"
    elif resultado == "DESCONOCIDO":
        color = "#8e3a00"  # Naranja
        prefijo = "⚠️ AVISO"

    mensaje = f"{modo}-Scan: {prefijo}\n{informe}"
    canvas.itemconfig(id_resultado, text=mensaje, fill=color)


# --- VIGILANCIA EN SEGUNDO PLANO ---
def vigilar_en_segundo_plano():
    ultima_url = ""
    while True:
        url_detectada = vigilancia.obtener_url_del_navegador()
        if url_detectada and url_detectada != ultima_url:
            ultima_url = url_detectada
            # Actualizamos la interfaz de forma segura
            ventana.after(0, lambda u=url_detectada: ejecutar_analisis(u, modo="Auto"))
        time.sleep(3)


# --- CONFIGURACIÓN DE LA VENTANA ---
ventana = tk.Tk()
ventana.title("Gandalf Security Panel 🛡️")
ventana.geometry("550x350")  # Un poco más alta para que quepa bien el texto

# Icono
ruta_ico = os.path.join(os.path.dirname(__file__), "img", "gandalf_grey.ico")
try:
    ventana.iconbitmap(ruta_ico)
except:
    pass

canvas = tk.Canvas(ventana, width=550, height=380, highlightthickness=0)
canvas.pack(fill="both", expand=True)

img_fondo_pil = degradar_gandalf(550, 380)
img_fondo = ImageTk.PhotoImage(img_fondo_pil)
canvas.create_image(0, 0, anchor="nw", image=img_fondo)

canvas.create_text(250, 60, text="CENTINELA GANDALF", font=('Yu Gothic UI', 22, 'bold'), fill="#2c3e50")

# Entrada de URL
entrada_url = tk.Entry(ventana, width=40, font=('Verdana', 11), borderwidth=0,
                       highlightthickness=1, highlightbackground="#bdc3c7", fg='#95a5a6')
entrada_url.insert(0, 'Introduce URL sospechosa...')
entrada_url.bind('<FocusIn>', on_entry_click)
entrada_url.bind('<FocusOut>', on_focusout)
canvas.create_window(250, 140, window=entrada_url, height=35)

# Botón
boton_analizar = tk.Button(ventana, text="Analizar Ahora", command=analizar_manual,
                           bg="#162683", fg="white", font=('Verdana', 10, 'bold'),
                           padx=15, borderwidth=2, cursor="hand2")
canvas.create_window(250, 210, window=boton_analizar)

# Resultado
id_resultado = canvas.create_text(250, 290, text="Esperando URL...",
                                  font=("Verdana", 10, 'bold'), width=450, fill="#2c3e50")

# --- 5. INICIO DEL CENTINELA ---
# hilo = threading.Thread(target=vigilar_en_segundo_plano, daemon=True)
# hilo.start()

ventana.protocol("WM_DELETE_WINDOW", ocultar_ventana)
ventana.withdraw()