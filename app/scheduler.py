from apscheduler.schedulers.background import BackgroundScheduler
from datetime import datetime
from app.database import SessionLocal
from app.recap import generate_daily_recap

scheduler = BackgroundScheduler()

def daily_recap_job():

    print("Scheduler triggered at:", datetime.now())

    db = SessionLocal()

    try:
        recap = generate_daily_recap(db)

        print("\n===== DAILY RECAP =====")
        print(recap)
        print("======================\n")

    finally:
        db.close()


def start_scheduler():

    print("Starting scheduler...")

    scheduler.add_job(
        daily_recap_job,
        trigger="interval",   # sementara kita ubah dulu
        seconds=30
    )

    print("Jobs:", scheduler.get_jobs())

    scheduler.start()

    print("Scheduler started")