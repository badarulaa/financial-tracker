from datetime import datetime, timedelta
from collections import defaultdict
from app.crud import get_transaction_between

def generate_daily_recap(db):
  now = datetime.now()
  start = datetime(now.year, now.month, now.day)
  end = start + timedelta(days=1)

  return _generate_recap(db, start, end, "📅 Rekap Hari Ini")

def generate_weekly_recap(db):
  now = datetime.now()
  start = now - timedelta(days=now.weekday())
  start = datetime(start.year, start.month, start.day)

  end = start + timedelta(days=7)

  return _generate_recap(db, start, end, "📅 Rekap Minggu Ini")

def generate_monthly_recap(db):
  now = datetime.now()
  start = datetime(now.year, now.month, 1)

  if now.month == 12:
    end = datetime(now.year +1, 1, 1)
  else:
    end = datetime(now.year, now.month +1, 1)

  return _generate_recap(db, start, end, "📅 Rekap Bulan Ini")

def _generate_recap(db, start, end, title):
  transactions = get_transaction_between(db, start, end)

  if not transactions:
    return f"{title}\n\nTidak ada transaksi."

  grouped = defaultdict(list)
  total_all = 0

  for trx in transactions:
    grouped[trx.name].append(trx)
    total_all += trx.amount

  lines = [f"{title}"]

  for name, items in grouped.items():
    subtotal = sum(t.amount for t in items)
    lines.append(f"{name}:")
    for t in items:
      lines.append(f"- {t.description} {format_rupiah(t.amount)}")

  lines.append(f"\nGrand Total: {format_rupiah(total_all)}")

  return "\n".join(lines)

def format_rupiah(amount:int):
  return f"{amount:,.0f}".replace(",", ".")