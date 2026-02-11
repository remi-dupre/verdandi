from functools import lru_cache

CATEGORY_MAPPING = {
    "unknown": ["tbc", "???"],
    "christmas-tree": ["🎄", "noël"],
    "heart": [*"❤💝💍", "couple"],
    "present": ["🎂", "anniversaire", "anniv"],
    "beer": [*"🍺🍻🍸", "cocktail", "bière", "verre"],
    "coffee": ["☕", "café", "brunch", "goûter"],
    "tablewear": ["🍽️", "dîner", "diner", "déjeuner", "repas"],
    "medical": [*"🩸💉🩺🧑🏽‍⚕", "médecin", "docteur", "dentiste"],
    "music": [*"🎵🎶🎤", "concert"],
    "scissors": ["✂", "coiffeur"],
    "shopping": [*"🛍🛒", "courses"],
    "work": ["séminaire", "travail", "entretiens"],
    "train": [*"🚂🚆🚉🚄🛤🚅🚃", "train", "gare"],
    "suitcase": ["🧳", "voyage"],
}


def keep_ascii(text: str) -> str:
    return "".join(c for c in text if ord(c) <= 255).strip()


@lru_cache(maxsize=1024)
def summary_to_category(text: str) -> str | None:
    text = text.lower()

    for icon, mapping in CATEGORY_MAPPING.items():
        for x in mapping:
            if x in text:
                return icon

    return None
