class VeltoSpriteError(Exception):
    pass


class VeltoSprite:
    def __init__(
        self,
        name="sprite",
        image=None,
        x=0,
        y=0,
        width=32,
        height=32
    ):
        self.name = str(name)
        self.image = image

        self.x = float(x)
        self.y = float(y)

        self.width = float(width)
        self.height = float(height)

        self.visible = True
        self.rotation = 0.0
        self.scale = 1.0

    def move(self, dx, dy):
        self.x += float(dx)
        self.y += float(dy)

    def set_position(self, x, y):
        self.x = float(x)
        self.y = float(y)

    def set_size(self, width, height):
        self.width = float(width)
        self.height = float(height)

    def set_rotation(self, angle):
        self.rotation = float(angle)

    def set_scale(self, scale):
        scale = float(scale)

        if scale <= 0:
            raise VeltoSpriteError(
                "Scale must be greater than zero"
            )

        self.scale = scale

    def show(self):
        self.visible = True

    def hide(self):
        self.visible = False

    def position(self):
        return {
            "x": self.x,
            "y": self.y
        }

    def size(self):
        return {
            "width": self.width * self.scale,
            "height": self.height * self.scale
        }

    def bounds(self):
        width = self.width * self.scale
        height = self.height * self.scale

        return {
            "left": self.x,
            "top": self.y,
            "right": self.x + width,
            "bottom": self.y + height
        }

    def info(self):
        return {
            "name": self.name,
            "image": self.image,
            "x": self.x,
            "y": self.y,
            "width": self.width,
            "height": self.height,
            "visible": self.visible,
            "rotation": self.rotation,
            "scale": self.scale
        }
