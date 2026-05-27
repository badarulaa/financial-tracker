from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from collections import defaultdict
from app.crud import get_transaction_between


WIB = ZoneInfo("Asia/Jakarta")
UTC = ZoneInfo("UTC")
DEFAULT_CATEGORY = "other"
FINANCIAL_CUTOFF_DAY = 26
DETAIL_TRANSACTION_LIMIT = 10
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
    start_local, end_local = get_current_financial_period()

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)
    subtitle = format_period(start_local, end_local)

    return _generate_recap(db, start, end, "Rekap Bulan Ini", owner=owner, view=view, subtitle=subtitle)


def generate_last_month_recap(db, owner=None, view="detail"):
    current_start, _ = get_current_financial_period()
    start_local = add_months(current_start, -1)
    end_local = current_start

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)
    subtitle = format_period(start_local, end_local)

    return _generate_recap(db, start, end, "Rekap Bulan Lalu", owner=owner, view=view, subtitle=subtitle)


def generate_current_period_balance(db):
    start_local, end_local = get_current_financial_period()
    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    transactions = get_transaction_between(db, start, end)
    total_income = sum(trx.amount for trx in transactions if trx.type == "income")
    total_expense = sum(trx.amount for trx in transactions if trx.type == "expense")
    remaining = total_income - total_expense

    return "\n".join([
        "💰 *Periode Ini*",
        format_period(start_local, end_local),
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Sisa    : {format_rupiah(remaining)}",
    ])


def _generate_recap(db, start, end, title, owner=None, view="detail", subtitle=None):
    transactions = get_transaction_between(db, start, end)

    if owner:
        transactions = [trx for trx in transactions if normalize_name(trx.name) == normalize_name(owner)]

    if not transactions:
        lines = [f"📊 *{title}*"]
        if subtitle:
            lines.extend([subtitle])
        lines.extend(["", "Belum ada transaksi."])
        return "\n".join(lines)

    if view == "category":
        return _generate_category_summary(transactions, title, subtitle=subtitle)

    if view == "owner":
        return _generate_owner_summary(transactions, title, owner=owner, subtitle=subtitle)

    return _generate_detail_recap(transactions, title, subtitle=subtitle)


def _generate_detail_recap(transactions, title, subtitle=None):
    income_items = [trx for trx in transactions if trx.type == "income"]
    expense_items = [trx for trx in transactions if trx.type == "expense"]

    total_income = sum(trx.amount for trx in income_items)
    total_expense = sum(trx.amount for trx in expense_items)
    net = total_income - total_expense

    lines = [f"📊 *{title}*"]
    if subtitle:
        lines.append(subtitle)

    lines.extend([
        "",
        "💰 *Summary*",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        f"🧾 *10 Transaksi Terakhir Per Orang*",
        "━━━━━━━━━━━━",
    ])

    _append_owner_detail_section(lines, transactions)

    lines.append("━━━━━━━━━━━━")
    lines.append("✅ Selesai")

    return "\n".join(lines)


def _generate_category_summary(transactions, title, subtitle=None):
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

    lines = [f"📊 *{title}*"]
    if subtitle:
        lines.append(subtitle)

    lines.extend([
        "",
        "💰 *Summary*",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        "━━━━━━━━━━━━",
    ])

    for category in sorted(grouped.keys(), key=category_sort_key):
        lines.append(f"• {format_text(category)} — {format_rupiah(grouped[category])}")

    lines.append("━━━━━━━━━━━━")
    lines.append("✅ Selesai")

    return "\n".join(lines)


def _generate_owner_summary(transactions, title, owner=None, subtitle=None):
    total_income = sum(trx.amount for trx in transactions if trx.type == "income")
    total_expense = sum(trx.amount for trx in transactions if trx.type == "expense")
    net = total_income - total_expense

    if owner:
        display_name = format_text(owner)
        display_icon = person_icon(owner)
    else:
        display_name = "Total"
        display_icon = "👥"

    lines = [f"📊 *{title}*"]
    if subtitle:
        lines.append(subtitle)

    lines.extend([
        "",
        f"{display_icon} *{display_name}*",
        "",
        f"Income  : {format_rupiah(total_income)}",
        f"Expense : {format_rupiah(total_expense)}",
        f"Net     : {format_rupiah(net)}",
        "",
        "✅ Selesai",
    ])

    return "\n".join(lines)


def _append_owner_detail_section(lines, transactions):
    grouped_by_name = defaultdict(list)

    for trx in transactions:
        grouped_by_name[trx.name or "Kita"].append(trx)

    for name in sorted(grouped_by_name.keys()):
        all_name_items = sorted(grouped_by_name[name], key=lambda item: item.created_at, reverse=True)
        shown_items = all_name_items[:DETAIL_TRANSACTION_LIMIT]
        hidden_count = max(len(all_name_items) - DETAIL_TRANSACTION_LIMIT, 0)

        income_total = sum(trx.amount for trx in all_name_items if trx.type == "income")
        expense_total = sum(trx.amount for trx in all_name_items if trx.type == "expense")
        net_total = income_total - expense_total

        lines.append(f"{person_icon(name)} *{format_text(name)}* — {format_rupiah(net_total)}")

        for trx in shown_items:
            amount = format_rupiah(trx.amount)
            sign = "+" if trx.type == "income" else "-"
            lines.append(f"• {format_text(trx.description)} — {sign}{amount}")

        if hidden_count:
            lines.append(f"...dan {hidden_count} transaksi {format_text(name)} lainnya")

        lines.append("")


def get_current_financial_period():
    now = datetime.now(WIB)

    if now.day >= FINANCIAL_CUTOFF_DAY:
        start_local = datetime(now.year, now.month, FINANCIAL_CUTOFF_DAY, tzinfo=WIB)
        end_local = add_months(start_local, 1)
    else:
        end_local = datetime(now.year, now.month, FINANCIAL_CUTOFF_DAY, tzinfo=WIB)
        start_local = add_months(end_local, -1)

    return start_local, end_local


def add_months(value: datetime, months: int) -> datetime:
    month = value.month - 1 + months
    year = value.year + month // 12
    month = month % 12 + 1
    return datetime(year, month, value.day, tzinfo=value.tzinfo)


def format_period(start_local: datetime, end_local: datetime):
    display_end = end_local - timedelta(days=1)
    return f"_Periode: {format_date(start_local)} - {format_date(display_end)}_"


def format_date(value: datetime):
    month_names = [
        "Jan", "Feb", "Mar", "Apr", "Mei", "Jun",
        "Jul", "Agu", "Sep", "Okt", "Nov", "Des",
    ]
    return f"{value.day} {month_names[value.month - 1]}"


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
