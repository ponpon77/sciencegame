import pyxel
import math
from data.levels import WATER_SOURCES, SOURCE_ORDER
from data.contracts import CONTRACTS, grade_meets_minimum
from graphics.sprites import draw_map_node
from graphics.ui import draw_text_box, draw_coin_counter
from graphics.cursor import draw_cursor, clicked, mouse_in_rect, mouse_in_circle
from graphics.ui import stext


class WorldMapScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.selected = 0
        self.frame = 0
        self.panel = "sources"  # "sources" or "contracts"
        self.contract_cursor = 0

    def update(self):
        self.frame += 1
        # auto-select source on hover
        if self.panel == "sources":
            for i, src_id in enumerate(SOURCE_ORDER):
                src = WATER_SOURCES[src_id]
                mx, my = src["map_pos"]
                if mouse_in_circle(mx, my, 12):
                    self.selected = i

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        if self.panel == "sources":
            self._draw_source_select(f)
        else:
            self._draw_contract_select(f)

        draw_cursor(f)

    def _draw_source_select(self, f):
        # map background
        pyxel.rect(0, 18, 256, 200, 1)
        pyxel.rect(30, 38, 200, 170, 3)
        for i in range(20):
            rx = 60 + int(math.sin(i * 0.4 + f * 0.01) * 15)
            ry = 50 + i * 8
            pyxel.line(rx, ry, rx + 8, ry + 4, 12)

        # header
        pyxel.rect(0, 0, 256, 18, 0)
        stext(4, 2, "SELECT WATER SOURCE", 12)
        draw_coin_counter(130, 2, self.game_state.get("coins", 0), f)
        rep = self.game_state.get("reputation", 0)
        stext(190, 2, f"REP:{rep}", 11)
        done = len(self.game_state.get("sources_completed", set()))
        total = len(SOURCE_ORDER)
        stext(190, 10, f"{done}/{total} done", 11 if done > 0 else 5)
        stext(4, 10, "Click source. Right buttons for contracts/shop.", 5)

        # draw map nodes
        completed = self.game_state.get("sources_completed", set())
        for i, src_id in enumerate(SOURCE_ORDER):
            src = WATER_SOURCES[src_id]
            mx, my = src["map_pos"]
            locked = not self._is_unlocked(src_id)
            sel = (i == self.selected)
            draw_map_node(mx, my, src["name"], src["color"], sel, locked, f)
            # show checkmark for completed sources
            if src_id in completed:
                pyxel.circ(mx + 10, my - 10, 4, 11)
                stext(mx + 8, my - 12, "v", 0)

        # connections
        for i in range(len(SOURCE_ORDER) - 1):
            s1 = WATER_SOURCES[SOURCE_ORDER[i]]
            s2 = WATER_SOURCES[SOURCE_ORDER[i + 1]]
            pyxel.line(s1["map_pos"][0], s1["map_pos"][1],
                       s2["map_pos"][0], s2["map_pos"][1], 5)

        # info panel
        src_id = SOURCE_ORDER[self.selected]
        src = WATER_SOURCES[src_id]
        locked = not self._is_unlocked(src_id)
        if locked:
            info = f"LOCKED - Cost: {src['unlock_cost']}\nClick to unlock"
        else:
            info = src["desc"] + f"\nDifficulty: {'*' * src['difficulty']}"
        draw_text_box(4, 218, 180, 34, info, src["name"], f)

        # side buttons
        # contracts button
        cb_x, cb_y, cb_w, cb_h = 192, 220, 58, 14
        hover_c = mouse_in_rect(cb_x, cb_y, cb_w, cb_h)
        pyxel.rect(cb_x, cb_y, cb_w, cb_h, 10 if hover_c else 1)
        pyxel.rectb(cb_x, cb_y, cb_w, cb_h, 7 if hover_c else 10)
        stext(cb_x + 4, cb_y + 4, "CONTRACTS", 0 if hover_c else 10)

        # shop button
        sb_x, sb_y = 192, 238
        hover_s = mouse_in_rect(sb_x, sb_y, cb_w, cb_h)
        pyxel.rect(sb_x, sb_y, cb_w, cb_h, 9 if hover_s else 1)
        pyxel.rectb(sb_x, sb_y, cb_w, cb_h, 7 if hover_s else 9)
        stext(sb_x + 6, sb_y + 4, "PUMP SHOP", 0 if hover_s else 9)

        # active contract display
        contract = self.game_state.get("active_contract")
        if contract:
            stext(192, 210, f"Job:{contract['name'][:8]}", 10)

    def _draw_contract_select(self, f):
        pyxel.rect(0, 0, 256, 18, 0)
        stext(4, 2, "AVAILABLE CONTRACTS", 10)
        draw_coin_counter(140, 2, self.game_state.get("coins", 0), f)
        stext(4, 10, "Click a contract to accept. Click BACK to return.", 5)

        y = 22
        for i, c in enumerate(CONTRACTS):
            bx, by, bw, bh = 8, y, 240, 34
            hover = mouse_in_rect(bx, by, bw, bh)
            bg = 5 if hover else 1
            border = 10 if hover else 5

            pyxel.rect(bx, by, bw, bh, bg)
            pyxel.rectb(bx, by, bw, bh, border)

            pyxel.circ(20, y + 17, 6, c["icon_color"])
            stext(18, y + 15, "C", 0)

            stext(32, y + 4, c["name"], 7)
            stext(32, y + 12, c["desc"].split("\n")[0], 6)
            stext(32, y + 22, f"Min: Grade {c['min_grade']}  Vol: {c['min_volume']}%", 6)

            stext(180, y + 4, f"{c['payout']}", 10)
            if c["bonus_grade_a"] > 0:
                stext(180, y + 12, f"+{c['bonus_grade_a']} A", 11)
            stext(180, y + 22, f"+{c['reputation']} REP", 12)

            y += 38

        # back button
        bk_x, bk_y, bk_w, bk_h = 100, 252 - 16, 56, 14
        hover_bk = mouse_in_rect(bk_x, bk_y, bk_w, bk_h)
        pyxel.rect(bk_x, bk_y, bk_w, bk_h, 5 if hover_bk else 1)
        pyxel.rectb(bk_x, bk_y, bk_w, bk_h, 7)
        stext(bk_x + 14, bk_y + 4, "BACK", 7)

    def handle_input(self):
        if self.panel == "sources":
            return self._handle_source_input()
        else:
            return self._handle_contract_input()

    def _handle_source_input(self):
        if clicked():
            # check map nodes
            for i, src_id in enumerate(SOURCE_ORDER):
                src = WATER_SOURCES[src_id]
                mx, my = src["map_pos"]
                if mouse_in_circle(mx, my, 12):
                    if self._is_unlocked(src_id):
                        self.game_state["current_source"] = src_id
                        pyxel.play(2, 0)  # click
                        return "shop"
                    elif self.game_state.get("coins", 0) >= src["unlock_cost"]:
                        self.game_state["coins"] -= src["unlock_cost"]
                        self.game_state.setdefault("unlocked", set()).add(src_id)
                        pyxel.play(1, 19)  # unlock reveal sound

            # contracts button
            if mouse_in_rect(192, 220, 58, 14):
                self.panel = "contracts"

            # shop button
            if mouse_in_rect(192, 238, 58, 14):
                src_id = SOURCE_ORDER[self.selected]
                if self._is_unlocked(src_id):
                    self.game_state["current_source"] = src_id
                    return "shop"

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            return "title"
        if pyxel.btnp(pyxel.KEY_Q):
            pyxel.quit()
        return None

    def _handle_contract_input(self):
        if clicked():
            # check contract cards
            y = 22
            for i, c in enumerate(CONTRACTS):
                if mouse_in_rect(8, y, 240, 34):
                    self.game_state["active_contract"] = c
                    self.panel = "sources"
                    pyxel.play(1, 17)  # contract accept
                    return None
                y += 38
            # back button
            if mouse_in_rect(100, 252 - 16, 56, 14):
                self.panel = "sources"

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self.panel = "sources"
        return None

    def _is_unlocked(self, src_id):
        src = WATER_SOURCES[src_id]
        if src["unlock_cost"] == 0:
            return True
        return src_id in self.game_state.get("unlocked", set())
