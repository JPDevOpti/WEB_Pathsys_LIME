"""Rutas de la API para el módulo de tickets."""

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
from app.core.dependencies import get_current_active_user, require_roles
from app.modules.auth.models.auth import AuthUser
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(tags=["tickets"])


def get_ticket_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> TicketService:
    """Dependencia para el servicio de tickets."""
    return TicketService(database)


def handle_exceptions(func):
    """Decorador para manejo centralizado de excepciones."""
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
            logger.error(f"Error inesperado en tickets: {str(e)}", exc_info=True)
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return wrapper


def is_admin(user: AuthUser) -> bool:
    """Verificar si el usuario es administrador."""
    return user.get_primary_role() == "admin"


# ============= ENDPOINTS PÚBLICOS (todos los usuarios autenticados) =============

@router.post("/", response_model=TicketResponse)
@handle_exceptions
async def crear_ticket(
    ticket_data: TicketCreate,
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Crear un nuevo ticket de soporte."""
    logger.info(f"Usuario {current_user.email} creando ticket: {ticket_data.titulo}")
    return await ticket_service.crear_ticket(ticket_data, str(current_user.id))


@router.get("/", response_model=List[TicketListResponse])
@handle_exceptions
async def listar_tickets(
    skip: int = Query(0, ge=0, description="Número de tickets a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de tickets a retornar"),
    sort_by: str = Query("fecha_ticket", description="Campo por el cual ordenar"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden ascendente o descendente"),
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Listar tickets. Todos los usuarios ven todos los tickets."""
    # Todos los usuarios ven todos los tickets
    return await ticket_service.listar_tickets(skip, limit, sort_by, sort_order)


@router.post("/search", response_model=List[TicketListResponse])
@handle_exceptions
async def buscar_tickets(
    search_params: TicketSearch,
    skip: int = Query(0, ge=0, description="Número de tickets a omitir"),
    limit: int = Query(20, ge=1, le=100, description="Número máximo de tickets a retornar"),
    sort_by: str = Query("fecha_ticket", description="Campo por el cual ordenar"),
    sort_order: str = Query("desc", regex="^(asc|desc)$", description="Orden ascendente o descendente"),
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Búsqueda avanzada de tickets con filtros."""
    # Todos los usuarios pueden buscar en todos los tickets
    return await ticket_service.buscar_tickets(search_params, skip, limit, sort_by, sort_order)


@router.get("/count", response_model=dict)
@handle_exceptions
async def contar_tickets(
    search_params: TicketSearch = Depends(),
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Contar tickets que coinciden con los filtros."""
    # Todos los usuarios pueden contar todos los tickets
    count = await ticket_service.contar_tickets(search_params)
    return {"total": count}


@router.get("/{ticket_code}", response_model=TicketResponse)
@handle_exceptions
async def obtener_ticket(
    ticket_code: str,
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Obtener un ticket por su código."""
    ticket = await ticket_service.obtener_ticket_por_codigo(ticket_code)
    
    # Verificar permisos: solo el creador o admins pueden ver el ticket
    if not is_admin(current_user) and ticket.created_by != str(current_user.id):
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permisos para ver este ticket"
        )
    
    return ticket


@router.put("/{ticket_code}", response_model=TicketResponse)
@handle_exceptions
async def actualizar_ticket(
    ticket_code: str,
    ticket_data: TicketUpdate,
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Actualizar un ticket. Solo el creador o admins pueden actualizar."""
    return await ticket_service.actualizar_ticket(
        ticket_code, 
        ticket_data, 
        str(current_user.id), 
        is_admin(current_user)
    )


# ============= ENDPOINTS SOLO PARA ADMINISTRADORES =============

@router.delete("/{ticket_code}", response_model=dict)
@handle_exceptions
async def eliminar_ticket(
    ticket_code: str,
    current_user: AuthUser = Depends(require_roles(["admin", "administrador"])),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Eliminar un ticket (solo administradores)."""
    logger.info(f"Admin {current_user.email} eliminando ticket: {ticket_code}")
    
    success = await ticket_service.eliminar_ticket(ticket_code)
    if success:
        return {"mensaje": f"Ticket {ticket_code} eliminado exitosamente"}
    else:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Error al eliminar el ticket"
        )


@router.patch("/{ticket_code}/status", response_model=TicketResponse)
@handle_exceptions
async def cambiar_estado_ticket(
    ticket_code: str,
    estado_data: TicketStatusUpdate,
    current_user: AuthUser = Depends(require_roles(["admin", "administrador"])),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Cambiar el estado de un ticket (solo administradores)."""
    logger.info(f"Admin {current_user.email} cambiando estado de {ticket_code} a {estado_data.estado}")
    
    return await ticket_service.cambiar_estado_ticket(ticket_code, estado_data)


# ============= ENDPOINTS DE GESTIÓN DE IMÁGENES =============

@router.post("/{ticket_code}/upload-image", response_model=ImageUploadResponse)
@handle_exceptions
async def subir_imagen_ticket(
    ticket_code: str,
    image: UploadFile = File(...),
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Subir imagen a un ticket. Solo el creador o admins pueden subir."""
    logger.info(f"Usuario {current_user.email} subiendo imagen a ticket: {ticket_code}")
    
    return await ticket_service.subir_imagen_ticket(
        ticket_code, 
        image, 
        str(current_user.id), 
        is_admin(current_user)
    )


@router.delete("/{ticket_code}/image", response_model=dict)
@handle_exceptions
async def eliminar_imagen_ticket(
    ticket_code: str,
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Eliminar imagen de un ticket. Solo el creador o admins pueden eliminar."""
    logger.info(f"Usuario {current_user.email} eliminando imagen de ticket: {ticket_code}")
    
    return await ticket_service.eliminar_imagen_ticket(
        ticket_code, 
        str(current_user.id), 
        is_admin(current_user)
    )


# ============= ENDPOINTS UTILITARIOS =============

@router.get("/siguiente-consecutivo", response_model=dict)
@handle_exceptions
async def obtener_siguiente_consecutivo(
    current_user: AuthUser = Depends(get_current_active_user),
    ticket_service: TicketService = Depends(get_ticket_service)
):
    """Consultar el siguiente código consecutivo disponible (NO lo consume)."""
    codigo = await ticket_service.obtener_siguiente_consecutivo()
    return {
        "codigo_consecutivo": codigo,
        "mensaje": "Este es el próximo código disponible. No se ha consumido."
    }


@router.get("/test", response_model=dict)
@handle_exceptions
async def test_endpoint():
    """Endpoint de prueba simple."""
    return {"message": "Tickets router funcionando correctamente"}
