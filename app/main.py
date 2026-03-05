from app.database import engine
from app.models import Base
from fastapi import FastAPI
from app.scheduler import start_scheduler

app = FastAPI()

Base.metadata.create_all(bind=engine)

@app.on_event("startup")
def startup_event():
  start_scheduler()

@app.get("/")
def root():
  return {"status": "Financial Tracker is Running"}