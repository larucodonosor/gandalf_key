import hashlib
import os
import json


def generar_huella(ruta_archivo):
    """Genera el hash SHA-256 de un archivo."""
    try:
        with open(ruta_archivo, "rb") as f:
            contenido = f.read()
            return hashlib.sha256(contenido).hexdigest()
    except Exception:
        return None


def mapear_carpeta(ruta_directorio):
    """Escanea una carpeta y devuelve un diccionario {archivo: hash}."""
    registro = {}
    # Listamos todo lo que hay en la carpeta
    for nombre_archivo in os.listdir(ruta_directorio):
        # Creamos la ruta completa (ej: "mis_docs" + "nota.txt" = "mis_docs/nota.txt")
        ruta_completa = os.path.join(ruta_directorio, nombre_archivo)

        # Solo procesamos si es un archivo (ignoramos subcarpetas por ahora)
        if os.path.isfile(ruta_completa):
            huella = generar_huella(ruta_completa)
            if huella:  # Solo lo añadimos si se pudo leer correctamente
                registro[nombre_archivo] = huella

    return registro