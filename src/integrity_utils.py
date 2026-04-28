import hashlib
import os


def get_file_hash(file_path):
    # Calcula el hash SHA256 usando chunks para asegurar la memoria.
    hasher = hashlib.sha256()
    try:
        with open(file_path, 'rb') as f:
            while chunk := f.read(8192):
                hasher.update(chunk)
        return hasher.hexdigest()
    except Exception:
        return None

def obtener_muestra_adn(ruta):
    try:
        tamano = os.path.getsize(ruta)
        if tamano == 0: return "00"
        L = len(os.path.basename(ruta))
        posicion = (L**2 + 7) % tamano
        with open(ruta, "rb") as f:
            f.seek(posicion)
            return f.read(1).hex()
    except:
        return "ff"

def validar_adn(ruta):
    FIRMAS = {b"\x89PNG": ".png", b"\xff\xd8\xff": ".jpg", b"%PDF": ".pdf", b"MZ": ".exe"}
    try:
        nombre_archivo = os.path.basename(ruta)
        ext_declarada = os.path.splitext(nombre_archivo)[1].lower()
        with open(ruta, "rb") as f:
            inicio = f.read(4)
        for firma, ext_real in FIRMAS.items():
            if inicio.startswith(firma):
                if ext_declarada != ext_real:
                    return False, f"¡CAMUFLAJE! ADN de {ext_real} oculto en {ext_declarada}"
        return True, "ADN correcto"
    except Exception as e:
        return True, f"No se pudo analizar: {e}"

def verify_integrity(file_path, original_hash):
    # Retorna True si el archivo está íntegro, False si ha sido alterado o no existe.
    if not os.path.exists(file_path):
        return False  # El archivo ha desaparecido (integridad rota)

    current_hash = get_file_hash(file_path)
    return current_hash == original_hash