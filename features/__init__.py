"""Feature engineering functions for the insurance prediction pipeline.

All derived features are computed here and used by both the training
script (model/train.py) and the serving layer (schema/user_input.py).
"""

from city.city_tier import tier_1_cities, tier_2_cities


def compute_bmi(weight: float, height: float) -> float:
    """Calculate Body Mass Index.

    Args:
        weight: Weight in kilograms.
        height: Height in meters.

    Returns:
        BMI value (kg/m²).
    """
    return weight / (height ** 2)


def compute_age_group(age: int) -> str:
    """Classify age into a predefined group.

    Args:
        age: Age in years.

    Returns:
        One of "young", "adult", "middle-aged", or "senior".
    """
    if age < 18:
        return "young"
    elif age < 45:
        return "adult"
    elif age < 65:
        return "middle-aged"
    return "senior"


def compute_lifestyle_risk(smoker: bool, bmi: float) -> str:
    """Estimate lifestyle risk based on smoking and BMI.

    Args:
        smoker: Whether the person smokes.
        bmi: Body Mass Index.

    Returns:
        One of "high", "medium", or "low".
    """
    if smoker and bmi > 30:
        return "high"
    elif smoker or bmi > 27:
        return "medium"
    return "low"


def compute_city_tier(city: str) -> int:
    """Determine city tier (1, 2, or 3) by membership in predefined lists.

    Args:
        city: City name (case-sensitive; should be title-cased beforehand).

    Returns:
        1 for tier-1 cities, 2 for tier-2, 3 for all others.
    """
    if city in tier_1_cities:
        return 1
    elif city in tier_2_cities:
        return 2
    return 3
