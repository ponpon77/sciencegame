import pyxel
import math

def stext(x, y, text, col):
    import pyxel
    for i, ch in enumerate(text):
        pyxel.text(x + i * 5, y, ch, col)


def draw_water_drop(x, y, size=8, color=12, frame=0):
    """Animated water drop icon."""
    bounce = math.sin(frame * 0.08) * 2
    cy = y + bounce
    pyxel.circ(x, cy + size // 2, size // 2, color)
    pyxel.tri(x - size // 2, cy + size // 2, x + size // 2, cy + size // 2, x, cy - size // 2 - 2, color)
    pyxel.circ(x - size // 4, cy + size // 4, 1, 7)


def draw_sdg6_icon(x, y, frame=0):
    """SDG6 water drop with gear."""
    draw_water_drop(x, y, 10, 12, frame)
    # gear around drop
    gx, gy = x + 8, y + 2
    for i in range(6):
        angle = frame * 0.02 + i * math.pi / 3
        tx = gx + math.cos(angle) * 5
        ty = gy + math.sin(angle) * 5
        pyxel.rect(int(tx) - 1, int(ty) - 1, 3, 3, 6)
    pyxel.circb(gx, gy, 3, 6)


def draw_filter_machine(x, y, filter_id, frame=0):
    """Draw a filter machine sprite at (x,y). ~16x24 pixels."""
    from engine.filters import FILTERS
    f = FILTERS.get(filter_id)
    if not f:
        return
    col = f["color"]

    if filter_id == "sedimentation":
        # settling tank: wide rectangular basin
        pyxel.rect(x, y + 4, 16, 16, 5)
        pyxel.rectb(x, y + 4, 16, 16, 6)
        # water layers
        pyxel.rect(x + 1, y + 5, 14, 8, 12)
        pyxel.rect(x + 1, y + 13, 14, 4, 4)
        # sediment dots
        for i in range(5):
            px = x + 2 + i * 3
            pyxel.pset(px, y + 17, 9)

    elif filter_id in ("slow_sand", "rapid_sand"):
        # sand column
        pyxel.rect(x + 2, y, 12, 22, 5)
        pyxel.rectb(x + 2, y, 12, 22, 6)
        # layers: gravel, sand, fine sand
        pyxel.rect(x + 3, y + 1, 10, 5, 12)
        pyxel.rect(x + 3, y + 6, 10, 6, 9)
        pyxel.rect(x + 3, y + 12, 10, 4, 15)
        pyxel.rect(x + 3, y + 16, 10, 5, 4)
        # pipe in/out
        pyxel.rect(x + 6, y - 2, 4, 3, 6)
        pyxel.rect(x + 6, y + 22, 4, 3, 6)

    elif filter_id == "gac":
        # dark carbon column
        pyxel.rect(x + 3, y, 10, 22, 0)
        pyxel.rectb(x + 3, y, 10, 22, 5)
        # carbon granules
        for i in range(8):
            gx = x + 4 + (i % 4) * 2
            gy = y + 2 + (i // 4) * 8 + (frame // 10 % 3)
            pyxel.pset(gx, gy, 5)
            pyxel.pset(gx + 1, gy, 1)
        # label
        pyxel.rect(x + 4, y + 9, 8, 5, 5)
        stext(x + 5, y + 10, "C", 7)

    elif filter_id == "reverse_osmosis":
        # high-tech box with membrane
        pyxel.rect(x, y + 2, 16, 18, 1)
        pyxel.rectb(x, y + 2, 16, 18, 12)
        # membrane lines
        for i in range(4):
            ly = y + 5 + i * 4
            pyxel.line(x + 2, ly, x + 13, ly, 12)
        # pressure gauge
        pyxel.circb(x + 8, y + 1, 3, 6)
        pyxel.circ(x + 8, y + 1, 2, 1)
        angle = math.sin(frame * 0.1) * 0.5 + 0.8
        pyxel.line(x + 8, y + 1, x + 8 + int(math.cos(angle) * 2), y + 1 - int(math.sin(angle) * 2), 8)
        # brine outlet
        pyxel.rect(x + 14, y + 14, 4, 2, 8)

    elif filter_id == "ion_exchange":
        # resin column
        pyxel.rect(x + 3, y, 10, 22, 5)
        pyxel.rectb(x + 3, y, 10, 22, 14)
        # colored resin beads
        colors = [14, 8, 9, 14, 11, 8]
        for i, c in enumerate(colors):
            bx = x + 4 + (i % 3) * 3
            by = y + 2 + (i // 3) * 8
            pyxel.circ(bx, by, 1, c)
        pyxel.rect(x + 5, y + 16, 6, 4, 14)

    elif filter_id == "uv":
        # UV lamp housing
        pyxel.rect(x + 2, y + 2, 12, 18, 1)
        pyxel.rectb(x + 2, y + 2, 12, 18, 13)
        # glowing lamp
        glow = abs(math.sin(frame * 0.15)) * 3
        pyxel.rect(x + 6, y + 4, 4, 14, 13)
        if frame % 4 < 3:
            pyxel.rect(x + 5, y + 5, 6, 12, 7)
        # rays
        for i in range(3):
            ry = y + 6 + i * 4
            pyxel.line(x + 3, ry, x + 5, ry, 13)
            pyxel.line(x + 11, ry, x + 13, ry, 13)

    elif filter_id == "chlorination":
        # chlorine tank
        pyxel.elli(x + 3, y + 2, 10, 18, 11)
        pyxel.rectb(x + 3, y + 2, 10, 18, 3)
        # Cl label
        stext(x + 5, y + 9, "Cl", 0)
        # drip
        if frame % 20 < 10:
            pyxel.pset(x + 8, y + 20 + (frame % 10) // 3, 11)

    elif filter_id == "lime_treatment":
        # lime bag/hopper
        pyxel.rect(x + 2, y + 2, 12, 14, 7)
        pyxel.rectb(x + 2, y + 2, 12, 14, 6)
        # funnel shape at bottom
        pyxel.tri(x + 3, y + 16, x + 13, y + 16, x + 8, y + 22, 7)
        # pH+ label
        stext(x + 4, y + 7, "pH", 0)
        pyxel.pset(x + 12, y + 7, 11)
        # lime particles falling
        if frame % 12 < 8:
            pyxel.pset(x + 7 + (frame % 3), y + 20, 7)
            pyxel.pset(x + 9 - (frame % 3), y + 19, 6)

    elif filter_id == "aeration":
        # aeration basin
        pyxel.rect(x + 1, y + 6, 14, 16, 1)
        pyxel.rectb(x + 1, y + 6, 14, 16, 6)
        # water
        pyxel.rect(x + 2, y + 10, 12, 11, 12)
        # rising bubbles (animated)
        for i in range(4):
            bx_ = x + 4 + i * 3
            by_ = y + 18 - ((frame + i * 5) % 10)
            if by_ > y + 10:
                pyxel.circb(bx_, by_, 1, 7)
        # air pipe at bottom
        pyxel.rect(x + 5, y + 20, 6, 3, 6)
        # fan icon on top
        pyxel.circ(x + 8, y + 3, 3, 6)
        pyxel.pset(x + 8, y + 3, 7)


def draw_pipe(x1, y1, x2, y2, frame=0, water_color=12):
    """Draw a connecting pipe with flowing water."""
    pyxel.line(x1, y1 - 1, x2, y2 - 1, 6)
    pyxel.line(x1, y1, x2, y2, water_color)
    pyxel.line(x1, y1 + 1, x2, y2 + 1, 6)
    # flow dots
    dx = x2 - x1
    for i in range(3):
        t = ((frame * 2 + i * 30) % 100) / 100.0
        px = x1 + dx * t
        pyxel.pset(int(px), y1, 7)


def draw_tank(x, y, w, h, fill_pct, dirty_pct, frame=0):
    """Draw a water tank with animated water level."""
    pyxel.rectb(x, y, w, h, 6)
    water_h = int((h - 2) * fill_pct)
    wy = y + h - 1 - water_h
    if water_h > 0:
        # water color based on dirtiness
        if dirty_pct > 0.7:
            wc = 4
        elif dirty_pct > 0.4:
            wc = 9
        elif dirty_pct > 0.15:
            wc = 12
        else:
            wc = 12
        pyxel.rect(x + 1, wy, w - 2, water_h, wc)
        # wave on top
        for wx in range(x + 1, x + w - 1):
            wave = math.sin((wx + frame * 0.5) * 0.3) * 1.5
            if int(wave) < 0:
                pyxel.pset(wx, wy, 0)
            elif int(wave) > 0 and wy > y + 1:
                pyxel.pset(wx, wy - 1, wc)


def draw_contaminant_bar(x, y, w, value, limit, label, frame=0):
    """Draw a horizontal bar showing contaminant level vs WHO limit."""
    if limit <= 0:
        ratio = 1.0 if value > 0 else 0.0
    else:
        ratio = min(value / (limit * 3), 1.0)

    # bar background
    pyxel.rect(x, y, w, 5, 1)

    # bar fill
    fill_w = int(w * ratio)
    if ratio > 1.0:
        bar_col = 8
    elif ratio > 0.7:
        bar_col = 9
    elif ratio > 0.3:
        bar_col = 10
    else:
        bar_col = 11

    if fill_w > 0:
        pyxel.rect(x, y, fill_w, 5, bar_col)

    # WHO limit marker
    if limit > 0:
        lx = x + int(w * min(limit / (limit * 3), 1.0))
        pyxel.line(lx, y - 1, lx, y + 5, 7)

    stext(x, y - 7, label, 7)


def draw_map_node(x, y, label, color, selected=False, locked=False, frame=0):
    """Draw a selectable map node."""
    r = 10 if selected else 8
    if locked:
        pyxel.circb(x, y, r, 5)
        stext(x - 2, y - 2, "?", 5)
    else:
        if selected:
            pulse = abs(math.sin(frame * 0.1)) * 2
            pyxel.circ(x, y, int(r + pulse), color)
            pyxel.circb(x, y, int(r + pulse), 7)
        else:
            pyxel.circ(x, y, r, color)
            pyxel.circb(x, y, r, 6)
    if not locked:
        tw = len(label) * 4
        stext(x - tw // 2, y + r + 3, label, 7)
