from typing import Dict, Any

INCOME_ALIASES = {"in", "income", "masuk", "pemasukan"}
EXPENSE_ALIASES = {"out", "expense", "keluar", "pengeluaran"}
TYPE_ALIASES = INCOME_ALIASES | EXPENSE_ALIASES
DEFAULT_CATEGORY = "other"
DEFAULT_NAME = "Kita"

CATEGORY_KEYWORDS = {
    "makanan": [
        "makan",
        "makanan",
        "nasi",
        "ayam",
        "bebek",
        "ikan",
        "daging",
        "sapi",
        "kambing",
        "telur",
        "sosis",
        "bakso",
        "mie",
        "mi ",
        "sate",
        "soto",
        "rawon",
        "rendang",
        "geprek",
        "padang",
        "warteg",
        "martabak",
        "roti",
        "snack",
        "cemilan",
        "jajan",
        "gorengan",
        "burger",
        "pizza",
        "kfc",
        "mcd",
        "mcdonald",
        "hokben",
        "solaria",
        "kopi",
        "coffee",
        "starbucks",
        "janji jiwa",
        "kopken",
        "kenangan",
        "teh",
        "boba",
        "es ",
        "minum",
        "minuman",
        "aqua",
        "galon",
        "gofood",
        "grabfood",
        "shopeefood",
        "resto",
        "restaurant",
        "restoran",
        "cafe",
        "kafe",
    ],
    "transportasi": [
        "grab",
        "gojek",
        "gocar",
        "goride",
        "go ride",
        "go car",
        "maxim",
        "indrive",
        "taxi",
        "taksi",
        "ojek",
        "bensin",
        "bbm",
        "pertalite",
        "pertamax",
        "solar",
        "shell",
        "spbu",
        "parkir",
        "tol",
        "etoll",
        "e-toll",
        "flazz",
        "emoney",
        "e-money",
        "kereta",
        "krl",
        "mrt",
        "lrt",
        "transjakarta",
        "tj",
        "bus",
        "travel",
        "tiket",
        "pesawat",
        "kapal",
        "ferry",
    ],
    "tagihan": [
        "listrik",
        "token",
        "pln",
        "wifi",
        "internet",
        "indihome",
        "biznet",
        "first media",
        "myrepublic",
        "pdam",
        "air",
        "gas",
        "elpiji",
        "lpg",
        "pulsa",
        "paket data",
        "kuota",
        "telkomsel",
        "xl",
        "axis",
        "indosat",
        "tri",
        "smartfren",
        "bpjs",
        "asuransi",
        "pajak",
        "ipl",
        "maintenance",
        "sewa",
        "kontrakan",
        "cicilan",
        "kartu kredit",
        "cc",
    ],
    "belanja": [
        "shopee",
        "tokopedia",
        "tiktok shop",
        "lazada",
        "blibli",
        "bukalapak",
        "zalora",
        "amazon",
        "belanja",
        "checkout",
        "cod",
        "ongkir",
        "indomaret",
        "alfamart",
        "alfamidi",
        "superindo",
        "hypermart",
        "transmart",
        "ranch market",
        "grand lucky",
        "mall",
        "miniso",
        "ace hardware",
        "ikea",
        "mr diy",
        "diy",
        "baju",
        "kaos",
        "kemeja",
        "celana",
        "jaket",
        "sepatu",
        "sendal",
        "sandal",
        "tas",
        "dompet",
        "parfum",
        "skincare",
        "kosmetik",
        "sabun",
        "sampo",
        "shampoo",
        "detergen",
        "tisu",
        "tissue",
        "perabot",
        "alat rumah",
    ],
    "kesehatan": [
        "obat",
        "dokter",
        "klinik",
        "rs",
        "rumah sakit",
        "rawat",
        "kontrol",
        "checkup",
        "medical",
        "vitamin",
        "suplemen",
        "apotik",
        "apotek",
        "farmasi",
        "halodoc",
        "alodokter",
        "dentist",
        "dokter gigi",
        "gigi",
        "kacamata",
        "optik",
        "lab",
        "vaksin",
        "terapi",
        "fisioterapi",
    ],
    "anak": [
        "anak",
        "bayi",
        "baby",
        "susu anak",
        "sufor",
        "diapers",
        "popok",
        "pampers",
        "tisu basah",
        "mainan",
        "toys",
        "sekolah",
        "spp",
        "les",
        "bimbel",
        "daycare",
        "paud",
        "tk",
        "seragam",
        "buku sekolah",
    ],
    "hiburan": [
        "bioskop",
        "cinema",
        "xxi",
        "cgv",
        "movie",
        "film",
        "netflix",
        "spotify",
        "youtube",
        "disney",
        "prime video",
        "viu",
        "wetv",
        "apple music",
        "game",
        "steam",
        "playstation",
        "psn",
        "nintendo",
        "xbox",
        "top up game",
        "konser",
        "event",
        "liburan",
        "hotel",
        "villa",
        "taman",
        "rekreasi",
        "karaoke",
    ],
    "rumah": [
        "rumah",
        "dapur",
        "kamar",
        "kasur",
        "lemari",
        "meja",
        "kursi",
        "lampu",
        "cat",
        "renovasi",
        "service ac",
        "servis ac",
        "ac",
        "pompa",
        "ledeng",
        "tukang",
        "laundry",
        "cuci",
        "galon",
        "aqua galon",
        "gas",
        "tabung",
        "kebersihan",
        "sapu",
        "pel",
    ],
    "sedekah": [
        "sedekah",
        "zakat",
        "infaq",
        "infak",
        "donasi",
        "amal",
        "wakaf",
        "masjid",
        "bantu",
        "sumbangan",
    ],
    "pendidikan": [
        "kursus",
        "course",
        "kelas",
        "bootcamp",
        "training",
        "workshop",
        "seminar",
        "buku",
        "ebook",
        "udemy",
        "skillshare",
        "coursera",
        "sertifikat",
        "sertifikasi",
    ],
    "pekerjaan": [
        "kantor",
        "meeting",
        "client",
        "klien",
        "software",
        "domain",
        "hosting",
        "server",
        "vps",
        "github",
        "canva",
        "figma",
        "notion",
        "openai",
        "chatgpt",
        "tools",
        "saas",
        "iklan",
        "ads",
        "meta ads",
        "google ads",
    ],
    "perawatan": [
        "salon",
        "barber",
        "cukuran",
        "potong rambut",
        "spa",
        "massage",
        "pijat",
        "nail",
        "facial",
        "treatment",
    ],
    "hadiah": [
        "hadiah",
        "gift",
        "kado",
        "birthday",
        "ulang tahun",
        "anniversary",
        "wedding",
        "nikahan",
        "parcel",
        "hampers",
    ],
    "income": [
        "gaji",
        "salary",
        "bonus",
        "thr",
        "freelance",
        "fee",
        "komisi",
        "profit",
        "laba",
        "refund",
        "cashback",
        "dividen",
        "bunga bank",
        "jualan",
        "bayaran",
        "transfer masuk",
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
    category = tokens[1]
    description = " ".join(tokens[2:-1]) or category

    return _transaction_result(trx_type, category, DEFAULT_NAME, description, amount, False)


def _parse_name_first(tokens, amount):
    if len(tokens) < 4:
        return _error("Format baru salah. Gunakan: nama out kategori keterangan nominal")

    name = tokens[0]
    trx_type = _normalize_transaction_type(tokens[1])
    category = tokens[2]
    description = " ".join(tokens[3:-1]) or category

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


def _detect_type_and_category(description: str):
    category = _detect_category(description)

    if category == "income":
        return "income", "income"

    return "expense", category


def _detect_category(description: str) -> str:
    desc = f" {description.lower()} "

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if f" {keyword.lower()} " in desc or keyword.lower() in desc:
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


def _error(message: str):
    return {"type": "error", "message": message}
