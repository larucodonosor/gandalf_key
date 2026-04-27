import json
import os

CONFIG_FILE = "config_user.json"

def cargar_config():
    if not os.path.exists(CONFIG_FILE):
        # Configuración por defecto si no existe
        return {"backup": {"enabled": True, "days": ["tuesday", "friday"], "time": "03:00"}}
    with open(CONFIG_FILE, "r") as f:
        return json.load(f)

def guardar_config(nueva_config):
    with open(CONFIG_FILE, "w") as f:
        json.dump(nueva_config, f, indent=4)