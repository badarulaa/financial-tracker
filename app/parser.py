from typing import Dict, Any

INCOME_ALIASES = {"in", "income", "masuk", "pemasukan"}
EXPENSE_ALIASES = {"out", "expense", "keluar", "pengeluaran"}
TYPE_ALIASES = INCOME_ALIASES | EXPENSE_ALIASES
OWNER_ALIASES = {"gw", "gue", "aku", "saya", "dar", "owner"}
WIFE_ALIASES = {"ai", "istri", "bini", "wife"}
DEFAULT_CATEGORY = "other"
DEFAULT_NAME = "Kita"

CATEGORY_KEYWORDS = {
    "income": [
        "gaji", "salary", "bonus", "thr", "freelance", "fee", "komisi",
        "profit", "laba", "refund", "cashback", "dividen", "bunga bank",
        "jualan", "bayaran", "transfer masuk", "masuk"
    ],
    "makanan": [
        "makan", "makanan", "nasi", "ayam", "bebek", "ikan", "daging",
        "telur", "bakso", "mie", "sate", "soto", "geprek", "padang",
        "warteg", "martabak", "roti", "snack", "cemilan", "jajan",
        "gorengan", "burger", "pizza", "kfc", "mcd", "hokben", "solaria",
        "kopi", "coffee", "starbucks", "janji jiwa", "kopken", "kenangan",
        "teh", "boba", "minum", "minuman", "aqua", "galon", "gofood",
        "grabfood", "shopeefood", "resto", "restaurant", "restoran", "cafe", "kafe"
    ],
    "transportasi": [
        "grab", "gojek", "gocar", "goride", "maxim", "indrive", "taxi",
        "taksi", "ojek", "bensin", "bbm", "pertalite", "pertamax", "solar",
        "shell", "spbu", "parkir", "tol", "etoll", "e-toll", "flazz",
        "emoney", "e-money", "kereta", "krl", "mrt", "lrt", "transjakarta",
        "tj", "bus", "travel", "tiket", "pesawat", "kapal", "ferry"
    ],
    "tagihan": [
        "listrik", "token", "pln", "wifi", "internet", "indihome", "biznet",
        "first media", "myrepublic", "pdam", "pulsa", "paket data", "kuota",
        "telkomsel", "xl", "axis", "indosat", "tri", "smartfren", "bpjs",
        "asuransi", "pajak", "ipl", "maintenance", "sewa", "kontrakan",
        "cicilan", "kartu kredit", "cc", "netflix", "spotify", "youtube premium",
        "disney", "prime video", "viu", "wetv"
    ],
    "belanja": [
        "shopee", "tokopedia", "tiktok shop", "lazada", "blibli", "bukalapak",
        "zalora", "amazon", "belanja", "checkout", "cod", "ongkir", "indomaret",
        "alfamart", "alfamidi", "superindo", "hypermart", "transmart", "mall",
        "miniso", "ace hardware", "ikea", "mr diy", "diy", "baju", "kaos",
        "kemeja", "celana", "jaket", "sepatu", "sendal", "sandal", "tas",
        "dompet", "parfum", "skincare", "kosmetik", "sabun", "sampo", "shampoo",
        "detergen", "tisu", "tissue", "perabot", "alat rumah", "mainan", "toys",
        "hadiah", "gift", "kado", "parcel", "hampers"
    ],
    "kesehatan": [
        "obat", "dokter", "klinik", "rs", "rumah sakit", "rawat", "kontrol",
        "checkup", "medical", "vitamin", "suplemen", "apotik", "apotek",
        "farmasi", "halodoc", "alodokter", "dentist", "dokter gigi", "gigi",
        "kacamata", "optik", "lab", "vaksin", "terapi", "fisioterapi"
    ],
    "rumah": [
        "rumah", "dapur", "kamar", "kasur", "lemari", "meja", "kursi",
        "lampu", "cat", "renovasi", "service ac", "servis ac", "ac", "pompa",
        "ledeng", "tukang", "laundry", "cuci", "gas", "elpiji", "lpg", "tabung",
        "kebersihan", "sapu", "pel", "anak", "bayi", "baby", "susu anak", "sufor",
        "diapers", "popok", "pampers", "tisu basah", "sekolah", "spp", "les",
        "bimbel", "daycare", "paud", "tk", "seragam", "buku sekolah", "zakat",
        "sedekah", "infaq", "infak", "donasi", "amal", "masjid", "sumbangan"
    ],
    "hiburan": [
        "bioskop", "cinema", "xxi", "cgv", "movie", "film", "game", "steam",
        "playstation", "psn", "nintendo", "xbox", "top up game", "konser", "event",
        "liburan", "hotel", "villa", "taman", "rekreasi", "karaoke", "salon",
        "barber", "cukuran", "potong rambut", "spa", "massage", "pijat", "facial"
    ],
    "other": [
        "kursus", "course", "kelas", "bootcamp", "training", "workshop", "seminar",
        "buku", "ebook", "udemy", "skillshare", "coursera", "sertifikat",
        "kantor", "meeting", "client", "klien", "software", "domain", "hosting",
        "server", "vps", "github", "canva", "figma", "notion", "openai",
        "chatgpt", "tools", "saas", "iklan", "ads", "meta ads", "google ads"
    ],
}


