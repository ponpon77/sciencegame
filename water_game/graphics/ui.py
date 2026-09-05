import pyxel
import math

# Pyxel's built-in font is 4px wide with NO gap between characters.
# Letters like 'a','d','n' etc blur together. This adds 1px spacing.
CHAR_W = 5  # 4px glyph + 1px gap


def stext(x, y, text, col):
    """Draw text with proper spacing (5px per char instead of 4)."""
    for i, ch in enumerate(text):
        pyxel.text(x + i * CHAR_W, y, ch, col)


def stext_width(text):
    """Width of spaced text in pixels."""
    return len(text) * CHAR_W


def big_text_width(text, scale=3):
    """Width in pixels of a big (scaled) title string."""
    return len(text) * 4 * scale


def draw_big_text(x, y, text, scale=3, col=7, shadow=None, outline=None):
    """Render chunky pixel-art title text by upscaling the built-in font.

    The text is drawn once into scratch image bank 2, then each lit font
    pixel is re-drawn as a `scale`x`scale` block. Optional drop `shadow`
    and `outline` colors give a 3D, Mario-style look.
    """
    img = pyxel.images[2]
    gw = len(text) * 4 + 2
    gh = 8
    img.rect(0, 0, gw, gh, 0)
    img.text(0, 0, text, 7)
    pts = [(gx, gy) for gy in range(gh) for gx in range(gw)
           if img.pget(gx, gy) == 7]

    if shadow is not None:
        s = max(1, scale // 2)
        for gx, gy in pts:
            pyxel.rect(x + gx * scale + s, y + gy * scale + s, scale, scale, shadow)

    if outline is not None:
        for gx, gy in pts:
            bx, by = x + gx * scale, y + gy * scale
            pyxel.rect(bx - 1, by, scale + 2, scale, outline)
            pyxel.rect(bx, by - 1, scale, scale + 2, outline)

    for gx, gy in pts:
        pyxel.rect(x + gx * scale, y + gy * scale, scale, scale, col)


def draw_text_box(x, y, w, h, text, title=None, frame=0):
    """Draw a bordered text box with optional title."""
    pyxel.rect(x, y, w, h, 1)
    pyxel.rectb(x, y, w, h, 12)
    pyxel.rectb(x + 1, y + 1, w - 2, h - 2, 5)
    ty = y + 4
    if title:
        tw = stext_width(title)
        tx = x + (w - tw) // 2
        pyxel.rect(tx - 2, y - 1, tw + 4, 7, 1)
        stext(tx, y, title, 10)
        ty = y + 10
    for line in text.split("\n"):
        stext(x + 4, ty, line, 7)
        ty += 8


def draw_button(x, y, w, h, label, selected=False, frame=0):
    """Draw a menu button."""
    bg = 12 if selected else 1
    border = 7 if selected else 5
    pyxel.rect(x, y, w, h, bg)
    pyxel.rectb(x, y, w, h, border)
    tw = stext_width(label)
    tx = x + (w - tw) // 2
    ty = y + (h - 5) // 2
    text_col = 0 if selected else 7
    stext(tx, ty, label, text_col)


def draw_meter(x, y, w, value, max_val, color_good=11, color_bad=8, label=""):
    """Draw a horizontal meter bar."""
    pyxel.rect(x, y, w, 4, 1)
    if max_val > 0:
        ratio = min(value / max_val, 1.0)
    else:
        ratio = 0
    fill = int(w * ratio)
    col = color_good if ratio < 0.5 else (9 if ratio < 0.8 else color_bad)
    if fill > 0:
        pyxel.rect(x, y, fill, 4, col)
    pyxel.rectb(x, y, w, 4, 5)
    if label:
        pyxel.text(x, y - 7, label, 6)


def draw_grade(x, y, grade, size=2):
    """Draw a large letter grade."""
    colors = {"A": 11, "B": 12, "C": 10, "D": 9, "F": 8}
    col = colors.get(grade, 7)
    # draw big text by using rect blocks
    pyxel.text(x, y, grade, col)
    if size >= 2:
        pyxel.text(x + 1, y, grade, col)
        pyxel.text(x, y + 1, grade, col)
        pyxel.text(x + 1, y + 1, grade, col)


def draw_blink_text(x, y, text, color=7, frame=0, speed=30):
    """Blinking text."""
    if (frame // speed) % 2 == 0:
        pyxel.text(x, y, text, color)


def draw_scroll_text(x, y, text, color=7, frame=0, speed=1):
    """Horizontally scrolling text."""
    tw = len(text) * 4
    offset = (frame * speed) % (tw + 256)
    px = 256 - offset + x
    pyxel.text(int(px), y, text, color)


def draw_stars(x, y, count, max_count=3, frame=0):
    """Draw star rating."""
    for i in range(max_count):
        sx = x + i * 10
        if i < count:
            pyxel.text(sx, y, "*", 10)
        else:
            pyxel.text(sx, y, "*", 5)


def draw_coin_counter(x, y, amount, frame=0):
    """Draw coin/money display."""
    pyxel.circ(x + 3, y + 3, 3, 10)
    pyxel.circ(x + 3, y + 3, 2, 9)
    stext(x + 2, y + 1, "C", 0)
    stext(x + 9, y, str(amount), 10)


def draw_water_bg(frame=0, color1=1, color2=12):
    """Draw animated water background."""
    for y in range(0, 256, 4):
        for x in range(0, 256, 4):
            wave = math.sin((x + frame * 0.5) * 0.05 + y * 0.03) * 0.5 + 0.5
            col = color1 if wave < 0.5 else color2
            pyxel.pset(x, y, col)
