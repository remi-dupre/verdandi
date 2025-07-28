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

_MONTH_STR = {
    1: "janvier",
    2: "février",
    3: "mars",
    4: "avril",
    5: "mai",
    6: "juin",
    7: "juillet",
    8: "août",
    9: "septembre",
    10: "octobre",
    11: "novembre",
    12: "décembre",
}


def weekday_humanized(date: date) -> str:
    return _DOW_STR[date.weekday()]


def month_humanized(date: date) -> str:
    return _MONTH_STR[date.month]
