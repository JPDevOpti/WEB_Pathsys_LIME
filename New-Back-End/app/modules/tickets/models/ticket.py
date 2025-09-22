"""Models for ticket management."""

from typing import Optional
from datetime import datetime
from enum import Enum
from pydantic import BaseModel, Field, field_validator
from app.shared.models.base import PyObjectId


class TicketCategoryEnum(str, Enum):
    """Available ticket categories."""
    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    TECHNICAL = "technical"


class TicketStatusEnum(str, Enum):
    """Available ticket statuses."""
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"


class Ticket(BaseModel):
    """Main Ticket model for MongoDB."""
    
    id: Optional[PyObjectId] = Field(default_factory=PyObjectId, alias="_id")
    ticket_code: str = Field(..., max_length=50, description="Unique ticket code (T-YYYY-NNN)")
    title: str = Field(..., max_length=100, min_length=1, description="Ticket title")
    category: TicketCategoryEnum = Field(..., description="Ticket category")
    description: str = Field(..., max_length=500, min_length=1, description="Detailed description")
    image: Optional[str] = Field(None, description="Attached image URL")
    ticket_date: datetime = Field(default_factory=datetime.utcnow, description="Ticket creation date")
    status: TicketStatusEnum = Field(default=TicketStatusEnum.OPEN, description="Current ticket status")
    created_by: str = Field(..., description="ID of the user who created the ticket")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    
    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        """Validate and clean title."""
        if not v or not v.strip():
            raise ValueError('The title cannot be empty')
        return v.strip()
    
    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        """Validate and clean description."""
        if not v or not v.strip():
            raise ValueError('The description cannot be empty')
        return v.strip()
    
    @field_validator('ticket_code')
    @classmethod
    def validate_ticket_code(cls, v):
        """Validate ticket code format (T-YYYY-NNN)."""
        if not v:
            raise ValueError('Ticket code is required')
        
        # Validate T-YYYY-NNN format
        parts = v.split('-')
        if len(parts) != 3 or parts[0] != 'T':
            raise ValueError('Code must have format T-YYYY-NNN')
        
        try:
            year = int(parts[1])
            number = int(parts[2])
            if year < 2000 or year > 2100:
                raise ValueError('Year must be between 2000 and 2100')
            if number < 1 or number > 999999:
                raise ValueError('Invalid consecutive number')
        except ValueError:
            raise ValueError('Invalid code format')
        
        return v

    class Config:
        populate_by_name = True
        arbitrary_types_allowed = True
        json_encoders = {
            PyObjectId: str,
            datetime: lambda v: v.isoformat()
        }
        from_attributes = True
