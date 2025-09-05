"""Repositorio para casos de aprobación"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.shared.repositories.base import BaseRepository
from app.modules.aprobacion.models.caso_aprobacion import CasoAprobacion, EstadoAprobacionEnum
from app.modules.aprobacion.schemas.caso_aprobacion import CasoAprobacionSearch, CasoAprobacionCreate, CasoAprobacionUpdate


class CasoAprobacionRepository(BaseRepository[CasoAprobacion, CasoAprobacionCreate, CasoAprobacionUpdate]):
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "casos_aprobacion", CasoAprobacion)

    async def find_by_caso_original(self, caso_original: str) -> Optional[CasoAprobacion]:
        """Buscar caso de aprobación por código del caso original"""
        document = await self.collection.find_one({
            "caso_original": caso_original,
            "is_active": True
        })
        return CasoAprobacion(**document) if document else None

    async def find_by_caso_aprobacion(self, caso_aprobacion: str) -> Optional[CasoAprobacion]:
        """Buscar caso de aprobación por código de aprobación"""
        document = await self.collection.find_one({
            "caso_aprobacion": caso_aprobacion,
            "is_active": True
        })
        return CasoAprobacion(**document) if document else None

    async def search_active_only(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacion]:
        """Buscar solo casos de aprobación activos"""
        query = await self._build_search_query(search_params, active_only=True)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1)
        documents = await cursor.to_list(length=limit)
        
        return [CasoAprobacion(**doc) for doc in documents]

    async def search_all(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacion]:
        """Buscar todos los casos de aprobación (incluye inactivos)"""
        query = await self._build_search_query(search_params, active_only=False)
        
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1)
        documents = await cursor.to_list(length=limit)
        
        return [CasoAprobacion(**doc) for doc in documents]

    async def count_active_only(self, search_params: CasoAprobacionSearch) -> int:
        """Contar casos de aprobación activos"""
        query = await self._build_search_query(search_params, active_only=True)
        return await self.collection.count_documents(query)

    async def count_all(self, search_params: CasoAprobacionSearch) -> int:
        """Contar todos los casos de aprobación"""
        query = await self._build_search_query(search_params, active_only=False)
        return await self.collection.count_documents(query)

    async def _build_search_query(self, search_params: CasoAprobacionSearch, active_only: bool = True) -> Dict[str, Any]:
        """Construir query de búsqueda"""
        query = {}
        
        # Filtro de activos
        if active_only:
            query["is_active"] = True
        elif not search_params.incluir_inactivos:
            query["is_active"] = True

        # Búsqueda general
        if search_params.query:
            query["$or"] = [
                {"caso_aprobacion": {"$regex": search_params.query, "$options": "i"}},
                {"caso_original": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.nombre": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.paciente_code": {"$regex": search_params.query, "$options": "i"}},
                {"aprobacion_info.motivo": {"$regex": search_params.query, "$options": "i"}}
            ]

        # Filtros específicos
        if search_params.caso_code:
            query["caso_original"] = {"$regex": search_params.caso_code, "$options": "i"}
        
        if search_params.caso_aprobacion:
            query["caso_aprobacion"] = {"$regex": search_params.caso_aprobacion, "$options": "i"}
        
        if search_params.paciente_code:
            query["paciente.paciente_code"] = {"$regex": search_params.paciente_code, "$options": "i"}
        
        if search_params.paciente_nombre:
            query["paciente.nombre"] = {"$regex": search_params.paciente_nombre, "$options": "i"}
        
        if search_params.estado_aprobacion:
            query["estado_aprobacion"] = search_params.estado_aprobacion.value
        
        if search_params.solicitado_por:
            query["aprobacion_info.solicitado_por"] = {"$regex": search_params.solicitado_por, "$options": "i"}
        
        if search_params.aprobado_por:
            query["aprobacion_info.aprobado_por"] = {"$regex": search_params.aprobado_por, "$options": "i"}

        # Filtros de fecha
        if search_params.fecha_solicitud_desde or search_params.fecha_solicitud_hasta:
            fecha_query = {}
            if search_params.fecha_solicitud_desde:
                fecha_query["$gte"] = search_params.fecha_solicitud_desde
            if search_params.fecha_solicitud_hasta:
                fecha_query["$lte"] = search_params.fecha_solicitud_hasta
            query["aprobacion_info.fecha_solicitud"] = fecha_query

        if search_params.fecha_aprobacion_desde or search_params.fecha_aprobacion_hasta:
            fecha_query = {}
            if search_params.fecha_aprobacion_desde:
                fecha_query["$gte"] = search_params.fecha_aprobacion_desde
            if search_params.fecha_aprobacion_hasta:
                fecha_query["$lte"] = search_params.fecha_aprobacion_hasta
            query["aprobacion_info.fecha_aprobacion"] = fecha_query

        return query

    async def get_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacion]:
        """Obtener casos por estado de aprobación"""
        cursor = self.collection.find({
            "estado_aprobacion": estado.value,
            "is_active": True
        }).limit(limit).sort("fecha_creacion", -1)
        
        documents = await cursor.to_list(length=limit)
        return [CasoAprobacion(**doc) for doc in documents]

    async def get_pendientes_por_usuario(self, usuario_id: str, limit: int = 50) -> List[CasoAprobacion]:
        """Obtener casos pendientes para un usuario específico"""
        cursor = self.collection.find({
            "aprobacion_info.solicitado_por": usuario_id,
            "estado_aprobacion": EstadoAprobacionEnum.PENDIENTE.value,
            "is_active": True
        }).limit(limit).sort("fecha_creacion", -1)
        
        documents = await cursor.to_list(length=limit)
        return [CasoAprobacion(**doc) for doc in documents]

    async def get_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de casos de aprobación"""
        pipeline = [
            {"$match": {"is_active": True}},
            {"$group": {
                "_id": "$estado_aprobacion",
                "count": {"$sum": 1}
            }}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        stats = {
            "total_casos": 0,
            "casos_pendientes": 0,
            "casos_gestionando": 0,
            "casos_aprobados": 0,
            "casos_rechazados": 0
        }
        
        for item in result:
            estado = item["_id"]
            count = item["count"]
            stats["total_casos"] += count
            
            if estado == EstadoAprobacionEnum.PENDIENTE.value:
                stats["casos_pendientes"] = count
            elif estado == EstadoAprobacionEnum.GESTIONANDO.value:
                stats["casos_gestionando"] = count
            elif estado == EstadoAprobacionEnum.APROBADO.value:
                stats["casos_aprobados"] = count
            elif estado == EstadoAprobacionEnum.RECHAZADO.value:
                stats["casos_rechazado"] = count
        
        return stats

    async def update_estado(self, caso_id: str, nuevo_estado: EstadoAprobacionEnum, usuario_id: str, comentarios: Optional[str] = None) -> bool:
        """Actualizar estado de un caso de aprobación"""
        update_data = {
            "estado_aprobacion": nuevo_estado.value,
            "fecha_actualizacion": datetime.utcnow(),
            "actualizado_por": usuario_id
        }
        
        # Campos específicos según el estado
        if nuevo_estado == EstadoAprobacionEnum.GESTIONANDO:
            update_data["aprobacion_info.gestionado_por"] = usuario_id
            update_data["aprobacion_info.fecha_gestion"] = datetime.utcnow()
            if comentarios:
                update_data["aprobacion_info.comentarios_gestion"] = comentarios
        
        elif nuevo_estado in [EstadoAprobacionEnum.APROBADO, EstadoAprobacionEnum.RECHAZADO]:
            update_data["aprobacion_info.aprobado_por"] = usuario_id
            update_data["aprobacion_info.fecha_aprobacion"] = datetime.utcnow()
            if comentarios:
                update_data["aprobacion_info.comentarios_aprobacion"] = comentarios
        
        result = await self.collection.update_one(
            {"_id": ObjectId(caso_id), "is_active": True},
            {"$set": update_data}
        )
        
        return result.modified_count > 0
