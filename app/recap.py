from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
from app.crud import get_transaction_between

WIB = ZoneInfo("Asia/Jakarta")
UTC = ZoneInfo("UTC")

def generate_daily_recap(db):
    now = datetime.now(WIB)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "📊 Rekap Hari Ini")


def generate_weekly_recap(db):
    now = datetime.now(WIB)
    start_local = now - timedelta(days=now.weekday())
    start_local = start_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=7)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "📊 Rekap Minggu Ini")


def generate_monthly_recap(db):

    now = datetime.now(WIB)

    start_local = datetime(now.year, now.month, 1, tzinfo=WIB)

    if now.month == 12:
        end_local = datetime(now.year + 1, 1, 1, tzinfo=WIB)
    else:
        end_local = datetime(now.year, now.month + 1, 1, tzinfo=WIB)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "📅 Rekap Bulan Ini\n")


def _generate_recap(db, start, end, title):

    transactions = get_transaction_between(db, start, end)

    if not transactions:
        return f"{title}\n\nBelum ada transaksi."

    grouped = defaultdict(list)

    for trx in transactions:
        grouped[trx.name].append(trx)

    lines = []
    lines.append(title)
    lines.append("")

    grand_total = 0

    for name, items in grouped.items():

        lines.append(f"{name}")

        subtotal = 0

        for trx in items:
            amount = format_rupiah(trx.amount)
            lines.append(f"• {trx.description} {amount}")
            subtotal += trx.amount

        lines.append(f"Subtotal: {format_rupiah(subtotal)}")
        lines.append("")

        grand_total += subtotal

    lines.append("────────")
    lines.append(f"Total: {format_rupiah(grand_total)}")

    return "\n".join(lines)


def format_rupiah(amount: int):
    return f"{amount:,.0f}".replace(",", ".")