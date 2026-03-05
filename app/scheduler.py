from apscheduler.schedulers.background import BackgroundScheduler
from app.database import SessionLocal
from app.recap import generate_daily_recap

scheduler = BackgroundScheduler()

def daily_recap_job():
  db = SessionLocal()

  try:
    recap = generate_daily_recap(db)
    print("\n===== DAILY RECAP =====")
    print(recap)
    print("======================\n")

  finally:
    db.close()

def start_scheduler():
  scheduler.add_job(
    daily_recap_job,
    trigger='cron',
    hour=21,
    minute=0
  )

  scheduler.start()