#!/usr/bin/env python3
import sys

from verdandi.component.icon import DIR_ICONS, _load_icon
from verdandi.util.image import validate_palette, invalid_colors
from verdandi.util.color import color_as_hex


def run():
    invalid_icons = set()

    for _root, _dirs, files in DIR_ICONS.walk():
        for icon_file in files:
            icon_name = icon_file.rsplit(".", maxsplit=1)[0]
            icon = _load_icon(icon_name)

            if not validate_palette(icon):
                invalid_icons.add(icon_name)

    if invalid_icons:
        print(f"{len(invalid_icons)} icons with invalid palette:")

        for icon_name in sorted(invalid_icons):
            icon = _load_icon(icon_name)

            colors = ", ".join(
                sorted(color_as_hex(color) for color in invalid_colors(icon))
            )

            print(f"- {icon_name}: {colors}")

        sys.exit(1)


if __name__ == "__main__":
    run()
