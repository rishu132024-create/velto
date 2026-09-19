from velto_sprite import VeltoSprite


def sprite(image=None, name="sprite"):
    return VeltoSprite(
        name=name,
        image=image
    )


def create_sprite(
    name,
    image=None,
    x=0,
    y=0,
    width=32,
    height=32
):
    return VeltoSprite(
        name=name,
        image=image,
        x=x,
        y=y,
        width=width,
        height=height
    )
