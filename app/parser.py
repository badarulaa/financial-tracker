import re
from typing import Dict, Any

def parse_message(text: str) -> Dict[str, Any]:
  text = text.strip()

  if not text:
    return _error("Pesan kosong.")

  lowered = text.lower()

  # ==== COMMAND DETECTION ====
  command_result = _parse_command(lowered)
  if command_result:
    return command_result

  # ==== TRANSACTION DETECTION ====
  return _parse_transaction(lowered)

# ============================
# COMMAND PARSER
# ============================

def _parse_command(text: str):
  if text.startswith("rekap"):
    if "hari ini" in text:
      return {"type": "command", "command": "rekap", "scope": "daily"}
    if "minggu ini" in text:
      return {"type": "command", "command": "rekap", "scope": "weekly"}
    if "bulan ini" in text:
      return {"type": "command", "command": "rekap", "scope": "monthly"}

    return _error("Format rekap tidak dikenali.")

  if text.startswith("hapus terakhir"):
    return {"type": "command", "command": "delete_last"}

  return None