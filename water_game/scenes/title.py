import pyxel
import math
from graphics.sprites import draw_water_drop
from graphics.cursor import draw_cursor, clicked, mouse_in_rect
from graphics.ui import (stext, stext_width,
                         draw_big_text, big_text_width)


# START button geometry (shared by draw + input)
BTN_X, BTN_Y, BTN_W, BTN_H = 78, 168, 100, 16
SEABED = 208


class TitleScene:
    def __init__(self):
        self.frame = 0
        # rising bubbles
        self.bubbles = []
        for i in range(28):
            self.bubbles.append({
                "x": (i * 47) % 256,
                "y": (i * 31) % 256,
                "r": 1 + (i % 3),
                "spd": 0.3 + (i % 5) * 0.15,
                "wob": i * 0.7,
            })
        # seaweed strand base positions
        self.weeds = [18, 60, 110, 150, 200, 240]

    def update(self):
        self.frame += 1
        for b in self.bubbles:
            b["y"] -= b["spd"]
            if b["y"] < -4:
                b["y"] = 260
                b["x"] = (b["x"] * 7 + 31) % 256

    def draw(self):
        f = self.frame
        self._draw_ocean(f)
        self._draw_seabed(f)
        self._draw_logo(f)
        self._draw_menu(f)
        draw_cursor(f)

    # --------------------------------------------------------------- ocean
    def _draw_ocean(self, f):
        # depth gradient bands (light near surface -> deep at bottom)
        for y in range(0, SEABED):
            t = y / SEABED
            if t < 0.22:
                c = 6
            elif t < 0.45:
                c = 12
            elif t < 0.72:
                c = 5
            else:
                c = 1
            pyxel.line(0, y, 256, y, c)

        # soft dither between bands
        for y in range(0, SEABED, 2):
            t = y / SEABED
            if 0.18 < t < 0.26 or 0.41 < t < 0.49 or 0.68 < t < 0.76:
                for x in range(0, 256, 4):
                    pyxel.pset(x + (y % 4), y, 5 if t > 0.5 else 12)

        # god rays slanting down from the surface
        for i in range(4):
            rx = (i * 74 + f * 0.4) % 330 - 50
            for yy in range(0, 150, 3):
                pyxel.pset(int(rx + yy * 0.55), yy, 6)

        # rising bubbles
        for b in self.bubbles:
            bx = int(b["x"] + math.sin(f * 0.04 + b["wob"]) * 3)
            by = int(b["y"])
            pyxel.circb(bx, by, b["r"], 7)
            pyxel.pset(bx - 1, by - 1, 7)

    # -------------------------------------------------------------- seabed
    def _draw_seabed(self, f):
        # sand
        pyxel.rect(0, SEABED, 256, 256 - SEABED, 15)
        pyxel.rect(0, SEABED, 256, 2, 9)
        # sand dunes
        for dx in (40, 130, 210):
            pyxel.elli(dx - 24, SEABED - 5, 48, 14, 15)
        # sand speckles
        for i in range(40):
            sx = (i * 53 + 7) % 256
            sy = SEABED + 4 + (i * 13) % (256 - SEABED - 4)
            pyxel.pset(sx, sy, 9)

        # swaying seaweed
        for wi, base in enumerate(self.weeds):
            col = 11 if wi % 2 == 0 else 3
            segs = 6 + wi % 3
            for s in range(segs):
                sway = math.sin(f * 0.05 + s * 0.5 + wi) * (s * 0.8)
                x = int(base + sway)
                y = SEABED - s * 4
                pyxel.rect(x, y, 3, 4, col)

        # coral nubs
        for cx2, col in ((84, 14), (176, 8)):
            pyxel.circ(cx2, SEABED - 2, 4, col)
            pyxel.circ(cx2 - 4, SEABED, 3, col)
            pyxel.circ(cx2 + 4, SEABED, 3, col)

        # little water-drop mascot swimming above the seabed
        mx = 128 + int(math.sin(f * 0.05) * 36)
        my = SEABED - 16 + int(math.sin(f * 0.1) * 3)
        draw_water_drop(mx, my, 8, 7, f)

    # ----------------------------------------------------------- logo box
    def _draw_logo(self, f):
        px, py, pw, ph = 40, 30, 176, 78
        pyxel.rect(px + 3, py + 4, pw, ph, 0)            # shadow
        pyxel.rect(px, py, pw, ph, 1)                   # deep-water body
        pyxel.rectb(px, py, pw, ph, 6)                  # light border
        pyxel.rectb(px + 2, py + 2, pw - 4, ph - 4, 12)  # inner accent
        cx = px + pw // 2

        # big chunky title (two lines, 3D look)
        t1 = "AQUA"
        draw_big_text(cx - big_text_width(t1, 4) // 2, py + 8,
                      t1, 4, col=7, shadow=0, outline=5)
        t2 = "PURIFIER"
        draw_big_text(cx - big_text_width(t2, 3) // 2, py + 44,
                      t2, 3, col=6, shadow=0, outline=5)

        # subtitle ribbon
        sub = "WATER TYCOON"
        sw = stext_width(sub)
        pyxel.rect(cx - sw // 2 - 4, py + ph + 2, sw + 8, 9, 0)
        stext(cx - sw // 2, py + ph + 3, sub, 10)

        # credit line
        cred = "(C) 2026  konh"
        stext(cx - stext_width(cred) // 2, py + ph + 14, cred, 6)

    # -------------------------------------------------------------- menu
    def _draw_menu(self, f):
        cx = 128
        hover = mouse_in_rect(BTN_X, BTN_Y, BTN_W, BTN_H)

        # bobbing water-drop selector
        sel_x = BTN_X - 12 + (1 if (f // 8) % 2 == 0 else 0)
        draw_water_drop(sel_x, BTN_Y + 4, 6, 10, f)

        # button
        pyxel.rect(BTN_X, BTN_Y, BTN_W, BTN_H, 5 if hover else 1)
        if hover:
            pyxel.rectb(BTN_X - 1, BTN_Y - 1, BTN_W + 2, BTN_H + 2, 7)
        label = "START GAME"
        stext(cx - stext_width(label) // 2, BTN_Y + 5, label,
              10 if hover else 7)

    # -------------------------------------------------------------- input
    def handle_input(self):
        if clicked() and mouse_in_rect(BTN_X, BTN_Y, BTN_W, BTN_H):
            pyxel.play(1, 2)  # success jingle on start
            return "world_map"
        if pyxel.btnp(pyxel.KEY_RETURN):
            pyxel.play(1, 2)
            return "world_map"
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        return None
