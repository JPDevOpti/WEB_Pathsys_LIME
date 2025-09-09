"""Servicio para la lógica de negocio de tickets."""

import os
import uuid
from typing import List, Optional, Dict, Any
from datetime import datetime
from fastapi import UploadFile

from app.modules.tickets.repositories.ticket_repository import TicketRepository
from app.modules.tickets.repositories.consecutivo_repository import ConsecutivoTicketRepository
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
    """Servicio para la gestión de tickets."""
    
    def __init__(self, database: Any):
        self.repository = TicketRepository(database)
        self.consecutivo_repository = ConsecutivoTicketRepository(database)
        self.upload_dir = os.getenv("TICKETS_UPLOAD_DIR", "/tmp/uploads/tickets/images")
        self.max_image_size = int(os.getenv("TICKETS_MAX_IMAGE_SIZE", "5242880"))  # 5MB
        
    async def crear_ticket(self, ticket_data: TicketCreate, usuario_id: str) -> TicketResponse:
        """Crear un nuevo ticket con código consecutivo automático."""
        ticket_code = await self._generar_codigo_consecutivo()
        
        ticket_dict = ticket_data.model_dump()
        ticket_dict.update({
            "ticket_code": ticket_code,
            "created_by": usuario_id
        })
        
        # Importante: pasar el diccionario completo al repositorio para no perder
        # campos internos (ticket_code y created_by) que no están en el schema público
        ticket = await self.repository.create(ticket_dict)
        return self._to_response(ticket)
    
    async def obtener_siguiente_consecutivo(self) -> str:
        """Obtener el siguiente código consecutivo disponible (solo consulta)."""
        return await self._consultar_proximo_consecutivo()
    
    async def _consultar_proximo_consecutivo(self) -> str:
        """Consulta el próximo código consecutivo sin incrementar el contador."""
        current_year = datetime.now().year
        proximo_numero = await self.consecutivo_repository.consultar_proximo_numero(current_year)
        return f"T-{current_year}-{proximo_numero:03d}"
    
    async def _generar_codigo_consecutivo(self) -> str:
        """Genera y consume el siguiente código consecutivo para el año actual."""
        current_year = datetime.now().year
        siguiente_numero = await self.consecutivo_repository.obtener_siguiente_numero(current_year)
        return f"T-{current_year}-{siguiente_numero:03d}"
    
    async def obtener_ticket_por_codigo(self, ticket_code: str) -> TicketResponse:
        """Obtener un ticket por código de ticket."""
        ticket = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        return self._to_response(ticket)
    
    async def listar_tickets(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "fecha_ticket",
        sort_order: str = "desc"
    ) -> List[TicketListResponse]:
        """Listar todos los tickets con paginación."""
        tickets = await self.repository.get_multi(
            skip=skip, 
            limit=limit
        )
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def buscar_tickets(
        self, 
        search_params: TicketSearch, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "fecha_ticket",
        sort_order: str = "desc"
    ) -> List[TicketListResponse]:
        """Buscar tickets con filtros avanzados."""
        tickets = await self.repository.search_tickets(
            search_params, skip, limit, sort_by, sort_order
        )
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def contar_tickets(self, search_params: TicketSearch) -> int:
        """Contar tickets que coinciden con los filtros."""
        return await self.repository.count_tickets(search_params)
    
    async def obtener_tickets_usuario(
        self, 
        user_id: str, 
        skip: int = 0, 
        limit: int = 20
    ) -> List[TicketListResponse]:
        """Obtener tickets creados por un usuario específico."""
        tickets = await self.repository.get_tickets_by_user(user_id, skip, limit)
        return [self._to_list_response(ticket) for ticket in tickets]
    
    async def actualizar_ticket(
        self, 
        ticket_code: str, 
        ticket_data: TicketUpdate, 
        usuario_id: str,
        is_admin: bool = False
    ) -> TicketResponse:
        """Actualizar un ticket existente."""
        ticket_existente = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket_existente:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        
        # Verificar permisos: solo el creador o admins pueden actualizar
        if not is_admin and ticket_existente.created_by != usuario_id:
            raise BadRequestError("No tienes permisos para actualizar este ticket")
        
        # Si no es admin, no puede cambiar el estado
        if not is_admin and ticket_data.estado is not None:
            raise BadRequestError("Solo los administradores pueden cambiar el estado del ticket")
        
        ticket_actualizado = await self.repository.update_by_ticket_code(ticket_code, ticket_data)
        if not ticket_actualizado:
            raise NotFoundError(f"Error al actualizar ticket {ticket_code}")
        
        return self._to_response(ticket_actualizado)
    
    async def cambiar_estado_ticket(
        self, 
        ticket_code: str, 
        estado_data: TicketStatusUpdate
    ) -> TicketResponse:
        """Cambiar el estado de un ticket (solo para administradores)."""
        ticket_existente = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket_existente:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        
        update_data = TicketUpdate(estado=estado_data.estado)
        ticket_actualizado = await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        if not ticket_actualizado:
            raise NotFoundError(f"Error al cambiar estado del ticket {ticket_code}")
        
        return self._to_response(ticket_actualizado)
    
    async def eliminar_ticket(self, ticket_code: str) -> bool:
        """Eliminar un ticket (solo para administradores)."""
        ticket_existente = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket_existente:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        
        # Si tiene imagen, eliminarla del disco
        if ticket_existente.imagen:
            await self._eliminar_imagen_archivo(ticket_existente.imagen)
        
        return await self.repository.delete_by_ticket_code(ticket_code)
    
    async def subir_imagen_ticket(
        self, 
        ticket_code: str, 
        file: UploadFile,
        usuario_id: str,
        is_admin: bool = False
    ) -> ImageUploadResponse:
        """Subir imagen a un ticket."""
        ticket_existente = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket_existente:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        
        # Verificar permisos
        if not is_admin and ticket_existente.created_by != usuario_id:
            raise BadRequestError("No tienes permisos para subir imágenes a este ticket")
        
        # Validar archivo
        self._validar_imagen(file)
        
        # Eliminar imagen anterior si existe
        if ticket_existente.imagen:
            await self._eliminar_imagen_archivo(ticket_existente.imagen)
        
        # Guardar nueva imagen
        image_url = await self._guardar_imagen(file, ticket_code)
        
        # Actualizar ticket con nueva URL
        update_data = TicketUpdate(imagen=image_url)
        await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        return ImageUploadResponse(
            image_url=image_url,
            mensaje="Imagen subida exitosamente"
        )
    
    async def eliminar_imagen_ticket(
        self, 
        ticket_code: str,
        usuario_id: str,
        is_admin: bool = False
    ) -> dict:
        """Eliminar imagen de un ticket."""
        ticket_existente = await self.repository.get_by_ticket_code(ticket_code)
        if not ticket_existente:
            raise NotFoundError(f"Ticket con código {ticket_code} no encontrado")
        
        # Verificar permisos
        if not is_admin and ticket_existente.created_by != usuario_id:
            raise BadRequestError("No tienes permisos para eliminar imágenes de este ticket")
        
        if not ticket_existente.imagen:
            raise BadRequestError("El ticket no tiene imagen adjunta")
        
        # Eliminar archivo del disco
        await self._eliminar_imagen_archivo(ticket_existente.imagen)
        
        # Actualizar ticket removiendo la imagen
        update_data = TicketUpdate(imagen=None)
        await self.repository.update_by_ticket_code(ticket_code, update_data)
        
        return {"mensaje": "Imagen eliminada exitosamente"}
    
    def _validar_imagen(self, file: UploadFile) -> None:
        """Validar que el archivo sea una imagen válida."""
        if not file.content_type or not file.content_type.startswith("image/"):
            raise BadRequestError("El archivo debe ser una imagen")
        
        if file.size and file.size > self.max_image_size:
            max_mb = self.max_image_size / (1024 * 1024)
            raise BadRequestError(f"La imagen no puede superar {max_mb}MB")
        
        allowed_extensions = [".jpg", ".jpeg", ".png", ".gif", ".webp"]
        if file.filename:
            ext = os.path.splitext(file.filename.lower())[1]
            if ext not in allowed_extensions:
                raise BadRequestError("Formato de imagen no permitido. Use: JPG, PNG, GIF, WEBP")
    
    async def _guardar_imagen(self, file: UploadFile, ticket_code: str) -> str:
        """Guardar imagen en el sistema de archivos."""
        # Crear directorio si no existe
        os.makedirs(self.upload_dir, exist_ok=True)
        
        # Generar nombre único para la imagen
        file_ext = os.path.splitext(file.filename or "")[1] if file.filename else ".jpg"
        timestamp = int(datetime.now().timestamp())
        filename = f"{ticket_code}_{timestamp}_{uuid.uuid4().hex[:8]}{file_ext}"
        file_path = os.path.join(self.upload_dir, filename)
        
        # Guardar archivo
        content = await file.read()
        with open(file_path, "wb") as buffer:
            buffer.write(content)
        
        # Retornar URL relativa
        return f"/uploads/tickets/images/{filename}"
    
    async def _eliminar_imagen_archivo(self, image_url: str) -> None:
        """Eliminar imagen del sistema de archivos."""
        try:
            # Extraer nombre del archivo de la URL
            filename = os.path.basename(image_url)
            file_path = os.path.join(self.upload_dir, filename)
            
            if os.path.exists(file_path):
                os.remove(file_path)
        except Exception:
            # No fallar si no se puede eliminar el archivo
            pass
    
    def _to_response(self, ticket: Ticket) -> TicketResponse:
        """Convertir modelo Ticket a TicketResponse."""
        return TicketResponse(
            ticket_code=ticket.ticket_code,
            titulo=ticket.titulo,
            categoria=ticket.categoria,
            descripcion=ticket.descripcion,
            imagen=ticket.imagen,
            fecha_ticket=ticket.fecha_ticket,
            estado=ticket.estado,
            created_by=ticket.created_by
        )
    
    def _to_list_response(self, ticket: Ticket) -> TicketListResponse:
        """Convertir modelo Ticket a TicketListResponse."""
        return TicketListResponse(
            ticket_code=ticket.ticket_code,
            titulo=ticket.titulo,
            categoria=ticket.categoria,
            descripcion=ticket.descripcion,
            estado=ticket.estado,
            imagen=ticket.imagen,
            fecha_ticket=ticket.fecha_ticket
        )
