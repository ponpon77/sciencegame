import pyxel
import math
from data.pumps import PUMPS, PUMP_ORDER
from graphics.cursor import draw_cursor, clicked, mouse_in_rect
from graphics.ui import draw_coin_counter, stext


class ShopScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0
        self.owned = game_state.get("owned_pumps", {"bucket"})
        self.equipped = game_state.get("equipped_pump", "bucket")
        self.message = ""
        self.msg_timer = 0

    def update(self):
        self.frame += 1
        if self.msg_timer > 0:
            self.msg_timer -= 1

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        # header
        pyxel.rect(0, 0, 256, 20, 1)
        stext(4, 2, "PUMP SHOP", 10)
        stext(4, 10, "Click a pump to buy/equip. Click GO when ready.", 5)
        draw_coin_counter(180, 2, self.game_state.get("coins", 0), f)

        # pump cards
        y = 28
        for i, pid in enumerate(PUMP_ORDER):
            pump = PUMPS[pid]
            owned = pid in self.owned
            equipped = pid == self.equipped

            # card background
            bx, by, bw, bh = 12, y, 232, 44
            if equipped:
                pyxel.rect(bx, by, bw, bh, 1)
                pyxel.rectb(bx, by, bw, bh, 11)
            elif owned:
                pyxel.rect(bx, by, bw, bh, 1)
                pyxel.rectb(bx, by, bw, bh, 12)
            else:
                pyxel.rect(bx, by, bw, bh, 0)
                pyxel.rectb(bx, by, bw, bh, 5)

            # pump icon
            ix = bx + 6
            iy = by + 8
            col = pump["color"]
            if pid == "bucket":
                pyxel.rect(ix, iy, 12, 10, col)
                pyxel.rectb(ix, iy, 12, 10, 7)
                pyxel.line(ix + 2, iy - 2, ix + 10, iy - 2, col)
                pyxel.rect(ix + 1, iy + 4, 10, 5, 12)
            elif pid == "hand_pump":
                pyxel.rect(ix + 2, iy, 8, 16, col)
                pyxel.rectb(ix + 2, iy, 8, 16, 7)
                pyxel.rect(ix, iy - 2, 12, 3, 6)
                pyxel.rect(ix + 4, iy - 4, 4, 3, 6)
            elif pid == "electric_pump":
                pyxel.rect(ix, iy, 14, 12, col)
                pyxel.rectb(ix, iy, 14, 12, 7)
                pyxel.circ(ix + 7, iy + 6, 3, 7)
                pyxel.circ(ix + 7, iy + 6, 1, col)
                pyxel.rect(ix + 12, iy + 4, 4, 3, 6)
            elif pid == "industrial_pump":
                pyxel.rect(ix, iy, 16, 14, col)
                pyxel.rectb(ix, iy, 16, 14, 7)
                pyxel.rect(ix + 2, iy + 2, 5, 10, 3)
                pyxel.rect(ix + 9, iy + 2, 5, 10, 3)
                pyxel.rect(ix + 6, iy + 12, 4, 4, 6)

            # pump info
            tx = bx + 28
            stext(tx, by + 4, pump["name"], 7)
            if equipped:
                stext(tx + 78, by + 4, "[EQUIP]", 11)
            elif owned:
                stext(tx + 78, by + 4, "[OWNED]", 12)
            for j, line in enumerate(pump["desc"].split("\n")):
                stext(tx, by + 14 + j * 8, line, 6)

            # stats (right column, divider keeps it clear of the desc)
            sx = bx + 168
            pyxel.line(sx - 6, by + 2, sx - 6, by + bh - 2, 5)
            stext(sx, by + 4, f"Spd:{pump['collect_rate']}", 12)
            stext(sx, by + 14, f"Rad:{pump['radius']}px", 12)
            auto = "Yes" if pump["auto_collect"] else "No"
            stext(sx, by + 24, f"Auto:{auto}", 12)

            if not owned:
                stext(sx, by + 34, f"${pump['cost']}", 10)
            else:
                stext(sx, by + 34, "Equip", 5)

            # hover highlight
            if mouse_in_rect(bx, by, bw, bh):
                pyxel.rectb(bx - 1, by - 1, bw + 2, bh + 2, 7)

            y += 48

        # GO button
        go_x, go_y, go_w, go_h = 90, 224, 76, 20
        hover_go = mouse_in_rect(go_x, go_y, go_w, go_h)
        pyxel.rect(go_x, go_y, go_w, go_h, 11 if hover_go else 3)
        pyxel.rectb(go_x, go_y, go_w, go_h, 7)
        stext(go_x + 10, go_y + 7, "GO COLLECT!", 0 if hover_go else 7)

        # back button
        bk_x, bk_y, bk_w, bk_h = 12, 224, 60, 20
        hover_bk = mouse_in_rect(bk_x, bk_y, bk_w, bk_h)
        pyxel.rect(bk_x, bk_y, bk_w, bk_h, 5 if hover_bk else 1)
        pyxel.rectb(bk_x, bk_y, bk_w, bk_h, 6)
        stext(bk_x + 12, bk_y + 7, "BACK", 7)

        # message
        if self.msg_timer > 0:
            pyxel.rect(40, 248, 176, 8, 0)
            stext(42, 248, self.message, 10)

        # cursor on top
        draw_cursor(self.frame)

    def handle_input(self):
        if clicked():
            # check pump cards
            y = 28
            for i, pid in enumerate(PUMP_ORDER):
                bx, by, bw, bh = 12, y, 232, 44
                if mouse_in_rect(bx, by, bw, bh):
                    self._handle_pump_click(pid)
                    break
                y += 48

            # GO button
            if mouse_in_rect(90, 224, 76, 20):
                return "collection"

            # Back button
            if mouse_in_rect(12, 224, 60, 20):
                return "world_map"

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            return "world_map"
        if pyxel.btnp(pyxel.KEY_RETURN):
            return "collection"

        return None

    def _handle_pump_click(self, pid):
        pump = PUMPS[pid]
        if pid in self.owned:
            # equip it
            self.equipped = pid
            self.game_state["equipped_pump"] = pid
            self.message = f"Equipped {pump['name']}!"
            self.msg_timer = 60
            pyxel.play(2, 12)  # equip sound
        else:
            # try to buy
            coins = self.game_state.get("coins", 0)
            if coins >= pump["cost"]:
                self.game_state["coins"] -= pump["cost"]
                self.owned.add(pid)
                self.game_state["owned_pumps"] = self.owned
                self.equipped = pid
                self.game_state["equipped_pump"] = pid
                self.message = f"Bought & equipped {pump['name']}!"
                self.msg_timer = 60
                pyxel.play(1, 10)  # purchase coin clink
            else:
                self.message = f"Need {pump['cost']}! You have {coins}"
                self.msg_timer = 60
                pyxel.play(2, 11)  # can't afford buzz
