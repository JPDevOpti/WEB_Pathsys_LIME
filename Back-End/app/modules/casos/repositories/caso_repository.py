"""Repositorio para operaciones CRUD de casos."""

from typing import Optional, List, Dict, Any, TYPE_CHECKING
from datetime import datetime, timedelta
from bson import ObjectId
import asyncio

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

from app.shared.repositories.base import BaseRepository
from app.modules.casos.models.caso import Caso
from app.modules.casos.schemas.caso import CasoCreate, CasoUpdate, CasoSearch, CasoStats, MuestraStats
from app.shared.schemas.common import EstadoCasoEnum


class CasoRepository(BaseRepository[Caso, CasoCreate, CasoUpdate]):
    """Repositorio para operaciones CRUD de casos con caché y paginación optimizada."""
    
    def __init__(self, database: Any):
        super().__init__(database, "casos", Caso)
        from app.modules.casos.services.cache_service import cache_service
        from app.modules.casos.services.pagination_service import PaginationService
        self.cache_service = cache_service
        self.pagination_service = PaginationService(self.collection)

    # ============================================================================
    # MÉTODOS AUXILIARES PRIVADOS
    # ============================================================================

    def _normalize_boolean_fields_for_write(self, data: Dict[str, Any]) -> Dict[str, Any]:
        return data

    def _clean_active_fields(self, document: Dict[str, Any]) -> Dict[str, Any]:
        """Limpiar campos de activación de documentos."""
        if document:
            document.pop("is_active", None)
            document.pop("isActive", None)
        return document

    def _get_estados_finalizados(self) -> List[str]:
        """Obtener lista de estados finalizados."""
        return [EstadoCasoEnum.COMPLETADO.value]
    
    def _get_stats_field_name(self, estado: str) -> str:
        """Mapear estado a nombre de campo de estadísticas."""
        estado_mapping = {
            EstadoCasoEnum.EN_PROCESO.value: "casos_en_proceso",
            EstadoCasoEnum.POR_FIRMAR.value: "casos_por_firmar",
            EstadoCasoEnum.POR_ENTREGAR.value: "casos_por_entregar",
            EstadoCasoEnum.COMPLETADO.value: "casos_completados"
        }
        return estado_mapping.get(estado, "casos_otros")

    def _build_search_query(self, search_params: CasoSearch) -> Dict[str, Any]:
        """Construir query de búsqueda basado en parámetros."""
        query = {}
        field_mappings = {
            'caso_code': ("caso_code", "regex"),
            'paciente_code': ("paciente.paciente_code", "exact"),
            'paciente_nombre': ("paciente.nombre", "regex"),
            'medico_nombre': ("medico_solicitante", "regex"),
            'patologo_codigo': ("patologo_asignado.codigo", "exact"),
            'estado': ("estado", "enum_value"),
            'prioridad': ("prioridad", "enum_value")
        }
        
        for param, (field, search_type) in field_mappings.items():
            value = getattr(search_params, param, None)
            if value:
                if search_type == "regex":
                    query[field] = {"$regex": value, "$options": "i"}
                elif search_type == "exact":
                    query[field] = value
                elif search_type == "enum_value":
                    query[field] = value.value
        
        if search_params.fecha_ingreso_desde or search_params.fecha_ingreso_hasta:
            fecha_query = {}
            if search_params.fecha_ingreso_desde:
                fecha_query["$gte"] = search_params.fecha_ingreso_desde
            if search_params.fecha_ingreso_hasta:
                fecha_query["$lte"] = search_params.fecha_ingreso_hasta
            query["fecha_creacion"] = fecha_query
        
        if search_params.solo_vencidos:
            fecha_limite = datetime.utcnow() - timedelta(days=15)
            query.update({
                "fecha_creacion": {"$lt": fecha_limite},
                "estado": {"$nin": self._get_estados_finalizados()}
            })
        
        if search_params.solo_sin_patologo:
            query["$or"] = [{"patologo_asignado": {"$exists": False}}, {"patologo_asignado": None}]
        
        if search_params.query:
            query["$or"] = [
                {"caso_code": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.nombre": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.paciente_code": {"$regex": search_params.query, "$options": "i"}},
                {"medico_solicitante": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        return query

    async def _get_casos_by_field(self, field: str, value: Any, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos por campo específico con paginación."""
        documents = await self.collection.find({field: value}).skip(skip).limit(limit).sort("fecha_creacion", -1).to_list(length=limit)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]

    # ============================================================================
    # MÉTODOS CRUD BÁSICOS
    # ============================================================================

    async def create(self, obj_in: CasoCreate) -> Caso:
        """Crear un nuevo caso en la base de datos."""
        obj_data = obj_in.model_dump(by_alias=False) if hasattr(obj_in, 'model_dump') else obj_in.dict(by_alias=False)
        obj_data.setdefault("fecha_creacion", datetime.utcnow())
        obj_data["fecha_actualizacion"] = datetime.utcnow()
        obj_data.pop("is_active", None)
        obj_data.pop("isActive", None)
        
        result = await self.collection.insert_one(obj_data)
        created_obj = await self.collection.find_one({"_id": result.inserted_id})
        if not created_obj:
            raise ValueError("Failed to create document")
        
        created_obj.pop("is_active", None)
        created_obj.pop("isActive", None)
        await self.cache_service.invalidate_stats_cache()
        return self.model_class(**created_obj)

    async def get(self, id: str) -> Optional[Caso]:
        """Obtener un caso por su ID."""
        if not ObjectId.is_valid(id):
            return None
        document = await self.collection.find_one({"_id": ObjectId(id)})
        return self.model_class(**self._clean_active_fields(document)) if document else None

    async def get_multi(self, skip: int = 0, limit: int = 100, filters: Optional[Dict[str, Any]] = None) -> List[Caso]:
        """Obtener múltiples casos con paginación y filtros."""
        query = filters.copy() if filters else {}
        documents = await self.collection.find(query).skip(skip).limit(limit).to_list(length=limit)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]
    
    async def update_by_caso_code(self, caso_code: str, update_data: Dict[str, Any]) -> Optional[Caso]:
        """Actualizar un caso por su código."""
        if not update_data:
            return await self.get_by_caso_code(caso_code)
        
        if any(key.startswith('$') for key in update_data.keys()):
            await self.collection.update_one({"caso_code": caso_code}, update_data)
        else:
            await self.collection.update_one({"caso_code": caso_code}, {"$set": update_data})
        
        return await self.get_by_caso_code(caso_code)

    async def delete_by_caso_code(self, caso_code: str) -> bool:
        """Eliminar un caso por su código."""
        result = await self.collection.delete_one({"caso_code": caso_code})
        return result.deleted_count > 0
    
    # ============================================================================
    # MÉTODOS DE BÚSQUEDA Y CONSULTA
    # ============================================================================

    async def get_by_codigo(self, caso_code: str) -> Optional[Caso]:
        """Obtener un caso por su código de caso."""
        document = await self.collection.find_one({"caso_code": caso_code})
        return self.model_class(**self._clean_active_fields(document)) if document else None
    
    async def get_by_caso_code(self, caso_code: str) -> Optional[Caso]:
        """Alias para get_by_codigo."""
        return await self.get_by_codigo(caso_code)

    async def get_by_paciente_code(self, paciente_code: str, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos por código de paciente."""
        return await self._get_casos_by_field("paciente.paciente_code", paciente_code, skip, limit)
    
    async def search_casos(self, search_params: CasoSearch, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Buscar casos con parámetros específicos."""
        query = self._build_search_query(search_params)
        documents = await self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1).to_list(length=limit)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]
    
    # ============================================================================
    # MÉTODOS DE GESTIÓN DE PATÓLOGOS
    # ============================================================================

    async def asignar_patologo_por_caso_code(self, caso_code: str, patologo_info: dict) -> Optional[Caso]:
        """Asignar un patólogo a un caso por código."""
        await self.collection.update_one({"caso_code": caso_code}, {"$set": {
            "patologo_asignado": patologo_info,
            "fecha_actualizacion": datetime.utcnow()
        }})
        return await self.get_by_caso_code(caso_code)
    
    async def desasignar_patologo_por_caso_code(self, caso_code: str) -> Optional[Caso]:
        """Desasignar patólogo de un caso por código."""
        await self.collection.update_one({"caso_code": caso_code}, {"$set": {
            "patologo_asignado": None,
            "fecha_actualizacion": datetime.utcnow()
        }})
        return await self.get_by_caso_code(caso_code)

    async def get_casos_by_patologo(self, patologo_codigo: str, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos asignados a un patólogo específico."""
        return await self._get_casos_by_field("patologo_asignado.codigo", patologo_codigo, skip, limit)
    
    async def get_casos_sin_patologo(self, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos sin patólogo asignado."""
        query = {"$or": [{"patologo_asignado": {"$exists": False}}, {"patologo_asignado": None}]}
        documents = await self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", 1).to_list(length=limit)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]

    # ============================================================================
    # MÉTODOS DE FILTROS POR ESTADO
    # ============================================================================

    async def get_casos_by_estado(self, estado: EstadoCasoEnum, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos por estado específico."""
        return await self._get_casos_by_field("estado", estado.value, skip, limit)
    
    async def get_casos_vencidos(self, dias_limite: int = 15) -> List[Caso]:
        """Obtener casos vencidos según días límite."""
        fecha_limite = datetime.utcnow() - timedelta(days=dias_limite)
        query = {
            "fecha_creacion": {"$lt": fecha_limite},
            "estado": {"$nin": self._get_estados_finalizados()}
        }
        documents = await self.collection.find(query).sort("fecha_creacion", 1).to_list(length=None)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]
    
    # ============================================================================
    # MÉTODOS DE CONSULTAS POR FECHAS
    # ============================================================================

    async def get_casos_por_año(self, año: int) -> List[Caso]:
        """Obtener casos por año específico."""
        inicio_año = datetime(año, 1, 1, 0, 0, 0, 0)
        fin_año = datetime(año, 12, 31, 23, 59, 59, 999999)
        documents = await self.collection.find({"fecha_creacion": {"$gte": inicio_año, "$lte": fin_año}}).sort("fecha_creacion", 1).to_list(length=None)
        return [self.model_class(**self._clean_active_fields(doc)) for doc in documents]
    
    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS GENERALES
    # ============================================================================
    
    async def get_estadisticas(self) -> CasoStats:
        """Obtener estadísticas generales de casos."""
        result_estados = await self.collection.aggregate([{"$group": {"_id": "$estado", "count": {"$sum": 1}}}]).to_list(length=None)
        stats = CasoStats()
        stats.total_casos = await self.count()
        
        for item in result_estados:
            setattr(stats, self._get_stats_field_name(item["_id"]), item["count"])
        
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1) if inicio_mes_actual.month > 1 else inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1) if inicio_mes_anterior.month > 1 else inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        casos_mes_anterior = await self.collection.count_documents({"fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}})
        casos_mes_anterior_anterior = await self.collection.count_documents({"fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}})
        
        stats.casos_mes_anterior = casos_mes_anterior
        stats.casos_mes_actual = casos_mes_anterior_anterior
        stats.cambio_porcentual = round(((casos_mes_anterior - casos_mes_anterior_anterior) / casos_mes_anterior_anterior) * 100, 2) if casos_mes_anterior_anterior > 0 else (100.0 if casos_mes_anterior > 0 else 0.0)
        
        inicio_semana = (datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
        stats.casos_semana_actual = await self.collection.count_documents({"fecha_creacion": {"$gte": inicio_semana}})
        
        result_patologos = await self.collection.aggregate([{"$match": {"patologo_asignado": {"$exists": True, "$ne": None}}}, {"$group": {"_id": "$patologo_asignado.nombre", "count": {"$sum": 1}}}]).to_list(length=None)
        stats.casos_por_patologo = {item["_id"]: item["count"] for item in result_patologos}
        
        result_pruebas = await self.collection.aggregate([{"$unwind": "$muestras"}, {"$unwind": "$muestras.pruebas"}, {"$group": {"_id": "$muestras.pruebas.nombre", "count": {"$sum": {"$ifNull": ["$muestras.pruebas.cantidad", 1]}}}}]).to_list(length=None)
        stats.casos_por_tipo_prueba = {item["_id"]: item["count"] for item in result_pruebas}
        
        result_tiempo = await self.collection.aggregate([{"$match": {"estado": EstadoCasoEnum.COMPLETADO.value, "fecha_entrega": {"$exists": True}}}, {"$project": {"tiempo_procesamiento": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}}, {"$group": {"_id": None, "tiempo_promedio": {"$avg": "$tiempo_procesamiento"}}}]).to_list(length=1)
        if result_tiempo and result_tiempo[0]["tiempo_promedio"]:
            stats.tiempo_promedio_procesamiento = round(result_tiempo[0]["tiempo_promedio"], 2)
        return stats
    
    async def get_estadisticas_muestras(self) -> MuestraStats:
        """Obtener estadísticas de muestras procesadas."""
        stats = MuestraStats()
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1) if inicio_mes_actual.month > 1 else inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1) if inicio_mes_anterior.month > 1 else inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        result_mes_anterior = await self.collection.aggregate([{"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}, "observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}}, {"$unwind": "$muestras"}, {"$group": {"_id": None, "total": {"$sum": 1}}}]).to_list(length=1)
        stats.muestras_mes_anterior = result_mes_anterior[0]["total"] if result_mes_anterior else 0
        
        result_mes_anterior_anterior = await self.collection.aggregate([{"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}, "observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}}, {"$unwind": "$muestras"}, {"$group": {"_id": None, "total": {"$sum": 1}}}]).to_list(length=1)
        stats.muestras_mes_anterior_anterior = result_mes_anterior_anterior[0]["total"] if result_mes_anterior_anterior else 0
        
        stats.cambio_porcentual = round(((stats.muestras_mes_anterior - stats.muestras_mes_anterior_anterior) / stats.muestras_mes_anterior_anterior) * 100, 2) if stats.muestras_mes_anterior_anterior > 0 else (100.0 if stats.muestras_mes_anterior > 0 else 0.0)
        
        result_total = await self.collection.aggregate([{"$match": {"observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}}, {"$unwind": "$muestras"}, {"$group": {"_id": None, "total": {"$sum": 1}}}]).to_list(length=1)
        stats.total_muestras = result_total[0]["total"] if result_total else 0
        
        inicio_12_meses = ahora - timedelta(days=365)
        result_region = await self.collection.aggregate([{"$match": {"fecha_creacion": {"$gte": inicio_12_meses}}}, {"$unwind": "$muestras"}, {"$group": {"_id": "$muestras.region_cuerpo", "count": {"$sum": 1}}}, {"$sort": {"count": -1}}, {"$limit": 10}]).to_list(length=None)
        stats.muestras_por_region = {item["_id"]: item["count"] for item in result_region}
        
        result_pruebas = await self.collection.aggregate([{"$match": {"fecha_creacion": {"$gte": inicio_12_meses}}}, {"$unwind": "$muestras"}, {"$unwind": "$muestras.pruebas"}, {"$group": {"_id": "$muestras.pruebas.nombre", "count": {"$sum": {"$ifNull": ["$muestras.pruebas.cantidad", 1]}}}}, {"$sort": {"count": -1}}, {"$limit": 10}]).to_list(length=None)
        stats.muestras_por_tipo_prueba = {item["_id"]: item["count"] for item in result_pruebas}
        
        result_tiempo = await self.collection.aggregate([{"$match": {"estado": EstadoCasoEnum.COMPLETADO.value, "fecha_firma": {"$exists": True, "$ne": None}}}, {"$project": {"tiempo_procesamiento": {"$divide": [{"$subtract": ["$fecha_firma", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}}, {"$group": {"_id": None, "tiempo_promedio": {"$avg": "$tiempo_procesamiento"}}}]).to_list(length=1)
        if result_tiempo and result_tiempo[0]["tiempo_promedio"]:
            stats.tiempo_promedio_procesamiento = round(result_tiempo[0]["tiempo_promedio"], 2)
        return stats

    # ============================================================================
    # MÉTODOS DE ANÁLISIS DE OPORTUNIDAD
    # ============================================================================

    async def get_oportunidad_por_mes_agregado(self, año: int) -> List[float]:
        """Obtener porcentajes de oportunidad por mes para un año."""
        inicio_año = datetime(año, 1, 1)
        fin_año = datetime(año, 12, 31, 23, 59, 59, 999999)
        result = await self.collection.aggregate([
            {"$match": {"fecha_entrega": {"$gte": inicio_año, "$lte": fin_año}}},
            {"$project": {
                "mes": {"$month": "$fecha_entrega"},
                "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}, 6]}
            }},
            {"$group": {"_id": "$mes", "total": {"$sum": 1}, "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}}},
            {"$project": {"mes": "$_id", "porcentaje": {"$cond": [{"$gt": ["$total", 0]}, {"$multiply": [{"$divide": ["$dentro", "$total"]}, 100]}, 0]}}}
        ]).to_list(length=None)
        meses = [0.0] * 12
        for item in result:
            mes_idx = int(item.get("mes", 0)) - 1
            if 0 <= mes_idx < 12:
                meses[mes_idx] = round(float(item.get("porcentaje", 0)), 2)
        return meses

    async def get_oportunidad_detalle_por_mes_agregado(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Obtener detalles de oportunidad por patólogos y pruebas en rango de fechas."""
        day_ms = 1000 * 60 * 60 * 24
        result = await self.collection.aggregate([
            {"$match": {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
            {"$facet": {
                "patologos": [
                    {"$project": {"patologo": {"$ifNull": ["$patologo_asignado.nombre", "Sin patólogo"]}, "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]}, "dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}}},
                    {"$group": {"_id": "$patologo", "total": {"$sum": 1}, "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}, "tiempoPromedio": {"$avg": "$dias"}}},
                    {"$project": {"_id": 0, "nombre": "$_id", "dentroOportunidad": "$dentro", "fueraOportunidad": {"$subtract": ["$total", "$dentro"]}, "tiempoPromedio": {"$round": ["$tiempoPromedio", 1]}}},
                    {"$sort": {"nombre": 1}}
                ],
                "pruebas": [
                    {"$unwind": {"path": "$muestras", "preserveNullAndEmptyArrays": False}},
                    {"$unwind": {"path": "$muestras.pruebas", "preserveNullAndEmptyArrays": False}},
                    {"$project": {"codigo": {"$ifNull": ["$muestras.pruebas.id", "$muestras.pruebas.pruebaCode"]}, "nombre": {"$ifNull": ["$muestras.pruebas.nombre", "$muestras.pruebas.pruebasName"]}, "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]}}},
                    {"$group": {"_id": {"codigo": "$codigo", "nombre": "$nombre"}, "total": {"$sum": 1}, "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}}},
                    {"$project": {"_id": 0, "codigo": "$_id.codigo", "nombre": "$_id.nombre", "dentroOportunidad": "$dentro", "fueraOportunidad": {"$subtract": ["$total", "$dentro"]}, "tiempoOportunidad": {"$literal": "7 días"}}},
                    {"$sort": {"nombre": 1}}
                ],
                "resumen": [
                    {"$project": {"dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]}}},
                    {"$group": {"_id": None, "total": {"$sum": 1}, "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}}},
                    {"$project": {"_id": 0, "total": 1, "dentro": 1, "fuera": {"$subtract": ["$total", "$dentro"]}}}
                ]
            }},
            {"$project": {"patologos": 1, "pruebas": 1, "resumen": 1}}
        ]).to_list(length=1)

        if result:
            item = result[0]
            return {"patologos": item.get("patologos", []), "pruebas": item.get("pruebas", []), "resumen": (item.get("resumen", []) or [{}])[0]}
        return {"patologos": [], "pruebas": [], "resumen": {"total": 0, "dentro": 0, "fuera": 0}}
    
    # ============================================================================
    # MÉTODOS DE ANÁLISIS POR PATÓLOGOS
    # ============================================================================

    async def get_entidades_por_patologo(self, patologo: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener entidades trabajadas por un patólogo específico."""
        pipeline = [{"$match": {"patologo_asignado.nombre": {"$regex": patologo, "$options": "i"}}}]
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        pipeline.extend([
            {"$group": {"_id": "$paciente.entidad_info.nombre", "codigo_entidad": {"$first": "$paciente.entidad_info.codigo"}, "casesCount": {"$sum": 1}, "tipos_atencion": {"$addToSet": "$paciente.tipo_atencion"}}},
            {"$project": {"_id": 0, "name": "$_id", "codigo": "$codigo_entidad", "casesCount": 1, "type": {"$arrayElemAt": ["$tipos_atencion", 0]}, "tipos_atencion": 1}},
            {"$sort": {"casesCount": -1}}
        ])
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        return [{"name": item["name"], "codigo": item.get("codigo", ""), "type": item.get("type", "No especificado"), "casesCount": item["casesCount"], "tipos_atencion": item.get("tipos_atencion", [])} for item in result if item.get("name")]

    async def get_pruebas_por_patologo(self, patologo: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener pruebas realizadas por un patólogo específico."""
        pipeline = [{"$match": {"patologo_asignado.nombre": {"$regex": patologo, "$options": "i"}}}]
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        pipeline.extend([
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {"$group": {"_id": {"nombre": "$muestras.pruebas.nombre", "codigo": "$muestras.pruebas.codigo"}, "count": {"$sum": 1}, "categorias": {"$addToSet": "$muestras.pruebas.categoria"}}},
            {"$project": {"_id": 0, "name": "$_id.nombre", "codigo": "$_id.codigo", "count": 1, "category": {"$arrayElemAt": ["$categorias", 0]}, "categorias": 1}},
            {"$sort": {"count": -1}}
        ])
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        return [{"name": item["name"], "codigo": item.get("codigo", ""), "category": item.get("category", "No especificada"), "count": item["count"], "categorias": item.get("categorias", [])} for item in result if item.get("name")]

    # ============================================================================
    # MÉTODOS DE ANÁLISIS POR ENTIDADES
    # ============================================================================

    async def get_estadisticas_entidades_mensual(self, fecha_inicio: datetime, fecha_fin: datetime, entity: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de entidades por rango de fechas."""
        match_filter = {
            "fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin},
            "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}
        }
        
        if entity and entity.strip():
            match_filter["$or"] = [{"paciente.entidad_info.codigo": entity.strip()}, {"paciente.entidad_info.id": entity.strip()}]
        
        if entity and entity.strip():
            pipeline = [
                {"$match": match_filter},
                {"$addFields": {"_entidad_codigo": {"$ifNull": ["$paciente.entidad_info.codigo", "$paciente.entidad_info.id"]}, "_entidad_nombre": "$paciente.entidad_info.nombre"}},
                {"$group": {"_id": None, "codigo_entidad": {"$first": "$_entidad_codigo"}, "nombre_entidad": {"$first": "$_entidad_nombre"}, "total_casos": {"$sum": 1}, "ambulatorios": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]}, 1, 0]}}, "hospitalizados": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]}, 1, 0]}}}},
                {"$project": {"_id": 0, "nombre": "$nombre_entidad", "codigo": "$codigo_entidad", "ambulatorios": 1, "hospitalizados": 1, "total": "$total_casos"}}
            ]
        else:
            pipeline = [
                {"$match": match_filter},
                {"$addFields": {"_entidad_codigo": {"$ifNull": ["$paciente.entidad_info.codigo", "$paciente.entidad_info.id"]}, "_entidad_nombre": "$paciente.entidad_info.nombre"}},
                {"$group": {"_id": "$_entidad_codigo", "nombre_entidad": {"$first": "$_entidad_nombre"}, "total_casos": {"$sum": 1}, "ambulatorios": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]}, 1, 0]}}, "hospitalizados": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]}, 1, 0]}}}},
                {"$project": {"_id": 0, "nombre": "$nombre_entidad", "codigo": "$_id", "ambulatorios": 1, "hospitalizados": 1, "total": "$total_casos"}},
                {"$sort": {"total": -1}}
            ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        total_ambulatorios = sum(item["ambulatorios"] for item in result)
        total_hospitalizados = sum(item["hospitalizados"] for item in result)
        
        pipeline_tiempo = [
            {"$match": {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin}, "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}}},
            {"$project": {"tiempo_dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}},
            {"$group": {"_id": None, "tiempo_promedio": {"$avg": "$tiempo_dias"}}}
        ]
        
        if entity and entity.strip():
            pipeline_tiempo[0]["$match"]["$or"] = [{"paciente.entidad_info.codigo": entity.strip()}, {"paciente.entidad_info.id": entity.strip()}]
        
        tiempo_result = await self.collection.aggregate(pipeline_tiempo).to_list(length=1)
        tiempo_promedio = tiempo_result[0]["tiempo_promedio"] if tiempo_result else 0
        
        if not (entity and entity.strip()):
            try:
                entidades_catalogo = await self.database["entidades"].find({"$or": [{"is_active": True}, {"isActive": True}]}, {"entidad_code": 1, "entidad_name": 1, "_id": 0}).to_list(length=None)
                codigos_presentes = {e["codigo"] for e in result}
                for ent in entidades_catalogo:
                    code, name = ent.get("entidad_code"), ent.get("entidad_name")
                    if code and code not in codigos_presentes:
                        result.append({"nombre": name or code, "codigo": code, "ambulatorios": 0, "hospitalizados": 0, "total": 0})
                result = sorted(result, key=lambda x: (-x["total"], x["nombre"]))
            except Exception:
                pass

        return {
            "entities": result,
            "summary": {"total": total_ambulatorios + total_hospitalizados, "ambulatorios": total_ambulatorios, "hospitalizados": total_hospitalizados, "tiempoPromedio": round(tiempo_promedio, 1)}
        }

    async def get_debug_entidades(self, fecha_inicio: datetime, fecha_fin: datetime, entity: Optional[str] = None) -> Dict[str, Any]:
        """Método de depuración para verificar datos de entidades."""
        basic_filter = {"fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}}
        fecha_entrega_filter = {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin, "$exists": True, "$ne": None}}
        completados_filter = {"fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}, "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}}
        
        total_casos_creacion = await self.collection.count_documents(basic_filter)
        total_casos_entrega = await self.collection.count_documents(fecha_entrega_filter)
        total_casos_completados = await self.collection.count_documents(completados_filter)
        
        match_filter = {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin}, "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}}
        if entity and entity.strip():
            match_filter["paciente.entidad_info.codigo"] = entity.strip()
        
        casos_raw = await self.collection.aggregate([
            {"$match": match_filter},
            {"$project": {"_id": 0, "caso_code": "$caso_code", "fecha_creacion": "$fecha_creacion", "entidad_nombre": "$paciente.entidad_info.nombre", "entidad_codigo": "$paciente.entidad_info.codigo", "tipo_atencion": "$paciente.tipo_atencion", "fecha_entrega": "$fecha_entrega"}},
            {"$limit": 20}
        ]).to_list(length=None)
        
        total_casos = await self.collection.count_documents(match_filter)
        counts = await self.collection.aggregate([{"$match": match_filter}, {"$group": {"_id": "$paciente.tipo_atencion", "count": {"$sum": 1}}}]).to_list(length=None)
        tipo_atencion_counts = {item["_id"]: item["count"] for item in counts}
        
        return {
            "total_casos_por_fecha_creacion": total_casos_creacion,
            "total_casos_con_fecha_entrega": total_casos_entrega, 
            "total_casos_completados": total_casos_completados,
            "total_casos_filtro_actual": total_casos,
            "tipo_atencion_counts": tipo_atencion_counts,
            "casos_ejemplo": casos_raw,
            "filtro_aplicado": match_filter,
            "filtros_probados": {"fecha_creacion": basic_filter, "fecha_entrega": fecha_entrega_filter, "completados": completados_filter}
        }

    async def get_detalle_entidad(self, entidad: str, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Obtener detalles completos de una entidad específica."""
        match_filter = {"$or": [{"paciente.entidad_info.codigo": entidad}, {"paciente.entidad_info.id": entidad}], "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}}
        
        basicas_result = await self.collection.aggregate([{
            "$match": match_filter
        }, {
                "$group": {
                    "_id": None,
                    "total_pacientes": {"$sum": 1},
                "ambulatorios": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]}, 1, 0]}},
                "hospitalizados": {"$sum": {"$cond": [{"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]}, 1, 0]}},
                    "total_muestras": {"$sum": {"$size": "$muestras"}}
                }
        }]).to_list(length=1)
        
        tiempos_result = await self.collection.aggregate([{
            "$match": {**match_filter, "fecha_entrega": {"$exists": True, "$ne": None}}
        }, {
            "$project": {"tiempo_dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}
        }, {
            "$group": {"_id": None, "promedio_dias": {"$avg": "$tiempo_dias"}, "minimo_dias": {"$min": "$tiempo_dias"}, "maximo_dias": {"$max": "$tiempo_dias"}, "muestras_completadas": {"$sum": 1}}
        }]).to_list(length=1)
        
        pruebas_result = await self.collection.aggregate([
            {"$match": match_filter},
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {"$group": {"_id": {"codigo": "$muestras.pruebas.codigo", "nombre": "$muestras.pruebas.nombre"}, "total_solicitudes": {"$sum": {"$ifNull": ["$muestras.pruebas.cantidad", 1]}}}},
            {"$project": {"_id": 0, "codigo": "$_id.codigo", "nombre": "$_id.nombre", "total_solicitudes": 1}},
            {"$sort": {"total_solicitudes": -1}},
            {"$limit": 10}
        ]).to_list(length=None)
        
        basicas = basicas_result[0] if basicas_result else {"total_pacientes": 0, "ambulatorios": 0, "hospitalizados": 0, "total_muestras": 0}
        tiempos = tiempos_result[0] if tiempos_result else {"promedio_dias": 0, "minimo_dias": 0, "maximo_dias": 0, "muestras_completadas": 0}
        promedio_muestras = basicas["total_muestras"] / basicas["total_pacientes"] if basicas["total_pacientes"] > 0 else 0
        
        return {
            "estadisticas_basicas": {"total_pacientes": basicas["total_pacientes"], "ambulatorios": basicas["ambulatorios"], "hospitalizados": basicas["hospitalizados"], "promedio_muestras_por_paciente": round(promedio_muestras, 1)},
            "tiempos_procesamiento": {"promedio_dias": round(tiempos["promedio_dias"], 1), "minimo_dias": round(tiempos["minimo_dias"], 1), "maximo_dias": round(tiempos["maximo_dias"], 1), "muestras_completadas": tiempos["muestras_completadas"]},
            "pruebas_mas_solicitadas": pruebas_result
        }

    async def get_patologos_por_entidad(self, entidad: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una entidad específica."""
        pipeline = [{"$match": {"$or": [{"paciente.entidad_info.codigo": entidad}, {"paciente.entidad_info.id": entidad}], "patologo_asignado": {"$exists": True, "$ne": None}}}]
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        pipeline.extend([
            {"$group": {"_id": {"codigo": "$patologo_asignado.codigo", "nombre": "$patologo_asignado.nombre"}, "casesCount": {"$sum": 1}}},
            {"$project": {"_id": 0, "name": "$_id.nombre", "codigo": "$_id.codigo", "casesCount": 1}},
            {"$sort": {"casesCount": -1}}
        ])
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        return [{"name": item["name"], "codigo": item.get("codigo", ""), "casesCount": item["casesCount"]} for item in result if item.get("name")]

    # ============================================================================
    # MÉTODOS DE ANÁLISIS POR PRUEBAS
    # ============================================================================

    async def get_estadisticas_pruebas_mensual(self, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        """Obtener estadísticas de pruebas por mes y año."""
        inicio_mes = datetime(year, month, 1)
        fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        pipeline = [{"$match": {"fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes}}}]
        if entity:
            pipeline[0]["$match"]["$or"] = [{"paciente.entidad_info.codigo": entity}, {"paciente.entidad_info.id": entity}]
        
        pipeline.extend([
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {"$group": {"_id": {"codigo": "$muestras.pruebas.id", "nombre": "$muestras.pruebas.nombre"}, "total_solicitadas": {"$sum": {"$ifNull": ["$muestras.pruebas.cantidad", 1]}}, "casos_ids": {"$addToSet": "$_id"}}},
            {"$project": {"_id": 0, "codigo": "$_id.codigo", "nombre": "$_id.nombre", "total_solicitadas": 1, "casos_ids": 1}},
            {"$sort": {"total_solicitadas": -1}}
        ])
        
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        pruebas_stats = []
        for prueba in result:
            casos_completados = await self._contar_casos_completados_por_prueba(prueba["casos_ids"], prueba["codigo"])
            tiempo_promedio = await self._calcular_tiempo_promedio_prueba(prueba["casos_ids"], prueba["codigo"])
            porcentaje_completado = (casos_completados / prueba["total_solicitadas"]) * 100 if prueba["total_solicitadas"] > 0 else 0
            pruebas_stats.append({
                "codigo": prueba["codigo"], "nombre": prueba["nombre"], "total_solicitadas": prueba["total_solicitadas"],
                "total_completadas": casos_completados, "tiempo_promedio": tiempo_promedio, "porcentaje_completado": round(porcentaje_completado, 1)
            })
        return pruebas_stats

    async def get_detalle_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        """Obtener detalles completos de una prueba específica."""
        inicio_mes = datetime(year, month, 1)
        fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        match_filter = {"fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes}, "muestras.pruebas.id": codigo_prueba}
        if entity:
            match_filter["$and"] = [{"$or": [{"paciente.entidad_info.codigo": entity}, {"paciente.entidad_info.id": entity}]}]
        
        casos = await self.collection.aggregate([
            {"$match": match_filter},
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {"$unwind": "$muestras.pruebas"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}}
        ]).to_list(length=None)
        
        if not casos:
            return {"estadisticas_principales": {"total_solicitadas": 0, "total_completadas": 0, "porcentaje_completado": 0}, "tiempos_procesamiento": {"promedio_dias": 0, "dentro_oportunidad": 0, "fuera_oportunidad": 0, "total_casos": 0}, "patologos": []}
        
        casos_validos = [c for c in casos if c is not None]
        if not casos_validos:
            return {"estadisticas_principales": {"total_solicitadas": 0, "total_completadas": 0, "porcentaje_completado": 0}, "tiempos_procesamiento": {"promedio_dias": 0, "dentro_oportunidad": 0, "fuera_oportunidad": 0, "total_casos": 0}, "patologos": []}
        
        total_solicitadas = len(casos_validos)
        casos_completados = [c for c in casos_validos if c and c.get("estado") == EstadoCasoEnum.COMPLETADO.value]
        total_completadas = len(casos_completados)
        porcentaje_completado = (total_completadas / total_solicitadas) * 100 if total_solicitadas > 0 else 0
        
        return {
            "estadisticas_principales": {"total_solicitadas": total_solicitadas, "total_completadas": total_completadas, "porcentaje_completado": round(porcentaje_completado, 1)},
            "tiempos_procesamiento": await self._calcular_tiempos_prueba(casos_validos),
            "patologos": await self._obtener_patologos_por_prueba(casos_validos)
        }

    async def get_patologos_por_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una prueba específica."""
        inicio_mes = datetime(year, month, 1)
        fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        match_filter = {"fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes}, "muestras.pruebas.id": codigo_prueba, "patologo_asignado": {"$exists": True, "$ne": None}}
        if entity:
            match_filter["$and"] = [{"$or": [{"paciente.entidad_info.codigo": entity}, {"paciente.entidad_info.id": entity}]}]
        
        result = await self.collection.aggregate([
            {"$match": match_filter},
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {"$group": {"_id": {"codigo": "$patologo_asignado.codigo", "nombre": "$patologo_asignado.nombre"}, "total_procesadas": {"$sum": 1}, "casos_ids": {"$addToSet": "$_id"}}},
            {"$project": {"_id": 0, "codigo": "$_id.codigo", "nombre": "$_id.nombre", "total_procesadas": 1, "casos_ids": 1}},
            {"$sort": {"total_procesadas": -1}}
        ]).to_list(length=None)
        
        patologos_stats = []
        for patologo in result:
            tiempo_promedio = await self._calcular_tiempo_promedio_patologo_prueba(patologo["casos_ids"], codigo_prueba)
            patologos_stats.append({"codigo": patologo["codigo"], "nombre": patologo["nombre"], "total_procesadas": patologo["total_procesadas"], "tiempo_promedio": tiempo_promedio})
        return patologos_stats

    # ============================================================================
    # MÉTODOS AUXILIARES PARA ANÁLISIS DE PRUEBAS
    # ============================================================================

    async def _contar_casos_completados_por_prueba(self, casos_ids: List[str], codigo_prueba: str) -> int:
        """Contar casos completados para una prueba específica."""
        if not casos_ids:
            return 0
        result = await self.collection.aggregate([
            {"$match": {"_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]}, "estado": EstadoCasoEnum.COMPLETADO.value, "muestras.pruebas.id": codigo_prueba}},
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {"$count": "total"}
        ]).to_list(length=1)
        return result[0]["total"] if result else 0

    async def _calcular_tiempo_promedio_prueba(self, casos_ids: List[str], codigo_prueba: str) -> float:
        """Calcular tiempo promedio de procesamiento para una prueba específica."""
        if not casos_ids:
            return 0.0
        result = await self.collection.aggregate([
            {"$match": {"_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]}, "estado": EstadoCasoEnum.COMPLETADO.value, "fecha_entrega": {"$exists": True, "$ne": None}, "muestras.pruebas.id": codigo_prueba}},
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {"$project": {"tiempo_dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}},
            {"$group": {"_id": None, "tiempo_promedio": {"$avg": "$tiempo_dias"}}}
        ]).to_list(length=1)
        return round(result[0]["tiempo_promedio"], 1) if result and result[0]["tiempo_promedio"] is not None else 0.0

    async def _calcular_tiempos_prueba(self, casos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular estadísticas de tiempo para una prueba."""
        casos_completados = [c for c in casos if c.get("estado") == EstadoCasoEnum.COMPLETADO.value]
        if not casos_completados:
            return {"promedio_dias": 0, "dentro_oportunidad": 0, "fuera_oportunidad": 0, "total_casos": 0}
        
        tiempos_dias = []
        dentro_oportunidad = 0
        fuera_oportunidad = 0
        
        for caso in casos_completados:
            fecha_entrega, fecha_creacion = caso.get("fecha_entrega"), caso.get("fecha_creacion")
            if fecha_entrega and fecha_creacion and hasattr(fecha_entrega, 'days') and hasattr(fecha_creacion, 'days'):
                tiempo = (fecha_entrega - fecha_creacion).days
                tiempos_dias.append(tiempo)
                if tiempo <= 6:
                    dentro_oportunidad += 1
                else:
                    fuera_oportunidad += 1
        
        promedio_dias = sum(tiempos_dias) / len(tiempos_dias) if tiempos_dias else 0
        return {"promedio_dias": round(promedio_dias, 1), "dentro_oportunidad": dentro_oportunidad, "fuera_oportunidad": fuera_oportunidad, "total_casos": len(casos_completados)}

    async def _obtener_patologos_por_prueba(self, casos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una prueba específica."""
        patologos_map = {}
        for caso in casos:
            if caso and caso.get("patologo_asignado"):
                patologo = caso["patologo_asignado"]
                if patologo:
                    codigo, nombre = patologo.get("codigo", ""), patologo.get("nombre", "")
                    if codigo and codigo not in patologos_map:
                        patologos_map[codigo] = {"codigo": codigo, "nombre": nombre, "total_procesadas": 0, "tiempo_promedio": 0.0}
                    if codigo:
                        patologos_map[codigo]["total_procesadas"] += 1
        
        for codigo, patologo in patologos_map.items():
            try:
                casos_patologo = [c for c in casos if c and c.get("patologo_asignado", {}).get("codigo") == codigo]
                casos_ids = [c["_id"] for c in casos_patologo if c and c.get("_id")]
                patologo["tiempo_promedio"] = await self._calcular_tiempo_promedio_patologo_prueba(casos_ids, "") if casos_ids else 0.0
            except Exception:
                patologo["tiempo_promedio"] = 0.0
        
        return sorted(patologos_map.values(), key=lambda x: x["total_procesadas"], reverse=True)

    async def _calcular_tiempo_promedio_patologo_prueba(self, casos_ids: List[str], codigo_prueba: str) -> float:
        """Calcular tiempo promedio de procesamiento para un patólogo en una prueba específica."""
        if not casos_ids:
            return 0.0
        pipeline = [{"$match": {"_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]}, "estado": EstadoCasoEnum.COMPLETADO.value, "fecha_entrega": {"$exists": True, "$ne": None}}}]
        if codigo_prueba:
            pipeline[0]["$match"]["muestras.pruebas.id"] = codigo_prueba
        pipeline.extend([
            {"$project": {"tiempo_dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}},
            {"$group": {"_id": None, "tiempo_promedio": {"$avg": "$tiempo_dias"}}}
        ])
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return round(result[0]["tiempo_promedio"], 1) if result and len(result) > 0 and result[0] and result[0].get("tiempo_promedio") is not None else 0.0

    # ============================================================================
    # MÉTODOS CON CACHÉ PARA OPTIMIZACIÓN
    # ============================================================================

    async def get_caso_cached(self, caso_code: str) -> Optional[Caso]:
        """Obtener caso con caché para mejor rendimiento."""
        cache_key = f"caso_detail:{caso_code}"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return self.model_class(**cached_result)
        caso = await self.get_by_caso_code(caso_code)
        if caso:
            await self.cache_service.set(cache_key, caso.model_dump(), 180)
        return caso

    async def get_multi_optimized(self, cursor: Optional[str] = None, limit: int = 100, filters: Optional[Dict[str, Any]] = None, sort_field: str = "fecha_creacion", sort_direction: int = -1) -> Dict[str, Any]:
        """Obtener múltiples casos con paginación cursor-based optimizada."""
        return await self.pagination_service.paginate_casos(cursor=cursor, limit=limit, sort_field=sort_field, sort_direction=sort_direction, filters=filters)

    async def get_estadisticas_cached(self) -> CasoStats:
        """Obtener estadísticas con caché para mejor rendimiento."""
        cache_key = "caso_stats:general"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return CasoStats(**cached_result)
        stats = await self.get_estadisticas()
        await self.cache_service.set(cache_key, stats.model_dump(), 300)
        return stats

    async def get_estadisticas_muestras_cached(self) -> MuestraStats:
        """Obtener estadísticas de muestras con caché."""
        cache_key = "muestra_stats:general"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return MuestraStats(**cached_result)
        stats = await self.get_estadisticas_muestras()
        await self.cache_service.set(cache_key, stats.model_dump(), 300)
        return stats

    async def get_casos_por_mes_cached(self, año: int) -> Dict[str, Any]:
        """Obtener casos por mes con caché para un año específico."""
        cache_key = f"casos_por_mes:{año}"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        casos = await self.get_casos_por_año(año)
        datos_mensuales = [0] * 12
        for caso in casos:
            if hasattr(caso, 'fecha_creacion') and caso.fecha_creacion:
                datos_mensuales[caso.fecha_creacion.month - 1] += 1
        result = {"datos": datos_mensuales, "total": sum(datos_mensuales), "año": año}
        await self.cache_service.set(cache_key, result, 600)
        return result

    async def get_oportunidad_por_mes_cached(self, año: int) -> Dict[str, Any]:
        """Obtener porcentajes de oportunidad por mes con caché."""
        cache_key = f"oportunidad_por_mes:{año}"
        cached_result = await self.cache_service.get(cache_key)
        if cached_result is not None:
            return cached_result
        datos = await self.get_oportunidad_por_mes_agregado(año)
        result = {"año": año, "porcentaje_por_mes": datos}
        await self.cache_service.set(cache_key, result, 600)
        return result

    # ============================================================================
    # MÉTODOS OPTIMIZADOS CON PAGINACIÓN CURSOR-BASED
    # ============================================================================

    async def search_casos_optimized(self, search_params: CasoSearch, cursor: Optional[str] = None, limit: int = 1000) -> Dict[str, Any]:
        """Buscar casos con paginación cursor-based optimizada."""
        return await self.pagination_service.paginate_search_results(search_params=search_params, cursor=cursor, limit=limit)

    async def get_casos_by_estado_optimized(self, estado: EstadoCasoEnum, cursor: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Obtener casos por estado con paginación optimizada."""
        return await self.pagination_service.paginate_casos_by_estado(estado=estado.value, cursor=cursor, limit=limit)

    async def get_casos_by_patologo_optimized(self, patologo_codigo: str, cursor: Optional[str] = None, limit: int = 100) -> Dict[str, Any]:
        """Obtener casos por patólogo con paginación optimizada."""
        return await self.pagination_service.paginate_casos_by_patologo(patologo_codigo=patologo_codigo, cursor=cursor, limit=limit)

    # ============================================================================
    # MÉTODOS DE ACTUALIZACIÓN OPTIMIZADOS
    # ============================================================================

    async def update_by_caso_code_optimized(self, caso_code: str, update_data: Dict[str, Any]) -> Optional[Caso]:
        """Actualizar caso con invalidación de caché."""
        caso_actualizado = await self.update_by_caso_code(caso_code, update_data)
        if caso_actualizado:
            await self.cache_service.invalidate_caso_cache(caso_code)
            if any(field in update_data for field in ['estado', 'fecha_creacion', 'fecha_entrega']):
                await self.cache_service.invalidate_stats_cache()
        return caso_actualizado

    async def delete_by_caso_code_optimized(self, caso_code: str) -> bool:
        """Eliminar caso con invalidación de caché."""
        result = await self.delete_by_caso_code(caso_code)
        if result:
            await self.cache_service.invalidate_caso_cache(caso_code)
            await self.cache_service.invalidate_stats_cache()
        return result

    async def get_casos_with_projection(self, projection: Dict[str, int], filters: Optional[Dict[str, Any]] = None, limit: int = 100) -> List[Dict[str, Any]]:
        """Obtener casos con proyección específica de campos."""
        query = filters.copy() if filters else {}
        return await self.collection.find(query, projection).limit(limit).to_list(length=limit)

    # ============================================================================
    # MÉTODOS DE ESTADÍSTICAS OPTIMIZADAS
    # ============================================================================

    async def get_estadisticas_optimized(self) -> CasoStats:
        """Obtener estadísticas usando agregación optimizada con $facet."""
        result = await self.collection.aggregate([{
            "$facet": {
                "estados": [{"$group": {"_id": "$estado", "count": {"$sum": 1}}}],
                "total": [{"$count": "total"}],
                "tiempo_promedio": [
                    {"$match": {"estado": "Completado", "fecha_entrega": {"$exists": True, "$ne": None}}},
                    {"$project": {"tiempo_dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}}},
                    {"$group": {"_id": None, "promedio": {"$avg": "$tiempo_dias"}}}
                ]
            }
        }]).to_list(length=1)
        
        if result:
            data = result[0]
            stats = CasoStats()
            stats.total_casos = data["total"][0]["total"] if data["total"] else 0
            
            for estado_data in data["estados"]:
                estado, count = estado_data["_id"], estado_data["count"]
                if estado == "En proceso":
                    stats.casos_en_proceso = count
                elif estado == "Por firmar":
                    stats.casos_por_firmar = count
                elif estado == "Por entregar":
                    stats.casos_por_entregar = count
                elif estado == "Completado":
                    stats.casos_completados = count
            
            if data["tiempo_promedio"]:
                stats.tiempo_promedio_procesamiento = round(data["tiempo_promedio"][0]["promedio"], 2)
            
            return stats
        return CasoStats()

    # ============================================================================
    # MÉTODOS DE OPERACIONES BULK
    # ============================================================================

    async def bulk_update_casos(self, updates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Actualizar múltiples casos en una sola operación bulk."""
        try:
            operations = [{"updateOne": {"filter": {"caso_code": update["caso_code"]}, "update": {"$set": update["data"]}}} for update in updates]
            result = await self.collection.bulk_write(operations)
            await self.cache_service.invalidate_stats_cache()
            return {"matched_count": result.matched_count, "modified_count": result.modified_count, "upserted_count": result.upserted_count}
        except Exception as e:
            return {"error": str(e)}