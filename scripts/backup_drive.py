import os
import datetime
import subprocess

from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from google.oauth2.credentials import Credentials
from google.auth.transport.requests import Request
import pickle
from app.config import Settings


SCOPES = ['https://www.googleapis.com/auth/drive.file']

DB_NAME = "financial_db"

def create_backup():

    date = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M")
    filename = f"backup_{date}.sql"

    subprocess.run(
        f"pg_dump -U postgres -h localhost {DB_NAME} > {filename}",
        shell=True
    )

    return filename


def authenticate():

    creds = None

    if os.path.exists("token.pickle"):
        with open("token.pickle", "rb") as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:

        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())

        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                "credentials.json", SCOPES
            )
            creds = flow.run_local_server(port=0)

        with open("token.pickle", "wb") as token:
            pickle.dump(creds, token)

    return creds


def upload_to_drive(filename):

    creds = authenticate()

    service = build("drive", "v3", credentials=creds)

    file_metadata = {
      "name": filename,
      "parents": [Settings.FOLDER_ID]
    }

    media = MediaFileUpload(filename)

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