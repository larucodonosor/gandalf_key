from cryptography.fernet import Fernet
import os
import sys
import base64
import hashlib
import keyring
import logging

logger=logging.getLogger(__name__)

# Estandariza las rutas tanto para desarrollo como producción
def get_derived_key():
    raw_key = keyring.get_password("Gandalf_Guard", "MASTER_KEY")
    if not raw_key:
        raise ValueError("No se encontró la MASTER_KEY en el llavero seguro.")

    # Ajusta la MASTER_KEY para FERNET: 32 bytes codificados en Base64
    hashed_key = hashlib.sha256(raw_key.encode('utf-8')).digest()
    return base64.urlsafe_b64encode(hashed_key)

def encrypt_file(file_path):
    # Cifra un archivo y devuelve los datos cifrados.
    try:
        key = get_derived_key()
        fernet = Fernet(key)
        with open(file_path, 'rb') as file:
            file_data = file.read()
        return fernet.encrypt(file_data)
    except Exception as e:
        logger.error(f'Error de encriptado en el archivo {file_path}: {e}')
        return None

def decrypt_file(file_path):
    # Descifra datos usando la clave maestra.
    try:
        key = get_derived_key()
        fernet = Fernet(key)
        with open(file_path, 'rb') as f:
            encrypted_data = f.read()
        return fernet.decrypt(encrypted_data)
    except Exception as e:
        logger.error(f'Error de decriptado en el archivo {file_path}: {e}')
        return None