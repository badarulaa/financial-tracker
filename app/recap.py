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


def generate_daily_recap(db, owner=None):
    now = datetime.now(WIB)
    start_local = now.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=1)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Hari Ini", owner=owner)


def generate_weekly_recap(db, owner=None):
    now = datetime.now(WIB)
    start_local = now - timedelta(days=now.weekday())
    start_local = start_local.replace(hour=0, minute=0, second=0, microsecond=0)
    end_local = start_local + timedelta(days=7)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Minggu Ini", owner=owner)


def generate_monthly_recap(db, owner=None):
    now = datetime.now(WIB)
    start_local = datetime(now.year, now.month, 1, tzinfo=WIB)

    if now.month == 12:
        end_local = datetime(now.year + 1, 1, 1, tzinfo=WIB)
    else:
        end_local = datetime(now.year, now.month + 1, 1, tzinfo=WIB)

    start = start_local.astimezone(UTC).replace(tzinfo=None)
    end = end_local.astimezone(UTC).replace(tzinfo=None)

    return _generate_recap(db, start, end, "Rekap Bulan Ini", owner=owner)


def _generate_recap(db, start, end, title, owner=None):
    transactions = get_transaction_between(db, start, end)

    if owner:
        transactions = [trx for trx in transactions if normalize_name(trx.name) == normalize_name(owner)]
        title = f"{title} - {format_text(owner)}"

    if not transactions:
        return f"📊 *{title}*\n\nBelum ada transaksi."

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

    _append_grouped_section(lines, "🟢 *Income*", income_items)
    _append_grouped_section(lines, "🔴 *Expense*", expense_items)

    lines.append("━━━━━━━━━━━━")
    lines.append("✅ Selesai")

    return "\n".join(lines)


def _append_grouped_section(lines, title, transactions):
    lines.append(title)

    if not transactions:
        lines.append("_Belum ada._")
        lines.append("")
        return 0

    grouped_by_category = defaultdict(list)

    for trx in transactions:
        category = trx.category or DEFAULT_CATEGORY
        if category == "legacy":
            category = DEFAULT_CATEGORY
        grouped_by_category[category].append(trx)

    section_total = 0

    for category in sorted(grouped_by_category.keys(), key=category_sort_key):
        category_items = grouped_by_category[category]
        category_total = sum(trx.amount for trx in category_items)

        lines.append("")
        lines.append(f"📌 *{format_text(category)}* — {format_rupiah(category_total)}")

        grouped_by_name = defaultdict(list)
        for trx in category_items:
            grouped_by_name[trx.name or "Kita"].append(trx)

        for name in sorted(grouped_by_name.keys()):
            name_items = grouped_by_name[name]
            name_total = sum(trx.amount for trx in name_items)

            lines.append(f"{person_icon(name)} {format_text(name)} · {format_rupiah(name_total)}")

            for trx in name_items:
                amount = format_rupiah(trx.amount)
                lines.append(f"  • {format_text(trx.description)} — {amount}")

        section_total += category_total

    lines.append("")
    lines.append(f"*Subtotal {strip_markdown(title)}*: {format_rupiah(section_total)}")
    lines.append("")

    return section_total


def person_icon(name: str) -> str:
    normalized_name = str(name).strip().lower()

    if normalized_name == "dar":
        return "👨🏻‍🦱"

    if normalized_name == "ai":
        return "🧕🏻"

    return "👤"


def category_sort_key(category: str):
    if category in CATEGORY_ORDER:
        return CATEGORY_ORDER.index(category)

    return len(CATEGORY_ORDER)


def normalize_name(value) -> str:
    return str(value or "").strip().lower()


def strip_markdown(value: str) -> str:
    return value.replace("*", "").replace("🟢", "").replace("🔴", "").strip()


def format_text(value) -> str:
    if value is None:
        return "-"

    return str(value).replace("_", " ").strip().title()


def format_rupiah(amount: int):
    return f"Rp {amount:,.0f}".replace(",", ".")
