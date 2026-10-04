from pydantic import BaseModel


class CalculationRequest(BaseModel):
    expression: str
