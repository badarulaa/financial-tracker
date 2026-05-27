from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
from app.crud import get_transaction_between


WIB = ZoneInfo("Asia/Jakarta")
UTC = ZoneInfo("UTC")
DEFAULT_CATEGORY = "other"
CATEGORY_ORDER = [
    "makanan",
    "transportasi",
    "tagihan",
    "belanja",
    "kesehatan",
    "rumah",
    "hiburan",
    "other",
]


def generate_daily_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Hari Ini", owner=owner, view=view)


def generate_yesterday_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    today_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    start_local = today_local - timedelta(days=1)
    end_local = today_local

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Kemarin", owner=owner, view=view)


def generate_weekly_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    start_local = now - timedelta(days=now.weekday())
    start_local = start_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=7)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Minggu Ini", owner=owner, view=view)


def generate_last_week_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    this_week_start = now - timedelta(days=now.weekday())
    this_week_start = this_week_start.replace(hour=0, minute=0, second=0, microsecond=0)
    start_local = this_week_start - timedelta(days=7)
    end_local = this_week_start

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Minggu Lalu", owner=owner, view=view)


def generate_monthly_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    start_local = datetime(now.year, now.month, 1, tzinfo=WIB)

    if now.month == 12:
        end_local = datetime(now.year + 1, 1, 1, tzinfo=WIB)
    else:
        end_local = datetime(now.year, now.month + 1, 1, tzinfo=WIB)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Bulan Ini", owner=owner, view=view)


def generate_last_month_recap(db, owner=None, view="detail"):
    now = datetime.now(WIB)
    this_month_start = datetime(now.year, now.month, 1, tzinfo=WIB)

    if now.month == 1:
        start_local = datetime(now.year - 1, 12, 1, tzinfo=WIB)
    else:
        start_local = datetime(now.year, now.month - 1, 1, tzinfo=WIB)

    end_local = this_month_start

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Bulan Lalu", owner=owner, view=view)


def _generate_recap(db, start, end, title, owner=None, view="detail"):
    transactions = get_transaction_between(db, start, end)

    if owner:
        transactions = [trx for trx in transactions if normalize_name(trx.name) == normalize_name(owner)]

    if not transactions:
        return f"📊 *{title}*\n\nBelum ada transaksi."

    if view == "category":
        return _generate_category_summary(transactions, title)

    if view == "owner":
        return _generate_owner_summary(transactions, title, owner=owner)

    return _generate_detail_recap(transactions, title)


def _generate_detail_recap(transactions, title):
    income_items = [trx for trx in transactions if trx.type == "income"]
    expense_items = [trx for trx in transactions if trx.type == "expense"]

    total_income = sum(trx.amount for trx in income_items)
    total_expense = sum(trx.amount for trx in expense_items)
    net = total_income - total_expense

    lines = [
        f"📊 *{title}*",
        "",
        "💰 *Summary*",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        "━━━━━━━━━━━━",
    ]

    _append_owner_detail_section(lines, transactions)

    lines.append("━━━━━━━━━━━━")
    lines.append("✅ Selesai")

    return "\n".join(lines)


def _generate_category_summary(transactions, title):
    total_income = sum(trx.amount for trx in transactions if trx.type == "income")
    total_expense = sum(trx.amount for trx in transactions if trx.type == "expense")
    net = total_income - total_expense

    grouped = defaultdict(int)

    for trx in transactions:
        if trx.type == "income":
            grouped["income"] += trx.amount
            continue

        category = trx.category or DEFAULT_CATEGORY
        if category == "legacy":
            category = DEFAULT_CATEGORY
        grouped[category] += trx.amount

    lines = [
        f"📊 *{title}*",
        "",
        "💰 *Summary*",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        "━━━━━━━━━━━━",
    ]

    for category in sorted(grouped.keys(), key=category_sort_key):
        lines.append(f"• {format_text(category)} — {format_rupiah(grouped[category])}")

    lines.append("━━━━━━━━━━━━")
    lines.append("✅ Selesai")

    return "\n".join(lines)


def _generate_owner_summary(transactions, title, owner=None):
    total_income = sum(trx.amount for trx in transactions if trx.type == "income")
    total_expense = sum(trx.amount for trx in transactions if trx.type == "expense")
    net = total_income - total_expense

    if owner:
        display_name = format_text(owner)
        display_icon = person_icon(owner)
    else:
        display_name = "Total"
        display_icon = "👥"

    lines = [
        f"📊 *{title}*",
        "",
        f"{display_icon} *{display_name}*",
        "",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        "✅ Selesai",
    ]

    return "\n".join(lines)


def _append_owner_detail_section(lines, transactions):
    grouped_by_name = defaultdict(list)

    for trx in transactions:
        grouped_by_name[trx.name or "Kita"].append(trx)

    for name in sorted(grouped_by_name.keys()):
        name_items = grouped_by_name[name]
        income_total = sum(trx.amount for trx in name_items if trx.type == "income")
        expense_total = sum(trx.amount for trx in name_items if trx.type == "expense")
        net_total = income_total - expense_total

        lines.append(f"{person_icon(name)} *{format_text(name)}* — {format_rupiah(net_total)}")

        for trx in sorted(name_items, key=lambda item: item.created_at, reverse=True):
            amount = format_rupiah(trx.amount)
            sign = "+" if trx.type == "income" else "-"
            lines.append(f"• {format_text(trx.description)} — {sign}{amount}")

        lines.append("")


def person_icon(name: str) -> str:
    normalized_name = str(name).strip().lower()

    if normalized_name == "dar":
        return "👨🏻‍🦱"

    if normalized_name == "ai":
        return "🧕🏻"

    return "👤"


def category_sort_key(category: str):
    if category == "income":
        return -1

    if category in CATEGORY_ORDER:
        return CATEGORY_ORDER.index(category)

    return len(CATEGORY_ORDER)


def normalize_name(value) -> str:
    return str(value or "").strip().lower()


def format_text(value) -> str:
    if value is None:
        return "-"

    return str(value).replace("_", " ").strip().title()


def format_rupiah(amount: int):
    return f"Rp {amount:,.0f}".replace(",", ".")
