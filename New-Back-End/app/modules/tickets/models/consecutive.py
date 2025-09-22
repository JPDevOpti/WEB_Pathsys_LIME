"""Models for ticket consecutive number management."""

from datetime import datetime
from pydantic import BaseModel, Field, field_validator


class ConsecutiveTicket(BaseModel):
    """Control of ticket consecutives by year."""
    
    year: int = Field(..., ge=2000, le=2100)
    last_number: int = Field(default=0, ge=0)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('year')
    @classmethod
    def validate_year(cls, v):
        current_year = datetime.now().year
        if v < 2000 or v > current_year + 5:
            raise ValueError(f'Year must be between 2000 and {current_year + 5}')
        return v

    @field_validator('last_number')
    @classmethod
    def validate_last_number(cls, v):
        if v < 0:
            raise ValueError('Last number cannot be negative')
        if v > 999999:
            raise ValueError('Last number exceeds allowed limit')
        return v


class ConsecutiveTicketCreate(BaseModel):
    """Schema for creating a new consecutive control."""
    year: int = Field(..., ge=2000, le=2100)
    last_number: int = Field(default=0, ge=0)
