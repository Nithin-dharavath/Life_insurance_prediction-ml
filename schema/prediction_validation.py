"""Pydantic model for the prediction response schema."""

from pydantic import BaseModel, Field
from typing import Dict

class Output(BaseModel):
    """Prediction result returned by the /predict endpoint.

    Wrapped in a ``{"Response": Output}`` envelope by ``app.py``.
    """

    predicted_category: str = Field(..., description="Predicted insurance category")
    confidence: float = Field(..., description="Prediction confidence score")
    class_probabilities: Dict[str, float] = Field(
        ..., 
        description="Probability across all possible classes"
    )