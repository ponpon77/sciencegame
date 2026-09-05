import pyxel
import math
from engine.filters import FILTERS, FILTER_ORDER
from engine.simulation import run_filtration, calculate_energy
from engine.water_quality import CONTAMINANTS
from graphics.sprites import draw_filter_machine, draw_pipe, draw_tank
from graphics.animations import draw_lab_background, draw_bubbles
from graphics.particles import WaterParticles
from graphics.ui import draw_text_box, draw_coin_counter, stext
from graphics.cursor import draw_cursor, clicked, mouse_in_rect


STATE_SELECT = 0
STATE_RUNNING = 1
STATE_DONE = 2


class LabScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0
        self.state = STATE_SELECT

        self.available_filters = list(FILTER_ORDER)
        self.max_pipeline = 5

        # filters are bought once and kept forever
        self.owned = game_state.setdefault("owned_filters", set())

        # load saved pipeline from last run (filters are bought once, kept forever)
        saved = game_state.get("saved_pipeline", [])
        self.pipeline = []
        for fid in saved:
            if fid in FILTERS:
                self.pipeline.append(fid)
                self.owned.add(fid)  # anything saved was already paid for

        # filter upgrade levels
        self.upgrades = game_state.get("filter_upgrades", {})

        self.water = game_state.get("water_sample")
        self.result_water = None
        self.stages = []
        self.run_frame = 0
        self.run_stage = 0

        self.water_particles = WaterParticles()
        if self.water:
            self.water_particles.generate(10, 50, 50, 40, self.water.levels)

        self.show_stats = False
        self.hover_filter = None

    def update(self):
        self.frame += 1
        self.water_particles.update(self.frame)

        if self.state == STATE_RUNNING:
            self.run_frame += 1
            if self.run_frame % 40 == 0 and self.run_stage < len(self.stages) - 1:
                self.run_stage += 1
                self.water_particles.remove_fraction(0.3)
                pyxel.play(2, 1)  # bubble sound for each stage
            if self.run_stage >= len(self.stages) - 1 and self.run_frame > len(self.stages) * 40 + 20:
                self.state = STATE_DONE
                pyxel.play(1, 15)  # filtration complete ding

    def draw(self):
        pyxel.cls(0)
        f = self.frame

        draw_lab_background(f)

        # header
        pyxel.rect(0, 0, 256, 14, 0)
        stext(4, 2, "FILTRATION LAB", 12)
        if self.water:
            stext(80, 2, f"Source: {self.water.source_name}", 6)
        draw_coin_counter(190, 2, self.game_state.get("coins", 0), f)
        stext(4, 8, "Click filters to add. Click RUN when ready.", 5)

        if self.state == STATE_SELECT:
            self._draw_select(f)
        elif self.state == STATE_RUNNING:
            self._draw_running(f)
        elif self.state == STATE_DONE:
            self._draw_done(f)

        draw_cursor(f)

    def _draw_select(self, f):
        # input tank
        if self.water:
            dirty = 1.0 - self.water.get_purity_score()
            draw_tank(8, 48, 44, 36, 0.8, dirty, f)
            draw_bubbles(9, 49, 42, 34, f, 3)
            self.water_particles.draw()
            stext(10, 40, "INPUT", 7)

        # pipeline area
        pyxel.rect(58, 38, 138, 50, 0)
        pyxel.rectb(58, 38, 138, 50, 5)
        stext(60, 30, "PIPELINE (click to remove)", 6)

        for i in range(self.max_pipeline):
            sx = 62 + i * 26
            sy = 42
            bx, by, bw, bh = sx, sy, 22, 42

            if i < len(self.pipeline):
                fid = self.pipeline[i]
                hover = mouse_in_rect(bx, by, bw, bh)
                draw_filter_machine(sx + 3, sy + 2, fid, f)
                stext(sx, sy + 28, FILTERS[fid]["short"][:4], FILTERS[fid]["color"])
                # show upgrade stars
                lvl = self.game_state.get("filter_upgrades", {}).get(fid, 0)
                if lvl > 0:
                    stext(sx, sy + 36, "*" * lvl, 10)
                if hover:
                    pyxel.rectb(bx - 1, by - 1, bw + 2, bh + 2, 8)
                    stext(sx, sy - 6, "X", 8)
            else:
                pyxel.rectb(bx + 2, by + 2, bw - 4, bh - 8, 5)
                stext(sx + 6, sy + 16, "+", 5)

            if i < self.max_pipeline - 1 and i < len(self.pipeline):
                draw_pipe(sx + 22, sy + 14, sx + 26, sy + 14, f)

        # output tank
        draw_tank(202, 48, 44, 36, 0.0, 0.0, f)
        stext(204, 40, "OUTPUT", 7)

        # filter shop grid
        pyxel.rect(0, 94, 256, 106, 0)
        pyxel.rectb(0, 94, 256, 106, 5)
        stext(4, 96, "AVAILABLE FILTERS (click to add)", 10)

        self.hover_filter = None
        cols = 5
        for i, fid in enumerate(self.available_filters):
            fdata = FILTERS[fid]
            col_idx = i % cols
            row = i // cols
            bx = 2 + col_idx * 51
            by = 106 + row * 46
            bw, bh = 49, 42

            hover = mouse_in_rect(bx, by, bw, bh)
            if hover:
                self.hover_filter = fid

            bg = 5 if hover else 1
            pyxel.rect(bx, by, bw, bh, bg)
            pyxel.rectb(bx, by, bw, bh, fdata["color"] if hover else 5)

            draw_filter_machine(bx + 2, by + 2, fid, f)
            stext(bx + 18, by + 2, fdata["short"][:5], fdata["color"])
            if fid in self.owned:
                stext(bx + 18, by + 10, "OWNED", 11)
            else:
                stext(bx + 18, by + 10, f"${fdata['cost']}", 10)

            # show pH/chlorine effect if present
            if fdata["ph_adjust"] != 0:
                sign = "+" if fdata["ph_adjust"] > 0 else ""
                stext(bx + 18, by + 18, f"pH{sign}{fdata['ph_adjust']}", 7)
            elif fdata["adds_chlorine"] > 0:
                stext(bx + 18, by + 18, f"+Cl", 11)
            else:
                stext(bx + 18, by + 18, f"E:{fdata['energy']}", 9)

            rem_keys = list(fdata["removal"].keys())[:2]
            for j, rk in enumerate(rem_keys):
                lo, hi = fdata["removal"][rk]
                pct = int((lo + hi) / 2 * 100)
                stext(bx + 2, by + 26 + j * 7, f"{rk[:4]}-{pct}%", 6)

        # bottom bar: costs + buttons
        pyxel.rect(0, 200, 256, 56, 0)

        total_energy = calculate_energy(self.pipeline)
        energy_cost = total_energy * 20
        coins = self.game_state.get("coins", 0)

        contract = self.game_state.get("active_contract")
        if contract:
            stext(4, 202, f"Contract: {contract['name']}", 10)
            stext(130, 202, f"Pay:{contract['payout']} Need:{contract['min_grade']}", 11)
        else:
            stext(4, 202, "Freelance (pick contract for more pay)", 5)

        stext(4, 212, f"Energy cost per run: {energy_cost}  (filters owned)", 9)
        stext(4, 220, f"Budget: {coins}", 10)

        # RUN button
        run_x, run_y, run_w, run_h = 170, 214, 76, 18
        can_run = len(self.pipeline) > 0 and self.water
        hover_run = mouse_in_rect(run_x, run_y, run_w, run_h) and can_run
        pyxel.rect(run_x, run_y, run_w, run_h, 11 if hover_run else (3 if can_run else 1))
        pyxel.rectb(run_x, run_y, run_w, run_h, 7 if hover_run else 5)
        stext(run_x + 6, run_y + 6, "RUN FILTER", 0 if hover_run else (7 if can_run else 5))

        # UPGRADE button
        up_x, up_y, up_w, up_h = 60, 236, 70, 14
        can_upgrade = len(self.pipeline) > 0
        hover_up = mouse_in_rect(up_x, up_y, up_w, up_h) and can_upgrade
        pyxel.rect(up_x, up_y, up_w, up_h, 10 if hover_up else (1 if can_upgrade else 0))
        pyxel.rectb(up_x, up_y, up_w, up_h, 7 if hover_up else 5)
        stext(up_x + 6, up_y + 4, "UPGRADE", 0 if hover_up else (10 if can_upgrade else 5))
        if can_upgrade:
            fid = self.pipeline[-1]
            lvl = self.game_state.get("filter_upgrades", {}).get(fid, 0)
            if lvl < 3:
                ucost = FILTERS[fid]["cost"] * (lvl + 1)
                stext(up_x, up_y - 8, f"Lv{lvl}>{ucost}", 6)
            else:
                stext(up_x, up_y - 8, "MAX!", 11)

        # STATS button
        st_x, st_y = 170, 236
        hover_st = mouse_in_rect(st_x, st_y, 76, 14)
        pyxel.rect(st_x, st_y, 76, 14, 12 if hover_st else 1)
        pyxel.rectb(st_x, st_y, 76, 14, 7)
        stext(st_x + 10, st_y + 4, "VIEW STATS", 0 if hover_st else 12)

        # BACK button
        bk_x, bk_y = 4, 236
        hover_bk = mouse_in_rect(bk_x, bk_y, 50, 14)
        pyxel.rect(bk_x, bk_y, 50, 14, 5 if hover_bk else 1)
        pyxel.rectb(bk_x, bk_y, 50, 14, 6)
        stext(bk_x + 14, bk_y + 4, "BACK", 7)

        # stats overlay
        if self.show_stats and self.water:
            self._draw_stats_overlay()

    def _draw_running(self, f):
        pyxel.rect(20, 20, 216, 200, 0)
        pyxel.rectb(20, 20, 216, 200, 12)
        stext(80, 24, "RUNNING FILTRATION", 12)

        stage_count = len(self.stages)
        spacing = 200 // max(stage_count, 1)
        for i, stage in enumerate(self.stages):
            sx = 30 + i * spacing
            sy = 50
            active = (i <= self.run_stage)
            col = 12 if active else 5

            if i == 0:
                stext(sx, sy, "IN", col)
            elif "filter_id" in stage:
                draw_filter_machine(sx, sy + 10, stage["filter_id"], f if active else 0)
                stext(sx, sy, stage["label"][:6], col)
            if i < stage_count - 1:
                nx = 30 + (i + 1) * spacing
                pipe_col = 12 if i < self.run_stage else 5
                draw_pipe(sx + 16, sy + 22, nx, sy + 22, f if active else 0, pipe_col)

            if i == self.run_stage and self.state == STATE_RUNNING:
                stext(sx + 4, sy + 40, ">>>", 10 if f % 10 < 5 else 0)

        if self.run_stage < len(self.stages):
            sd = self.stages[min(self.run_stage, len(self.stages) - 1)]
            levels = sd["levels"]
            vol = sd.get("volume", 100)
            ly = 110
            stext(30, ly, f"Stage: {sd['label']}", 7)
            stext(30, ly + 8, f"Volume: {vol:.0f}%", 12)
            ly += 18
            for key in ["turbidity", "bacteria", "tds", "heavy_metals", "nitrates", "pesticides"]:
                if key in levels:
                    info = CONTAMINANTS[key]
                    val = levels[key]
                    limit = info.get("who_limit", 100)
                    safe = val <= limit
                    c = 11 if safe else 8
                    stext(30, ly, f"{info['name'][:16]}: {val:.1f}", c)
                    ly += 8

        self.water_particles.draw()

    def _draw_done(self, f):
        pyxel.rect(40, 80, 176, 50, 0)
        pyxel.rectb(40, 80, 176, 50, 11)
        stext(60, 90, "FILTRATION COMPLETE!", 11)

        # results button
        rb_x, rb_y, rb_w, rb_h = 70, 106, 116, 18
        hover = mouse_in_rect(rb_x, rb_y, rb_w, rb_h)
        pyxel.rect(rb_x, rb_y, rb_w, rb_h, 11 if hover else 3)
        pyxel.rectb(rb_x, rb_y, rb_w, rb_h, 7)
        stext(rb_x + 14, rb_y + 6, "VIEW RESULTS", 0 if hover else 7)

    def _draw_stats_overlay(self):
        pyxel.rect(20, 20, 216, 200, 0)
        pyxel.rectb(20, 20, 216, 200, 12)
        stext(24, 24, "WATER ANALYSIS (click to close)", 12)

        y = 36
        for key, val in self.water.levels.items():
            info = CONTAMINANTS.get(key, {})
            name = info.get("name", key)[:20]
            unit = info.get("unit", "")
            if key == "ph":
                lo, hi = info.get("who_limit_low", 6.5), info.get("who_limit_high", 8.5)
                safe = lo <= val <= hi
                limit_str = f"{lo}-{hi}"
            elif key == "chlorine":
                lo, hi = info.get("who_target_low", 0.2), info.get("who_target_high", 0.5)
                safe = lo <= val <= hi
                limit_str = f"{lo}-{hi}"
            else:
                limit = info.get("who_limit", 999)
                safe = val <= limit
                limit_str = str(limit)

            col = 11 if safe else 8
            dec = info.get("decimals", 2)
            stext(24, y, name, 7)
            stext(130, y, f"{val:.{dec}f} {unit}", col)
            stext(200, y, f"[{limit_str}]", 6)
            y += 9

    def handle_input(self):
        if self.state == STATE_SELECT:
            return self._handle_select_input()
        elif self.state == STATE_DONE:
            if clicked() and mouse_in_rect(70, 106, 116, 18):
                return "results"
            if pyxel.btnp(pyxel.KEY_RETURN):
                return "results"
        return None

    def _handle_select_input(self):
        # stats toggle
        if self.show_stats:
            if clicked():
                self.show_stats = False
            return None

        if clicked():
            # pipeline slots (click to remove). No refund: the filter is
            # owned forever, removing just takes it out of this run's pipeline.
            for i in range(min(len(self.pipeline), self.max_pipeline)):
                sx = 62 + i * 26
                if mouse_in_rect(sx, 42, 22, 42):
                    self.pipeline.pop(i)
                    pyxel.play(2, 13)  # remove sound
                    return None

            # filter grid (click to add)
            cols = 5
            for i, fid in enumerate(self.available_filters):
                col_idx = i % cols
                row = i // cols
                bx = 2 + col_idx * 51
                by = 106 + row * 46
                if mouse_in_rect(bx, by, 49, 42):
                    if len(self.pipeline) < self.max_pipeline:
                        cost = FILTERS[fid]["cost"]
                        if fid in self.owned:
                            # already bought - add for free
                            self.pipeline.append(fid)
                            pyxel.play(2, 12)  # add filter sound
                        elif self.game_state.get("coins", 0) >= cost:
                            self.pipeline.append(fid)
                            self.game_state["coins"] -= cost
                            self.owned.add(fid)
                            self.game_state["owned_filters"] = self.owned
                            pyxel.play(1, 10)  # purchase coin clink
                        else:
                            pyxel.play(2, 11)  # can't afford
                    else:
                        pyxel.play(2, 21)  # pipeline full
                    return None

            # RUN button
            if mouse_in_rect(170, 214, 76, 18) and self.pipeline and self.water:
                self._run_filtration()
                pyxel.play(1, 14)  # filtration running sound
                return None

            # STATS button
            if mouse_in_rect(170, 236, 76, 14):
                self.show_stats = True
                pyxel.play(3, 0)  # click
                return None

            # UPGRADE button
            if mouse_in_rect(60, 236, 70, 14):
                self._try_upgrade()
                return None

            # BACK button
            if mouse_in_rect(4, 236, 50, 14):
                self._save_pipeline()
                return "world_map"

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            self._save_pipeline()
            return "world_map"

        if pyxel.btnp(pyxel.KEY_R) and self.pipeline and self.water:
            self._run_filtration()

        return None

    def _run_filtration(self):
        """Run the filtration and save pipeline for reuse."""
        self.result_water = self.water.copy()
        self.result_water, self.stages = run_filtration(
            self.result_water, self.pipeline,
            self.game_state.get("filter_uses", {}),
            self.game_state.get("filter_upgrades", {}),
        )
        self.game_state["result_water"] = self.result_water
        self.game_state["stages"] = self.stages
        self.game_state["pipeline"] = list(self.pipeline)
        self.game_state["saved_pipeline"] = list(self.pipeline)
        self.state = STATE_RUNNING
        self.run_frame = 0
        self.run_stage = 0

    def _save_pipeline(self):
        """Save the pipeline setup (filters are kept forever once bought)."""
        self.game_state["saved_pipeline"] = list(self.pipeline)

    def _try_upgrade(self):
        """Upgrade the hovered or last pipeline filter (boost efficiency)."""
        if not self.pipeline:
            return
        # upgrade last filter in pipeline
        fid = self.pipeline[-1]
        upgrades = self.game_state.get("filter_upgrades", {})
        level = upgrades.get(fid, 0)
        if level >= 3:
            pyxel.play(2, 11)  # already max
            return
        cost = FILTERS[fid]["cost"] * (level + 1)  # cost scales with level
        if self.game_state.get("coins", 0) >= cost:
            self.game_state["coins"] -= cost
            upgrades[fid] = level + 1
            self.game_state["filter_upgrades"] = upgrades
            pyxel.play(1, 16)  # upgrade power-up sound
        else:
            pyxel.play(2, 11)  # can't afford
