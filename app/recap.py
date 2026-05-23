from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
from app.crud import get_transaction_between


WIB = ZoneInfo("Asia/Jakarta")
UTC = ZoneInfo("UTC")
DEFAULT_CATEGORY = "other"


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

    return _generate_recap(db, start, end, "📅 Rekap Bulan Ini")


def _generate_recap(db, start, end, title):
    transactions = get_transaction_between(db, start, end)

    if not transactions:
        return f"{title}\n\nBelum ada transaksi."

    income_items = [trx for trx in transactions if trx.type == "income"]
    expense_items = [trx for trx in transactions if trx.type == "expense"]

    lines = [title, ""]

    total_income = _append_grouped_section(lines, "🟢 Income", income_items)
    total_expense = _append_grouped_section(lines, "🔴 Expense", expense_items)
    net = total_income - total_expense

    lines.append("────────")
    lines.append(f"Total Income: {format_rupiah(total_income)}")
    lines.append(f"Total Expense: {format_rupiah(total_expense)}")
    lines.append(f"Net: {format_rupiah(net)}")

    return "\n".join(lines)


def _append_grouped_section(lines, title, transactions):
    lines.append(title)

    if not transactions:
        lines.append("Belum ada.")
        lines.append("")
        return 0

    grouped_by_category = defaultdict(list)

    for trx in transactions:
        category = trx.category or DEFAULT_CATEGORY
        if category == "legacy":
            category = DEFAULT_CATEGORY
        grouped_by_category[category].append(trx)

    section_total = 0

    for category, category_items in grouped_by_category.items():
        lines.append(category.capitalize())

        grouped_by_name = defaultdict(list)
        for trx in category_items:
            grouped_by_name[trx.name or "Kita"].append(trx)

        category_total = 0

        for name, name_items in grouped_by_name.items():
            lines.append(f"{name}")

            name_total = 0
            for trx in name_items:
                amount = format_rupiah(trx.amount)
                lines.append(f"• {trx.description} {amount}")
                name_total += trx.amount

            lines.append(f"Subtotal {name}: {format_rupiah(name_total)}")
            category_total += name_total

        lines.append(f"Subtotal {category.capitalize()}: {format_rupiah(category_total)}")
        lines.append("")

        section_total += category_total

    return section_total


def format_rupiah(amount: int):
    return f"{amount:,.0f}".replace(",", ".")
