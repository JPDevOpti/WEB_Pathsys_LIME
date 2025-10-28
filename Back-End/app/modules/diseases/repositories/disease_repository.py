from typing import List, Optional, Dict, Any
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from datetime import datetime, timezone
from app.modules.diseases.models.disease import DiseaseCreate, DiseaseResponse


class DiseaseRepository:
    """Repository for disease operations"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.diseases
    
    def _convert_objectid_to_string(self, doc: dict) -> dict:
        """Convert ObjectId to string in document"""
        if doc and "_id" in doc:
            doc["_id"] = str(doc["_id"])
        return doc
    
    async def create(self, disease: DiseaseCreate) -> DiseaseResponse:
        """Create a new disease"""
        disease_dict = disease.model_dump()
        disease_dict["created_at"] = datetime.now(timezone.utc)
        disease_dict["updated_at"] = datetime.now(timezone.utc)
        
        result = await self.collection.insert_one(disease_dict)
        disease_dict["_id"] = str(result.inserted_id)
        
        return DiseaseResponse(**disease_dict)
    
    async def get_by_code(self, code: str) -> Optional[DiseaseResponse]:
        """Get disease by code"""
        document = await self.collection.find_one({"code": code})
        if document:
            document = self._convert_objectid_to_string(document)
            return DiseaseResponse(**document)
        return None
    
    async def get_all(
        self, 
        skip: int = 0, 
        limit: int = 100,
        is_active: Optional[bool] = None
    ) -> List[DiseaseResponse]:
        """Get all diseases with pagination"""
        filter_query = {}
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        diseases = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                disease = DiseaseResponse(**doc)
                diseases.append(disease)
            except Exception as e:
                print(f"Error converting document: {e}")
                continue
        
        return diseases
    
    async def search_by_name(
        self, 
        name: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DiseaseResponse]:
        """Search diseases by name"""
        filter_query = {
            "name": {"$regex": name, "$options": "i"},
            "is_active": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        diseases = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                disease = DiseaseResponse(**doc)
                diseases.append(disease)
            except Exception as e:
                print(f"Error converting document: {e}")
                continue
        
        return diseases
    
    async def search_by_code(
        self, 
        code: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DiseaseResponse]:
        """Search diseases by code"""
        filter_query = {
            "code": {"$regex": code, "$options": "i"},
            "is_active": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        diseases = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                disease = DiseaseResponse(**doc)
                diseases.append(disease)
            except Exception as e:
                print(f"Error converting document: {e}")
                continue
        
        return diseases
    
    async def get_by_table(
        self, 
        table: str, 
        skip: int = 0, 
        limit: int = 100
    ) -> List[DiseaseResponse]:
        """Get diseases by reference table"""
        filter_query = {
            "table": table,
            "is_active": True
        }
        
        cursor = self.collection.find(filter_query).skip(skip).limit(limit)
        documents = await cursor.to_list(length=limit)
        
        diseases = []
        for doc in documents:
            doc = self._convert_objectid_to_string(doc)
            try:
                disease = DiseaseResponse(**doc)
                diseases.append(disease)
            except Exception as e:
                print(f"Error converting document: {e}")
                continue
        
        return diseases
    
    async def delete(self, disease_id: str) -> bool:
        """Delete a disease permanently"""
        try:
            obj_id = ObjectId(disease_id)
            result = await self.collection.delete_one({"_id": obj_id})
            return result.deleted_count > 0
        except Exception:
            return False
    
    async def count_total(self, is_active: Optional[bool] = None) -> int:
        """Count total diseases"""
        filter_query = {}
        if is_active is not None:
            filter_query["is_active"] = is_active
        
        return await self.collection.count_documents(filter_query)
    
    async def exists_by_code(self, code: str) -> bool:
        """Check if a disease with the given code exists"""
        count = await self.collection.count_documents({"code": code})
        return count > 0
