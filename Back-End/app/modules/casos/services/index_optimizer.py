"""Servicio para optimizar índices de MongoDB en el módulo de casos."""

from typing import List, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)


class IndexOptimizer:
    """Optimizador de índices para mejorar el rendimiento de consultas."""
    
    def __init__(self, database: AsyncIOMotorDatabase):
        self.database = database
        self.collection = database.casos
    
    async def create_optimized_indexes(self) -> Dict[str, Any]:
        """Crear todos los índices optimizados para el módulo de casos."""
        results = {}
        
        try:
            # Índices básicos únicos
            results.update(await self._create_basic_indexes())
            
            # Índices compuestos para consultas frecuentes
            results.update(await self._create_compound_indexes())
            
            # Índices para estadísticas y reportes
            results.update(await self._create_analytics_indexes())
            
            # Índices para búsquedas complejas
            results.update(await self._create_search_indexes())
            
            # Índices para paginación eficiente
            results.update(await self._create_pagination_indexes())
            
            logger.info("Índices optimizados creados exitosamente")
            return results
            
        except Exception as e:
            logger.error(f"Error creando índices: {e}")
            return {"error": str(e)}
    
    async def _create_basic_indexes(self) -> Dict[str, Any]:
        """Crear índices básicos únicos."""
        results = {}
        
        # Índice único para caso_code
        try:
            await self.collection.create_index("caso_code", unique=True, background=True)
            results["caso_code_unique"] = "Creado"
        except Exception as e:
            results["caso_code_unique"] = f"Error: {e}"
        
        # Índice para patologo_asignado.codigo
        try:
            await self.collection.create_index("patologo_asignado.codigo", background=True)
            results["patologo_codigo"] = "Creado"
        except Exception as e:
            results["patologo_codigo"] = f"Error: {e}"
        
        return results
    
    async def _create_compound_indexes(self) -> Dict[str, Any]:
        """Crear índices compuestos para consultas frecuentes."""
        results = {}
        
        # Índice para consultas por estado y fecha
        try:
            await self.collection.create_index(
                [("estado", 1), ("fecha_creacion", -1)],
                background=True,
                name="estado_fecha_creacion"
            )
            results["estado_fecha_creacion"] = "Creado"
        except Exception as e:
            results["estado_fecha_creacion"] = f"Error: {e}"
        
        # Índice para consultas por patólogo y estado
        try:
            await self.collection.create_index(
                [("patologo_asignado.codigo", 1), ("estado", 1), ("fecha_creacion", -1)],
                background=True,
                name="patologo_estado_fecha"
            )
            results["patologo_estado_fecha"] = "Creado"
        except Exception as e:
            results["patologo_estado_fecha"] = f"Error: {e}"
        
        # Índice para consultas por entidad y fecha
        try:
            await self.collection.create_index(
                [("paciente.entidad_info.id", 1), ("fecha_creacion", -1)],
                background=True,
                name="entidad_fecha_creacion"
            )
            results["entidad_fecha_creacion"] = "Creado"
        except Exception as e:
            results["entidad_fecha_creacion"] = f"Error: {e}"
        
        # Índice para consultas por prioridad y estado
        try:
            await self.collection.create_index(
                [("prioridad", 1), ("estado", 1), ("fecha_creacion", -1)],
                background=True,
                name="prioridad_estado_fecha"
            )
            results["prioridad_estado_fecha"] = "Creado"
        except Exception as e:
            results["prioridad_estado_fecha"] = f"Error: {e}"
        
        return results
    
    async def _create_analytics_indexes(self) -> Dict[str, Any]:
        """Crear índices para estadísticas y reportes."""
        results = {}
        
        # Índice para estadísticas mensuales
        try:
            await self.collection.create_index(
                [("fecha_creacion", 1), ("estado", 1)],
                background=True,
                name="fecha_estado_analytics"
            )
            results["fecha_estado_analytics"] = "Creado"
        except Exception as e:
            results["fecha_estado_analytics"] = f"Error: {e}"
        
        # Índice para estadísticas de oportunidad
        try:
            await self.collection.create_index(
                [("fecha_entrega", 1), ("oportunidad", 1), ("estado", 1)],
                background=True,
                name="oportunidad_analytics"
            )
            results["oportunidad_analytics"] = "Creado"
        except Exception as e:
            results["oportunidad_analytics"] = f"Error: {e}"
        
        # Índice para estadísticas de muestras
        try:
            await self.collection.create_index(
                [("fecha_creacion", 1), ("muestras.region_cuerpo", 1)],
                background=True,
                name="muestras_analytics"
            )
            results["muestras_analytics"] = "Creado"
        except Exception as e:
            results["muestras_analytics"] = f"Error: {e}"
        
        # Índice para estadísticas de pruebas
        try:
            await self.collection.create_index(
                [("fecha_creacion", 1), ("muestras.pruebas.id", 1)],
                background=True,
                name="pruebas_analytics"
            )
            results["pruebas_analytics"] = "Creado"
        except Exception as e:
            results["pruebas_analytics"] = f"Error: {e}"
        
        return results
    
    async def _create_search_indexes(self) -> Dict[str, Any]:
        """Crear índices para búsquedas complejas."""
        results = {}
        
        # Índice de texto para búsquedas generales
        try:
            await self.collection.create_index(
                [
                    ("caso_code", "text"),
                    ("paciente.nombre", "text"),
                    ("paciente.paciente_code", "text"),
                    ("medico_solicitante", "text")
                ],
                background=True,
                name="text_search",
                default_language="spanish"
            )
            results["text_search"] = "Creado"
        except Exception as e:
            results["text_search"] = f"Error: {e}"
        
        # Índice para búsquedas por paciente
        try:
            await self.collection.create_index(
                [("paciente.paciente_code", 1), ("fecha_creacion", -1)],
                background=True,
                name="paciente_fecha"
            )
            results["paciente_fecha"] = "Creado"
        except Exception as e:
            results["paciente_fecha"] = f"Error: {e}"
        
        # Índice para casos vencidos
        try:
            await self.collection.create_index(
                [("fecha_creacion", 1), ("estado", 1)],
                background=True,
                name="casos_vencidos",
                partialFilterExpression={"estado": {"$nin": ["Completado"]}}
            )
            results["casos_vencidos"] = "Creado"
        except Exception as e:
            results["casos_vencidos"] = f"Error: {e}"
        
        # Índice para casos sin patólogo
        try:
            await self.collection.create_index(
                [("patologo_asignado", 1), ("fecha_creacion", -1)],
                background=True,
                name="sin_patologo",
                partialFilterExpression={"patologo_asignado": None}
            )
            results["sin_patologo"] = "Creado"
        except Exception as e:
            results["sin_patologo"] = f"Error: {e}"
        
        return results
    
    async def _create_pagination_indexes(self) -> Dict[str, Any]:
        """Crear índices para paginación eficiente."""
        results = {}
        
        # Índice para paginación por fecha de creación
        try:
            await self.collection.create_index(
                [("fecha_creacion", -1), ("_id", 1)],
                background=True,
                name="pagination_fecha_id"
            )
            results["pagination_fecha_id"] = "Creado"
        except Exception as e:
            results["pagination_fecha_id"] = f"Error: {e}"
        
        # Índice para paginación por estado y fecha
        try:
            await self.collection.create_index(
                [("estado", 1), ("fecha_creacion", -1), ("_id", 1)],
                background=True,
                name="pagination_estado_fecha_id"
            )
            results["pagination_estado_fecha_id"] = "Creado"
        except Exception as e:
            results["pagination_estado_fecha_id"] = f"Error: {e}"
        
        return results
    
    async def get_index_stats(self) -> Dict[str, Any]:
        """Obtener estadísticas de los índices."""
        try:
            stats = await self.collection.index_stats()
            return {
                "total_indexes": len(stats),
                "indexes": [
                    {
                        "name": idx.get("name", "unnamed"),
                        "size": idx.get("size", 0),
                        "usage": idx.get("usage", {})
                    }
                    for idx in stats
                ]
            }
        except Exception as e:
            return {"error": str(e)}
    
    async def drop_unused_indexes(self) -> Dict[str, Any]:
        """Eliminar índices no utilizados."""
        try:
            stats = await self.collection.index_stats()
            unused_indexes = []
            
            for idx in stats:
                usage = idx.get("usage", {})
                if usage.get("accesses", {}).get("ops", 0) == 0:
                    unused_indexes.append(idx.get("name"))
            
            results = {}
            for idx_name in unused_indexes:
                if idx_name not in ["_id_", "caso_code_1"]:  # No eliminar índices críticos
                    try:
                        await self.collection.drop_index(idx_name)
                        results[idx_name] = "Eliminado"
                    except Exception as e:
                        results[idx_name] = f"Error: {e}"
            
            return results
        except Exception as e:
            return {"error": str(e)}
