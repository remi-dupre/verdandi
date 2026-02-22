from verdandi.widget.abs_widget import Widget

from PIL.ImageDraw import ImageDraw

from verdandi.component.icon import list_icons, icon_size, draw_icon

MARGIN = 5
ICON_MARGIN = 5


class DebugIcons3x4(Widget):
    name = "debug-icons-3x4"
    size = (3, 4)

    @classmethod
    def example(cls) -> "DebugIcons3x4":
        return DebugIcons3x4()

    def draw(self, draw: ImageDraw):  # ty:ignore[invalid-method-override]
        icons = list_icons()
        icons.sort(key=lambda icon: (icon_size(icon)[0], icon), reverse=True)

        curr_height = 0
        curr_x = MARGIN
        curr_y = MARGIN - ICON_MARGIN

        for icon in icons:
            icon_w, icon_h = icon_size(icon)

            if icon_h != curr_height or curr_x + icon_w > self.width() - MARGIN:
                curr_x = MARGIN
                curr_y += curr_height + ICON_MARGIN
                curr_height = icon_h

            draw_icon(draw, (curr_x, curr_y), icon)
            curr_x += icon_w + ICON_MARGIN
