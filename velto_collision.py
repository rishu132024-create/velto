class VeltoCollisionError(Exception):
    pass


def bounds(sprite):
    if not hasattr(sprite, "bounds"):
        raise VeltoCollisionError("Invalid sprite")
    return sprite.bounds()


def intersects(first, second):
    a = bounds(first)
    b = bounds(second)

    return not (
        a["right"] <= b["left"]
        or a["left"] >= b["right"]
        or a["bottom"] <= b["top"]
        or a["top"] >= b["bottom"]
    )


def point_inside(sprite, x, y):
    box = bounds(sprite)
    return (
        x >= box["left"]
        and x <= box["right"]
        and y >= box["top"]
        and y <= box["bottom"]
    )


def distance(first, second):
    a = first.position()
    b = second.position()

    dx = b["x"] - a["x"]
    dy = b["y"] - a["y"]

    return (dx * dx + dy * dy) ** 0.5
