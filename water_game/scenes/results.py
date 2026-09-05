import pyxel
import math
import random
from engine.water_quality import CONTAMINANTS
from engine.filters import FILTERS
from engine.simulation import calculate_energy
from graphics.ui import draw_grade, draw_text_box, draw_coin_counter, stext
from graphics.sprites import draw_water_drop
from graphics.cursor import draw_cursor, clicked, mouse_in_rect
from data.levels import SDG6_FACTS
from data.contracts import grade_meets_minimum


class ResultsScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0
        self.water = game_state.get("result_water")
        self.input_water = game_state.get("water_sample")
        self.stages = game_state.get("stages", [])
        self.pipeline = game_state.get("pipeline", [])
        self.scroll_y = 0
        self.fact = random.choice(SDG6_FACTS)

        self.grade = self.water.get_grade() if self.water else "F"
        self.purity = self.water.get_purity_percent() if self.water else 0
        self.volume = self.water.volume_percent if self.water else 0

        # tycoon calculations (filters are buy-once, only energy costs per run)
        self.contract = game_state.get("active_contract")
        self.energy_cost = calculate_energy(self.pipeline) * 20

        self.contract_payout = 0
        self.bonus = 0
        self.rep_gain = 0
        self.contract_met = False

        if self.contract:
            meets_grade = grade_meets_minimum(self.grade, self.contract["min_grade"])
            meets_volume = self.volume >= self.contract["min_volume"]
            self.contract_met = meets_grade and meets_volume
            if self.contract_met:
                self.contract_payout = self.contract["payout"]
                self.rep_gain = self.contract["reputation"]
                if self.grade == "A":
                    self.bonus = self.contract.get("bonus_grade_a", 0)
        else:
            # freelance: smaller base pay
            grade_pay = {"A": 300, "B": 200, "C": 120, "D": 60, "F": 10}
            self.contract_payout = grade_pay.get(self.grade, 10)
            self.rep_gain = 1 if self.grade in ("A", "B") else 0

        self.total_income = self.contract_payout + self.bonus
        self.profit = self.total_income - self.energy_cost

        self.applied = False

    def update(self):
        self.frame += 1
        if not self.applied:
            self.game_state["coins"] = self.game_state.get("coins", 0) + self.profit
            self.game_state["reputation"] = self.game_state.get("reputation", 0) + self.rep_gain
            liters = int(self.purity * 10)
            self.game_state["total_liters"] = self.game_state.get("total_liters", 0) + liters
            self.game_state["total_earned"] = self.game_state.get("total_earned", 0) + max(0, self.profit)
            self.game_state["jobs_done"] = self.game_state.get("jobs_done", 0) + 1
            # track completed sources (Grade A or B = source purified)
            if self.grade in ("A", "B"):
                src = self.game_state.get("current_source", "")
                completed = self.game_state.setdefault("sources_completed", set())
                completed.add(src)
            self.applied = True

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        # header
        pyxel.rect(0, 0, 256, 14, 1)
        stext(4, 4, "FILTRATION RESULTS", 12)
        draw_coin_counter(180, 4, self.game_state.get("coins", 0), f)

        # grade + purity
        pyxel.rect(8, 18, 72, 48, 1)
        pyxel.rectb(8, 18, 72, 48, 12)
        stext(16, 20, "GRADE", 7)
        draw_grade(30, 30, self.grade, 2)
        stext(12, 52, f"{self.purity:.0f}% pure", 7)

        # water drop visual
        draw_water_drop(120, 28, 10, 12, f)
        vol_col = 11 if self.volume > 60 else (9 if self.volume > 40 else 8)
        stext(108, 46, f"Vol:{self.volume:.0f}%", vol_col)

        # contract status
        if self.contract:
            cx = 150
            pyxel.rect(cx, 18, 100, 48, 1)
            pyxel.rectb(cx, 18, 100, 48, 10 if self.contract_met else 8)
            stext(cx + 4, 20, self.contract["name"], 10 if self.contract_met else 8)
            status = "CONTRACT MET!" if self.contract_met else "FAILED"
            col = 11 if self.contract_met else 8
            stext(cx + 4, 30, status, col)
            stext(cx + 4, 40, f"Req: {self.contract['min_grade']}  Vol>{self.contract['min_volume']}%", 6)
            stext(cx + 4, 50, f"Pay: {self.contract['payout']}", 6)
        else:
            pyxel.rect(150, 18, 100, 48, 1)
            pyxel.rectb(150, 18, 100, 48, 5)
            stext(154, 20, "FREELANCE JOB", 6)
            stext(154, 32, "No contract", 5)
            stext(154, 42, "Pick contracts for", 5)
            stext(154, 50, "bigger payouts!", 5)

        # FINANCIAL SUMMARY (tycoon core)
        fy = 70
        pyxel.rect(8, fy, 240, 44, 1)
        pyxel.rectb(8, fy, 240, 44, 10)
        stext(12, fy + 2, "FINANCIAL SUMMARY", 10)

        stext(12, fy + 12, f"Contract payout:", 7)
        stext(130, fy + 12, f"+{self.contract_payout}", 11)

        if self.bonus > 0:
            stext(12, fy + 20, f"Grade A bonus:", 7)
            stext(130, fy + 20, f"+{self.bonus}", 11)

        stext(12, fy + 20 + (8 if self.bonus > 0 else 0), f"Energy costs:", 7)
        stext(130, fy + 20 + (8 if self.bonus > 0 else 0), f"-{self.energy_cost}", 8)

        # profit line
        profit_col = 11 if self.profit >= 0 else 8
        sign = "+" if self.profit >= 0 else ""
        stext(180, fy + 32, f"PROFIT: {sign}{self.profit}", profit_col)

        if self.rep_gain > 0:
            stext(12, fy + 36, f"+{self.rep_gain} Reputation", 12)

        # contaminant table
        ty = fy + 48
        pyxel.rect(8, ty, 240, 8, 1)
        stext(10, ty + 2, "CONTAMINANT", 12)
        stext(100, ty + 2, "BEFORE", 8)
        stext(140, ty + 2, "AFTER", 11)
        stext(180, ty + 2, "WHO", 6)
        stext(220, ty + 2, "OK?", 7)

        row_y = ty + 10 - self.scroll_y
        if self.input_water and self.water:
            for key in self.input_water.levels:
                if row_y < ty + 8:
                    row_y += 9
                    continue
                if row_y > 210:
                    break
                info = CONTAMINANTS.get(key, {})
                name = info.get("name", key)[:13]
                dec = info.get("decimals", 2)
                before = self.input_water.levels.get(key, 0)
                after = self.water.levels.get(key, 0)

                stext(10, row_y, name, 7)
                stext(100, row_y, f"{before:.{dec}f}", 8)
                stext(140, row_y, f"{after:.{dec}f}", 11)

                if key == "ph":
                    lo, hi = info.get("who_limit_low", 6.5), info.get("who_limit_high", 8.5)
                    safe = lo <= after <= hi
                    stext(180, row_y, f"{lo}-{hi}", 6)
                elif key == "chlorine":
                    lo, hi = info.get("who_target_low", 0.2), info.get("who_target_high", 0.5)
                    safe = lo <= after <= hi
                    stext(180, row_y, f"{lo}-{hi}", 6)
                else:
                    limit = info.get("who_limit", 999)
                    safe = after <= limit
                    stext(180, row_y, f"{limit}", 6)

                stext(224, row_y, "YES" if safe else "NO", 11 if safe else 8)
                row_y += 9

        # SDG6 fact (compact, single line)
        pyxel.rect(4, 214, 248, 16, 1)
        pyxel.rectb(4, 214, 248, 16, 3)
        stext(8, 216, "SDG6:", 11)
        fact_line = self.fact.split("\n")[0][:42]
        stext(38, 216, fact_line, 7)

        # buttons
        btn_y = 234

        # Continue button
        cb_x, cb_w, cb_h = 140, 80, 16
        hover_c = mouse_in_rect(cb_x, btn_y, cb_w, cb_h)
        pyxel.rect(cb_x, btn_y, cb_w, cb_h, 11 if hover_c else 3)
        pyxel.rectb(cb_x, btn_y, cb_w, cb_h, 7)
        stext(cb_x + 12, btn_y + 5, "CONTINUE", 0 if hover_c else 7)

        # Retry button
        rb_x, rb_w = 40, 60
        hover_r = mouse_in_rect(rb_x, btn_y, rb_w, cb_h)
        pyxel.rect(rb_x, btn_y, rb_w, cb_h, 9 if hover_r else 1)
        pyxel.rectb(rb_x, btn_y, rb_w, cb_h, 7)
        stext(rb_x + 14, btn_y + 5, "RETRY", 0 if hover_r else 9)

        draw_cursor(self.frame)

    def handle_input(self):
        # scroll with mouse wheel or keys
        if pyxel.btnp(pyxel.KEY_W):
            self.scroll_y = max(0, self.scroll_y - 10)
        if pyxel.btnp(pyxel.KEY_S):
            self.scroll_y += 10

        if clicked():
            if mouse_in_rect(140, 234, 80, 16):
                self.game_state["active_contract"] = None
                pyxel.play(2, 0)  # click
                return "world_map"
            if mouse_in_rect(40, 234, 60, 16):
                pyxel.play(2, 0)  # click
                return "lab"

        if pyxel.btnp(pyxel.KEY_RETURN):
            self.game_state["active_contract"] = None
            return "world_map"
        if pyxel.btnp(pyxel.KEY_ESCAPE):
            return "lab"
        return None