def parse_message(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return _error("Pesan kosong.")

    lowered = text.lower()
    command_result = _parse_command(lowered)
    if command_result:
        return command_result

    return _parse_transaction(lowered)


def get_category_help() -> str:
    lines = [
        "📚 *Kategori Yang Dipakai*",
        "",
        "Bot tetap nerima input bebas. Keyword akan diarahkan otomatis ke kategori umum ini:",
        "",
    ]

    for category in ["income", "makanan", "transportasi", "tagihan", "belanja", "kesehatan", "rumah", "hiburan", "other"]:
        samples = ", ".join(CATEGORY_KEYWORDS[category][:8])
        lines.append(f"• *{format_text(category)}* — {samples}")

    lines.extend([
        "",
        "Contoh:",
        "nasi padang 20k → Makanan",
        "grab kantor 35k → Transportasi",
        "netflix 65k → Tagihan",
        "diapers 150k → Rumah",
        "domain 180k → Other",
    ])

    return "\n".join(lines)


def _parse_command(text: str):
    if text == "kategori" or text.startswith("kategori "):
        return {"type": "command", "command": "category_help"}

    if text.startswith("rekap"):
        owner = _parse_owner_filter(text)
        view = _parse_recap_view(text, owner)

        if "hari ini" in text:
            return {"type": "command", "command": "rekap", "scope": "daily", "owner": owner, "view": view}
        if "minggu ini" in text:
            return {"type": "command", "command": "rekap", "scope": "weekly", "owner": owner, "view": view}
        if "bulan ini" in text:
            return {"type": "command", "command": "rekap", "scope": "monthly", "owner": owner, "view": view}
        return _error("Format rekap tidak dikenali.")

    if text.startswith("hapus terakhir"):
        return {"type": "command", "command": "delete_last", "owner": _parse_owner_filter(text)}

    return None


def _parse_recap_view(text: str, owner):
    if "kategori" in set(text.split()):
        return "category"

    if owner:
        return "owner"

    return "detail"


def _parse_owner_filter(text: str):
    tokens = set(text.split())

    if tokens & OWNER_ALIASES:
        return "Dar"

    if tokens & WIFE_ALIASES:
        return "Ai"

    return None


def _parse_transaction(text: str):
    tokens = text.split()
    if len(tokens) < 2:
        return _error("Format salah. Gunakan format lama atau format baru.")

    amount = _parse_amount(tokens[-1])
    if amount is None:
        return _error("Nominal tidak valid.")

    first = tokens[0]
    second = tokens[1] if len(tokens) > 1 else ""

    if first in TYPE_ALIASES:
        return _parse_type_first(tokens, amount)

    if second in TYPE_ALIASES:
        return _parse_name_first(tokens, amount)

    return _parse_legacy(tokens, amount)


def _parse_type_first(tokens, amount):
    if len(tokens) < 3:
        return _error("Format baru salah. Gunakan: out kategori keterangan nominal")

    trx_type = _normalize_transaction_type(tokens[0])
    category = _canonical_category(tokens[1], " ".join(tokens[2:-1]))
    description = " ".join(tokens[2:-1]) or tokens[1]

    return _transaction_result(trx_type, category, DEFAULT_NAME, description, amount, False)


def _parse_name_first(tokens, amount):
    if len(tokens) < 4:
        return _error("Format baru salah. Gunakan: nama out kategori keterangan nominal")

    name = tokens[0]
    trx_type = _normalize_transaction_type(tokens[1])
    category = _canonical_category(tokens[2], " ".join(tokens[3:-1]))
    description = " ".join(tokens[3:-1]) or tokens[2]

    return _transaction_result(trx_type, category, name, description, amount, False)


def _parse_legacy(tokens, amount):
    if len(tokens) == 2:
        name = DEFAULT_NAME
        description = tokens[0]
    else:
        name = tokens[0]
        description = " ".join(tokens[1:-1])

    trx_type, category = _detect_type_and_category(description)

    return _transaction_result(trx_type, category, name, description, amount, True)


def _canonical_category(category_hint: str, description: str) -> str:
    text = f"{category_hint} {description}".strip()
    detected = _detect_category(text)
    if detected != DEFAULT_CATEGORY:
        return detected

    return DEFAULT_CATEGORY


def _detect_type_and_category(description: str):
    category = _detect_category(description)

    if category == "income":
        return "income", "income"

    return "expense", category


def _detect_category(description: str) -> str:
    desc = f" {description.lower()} "

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            keyword = keyword.lower().strip()
            if not keyword:
                continue
            if keyword in desc:
                return category

    return DEFAULT_CATEGORY


def _transaction_result(trx_type: str, category: str, name: str, description: str, amount: int, is_legacy: bool):
    return {
        "type": "transaction",
        "transaction_type": trx_type,
        "category": _normalize_category(category),
        "name": _normalize_name(name),
        "description": description,
        "amount": amount,
        "is_legacy": is_legacy,
    }


def _parse_amount(value: str):
    value = value.lower().replace(".", "").replace(",", ".")
    try:
        if value.endswith("jt"):
            return int(float(value[:-2]) * 1_000_000)
        if value.endswith("rb"):
            return int(float(value[:-2]) * 1_000)
        if value.endswith("k"):
            return int(float(value[:-1]) * 1_000)
        return int(float(value))
    except ValueError:
        return None


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


def format_text(value) -> str:
    if value is None:
        return "-"
    return str(value).replace("_", " ").strip().title()


def _error(message: str):
    return {"type": "error", "message": message}
