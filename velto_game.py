from velto_sprite import VeltoSprite
from velto_animation import VeltoAnimation
from velto_collision import intersects
from velto_collision import point_inside
from velto_collision import distance
from velto_sound import VeltoSound
from velto_physics import PhysicsBody
from velto_ui import Label
from velto_ui import Panel
from velto_buttons import VeltoButton
from velto_textfield import VeltoTextField
from velto_layout import Row
from velto_layout import Column
from velto_layout import Grid
from velto_app import VeltoApp
from velto_android import AndroidProject


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


def button(text="Button", x=0, y=0, width=120, height=40):
    return VeltoButton(text, x, y, width, height)


def label(text="", x=0, y=0):
    return Label(text, x, y)


def panel(x=0, y=0, width=300, height=200):
    return Panel(x, y, width, height)


def text_field(
    text="",
    placeholder="",
    x=0,
    y=0,
    width=200,
    height=40
):
    return VeltoTextField(
        text,
        placeholder,
        x,
        y,
        width,
        height
    )


def row(x=0, y=0, width=400, height=100, spacing=10):
    return Row(x, y, width, height, spacing)


def column(x=0, y=0, width=400, height=300, spacing=10):
    return Column(x, y, width, height, spacing)


def grid(columns=2, x=0, y=0, width=400, height=300, spacing=10):
    return Grid(
        columns,
        x,
        y,
        width,
        height,
        spacing
    )


def app(title="Velto App", width=800, height=600):
    return VeltoApp(title, width, height)


def android_project(
    name,
    package_name,
    version="1.0.0",
    min_sdk=23
):
    return AndroidProject(
        name,
        package_name,
        version,
        min_sdk
    )
