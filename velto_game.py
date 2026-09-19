from velto_sprite import VeltoSprite
from velto_animation import VeltoAnimation
from velto_collision import intersects
from velto_collision import point_inside
from velto_collision import distance
from velto_sound import VeltoSound
from velto_physics import PhysicsBody
from velto_ui import Button
from velto_ui import Label
from velto_ui import Panel


def sprite(image=None, name="sprite"):
    return VeltoSprite(name=name, image=image)


def create_sprite(name, image=None, x=0, y=0, width=32, height=32):
    return VeltoSprite(
        name=name,
        image=image,
        x=x,
        y=y,
        width=width,
        height=height
    )


def animation(name="animation"):
    return VeltoAnimation(name)


def collision(first, second):
    return intersects(first, second)


def contains_point(sprite_object, x, y):
    return point_inside(sprite_object, x, y)


def distance_between(first, second):
    return distance(first, second)


def sound(source=None):
    return VeltoSound(source)


def physics(x=0, y=0, mass=1.0):
    return PhysicsBody(x, y, mass)


def button(text="Button", x=0, y=0):
    return Button(text, x, y)


def label(text="", x=0, y=0):
    return Label(text, x, y)


def panel(x=0, y=0, width=300, height=200):
    return Panel(x, y, width, height)
