import os
import datetime
import subprocess
import gzip
import json

from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.config import settings


# =============================
# CONFIG
# =============================

DB_NAME = "financial_db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TOKEN_FILE = "/root/.hermes/google_token.json"

SCOPES = ['https://www.googleapis.com/auth/drive']


# =============================
# GOOGLE DRIVE SERVICE (OAuth2)
# =============================

def get_drive_service():
    creds = Credentials.from_authorized_user_file(TOKEN_FILE, SCOPES)

    if creds and creds.expired and creds.refresh_token:
        creds.refresh(Request())
        # Save refreshed token
        with open(TOKEN_FILE, 'w') as f:
            f.write(creds.to_json())

    return build("drive", "v3", credentials=creds)


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
# UPLOAD BACKUP
# =============================

def upload_to_drive(filepath):

    print("DEBUG FOLDER_ID:", settings.FOLDER_ID)

    service = get_drive_service()

    file_metadata = {
        "name": os.path.basename(filepath),
        "parents": [settings.FOLDER_ID]
    }

    media = MediaFileUpload(filepath, resumable=True)

    service.files().create(
        body=file_metadata,
        media_body=media,
        fields="id"
    ).execute()


# =============================
# DELETE OLD BACKUPS (>7 DAYS)
# =============================

def cleanup_old_backups():

    service = get_drive_service()

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

    print("Starting backup...")

    backup_file = create_backup()
    print(f"Backup created: {backup_file}")

    upload_to_drive(backup_file)
    print("Uploaded to Google Drive")

    os.remove(backup_file)
    print("Local file removed")

    cleanup_old_backups()
    print("Old backups cleaned")

    print("Backup process completed ✅")

if __name__ == "__main__":
    main()
