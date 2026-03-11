import os
import datetime
import subprocess
import pickle
import gzip

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.auth.transport.requests import Request

from app.config import settings


SCOPES = ['https://www.googleapis.com/auth/drive.file']
DB_NAME = "financial_db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_PATH = os.path.join(BASE_DIR, "token.pickle")
CREDENTIAL_PATH = os.path.join(BASE_DIR, "credentials.json")


# =============================
# CREATE DATABASE BACKUP
# =============================

def create_backup():

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")

    sql_file = f"backup_{date}.sql"
    gz_file = f"{sql_file}.gz"

    subprocess.run(
        f"pg_dump -U postgres -h localhost {DB_NAME} > {sql_file}",
        shell=True,
        check=True
    )

    with open(sql_file, "rb") as f_in:
        with gzip.open(gz_file, "wb") as f_out:
            f_out.writelines(f_in)

    os.remove(sql_file)

    return gz_file


# =============================
# GOOGLE AUTH
# =============================

def authenticate():

    creds = None

    if os.path.exists(TOKEN_PATH):
        with open(TOKEN_PATH, "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                CREDENTIAL_PATH,
                SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return creds


# =============================
# UPLOAD BACKUP
# =============================

def upload_to_drive(filepath):

    creds = authenticate()

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
        "name": os.path.basename(filepath),
        "parents": [settings.FOLDER_ID]
    }

    media = MediaFileUpload(filepath)

    service.files().create(
        body=file_metadata,
        media_body=media
    ).execute()


# =============================
# DELETE OLD BACKUPS (>7 DAYS)
# =============================

def cleanup_old_backups():

    creds = authenticate()

    service = build("drive", "v3", credentials=creds)

    seven_days_ago = (
        datetime.datetime.utcnow() - datetime.timedelta(days=7)
    ).isoformat() + "Z"

    query = (
        f"'{settings.FOLDER_ID}' in parents "
        f"and createdTime < '{seven_days_ago}'"
    )

    results = service.files().list(
        q=query,
        fields="files(id, name)"
    ).execute()

    files = results.get("files", [])

    for file in files:
        print(f"Deleting old backup: {file['name']}")
        service.files().delete(fileId=file["id"]).execute()


# =============================
# MAIN
# =============================

def main():

    backup_file = create_backup()

    upload_to_drive(backup_file)

    os.remove(backup_file)

    cleanup_old_backups()

    print("Backup uploaded. Old backups cleaned.")


if __name__ == "__main__":
    main()