import pyxel
import math


def draw_cursor(frame=0):
    """Draw a custom animated cursor at the mouse position.
    A water-drop shaped pointer with a glowing ring."""
    mx = pyxel.mouse_x
    my = pyxel.mouse_y

    # outer glow ring (pulses)
    pulse = abs(math.sin(frame * 0.12)) * 2
    r = int(5 + pulse)
    pyxel.circb(mx, my, r, 12)

    # pointer arrow (top-left aligned like a real cursor)
    # main arrow body - white with dark outline
    # outline
    pyxel.line(mx, my, mx, my + 10, 0)
    pyxel.line(mx, my, mx + 7, my + 7, 0)
    pyxel.line(mx + 7, my + 7, mx + 3, my + 7, 0)
    pyxel.line(mx + 3, my + 7, mx + 5, my + 11, 0)
    pyxel.line(mx + 5, my + 11, mx + 3, my + 12, 0)
    pyxel.line(mx + 3, my + 12, mx + 1, my + 8, 0)
    pyxel.line(mx + 1, my + 8, mx, my + 10, 0)
    # fill
    pyxel.tri(mx + 1, my + 1, mx + 1, my + 9, mx + 6, my + 7, 7)

    # small water drop at tip
    pyxel.pset(mx, my, 12)
    pyxel.pset(mx + 1, my + 1, 12)


def draw_cursor_bucket(frame=0):
    """Draw a bucket-shaped cursor for the collection scene."""
    mx = pyxel.mouse_x
    my = pyxel.mouse_y

    # bucket body
    pyxel.rect(mx - 4, my - 2, 9, 8, 6)
    pyxel.rectb(mx - 4, my - 2, 9, 8, 7)
    # handle
    pyxel.line(mx - 2, my - 4, mx + 2, my - 4, 6)
    pyxel.line(mx - 2, my - 4, mx - 4, my - 2, 6)
    pyxel.line(mx + 2, my - 4, mx + 4, my - 2, 6)
    # water inside (animated slosh)
    slosh = int(math.sin(frame * 0.15) * 1)
    pyxel.rect(mx - 3, my + 1 + slosh, 7, 4 - slosh, 12)
    # highlight
    pyxel.pset(mx - 2, my, 7)

    # collection radius indicator
    pulse = abs(math.sin(frame * 0.1)) * 3
    pyxel.circb(mx, my, int(12 + pulse), 12)


def draw_cursor_pump(frame=0):
    """Draw a pump-shaped cursor for when pump is equipped."""
    mx = pyxel.mouse_x
    my = pyxel.mouse_y

    # pump body
    pyxel.rect(mx - 3, my - 6, 7, 12, 5)
    pyxel.rectb(mx - 3, my - 6, 7, 12, 6)
    # handle on top
    pyxel.rect(mx - 5, my - 8, 11, 3, 6)
    pyxel.rect(mx - 1, my - 10, 3, 3, 6)
    # nozzle at bottom
    pyxel.rect(mx - 1, my + 6, 3, 4, 6)
    # water spray from nozzle
    if frame % 6 < 4:
        pyxel.pset(mx, my + 10, 12)
        pyxel.pset(mx - 1, my + 11, 12)
        pyxel.pset(mx + 1, my + 11, 12)
        pyxel.pset(mx, my + 12, 12)
    # pump action indicator
    bob = int(math.sin(frame * 0.2) * 2)
    pyxel.rect(mx - 1, my - 10 + bob, 3, 2, 7)

    # large collection radius
    pulse = abs(math.sin(frame * 0.08)) * 4
    pyxel.circb(mx, my, int(18 + pulse), 11)


def mouse_in_rect(x, y, w, h):
    """Check if mouse is inside a rectangle."""
    return x <= pyxel.mouse_x < x + w and y <= pyxel.mouse_y < y + h


def mouse_in_circle(cx, cy, r):
    """Check if mouse is inside a circle."""
    dx = pyxel.mouse_x - cx
    dy = pyxel.mouse_y - cy
    return dx * dx + dy * dy <= r * r


def clicked():
    """Check if left mouse button was just pressed."""
    return pyxel.btnp(pyxel.MOUSE_BUTTON_LEFT)


def holding():
    """Check if left mouse button is held down."""
    return pyxel.btn(pyxel.MOUSE_BUTTON_LEFT)
