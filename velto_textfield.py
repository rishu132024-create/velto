class VeltoTextFieldError(Exception):
    pass


class VeltoTextField:
    def __init__(
        self,
        text="",
        placeholder="",
        x=0,
        y=0,
        width=200,
        height=40
    ):
        self.text = str(text)
        self.placeholder = str(placeholder)

        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)

        self.enabled = True
        self.visible = True
        self.focused = False

        self.max_length = None

        self._on_change = None
        self._on_submit = None

    def set_text(self, text):
        text = str(text)

        if self.max_length is not None:
            text = text[:self.max_length]

        self.text = text

        if self._on_change is not None:
            self._on_change(self.text)

    def get_text(self):
        return self.text

    def clear(self):
        self.set_text("")

    def set_placeholder(self, text):
        self.placeholder = str(text)

    def set_max_length(self, length):
        length = int(length)

        if length <= 0:
            raise VeltoTextFieldError(
                "Maximum length must be greater than zero"
            )

        self.max_length = length

        if len(self.text) > length:
            self.text = self.text[:length]

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set_size(self, width, height):
        self.width = float(width)
        self.height = float(height)

    def focus(self):
        if self.enabled and self.visible:
            self.focused = True

    def blur(self):
        self.focused = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False
        self.focused = False

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False
        self.focused = False

    def contains(self, x, y):
        return (
            self.x <= x <= self.x + self.width
            and
            self.y <= y <= self.y + self.height
        )

    def set_on_change(self, callback):
        if not callable(callback):
            raise VeltoTextFieldError(
                "Change handler must be callable"
            )

        self._on_change = callback

    def set_on_submit(self, callback):
        if not callable(callback):
            raise VeltoTextFieldError(
                "Submit handler must be callable"
            )

        self._on_submit = callback

    def submit(self):
        if not self.enabled:
            return False

        if self._on_submit is not None:
            self._on_submit(self.text)

        return True

    def info(self):
        return {
            "text": self.text,
            "placeholder": self.placeholder,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "enabled": self.enabled,
            "visible": self.visible,
            "focused": self.focused,
            "max_length": self.max_length
        }
