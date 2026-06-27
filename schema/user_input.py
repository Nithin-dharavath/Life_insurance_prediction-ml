from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated

from features import compute_bmi, compute_age_group, compute_lifestyle_risk, compute_city_tier


#pydantic model to validate inncomming data
class UserInput(BaseModel):

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
        v = v.strip().title()
        return v

    @computed_field
    @property
    def bmi(self) -> float:
        return compute_bmi(self.weight, self.height)

    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        return compute_lifestyle_risk(self.smoker, self.bmi)

    @computed_field
    @property
    def age_group(self) -> str:
        return compute_age_group(self.age)

    @computed_field
    @property
    def city_tier(self) -> int:
        return compute_city_tier(self.city)