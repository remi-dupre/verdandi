CB = 0  # Black
CD = 85  # Dark Grey
CL = 170  # Light Grey
CW = 255  # White

# How much darker eink is
EINK_SHADING = 1.4


def color_as_hex(color: int) -> str:
    """
    Return the hex representation of input color.
    """
    return "#" + f"{color:02x}" * 3


def map_simulate_eink(color: int) -> int:
    """
    On the actual TRML screen the rendering is darker, this maps the palette to
    a darker tone to simulate the actual screen on a regular LCD panel.
    """
    return int(255 * (color / 255) ** EINK_SHADING)
