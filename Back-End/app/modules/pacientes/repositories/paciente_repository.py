from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError
from ..schemas import PacienteCreate, PacienteUpdate, PacienteSearch
from app.core.exceptions import ConflictError, NotFoundError


class PacienteRepository:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.collection = database.pacientes

    def _convert_doc_to_response(self, doc: dict) -> dict:
        if doc:
            doc["id"] = str(doc["_id"])
            doc["paciente_code"] = doc.get("paciente_code", "")
        return doc

    async def create(self, paciente: PacienteCreate) -> dict:
        try:
            paciente_data = paciente.dict()
            paciente_data["fecha_creacion"] = datetime.now(timezone.utc)
            paciente_data["fecha_actualizacion"] = datetime.now(timezone.utc)
            await self.collection.insert_one(paciente_data)
            created_patient = await self.collection.find_one({"paciente_code": paciente.paciente_code})
            if not created_patient:
                raise ConflictError("Error al crear el paciente")
            return self._convert_doc_to_response(dict(created_patient))
        except DuplicateKeyError:
            raise ConflictError(f"Ya existe un paciente con el código {paciente.paciente_code}")

    async def get_by_id(self, paciente_id: str) -> Optional[dict]:
        paciente = await self.collection.find_one({"paciente_code": paciente_id})
        return self._convert_doc_to_response(dict(paciente)) if paciente else None

    async def update(self, paciente_id: str, paciente_update: PacienteUpdate) -> dict:
        existing_patient = await self.collection.find_one({"paciente_code": paciente_id})
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")
        update_data = {k: v for k, v in paciente_update.dict().items() if v is not None}
        if update_data:
            update_data["fecha_actualizacion"] = datetime.now(timezone.utc)
            await self.collection.update_one({"paciente_code": paciente_id}, {"$set": update_data})
        updated_patient = await self.collection.find_one({"paciente_code": paciente_id})
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después de la actualización")
        return self._convert_doc_to_response(dict(updated_patient))

    async def change_code(self, old_code: str, new_code: str, casos_collection) -> dict:
        existing_patient = await self.collection.find_one({"paciente_code": old_code})
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")
        duplicated = await self.collection.find_one({"paciente_code": new_code})
        if duplicated:
            raise ConflictError(f"Ya existe un paciente con el código {new_code}")
        await self.collection.update_one(
            {"paciente_code": old_code},
            {"$set": {"paciente_code": new_code, "fecha_actualizacion": datetime.now(timezone.utc)}}
        )
        if casos_collection is not None:
            await casos_collection.update_many(
                {"paciente.paciente_code": old_code},
                {"$set": {"paciente.paciente_code": new_code}}
            )
        updated_patient = await self.collection.find_one({"paciente_code": new_code})
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después de cambiar el código")
        return self._convert_doc_to_response(dict(updated_patient))

    async def delete(self, paciente_id: str) -> bool:
        result = await self.collection.delete_one({"paciente_code": paciente_id})
        if result.deleted_count == 0:
            raise NotFoundError("Paciente no encontrado")
        return True

    async def list_with_filters(
        self,
        skip: int = 0,
        limit: int = 100,
        buscar: Optional[str] = None,
        entidad: Optional[str] = None,
        sexo: Optional[str] = None,
        tipo_atencion: Optional[str] = None
    ) -> List[dict]:
        filtro = {}
        if buscar:
            filtro["$or"] = [
                {"nombre": {"$regex": buscar, "$options": "i"}},
                {"paciente_code": {"$regex": str(buscar), "$options": "i"}}
            ]
        if entidad:
            filtro["entidad_info.nombre"] = {"$regex": entidad, "$options": "i"}
        if sexo:
            filtro["sexo"] = sexo
        if tipo_atencion:
            filtro["tipo_atencion"] = tipo_atencion
        cursor = self.collection.find(filtro).skip(skip).limit(limit).sort("fecha_creacion", -1)
        pacientes = await cursor.to_list(length=limit)
        return [self._convert_doc_to_response(p) for p in pacientes]

    async def advanced_search(self, search_params: PacienteSearch) -> Dict[str, Any]:
        filtro = {}
        if search_params.nombre:
            filtro["nombre"] = {"$regex": search_params.nombre, "$options": "i"}
        if search_params.paciente_code:
            filtro["paciente_code"] = {"$regex": search_params.paciente_code, "$options": "i"}
        if search_params.edad_min is not None or search_params.edad_max is not None:
            edad_filter = {}
            if search_params.edad_min is not None:
                edad_filter["$gte"] = search_params.edad_min
            if search_params.edad_max is not None:
                edad_filter["$lte"] = search_params.edad_max
            filtro["edad"] = edad_filter
        if hasattr(search_params, 'entidad') and search_params.entidad:
            filtro["entidad_info.nombre"] = {"$regex": search_params.entidad, "$options": "i"}
        if search_params.sexo:
            filtro["sexo"] = search_params.sexo.value
        if search_params.tipo_atencion:
            filtro["tipo_atencion"] = search_params.tipo_atencion.value
        if search_params.fecha_desde or search_params.fecha_hasta:
            fecha_filter = {}
            if search_params.fecha_desde:
                fecha_filter["$gte"] = datetime.fromisoformat(search_params.fecha_desde)
            if search_params.fecha_hasta:
                fecha_filter["$lte"] = datetime.fromisoformat(search_params.fecha_hasta + "T23:59:59")
            filtro["fecha_creacion"] = fecha_filter
        total = await self.collection.count_documents(filtro)
        cursor = self.collection.find(filtro).skip(search_params.skip).limit(search_params.limit).sort("fecha_creacion", -1)
        pacientes = await cursor.to_list(length=search_params.limit)
        return {
            "pacientes": [self._convert_doc_to_response(p) for p in pacientes],
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit
        }


    async def get_entidades_list(self) -> List[str]:
        entidades = await self.collection.distinct("entidad_info.nombre")
        return sorted(entidades)

    async def count_total(self) -> int:
        return await self.collection.count_documents({})

    async def exists(self, paciente_id: str) -> bool:
        count = await self.collection.count_documents({"paciente_code": paciente_id})
        return count > 0