from sqlalchemy.orm import Session
from datetime import datetime, date
from app.models import Transaction

def create_transaction(db: Session, name: str, description: str, amount: int):
  transaction = Transaction(
    name=name,
    description=description,
    amount=amount,
  )
  db.add(transaction)
  db.commit()
  db.refresh(transaction)
  return transaction

def get_today_transactions(db: Session):
  today = date.today()

  return db.query(Transaction).filter(
    Transaction.created_at >= datetime.combine(today, datetime.min.time())
  ).all()

def delete_last_transaction(db: Session):
  last = db.query(Transaction).order_by(Transaction.created_at.desc()).first()

  if last:
    db.delete(last)
    db.commit()
    return last

  return None

def get_transaction_between(db, start: datetime, end: datetime):
  return (
    db.query(Transaction)
    .filter(Transaction.created_at >= start)
    .filter(Transaction.created_at <= end)
    .order_by(Transaction.created_at.asc())
    .all()
  )