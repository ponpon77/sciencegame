import pyxel
import math
from graphics.cursor import draw_cursor, clicked, mouse_in_rect
from graphics.ui import stext, draw_coin_counter


class EndingScene:
    """Victory ending — player purified all 5 water sources."""

    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0

    def update(self):
        self.frame += 1

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        # animated water rising from bottom
        water_h = min(f // 2, 200)
        if water_h > 0:
            pyxel.rect(0, 256 - water_h, 256, water_h, 12)
            # wave on top
            for x in range(0, 256, 2):
                wy = 256 - water_h + int(math.sin(x * 0.08 + f * 0.05) * 3)
                pyxel.pset(x, wy, 7)
                pyxel.pset(x + 1, wy, 7)

        # sparkle particles
        for i in range(20):
            sx = (i * 37 + f * 2) % 256
            sy = (i * 23 + f) % 200 + 30
            if (f + i * 7) % 20 < 12:
                pyxel.pset(sx, sy, 7 if (f + i) % 3 == 0 else 10)

        # dark panel
        if f > 30:
            pyxel.rect(24, 20, 208, 210, 0)
            pyxel.rectb(24, 20, 208, 210, 11)
            pyxel.rectb(26, 22, 204, 206, 5)

        # title appears
        if f > 50:
            stext(56, 30, "MISSION COMPLETE!", 11)
            pyxel.line(56, 38, 200, 38, 11)

        # story text fades in
        if f > 80:
            stext(34, 48, "You purified all 5 water", 7)
            stext(34, 58, "sources in the region!", 7)

        if f > 110:
            stext(34, 74, "Thanks to your filtration", 12)
            stext(34, 84, "expertise, thousands of", 12)
            stext(34, 94, "people now have access to", 12)
            stext(34, 104, "clean, safe drinking water.", 12)

        if f > 150:
            stext(34, 120, "SDG6: Clean Water &", 11)
            stext(34, 130, "Sanitation for All", 11)

        # stats
        if f > 180:
            pyxel.line(34, 142, 222, 142, 5)
            stext(34, 148, "YOUR LEGACY:", 10)

            jobs = self.game_state.get("jobs_done", 0)
            liters = self.game_state.get("total_liters", 0)
            earned = self.game_state.get("total_earned", 0)
            rep = self.game_state.get("reputation", 0)
            coins = self.game_state.get("coins", 0)

            stext(34, 160, f"Jobs completed: {jobs}", 7)
            stext(34, 170, f"Water purified: {liters}L", 7)
            stext(34, 180, f"Total earned: {earned}", 7)
            stext(34, 190, f"Reputation: {rep}", 7)
            stext(34, 200, f"Final balance: {coins}", 10)

        # play again button
        if f > 220:
            bx, by, bw, bh = 72, 214, 112, 14
            hover = mouse_in_rect(bx, by, bw, bh)
            pyxel.rect(bx, by, bw, bh, 11 if hover else 1)
            pyxel.rectb(bx, by, bw, bh, 7)
            stext(bx + 14, by + 4, "PLAY AGAIN", 0 if hover else 11)

        draw_cursor(f)

    def handle_input(self):
        if self.frame > 220 and clicked():
            if mouse_in_rect(72, 214, 112, 14):
                return "new_game"
        if pyxel.btnp(pyxel.KEY_RETURN) and self.frame > 220:
            return "new_game"
        return None


class GameOverScene:
    """Game over — player ran out of coins."""

    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0

    def update(self):
        self.frame += 1

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        # red tinted background
        for y in range(0, 256, 8):
            for x in range(0, 256, 8):
                if (x + y + f) % 24 < 4:
                    pyxel.rect(x, y, 8, 8, 2)

        # panel
        if f > 10:
            pyxel.rect(30, 40, 196, 180, 0)
            pyxel.rectb(30, 40, 196, 180, 8)
            pyxel.rectb(32, 42, 192, 176, 2)

        if f > 30:
            stext(72, 52, "GAME OVER", 8)
            pyxel.line(72, 60, 184, 60, 8)

        if f > 50:
            stext(42, 72, "You ran out of coins!", 7)
            stext(42, 86, "Without funding, your", 6)
            stext(42, 96, "water treatment plant", 6)
            stext(42, 106, "had to shut down.", 6)

        if f > 80:
            stext(42, 122, "Millions still lack clean", 8)
            stext(42, 132, "water. Will you try again?", 8)

        # stats
        if f > 100:
            pyxel.line(42, 146, 214, 146, 5)
            jobs = self.game_state.get("jobs_done", 0)
            liters = self.game_state.get("total_liters", 0)
            stext(42, 152, f"Jobs completed: {jobs}", 7)
            stext(42, 162, f"Water purified: {liters}L", 7)

        # retry button
        if f > 120:
            bx, by, bw, bh = 72, 182, 112, 18
            hover = mouse_in_rect(bx, by, bw, bh)
            pyxel.rect(bx, by, bw, bh, 9 if hover else 1)
            pyxel.rectb(bx, by, bw, bh, 7)
            stext(bx + 14, by + 6, "TRY AGAIN", 0 if hover else 9)

            stext(42, 206, "Tip: Take contracts for", 5)
            stext(42, 214, "bigger payouts!", 5)

        draw_cursor(f)

    def handle_input(self):
        if self.frame > 120 and clicked():
            if mouse_in_rect(72, 182, 112, 18):
                return "new_game"
        if pyxel.btnp(pyxel.KEY_RETURN) and self.frame > 120:
            return "new_game"
        return None
