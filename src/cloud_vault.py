import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import crypto_utils
import index_manager

# Alcance: Solo permite que la app gestione archivos creados por ella misma
SCOPES = ['https://www.googleapis.com/auth/drive.file']

def get_drive_service():
    # Autenticación y creación del servicio de Drive.
    creds = None
    # Rutas relativas para encontrar el JSON desde src/
    base_dir = os.path.dirname(os.path.dirname(__file__))
    cred_path = os.path.join(base_dir, 'config', 'credentials.json')
    token_path = os.path.join(base_dir, 'config', 'token.pickle')

    if os.path.exists(token_path):
        with open(token_path, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(cred_path, SCOPES)
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
        file_metadata = {'name': f"{file_hash}.encrypted"}
        media = MediaFileUpload(temp_filename, mimetype='application/octet-stream')

        file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()
        file_id = file.get('id')

        # 4. Registro en el índice
        index_manager.update_index(file_path, file_id)
        print(f" Subida completada. ID: {file_id}")
        return file_id

    finally:
        # 5. Limpieza
        if os.path.exists(temp_filename):
            try:
                os.remove(temp_filename)
            except PermissionError:
                pass
                print(
                    f"⚠ Nota: No pude borrar el temporal {temp_filename} (bloqueado por el SO), lo borraré en la próxima ejecución.")

def download_and_decrypt(file_id, output_path):
    # Descarga desde Drive, descifra y guarda en local
    service = get_drive_service()
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
    finally:
        # 4. Limpieza
        if os.path.exists(temp_encrypted):
            os.remove(temp_encrypted)
