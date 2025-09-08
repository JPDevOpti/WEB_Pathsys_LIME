"""Repositorio para casos de aprobación"""

from typing import List, Optional, Dict, Any, Tuple
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shared.repositories.base import BaseRepository
from app.modules.aprobacion.models.caso_aprobacion import CasoAprobacion, EstadoAprobacionEnum
from app.modules.aprobacion.schemas.caso_aprobacion import CasoAprobacionSearch, CasoAprobacionCreate, CasoAprobacionUpdate


class CasoAprobacionRepository(BaseRepository[CasoAprobacion, CasoAprobacionCreate, CasoAprobacionUpdate]):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "casos_aprobacion", CasoAprobacion)

    async def create(self, obj_in: CasoAprobacion) -> CasoAprobacion:
        data = obj_in.model_dump(by_alias=False) if hasattr(obj_in, 'model_dump') else obj_in
        data.setdefault("fecha_creacion", datetime.utcnow())
        data.pop("is_active", None)
        data.pop("isActive", None)
        data.pop("id", None)  # Remover id si existe para que MongoDB genere el _id
        result = await self.collection.insert_one(data)
        created = await self.collection.find_one({"_id": result.inserted_id})
        created['id'] = str(created['_id'])  # Agregar el id
        return CasoAprobacion(**created)

    async def find_by_caso_original(self, caso_original: str) -> Optional[CasoAprobacion]:
        doc = await self.collection.find_one({"caso_original": caso_original})
        return CasoAprobacion(**doc) if doc else None

    async def find_by_caso_original_with_id(self, caso_original: str) -> Tuple[Optional[dict], Optional[CasoAprobacion]]:
        doc = await self.collection.find_one({"caso_original": caso_original})
        if doc:
            return doc, CasoAprobacion(**doc)
        return None, None

    async def _build_search_query(self, search_params: CasoAprobacionSearch) -> Dict[str, Any]:
        q: Dict[str, Any] = {}
        if search_params.caso_original:
            q["caso_original"] = {"$regex": search_params.caso_original, "$options": "i"}
        if search_params.estado_aprobacion:
            q["estado_aprobacion"] = search_params.estado_aprobacion.value
        if search_params.fecha_solicitud_desde or search_params.fecha_solicitud_hasta:
            f: Dict[str, Any] = {}
            if search_params.fecha_solicitud_desde: f["$gte"] = search_params.fecha_solicitud_desde
            if search_params.fecha_solicitud_hasta: f["$lte"] = search_params.fecha_solicitud_hasta
            q["aprobacion_info.fecha_solicitud"] = f
        if search_params.fecha_aprobacion_desde or search_params.fecha_aprobacion_hasta:
            f: Dict[str, Any] = {}
            if search_params.fecha_aprobacion_desde: f["$gte"] = search_params.fecha_aprobacion_desde
            if search_params.fecha_aprobacion_hasta: f["$lte"] = search_params.fecha_aprobacion_hasta
            q["aprobacion_info.fecha_aprobacion"] = f
        return q

    async def search(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacion]:
        q = await self._build_search_query(search_params)
        cursor = self.collection.find(q).skip(skip).limit(limit).sort("fecha_creacion", -1)
        docs = await cursor.to_list(length=limit)
        result = []
        for d in docs:
            d['id'] = str(d['_id'])  # Agregar el id al documento
            result.append(CasoAprobacion(**d))
        return result

    async def count(self, search_params: CasoAprobacionSearch) -> int:
        q = await self._build_search_query(search_params)
        return await self.collection.count_documents(q)

    async def get_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacion]:
        cursor = self.collection.find({"estado_aprobacion": estado.value}).limit(limit).sort("fecha_creacion", -1)
        docs = await cursor.to_list(length=limit)
        result = []
        for d in docs:
            d['id'] = str(d['_id'])  # Agregar el id al documento
            result.append(CasoAprobacion(**d))
        return result

    async def update_estado(self, caso_id: str, nuevo_estado: EstadoAprobacionEnum) -> bool:
        update_data = {"estado_aprobacion": nuevo_estado.value}
        if nuevo_estado == EstadoAprobacionEnum.PENDIENTE_APROBACION:
            update_data["aprobacion_info.fecha_gestion"] = datetime.utcnow()
        result = await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        return result.modified_count > 0

    async def update_fecha_aprobacion(self, caso_id: str) -> bool:
        update_data = {"aprobacion_info.fecha_aprobacion": datetime.utcnow()}
        result = await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        return result.modified_count > 0

    async def update_pruebas_complementarias(self, caso_id: str, pruebas_complementarias: list) -> Optional[CasoAprobacion]:
        update_data = {"pruebas_complementarias": pruebas_complementarias}
        result = await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        if result.modified_count > 0:
            return await self.get(caso_id)
        return None

    async def get_stats(self) -> Dict[str, Any]:
        pipeline = [{"$group": {"_id": "$estado_aprobacion", "count": {"$sum": 1}}}]
        res = await self.collection.aggregate(pipeline).to_list(length=None)
        stats = {"total_casos": 0, "casos_solicitud_hecha": 0, "casos_pendientes_aprobacion": 0, "casos_aprobados": 0, "casos_rechazados": 0}
        for it in res:
            estado, count = it.get("_id"), it.get("count", 0)
            stats["total_casos"] += count
            if estado == EstadoAprobacionEnum.SOLICITUD_HECHA.value: stats["casos_solicitud_hecha"] = count
            elif estado == EstadoAprobacionEnum.PENDIENTE_APROBACION.value: stats["casos_pendientes_aprobacion"] = count
            elif estado == EstadoAprobacionEnum.APROBADO.value: stats["casos_aprobados"] = count
            elif estado == EstadoAprobacionEnum.RECHAZADO.value: stats["casos_rechazados"] = count
        return stats
