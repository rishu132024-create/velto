from velto_sprite import VeltoSprite
from velto_animation import VeltoAnimation
from velto_collision import intersects
from velto_collision import point_inside
from velto_collision import distance


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
