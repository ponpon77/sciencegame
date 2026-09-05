"""Pump equipment for the collection phase.
Better pumps collect water faster and from a wider area."""

PUMPS = {
    "bucket": {
        "name": "Bucket",
        "desc": "Basic bucket.\nScoop water slowly.",
        "collect_rate": 4,
        "radius": 14,
        "cost": 0,
        "color": 6,
        "auto_collect": False,
    },
    "hand_pump": {
        "name": "Hand Pump",
        "desc": "Manual pump.\nFaster, wider reach.",
        "collect_rate": 8,
        "radius": 22,
        "cost": 200,
        "color": 9,
        "auto_collect": False,
    },
    "electric_pump": {
        "name": "Electric Pump",
        "desc": "Motor pump. Hold\nclick to auto-pull!",
        "collect_rate": 12,
        "radius": 28,
        "cost": 500,
        "color": 12,
        "auto_collect": True,
    },
    "industrial_pump": {
        "name": "Industrial Pump",
        "desc": "Heavy-duty. Huge\nradius, auto-pull.",
        "collect_rate": 20,
        "radius": 38,
        "cost": 1200,
        "color": 11,
        "auto_collect": True,
    },
}

PUMP_ORDER = ["bucket", "hand_pump", "electric_pump", "industrial_pump"]
