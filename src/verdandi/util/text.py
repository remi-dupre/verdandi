def keep_ascii(text: str) -> str:
    return "".join(c for c in text if ord(c) <= 255).strip()
