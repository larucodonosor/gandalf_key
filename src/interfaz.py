import tkinter as tk
from tkinter import messagebox
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import random
import vigilancia

def degradar_gandalf(ancho, alto):
    colores = [
        (178, 206, 247),  # Azul pálido (Cielo)
        (136, 247, 181),  # Verde pálido (Bosque)
        (253, 253, 37, 186),  # Amarillo/Crema (Luz)
        (255, 186, 21, 222),  # Naranja pálido (Atardecer)
        (245, 195, 195),  # Rojo/Rosa pálido (Fuego suave)
        (221, 182, 247)  # Violeta pálido
    ]
    # Imagen base
    img = Image.new('RGB', (ancho, alto), colores[0][:3])

    for color in colores[1:]:
        # Capa transparente para cada color
        capa = Image.new('RGBA', (ancho, alto), (0, 0, 0, 0))
        dibujo = ImageDraw.Draw(capa)

        num_manchas = 7
        # Dibujamos unos de círculos aleatorios
        for _ in range(num_manchas):
            radio = random.randint(30, 140)
            x, y = random.randint(0, ancho), random.randint(0, alto)
            # Manejamos si el color tiene alpha (0-1) o no
            rgb = color[:3]
            alfa_val = color[3] if len(color) > 3 else 30
            dibujo.ellipse([x - radio, y - radio, x + radio, y + radio], fill=(*rgb, alfa_val))

        # El secreto: un desenfoque (blur) MUY fuerte para que parezca una nube
        capa = capa.filter(ImageFilter.GaussianBlur(40))
        img.paste(capa, (0, 0), capa)
    return img

def analizar_manual():
    url = entrada_url.get()
    if not url or url == 'Introduce URL sospechosa...':
        messagebox.showerror("Atención", "Debes pegar la URL que quieres analizar.")
        return
    resultado, informe = vigilancia.analizar_url(url)



    # Para cambiar el texto en un Canvas usamos itemconfig
    color = "#71ff47"
    mensaje = f"✅ SEGURO: {informe}"
    if resultado == "BLOQUEAR":
        color = "#C0392B"
        mensaje = f"💀 PELIGRO: {informe}"
    elif resultado == "DESCONOCIDO":
        color = "#D35400"
        mensaje = f"⚠️ AVISO: {informe}"

    canvas.itemconfig(id_resultado, text=mensaje, fill=color)

def on_entry_click(event):
    if entrada_url.get() == 'Introduce URL sospechosa...':
       entrada_url.delete(0, tk.END) # Borra el placeholder
       entrada_url.config(fg='#2c3e50') # Pone el texto en color normal

def on_focusout(event):
    if entrada_url.get() == '':
        entrada_url.insert(0, 'Introduce URL sospechosa...') # Vuelve a poner el placeholder
        entrada_url.config(fg='#95a5a6') # Pone el texto en gris

# --- Configuración de la Ventana ---
ventana = tk.Tk()
ventana.title("Gandalf Security Panel 🛡️")
ventana.geometry("550x350")

canvas = tk.Canvas(ventana, width=550, height=350, highlightthickness=0)
canvas.pack(fill="both", expand=True)

# Creamos y aplicamos el degradado como fondo
img_fondo_pil = degradar_gandalf(550, 350)
img_fondo = ImageTk.PhotoImage(img_fondo_pil)
canvas.create_image(0, 0, anchor="nw", image=img_fondo)

# label_fondo = tk.Label(ventana, image=img_fondo)
# label_fondo.place(x=0, y=0, relwidth=1, relheight=1)  # .place para que sea el fondo

# tk.Label(ventana, text='Introduce URL sospechosa:', font=('Verdana', 11),bg="#e6f0ff", fg="#7f8c8d").pack(pady=10)
# tk.Label(ventana, text='CENTINELA GANDALF', font=('Yu Gothic UI Light', 22), fg="#2c3e50").pack(pady=(30, 10))
# tk.Label(ventana, text='Introduce URL sospechosa:', font=('Verdana', 10), fg="#7f8c8d").pack(pady=(30, 5))
# 1. DIBUJAMOS EL TÍTULO (Sin background)
canvas.create_text(250, 60, text="CENTINELA GANDALF",
                   font=('Yu Gothic UI', 22), fill="#2c3e50")

entrada_url = tk.Entry(ventana, width=40, font=('Verdana', 11), borderwidth=0, highlightthickness=1, highlightbackground="#bdc3c7", # Borde gris fino
                       fg='#95a5a6')
entrada_url.insert(0, 'Introduce URL sospechosa...') # Insertar placeholder inicial
entrada_url.bind('<FocusIn>', on_entry_click)
entrada_url.bind('<FocusOut>', on_focusout)

canvas.create_window(250, 140, window=entrada_url, height=35)

boton_analizar = tk.Button(ventana, text="Analizar", command=analizar_manual, bg="#162683", fg="white", font=('Verdana', 10, 'bold'), padx=20, borderwidth=2, cursor="hand2")
# boton_analizar.pack(pady=20)
canvas.create_window(250, 210, window=boton_analizar)

id_resultado = canvas.create_text(250, 280, text="Esperando URL...", font=("Verdana", 10, 'bold'), width=450, fill="#2c3e50")


ventana.mainloop()
