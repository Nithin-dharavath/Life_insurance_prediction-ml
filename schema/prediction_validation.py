from pydantic import BaseModel, Field
from typing import Dict

class Output(BaseModel):
    predicted_category: str = Field(..., description="Predicted insurance category")
    confidence: float = Field(..., description="Prediction confidence score")
    class_probabilities: Dict[str, float] = Field(
        ..., 
        description="Probability across all possible classes"
    )