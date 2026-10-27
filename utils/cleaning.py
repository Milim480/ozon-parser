def clean_price(value):
    digits = "".join(ch for ch in value if ch.isdigit())
    return int(digits) if digits else None