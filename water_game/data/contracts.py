"""Customer contracts for the tycoon system.
Each contract has requirements and payouts."""

CONTRACTS = [
    {
        "id": "village_basic",
        "name": "Village Supply",
        "desc": "Basic clean water for\na small village.",
        "min_grade": "C",
        "min_volume": 50,
        "payout": 300,
        "bonus_grade_a": 150,
        "reputation": 5,
        "icon_color": 11,
    },
    {
        "id": "farm_irrigation",
        "name": "Farm Irrigation",
        "desc": "Irrigation water for crops.\nDoesn't need to be drinkable.",
        "min_grade": "D",
        "min_volume": 70,
        "payout": 200,
        "bonus_grade_a": 50,
        "reputation": 3,
        "icon_color": 3,
    },
    {
        "id": "hospital",
        "name": "Hospital Supply",
        "desc": "Ultra-pure water for\nmedical use. Grade A only!",
        "min_grade": "A",
        "min_volume": 60,
        "payout": 800,
        "bonus_grade_a": 0,
        "reputation": 15,
        "icon_color": 8,
    },
    {
        "id": "bottling_plant",
        "name": "Bottling Plant",
        "desc": "Premium bottled water.\nNeeds grade B or better.",
        "min_grade": "B",
        "min_volume": 65,
        "payout": 500,
        "bonus_grade_a": 200,
        "reputation": 10,
        "icon_color": 12,
    },
    {
        "id": "school",
        "name": "School District",
        "desc": "Safe drinking water\nfor local schools.",
        "min_grade": "B",
        "min_volume": 50,
        "payout": 400,
        "bonus_grade_a": 100,
        "reputation": 8,
        "icon_color": 10,
    },
    {
        "id": "factory",
        "name": "Factory Coolant",
        "desc": "Industrial cooling water.\nLow purity is fine.",
        "min_grade": "D",
        "min_volume": 80,
        "payout": 250,
        "bonus_grade_a": 30,
        "reputation": 2,
        "icon_color": 5,
    },
]

GRADE_ORDER = {"A": 0, "B": 1, "C": 2, "D": 3, "F": 4}


def grade_meets_minimum(achieved, required):
    return GRADE_ORDER.get(achieved, 4) <= GRADE_ORDER.get(required, 4)
