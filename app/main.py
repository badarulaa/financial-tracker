from fastapi import FastAPI, Request
from fastapi.responses import PlainTextResponse
from app.database import engine, SessionLocal
from app.models import Base
from app.scheduler import start_scheduler
from app.config import settings
from app.handler import handle_message
from app.whatsapp import send_whatsapp_message

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
  start_scheduler()

@app.get("/")
def root():
  return {"status": "Financial Tracker is Running"}

# ===== WEBHOOK ENDPOINT =====
@app.get("/webhook")
async def verify_webhook(request: Request):

  mode = request.query_params.get("hub.mode")
  token = request.query_params.get("hub.verify_token")
  challenge = request.query_params.get("hub.challenge")

  print("MODE: ", mode)
  print("TOKEN: ", token)
  print("EXPECTED: ", settings.WHATSAPP_VERIFY_TOKEN)
  print("CHALLENGE: ", challenge)

  if mode == "subscribe" and token == settings.WHATSAPP_VERIFY_TOKEN:
    return PlainTextResponse(content=challenge, status_code=200)

  return PlainTextResponse(content="verification failed", status_code=403)

@app.post("/webhook")
async def receive_message(request: Request):

  body = await request.json()

  try:
    entry = body["entry"][0]
    changes = entry["changes"][0]
    value = changes["value"]

    if "messages" not in value:
      return {"status": "ignored"}

    message = value["messages"][0]["text"]["body"]
    sender = value["messages"][0]["from"]

    db = SessionLocal()

    response = handle_message(db, message)

    send_whatsapp_message(sender, response)

    db.close()

  except Exception as e:
    print("Webhook error:", e)

  return {"status": "ok"}