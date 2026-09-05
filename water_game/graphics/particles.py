import pyxel
import random
import math


class Particle:
    __slots__ = ("x", "y", "vx", "vy", "life", "max_life", "color", "size")

    def __init__(self, x, y, vx, vy, life, color, size=1):
        self.x = x
        self.y = y
        self.vx = vx
        self.vy = vy
        self.life = life
        self.max_life = life
        self.color = color
        self.size = size


class ParticleSystem:
    def __init__(self, max_particles=200):
        self.particles = []
        self.max_particles = max_particles

    def emit(self, x, y, vx=0, vy=0, color=12, life=60, count=1, spread=1.0, size=1):
        for _ in range(count):
            if len(self.particles) >= self.max_particles:
                break
            p = Particle(
                x + random.uniform(-spread, spread),
                y + random.uniform(-spread, spread),
                vx + random.uniform(-0.3, 0.3),
                vy + random.uniform(-0.3, 0.3),
                life + random.randint(-10, 10),
                color,
                size,
            )
            self.particles.append(p)

    def update(self):
        alive = []
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.life -= 1
            if p.life > 0:
                alive.append(p)
        self.particles = alive

    def draw(self):
        for p in self.particles:
            alpha = p.life / p.max_life
            if alpha < 0.3:
                continue
            if p.size <= 1:
                pyxel.pset(int(p.x), int(p.y), p.color)
            else:
                pyxel.circ(int(p.x), int(p.y), p.size, p.color)

    def clear(self):
        self.particles.clear()


class WaterParticles:
    """Manages contaminant particles floating in a water region."""

    def __init__(self):
        self.dots = []

    def generate(self, x, y, w, h, contaminant_levels, max_dots=80):
        self.dots.clear()
        total = 0
        for key, val in contaminant_levels.items():
            if key in ("ph", "chlorine"):
                continue
            from engine.water_quality import CONTAMINANTS
            info = CONTAMINANTS.get(key, {})
            limit = info.get("who_limit", 100)
            if limit <= 0:
                limit = 1
            ratio = min(val / (limit * 5), 1.0)
            count = int(ratio * 12)
            color = _contaminant_color(key)
            for _ in range(count):
                if total >= max_dots:
                    break
                dx = random.uniform(x + 2, x + w - 2)
                dy = random.uniform(y + 2, y + h - 2)
                self.dots.append({
                    "x": dx, "y": dy,
                    "base_x": dx, "base_y": dy,
                    "color": color,
                    "speed": random.uniform(0.2, 0.8),
                    "phase": random.uniform(0, math.pi * 2),
                })
                total += 1

    def update(self, frame):
        for d in self.dots:
            d["x"] = d["base_x"] + math.sin(frame * 0.03 + d["phase"]) * 3
            d["y"] = d["base_y"] + math.cos(frame * 0.02 + d["phase"]) * 2

    def draw(self):
        for d in self.dots:
            pyxel.pset(int(d["x"]), int(d["y"]), d["color"])

    def remove_fraction(self, fraction):
        remove_count = int(len(self.dots) * fraction)
        if remove_count > 0 and self.dots:
            for _ in range(min(remove_count, len(self.dots))):
                idx = random.randint(0, len(self.dots) - 1)
                self.dots.pop(idx)


def _contaminant_color(key):
    colors = {
        "tds": 5,
        "turbidity": 4,
        "bacteria": 11,
        "heavy_metals": 6,
        "nitrates": 10,
        "pesticides": 2,
        "hardness": 15,
    }
    return colors.get(key, 5)
