import logging


def keep_ascii(text: str) -> str:
    for c in text:
        if ord(c) > 255:
            logging.info("%s: %d", c, ord(c))

    return "".join(c for c in text if ord(c) <= 255).strip()
