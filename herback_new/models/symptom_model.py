from pydantic import BaseModel, field_validator
from typing import List, Optional

class SymptomPayload(BaseModel):
    """Validated schema for user symptom input."""
    symptoms: List[str]
    severity: str
    cycle_day: int
    notes: Optional[str] = None
    
    @field_validator('severity')
    @classmethod
    def validate_severity(cls, v):
        """Ensure severity is one of allowed values."""
        if v not in ['mild', 'moderate', 'severe']:
            raise ValueError('severity must be mild, moderate, or severe')
        return v
    
    @field_validator('cycle_day')
    @classmethod
    def validate_cycle_day(cls, v):
        """Ensure cycle day is within valid range."""
        if not (1 <= v <= 40):
            raise ValueError('cycle_day must be between 1 and 40')
        return v
    
    @field_validator('symptoms')
    @classmethod
    def validate_symptoms(cls, v):
        """Ensure symptoms list is not empty."""
        if not v or len(v) == 0:
            raise ValueError('symptoms list cannot be empty')
        return v
