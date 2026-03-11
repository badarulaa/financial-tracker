from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.recap import generate_weekly_recap
from app.whatsapp import send_whatsapp_message
from app.config import settings


scheduler = BackgroundScheduler()


def weekly_recap_job():

    db = SessionLocal()

    try:
        recap = generate_weekly_recap(db)

        print("\n===== WEEKLY RECAP =====")
        print(recap)
        print("========================\n")

        # kirim ke kamu
        send_whatsapp_message(settings.USER_PHONE, recap)

        # kirim ke istri
        send_whatsapp_message(settings.WIFE_PHONE, recap)

    finally:
        db.close()


def start_scheduler():

    scheduler.add_job(
        weekly_recap_job,
        trigger="cron",
        day_of_week="sun",   # setiap Minggu
        hour=21,
        minute=0
    )

    scheduler.start()