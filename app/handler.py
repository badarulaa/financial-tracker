from app.parser import parse_message
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
    )
    return f"✅ Dicatat: {parsed['name']} - {parsed['description']} {parsed['amount']:,.0f}".replace(",", ".")

  if parsed["type"] == "command":
    command = parsed["command"]

    if command == "rekap":
      scope = parsed["scope"]

      if scope == "daily":
        return generate_daily_recap(db)

      if scope == "weekly":
        return generate_weekly_recap(db)

      if scope == "monthly":
        return generate_monthly_recap(db)

    if command == "delete_last":
      deleted = delete_last_transaction(db)
      if deleted:
        return f"🗑️ Transaksi terakhir dihapus: {deleted.name} - {deleted.description} {deleted.amount:,.0f}".replace(",", ".")
      return "Tidak ada transaksi untuk dihapus."

  return "⚠ Perintah tidak dikenali."