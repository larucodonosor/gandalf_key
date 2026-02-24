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
    BLACKLIST = [".git", ".idea", "__pycache__", "venv", "estado_base.json", "logs"]
    # Listamos todo lo que hay en la carpeta
    for nombre_archivo in os.listdir(ruta_directorio):
        # Aplicamos filtro para excluir ciertos archivos
        if (nombre_archivo in BLACKLIST) or nombre_archivo.startswith('.'):
            continue  # Salta al siguiente archivo
        # Creamos la ruta completa (ej: "mis_docs" + "nota.txt" = "mis_docs/nota.txt")
        ruta_completa = os.path.join(ruta_directorio, nombre_archivo)

        # Solo procesamos si es un archivo (ignoramos subcarpetas por ahora)
        if os.path.isfile(ruta_completa):
            stats = os.stat(ruta_completa)  # Sacamos los rayos X una sola vez
            ruta_dni = os.path.abspath(ruta_completa)
            huella = generar_huella(ruta_completa)
            if huella: # Solo lo añadimos si se pudo leer correctamente
                # 1. Calculamos el tamaño
                tamano = os.path.getsize(ruta_completa)
                registro[ruta_dni] = {
                    'hash': huella,
                    'tamano': tamano,
                    'modificado': stats.st_mtime #Guardamos la fecha e formato máquina
                }

    return registro

def validar_adn(ruta):
    # Diccionario de firmas conocidas (Magic Numbers)
    FIRMAS = {
        b"\x89PNG": ".png",
        b"\xff\xd8\xff": ".jpg",
        b"%PDF": ".pdf",
        b"MZ": ".exe"
     }

    try:
        nombre_archivo = os.path.basename(ruta)
        extension_declarada = os.path.splitext(nombre_archivo)[1].lower()
        with open(ruta, "rb") as f:
            inicio = f.read(4) # Leemos el encabezado

        # Comprobamos si el inicio coincide con alguna firma
        for firma, ext_real in FIRMAS.items():
            if inicio.startswith(firma):
                if extension_declarada != ext_real:
                    return False, f"¡CAMUFLAJE! ADN de {ext_real} oculto en {extension_declarada}"

        return True, "ADN correcto"
    except Exception as e:
         return True, f"No se pudo analizar:{e}"