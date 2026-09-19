class VeltoButtonError(Exception):
    pass


class VeltoButton:
    def __init__(
        self,
        text="Button",
        x=0,
        y=0,
        width=120,
        height=40
    ):
        self.text = str(text)
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

        self.enabled = True
        self.visible = True
        self.pressed = False
        self.hovered = False

        self._callback = None

    def set_text(self, text):
        self.text = str(text)

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set_size(self, width, height):
        self.width = float(width)
        self.height = float(height)

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def set_on_click(self, callback):
        if not callable(callback):
            raise VeltoButtonError(
                "Click handler must be callable"
            )

        self._callback = callback

    def contains(self, x, y):
        return (
            self.x <= x <= self.x + self.width
            and
            self.y <= y <= self.y + self.height
        )

    def click(self):
        if not self.enabled:
            return False

        if not self.visible:
            return False

        self.pressed = True

        if self._callback is not None:
            self._callback()

        return True

    def release(self):
        self.pressed = False

    def hover(self, x, y):
        self.hovered = self.contains(
            x,
            y
        )

        return self.hovered

    def info(self):
        return {
            "text": self.text,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "enabled": self.enabled,
            "visible": self.visible,
            "pressed": self.pressed,
            "hovered": self.hovered
        }
