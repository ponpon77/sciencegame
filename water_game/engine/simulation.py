import random
from engine.filters import FILTERS


def run_filtration(water, pipeline, filter_uses=None, filter_upgrades=None):
    """Run water through a pipeline of filter IDs. Returns (result_water, stage_snapshots).
    filter_upgrades: dict of {filter_id: upgrade_level (0-3)} boosting efficiency."""
    if filter_uses is None:
        filter_uses = {}
    if filter_upgrades is None:
        filter_upgrades = {}

    stages = []
    stages.append({"label": "Input", "levels": water.snapshot(), "volume": water.volume_percent})

    for fid in pipeline:
        fdata = FILTERS[fid]
        use_count = filter_uses.get(fid, 0)
        upgrade_level = filter_upgrades.get(fid, 0)

        for contaminant, (lo, hi) in fdata["removal"].items():
            if contaminant not in water.levels:
                continue

            base_rate = random.uniform(lo, hi)

            # Upgrade bonus: each level adds 5% effectiveness
            if upgrade_level > 0:
                base_rate = min(1.0, base_rate * (1.0 + 0.05 * upgrade_level))

            # UV turbidity penalty
            if fdata.get("uv_turbidity_sensitive") and contaminant == "bacteria":
                turb = water.levels.get("turbidity", 0)
                if turb > 5:
                    base_rate *= 0.3
                elif turb > 2:
                    base_rate *= 0.7

            # Degradation from repeated use
            deg = fdata.get("degradation", 0)
            if deg > 0 and use_count > 0:
                base_rate *= max(0.3, 1.0 - deg * use_count)

            old_val = water.levels[contaminant]
            new_val = old_val * (1.0 - base_rate)
            water.levels[contaminant] = max(new_val, 0)

        # pH adjustment
        if fdata["ph_adjust"] != 0:
            water.levels["ph"] = water.levels.get("ph", 7.0) + fdata["ph_adjust"]
            water.levels["ph"] = max(0, min(14, water.levels["ph"]))

        # Chlorine addition
        if fdata["adds_chlorine"] > 0:
            water.levels["chlorine"] = water.levels.get("chlorine", 0) + fdata["adds_chlorine"]

        # Water loss
        water.volume_percent *= (1.0 - fdata["water_loss"])

        # Track usage
        filter_uses[fid] = use_count + 1

        stages.append({
            "label": fdata["name"],
            "filter_id": fid,
            "levels": water.snapshot(),
            "volume": water.volume_percent,
        })

    # Round final values
    from engine.water_quality import CONTAMINANTS
    for key in water.levels:
        dec = CONTAMINANTS.get(key, {}).get("decimals", 2)
        water.levels[key] = round(water.levels[key], dec)

    return water, stages


def calculate_cost(pipeline):
    total = 0
    for fid in pipeline:
        total += FILTERS[fid]["cost"]
    return total


def calculate_energy(pipeline):
    total = 0
    for fid in pipeline:
        total += FILTERS[fid]["energy"]
    return total
