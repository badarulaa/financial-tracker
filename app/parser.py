from typing import Dict, Any


INCOME_ALIASES = {"in", "income", "masuk", "pemasukan"}
EXPENSE_ALIASES = {"out", "expense", "keluar", "pengeluaran"}


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

    if len(tokens) < 2:
        return _error("Format salah. Gunakan format lama atau format baru.")

    amount = _parse_amount(tokens[-1])
    if amount is None:
        return _error("Nominal tidak valid.")

    first_token = tokens[0]

    if first_token in INCOME_ALIASES or first_token in EXPENSE_ALIASES:
        return _parse_new_format(tokens, amount)

    return _parse_legacy_format(tokens, amount)


def _parse_new_format(tokens, amount):
    if len(tokens) < 3:
        return _error("Format baru salah. Gunakan: out kategori keterangan nominal")

    raw_type = tokens[0]
    category = tokens[1]

    if raw_type in INCOME_ALIASES:
        transaction_type = "income"
    elif raw_type in EXPENSE_ALIASES:
        transaction_type = "expense"
    else:
        return _error("Tipe transaksi tidak valid.")

    if len(tokens) == 3:
        description = category
    else:
        description = " ".join(tokens[2:-1])

    return {
        "type": "transaction",
        "transaction_type": transaction_type,
        "category": _normalize_category(category),
        "name": "Kita",
        "description": description,
        "amount": amount,
        "is_legacy": False,
    }


def _parse_legacy_format(tokens, amount):
    if len(tokens) == 2:
        name = "Kita"
        description = tokens[0]
    else:
        name = tokens[0]
        description = " ".join(tokens[1:-1])

    return {
        "type": "transaction",
        "transaction_type": "expense",
        "category": "legacy",
        "name": _normalize_name(name),
        "description": description,
        "amount": amount,
        "is_legacy": True,
    }


# ============================
# AMOUNT PARSER
# ============================


def _parse_amount(value: str):
    value = value.lower().replace(".", "").replace(",", ".")

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

        return int(float(value))

    except ValueError:
        return None


# ============================
# NORMALIZER
# ============================


def _normalize_name(name: str) -> str:
    return name.lower().capitalize()


def _normalize_category(category: str) -> str:
    return category.lower().strip()


# ============================
# ERROR HELPER
# ============================


def _error(message: str):
    return {"type": "error", "message": message}
