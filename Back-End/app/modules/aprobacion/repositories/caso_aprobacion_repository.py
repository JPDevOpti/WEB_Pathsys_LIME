"""Repositorio para casos de aprobación"""

from typing import List, Optional, Dict, Any
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
        data["fecha_actualizacion"] = datetime.utcnow()
        data.pop("is_active", None)
        data.pop("isActive", None)
        result = await self.collection.insert_one(data)
        created = await self.collection.find_one({"_id": result.inserted_id})
        return CasoAprobacion(**created)

    async def find_by_caso_original(self, caso_original: str) -> Optional[CasoAprobacion]:
        doc = await self.collection.find_one({"caso_original": caso_original})
        return CasoAprobacion(**doc) if doc else None

    async def _build_search_query(self, search_params: CasoAprobacionSearch) -> Dict[str, Any]:
        q: Dict[str, Any] = {}
        if search_params.caso_original:
            q["caso_original"] = {"$regex": search_params.caso_original, "$options": "i"}
        if search_params.estado_aprobacion:
            q["estado_aprobacion"] = search_params.estado_aprobacion.value
        if search_params.solicitado_por:
            q["aprobacion_info.solicitado_por"] = {"$regex": search_params.solicitado_por, "$options": "i"}
        if search_params.aprobado_por:
            q["aprobacion_info.aprobado_por"] = {"$regex": search_params.aprobado_por, "$options": "i"}
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
        return [CasoAprobacion(**d) for d in docs]

    async def count(self, search_params: CasoAprobacionSearch) -> int:
        q = await self._build_search_query(search_params)
        return await self.collection.count_documents(q)

    async def get_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacion]:
        cursor = self.collection.find({"estado_aprobacion": estado.value}).limit(limit).sort("fecha_creacion", -1)
        docs = await cursor.to_list(length=limit)
        return [CasoAprobacion(**d) for d in docs]

    async def update_estado(self, caso_id: str, nuevo_estado: EstadoAprobacionEnum, usuario_id: str, comentarios: Optional[str] = None) -> bool:
        update_data: Dict[str, Any] = {
            "estado_aprobacion": nuevo_estado.value,
            "fecha_actualizacion": datetime.utcnow()
        }
        if nuevo_estado == EstadoAprobacionEnum.GESTIONANDO:
            update_data["aprobacion_info.gestionado_por"] = usuario_id
            update_data["aprobacion_info.fecha_gestion"] = datetime.utcnow()
            if comentarios: update_data["aprobacion_info.comentarios_gestion"] = comentarios
        elif nuevo_estado in [EstadoAprobacionEnum.APROBADO, EstadoAprobacionEnum.RECHAZADO]:
            update_data["aprobacion_info.aprobado_por"] = usuario_id
            update_data["aprobacion_info.fecha_aprobacion"] = datetime.utcnow()
            if comentarios: update_data["aprobacion_info.comentarios_aprobacion"] = comentarios
        result = await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        return result.modified_count > 0

    async def get_stats(self) -> Dict[str, Any]:
        pipeline = [{"$group": {"_id": "$estado_aprobacion", "count": {"$sum": 1}}}]
        res = await self.collection.aggregate(pipeline).to_list(length=None)
        stats = {"total_casos": 0, "casos_pendientes": 0, "casos_gestionando": 0, "casos_aprobados": 0, "casos_rechazados": 0}
        for it in res:
            estado, count = it.get("_id"), it.get("count", 0)
            stats["total_casos"] += count
            if estado == EstadoAprobacionEnum.PENDIENTE.value: stats["casos_pendientes"] = count
            elif estado == EstadoAprobacionEnum.GESTIONANDO.value: stats["casos_gestionando"] = count
            elif estado == EstadoAprobacionEnum.APROBADO.value: stats["casos_aprobados"] = count
            elif estado == EstadoAprobacionEnum.RECHAZADO.value: stats["casos_rechazados"] = count
        return stats
