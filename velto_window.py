class VeltoWindowError(Exception):
    pass


class VeltoWindow:
    def __init__(
        self,
        width=800,
        height=600,
        title="Velto",
        background="black"
    ):
        self.width = int(width)
        self.height = int(height)
        self.title = str(title)
        self.background = str(background)
        self.created = False
        self.running = False

    def create(self):
        if self.created:
            raise VeltoWindowError(
                "Window already exists"
            )

        self.created = True

        return True

    def set_title(self, title):
        if not self.created:
            raise VeltoWindowError(
                "Window is not created"
            )

        self.title = str(title)

    def set_background(self, color):
        if not self.created:
            raise VeltoWindowError(
                "Window is not created"
            )

        self.background = str(color)

    def size(self):
        return {
            "width": self.width,
            "height": self.height
        }

    def clear(self):
        if not self.created:
            raise VeltoWindowError(
                "Window is not created"
            )

        return True

    def close(self):
        if not self.created:
            return False

        self.running = False
        self.created = False

        return True

    def run(self):
        if not self.created:
            raise VeltoWindowError(
                "Window is not created"
            )

        self.running = True

        print(
            "Velto Window"
        )

        print(
            "Title: "
            + self.title
        )

        print(
            "Size: "
            + str(self.width)
            + "x"
            + str(self.height)
        )

        print(
            "Background: "
            + self.background
        )

        print(
            "Window backend is ready"
        )

        return True
