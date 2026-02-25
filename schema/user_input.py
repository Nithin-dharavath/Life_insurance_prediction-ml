from pydantic import BaseModel, Field, computed_field, field_validator
from typing import Literal, Annotated
from city.city_tier import tier_1_cities, tier_2_cities

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
        return self.weight/(self.height**2)
    
    @computed_field
    @property
    def lifestyle_risk(self) -> str:
        if self.smoker and self.bmi > 30:
            return "high"
        elif self.smoker and self.bmi > 27:
            return "medium"
        else:
            return "low"
        
    @computed_field
    @property
    def age_group(self) -> str :
        if self.age < 18:
             return "young"
        elif self.age < 45:
             return "adult"
        elif self.age < 65:
            return "middle-aged"
        return "senior"
    
    @computed_field
    @property
    def city_tier(self) -> int:
        if self.city in tier_1_cities:
            return 1
        elif self.city in tier_2_cities:
            return 2
        else:
            return 3