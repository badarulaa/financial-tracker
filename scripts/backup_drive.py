import os
import datetime
import subprocess
import gzip

from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload

from app.config import settings


# =============================
# CONFIG
# =============================

DB_NAME = "financial_db"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SERVICE_ACCOUNT_FILE = os.path.join(BASE_DIR, "credentials.json")

SCOPES = ['https://www.googleapis.com/auth/drive']


# =============================
# GOOGLE DRIVE SERVICE
# =============================

def get_drive_service():
    creds = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE,
        scopes=SCOPES
    )
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

    service = get_drive_service()

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