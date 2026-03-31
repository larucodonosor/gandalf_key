import tkinter as tk
from tkinter import messagebox
import vigilancia
def analizar_manual():
    url = entrada_url.get()
    if not url:
        messagebox.showerror("Atención", "Debes oegar la url que quieres analizar.")
        return
    resultado, informe = vigilancia.analizar_url(url)

    # Cambiamos el color y el texto según el veredicto
    if resultado == "BLOQUEAR":
        etiqueta_resultado.config(text=f"💀 PELIGRO: {informe}", fg="red")
    elif resultado == "DESCONOCIDO":
        etiqueta_resultado.config(text=f"⚠️ AVISO: {informe}", fg="orange")
    else:
        etiqueta_resultado.config(text=f"✅ SEGURO: {informe}", fg="green")

# --- Configuración de la Ventana ---
ventana = tk.Tk()
ventana.title("Gandalf Security Panel 🛡️")
ventana.geometry("500x300")

tk.Label(ventana, text='Introduce URL sospechosa:', font=('Arial', 12)).pack(pady=10)

entrada_url = tk.Entry(ventana, width=50)
entrada_url.pack(pady=5)

boton_analizar = tk.Button(ventana, text="Analizar en Cuarentena", command=analizar_manual, bg="blue", fg="white")
boton_analizar.pack(pady=20)

etiqueta_resultado = tk.Label(ventana, text="Esperando URL...", font=("Arial", 10), wraplength=400)
etiqueta_resultado.pack(pady=10)

ventana.mainloop()
