import json
import os
from dotenv import load_dotenv

load_dotenv()
MASTER_KEY = os.getenv("MASTER_KEY")
DB_USB = "conocidos.json"

def asegurar_archivo_db():
    # Crea el archivo si no existe
    if not os.path.exists(DB_USB):
        with open(DB_USB, "w") as f:
            json.dump([], f)
        print(f" Base de datos {DB_USB} creada correctamente.")

def cargar_conocidos():
    asegurar_archivo_db()
    try:
        with open(DB_USB, "r") as f:
        return json.load(f)
    except:
        return []

def es_usb_autorizado(id_usb):
    return id_usb in cargar_conocidos()

def autorizar_nuevo_usb(id_usb, clave_introducida):
    # Verifica la llave maestra antes de guardar
    if clave_introducida == MASTER_KEY:
        conocidos = cargar_conocidos()
        if id_usb not in conocidos:
            conocidos.append(id_usb)
            with open(DB_USB, "w") as f:
                json.dump(conocidos, f, indent=4)
        return True, "✅ USB Autorizado con éxito."
    return False, "❌ Clave incorrecta. Acceso denegado."