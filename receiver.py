import os
import hashlib
import hmac
import logging
from flask import Flask, request, jsonify
from dotenv import load_dotenv
from datetime import datetime
import gspread
from google.oauth2.service_account import Credentials

load_dotenv()

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

VERIFY_TOKEN = os.getenv("VERIFY_TOKEN")
APP_SECRET = os.getenv("APP_SECRET")

# ================= GOOGLE SHEETS =================
SCOPES = [
    "https://www.googleapis.com/auth/spreadsheets",
    "https://www.googleapis.com/auth/drive",
]

creds = Credentials.from_service_account_file(
    os.getenv("GOOGLE_CREDENTIALS_PATH"),
    scopes=SCOPES
)
client = gspread.authorize(creds)
sheet = client.open_by_key(os.getenv("GOOGLE_SHEET_ID")).sheet1

processed_messages = set()

# ================= WEBHOOK VERIFICATION =================
@app.get("/webhook")
def verify():
    mode = request.args.get("hub.mode")
    token = request.args.get("hub.verify_token")
    challenge = request.args.get("hub.challenge")

    if mode == "subscribe" and token == VERIFY_TOKEN:
        return challenge, 200
    return "Forbidden", 403


def verify_signature(payload, signature):
    expected = hmac.new(
        APP_SECRET.encode(),
        payload,
        hashlib.sha256
    ).hexdigest()

    return hmac.compare_digest(f"sha256={expected}", signature)


# ================= PARSER =================
def parse_message(text):
    parts = text.strip().split()
    if len(parts) < 3:
        return None

    nama = parts[0]
    ket = " ".join(parts[1:-1])
    nominal_raw = parts[-1].lower()

    nominal_raw = (
        nominal_raw.replace("rp", "")
        .replace(".", "")
        .replace(",", "")
        .strip()
    )

    if nominal_raw.endswith("k"):
        nominal_raw = nominal_raw[:-1]
        if nominal_raw.isdigit():
            return nama, ket, int(nominal_raw) * 1000

    if nominal_raw.isdigit():
        return nama, ket, int(nominal_raw)

    return None


# ================= MESSAGE RECEIVER =================
@app.post("/webhook")
def webhook():
    signature = request.headers.get("X-Hub-Signature-256")
    if not signature or not verify_signature(request.data, signature):
        return "Invalid signature", 403

    data = request.get_json()

    try:
        entry = data["entry"][0]
        change = entry["changes"][0]["value"]
        message = change.get("messages", [])[0]

        message_id = message["id"]

        if message_id in processed_messages:
            return "OK", 200

        processed_messages.add(message_id)

        text = message["text"]["body"].lower()

        parsed = parse_message(text)
        if not parsed:
            return "OK", 200

        nama, ket, nominal = parsed
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        sheet.append_row([timestamp, nama, ket, nominal])

        logging.info(f"Transaksi tercatat: {nama} {nominal}")

    except Exception as e:
        logging.error(str(e))

    return "OK", 200


@app.get("/")
def home():
    return "Official WhatsApp Cloud API Receiver Running", 200


if __name__ == "__main__":
    app.run(
        host="0.0.0.0",
        port=int(os.getenv("PORT", 5000)),
        debug=False
    )