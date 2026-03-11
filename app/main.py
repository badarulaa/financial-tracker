from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse

from app.database import engine, SessionLocal
from app.models import Base
from app.scheduler import start_scheduler
from app.config import settings
from app.handler import handle_message
from app.whatsapp import send_whatsapp_message


app = FastAPI()

# Create table jika belum ada
Base.metadata.create_all(bind=engine)


# ===== STARTUP =====
@app.on_event("startup")
def startup_event():
    start_scheduler()


# ===== ROOT ENDPOINT =====
@app.get("/")
def root():
    return {"status": "Financial Tracker is Running"}


# ===== WEBHOOK VERIFICATION =====
@app.get("/webhook")
async def verify_webhook(request: Request):

    mode = request.query_params.get("hub.mode")
    token = request.query_params.get("hub.verify_token")
    challenge = request.query_params.get("hub.challenge")

    print("MODE:", mode)
    print("TOKEN:", token)
    print("EXPECTED:", settings.WHATSAPP_VERIFY_TOKEN)
    print("CHALLENGE:", challenge)

    if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
        return PlainTextResponse(content=challenge)

    return {"status": "webhook endpoint ready"}


# ===== RECEIVE MESSAGE =====
@app.post("/webhook")
async def receive_message(request: Request):

    body = await request.json()

    entry = body["entry"][0]
    changes = entry["changes"][0]
    value = changes["value"]

    # ignore status update
    if "messages" not in value:
        return {"status": "ignored"}

    message = value["messages"][0]["text"]["body"]
    sender = value["messages"][0]["from"]

    print("Incoming message:", message)
    print("Sender:", sender)

    db = SessionLocal()

    response = handle_message(db, message)

    send_whatsapp_message(sender, response)

    db.close()

    return {"status": "ok"}