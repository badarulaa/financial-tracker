import os
import subprocess
from datetime import datetime
from google.oauth2.credentials import Credentials
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

# ================= CONFIG =================
DB_NAME = "finance_db"
DB_USER = "finance_user"
DB_HOST = "127.0.0.1"
FOLDER_ID = "1WGFkuNKAdJOSKMgTxbhMRAP1UD_e43ps"
SCOPES = ['https://www.googleapis.com/auth/drive.file']
# ==========================================

def create_backup():
    date_str = datetime.now().strftime("%Y-%m-%d")
    file_name = f"finance_backup_{date_str}.sql"

    command = [
        "pg_dump",
        "-h", DB_HOST,
        "-U", DB_USER,
        DB_NAME,
        "-f", file_name
    ]

    env = os.environ.copy()
    env["PGPASSWORD"] = os.getenv("DB_PASSWORD")

    subprocess.run(command, env=env, check=True)
    return file_name

def upload_to_drive(file_name):
    creds = Credentials.from_authorized_user_file('token.json', SCOPES)
    service = build('drive', 'v3', credentials=creds)

    file_metadata = {
        'name': file_name,
        'parents': [FOLDER_ID]
    }

    media = MediaFileUpload(file_name, resumable=True)

    file = service.files().create(
        body=file_metadata,
        media_body=media,
        fields='id'
    ).execute()

    print("Upload berhasil. File ID:", file.get('id'))

    cleanup_old_backups(service)

def cleanup_old_backups(service):
    query = f"'{FOLDER_ID}' in parents and name contains 'finance_backup_'"
    results = service.files().list(
        q=query,
        fields="files(id, name, createdTime)",
        orderBy="createdTime asc"
    ).execute()

    files = results.get('files', [])

    if len(files) <= 30:
        return

    for file in files [:-30]:
        service.files().delete(fileId=file['id']).execute()
        print("Deleted old backup:", file['name'])

def main():
    file_name = create_backup()
    upload_to_drive(file_name)
    os.remove(file_name)
    print("Backup selesai dan file lokal dihapus.")

if __name__ == "__main__":
    main()