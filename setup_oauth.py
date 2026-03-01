import os
from google_auth_oauthlib.flow import InstalledAppFlow
from googleapiclient.discovery import build

SCOPES = ['https://www.googleapis.com/auth/drive.file']
CLIENT_SECRET_FILE = os.path.expanduser("~/credentials/financial-backup.json")

flow = InstalledAppFlow.from_client_secrest_file(
  CLIENT_SECRET_FILE,
  SCOPES,
  redirect_uri='urn:ietf:wg:oauth:2.0:oob'
)

auth_url, _ = flow.authorization_url(prompt='consent')

print("\nBuka URL ini di browser kamu:\n")
print(auth_url)

code=input("\nPaste authorization code disini:")

flow.fetch_token(code=code)

with open("token.json", "w") as token_file:
    token_file.write(flow.credentials.to_json())
    
print("Oauth setup complete. Token.json saved.")