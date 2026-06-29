"""Pydantic model for validating incoming prediction requests.

Automatically computes derived features (bmi, age_group, lifestyle_risk,
city_tier) as computed fields that are exposed on the validated object.
"""

from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated

from city.city_tier import tier_1_cities, tier_2_cities
from features import compute_bmi, compute_age_group, compute_lifestyle_risk, compute_city_tier

_SUPPORTED_CITIES = frozenset(tier_1_cities + tier_2_cities)


class UserInput(BaseModel):
    """Validated user input for a premium prediction request.

    Raw fields (age, weight, height, income_lpa, occupation, smoker, city)
    are validated on ingress. Derived features are computed as read-only
    computed fields.
    """

    age : Annotated[int, Field(..., gt=0, lt=120, description="age of the user")]
    weight : Annotated[float, Field(..., gt=0, description="weight of the user")]
    height : Annotated[float, Field(..., gt=0, description="height of the user")]
    income_lpa : Annotated[float, Field(..., gt=0, description="Annual salary of the user")]
    occupation : Annotated[Literal["retired", "freelancer", "student", "government_job", "business_owner", "unemployed", "private_job"], Field(...,  description="work field of the user")]
    smoker : Annotated[bool, Field(..., description="is user smoker")]
    city : Annotated[str, Field(..., description="city name of the user")]

    @field_validator("city")
    @classmethod
    def normalize_city(cls, v: str) -> str:
        """Normalize and validate the city name.

        Strips whitespace and title-cases the input, then checks against
        the list of known cities. Rejects unrecognized cities with a
        descriptive error.

        Args:
            v: Raw city string.

        Returns:
            Normalized city name.

        Raises:
            ValueError: If the city is not in the supported list.
        """
        v = v.strip().title()
        if v not in _SUPPORTED_CITIES:
            raise ValueError(
                f"Unsupported city: '{v}'. Must be one of the recognized cities. "
                f"See /city/city_tier.py for the full list."
            )
        return v

    @computed_field
    @property
    def bmi(self) -> float:
        """Body Mass Index computed from weight and height."""
        return compute_bmi(self.weight, self.height)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        """Lifestyle risk category (high / medium / low)."""
        return compute_lifestyle_risk(self.smoker, self.bmi)

    @computed_field
    @property
    def age_group(self) -> str:
        """Age group classification (young / adult / middle-aged / senior)."""
        return compute_age_group(self.age)

    @computed_field
    @property
    def city_tier(self) -> int:
        """City tier (1, 2, or 3)."""
        return compute_city_tier(self.city)