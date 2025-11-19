from functools import lru_cache

ICON_MAPPING = {
    "christmas-tree": ["🎄"],
    "heart": ["❤️", "💍", "couple"],
    "present": ["🎂", "anniversaire"],
    "beer": ["🍺", "🍻", "🍸", "cocktail", "bière"],
    "coffee": ["☕", "café", "brunch", "goûter"],
    "tablewear": ["🍽️", "dîner", "déjeuner", "repas"],
    "medical": ["🩸", "💉", "🩺", "🧑🏽‍⚕"],
}


def keep_ascii(text: str) -> str:
    return "".join(c for c in text if ord(c) <= 255).strip()


@lru_cache(maxsize=1024)
def guess_icon(text: str) -> str | None:
    text = text.lower()

    for icon, mapping in ICON_MAPPING.items():
        for x in mapping:
            if x in text:
                return icon

    return None
