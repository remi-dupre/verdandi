from datetime import date

_DOW_STR = {
    0: "lundi",
    1: "mardi",
    2: "mercredi",
    3: "jeudi",
    4: "vendredi",
    5: "samedi",
    6: "dimanche",
}


def weekday_humanized(date: date) -> str:
    return _DOW_STR[date.weekday()]
