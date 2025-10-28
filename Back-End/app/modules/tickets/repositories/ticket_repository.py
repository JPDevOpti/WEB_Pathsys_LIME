"""Repository for ticket CRUD operations."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timezone
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.shared.repositories.base import BaseRepository
from app.modules.tickets.models.ticket import Ticket
from app.modules.tickets.schemas.ticket import TicketCreate, TicketUpdate, TicketSearch


class TicketRepository(BaseRepository[Ticket, TicketCreate, TicketUpdate]):
    """Repository for ticket CRUD operations."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "tickets", Ticket)

    def _normalize_boolean_fields_for_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Override method for tickets: NO add is_active/isActive fields"""
        return data

    async def create(self, obj_in: Any) -> Ticket:
        """Create a new ticket WITHOUT is_active/isActive fields"""
        if isinstance(obj_in, dict):
            obj_data = dict(obj_in)
        elif hasattr(obj_in, 'model_dump'):
            obj_data = obj_in.model_dump(by_alias=False)
        else:
            obj_data = obj_in.dict(by_alias=False)
        
        obj_data.setdefault("created_at", datetime.now(timezone.utc))
        obj_data["updated_at"] = datetime.now(timezone.utc)
        obj_data.setdefault("ticket_date", datetime.now(timezone.utc))
        
        # NO add is_active/isActive fields for tickets
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
                raise ValueError("Error retrieving created ticket")
        except Exception as e:
            raise ValueError(f"Error creating ticket: {str(e)}")

    async def update(self, id: Any, obj_in: TicketUpdate) -> Optional[Ticket]:
        """Update an existing ticket"""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(by_alias=False, exclude_unset=True)
        else:
            update_data = obj_in.dict(by_alias=False, exclude_unset=True)
        
        if not update_data:
            return await self.get(id)
        
        update_data["updated_at"] = datetime.now(timezone.utc)
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
            raise ValueError(f"Error updating ticket: {str(e)}")

    async def get_by_ticket_code(self, ticket_code: str) -> Optional[Ticket]:
        """Get ticket by its unique code."""
        try:
            document = await self.collection.find_one({"ticket_code": ticket_code})
            if document:
                document.pop("is_active", None)
                document.pop("isActive", None)
                return self.model_class(**document)
            return None
        except Exception as e:
            raise ValueError(f"Error searching ticket by code: {str(e)}")

    async def update_by_ticket_code(self, ticket_code: str, obj_in: TicketUpdate) -> Optional[Ticket]:
        """Update ticket by its unique code."""
        if hasattr(obj_in, 'model_dump'):
            update_data = obj_in.model_dump(by_alias=False, exclude_unset=True)
        else:
            update_data = obj_in.dict(by_alias=False, exclude_unset=True)
        
        if not update_data:
            return await self.get_by_ticket_code(ticket_code)
        
        update_data["updated_at"] = datetime.now(timezone.utc)
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
            raise ValueError(f"Error updating ticket: {str(e)}")

    async def delete_by_ticket_code(self, ticket_code: str) -> bool:
        """Delete ticket by its unique code."""
        try:
            result = await self.collection.delete_one({"ticket_code": ticket_code})
            return result.deleted_count > 0
        except Exception as e:
            raise ValueError(f"Error deleting ticket: {str(e)}")

    async def search_tickets(
        self, 
        search_params: TicketSearch,
        skip: int = 0,
        limit: int = 20,
        sort_by: str = "ticket_date",
        sort_order: str = "desc"
    ) -> List[Ticket]:
        """Advanced ticket search with filters and pagination."""
        try:
            # Build filters
            query = {}
            
            if search_params.status:
                query["status"] = search_params.status
            
            if search_params.category:
                query["category"] = search_params.category
            
            if search_params.created_by:
                query["created_by"] = search_params.created_by
            
            if search_params.search_text:
                query["$or"] = [
                    {"title": {"$regex": search_params.search_text, "$options": "i"}},
                    {"description": {"$regex": search_params.search_text, "$options": "i"}}
                ]
            
            if search_params.date_from or search_params.date_to:
                date_filter = {}
                if search_params.date_from:
                    date_filter["$gte"] = search_params.date_from
                if search_params.date_to:
                    date_filter["$lte"] = search_params.date_to
                query["ticket_date"] = date_filter
            
            # Configure sorting
            sort_direction = -1 if sort_order.lower() == "desc" else 1
            sort_criteria = [(sort_by, sort_direction)]
            
            # Execute query
            cursor = self.collection.find(query).sort(sort_criteria).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Clean and convert to models
            tickets = []
            for doc in documents:
                doc.pop("is_active", None)
                doc.pop("isActive", None)
                tickets.append(self.model_class(**doc))
            
            return tickets
            
        except Exception as e:
            raise ValueError(f"Error in ticket search: {str(e)}")

    async def count_tickets(self, search_params: TicketSearch) -> int:
        """Count tickets that match the filters."""
        try:
            # Use the same filter logic as in search_tickets
            query = {}
            
            if search_params.status:
                query["status"] = search_params.status
            
            if search_params.category:
                query["category"] = search_params.category
            
            if search_params.created_by:
                query["created_by"] = search_params.created_by
            
            if search_params.search_text:
                query["$or"] = [
                    {"title": {"$regex": search_params.search_text, "$options": "i"}},
                    {"description": {"$regex": search_params.search_text, "$options": "i"}}
                ]
            
            if search_params.date_from or search_params.date_to:
                date_filter = {}
                if search_params.date_from:
                    date_filter["$gte"] = search_params.date_from
                if search_params.date_to:
                    date_filter["$lte"] = search_params.date_to
                query["ticket_date"] = date_filter
            
            return await self.collection.count_documents(query)
            
        except Exception as e:
            raise ValueError(f"Error counting tickets: {str(e)}")

    async def get_tickets_by_user(self, user_id: str, skip: int = 0, limit: int = 20) -> List[Ticket]:
        """Get tickets created by a specific user."""
        try:
            cursor = self.collection.find({"created_by": user_id}) \
                .sort("ticket_date", -1) \
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
            raise ValueError(f"Error getting user tickets: {str(e)}")

    async def list_all_tickets(
        self, 
        skip: int = 0, 
        limit: int = 20,
        sort_by: str = "ticket_date",
        sort_order: str = "desc"
    ) -> List[Ticket]:
        """List all tickets with pagination and sorting."""
        try:
            # Configure sorting
            sort_direction = -1 if sort_order.lower() == "desc" else 1
            sort_criteria = [(sort_by, sort_direction)]
            
            # Execute query
            cursor = self.collection.find({}).sort(sort_criteria).skip(skip).limit(limit)
            documents = await cursor.to_list(length=limit)
            
            # Clean and convert to models
            tickets = []
            for doc in documents:
                # Clean unwanted fields
                doc.pop("is_active", None)
                doc.pop("isActive", None)
                
                # Verify required fields are present
                if "ticket_code" not in doc or "created_by" not in doc:
                    print(f"Warning: Document with missing fields: {doc.get('_id', 'unknown')}")
                    continue
                
                try:
                    tickets.append(self.model_class(**doc))
                except Exception as e:
                    print(f"Error converting document to model: {e}")
                    print(f"Problematic document: {doc}")
                    continue
            
            return tickets
            
        except Exception as e:
            raise ValueError(f"Error listing tickets: {str(e)}")

    async def initialize_indexes(self):
        """Create indexes to optimize queries."""
        await self.collection.create_index("ticket_code", unique=True)  # MAIN - unique
        await self.collection.create_index([("created_by", 1), ("ticket_date", -1)])
        await self.collection.create_index([("status", 1), ("category", 1)])
        await self.collection.create_index([("title", "text"), ("description", "text")])
