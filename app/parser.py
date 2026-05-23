from typing import Dict, Any


INCOME_ALIASES = {"in", "income", "masuk", "pemasukan"}
EXPENSE_ALIASES = {"out", "expense", "keluar", "pengeluaran"}
TRANSACTION_TYPE_ALIASES = INCOME_ALIASES | EXPENSE_ALIASES
DEFAULT_CATEGORY = "other"
DEFAULT_NAME = "Kita"


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
    second_token = tokens[1] if len(tokens) > 1 else ""

    # Format baru tanpa nama: out makan kopi 25rb
    if first_token in TRANSACTION_TYPE_ALIASES:
        return _parse_type_first_format(tokens, amount)

    # Format baru dengan nama tetap di depan: dar out makan kopi 25rb
    if second_token in TRANSACTION_TYPE_ALIASES:
        return _parse_name_first_format(tokens, amount)

    # Format lama: dar geprek 10k / ai ahas 100k
    return _parse_legacy_format(tokens, amount)


def _parse_type_first_format(tokens, amount):
    if len(tokens) < 3:
        return _error("Format baru salah. Gunakan: out kategori keterangan nominal")

    raw_type = tokens[0]
    name = DEFAULT_NAME
    category = tokens[1]
    description_tokens = tokens[2:-1]

    transaction_type = _normalize_transaction_type(raw_type)
    description = " ".join(description_tokens) if description_tokens else category

    return _transaction_result(
        transaction_type=transaction_type,
        category=category,
        name=name,
        description=description,
        amount=amount,
        is_legacy=False,
    )


def _parse_name_first_format(tokens, amount):
    if len(tokens) < 4:
        return _error("Format baru salah. Gunakan: nama out kategori keterangan nominal")

    name = tokens[0]
    raw_type = tokens[1]
    category = tokens[2]
    description_tokens = tokens[3:-1]

    transaction_type = _normalize_transaction_type(raw_type)
    description = " ".join(description_tokens) if description_tokens else category

    return _transaction_result(
        transaction_type=transaction_type,
        category=category,
        name=name,
        description=description,
        amount=amount,
        is_legacy=False,
    )


def _parse_legacy_format(tokens, amount):
    if len(tokens) == 2:
        name = DEFAULT_NAME
        description = tokens[0]
    else:
        name = tokens[0]
        description = " ".join(tokens[1:-1])

    return _transaction_result(
        transaction_type="expense",
        category=DEFAULT_CATEGORY,
        name=name,
        description=description,
        amount=amount,
        is_legacy=True,
    )


def _transaction_result(
    transaction_type: str,
    category: str,
    name: str,
    description: str,
    amount: int,
    is_legacy: bool,
):
    return {
        "type": "transaction",
        "transaction_type": transaction_type,
        "category": _normalize_category(category),
        "name": _normalize_name(name),
        "description": description,
        "amount": amount,
        "is_legacy": is_legacy,
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


def _normalize_transaction_type(value: str) -> str:
    if value in INCOME_ALIASES:
        return "income"

    if value in EXPENSE_ALIASES:
        return "expense"

    return "expense"


def _normalize_name(name: str) -> str:
    return name.lower().capitalize()


def _normalize_category(category: str) -> str:
    return category.lower().strip() or DEFAULT_CATEGORY


# ============================
# ERROR HELPER
# ============================


def _error(message: str):
    return {"type": "error", "message": message}
