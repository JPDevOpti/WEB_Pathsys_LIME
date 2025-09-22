"""Pydantic schemas for the tickets API."""

from typing import Optional
from datetime import datetime
from pydantic import BaseModel, Field, field_validator
from app.modules.tickets.models.ticket import TicketCategoryEnum, TicketStatusEnum


class TicketCreate(BaseModel):
    """Schema for creating a new ticket."""
    title: str = Field(..., max_length=100, min_length=1, description="Ticket title")
    category: TicketCategoryEnum = Field(..., description="Ticket category")
    description: str = Field(..., max_length=500, min_length=1, description="Detailed description")
    image: Optional[str] = Field(None, description="Attached image URL")

    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        if not v or not v.strip():
            raise ValueError('The title cannot be empty')
        return v.strip()

    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        if not v or not v.strip():
            raise ValueError('The description cannot be empty')
        return v.strip()

    class Config:
        from_attributes = True


class TicketUpdate(BaseModel):
    """Schema for updating a ticket."""
    title: Optional[str] = Field(None, max_length=100, min_length=1)
    category: Optional[TicketCategoryEnum] = None
    description: Optional[str] = Field(None, max_length=500, min_length=1)
    image: Optional[str] = None
    status: Optional[TicketStatusEnum] = None

    @field_validator('title', mode='before')
    @classmethod
    def validate_title(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('The title cannot be empty')
        return v.strip() if v else v

    @field_validator('description', mode='before')
    @classmethod
    def validate_description(cls, v):
        if v is not None and (not v or not v.strip()):
            raise ValueError('The description cannot be empty')
        return v.strip() if v else v

    class Config:
        from_attributes = True


class TicketSearch(BaseModel):
    """Schema for ticket search and filters."""
    status: Optional[TicketStatusEnum] = None
    category: Optional[TicketCategoryEnum] = None
    created_by: Optional[str] = None
    search_text: Optional[str] = Field(None, description="Search in title and description")
    date_from: Optional[datetime] = None
    date_to: Optional[datetime] = None

    class Config:
        from_attributes = True


class TicketStatusUpdate(BaseModel):
    """Schema for changing only the status of a ticket."""
    status: TicketStatusEnum = Field(..., description="New ticket status")

    class Config:
        from_attributes = True


class TicketResponse(BaseModel):
    """Complete ticket response schema."""
    ticket_code: str = Field(..., description="Unique ticket code")
    title: str = Field(..., description="Ticket title")
    category: TicketCategoryEnum = Field(..., description="Ticket category")
    description: str = Field(..., description="Detailed description")
    image: Optional[str] = Field(None, description="Attached image URL")
    ticket_date: datetime = Field(..., description="Ticket creation date")
    status: TicketStatusEnum = Field(..., description="Current ticket status")
    created_by: Optional[str] = Field(None, description="ID of the user who created the ticket")

    class Config:
        from_attributes = True


class TicketListResponse(BaseModel):
    """Compact response schema for ticket lists."""
    ticket_code: str = Field(..., description="Unique ticket code")
    title: str = Field(..., description="Ticket title")
    category: TicketCategoryEnum = Field(..., description="Ticket category")
    description: str = Field(..., description="Brief ticket description")
    status: TicketStatusEnum = Field(..., description="Current ticket status")
    image: Optional[str] = Field(None, description="Attached image URL")
    ticket_date: datetime = Field(..., description="Ticket creation date")

    class Config:
        from_attributes = True


class ImageUploadResponse(BaseModel):
    """Response schema for image upload."""
    image_url: str = Field(..., description="Uploaded image URL")
    message: str = Field(..., description="Confirmation message")

    class Config:
        from_attributes = True
