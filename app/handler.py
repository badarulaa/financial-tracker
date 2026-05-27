from app.parser import parse_message, get_category_help
from app.crud import create_transaction, delete_last_transaction
from app.recap import (
    generate_daily_recap,
    generate_yesterday_recap,
    generate_weekly_recap,
    generate_last_week_recap,
    generate_monthly_recap,
    generate_last_month_recap,
    generate_current_period_balance,
)


HELP_COMMANDS = {"help", "bantuan", "command", "commands", "cara pakai"}


def handle_message(db, text: str) -> str:
    if is_help_command(text):
        return get_help_text()

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
        balance = generate_current_period_balance(db)

        return (
            f"✅ {label} dicatat\n"
            f"Nama: {format_text(parsed['name'])}\n"
            f"Kategori: {format_text(parsed['category'])}\n"
            f"Detail: {format_text(parsed['description'])}\n"
            f"Nominal: {format_rupiah(parsed['amount'])}\n"
            f"\n{balance}"
        )

    if parsed["type"] == "command":
        command = parsed["command"]

        if command == "category_help":
            return get_category_help()

        if command == "balance":
            return generate_current_period_balance(db)

        if command == "rekap":
            scope = parsed["scope"]
            owner = parsed.get("owner")
            view = parsed.get("view", "detail")

            if scope == "daily":
                return generate_daily_recap(db, owner=owner, view=view)

            if scope == "yesterday":
                return generate_yesterday_recap(db, owner=owner, view=view)

            if scope == "weekly":
                return generate_weekly_recap(db, owner=owner, view=view)

            if scope == "last_week":
                return generate_last_week_recap(db, owner=owner, view=view)

            if scope == "monthly":
                return generate_monthly_recap(db, owner=owner, view=view)

            if scope == "last_month":
                return generate_last_month_recap(db, owner=owner, view=view)

        if command == "delete_last":
            owner = parsed.get("owner")
            deleted = delete_last_transaction(db, name=owner)
            if deleted:
                owner_label = f" milik {format_text(owner)}" if owner else ""
                return (
                    f"🗑️ Transaksi terakhir{owner_label} dihapus:\n"
                    f"{format_text(deleted.name)} - {format_text(deleted.type)} - "
                    f"{format_text(deleted.category)} - {format_text(deleted.description)} "
                    f"{format_rupiah(deleted.amount)}"
                )
            if owner:
                return f"Tidak ada transaksi terakhir milik {format_text(owner)} untuk dihapus."
            return "Tidak ada transaksi untuk dihapus."

    return "⚠ Perintah tidak dikenali."


def is_help_command(text: str) -> bool:
    return text.strip().lower() in HELP_COMMANDS


def get_help_text() -> str:
    return "\n".join([
        "📖 *Help Financial Tracker*",
        "",
        "*Catat Pengeluaran*",
        "Tulis detail + nominal. Nama Dar/Ai otomatis dari nomor WhatsApp.",
        "• makan lawson 22k",
        "• nasi padang 25rb",
        "• grab kantor 35k",
        "• listrik rumah 200k",
        "• obat batuk 30k",
        "• shopee kaos 100k",
        "",
        "*Catat Pemasukan*",
        "• gaji kantor 10jt",
        "• bonus kantor 500k",
        "• freelance website 2jt",
        "• in gaji kantor 10jt",
        "",
        "*Saldo Periode*",
        "• saldo",
        "• saldo bulan ini",
        "• saldo periode ini",
        "",
        "*Rekap Detail Lengkap*",
        "• rekap hari ini",
        "• rekap kemarin",
        "• rekap minggu ini",
        "• rekap minggu lalu",
        "• rekap bulan ini",
        "• rekap bulan lalu",
        "",
        "*Rekap Kategori*",
        "• rekap kategori hari ini",
        "• rekap kategori kemarin",
        "• rekap kategori minggu ini",
        "• rekap kategori minggu lalu",
        "• rekap kategori bulan ini",
        "• rekap kategori bulan lalu",
        "",
        "*Rekap Per Orang*",
        "• rekap gw hari ini",
        "• rekap dar minggu lalu",
        "• rekap istri kemarin",
        "• rekap ai bulan lalu",
        "",
        "*Kategori & Hapus*",
        "• kategori",
        "• hapus terakhir",
        "• hapus terakhir gw",
        "• hapus terakhir istri",
        "",
        "*Format Nominal*",
        "Bisa pakai: 10k, 25rb, 2.5jt, atau 25000.",
        "",
        "*Catatan Periode Bulanan*",
        "Rekap bulan ini pakai periode finansial tanggal 26 - 25, bukan kalender 1 - 31.",
    ])


def format_text(value) -> str:
    if value is None:
        return "-"

    return str(value).replace("_", " ").strip().title()


def format_rupiah(amount: int) -> str:
    return f"{amount:,.0f}".replace(",", ".")
