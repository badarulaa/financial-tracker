from datetime import datetime, timedelta
from collections import defaultdict
from app.crud import get_transaction_between

def generate_daily_recap(db):
  now = datetime.now()
  start = datetime(now.year, now.month, now.day)
  end = start + timedelta(days=1)

  return _generate_recap(db, start, end, "📅 Rekap Hari Ini\n")

def generate_weekly_recap(db):
  now = datetime.now()
  start = now - timedelta(days=now.weekday())
  start = datetime(start.year, start.month, start.day)

  end = start + timedelta(days=7)

  return _generate_recap(db, start, end, "📅 Rekap Minggu Ini\n")

def generate_monthly_recap(db):
  now = datetime.now()

  start = datetime(now.year, now.month, 1)

  if now.month == 12:
    end = datetime(now.year +1, 1, 1)
  else:
    end = datetime(now.year, now.month +1, 1)

  return _generate_recap(db, start, end, "📅 Rekap Bulan Ini\n")

def _generate_recap(db, start, end, title):

  transactions = get_transaction_between(db, start, end)

  if not transactions:
    return f"{title}\n\nTidak ada transaksi."

  grouped = defaultdict(list)

  for trx in transactions:
    grouped[trx.name].append(trx)

  lines = [title]
  lines.append(f"📅 {start.strftime('%d %b')} - {end.strftime('%d %b %Y')}")
  lines.append("")

  grand_total = 0

  for name, items in grouped.items():

    lines.append(f"{name}:")

    subtotal = 0

    for trx in items:
      amount = format_rupiah(trx.amount)
      lines.append(f"- {trx.description} {amount}")
      subtotal += trx.amount

    lines.append(f"Subtotal: {format_rupiah(subtotal)}")
    lines.append("")

    grand_total += subtotal

  lines.append("====================")
  lines.append(f"💰 Total: {format_rupiah(grand_total)}")

  return "\n".join(lines)

def format_rupiah(amount:int):
  return f"{amount:,.0f}".replace(",", ".")