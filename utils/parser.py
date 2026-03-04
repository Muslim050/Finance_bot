import re
from dataclasses import dataclass
from typing import Optional


@dataclass
class Transaction:
    amount: float
    currency: str
    card: str
    merchant: str
    datetime_str: str
    balance: Optional[float] = None
    raw: str = ""


def parse_cardxabar(text: str) -> Optional[Transaction]:
    """
    Parse cardxabar notification format:
    
    🔴 Platezh
    ➖ 5 706 000.00 UZS
    💳 ***1519
    📍 OFB UZCARD2LOAN, UZ
    🕓 02.03.26 21:33
    💵 8 342 402.46 UZS
    """
    try:
        # Check it's a payment notification
        if "Platezh" not in text and "platezh" not in text.lower():
            return None

        # Amount — line with ➖
        amount_match = re.search(r'➖\s*([\d\s]+\.?\d*)\s*(UZS|USD|EUR|RUB)', text)
        if not amount_match:
            return None
        amount_str = amount_match.group(1).replace(" ", "")
        amount = float(amount_str)
        currency = amount_match.group(2)

        # Card
        card_match = re.search(r'💳\s*(\*+\d+)', text)
        card = card_match.group(1) if card_match else "unknown"

        # Merchant — line with 📍, strip country code
        merchant_match = re.search(r'📍\s*(.+)', text)
        merchant = "Неизвестно"
        if merchant_match:
            raw_merchant = merchant_match.group(1).strip()
            # Remove trailing ", UZ" or ", RU" etc.
            merchant = re.sub(r',\s*[A-Z]{2}\s*$', '', raw_merchant).strip()

        # Datetime — format: 02.03.26 21:33 → convert to 2026-03-02 21:33
        dt_match = re.search(r'🕓\s*(\d{2})\.(\d{2})\.(\d{2})\s+(\d{2}:\d{2})', text)
        datetime_str = ""
        if dt_match:
            day, month, year_short, time = dt_match.groups()
            datetime_str = f"20{year_short}-{month}-{day} {time}"

        # Balance after payment
        balance_match = re.search(r'💵\s*([\d\s]+\.?\d*)\s*(UZS|USD|EUR|RUB)', text)
        balance = None
        if balance_match:
            balance = float(balance_match.group(1).replace(" ", ""))

        return Transaction(
            amount=amount,
            currency=currency,
            card=card,
            merchant=merchant,
            datetime_str=datetime_str,
            balance=balance,
            raw=text
        )
    except Exception:
        return None


def normalize_merchant(merchant: str) -> str:
    """Normalize merchant name for better matching."""
    return merchant.upper().strip()