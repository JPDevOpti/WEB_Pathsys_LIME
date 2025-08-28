"""Repositorio para el módulo de pacientes"""

from typing import List, Optional, Dict, Any
from datetime import datetime, timezone
from motor.motor_asyncio import AsyncIOMotorDatabase
from pymongo.errors import DuplicateKeyError

from ..models import Paciente
from ..schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteSearch
)
from app.core.exceptions import ConflictError, NotFoundError


class PacienteRepository:
    """Repositorio para operaciones de base de datos de pacientes"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.db = database
        self.collection = database.pacientes

    def _convert_doc_to_response(self, doc: dict) -> dict:
        """Convierte un documento de MongoDB al formato de respuesta"""
        if doc:
            # Asignar explícitamente el campo id desde _id
            doc["id"] = str(doc["_id"])
            doc["paciente_code"] = doc.get("paciente_code", "")
        return doc

    async def create(self, paciente: PacienteCreate) -> dict:
        """Crear un nuevo paciente"""
        try:
            # Preparar datos del paciente
            paciente_data = paciente.dict(exclude={"paciente_code"})
            paciente_data["paciente_code"] = paciente.paciente_code
            paciente_data["fecha_creacion"] = datetime.now(timezone.utc)
            paciente_data["fecha_actualizacion"] = datetime.now(timezone.utc)
            paciente_data["id_casos"] = []

            # Insertar en la base de datos
            await self.collection.insert_one(paciente_data)

            # Recuperar el paciente creado
            created_patient = await self.collection.find_one({"paciente_code": paciente.paciente_code})
            if not created_patient:
                raise ConflictError("Error al crear el paciente")
            return self._convert_doc_to_response(dict(created_patient))

        except DuplicateKeyError:
            raise ConflictError(f"Ya existe un paciente con el código {paciente.paciente_code}")

    async def get_by_id(self, paciente_id: str) -> Optional[dict]:
        """Obtener un paciente por su ID (paciente_code)"""
        paciente = await self.collection.find_one({"paciente_code": paciente_id})
        if not paciente:
            return None
        return self._convert_doc_to_response(dict(paciente))

    async def get_by_paciente_code(self, paciente_code: str) -> Optional[dict]:
        """Buscar un paciente por su código"""
        return await self.get_by_id(paciente_code)

    async def update(self, paciente_id: str, paciente_update: PacienteUpdate) -> dict:
        """Actualizar un paciente existente"""
        # Verificar que el paciente existe
        existing_patient = await self.collection.find_one({"paciente_code": paciente_id})
        if not existing_patient:
            raise NotFoundError("Paciente no encontrado")

        # Preparar datos para actualización (solo campos no nulos)
        update_data = {k: v for k, v in paciente_update.dict().items() if v is not None}
        if update_data:
            update_data["fecha_actualizacion"] = datetime.now(timezone.utc)
            
            # Actualizar el paciente
            await self.collection.update_one(
                {"paciente_code": paciente_id},
                {"$set": update_data}
            )

        # Retornar el paciente actualizado
        updated_patient = await self.collection.find_one({"paciente_code": paciente_id})
        if not updated_patient:
            raise NotFoundError("Paciente no encontrado después de la actualización")
        return self._convert_doc_to_response(dict(updated_patient))

    async def delete(self, paciente_id: str) -> bool:
        """Eliminar un paciente"""
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
        """Listar pacientes con filtros básicos"""
        # Construir filtro de búsqueda
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
        
        # Ejecutar consulta con paginación
        cursor = self.collection.find(filtro).skip(skip).limit(limit).sort("fecha_creacion", -1)
        pacientes = await cursor.to_list(length=limit)
        
        return [self._convert_doc_to_response(p) for p in pacientes]

    async def advanced_search(self, search_params: PacienteSearch) -> Dict[str, Any]:
        """Búsqueda avanzada de pacientes con múltiples filtros"""
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
        
        if search_params.tiene_casos is not None:
            if search_params.tiene_casos:
                filtro["id_casos"] = {"$exists": True, "$not": {"$size": 0}}
            else:
                filtro["$or"] = [
                    {"id_casos": {"$exists": False}},
                    {"id_casos": {"$size": 0}}
                ]
        
        if search_params.fecha_desde or search_params.fecha_hasta:
            fecha_filter = {}
            if search_params.fecha_desde:
                fecha_filter["$gte"] = datetime.fromisoformat(search_params.fecha_desde)
            if search_params.fecha_hasta:
                fecha_filter["$lte"] = datetime.fromisoformat(search_params.fecha_hasta + "T23:59:59")
            filtro["fecha_creacion"] = fecha_filter
        
        # Contar total de resultados
        total = await self.collection.count_documents(filtro)
        
        # Ejecutar consulta con paginación
        cursor = self.collection.find(filtro).skip(search_params.skip).limit(search_params.limit).sort("fecha_creacion", -1)
        pacientes = await cursor.to_list(length=search_params.limit)
        
        return {
            "pacientes": [self._convert_doc_to_response(p) for p in pacientes],
            "total": total,
            "skip": search_params.skip,
            "limit": search_params.limit,
            "filtros_aplicados": {
                k: v for k, v in {
                    "nombre": search_params.nombre,
                    "paciente_code": search_params.paciente_code,
                    "edad_min": search_params.edad_min,
                    "edad_max": search_params.edad_max,
                    "entidad": search_params.entidad,
                    "sexo": search_params.sexo,
                    "tipo_atencion": search_params.tipo_atencion,
                    "tiene_casos": search_params.tiene_casos,
                    "fecha_desde": search_params.fecha_desde,
                    "fecha_hasta": search_params.fecha_hasta
                }.items() if v is not None
            }
        }

    async def get_statistics(self) -> Dict[str, Any]:
        """Obtener estadísticas generales de pacientes"""
        from datetime import datetime, timedelta
        
        # Agregación para obtener estadísticas generales (excluyendo datos de prueba)
        pipeline_general = [
            {
                "$match": {
                    "observaciones": {"$ne": "Datos de prueba generados automáticamente"}
                }
            },
            {
                "$group": {
                    "_id": None,
                    "total_pacientes": {"$sum": 1},
                    "promedio_edad": {"$avg": "$edad"},
                    "edad_minima": {"$min": "$edad"},
                    "edad_maxima": {"$max": "$edad"}
                }
            }
        ]
        
        stats_general = await self.collection.aggregate(pipeline_general).to_list(1)
        
        # Estadísticas por sexo (excluyendo datos de prueba)
        pipeline_sexo = [
            {
                "$match": {
                    "observaciones": {"$ne": "Datos de prueba generados automáticamente"}
                }
            },
            {
                "$group": {
                    "_id": "$sexo",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats_sexo = await self.collection.aggregate(pipeline_sexo).to_list(None)
        
        # Estadísticas por entidad (excluyendo datos de prueba)
        pipeline_entidad = [
            {
                "$match": {
                    "observaciones": {"$ne": "Datos de prueba generados automáticamente"}
                }
            },
            {
                "$group": {
                    "_id": "$entidad_info.nombre",
                    "count": {"$sum": 1}
                }
            },
            {"$sort": {"count": -1}},
            {"$limit": 10}
        ]
        
        stats_entidad = await self.collection.aggregate(pipeline_entidad).to_list(10)
        
        # Estadísticas por tipo de atención (excluyendo datos de prueba)
        pipeline_atencion = [
            {
                "$match": {
                    "observaciones": {"$ne": "Datos de prueba generados automáticamente"}
                }
            },
            {
                "$group": {
                    "_id": "$tipo_atencion",
                    "count": {"$sum": 1}
                }
            }
        ]
        
        stats_atencion = await self.collection.aggregate(pipeline_atencion).to_list(None)
        
        # Estadísticas de pacientes con casos (excluyendo datos de prueba)
        pipeline_casos = [
            {
                "$match": {
                    "observaciones": {"$ne": "Datos de prueba generados automáticamente"}
                }
            },
            {
                "$project": {
                    "tiene_casos": {"$gt": [{"$size": "$id_casos"}, 0]},
                    "cantidad_casos": {"$size": "$id_casos"}
                }
            },
            {
                "$group": {
                    "_id": "$tiene_casos",
                    "count": {"$sum": 1},
                    "promedio_casos": {"$avg": "$cantidad_casos"}
                }
            }
        ]
        
        stats_casos = await self.collection.aggregate(pipeline_casos).to_list(None)
        
        # Estadísticas mensuales para el dashboard
        ahora = datetime.now(timezone.utc)
        inicio_mes_actual = ahora.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        # Mes anterior
        if inicio_mes_actual.month == 1:
            inicio_mes_anterior = inicio_mes_actual.replace(year=inicio_mes_actual.year - 1, month=12)
        else:
            inicio_mes_anterior = inicio_mes_actual.replace(month=inicio_mes_actual.month - 1)
        
        fin_mes_anterior = inicio_mes_actual - timedelta(seconds=1)
        
        # Pacientes del mes actual (desde inicio del mes hasta ahora)
        pacientes_mes_actual = await self.collection.count_documents({
            "fecha_creacion": {"$gte": inicio_mes_actual}
        })
        
        # Pacientes del mes anterior
        pacientes_mes_anterior = await self.collection.count_documents({
            "fecha_creacion": {"$gte": inicio_mes_anterior, "$lte": fin_mes_anterior}
        })
        
        # Calcular cambio porcentual (mes actual vs mes anterior)
        cambio_porcentual = 0.0
        if pacientes_mes_anterior > 0:
            cambio_porcentual = round(((pacientes_mes_actual - pacientes_mes_anterior) / pacientes_mes_anterior) * 100, 2)
        elif pacientes_mes_actual > 0:
            cambio_porcentual = 100.0
        
        return {
            "general": stats_general[0] if stats_general else {
                "total_pacientes": 0,
                "promedio_edad": 0,
                "edad_minima": 0,
                "edad_maxima": 0
            },
            "por_sexo": stats_sexo,
            "por_entidad": stats_entidad,
            "por_tipo_atencion": stats_atencion,
            "casos": stats_casos,
            "mensuales": {
                "pacientes_mes_actual": pacientes_mes_actual,
                "pacientes_mes_anterior": pacientes_mes_anterior,
                "cambio_porcentual": cambio_porcentual
            }
        }

    async def get_entidades_list(self) -> List[str]:
        """Obtener lista de entidades únicas en el sistema"""
        entidades = await self.collection.distinct("entidad_info.nombre")
        return sorted(entidades)

    async def add_caso_to_paciente(self, paciente_id: str, id_caso: str) -> bool:
        """Agregar un ID de caso a un paciente"""
        result = await self.collection.update_one(
            {"paciente_code": paciente_id},
            {"$addToSet": {"id_casos": id_caso}}
        )
        return result.modified_count > 0

    async def remove_caso_from_paciente(self, paciente_id: str, id_caso: str) -> bool:
        """Remover un ID de caso de un paciente"""
        result = await self.collection.update_one(
            {"paciente_code": paciente_id},
            {"$pull": {"id_casos": id_caso}}
        )
        return result.modified_count > 0

    async def count_total(self) -> int:
        """Contar el total de pacientes"""
        return await self.collection.count_documents({})

    async def exists(self, paciente_id: str) -> bool:
        """Verificar si existe un paciente"""
        count = await self.collection.count_documents({"paciente_code": paciente_id})
        return count > 0