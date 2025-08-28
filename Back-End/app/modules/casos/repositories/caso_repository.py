"""Repositorio para operaciones CRUD de casos."""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta
from motor.motor_asyncio import AsyncIOMotorDatabase
from bson import ObjectId

from app.shared.repositories.base import BaseRepository
from app.modules.casos.models.caso import Caso
from app.modules.casos.schemas.caso import CasoCreate, CasoUpdate, CasoSearch, CasoStats, MuestraStats
from app.shared.schemas.common import EstadoCasoEnum


class CasoRepository(BaseRepository[Caso, CasoCreate, CasoUpdate]):
    """Repositorio para operaciones CRUD de casos."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        super().__init__(database, "casos", Caso)
    
    async def get_by_codigo(self, caso_code: str) -> Optional[Caso]:
        """Obtener caso por código."""
        document = await self.collection.find_one({"caso_code": caso_code})
        return self.model_class(**document) if document else None
    
    async def get_by_caso_code(self, caso_code: str) -> Optional[Caso]:
        """Alias para get_by_codigo - Obtener caso por código."""
        return await self.get_by_codigo(caso_code)
    
    async def asignar_patologo_por_caso_code(self, caso_code: str, patologo_info: dict) -> Optional[Caso]:
        """Asignar patólogo a un caso por código de caso."""
        update_data = {
            "patologo_asignado": patologo_info,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        await self.collection.update_one({"caso_code": caso_code}, {"$set": update_data})
        return await self.get_by_caso_code(caso_code)
    
    async def desasignar_patologo_por_caso_code(self, caso_code: str) -> Optional[Caso]:
        """Desasignar patólogo de un caso por código de caso."""
        update_data = {
            "patologo_asignado": None,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        await self.collection.update_one({"caso_code": caso_code}, {"$set": update_data})
        return await self.get_by_caso_code(caso_code)
    
    async def update_by_caso_code(self, caso_code: str, update_data: Dict[str, Any]) -> Optional[Caso]:
        """Actualizar un caso por su código de caso."""
        if not update_data:
            return await self.get_by_caso_code(caso_code)
        # Asegurar fecha de actualización
        update_data = {**update_data, "fecha_actualizacion": datetime.utcnow()}
        await self.collection.update_one({"caso_code": caso_code}, {"$set": update_data})
        return await self.get_by_caso_code(caso_code)

    async def delete_by_caso_code(self, caso_code: str) -> bool:
        """Eliminar un caso por su código de caso."""
        result = await self.collection.delete_one({"caso_code": caso_code})
        return result.deleted_count > 0
    
    
    async def search_casos(self, search_params: CasoSearch, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Búsqueda avanzada de casos."""
        query = self._build_search_query(search_params)
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1)
        documents = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_casos_by_patologo(self, patologo_codigo: str, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos asignados a un patólogo específico."""
        return await self._get_casos_by_field("patologo_asignado.codigo", patologo_codigo, skip, limit)
    
    async def get_casos_by_estado(self, estado: EstadoCasoEnum, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos por estado."""
        return await self._get_casos_by_field("estado", estado.value, skip, limit)
    
    
    async def get_casos_vencidos(self, dias_limite: int = 15) -> List[Caso]:
        """Obtener casos vencidos (más de X días sin completar)."""
        fecha_limite = datetime.utcnow() - timedelta(days=dias_limite)
        query = {
            "fecha_creacion": {"$lt": fecha_limite},
            "estado": {"$nin": self._get_estados_finalizados()}
        }
        documents = await self.collection.find(query).sort("fecha_creacion", 1).to_list(length=None)
        return [self.model_class(**doc) for doc in documents]
    
    async def get_casos_sin_patologo(self, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos sin patólogo asignado."""
        query = {"$or": [{"patologo_asignado": {"$exists": False}}, {"patologo_asignado": None}]}
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", 1)
        documents = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in documents]
    
    
    async def asignar_patologo(self, caso_id: str, patologo_info: dict) -> Optional[Caso]:
        """Asignar patólogo a un caso."""
        if not ObjectId.is_valid(caso_id):
            return None
        
        update_data = {
            "patologo_asignado": patologo_info,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        return await self.get(caso_id)
    
    async def actualizar_estado(self, caso_id: str, nuevo_estado: EstadoCasoEnum) -> Optional[Caso]:
        """Actualizar estado de un caso."""
        if not ObjectId.is_valid(caso_id):
            return None
        
        update_data = {
            "estado": nuevo_estado.value,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        if nuevo_estado == EstadoCasoEnum.COMPLETADO:
            update_data["fecha_entrega"] = datetime.utcnow()
        
        await self.collection.update_one({"_id": ObjectId(caso_id)}, {"$set": update_data})
        return await self.get(caso_id)
    
    
    async def get_estadisticas(self) -> CasoStats:
        """Obtener estadísticas de casos."""
        # Obtener estadísticas por estado
        pipeline_estados = [{"$group": {"_id": "$estado", "count": {"$sum": 1}}}]
        result_estados = await self.collection.aggregate(pipeline_estados).to_list(length=None)
        
        # Inicializar estadísticas
        stats = CasoStats()
        stats.total_casos = await self.count()
        
        # Procesar estadísticas por estado
        for item in result_estados:
            estado, count = item["_id"], item["count"]
            field_name = self._get_stats_field_name(estado)
            setattr(stats, field_name, count)
        
        # Estadísticas de tiempo - casos del mes anterior
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        
        # Mes anterior al anterior
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        # Casos del mes anterior
        casos_mes_anterior = await self.collection.count_documents({
            "fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}
        })
        stats.casos_mes_anterior = casos_mes_anterior
        
        # Casos del mes anterior al anterior
        casos_mes_anterior_anterior = await self.collection.count_documents({
            "fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}
        })
        stats.casos_mes_actual = casos_mes_anterior_anterior
        
        # Calcular cambio porcentual (mes anterior vs mes anterior al anterior)
        if casos_mes_anterior_anterior > 0:
            stats.cambio_porcentual = round(((casos_mes_anterior - casos_mes_anterior_anterior) / casos_mes_anterior_anterior) * 100, 2)
        else:
            stats.cambio_porcentual = 100.0 if casos_mes_anterior > 0 else 0.0
        
        # Casos de la semana actual
        inicio_semana = datetime.utcnow() - timedelta(days=datetime.utcnow().weekday())
        inicio_semana = inicio_semana.replace(hour=0, minute=0, second=0, microsecond=0)
        
        casos_semana_actual = await self.collection.count_documents({
            "fecha_creacion": {"$gte": inicio_semana}
        })
        stats.casos_semana_actual = casos_semana_actual
        
        # Estadísticas por patólogo
        pipeline_patologos = [
            {"$match": {"patologo_asignado": {"$exists": True, "$ne": None}}},
            {"$group": {"_id": "$patologo_asignado.nombre", "count": {"$sum": 1}}}
        ]
        result_patologos = await self.collection.aggregate(pipeline_patologos).to_list(length=None)
        stats.casos_por_patologo = {item["_id"]: item["count"] for item in result_patologos}
        
        # Estadísticas por tipo de prueba
        pipeline_pruebas = [
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {"$group": {"_id": "$muestras.pruebas.nombre", "count": {"$sum": 1}}}
        ]
        result_pruebas = await self.collection.aggregate(pipeline_pruebas).to_list(length=None)
        stats.casos_por_tipo_prueba = {item["_id"]: item["count"] for item in result_pruebas}
        
        # Calcular tiempo promedio de procesamiento (casos completados)
        pipeline_tiempo = [
            {"$match": {"estado": EstadoCasoEnum.COMPLETADO.value, "fecha_entrega": {"$exists": True}}},
            {"$project": {
                "tiempo_procesamiento": {
                    "$divide": [
                        {"$subtract": ["$fecha_entrega", "$fecha_creacion"]},
                        1000 * 60 * 60 * 24  # Convertir a días
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "tiempo_promedio": {"$avg": "$tiempo_procesamiento"}
            }}
        ]
        result_tiempo = await self.collection.aggregate(pipeline_tiempo).to_list(length=1)
        if result_tiempo and result_tiempo[0]["tiempo_promedio"]:
            stats.tiempo_promedio_procesamiento = round(result_tiempo[0]["tiempo_promedio"], 2)
        
        return stats
    
    
    def _build_search_query(self, search_params: CasoSearch) -> Dict[str, Any]:
        """Construir query de búsqueda."""
        query = {}
        
        # Mapeo de campos de búsqueda
        field_mappings = {
            'caso_code': ("caso_code", "regex"),
            'paciente_cedula': ("paciente.cedula", "exact"),
            'paciente_nombre': ("paciente.nombre", "regex"),
            'medico_nombre': ("medico_solicitante.nombre", "regex"),
            'patologo_codigo': ("patologo_asignado.codigo", "exact"),
            'estado': ("estado", "enum_value")
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
        
        # Filtros de fecha
        if search_params.fecha_ingreso_desde or search_params.fecha_ingreso_hasta:
            fecha_query = {}
            if search_params.fecha_ingreso_desde:
                fecha_query["$gte"] = search_params.fecha_ingreso_desde
            if search_params.fecha_ingreso_hasta:
                fecha_query["$lte"] = search_params.fecha_ingreso_hasta
            # Mantener compatibilidad: mapear filtros de ingreso a fecha_creacion
            query["fecha_creacion"] = fecha_query
        
        # Filtros especiales
        if search_params.solo_vencidos:
            fecha_limite = datetime.utcnow() - timedelta(days=15)
            query.update({
                "fecha_creacion": {"$lt": fecha_limite},
                "estado": {"$nin": self._get_estados_finalizados()}
            })
        
        if search_params.solo_sin_patologo:
            query["$or"] = [{"patologo_asignado": {"$exists": False}}, {"patologo_asignado": None}]
        
        # Búsqueda general
        if search_params.query:
            query["$or"] = [
                {"caso_code": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.nombre": {"$regex": search_params.query, "$options": "i"}},
                {"paciente.cedula": {"$regex": search_params.query, "$options": "i"}},
                {"medico_solicitante.nombre": {"$regex": search_params.query, "$options": "i"}}
            ]
        
        return query
    
    async def _get_casos_by_field(self, field: str, value: Any, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Método auxiliar para obtener casos por campo específico."""
        query = {field: value}
        cursor = self.collection.find(query).skip(skip).limit(limit).sort("fecha_creacion", -1)
        documents = await cursor.to_list(length=limit)
        return [self.model_class(**doc) for doc in documents]

    async def get_by_paciente_documento(self, numero_documento: str, skip: int = 0, limit: int = 100) -> List[Caso]:
        """Obtener casos por número de documento del paciente (cédula)."""
        return await self._get_casos_by_field("paciente.cedula", numero_documento, skip, limit)
    
    def _get_estados_finalizados(self) -> List[str]:
        """Obtener lista de estados considerados como finalizados."""
        return [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.CANCELADO.value]
    
    def _get_stats_field_name(self, estado: str) -> str:
        """Obtener nombre del campo en estadísticas según el estado."""
        estado_mapping = {
            EstadoCasoEnum.EN_PROCESO.value: "casos_en_proceso",
            EstadoCasoEnum.POR_FIRMAR.value: "casos_por_firmar",
            EstadoCasoEnum.POR_ENTREGAR.value: "casos_por_entregar",
            EstadoCasoEnum.COMPLETADO.value: "casos_completados",
            EstadoCasoEnum.CANCELADO.value: "casos_cancelados"
        }
        return estado_mapping.get(estado, "casos_otros")
    
    async def get_casos_por_año(self, año: int) -> List[Caso]:
        """Obtener todos los casos de un año específico sin limitación."""
        
        # Calcular fechas de inicio y fin del año
        inicio_año = datetime(año, 1, 1, 0, 0, 0, 0)
        fin_año = datetime(año, 12, 31, 23, 59, 59, 999999)
        
        # Query para obtener todos los casos del año
        query = {
            "fecha_creacion": {
                "$gte": inicio_año,
                "$lte": fin_año
            }
        }
        
        # Obtener todos los casos del año sin límite
        cursor = self.collection.find(query).sort("fecha_creacion", 1)
        documents = await cursor.to_list(length=None)  # Sin límite
        
        return [self.model_class(**doc) for doc in documents]
    
    async def get_casos_por_fecha_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Caso]:
        """Obtener todos los casos en un rango de fechas específico."""
        # Query para obtener todos los casos en el rango de fechas
        query = {
            "fecha_creacion": {
                "$gte": fecha_inicio,
                "$lte": fecha_fin
            }
        }
        
        # Obtener todos los casos en el rango sin límite
        cursor = self.collection.find(query).sort("fecha_creacion", 1)
        documents = await cursor.to_list(length=None)  # Sin límite
        
        return [self.model_class(**doc) for doc in documents]

    async def get_casos_por_entrega_rango(self, fecha_inicio: datetime, fecha_fin: datetime) -> List[Caso]:
        """Obtener todos los casos cuya fecha_entrega esté dentro del rango especificado."""
        query = {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin}}
        # Proyectar solo campos necesarios para el cálculo
        cursor = self.collection.find(query, {
            "fecha_creacion": 1,
            "fecha_entrega": 1,
            "estado": 1,
            "muestras": 1,
            "patologo_asignado": 1
        }).sort("fecha_entrega", 1)
        documents = await cursor.to_list(length=None)
        return [self.model_class(**doc) for doc in documents]

    async def get_oportunidad_por_mes_agregado(self, año: int) -> List[float]:
        """Calcular % de oportunidad por mes del año via agregación en MongoDB."""
        inicio_año = datetime(año, 1, 1)
        fin_año = datetime(año, 12, 31, 23, 59, 59, 999999)
        pipeline = [
            {"$match": {"fecha_entrega": {"$gte": inicio_año, "$lte": fin_año}}},
            {"$project": {
                "mes": {"$month": "$fecha_entrega"},
                "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, 1000 * 60 * 60 * 24]}, 6]}
            }},
            {"$group": {
                "_id": "$mes",
                "total": {"$sum": 1},
                "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}
            }},
            {"$project": {
                "mes": "$_id",
                "porcentaje": {"$cond": [{"$gt": ["$total", 0]}, {"$multiply": [{"$divide": ["$dentro", "$total"]}, 100]}, 0]}
            }},
        ]
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        # Inicializar 12 meses en 0.0 y rellenar
        meses = [0.0] * 12
        for item in result:
            mes_idx = int(item.get("mes", 0)) - 1
            if 0 <= mes_idx < 12:
                meses[mes_idx] = round(float(item.get("porcentaje", 0)), 2)
        return meses

    async def get_oportunidad_detalle_por_mes_agregado(self, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Detalle de oportunidad (por patólogo y por prueba) en el rango [fecha_inicio, fecha_fin] usando agregación."""
        day_ms = 1000 * 60 * 60 * 24
        pipeline = [
            {"$match": {"fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin}}},
            {"$facet": {
                "patologos": [
                    {"$project": {
                        "patologo": {"$ifNull": ["$patologo_asignado.nombre", "Sin patólogo"]},
                        "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]},
                        "dias": {"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}
                    }},
                    {"$group": {
                        "_id": "$patologo",
                        "total": {"$sum": 1},
                        "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}},
                        "tiempoPromedio": {"$avg": "$dias"}
                    }},
                    {"$project": {
                        "_id": 0,
                        "nombre": "$_id",
                        "dentroOportunidad": "$dentro",
                        "fueraOportunidad": {"$subtract": ["$total", "$dentro"]},
                        "tiempoPromedio": {"$round": ["$tiempoPromedio", 1]}
                    }},
                    {"$sort": {"nombre": 1}}
                ],
                "pruebas": [
                    {"$unwind": {"path": "$muestras", "preserveNullAndEmptyArrays": False}},
                    {"$unwind": {"path": "$muestras.pruebas", "preserveNullAndEmptyArrays": False}},
                    {"$project": {
                        "codigo": {"$ifNull": ["$muestras.pruebas.id", "$muestras.pruebas.pruebaCode"]},
                        "nombre": {"$ifNull": ["$muestras.pruebas.nombre", "$muestras.pruebas.pruebasName"]},
                        "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]}
                    }},
                    {"$group": {
                        "_id": {"codigo": "$codigo", "nombre": "$nombre"},
                        "total": {"$sum": 1},
                        "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}
                    }},
                    {"$project": {
                        "_id": 0,
                        "codigo": "$_id.codigo",
                        "nombre": "$_id.nombre",
                        "dentroOportunidad": "$dentro",
                        "fueraOportunidad": {"$subtract": ["$total", "$dentro"]},
                        "tiempoOportunidad": {"$literal": "7 días"}
                    }},
                    {"$sort": {"nombre": 1}}
                ],
                "resumen": [
                    {"$project": {
                        "dentro": {"$lte": [{"$divide": [{"$subtract": ["$fecha_entrega", "$fecha_creacion"]}, day_ms]}, 6]}
                    }},
                    {"$group": {
                        "_id": None,
                        "total": {"$sum": 1},
                        "dentro": {"$sum": {"$cond": ["$dentro", 1, 0]}}
                    }},
                    {"$project": {
                        "_id": 0,
                        "total": 1,
                        "dentro": 1,
                        "fuera": {"$subtract": ["$total", "$dentro"]}
                    }}
                ]
            }},
            {"$project": {"patologos": 1, "pruebas": 1, "resumen": 1}}
        ]

        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result:
            item = result[0]
            return {
                "patologos": item.get("patologos", []),
                "pruebas": item.get("pruebas", []),
                "resumen": (item.get("resumen", []) or [{}])[0]
            }
        return {"patologos": [], "pruebas": [], "resumen": {"total": 0, "dentro": 0, "fuera": 0}}
    
    async def get_estadisticas_muestras(self) -> MuestraStats:
        """Obtener estadísticas de muestras."""
        
        stats = MuestraStats()
        
        # Calcular fechas para el mes anterior y el mes anterior al anterior
        ahora = datetime.utcnow()
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        
        # Mes anterior al anterior
        if inicio_mes_anterior.month == 1:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(year=inicio_mes_anterior.year - 1, month=12)
        else:
            inicio_mes_anterior_anterior = inicio_mes_anterior.replace(month=inicio_mes_anterior.month - 1)
        
        fin_mes_anterior_anterior = inicio_mes_anterior - timedelta(seconds=1)
        
        # Contar muestras del mes anterior (excluyendo datos de prueba)
        pipeline_mes_anterior = [
            {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}}},
            {"$match": {"observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}},
            {"$unwind": "$muestras"},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
        result_mes_anterior = await self.collection.aggregate(pipeline_mes_anterior).to_list(length=1)
        stats.muestras_mes_anterior = result_mes_anterior[0]["total"] if result_mes_anterior else 0
        
        # Contar muestras del mes anterior al anterior (excluyendo datos de prueba)
        pipeline_mes_anterior_anterior = [
            {"$match": {"fecha_creacion": {"$gte": inicio_mes_anterior_anterior, "$lte": fin_mes_anterior_anterior}}},
            {"$match": {"observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}},
            {"$unwind": "$muestras"},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
        result_mes_anterior_anterior = await self.collection.aggregate(pipeline_mes_anterior_anterior).to_list(length=1)
        stats.muestras_mes_anterior_anterior = result_mes_anterior_anterior[0]["total"] if result_mes_anterior_anterior else 0
        
        # Calcular cambio porcentual
        if stats.muestras_mes_anterior_anterior > 0:
            stats.cambio_porcentual = round(((stats.muestras_mes_anterior - stats.muestras_mes_anterior_anterior) / stats.muestras_mes_anterior_anterior) * 100, 2)
        else:
            stats.cambio_porcentual = 100.0 if stats.muestras_mes_anterior > 0 else 0.0
        
        # Total de muestras (todas las muestras en el sistema, excluyendo datos de prueba)
        pipeline_total = [
            {"$match": {"observaciones_generales": {"$ne": "Datos de prueba generados automáticamente"}}},
            {"$unwind": "$muestras"},
            {"$group": {"_id": None, "total": {"$sum": 1}}}
        ]
        result_total = await self.collection.aggregate(pipeline_total).to_list(length=1)
        stats.total_muestras = result_total[0]["total"] if result_total else 0
        
        # Distribución por región del cuerpo (últimos 12 meses)
        inicio_12_meses = ahora - timedelta(days=365)
        pipeline_region = [
            {"$match": {"fecha_creacion": {"$gte": inicio_12_meses}}},
            {"$unwind": "$muestras"},
            {"$group": {"_id": "$muestras.region_cuerpo", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        result_region = await self.collection.aggregate(pipeline_region).to_list(length=None)
        stats.muestras_por_region = {item["_id"]: item["count"] for item in result_region}
        
        # Distribución por tipo de prueba (últimos 12 meses)
        pipeline_pruebas = [
            {"$match": {"fecha_creacion": {"$gte": inicio_12_meses}}},
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {"$group": {"_id": "$muestras.pruebas.nombre", "count": {"$sum": 1}}},
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        result_pruebas = await self.collection.aggregate(pipeline_pruebas).to_list(length=None)
        stats.muestras_por_tipo_prueba = {item["_id"]: item["count"] for item in result_pruebas}
        
        # Calcular tiempo promedio de procesamiento (casos completados)
        pipeline_tiempo = [
            {"$match": {"estado": EstadoCasoEnum.COMPLETADO.value}},
            {"$match": {"fecha_firma": {"$exists": True, "$ne": None}}},
            {"$project": {
                "tiempo_procesamiento": {
                    "$divide": [
                        {"$subtract": ["$fecha_firma", "$fecha_creacion"]},
                        1000 * 60 * 60 * 24  # Convertir a días
                    ]
                }
            }},
            {"$group": {
                "_id": None,
                "tiempo_promedio": {"$avg": "$tiempo_procesamiento"}
            }}
        ]
        result_tiempo = await self.collection.aggregate(pipeline_tiempo).to_list(length=1)
        if result_tiempo and result_tiempo[0]["tiempo_promedio"]:
            stats.tiempo_promedio_procesamiento = round(result_tiempo[0]["tiempo_promedio"], 2)
        
        return stats

    async def get_entidades_por_patologo(self, patologo: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener entidades donde ha trabajado un patólogo específico."""
        # Construir el pipeline de agregación
        pipeline = [
            # Filtrar por patólogo (buscar en el nombre del patólogo asignado)
            {
                "$match": {
                    "patologo_asignado.nombre": {"$regex": patologo, "$options": "i"}
                }
            }
        ]
        
        # Agregar filtros de fecha si se proporcionan
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        
        # Continuar con el pipeline
        pipeline.extend([
            # Agrupar por entidad
            {
                "$group": {
                    "_id": "$paciente.entidad_info.nombre",
                    "codigo_entidad": {"$first": "$paciente.entidad_info.codigo"},
                    "casesCount": {"$sum": 1},
                    "tipos_atencion": {"$addToSet": "$paciente.tipo_atencion"}
                }
            },
            # Proyectar el resultado final
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id",
                    "codigo": "$codigo_entidad",
                    "casesCount": 1,
                    "type": {"$arrayElemAt": ["$tipos_atencion", 0]},  # Tomar el primer tipo de atención
                    "tipos_atencion": 1
                }
            },
            # Ordenar por número de casos descendente
            {"$sort": {"casesCount": -1}}
        ])
        
        # Ejecutar la agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Debug temporal
        print(f"Pipeline de entidades: {pipeline}")
        print(f"Resultado de agregación: {result}")
        
        # Procesar y limpiar los resultados
        entidades = []
        for item in result:
            if item.get("name"):  # Solo incluir si tiene nombre de entidad
                entidades.append({
                    "name": item["name"],
                    "codigo": item.get("codigo", ""),
                    "type": item.get("type", "No especificado"),
                    "casesCount": item["casesCount"],
                    "tipos_atencion": item.get("tipos_atencion", [])
                })
        
        print(f"Entidades procesadas: {entidades}")
        return entidades

    async def get_pruebas_por_patologo(self, patologo: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener pruebas realizadas por un patólogo específico."""
        # Construir el pipeline de agregación
        pipeline = [
            # Filtrar por patólogo (buscar en el nombre del patólogo asignado)
            {
                "$match": {
                    "patologo_asignado.nombre": {"$regex": patologo, "$options": "i"}
                }
            }
        ]
        
        # Agregar filtros de fecha si se proporcionan
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        
        # Continuar con el pipeline
        pipeline.extend([
            # Descomponer las muestras
            {"$unwind": "$muestras"},
            # Descomponer las pruebas dentro de cada muestra
            {"$unwind": "$muestras.pruebas"},
            # Agrupar por prueba
            {
                "$group": {
                    "_id": {
                        "nombre": "$muestras.pruebas.nombre",
                        "codigo": "$muestras.pruebas.codigo"
                    },
                    "count": {"$sum": 1},
                    "categorias": {"$addToSet": "$muestras.pruebas.categoria"}
                }
            },
            # Proyectar el resultado final
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.nombre",
                    "codigo": "$_id.codigo",
                    "count": 1,
                    "category": {"$arrayElemAt": ["$categorias", 0]},  # Tomar la primera categoría
                    "categorias": 1
                }
            },
            # Ordenar por número de pruebas descendente
            {"$sort": {"count": -1}}
        ])
        
        # Ejecutar la agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Procesar y limpiar los resultados
        pruebas = []
        for item in result:
            if item.get("name"):  # Solo incluir si tiene nombre de prueba
                pruebas.append({
                    "name": item["name"],
                    "codigo": item.get("codigo", ""),
                    "category": item.get("category", "No especificada"),
                    "count": item["count"],
                    "categorias": item.get("categorias", [])
                })
        
        return pruebas

    async def get_estadisticas_entidades_mensual(self, fecha_inicio: datetime, fecha_fin: datetime, entity: Optional[str] = None) -> Dict[str, Any]:
        """Obtener estadísticas de entidades por mes con distribución de ambulatorios y hospitalizados."""
        # Construir el filtro base por fecha y estado
        match_filter = {
            "fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin},
            "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}  # Solo casos completados o por entregar
        }
        
        # Si se especifica una entidad, agregar el filtro
        if entity and entity.strip():
            match_filter["paciente.entidad_info.codigo"] = entity.strip()
        
        # Si se filtra por entidad específica, usar pipeline diferente
        if entity and entity.strip():
            # Pipeline para entidad específica - no agrupar por entidad
            pipeline = [
                {
                    "$match": match_filter
                },
                {
                    "$group": {
                        "_id": None,  # No agrupar por entidad
                        "codigo_entidad": {"$first": "$paciente.entidad_info.codigo"},
                        "nombre_entidad": {"$first": "$paciente.entidad_info.nombre"},
                        "total_casos": {"$sum": 1},
                        "ambulatorios": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "hospitalizados": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "nombre": "$nombre_entidad",
                        "codigo": "$codigo_entidad",
                        "ambulatorios": 1,
                        "hospitalizados": 1,
                        "total": "$total_casos"
                    }
                }
            ]
        else:
            # Pipeline original para todas las entidades
            pipeline = [
                {
                    "$match": match_filter
                },
                {
                    "$group": {
                        "_id": "$paciente.entidad_info.codigo",  # Agrupar por código en lugar de nombre
                        "nombre_entidad": {"$first": "$paciente.entidad_info.nombre"},
                        "total_casos": {"$sum": 1},
                        "ambulatorios": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]},
                                    1,
                                    0
                                ]
                            }
                        },
                        "hospitalizados": {
                            "$sum": {
                                "$cond": [
                                    {"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]},
                                    1,
                                    0
                                ]
                            }
                        }
                    }
                },
                {
                    "$project": {
                        "_id": 0,
                        "nombre": "$nombre_entidad",
                        "codigo": "$_id",  # El código es el _id del grupo
                        "ambulatorios": 1,
                        "hospitalizados": 1,
                        "total": "$total_casos"
                    }
                },
                {
                    "$sort": {"total": -1}
                }
            ]
        
        # Ejecutar la agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Calcular resumen
        total_ambulatorios = sum(item["ambulatorios"] for item in result)
        total_hospitalizados = sum(item["hospitalizados"] for item in result)
        total_pacientes = total_ambulatorios + total_hospitalizados
        
        # Calcular tiempo promedio de procesamiento
        pipeline_tiempo = [
            {
                "$match": {
                    "fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin},
                    "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}
                }
            },
            {
                "$project": {
                    "tiempo_dias": {
                        "$divide": [
                            {"$subtract": ["$fecha_entrega", "$fecha_creacion"]},
                            1000 * 60 * 60 * 24  # Convertir milisegundos a días
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "tiempo_promedio": {"$avg": "$tiempo_dias"}
                }
            }
        ]
        
        # Si se especifica una entidad, agregar el filtro al pipeline de tiempo
        if entity and entity.strip():
            pipeline_tiempo[0]["$match"]["paciente.entidad_info.codigo"] = entity.strip()
        
        tiempo_result = await self.collection.aggregate(pipeline_tiempo).to_list(length=1)
        tiempo_promedio = tiempo_result[0]["tiempo_promedio"] if tiempo_result else 0
        
        return {
            "entities": result,
            "summary": {
                "total": total_pacientes,
                "ambulatorios": total_ambulatorios,
                "hospitalizados": total_hospitalizados,
                "tiempoPromedio": round(tiempo_promedio, 1)
            }
        }

    async def get_debug_entidades(self, fecha_inicio: datetime, fecha_fin: datetime, entity: Optional[str] = None) -> Dict[str, Any]:
        """Método de depuración para ver los datos reales de entidades."""
        # Primero, vamos a ver qué datos hay en la base de datos sin filtros restrictivos
        basic_filter = {
            "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}
        }
        
        # Contar casos por fecha_creacion (sin filtro de estado)
        total_casos_creacion = await self.collection.count_documents(basic_filter)
        
        # Contar casos con fecha_entrega
        fecha_entrega_filter = {
            "fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin, "$exists": True, "$ne": None}
        }
        total_casos_entrega = await self.collection.count_documents(fecha_entrega_filter)
        
        # Contar casos completados por fecha_creacion
        completados_filter = {
            "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin},
            "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}
        }
        total_casos_completados = await self.collection.count_documents(completados_filter)
        
        # Construir el filtro que estaba usando antes
        match_filter = {
            "fecha_entrega": {"$gte": fecha_inicio, "$lte": fecha_fin},
            "estado": {"$in": [EstadoCasoEnum.COMPLETADO.value, EstadoCasoEnum.POR_ENTREGAR.value]}
        }
        
        # Si se especifica una entidad, agregar el filtro
        if entity and entity.strip():
            match_filter["paciente.entidad_info.codigo"] = entity.strip()
        
        # Pipeline simple para ver los datos sin procesar
        pipeline = [
            {
                "$match": match_filter
            },
            {
                "$project": {
                    "_id": 0,
                    "caso_code": "$caso_code",
                    "fecha_creacion": "$fecha_creacion",
                    "entidad_nombre": "$paciente.entidad_info.nombre",
                    "entidad_codigo": "$paciente.entidad_info.codigo",
                    "tipo_atencion": "$paciente.tipo_atencion",
                    "fecha_entrega": "$fecha_entrega"
                }
            },
            {
                "$limit": 20  # Limitar a 20 casos para no sobrecargar
            }
        ]
        
        # Ejecutar la agregación
        casos_raw = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Contar totales simples
        total_casos = await self.collection.count_documents(match_filter)
        
        # Contar por tipo de atención
        pipeline_count = [
            {
                "$match": match_filter
            },
            {
                "$group": {
                    "_id": "$paciente.tipo_atencion",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        counts = await self.collection.aggregate(pipeline_count).to_list(length=None)
        tipo_atencion_counts = {item["_id"]: item["count"] for item in counts}
        
        return {
            "total_casos_por_fecha_creacion": total_casos_creacion,
            "total_casos_con_fecha_entrega": total_casos_entrega, 
            "total_casos_completados": total_casos_completados,
            "total_casos_filtro_actual": total_casos,
            "tipo_atencion_counts": tipo_atencion_counts,
            "casos_ejemplo": casos_raw,
            "filtro_aplicado": match_filter,
            "filtros_probados": {
                "fecha_creacion": basic_filter,
                "fecha_entrega": fecha_entrega_filter,
                "completados": completados_filter
            }
        }

    async def get_detalle_entidad(self, entidad: str, fecha_inicio: datetime, fecha_fin: datetime) -> Dict[str, Any]:
        """Obtener detalles completos de una entidad específica."""
        # Pipeline para estadísticas básicas
        pipeline_basicas = [
            {
                "$match": {
                    "paciente.entidad_info.codigo": entidad,
                    "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_pacientes": {"$sum": 1},
                    "ambulatorios": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$paciente.tipo_atencion", "Ambulatorio"]},
                                1,
                                0
                            ]
                        }
                    },
                    "hospitalizados": {
                        "$sum": {
                            "$cond": [
                                {"$eq": ["$paciente.tipo_atencion", "Hospitalizado"]},
                                1,
                                0
                            ]
                        }
                    },
                    "total_muestras": {"$sum": {"$size": "$muestras"}}
                }
            }
        ]
        
        # Pipeline para tiempos de procesamiento
        pipeline_tiempos = [
            {
                "$match": {
                    "paciente.entidad_info.codigo": entidad,
                    "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin},
                    "fecha_entrega": {"$exists": True, "$ne": None}
                }
            },
            {
                "$project": {
                    "tiempo_dias": {
                        "$divide": [
                            {"$subtract": ["$fecha_entrega", "$fecha_creacion"]},
                            1000 * 60 * 60 * 24
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "promedio_dias": {"$avg": "$tiempo_dias"},
                    "minimo_dias": {"$min": "$tiempo_dias"},
                    "maximo_dias": {"$max": "$tiempo_dias"},
                    "muestras_completadas": {"$sum": 1}
                }
            }
        ]
        
        # Pipeline para pruebas más solicitadas
        pipeline_pruebas = [
            {
                "$match": {
                    "paciente.entidad_info.codigo": entidad,
                    "fecha_creacion": {"$gte": fecha_inicio, "$lte": fecha_fin}
                }
            },
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {
                "$group": {
                    "_id": {
                        "codigo": "$muestras.pruebas.codigo",
                        "nombre": "$muestras.pruebas.nombre"
                    },
                    "total_solicitudes": {"$sum": 1}
                }
            },
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.codigo",
                    "nombre": "$_id.nombre",
                    "total_solicitudes": 1
                }
            },
            {"$sort": {"total_solicitudes": -1}},
            {"$limit": 10}
        ]
        
        # Ejecutar todas las agregaciones
        basicas_result = await self.collection.aggregate(pipeline_basicas).to_list(length=1)
        tiempos_result = await self.collection.aggregate(pipeline_tiempos).to_list(length=1)
        pruebas_result = await self.collection.aggregate(pipeline_pruebas).to_list(length=None)
        
        # Procesar resultados
        basicas = basicas_result[0] if basicas_result else {
            "total_pacientes": 0,
            "ambulatorios": 0,
            "hospitalizados": 0,
            "total_muestras": 0
        }
        
        tiempos = tiempos_result[0] if tiempos_result else {
            "promedio_dias": 0,
            "minimo_dias": 0,
            "maximo_dias": 0,
            "muestras_completadas": 0
        }
        
        promedio_muestras = basicas["total_muestras"] / basicas["total_pacientes"] if basicas["total_pacientes"] > 0 else 0
        
        return {
            "estadisticas_basicas": {
                "total_pacientes": basicas["total_pacientes"],
                "ambulatorios": basicas["ambulatorios"],
                "hospitalizados": basicas["hospitalizados"],
                "promedio_muestras_por_paciente": round(promedio_muestras, 1)
            },
            "tiempos_procesamiento": {
                "promedio_dias": round(tiempos["promedio_dias"], 1),
                "minimo_dias": round(tiempos["minimo_dias"], 1),
                "maximo_dias": round(tiempos["maximo_dias"], 1),
                "muestras_completadas": tiempos["muestras_completadas"]
            },
            "pruebas_mas_solicitadas": pruebas_result
        }

    async def get_patologos_por_entidad(self, entidad: str, filtros_fecha: Dict[str, Any] = None) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una entidad específica."""
        pipeline = [
            # Filtrar por entidad
            {
                "$match": {
                    "paciente.entidad_info.codigo": entidad,
                    "patologo_asignado": {"$exists": True, "$ne": None}
                }
            }
        ]
        
        # Agregar filtros de fecha si se proporcionan
        if filtros_fecha:
            pipeline[0]["$match"].update(filtros_fecha)
        
        # Continuar con el pipeline
        pipeline.extend([
            # Agrupar por patólogo
            {
                "$group": {
                    "_id": {
                        "codigo": "$patologo_asignado.codigo",
                        "nombre": "$patologo_asignado.nombre"
                    },
                    "casesCount": {"$sum": 1}
                }
            },
            # Proyectar el resultado final
            {
                "$project": {
                    "_id": 0,
                    "name": "$_id.nombre",
                    "codigo": "$_id.codigo",
                    "casesCount": 1
                }
            },
            # Ordenar por número de casos descendente
            {"$sort": {"casesCount": -1}}
        ])
        
        # Ejecutar la agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Procesar y limpiar los resultados
        patologos = []
        for item in result:
            if item.get("name"):  # Solo incluir si tiene nombre de patólogo
                patologos.append({
                    "name": item["name"],
                    "codigo": item.get("codigo", ""),
                    "casesCount": item["casesCount"]
                })
        
        return patologos

    # ============================================================================
    # MÉTODOS PARA ESTADÍSTICAS DE PRUEBAS
    # ============================================================================

    async def get_estadisticas_pruebas_mensual(self, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        """Obtener estadísticas de pruebas por mes/año y opcionalmente por entidad."""
        
        # Calcular fechas del mes
        inicio_mes = datetime(year, month, 1)
        if month == 12:
            fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            fin_mes = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Construir pipeline base
        pipeline = [
            # Filtrar por rango de fechas
            {
                "$match": {
                    "fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes}
                }
            }
        ]
        
        # Agregar filtro de entidad si se especifica
        if entity:
            pipeline[0]["$match"]["paciente.entidad_info.codigo"] = entity
        
        # Continuar con el pipeline
        pipeline.extend([
            # Descomponer muestras
            {"$unwind": "$muestras"},
            # Descomponer pruebas dentro de cada muestra
            {"$unwind": "$muestras.pruebas"},
            # Agrupar por prueba
            {
                "$group": {
                    "_id": {
                        "codigo": "$muestras.pruebas.id",
                        "nombre": "$muestras.pruebas.nombre"
                    },
                    "total_solicitadas": {"$sum": 1},
                    "casos_ids": {"$addToSet": "$_id"}
                }
            },
            # Proyectar resultado
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.codigo",
                    "nombre": "$_id.nombre",
                    "total_solicitadas": 1,
                    "casos_ids": 1
                }
            },
            # Ordenar por total de solicitudes descendente
            {"$sort": {"total_solicitadas": -1}}
        ])
        
        # Ejecutar agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Calcular estadísticas adicionales para cada prueba
        pruebas_stats = []
        for prueba in result:
            # Obtener casos completados para esta prueba
            casos_completados = await self._contar_casos_completados_por_prueba(
                prueba["casos_ids"], 
                prueba["codigo"]
            )
            
            # Calcular tiempo promedio
            tiempo_promedio = await self._calcular_tiempo_promedio_prueba(
                prueba["casos_ids"], 
                prueba["codigo"]
            )
            
            # Calcular porcentaje completado
            porcentaje_completado = (
                (casos_completados / prueba["total_solicitadas"]) * 100 
                if prueba["total_solicitadas"] > 0 else 0
            )
            
            pruebas_stats.append({
                "codigo": prueba["codigo"],
                "nombre": prueba["nombre"],
                "total_solicitadas": prueba["total_solicitadas"],
                "total_completadas": casos_completados,
                "tiempo_promedio": tiempo_promedio,
                "porcentaje_completado": round(porcentaje_completado, 1)
            })
        
        return pruebas_stats

    async def get_detalle_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        """Obtener detalles completos de una prueba específica."""
        
        # Calcular fechas del mes
        inicio_mes = datetime(year, month, 1)
        if month == 12:
            fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            fin_mes = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Construir pipeline base
        pipeline = [
            # Filtrar por rango de fechas y prueba específica
            {
                "$match": {
                    "fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes},
                    "muestras.pruebas.id": codigo_prueba
                }
            }
        ]
        
        # Agregar filtro de entidad si se especifica
        if entity:
            pipeline[0]["$match"]["paciente.entidad_info.codigo"] = entity
        
        # Continuar con el pipeline
        pipeline.extend([
            # Descomponer muestras
            {"$unwind": "$muestras"},
            # Filtrar solo la prueba específica
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            # Descomponer pruebas
            {"$unwind": "$muestras.pruebas"},
            # Filtrar la prueba específica nuevamente
            {"$match": {"muestras.pruebas.id": codigo_prueba}}
        ])
        
        # Ejecutar agregación para obtener casos
        casos = await self.collection.aggregate(pipeline).to_list(length=None)
        
        if not casos:
            return {
                "estadisticas_principales": {
                    "total_solicitadas": 0,
                    "total_completadas": 0,
                    "porcentaje_completado": 0
                },
                "tiempos_procesamiento": {
                    "promedio_dias": 0,
                    "dentro_oportunidad": 0,
                    "fuera_oportunidad": 0,
                    "total_casos": 0
                },
                "patologos": []
            }
        
        # Calcular estadísticas principales
        total_solicitadas = len(casos)
        casos_completados = [c for c in casos if c.get("estado") == EstadoCasoEnum.COMPLETADO.value]
        total_completadas = len(casos_completados)
        porcentaje_completado = (
            (total_completadas / total_solicitadas) * 100 
            if total_solicitadas > 0 else 0
        )
        
        # Calcular tiempos de procesamiento
        tiempos = await self._calcular_tiempos_prueba(casos)
        
        # Obtener patólogos
        patologos = await self._obtener_patologos_por_prueba(casos)
        
        return {
            "estadisticas_principales": {
                "total_solicitadas": total_solicitadas,
                "total_completadas": total_completadas,
                "porcentaje_completado": round(porcentaje_completado, 1)
            },
            "tiempos_procesamiento": tiempos,
            "patologos": patologos
        }

    async def get_patologos_por_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una prueba específica."""
        
        # Calcular fechas del mes
        inicio_mes = datetime(year, month, 1)
        if month == 12:
            fin_mes = datetime(year + 1, 1, 1) - timedelta(seconds=1)
        else:
            fin_mes = datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        # Construir pipeline
        pipeline = [
            # Filtrar por rango de fechas y prueba específica
            {
                "$match": {
                    "fecha_creacion": {"$gte": inicio_mes, "$lte": fin_mes},
                    "muestras.pruebas.id": codigo_prueba,
                    "patologo_asignado": {"$exists": True, "$ne": None}
                }
            },
            # Descomponer muestras
            {"$unwind": "$muestras"},
            # Filtrar solo la prueba específica
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            # Agrupar por patólogo
            {
                "$group": {
                    "_id": {
                        "codigo": "$patologo_asignado.codigo",
                        "nombre": "$patologo_asignado.nombre"
                    },
                    "total_procesadas": {"$sum": 1},
                    "casos_ids": {"$addToSet": "$_id"}
                }
            },
            # Proyectar resultado
            {
                "$project": {
                    "_id": 0,
                    "codigo": "$_id.codigo",
                    "nombre": "$_id.nombre",
                    "total_procesadas": 1,
                    "casos_ids": 1
                }
            },
            # Ordenar por total de casos procesados descendente
            {"$sort": {"total_procesadas": -1}}
        ]
        
        # Agregar filtro de entidad si se especifica
        if entity:
            pipeline[0]["$match"]["paciente.entidad_info.codigo"] = entity
        
        # Ejecutar agregación
        result = await self.collection.aggregate(pipeline).to_list(length=None)
        
        # Calcular tiempo promedio para cada patólogo
        patologos_stats = []
        for patologo in result:
            tiempo_promedio = await self._calcular_tiempo_promedio_patologo_prueba(
                patologo["casos_ids"], 
                codigo_prueba
            )
            
            patologos_stats.append({
                "codigo": patologo["codigo"],
                "nombre": patologo["nombre"],
                "total_procesadas": patologo["total_procesadas"],
                "tiempo_promedio": tiempo_promedio
            })
        
        return patologos_stats

    # ============================================================================
    # MÉTODOS AUXILIARES PARA ESTADÍSTICAS DE PRUEBAS
    # ============================================================================

    async def _contar_casos_completados_por_prueba(self, casos_ids: List[str], codigo_prueba: str) -> int:
        """Contar casos completados para una prueba específica."""
        if not casos_ids:
            return 0
        
        pipeline = [
            {
                "$match": {
                    "_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]},
                    "estado": EstadoCasoEnum.COMPLETADO.value,
                    "muestras.pruebas.id": codigo_prueba
                }
            },
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {"$count": "total"}
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        return result[0]["total"] if result else 0

    async def _calcular_tiempo_promedio_prueba(self, casos_ids: List[str], codigo_prueba: str) -> float:
        """Calcular tiempo promedio de procesamiento para una prueba específica."""
        if not casos_ids:
            return 0.0
        
        pipeline = [
            {
                "$match": {
                    "_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]},
                    "estado": EstadoCasoEnum.COMPLETADO.value,
                    "fecha_entrega": {"$exists": True, "$ne": None},
                    "muestras.pruebas.id": codigo_prueba
                }
            },
            {"$unwind": "$muestras"},
            {"$match": {"muestras.pruebas.id": codigo_prueba}},
            {
                "$project": {
                    "tiempo_dias": {
                        "$divide": [
                            {"$subtract": ["$fecha_entrega", "$fecha_creacion"]},
                            1000 * 60 * 60 * 24  # Convertir a días
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "tiempo_promedio": {"$avg": "$tiempo_dias"}
                }
            }
        ]
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result and result[0]["tiempo_promedio"] is not None:
            return round(result[0]["tiempo_promedio"], 1)
        return 0.0

    async def _calcular_tiempos_prueba(self, casos: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Calcular estadísticas de tiempo para una prueba."""
        casos_completados = [c for c in casos if c.get("estado") == EstadoCasoEnum.COMPLETADO.value]
        
        if not casos_completados:
            return {
                "promedio_dias": 0,
                "dentro_oportunidad": 0,
                "fuera_oportunidad": 0,
                "total_casos": 0
            }
        
        # Calcular tiempos de procesamiento
        tiempos_dias = []
        dentro_oportunidad = 0
        fuera_oportunidad = 0
        
        for caso in casos_completados:
            if caso.get("fecha_entrega") and caso.get("fecha_creacion"):
                tiempo = (caso["fecha_entrega"] - caso["fecha_creacion"]).days
                tiempos_dias.append(tiempo)
                
                if tiempo <= 6:  # Dentro de oportunidad (≤6 días)
                    dentro_oportunidad += 1
                else:
                    fuera_oportunidad += 1
        
        promedio_dias = sum(tiempos_dias) / len(tiempos_dias) if tiempos_dias else 0
        
        return {
            "promedio_dias": round(promedio_dias, 1),
            "dentro_oportunidad": dentro_oportunidad,
            "fuera_oportunidad": fuera_oportunidad,
            "total_casos": len(casos_completados)
        }

    async def _obtener_patologos_por_prueba(self, casos: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una prueba específica."""
        patologos_map = {}
        
        for caso in casos:
            if caso.get("patologo_asignado"):
                patologo = caso["patologo_asignado"]
                codigo = patologo.get("codigo", "")
                nombre = patologo.get("nombre", "")
                
                if codigo not in patologos_map:
                    patologos_map[codigo] = {
                        "codigo": codigo,
                        "nombre": nombre,
                        "total_procesadas": 0,
                        "tiempo_promedio": 0.0
                    }
                
                patologos_map[codigo]["total_procesadas"] += 1
        
        # Calcular tiempo promedio para cada patólogo
        for codigo, patologo in patologos_map.items():
            tiempo_promedio = await self._calcular_tiempo_promedio_patologo_prueba(
                [c["_id"] for c in casos if c.get("patologo_asignado", {}).get("codigo") == codigo],
                ""  # No necesitamos codigo_prueba aquí
            )
            patologo["tiempo_promedio"] = tiempo_promedio
        
        # Convertir a lista y ordenar por total procesadas
        patologos_list = list(patologos_map.values())
        patologos_list.sort(key=lambda x: x["total_procesadas"], reverse=True)
        
        return patologos_list

    async def _calcular_tiempo_promedio_patologo_prueba(self, casos_ids: List[str], codigo_prueba: str) -> float:
        """Calcular tiempo promedio de procesamiento para un patólogo en una prueba específica."""
        if not casos_ids:
            return 0.0
        
        pipeline = [
            {
                "$match": {
                    "_id": {"$in": [ObjectId(cid) for cid in casos_ids if ObjectId.is_valid(cid)]},
                    "estado": EstadoCasoEnum.COMPLETADO.value,
                    "fecha_entrega": {"$exists": True, "$ne": None}
                }
            }
        ]
        
        # Agregar filtro de prueba si se especifica
        if codigo_prueba:
            pipeline[0]["$match"]["muestras.pruebas.id"] = codigo_prueba
        
        pipeline.extend([
            {
                "$project": {
                    "tiempo_dias": {
                        "$divide": [
                            {"$subtract": ["$fecha_entrega", "$fecha_creacion"]},
                            1000 * 60 * 60 * 24  # Convertir a días
                        ]
                    }
                }
            },
            {
                "$group": {
                    "_id": None,
                    "tiempo_promedio": {"$avg": "$tiempo_dias"}
                }
            }
        ])
        
        result = await self.collection.aggregate(pipeline).to_list(length=1)
        if result and result[0]["tiempo_promedio"] is not None:
            return round(result[0]["tiempo_promedio"], 1)
        return 0.0