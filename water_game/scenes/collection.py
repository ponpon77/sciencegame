import pyxel
import math
import random
from data.levels import WATER_SOURCES
from data.pumps import PUMPS, PUMP_ORDER
from engine.water_quality import WaterSample, generate_water
from graphics.particles import ParticleSystem
from graphics.animations import draw_water_surface, draw_bubbles
from graphics.cursor import (
    draw_cursor_bucket, draw_cursor_pump,
    mouse_in_circle, clicked, holding, mouse_in_rect,
)
from graphics.ui import draw_coin_counter, stext


class CollectionScene:
    def __init__(self, game_state):
        self.game_state = game_state
        self.frame = 0
        self.water_collected = 0.0
        self.target = 100.0
        self.hazards = []
        self.collectibles = []
        self.particles = ParticleSystem(120)
        self.done = False
        self.countdown = 0
        self.hit_flash = 0

        # pump system
        self.pump_id = game_state.get("equipped_pump", "bucket")
        self.pump = PUMPS[self.pump_id]

        self._init_level()

    def _init_level(self):
        src_id = self.game_state.get("current_source", "river")
        self.source = WATER_SOURCES[src_id]
        # spawn hazards
        self.hazards = []
        for _ in range(6 + self.source["difficulty"] * 2):
            self.hazards.append({
                "x": random.randint(20, 236),
                "y": random.randint(165, 245),
                "type": random.choice(["trash", "oil", "sewage"]),
                "vx": random.uniform(-0.4, 0.4),
                "vy": random.uniform(-0.1, 0.1),
            })
        # spawn water drops to collect
        self.collectibles = []
        for _ in range(20):
            self.collectibles.append({
                "x": random.randint(15, 241),
                "y": random.randint(162, 248),
                "collected": False,
                "phase": random.uniform(0, math.pi * 2),
            })

    def update(self):
        self.frame += 1
        self.particles.update()

        if self.hit_flash > 0:
            self.hit_flash -= 1

        if self.done:
            self.countdown += 1
            return

        mx = pyxel.mouse_x
        my = pyxel.mouse_y
        pump = self.pump
        radius = pump["radius"]
        rate = pump["collect_rate"]
        is_clicking = clicked()
        is_holding = holding()

        # auto-collect pumps work on hold, manual pumps on click
        do_collect = False
        if pump["auto_collect"]:
            do_collect = is_holding
        else:
            do_collect = is_clicking

        if do_collect:
            # collect water drops near cursor
            for c in self.collectibles:
                if c["collected"]:
                    continue
                if mouse_in_circle(c["x"], c["y"], radius):
                    c["collected"] = True
                    self.water_collected += rate
                    # play collect sound (alternate channels to avoid cutting off)
                    if self.frame % 6 < 3:
                        pyxel.play(1, 8)
                    else:
                        pyxel.play(2, 8)
                    self.particles.emit(
                        c["x"], c["y"],
                        vx=0, vy=-1.5,
                        color=12, life=25, count=6, spread=3,
                    )

            # check hazard collision with cursor area
            for h in self.hazards:
                if mouse_in_circle(h["x"], h["y"], radius // 2):
                    self.water_collected = max(0, self.water_collected - rate * 0.5)
                    self.hit_flash = 8
                    pyxel.play(3, 9)  # hazard hit sound
                    self.particles.emit(
                        h["x"], h["y"],
                        vy=-0.5, color=8, life=15, count=4, spread=2,
                    )

        # move hazards
        for h in self.hazards:
            h["x"] += h["vx"]
            h["y"] += h["vy"]
            if h["x"] < 5 or h["x"] > 250:
                h["vx"] = -h["vx"]
            if h["y"] < 162 or h["y"] > 248:
                h["vy"] = -h["vy"]

        # respawn collected drops after a delay
        if self.frame % 60 == 0:
            for c in self.collectibles:
                if c["collected"]:
                    c["collected"] = False
                    c["x"] = random.randint(15, 241)
                    c["y"] = random.randint(162, 248)
                    break  # only respawn one per tick

        if self.water_collected >= self.target and not self.done:
            self.done = True
            pyxel.play(1, 18)  # collection complete splash

    def draw(self):
        pyxel.cls(0)
        f = self.frame
        src = self.source

        # sky gradient
        pyxel.rect(0, 18, 256, 60, 1)
        pyxel.rect(0, 78, 256, 40, 1)
        # clouds
        for i in range(4):
            cx = (40 + i * 70 + f // 3) % 280 - 20
            pyxel.elli(cx, 40 + i * 12, 30, 10, 7)
            pyxel.elli(cx + 8, 36 + i * 12, 20, 8, 6)

        # ground/bank
        pyxel.rect(0, 118, 256, 44, 3)
        for x in range(0, 256, 6):
            h_var = int(math.sin(x * 0.12) * 3)
            pyxel.rect(x, 115 + h_var, 6, 6, 3)
        # grass details
        for i in range(30):
            gx = (i * 9) % 256
            pyxel.line(gx, 120, gx - 1, 117, 11)
            pyxel.line(gx + 3, 122, gx + 2, 118, 3)

        # water body
        water_col = src["color"]
        pyxel.rect(0, 158, 256, 98, water_col)
        # lighter water band
        pyxel.rect(0, 158, 256, 6, 12)
        draw_water_surface(0, 156, 256, f, 12)
        draw_bubbles(0, 165, 256, 85, f, 10)

        # collectible water drops (glow when near cursor)
        mx, my = pyxel.mouse_x, pyxel.mouse_y
        for c in self.collectibles:
            if c["collected"]:
                continue
            bob = math.sin(f * 0.06 + c["phase"]) * 2.5
            cx, cy = int(c["x"]), int(c["y"] + bob)
            near = (mx - cx) ** 2 + (my - cy) ** 2 < self.pump["radius"] ** 2
            # glow ring if near
            if near:
                pyxel.circb(cx, cy, 5, 7)
            # drop
            pyxel.circ(cx, cy, 3, 12)
            pyxel.tri(cx - 2, cy, cx + 2, cy, cx, cy - 4, 12)
            pyxel.pset(cx - 1, cy - 1, 7)  # highlight

        # hazards
        for h in self.hazards:
            hx, hy = int(h["x"]), int(h["y"])
            if h["type"] == "trash":
                pyxel.rect(hx - 3, hy - 3, 7, 6, 5)
                pyxel.rectb(hx - 3, hy - 3, 7, 6, 6)
                stext(hx - 1, hy - 2, "X", 8)
            elif h["type"] == "oil":
                pyxel.elli(hx - 5, hy - 3, 10, 6, 0)
                pyxel.elli(hx - 3, hy - 1, 6, 3, 2)
            elif h["type"] == "sewage":
                pyxel.circ(hx, hy, 4, 4)
                pyxel.circ(hx, hy, 2, 2)
                pyxel.pset(hx, hy, 9)

        self.particles.draw()

        # flash screen edge on hazard hit
        if self.hit_flash > 0:
            pyxel.rectb(0, 18, 256, 238, 8)
            pyxel.rectb(1, 19, 254, 236, 8)

        # draw custom cursor (on top of everything)
        if self.pump_id == "bucket":
            draw_cursor_bucket(f)
        else:
            draw_cursor_pump(f)

        # === UI OVERLAY (top bar) ===
        pyxel.rect(0, 0, 256, 18, 0)
        stext(4, 2, f"Water: {int(self.water_collected)}/{int(self.target)}", 12)

        # progress bar
        bar_x, bar_w = 80, 90
        pyxel.rect(bar_x, 2, bar_w, 6, 1)
        fill_w = int(bar_w * min(self.water_collected / self.target, 1.0))
        pyxel.rect(bar_x, 2, fill_w, 6, 12)
        pyxel.rectb(bar_x, 2, bar_w, 6, 5)

        draw_coin_counter(180, 2, self.game_state.get("coins", 0), f)

        stext(4, 10, src["name"], src["color"])
        click_word = "Hold" if self.pump["auto_collect"] else "Click"
        stext(80, 10, f"{click_word} water! Pump:{self.pump['name']}", 5)

        # done overlay
        if self.done:
            pyxel.rect(50, 90, 156, 40, 0)
            pyxel.rectb(50, 90, 156, 40, 11)
            stext(66, 98, "WATER COLLECTED!", 11)
            stext(56, 110, "Click to go to the lab...", 7 if f % 30 < 20 else 0)

    def handle_input(self):
        if self.done:
            if clicked() or self.countdown > 120:
                src_id = self.game_state.get("current_source", "river")
                levels = generate_water(self.source["profile"])
                self.game_state["water_sample"] = WaterSample(self.source["name"], levels)
                return "lab"

        if pyxel.btnp(pyxel.KEY_ESCAPE):
            return "world_map"
        return None
