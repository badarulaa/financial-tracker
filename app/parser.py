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

# =============================
# TRANSACTION PARSER
# =============================

def _parse_transaction(text: str):
  tokens = text.split()

  if len(tokens) < 2 :
    return _error("Format salah. Gunakan: nama keterangan nominal")

  # Nominal selalu token terakhir
  nominal_raw = tokens[-1]

  amount = _parse_amount(nominal_raw)
  if amount is None:
    return _error("Nominal tidak valid.")

  if len(tokens) == 2:
    name = "Kita"
    description =tokens[0]
  else:
    name = tokens[0]
    description = " ".join(tokens[1:-1])

  name = normalize_name(name)

  return {
    "type": "transaction",
    "name": name,
    "description": description,
    "amount": amount,
  }

# ============================
# AMOUNT PARSER
# ============================

def _parse_amount(value: str):
  value = value.lower().replace(".", "")

  try:
    if value.endswith("jt"):
      number = float(value[:-2])
      return int(number * 1_000_000)

    if value.endswith("rb"):
      number = float(value[:-2])
      return int(number * 1_000)

    if value.endswith("k"):
      number = float(value[:-1])
      return int(number * 1_000)

    return int(value)

  except ValueError:
    return None

# ============================
# NAME NORMALIZER
# ============================

def _normalize_name(name: str) -> str:
  return name.lower().capitalize()

# ============================
# ERROR HELPER
# ============================

def _error(message: str):
  return {"type": "error", "message": message}