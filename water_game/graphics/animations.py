import pyxel
import math

def stext(x, y, text, col):
    import pyxel
    for i, ch in enumerate(text):
        pyxel.text(x + i * 5, y, ch, col)


def draw_water_surface(x, y, w, frame, color=12, amplitude=2):
    """Draw an animated sine-wave water surface."""
    for px in range(w):
        wave_y = y + int(math.sin((x + px + frame * 0.8) * 0.1) * amplitude)
        pyxel.pset(x + px, wave_y, color)
        pyxel.line(x + px, wave_y + 1, x + px, y + amplitude + 4, color)


def draw_bubbles(x, y, w, h, frame, count=6, color=7):
    """Animated rising bubbles in a water region."""
    for i in range(count):
        phase = i * 1.7
        bx = x + (i * 17 + int(math.sin(frame * 0.04 + phase) * 5)) % w
        by = y + h - ((frame * (1 + i % 3) + i * 40) % (h + 10))
        if y <= by <= y + h:
            pyxel.circb(bx, by, 1, color)


def draw_rain(frame, intensity=20):
    """Animated rain overlay."""
    for i in range(intensity):
        rx = (i * 37 + frame * 3) % 256
        ry = (i * 23 + frame * 5) % 256
        pyxel.line(rx, ry, rx - 1, ry + 3, 12)


def draw_flow_arrow(x, y, direction="right", frame=0, color=12):
    """Animated flow direction arrow."""
    offset = (frame // 5) % 6
    if direction == "right":
        for i in range(3):
            ax = x + offset + i * 6
            pyxel.pset(ax, y, color)
            pyxel.pset(ax + 1, y - 1, color)
            pyxel.pset(ax + 1, y + 1, color)


def draw_lab_background(frame):
    """Draw the filtration lab background (clean back wall + floor)."""
    # floor tiles (covered by the bottom bar, kept subtle)
    for ty in range(200, 256, 12):
        for tx in range(0, 256, 12):
            col = 5 if (tx // 12 + ty // 12) % 2 == 0 else 1
            pyxel.rect(tx, ty, 12, 12, col)

    # plain back wall - no clutter so it can't overlap the UI
    pyxel.rect(0, 0, 256, 38, 1)
    pyxel.line(0, 38, 256, 38, 5)


def draw_map_background(frame):
    """Draw the world map background with terrain."""
    # ocean - use large rects for speed
    pyxel.cls(1)
    for y in range(0, 256, 8):
        for x in range(0, 256, 8):
            wave = math.sin((x + frame * 0.3) * 0.05 + y * 0.04)
            col = 1 if wave < 0 else 12
            pyxel.rect(x, y, 8, 8, col)

    # land mass
    land_points = [
        (30, 50), (80, 30), (140, 40), (200, 50), (230, 70),
        (220, 130), (200, 180), (160, 200), (100, 210),
        (50, 190), (30, 150), (20, 100),
    ]
    # simplified land fill
    pyxel.rect(30, 40, 200, 180, 3)
    pyxel.rect(35, 45, 190, 170, 11)
    pyxel.rect(40, 50, 180, 160, 3)

    # rivers on land
    for i in range(30):
        rx = 60 + int(math.sin(i * 0.3 + frame * 0.01) * 20)
        ry = 50 + i * 5
        pyxel.line(rx, ry, rx + 10, ry + 3, 12)

    # mountain
    pyxel.tri(160, 80, 140, 120, 180, 120, 5)
    pyxel.tri(160, 80, 150, 95, 170, 95, 6)

    # trees
    for i in range(8):
        tx = 60 + i * 20
        ty = 140 + (i % 3) * 10
        pyxel.tri(tx, ty - 6, tx - 3, ty, tx + 3, ty, 3)
        pyxel.rect(tx - 1, ty, 2, 3, 4)
