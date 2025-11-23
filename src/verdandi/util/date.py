from datetime import date, datetime, timedelta

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


def next_time_cadenced(now: datetime, interval: timedelta) -> datetime:
    """
    Split the days into intervals of fixed time and return the next recurring
    interval.
    """
    date_start = now.replace(hour=0, minute=0, second=0, microsecond=0)
    curr = date_start
    assert interval.total_seconds() > 0.0

    while curr <= now:
        curr += interval

    if curr.date() > now.date():
        return date_start + timedelta(days=1)

    return curr
