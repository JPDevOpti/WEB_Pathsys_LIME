"""Service for ticket business logic."""

import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile

from app.modules.tickets.repositories.ticket_repository import TicketRepository
from app.modules.tickets.repositories.consecutive_repository import ConsecutiveTicketRepository
from app.modules.tickets.models.ticket import Ticket, TicketStatusEnum
from app.modules.tickets.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketSearch,
    TicketStatusUpdate,
    ImageUploadResponse
)
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError


class TicketService:
    """Service for ticket management."""
    
    def __init__(self, database: Any):
        self.repository = TicketRepository(database)
        self.consecutive_repository = ConsecutiveTicketRepository(database)
        self.upload_dir = os.getenv("TICKETS_UPLOAD_DIR", "/tmp/uploads/tickets/images")
        self.max_image_size = int(os.getenv("TICKETS_MAX_IMAGE_SIZE", "5242880"))  # 5MB
        
    async def create_ticket(self, ticket_data: TicketCreate, user_id: str) -> TicketResponse:
        """Create a new ticket with automatic consecutive code."""
        ticket_code = await self._generate_consecutive_code()
        
        ticket_dict = ticket_data.model_dump()
        ticket_dict.update({
            "ticket_code": ticket_code,
            "created_by": user_id
        })
        
        # Important: pass the complete dictionary to the repository to not lose
        # internal fields (ticket_code and created_by) that are not in the public schema
        ticket = await self.repository.create(ticket_dict)
        return self._to_response(ticket)
    
    async def get_next_consecutive(self) -> str:
        """Get the next available consecutive code (query only)."""
        return await self._get_next_consecutive_preview()
    
    async def _get_next_consecutive_preview(self) -> str:
        """Query the next consecutive code without incrementing the counter."""
        current_year = datetime.now().year
        next_number = await self.consecutive_repository.get_next_number_preview(current_year)
        return f"T-{current_year}-{next_number:03d}"
    
    async def _generate_consecutive_code(self) -> str:
        """Generate and consume the next consecutive code for the current year."""
        current_year = datetime.now().year
        next_number = await self.consecutive_repository.get_next_number(current_year)
        return f"T-{current_year}-{next_number:03d}"
    
    async def get_ticket_by_code(self, ticket_code: str) -> TicketResponse:
        """Get a ticket by ticket code."""
        ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        return self._to_response(ticket)
    
    async def list_tickets(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "ticket_date",
        sort_order: str = "desc"
    ) -> List[TicketListResponse]:
        """List all tickets with pagination."""
        tickets = await self.repository.list_all_tickets(skip, limit, sort_by, sort_order)
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def search_tickets(
        self, 
        search_params: TicketSearch, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "ticket_date",
        sort_order: str = "desc"
    ) -> List[TicketListResponse]:
        """Search tickets with advanced filters."""
        tickets = await self.repository.search_tickets(
            search_params, skip, limit, sort_by, sort_order
        )
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def count_tickets(self, search_params: TicketSearch) -> int:
        """Count tickets that match the filters."""
        return await self.repository.count_tickets(search_params)
    
    async def get_user_tickets(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[TicketListResponse]:
        """Get tickets created by a specific user."""
        tickets = await self.repository.get_tickets_by_user(user_id, skip, limit)
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def update_ticket(
        self, 
        ticket_code: str, 
        ticket_data: TicketUpdate, 
        user_id: str,
        is_admin: bool = False
    ) -> TicketResponse:
        """Update an existing ticket."""
        existing_ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not existing_ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        
        # Check permissions: only creator or admins can update
        if not is_admin and existing_ticket.created_by != user_id:
            raise BadRequestError("You don't have permission to update this ticket")
        
        # If not admin, cannot change status
        if not is_admin and ticket_data.status is not None:
            raise BadRequestError("Only administrators can change the ticket status")
        
        updated_ticket = await self.repository.update_by_ticket_code(ticket_code, ticket_data)
        if not updated_ticket:
            raise NotFoundError(f"Error updating ticket {ticket_code}")
        
        return self._to_response(updated_ticket)
    
    async def change_ticket_status(
        self, 
        ticket_code: str, 
        status_data: TicketStatusUpdate
    ) -> TicketResponse:
        """Change the status of a ticket (only for administrators)."""
        existing_ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not existing_ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        
        update_data = TicketUpdate(status=status_data.status)
        updated_ticket = await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        if not updated_ticket:
            raise NotFoundError(f"Error changing status of ticket {ticket_code}")
        
        return self._to_response(updated_ticket)
    
    async def delete_ticket(self, ticket_code: str) -> bool:
        """Delete a ticket (only for administrators)."""
        existing_ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not existing_ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        
        # If has image, delete it from disk
        if existing_ticket.image:
            await self._delete_image_file(existing_ticket.image)
        
        return await self.repository.delete_by_ticket_code(ticket_code)
    
    async def upload_ticket_image(
        self, 
        ticket_code: str, 
        file: UploadFile,
        user_id: str,
        is_admin: bool = False
    ) -> ImageUploadResponse:
        """Upload image to a ticket."""
        existing_ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not existing_ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        
        # Check permissions
        if not is_admin and existing_ticket.created_by != user_id:
            raise BadRequestError("You don't have permission to upload images to this ticket")
        
        # Validate file
        self._validate_image(file)
        
        # Delete previous image if exists
        if existing_ticket.image:
            await self._delete_image_file(existing_ticket.image)
        
        # Save new image
        image_url = await self._save_image(file, ticket_code)
        
        # Update ticket with new URL
        update_data = TicketUpdate(image=image_url)
        await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        return ImageUploadResponse(
            image_url=image_url,
            message="Image uploaded successfully"
        )
    
    async def delete_ticket_image(
        self, 
        ticket_code: str,
        user_id: str,
        is_admin: bool = False
    ) -> dict:
        """Delete image from a ticket."""
        existing_ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not existing_ticket:
            raise NotFoundError(f"Ticket with code {ticket_code} not found")
        
        # Check permissions
        if not is_admin and existing_ticket.created_by != user_id:
            raise BadRequestError("You don't have permission to delete images from this ticket")
        
        if not existing_ticket.image:
            raise BadRequestError("The ticket has no attached image")
        
        # Delete file from disk
        await self._delete_image_file(existing_ticket.image)
        
        # Update ticket removing the image
        update_data = TicketUpdate(image=None)
        await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        return {"message": "Image deleted successfully"}
    
    def _validate_image(self, file: UploadFile) -> None:
        """Validate that the file is a valid image."""
        if not file.content_type or not file.content_type.startswith("image/"):
            raise BadRequestError("The file must be an image")
        
        if file.size and file.size > self.max_image_size:
            max_mb = self.max_image_size / (1024 * 1024)
            raise BadRequestError(f"The image cannot exceed {max_mb}MB")
        
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if file.filename:
            ext = os.path.splitext(file.filename.lower())[1]
            if ext not in allowed_extensions:
                raise BadRequestError("Image format not allowed. Use: JPG, PNG, GIF, WEBP")
    
    async def _save_image(self, file: UploadFile, ticket_code: str) -> str:
        """Generate a Data URL base64 to store the image in the DB (similar to signatures)."""
        content = await file.read()
        try:
            import base64
            mime = file.content_type or "image/png"
            b64 = base64.b64encode(content).decode("utf-8")
            return f"data:{mime};base64,{b64}"
        except Exception:
            # Fallback: no valid image
            return ""
    
    async def _delete_image_file(self, image_url: str) -> None:
        """No physical deletion required: we store as Data URL in DB."""
        return None
    
    def _to_response(self, ticket: Ticket) -> TicketResponse:
        """Convert Ticket model to TicketResponse."""
        return TicketResponse(
            ticket_code=ticket.ticket_code,
            title=ticket.title,
            category=ticket.category,
            description=ticket.description,
            image=ticket.image,
            ticket_date=ticket.ticket_date,
            status=ticket.status,
            created_by=ticket.created_by
        )
    
    def _to_list_response(self, ticket: Ticket) -> TicketListResponse:
        """Convert Ticket model to TicketListResponse."""
        return TicketListResponse(
            ticket_code=ticket.ticket_code,
            title=ticket.title,
            category=ticket.category,
            description=ticket.description,
            status=ticket.status,
            image=ticket.image,
            ticket_date=ticket.ticket_date
        )
