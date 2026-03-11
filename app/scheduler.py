from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.recap import generate_daily_recap
from app.whatsapp import send_whatsapp_message
from app.config import settings

scheduler = BackgroundScheduler()

def daily_recap_job():
  db = SessionLocal()

  try:
    recap = generate_daily_recap(db)
    print("\n===== DAILY RECAP =====")
    print(recap)
    print("======================\n")

    send_whatsapp_message(settings.USER_PHONE_OWNER, recap)
    send_whatsapp_message(settings.USER_PHONE_WIFE, recap)

  finally:
    db.close()

def start_scheduler():

    print("Starting scheduler...")

    scheduler.add_job(
        daily_recap_job,
        trigger="cron",
        # hour=21,
        minute=1
    )

    scheduler.start()

    print("Scheduler started")