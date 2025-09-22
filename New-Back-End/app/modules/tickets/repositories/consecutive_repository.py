"""Repository for ticket consecutive number management."""

from typing import Optional, List
from datetime import datetime
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from app.modules.tickets.models.consecutive import ConsecutiveTicket


class ConsecutiveTicketRepository:
    """Repository for CRUD operations of ticket consecutives."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.consecutive_tickets
        
    async def initialize_indexes(self):
        """Create unique indexes to optimize queries."""
        await self.collection.create_index("year", unique=True)
    
    async def get_next_number(self, year: int) -> int:
        """Get the next consecutive number atomically."""
        self._validate_year(year)
        
        result = await self.collection.find_one_and_update(
            {"year": year},
            {
                "$inc": {"last_number": 1},
                "$set": {"updated_at": datetime.utcnow()}
            },
            upsert=True,
            return_document=True
        )
        
        return result["last_number"] if result else 1
    
    async def get_next_number_preview(self, year: int) -> int:
        """Query what the next consecutive number will be WITHOUT incrementing it."""
        self._validate_year(year)
        document = await self.collection.find_one({"year": year}, {"last_number": 1})
        return document["last_number"] + 1 if document else 1
    
    async def get_consecutive_by_year(self, year: int) -> Optional[ConsecutiveTicket]:
        """Get consecutive information for a specific year."""
        self._validate_year(year)
        document = await self.collection.find_one({"year": year})
        return ConsecutiveTicket(**document) if document else None
    
    async def create_consecutive_year(self, year: int, initial_number: int = 0) -> ConsecutiveTicket:
        """Create a new consecutive control for a year."""
        self._validate_year(year)
        self._validate_initial_number(initial_number)
        
        consecutive_data = {
            "year": year,
            "last_number": initial_number,
            "updated_at": datetime.utcnow()
        }
        
        try:
            await self.collection.insert_one(consecutive_data)
            return ConsecutiveTicket(**consecutive_data)
        except DuplicateKeyError:
            raise ValueError(f"Consecutive for year {year} already exists")
    
    async def list_all_consecutives(self) -> List[ConsecutiveTicket]:
        """List all consecutives by year."""
        cursor = self.collection.find({}, {"_id": 0}).sort("year", -1)
        documents = await cursor.to_list(length=None)
        return [ConsecutiveTicket(**doc) for doc in documents]
    
    async def reset_consecutive_year(self, year: int, new_number: int = 0) -> bool:
        """Reset the consecutive for a specific year."""
        self._validate_year(year)
        self._validate_initial_number(new_number)
        
        result = await self.collection.update_one(
            {"year": year},
            {"$set": {"last_number": new_number, "updated_at": datetime.utcnow()}}
        )
        return result.modified_count > 0
    
    async def generate_ticket_code(self, year: int) -> str:
        """Generate complete ticket code (T-YYYY-NNN)."""
        number = await self.get_next_number(year)
        return f"T-{year}-{number:03d}"
    
    async def get_consecutive_statistics(self) -> dict:
        """Get statistics of all consecutives."""
        pipeline = [
            {
                "$group": {
                    "_id": None,
                    "total_years": {"$sum": 1},
                    "total_tickets": {"$sum": "$last_number"},
                    "min_year": {"$min": "$year"},
                    "max_year": {"$max": "$year"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(1)
        if result:
            stats = result[0]
            stats.pop("_id")
            return stats
        
        return {
            "total_years": 0,
            "total_tickets": 0,
            "min_year": None,
            "max_year": None
        }
    
    def _validate_year(self, year: int) -> None:
        """Validate that the year is in the allowed range."""
        current_year = datetime.now().year
        if year < 2000 or year > current_year + 5:
            raise ValueError(f"Year must be between 2000 and {current_year + 5}")
    
    def _validate_initial_number(self, number: int) -> None:
        """Validate the initial number."""
        if number < 0:
            raise ValueError("Initial number cannot be negative")
        if number > 999999:
            raise ValueError("Initial number exceeds allowed limit")
