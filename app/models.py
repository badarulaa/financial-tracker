from sqlalchemy import Column, Integer, String, Text, DateTime
from datetime import datetime
from app.database import Base

class Transaction(Base):
  __tablename__ = "transactions"

  id = Column(Integer, primary_key=True, index=True)
  name = Column(String(50), nullable=False)
  description = Column(Text, nullable=True)
  amount = Column(Integer, nullable=False)
  created_at = Column(DateTime, default=datetime.utcnow)