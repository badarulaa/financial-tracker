from app.database import SessionLocal
from app.models import Transaction


<<<<<<< HEAD
=======
DEFAULT_CATEGORY = "other"

>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f
CATEGORY_KEYWORDS = {
    "makan": [
        "makan",
        "nasi",
        "ayam",
        "kopi",
        "gofood",
        "grabfood",
        "resto",
        "bakso",
        "mie",
        "sate",
    ],
    "transport": [
        "grab",
        "gojek",
        "bensin",
        "tol",
        "parkir",
        "ojek",
    ],
    "tagihan": [
        "listrik",
        "wifi",
        "internet",
        "pdam",
        "air",
        "pulsa",
        "token",
    ],
    "belanja": [
        "shopee",
        "tokopedia",
        "indomaret",
        "alfamart",
        "belanja",
        "mall",
    ],
    "kesehatan": [
        "obat",
        "dokter",
        "klinik",
        "rs",
        "rumah sakit",
    ],
}


INCOME_KEYWORDS = [
    "gaji",
    "salary",
    "bonus",
    "freelance",
    "refund",
    "income",
    "masuk",
]


def detect_type(description: str) -> str:
    desc = description.lower()

    for keyword in INCOME_KEYWORDS:
        if keyword in desc:
            return "income"

    return "expense"


def detect_category(description: str, transaction_type: str) -> str:
    desc = description.lower()

    if transaction_type == "income":
        if "gaji" in desc or "salary" in desc:
            return "gaji"
        if "freelance" in desc:
            return "freelance"
        if "bonus" in desc:
            return "bonus"
        if "refund" in desc:
            return "refund"
<<<<<<< HEAD
        return "lainnya"
=======
        return DEFAULT_CATEGORY
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f

    for category, keywords in CATEGORY_KEYWORDS.items():
        for keyword in keywords:
            if keyword in desc:
                return category

<<<<<<< HEAD
    return "legacy"
=======
    return DEFAULT_CATEGORY
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f


def main():
    db = SessionLocal()

    try:
        transactions = (
            db.query(Transaction)
<<<<<<< HEAD
            .filter(Transaction.category == "legacy")
=======
            .filter(Transaction.category.in_(["legacy", DEFAULT_CATEGORY]))
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f
            .all()
        )

        updated = 0

        for trx in transactions:
            description = trx.description or ""

            detected_type = detect_type(description)
            detected_category = detect_category(description, detected_type)

<<<<<<< HEAD
            if detected_category != "legacy" or detected_type != trx.type:
=======
            if detected_category != DEFAULT_CATEGORY or trx.category == "legacy" or detected_type != trx.type:
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f
                trx.type = detected_type
                trx.category = detected_category
                updated += 1

        db.commit()
<<<<<<< HEAD

=======
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f
        print(f"Backfill selesai. Updated: {updated} transaksi.")

    finally:
        db.close()


if __name__ == "__main__":
<<<<<<< HEAD
    main()
=======
    main()
>>>>>>> f56b3f36128f503cdff548dcef3aabd379701c9f
