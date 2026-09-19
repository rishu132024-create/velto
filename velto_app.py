class VeltoAppError(Exception):
    pass


class VeltoApp:
    def __init__(
        self,
        title="Velto App",
        width=800,
        height=600
    ):
        self.title = str(title)
        self.width = int(width)
        self.height = int(height)

        self.running = False
        self.elements = []
        self._on_start = None
        self._on_close = None

    def set_title(self, title):
        self.title = str(title)

    def set_size(self, width, height):
        self.width = int(width)
        self.height = int(height)

    def add(self, element):
        self.elements.append(element)

    def remove(self, element):
        if element in self.elements:
            self.elements.remove(element)

    def clear(self):
        self.elements.clear()

    def set_on_start(self, callback):
        if not callable(callback):
            raise VeltoAppError(
                "Start handler must be callable"
            )

        self._on_start = callback

    def set_on_close(self, callback):
        if not callable(callback):
            raise VeltoAppError(
                "Close handler must be callable"
            )

        self._on_close = callback

    def start(self):
        if self.running:
            return False

        self.running = True

        if self._on_start is not None:
            self._on_start()

        return True

    def close(self):
        if not self.running:
            return False

        self.running = False

        if self._on_close is not None:
            self._on_close()

        return True

    def is_running(self):
        return self.running

    def info(self):
        return {
            "title": self.title,
            "width": self.width,
            "height": self.height,
            "running": self.running,
            "elements": len(self.elements)
        }
