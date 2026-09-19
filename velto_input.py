class VeltoInputError(Exception):
    pass


class VeltoInput:
    def __init__(self):
        self.keys_down = set()
        self.keys_pressed = set()
        self.keys_released = set()

        self.mouse_x = 0
        self.mouse_y = 0

        self.mouse_buttons_down = set()
        self.mouse_buttons_pressed = set()
        self.mouse_buttons_released = set()

    def key_down(self, key):
        key = str(key).lower()

        return key in self.keys_down

    def key_pressed(self, key):
        key = str(key).lower()

        return key in self.keys_pressed

    def key_released(self, key):
        key = str(key).lower()

        return key in self.keys_released

    def mouse_down(self, button):
        button = str(button).lower()

        return button in self.mouse_buttons_down

    def mouse_pressed(self, button):
        button = str(button).lower()

        return button in self.mouse_buttons_pressed

    def mouse_released(self, button):
        button = str(button).lower()

        return button in self.mouse_buttons_released

    def get_mouse_position(self):
        return {
            "x": self.mouse_x,
            "y": self.mouse_y
        }

    def press_key(self, key):
        key = str(key).lower()

        if key not in self.keys_down:
            self.keys_pressed.add(key)

        self.keys_down.add(key)

    def release_key(self, key):
        key = str(key).lower()

        if key in self.keys_down:
            self.keys_released.add(key)

        self.keys_down.discard(key)

    def press_mouse(self, button, x=0, y=0):
        button = str(button).lower()

        self.mouse_x = int(x)
        self.mouse_y = int(y)

        if button not in self.mouse_buttons_down:
            self.mouse_buttons_pressed.add(button)

        self.mouse_buttons_down.add(button)

    def release_mouse(self, button, x=0, y=0):
        button = str(button).lower()

        self.mouse_x = int(x)
        self.mouse_y = int(y)

        if button in self.mouse_buttons_down:
            self.mouse_buttons_released.add(button)

        self.mouse_buttons_down.discard(button)

    def set_mouse_position(self, x, y):
        self.mouse_x = int(x)
        self.mouse_y = int(y)

    def update(self):
        self.keys_pressed.clear()
        self.keys_released.clear()

        self.mouse_buttons_pressed.clear()
        self.mouse_buttons_released.clear()
