import os
import datetime
import subprocess
import pickle

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

BACKUP_DIR = os.path.join(BASE_DIR, "tmp")
os.makedirs(BACKUP_DIR, exist_ok=True)


def create_backup():

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"backup_{date}.sql"

    filepath = os.path.join(BACKUP_DIR, filename)

    subprocess.run(
        f"pg_dump -U postgres -h localhost {DB_NAME} > {filepath}",
        shell=True,
        check=True
    )

    return filepath


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
                CREDENTIAL_PATH, SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open(TOKEN_PATH, "wb") as token:
            pickle.dump(creds, token)

    return creds


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


def main():

    backup_file = create_backup()

    upload_to_drive(backup_file)

    os.remove(backup_file)


if __name__ == "__main__":
    main()