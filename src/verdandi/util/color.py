CB = 0  # Black
CD = 85  # Dark Grey
CL = 170  # Light Grey
CW = 255  # White


def color_as_hex(color: int) -> str:
    """
    Return the hex representation of input color.
    """
    return "#" + f"{color:02x}" * 3
