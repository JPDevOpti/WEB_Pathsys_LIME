"""Repositorio para operaciones CRUD de tickets."""

from typing import Optional, List, Dict, Any
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.shared.repositories.base import BaseRepository
from app.modules.tickets.models.ticket import Ticket
from app.modules.tickets.schemas.ticket import TicketCreate, TicketUpdate, TicketSearch


class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate]):
    """Repositorio para operaciones CRUD de tickets."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "tickets", Ticket)

    def _normalize_boolean_fields_for_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Sobrescribir método para tickets: NO agregar campos is_active/isActive"""
        return data

    async def create(self, obj_in: Any) -> Ticket:
        """Crear un nuevo ticket SIN campos is_active/isActive"""
        if isinstance(obj_in, dict):
            obj_data = dict(obj_in)
        elif hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False)
        else:
            obj_data = obj_in.dict(by_alias=False)
        
        obj_data.setdefault("fecha_creacion", datetime.utcnow())
        obj_data["fecha_actualizacion"] = datetime.utcnow()
        obj_data.setdefault("fecha_ticket", datetime.utcnow())
        
        # NO agregar campos is_active/isActive para tickets
        obj_data.pop("is_active", None)
        obj_data.pop("isActive", None)
        
        try:
            result = await self.collection.insert_one(obj_data)
            created_obj = await self.collection.find_one({"_id": result.inserted_id})
            if created_obj:
                created_obj.pop("is_active", None)
                created_obj.pop("isActive", None)
                return self.model_class(**created_obj)
            else:
                raise ValueError("Error al recuperar el ticket creado")
        except Exception as e:
            raise ValueError(f"Error al crear el ticket: {str(e)}")

    async def update(self, id: Any, obj_in: TicketUpdate) -> Optional[Ticket]:
        """Actualizar un ticket existente"""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(by_alias=False, exclude_unset=True)
        else:
            update_data = obj_in.dict(by_alias=False, exclude_unset=True)
        
        if not update_data:
            return await self.get(id)
        
        update_data["fecha_actualizacion"] = datetime.utcnow()
        update_data.pop("is_active", None)
        update_data.pop("isActive", None)
        
        query = {"_id": ObjectId(id)} if isinstance(id, str) else {"_id": id}
        
        try:
            result = await self.collection.find_one_and_update(
                query,
                {"$set": update_data},
                return_document=True
            )
            if result:
                result.pop("is_active", None)
                result.pop("isActive", None)
                return self.model_class(**result)
            return None
        except Exception as e:
            raise ValueError(f"Error al actualizar el ticket: {str(e)}")

    async def get_by_ticket_code(self, ticket_code: str) -> Optional[Ticket]:
        """Obtener ticket por su código único."""
        try:
            document = await self.collection.find_one({"ticket_code": ticket_code})
            if document:
                document.pop("is_active", None)
                document.pop("isActive", None)
                return self.model_class(**document)
            return None
        except Exception as e:
            raise ValueError(f"Error al buscar ticket por código: {str(e)}")

    async def update_by_ticket_code(self, ticket_code: str, obj_in: TicketUpdate) -> Optional[Ticket]:
        """Actualizar ticket por su código único."""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(by_alias=False, exclude_unset=True)
        else:
            update_data = obj_in.dict(by_alias=False, exclude_unset=True)
        
        if not update_data:
            return await self.get_by_ticket_code(ticket_code)
        
        update_data["fecha_actualizacion"] = datetime.utcnow()
        update_data.pop("is_active", None)
        update_data.pop("isActive", None)
        
        try:
            result = await self.collection.find_one_and_update(
                {"ticket_code": ticket_code},
                {"$set": update_data},
                return_document=True
            )
            if result:
                result.pop("is_active", None)
                result.pop("isActive", None)
                return self.model_class(**result)
            return None
        except Exception as e:
            raise ValueError(f"Error al actualizar ticket: {str(e)}")

    async def delete_by_ticket_code(self, ticket_code: str) -> bool:
        """Eliminar ticket por su código único."""
        try:
            result = await self.collection.delete_one({"ticket_code": ticket_code})
            return result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Error al eliminar ticket: {str(e)}")

    async def search_tickets(
        self, 
        search_params: TicketSearch,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "fecha_ticket",
        sort_order: str = "desc"
    ) -> List[Ticket]:
        """Búsqueda avanzada de tickets con filtros y paginación."""
        try:
            # Construir filtros
            query = {}
            
            if search_params.estado:
                query["estado"] = search_params.estado
            
            if search_params.categoria:
                query["categoria"] = search_params.categoria
            
            if search_params.created_by:
                query["created_by"] = search_params.created_by
            
            if search_params.search_text:
                query["$or"] = [
                    {"titulo": {"$regex": search_params.search_text, "$options": "i"}},
                    {"descripcion": {"$regex": search_params.search_text, "$options": "i"}}
                ]
            
            if search_params.date_from or search_params.date_to:
                date_filter = {}
                if search_params.date_from:
                    date_filter["$gte"] = search_params.date_from
                if search_params.date_to:
                    date_filter["$lte"] = search_params.date_to
                query["fecha_ticket"] = date_filter
            
            # Configurar ordenamiento
            sort_direction = -1 if sort_order.lower() == "desc" else 1
            sort_criteria = [(sort_by, sort_direction)]
            
            # Ejecutar consulta
            cursor = self.collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Limpiar y convertir a modelos
            tickets = []
            for doc in documents:
                doc.pop("is_active", None)
                doc.pop("isActive", None)
                tickets.append(self.model_class(**doc))
            
            return tickets
            
        except Exception as e:
            raise ValueError(f"Error en búsqueda de tickets: {str(e)}")

    async def count_tickets(self, search_params: TicketSearch) -> int:
        """Contar tickets que coinciden con los filtros."""
        try:
            # Usar la misma lógica de filtros que en search_tickets
            query = {}
            
            if search_params.estado:
                query["estado"] = search_params.estado
            
            if search_params.categoria:
                query["categoria"] = search_params.categoria
            
            if search_params.created_by:
                query["created_by"] = search_params.created_by
            
            if search_params.search_text:
                query["$or"] = [
                    {"titulo": {"$regex": search_params.search_text, "$options": "i"}},
                    {"descripcion": {"$regex": search_params.search_text, "$options": "i"}}
                ]
            
            if search_params.date_from or search_params.date_to:
                date_filter = {}
                if search_params.date_from:
                    date_filter["$gte"] = search_params.date_from
                if search_params.date_to:
                    date_filter["$lte"] = search_params.date_to
                query["fecha_ticket"] = date_filter
            
            return await self.collection.count_documents(query)
            
        except Exception as e:
            raise ValueError(f"Error al contar tickets: {str(e)}")

    async def get_tickets_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Ticket]:
        """Obtener tickets creados por un usuario específico."""
        try:
            cursor = self.collection.find({"created_by": user_id}) \
                .sort("fecha_ticket", -1) \
                .skip(skip) \
                .limit(limit)
            
            documents = await cursor.to_list(length=limit)
            
            tickets = []
            for doc in documents:
                doc.pop("is_active", None)
                doc.pop("isActive", None)
                tickets.append(self.model_class(**doc))
            
            return tickets
            
        except Exception as e:
            raise ValueError(f"Error al obtener tickets del usuario: {str(e)}")

    async def listar_todos_tickets(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "fecha_ticket",
        sort_order: str = "desc"
    ) -> List[Ticket]:
        """Listar todos los tickets con paginación y ordenamiento."""
        try:
            # Configurar ordenamiento
            sort_direction = -1 if sort_order.lower() == "desc" else 1
            sort_criteria = [(sort_by, sort_direction)]
            
            # Ejecutar consulta
            cursor = self.collection.find({}).sort(sort_criteria).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Limpiar y convertir a modelos
            tickets = []
            for doc in documents:
                # Limpiar campos no deseados
                doc.pop("is_active", None)
                doc.pop("isActive", None)
                
                # Verificar que los campos requeridos estén presentes
                if "ticket_code" not in doc or "created_by" not in doc:
                    print(f"Warning: Documento con campos faltantes: {doc.get('_id', 'unknown')}")
                    continue
                
                try:
                    tickets.append(self.model_class(**doc))
                except Exception as e:
                    print(f"Error al convertir documento a modelo: {e}")
                    print(f"Documento problemático: {doc}")
                    continue
            
            return tickets
            
        except Exception as e:
            raise ValueError(f"Error al listar tickets: {str(e)}")

    async def inicializar_indices(self):
        """Crear índices para optimizar consultas."""
        await self.collection.create_index("ticket_code", unique=True)  # PRINCIPAL - único
        await self.collection.create_index([("created_by", 1), ("fecha_ticket", -1)])
        await self.collection.create_index([("estado", 1), ("categoria", 1)])
        await self.collection.create_index([("titulo", "text"), ("descripcion", "text")])
