import random


CONTAMINANTS = {
    "tds": {"name": "Total Dissolved Solids", "unit": "mg/L", "who_limit": 500, "decimals": 0},
    "turbidity": {"name": "Turbidity", "unit": "NTU", "who_limit": 1, "decimals": 1},
    "bacteria": {"name": "E. coli Bacteria", "unit": "CFU/100mL", "who_limit": 0, "decimals": 0},
    "heavy_metals": {"name": "Heavy Metals", "unit": "µg/L", "who_limit": 10, "decimals": 1},
    "nitrates": {"name": "Nitrates", "unit": "mg/L", "who_limit": 50, "decimals": 1},
    "pesticides": {"name": "Pesticides/VOCs", "unit": "µg/L", "who_limit": 0.5, "decimals": 2},
    "hardness": {"name": "Hardness (Ca/Mg)", "unit": "mg/L", "who_limit": 300, "decimals": 0},
    "ph": {"name": "pH", "unit": "", "who_limit_low": 6.5, "who_limit_high": 8.5, "decimals": 1},
    "chlorine": {"name": "Chlorine Residual", "unit": "mg/L", "who_target_low": 0.2, "who_target_high": 0.5, "decimals": 2},
}


class WaterSample:
    def __init__(self, source_name="Unknown", levels=None):
        self.source_name = source_name
        self.levels = levels or {}
        self.volume_percent = 100.0
        self.history = []

    def copy(self):
        w = WaterSample(self.source_name, dict(self.levels))
        w.volume_percent = self.volume_percent
        w.history = list(self.history)
        return w

    def snapshot(self):
        return dict(self.levels)

    def get_purity_score(self):
        score = 0
        total = 0
        for key, val in self.levels.items():
            if key == "ph":
                low = CONTAMINANTS["ph"]["who_limit_low"]
                high = CONTAMINANTS["ph"]["who_limit_high"]
                if low <= val <= high:
                    score += 1
                total += 1
            elif key == "chlorine":
                low = CONTAMINANTS["chlorine"]["who_target_low"]
                high = CONTAMINANTS["chlorine"]["who_target_high"]
                if low <= val <= high:
                    score += 1
                elif val < low:
                    score += 0.5
                total += 1
            else:
                limit = CONTAMINANTS[key]["who_limit"]
                if val <= limit:
                    score += 1
                elif val <= limit * 2:
                    score += 0.5
                total += 1
        if total == 0:
            return 0
        return score / total

    def get_grade(self):
        p = self.get_purity_score()
        violations = self.count_violations()
        if violations == 0 and p >= 0.95:
            return "A"
        elif violations <= 1 and p >= 0.8:
            return "B"
        elif violations <= 3 and p >= 0.6:
            return "C"
        elif p >= 0.4:
            return "D"
        return "F"

    def count_violations(self):
        count = 0
        for key, val in self.levels.items():
            if key == "ph":
                low = CONTAMINANTS["ph"]["who_limit_low"]
                high = CONTAMINANTS["ph"]["who_limit_high"]
                if val < low or val > high:
                    count += 1
            elif key == "chlorine":
                continue
            else:
                if val > CONTAMINANTS[key]["who_limit"]:
                    count += 1
        return count

    def get_purity_percent(self):
        return self.get_purity_score() * 100

    def is_safe(self):
        return self.get_grade() == "A"


def generate_water(source_profile):
    levels = {}
    for key, (low, high) in source_profile.items():
        levels[key] = round(random.uniform(low, high), CONTAMINANTS.get(key, {}).get("decimals", 2))
    return levels
