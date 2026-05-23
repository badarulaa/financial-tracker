from app.parser import parse_message, get_category_help
from app.crud import create_transaction, delete_last_transaction
from app.recap import (
    generate_daily_recap,
    generate_weekly_recap,
    generate_monthly_recap,
)


def handle_message(db, text: str) -> str:
    parsed = parse_message(text)

    if parsed["type"] == "error":
        return parsed["message"]

    if parsed["type"] == "transaction":
        create_transaction(
            db,
            parsed["name"],
            parsed["description"],
            parsed["amount"],
            transaction_type=parsed["transaction_type"],
            category=parsed["category"],
        )

        label = "Income" if parsed["transaction_type"] == "income" else "Expense"

        return (
            f"✅ {label} dicatat\n"
            f"Nama: {format_text(parsed['name'])}\n"
            f"Kategori: {format_text(parsed['category'])}\n"
            f"Detail: {format_text(parsed['description'])}\n"
            f"Nominal: {format_rupiah(parsed['amount'])}"
        )

    if parsed["type"] == "command":
        command = parsed["command"]

        if command == "category_help":
            return get_category_help()

        if command == "rekap":
            scope = parsed["scope"]
            owner = parsed.get("owner")

            if scope == "daily":
                return generate_daily_recap(db, owner=owner)

            if scope == "weekly":
                return generate_weekly_recap(db, owner=owner)

            if scope == "monthly":
                return generate_monthly_recap(db, owner=owner)

        if command == "delete_last":
            deleted = delete_last_transaction(db)
            if deleted:
                return (
                    f"🗑️ Transaksi terakhir dihapus:\n"
                    f"{format_text(deleted.name)} - {format_text(deleted.type)} - "
                    f"{format_text(deleted.category)} - {format_text(deleted.description)} "
                    f"{format_rupiah(deleted.amount)}"
                )
            return "Tidak ada transaksi untuk dihapus."

    return "⚠ Perintah tidak dikenali."


def format_text(value) -> str:
    if value is None:
        return "-"

    return str(value).replace("_", " ").strip().title()


def format_rupiah(amount: int) -> str:
    return f"{amount:,.0f}".replace(",", ".")
