"""API routes for the tickets module."""

from typing import List, Optional
from functools import wraps
from fastapi import APIRouter, Depends, HTTPException, Query, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.modules.tickets.services.ticket_service import TicketService
from app.modules.tickets.schemas.ticket import (
    TicketCreate,
    TicketUpdate,
    TicketResponse,
    TicketListResponse,
    TicketSearch,
    TicketStatusUpdate,
    ImageUploadResponse
)
from app.config.database import get_database
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from app.modules.auth.routes.auth_routes import get_current_user_id

# Configure logger
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tickets"])


def get_ticket_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> TicketService:
    """Dependency for the ticket service."""
    return TicketService(database)


def handle_exceptions(func):
    """Decorator for centralized exception handling."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConflictError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except BadRequestError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            logger.error(f"Unexpected error in tickets: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return wrapper


# ============= PUBLIC ENDPOINTS =============

@router.post("/", response_model=TicketResponse)
@handle_exceptions
async def create_ticket(
    ticket_data: TicketCreate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Create a new support ticket."""
    logger.info(f"Creating ticket: {ticket_data.title}")
    return await ticket_service.create_ticket(ticket_data, current_user_id)


@router.get("/", response_model=List[TicketListResponse])
@handle_exceptions
async def list_tickets(
    skip: int = Query(0, ge=0, description="Number of tickets to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tickets to return"),
    sort_by: str = Query("ticket_date", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Ascending or descending order"),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """List tickets."""
    return await ticket_service.list_tickets(skip, limit, sort_by, sort_order)


@router.post("/search", response_model=List[TicketListResponse])
@handle_exceptions
async def search_tickets(
    search_params: TicketSearch,
    skip: int = Query(0, ge=0, description="Number of tickets to skip"),
    limit: int = Query(20, ge=1, le=100, description="Maximum number of tickets to return"),
    sort_by: str = Query("ticket_date", description="Field to sort by"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Ascending or descending order"),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Advanced ticket search with filters."""
    return await ticket_service.search_tickets(search_params, skip, limit, sort_by, sort_order)


@router.get("/count", response_model=dict)
@handle_exceptions
async def count_tickets(
    search_params: TicketSearch = Depends(),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Count tickets that match the filters."""
    count = await ticket_service.count_tickets(search_params)
    return {"total": count}


@router.get("/{ticket_code}", response_model=TicketResponse)
@handle_exceptions
async def get_ticket(
    ticket_code: str,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get a ticket by its code."""
    return await ticket_service.get_ticket_by_code(ticket_code)


# ============= ADMIN ONLY ENDPOINTS =============

@router.put("/{ticket_code}", response_model=TicketResponse)
@handle_exceptions
async def update_ticket(
    ticket_code: str,
    ticket_data: TicketUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Update an existing ticket (admin only)."""
    return await ticket_service.update_ticket(
        ticket_code,
        ticket_data,
        current_user_id,
        is_admin=True  # For now, allow all authenticated users
    )


@router.delete("/{ticket_code}", response_model=dict)
@handle_exceptions
async def delete_ticket(
    ticket_code: str,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete a ticket (admin only)."""
    success = await ticket_service.delete_ticket(ticket_code)
    if success:
        return {"message": f"Ticket {ticket_code} deleted successfully"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error deleting ticket"
        )


@router.patch("/{ticket_code}/status", response_model=TicketResponse)
@handle_exceptions
async def change_ticket_status(
    ticket_code: str,
    status_data: TicketStatusUpdate,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Change the status of a ticket (admin only)."""
    return await ticket_service.change_ticket_status(ticket_code, status_data)


@router.post("/{ticket_code}/upload-image", response_model=ImageUploadResponse)
@handle_exceptions
async def upload_ticket_image(
    ticket_code: str,
    image: UploadFile = File(...),
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Upload an image to a ticket (admin only)."""
    return await ticket_service.upload_ticket_image(
        ticket_code,
        image,
        current_user_id,
        is_admin=True  # For now, allow all authenticated users
    )


@router.delete("/{ticket_code}/image", response_model=dict)
@handle_exceptions
async def delete_ticket_image(
    ticket_code: str,
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Delete an image from a ticket (admin only)."""
    return await ticket_service.delete_ticket_image(
        ticket_code,
        current_user_id,
        is_admin=True  # For now, allow all authenticated users
    )


@router.get("/next-consecutive", response_model=dict)
@handle_exceptions
async def get_next_consecutive(
    ticket_service: TicketService = Depends(get_ticket_service),
    current_user_id: str = Depends(get_current_user_id)
):
    """Get the next available consecutive code (does not consume it)."""
    code = await ticket_service.get_next_consecutive()
    return {
        "consecutive_code": code,
        "message": "This is the next available code. It has not been consumed."
    }