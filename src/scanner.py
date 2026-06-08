import os
import integrity_utils
import unicodedata
import logging

logger = logging.getLogger(__name__)

def map_folder(directory_path):
    # Escanea una carpeta y devuelve un diccionario {archivo: hash}.
    registry = {}

    # Verificación de seguridad para evitar errores en el bucle principal
    if not os.path.exists(directory_path):
        logger.warning(f"El escáner intentó acceder a una ruta inexistente: {directory_path}")
        return None

    try:
        # Recorre carpetas, subcarpetas y archivos
        for root, dirs, files in os.walk(directory_path):
            for file_name in files:
                full_path = str(os.path.join(root, file_name))
                full_path = unicodedata.normalize('NFC', full_path)

                file_hash = integrity_utils.get_file_hash(full_path)
                if file_hash: # Lo añade si se pudo leer correctamente
                    stats = os.stat(full_path)
                    file_id = os.path.abspath(full_path)  # ID única

                    registry[file_id] = {
                        'hash': file_hash,
                        'size': stats.st_size,
                        'modified_at': stats.st_mtime, #Guarda la fecha e formato máquina
                        'dna_sample': integrity_utils.get_dna_sample(full_path), # adn_muestra
                    }
    except Exception as e:
        logger.error(f"Error crítico durante el mapeo de la carpeta {directory_path}: {e}")

    return registry
