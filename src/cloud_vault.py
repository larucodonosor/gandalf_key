import os
import pickle
import keyring
import sys
from google.auth.exceptions import RefreshError
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import crypto_utils
import index_manager
import logging

logger = logging.getLogger(__name__)

# Alcance: Solo permite que la app gestione archivos creados por ella misma
SCOPES = ['https://www.googleapis.com/auth/drive']

def get_secure_token_path():
     # AJUSTE DE RUTA PARA EL EJECUTABLE (.EXE)
    if getattr(sys, 'frozen', False):
        base_dir = os.path.dirname(sys.executable)
    else:
        base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    config_dir = os.path.join(base_dir, 'config')
    os.makedirs(config_dir, exist_ok=True)
    return os.path.join(config_dir, 'token.pickle')

def build_credentials_dict():
    #  Extrae los secretos desde Keyring y monta el diccionario OAuth
    client_id = keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_ID")
    client_secret = keyring.get_password("Gandalf_Guard", "GOOGLE_CLIENT_SECRET")
    if not client_id or not client_secret:
        logger.error("Error: No se encontraron las credenciales de Google OAuth en el Keyring.")
        return None

    return {
        "installed": {
            "client_id": client_id,
            "project_id": "gandalf-guard",
            "auth_uri": "https://accounts.google.com/o/oauth2/auth",
            "token_uri": "https://oauth2.googleapis.com/token",
            "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
            "client_secret": client_secret,
            "redirect_uris": ["http://localhost"]
        }
    }

def get_drive_service():
    # Autenticación y creación del servicio de Drive.
    creds = None
    token_path = get_secure_token_path()

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    try:
        if not creds or not creds.valid:
            if creds and creds.expired and creds.refresh_token:
                creds.refresh(Request())
            else:
                config_dict = build_credentials_dict()
                if not config_dict:
                    return None
                flow = InstalledAppFlow.from_client_config(config_dict, SCOPES)
                creds = flow.run_local_server(port=0)

            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

    except RefreshError as e:
        logger.warning(f"⚠ Token caducado o inválido detectado ({e}). Iniciando borrado automático...")
        # 1. Fuerza la eliminación del archivo pickle caducado
        if os.path.exists(token_path):
            try:
                os.remove(token_path)
            except Exception as delete_error:
                logger.error(f"No se pudo eliminar el archivo token: {delete_error}")

        config_dict = build_credentials_dict()
        if config_dict:
            flow = InstalledAppFlow.from_client_config(config_dict, SCOPES)
            creds = flow.run_local_server(port=0)
            with open(token_path, 'wb') as token:
                pickle.dump(creds, token)

    return build('drive', 'v3', credentials=creds)

def upload_to_drive(file_path, file_hash):
    # 1. Cifra el contenido antes de subirlo
    encrypted_data = crypto_utils.encrypt_file(file_path)

    # 2. Crea un archivo temporal con los datos cifrados
    temp_filename = f"{file_hash}.tmp"
    with open(temp_filename, 'wb') as f:
        f.write(encrypted_data)
        f.flush()  # Fuerza el volcado al disco
        os.fsync(f.fileno())  # Fuerza la sincronización con el disco físico
    # Al salir de este bloque 'with', el archivo ya está cerrado

    # 3. Sube el archivo cifrado a Google Drive.
    try:
        service = get_drive_service()
        if not service:
            logger.error("No se pudo subir a Drive: Servicio no disponible.")
            return None
        file_metadata = {'name': f"{file_hash}.encrypted"}
        media = MediaFileUpload(temp_filename, mimetype='application/octet-stream')

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        # 4. Registro en el índice
        index_manager.update_index(file_path, file_id)
        logger.info(f" Subida completada. ID: {file_id}")
        return file_id

    except Exception as e:
        logger.error(f"Fallo crítico en el proceso de subida a Drive: {e}")
        return None

    finally:
        # 5. Limpieza
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except PermissionError:
                pass
                logger.warning(f"⚠ Nota: No pude borrar el temporal {temp_filename} (bloqueado por el SO), lo borraré en la próxima ejecución.")

def download_and_decrypt(file_id, output_path):
    # Descarga desde Drive, descifra y guarda en local
    service = get_drive_service()
    if not service:
        logger.error("No se puede descargar: Servicio Google Drive no inicializado.")
        return False
    temp_encrypted = "temp_download.encrypted"

    try:
        # 1. Descarga
        request = service.files().get_media(fileId=file_id)
        file_content = request.execute()

        with open(temp_encrypted, 'wb') as f:
            f.write(file_content)

        # 2. Descifra
        decrypted_data = crypto_utils.decrypt_file(temp_encrypted)
        # 3. Guardado final
        with open(output_path, 'wb') as f:
            f.write(decrypted_data)

    except Exception as e:
        logger.error(f"Error al descargar o descifrar el archivo {file_id}: {e}")
        return False

    finally:
        # 4. Limpieza
        if os.path.exists(temp_encrypted):
            os.remove(temp_encrypted)
