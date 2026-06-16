import os
import json
from cryptography.fernet import Fernet
import cloud_vault
import crypto_utils
import config_manager
import index_manager
import logging

logger = logging.getLogger(__name__)

def decrypt_and_save(encrypted_bytes, target_path):
    # Desencripta los bytes usando la MASTER_KEY y los guarda en el disco.
    # 1. Recupera la clave del llavero del sistema
    try:
        key = crypto_utils.get_derived_key()
        fernet = Fernet(key)

        # Desencripta los bytes en memoria
        decrypted_data = fernet.decrypt(encrypted_bytes)

        # Si el usuario borró la carpeta por completo, la recrea antes de escribir el archivo
        os.makedirs(os.path.dirname(target_path), exist_ok=True)

        with open(target_path, 'wb') as f:
            f.write(decrypted_data)

        logger.info(f"Archivo resucitado con éxito en: {target_path}")
        return True
    except Exception as e:
        logger.error(f"Error al descifrar y guardar el archivo en {target_path}: {e}")
        return False

def restore_single_file(file_path):
    # Descarga y restaura un único archivo específico.
    logger.info(f" Iniciando recuperación de archivo individual: {file_path}")

    index_path = index_manager.get_index_file_path()
    if not os.path.exists(index_path):
        raise FileNotFoundError("No se encuentra el índice local para rastrear el archivo en la nube.")

    with open(index_path, 'r') as f:
        index = json.load(f)

    if file_path not in index:
        raise ValueError(f"El archivo {file_path} no está registrado en el índice del búnker.")

    file_id_cloud = index[file_path].get("drive_id")

    # Descargar bytes cifrados desde Google Drive
    encrypted_bytes = cloud_vault.download_file(file_id_cloud)
    if not encrypted_bytes:
        raise RuntimeError("Fallo al descargar el archivo desde Google Drive.")
    # Desencriptar y guardar en su ruta original
    return decrypt_and_save(encrypted_bytes, file_path)

def restore_full_backup():
    # Restaura todos los archivos registrados en el índice.
    logger.info("INICIANDO RECUPERACIÓN COMPLETA DEL BÚNKER")

    index_path = config_manager.get_secure_config_path("index.json")
    if not os.path.exists(index_path):
        raise FileNotFoundError("Índice no encontrado. No se puede realizar la restauración completa.")

    with open(index_path, 'r') as f:
        index = json.load(f)

    success_count = 0
    total_files = len(index)

    for file_path, info in index.items():
        try:
            file_id_cloud = info.get("drive_id")
            if not file_id_cloud:
                continue
            encrypted_bytes = cloud_vault.download_file(file_id_cloud)
            if encrypted_bytes and decrypt_and_save(encrypted_bytes, file_path):
                success_count += 1
        except Exception as e:
            logger.error(f"❌ Error restaurando {file_path}: {e}")

    logger.info(f"📥 Restauración completada. {success_count}/{len(index)} archivos recuperados.")
    return success_count