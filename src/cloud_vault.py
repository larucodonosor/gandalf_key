import os
import pickle
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import crypto_utils

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
    print(f"🔒 Cifrando archivo: {file_path}...")
    encrypted_data = crypto_utils.encrypt_file(file_path)

    # 2. Crea un archivo temporal con los datos cifrados
    temp_filename = f"{file_hash}.tmp"
    with open(temp_filename, 'wb') as f:
        f.write(encrypted_data)

    # 3. Sube el archivo cifrado a Google Drive.
    service = get_drive_service()
    file_metadata = {'name': f"{file_hash}.encrypted"}  # Usa el hash como nombre
    media = MediaFileUpload(file_path, mimetype='application/octet-stream')

    print(f" Subiendo {file_path} a la nube...")
    file = service.files().create(body=file_metadata, media_body=media, fields='id').execute()

    # 4. Borra el archivo temporal
    if os.path.exists(temp_filename):
        os.remove(temp_filename)

    print(f" Subida completada. ID del archivo en nube: {file.get('id')}")
    return file.get('id')