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

def get_dna_sample(file_path):
    try:
        file_size = os.path.getsize(file_path)
        if file_size == 0: return "00"
        L = len(os.path.basename(file_path))
        position = (L**2 + 7) % file_size
        with open(file_path, "rb") as f:
            f.seek(position)
            return f.read(1).hex()
    except Exception:
        return "ff"

def validate_dna(file_path):
    SIGNATURES = {b"\x89PNG": ".png", b"\xff\xd8\xff": ".jpg", b"%PDF": ".pdf", b"MZ": ".exe"}
    try:
        file_name = os.path.basename(file_path)
        declared_ext = os.path.splitext(file_name)[1].lower()
        with open(file_path, "rb") as f:
            header = f.read(4)
        for sign, real_ext in SIGNATURES.items():
            if header.startswith(sign):
                if declared_ext != real_ext:
                    return False, f"¡CAMUFLAJE! ADN de {real_ext} oculto en {declared_ext}"
        return True, "ADN correcto"
    except Exception as e:
        return True, f"No se pudo analizar: {e}"

def verify_integrity(file_path, original_hash):
    # Retorna True si el archivo está íntegro, False si ha sido alterado o no existe.
    if not os.path.exists(file_path):
        return False  # El archivo ha desaparecido (integridad rota)

    current_hash = get_file_hash(file_path)
    return current_hash == original_hash