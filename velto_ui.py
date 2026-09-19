class VeltoUIError(Exception):
    pass


class UIElement:
    def __init__(
        self,
        x=0,
        y=0,
        width=100,
        height=40
    ):
        self.x = float(x)
        self.y = float(y)
        self.width = float(width)
        self.height = float(height)
        self.visible = True
        self.enabled = True

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set_size(self, width, height):
        self.width = float(width)
        self.height = float(height)

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def enable(self):
        self.enabled = True

    def disable(self):
        self.enabled = False

    def contains(self, x, y):
        return (
            self.x <= x <= self.x + self.width
            and
            self.y <= y <= self.y + self.height
        )

    def info(self):
        return {
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "visible": self.visible,
            "enabled": self.enabled
        }


class Label(UIElement):
    def __init__(
        self,
        text="",
        x=0,
        y=0
    ):
        super().__init__(
            x,
            y,
            100,
            40
        )

        self.text = str(text)

    def set_text(self, text):
        self.text = str(text)

    def info(self):
        data = super().info()
        data["text"] = self.text
        data["type"] = "label"
        return data


class Panel(UIElement):
    def __init__(
        self,
        x=0,
        y=0,
        width=300,
        height=200
    ):
        super().__init__(
            x,
            y,
            width,
            height
        )

        self.children = []

    def add(self, element):
        if not isinstance(element, UIElement):
            raise VeltoUIError(
                "Invalid UI element"
            )

        self.children.append(element)

    def remove(self, element):
        if element in self.children:
            self.children.remove(element)

    def info(self):
        data = super().info()
        data["type"] = "panel"
        data["children"] = len(self.children)
        return data


class Button(UIElement):
    def __init__(
        self,
        text="Button",
        x=0,
        y=0,
        width=120,
        height=40
    ):
        super().__init__(
            x,
            y,
            width,
            height
        )

        self.text = str(text)
        self.clicked = False
        self.on_click = None

    def set_text(self, text):
        self.text = str(text)

    def click(self):
        if not self.enabled:
            return False

        self.clicked = True

        if callable(self.on_click):
            self.on_click()

        return True

    def reset(self):
        self.clicked = False

    def set_on_click(self, callback):
        if not callable(callback):
            raise VeltoUIError(
                "Callback must be callable"
            )

        self.on_click = callback

    def info(self):
        data = super().info()
        data["text"] = self.text
        data["clicked"] = self.clicked
        data["type"] = "button"
        return data
