from city.city_tier import tier_1_cities, tier_2_cities


def compute_bmi(weight: float, height: float) -> float:
    return weight / (height ** 2)


def compute_age_group(age: int) -> str:
    if age < 18:
        return "young"
    elif age < 45:
        return "adult"
    elif age < 65:
        return "middle-aged"
    return "senior"


def compute_lifestyle_risk(smoker: bool, bmi: float) -> str:
    if smoker and bmi > 30:
        return "high"
    elif smoker or bmi > 27:
        return "medium"
    return "low"


def compute_city_tier(city: str) -> int:
    if city in tier_1_cities:
        return 1
    elif city in tier_2_cities:
        return 2
    return 3
