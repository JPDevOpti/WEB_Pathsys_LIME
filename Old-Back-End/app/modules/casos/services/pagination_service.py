"""Servicio de paginación cursor-based para optimizar consultas de grandes volúmenes."""

from typing import List, Dict, Any, Optional, Tuple
from datetime import datetime
from bson import ObjectId
from motor.motor_asyncio import AsyncIOMotorCollection
import logging

logger = logging.getLogger(__name__)


class PaginationService:
    """Servicio de paginación cursor-based para consultas eficientes."""
    
    def __init__(self, collection: AsyncIOMotorCollection):
        self.collection = collection
    
    async def paginate_casos(
        self,
        cursor: Optional[str] = None,
        limit: int = 100,
        sort_field: str = "fecha_creacion",
        sort_direction: int = -1,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Paginación cursor-based para casos.
        
        Args:
            cursor: Cursor de paginación (ObjectId como string)
            limit: Número máximo de resultados
            sort_field: Campo por el cual ordenar
            sort_direction: Dirección del ordenamiento (1: asc, -1: desc)
            filters: Filtros adicionales para la consulta
        
        Returns:
            Dict con resultados, next_cursor y has_more
        """
        try:
            # Construir query base
            query = filters.copy() if filters else {}
            
            # Agregar filtro de cursor si existe
            if cursor:
                try:
                    cursor_id = ObjectId(cursor)
                    if sort_direction == -1:
                        query["_id"] = {"$lt": cursor_id}
                    else:
                        query["_id"] = {"$gt": cursor_id}
                except Exception:
                    # Si el cursor no es válido, ignorarlo
                    pass
            
            # Ejecutar consulta con límite + 1 para determinar si hay más resultados
            cursor_obj = self.collection.find(query).sort(sort_field, sort_direction).limit(limit + 1)
            results = await cursor_obj.to_list(length=limit + 1)
            
            # Determinar si hay más resultados
            has_more = len(results) > limit
            if has_more:
                results = results[:limit]  # Remover el resultado extra
            
            # Obtener el cursor para la siguiente página
            next_cursor = None
            if has_more and results:
                next_cursor = str(results[-1]["_id"])
            
            return {
                "results": results,
                "next_cursor": next_cursor,
                "has_more": has_more,
                "count": len(results)
            }
            
        except Exception as e:
            logger.error(f"Error en paginación cursor-based: {e}")
            return {
                "results": [],
                "next_cursor": None,
                "has_more": False,
                "count": 0,
                "error": str(e)
            }
    
    async def paginate_casos_by_estado(
        self,
        estado: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Paginación específica para casos por estado."""
        filters = {"estado": estado}
        return await self.paginate_casos(
            cursor=cursor,
            limit=limit,
            sort_field="fecha_creacion",
            sort_direction=-1,
            filters=filters
        )
    
    async def paginate_casos_by_patologo(
        self,
        patologo_codigo: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Paginación específica para casos por patólogo."""
        filters = {"patologo_asignado.codigo": patologo_codigo}
        return await self.paginate_casos(
            cursor=cursor,
            limit=limit,
            sort_field="fecha_creacion",
            sort_direction=-1,
            filters=filters
        )
    
    async def paginate_casos_by_entidad(
        self,
        entidad_id: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Paginación específica para casos por entidad."""
        filters = {"paciente.entidad_info.id": entidad_id}
        return await self.paginate_casos(
            cursor=cursor,
            limit=limit,
            sort_field="fecha_creacion",
            sort_direction=-1,
            filters=filters
        )
    
    async def paginate_search_results(
        self,
        search_params: Dict[str, Any],
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Paginación para resultados de búsqueda."""
        # Construir filtros de búsqueda
        filters = self._build_search_filters(search_params)
        
        return await self.paginate_casos(
            cursor=cursor,
            limit=limit,
            sort_field="fecha_creacion",
            sort_direction=-1,
            filters=filters
        )
    
    def _build_search_filters(self, search_params: Dict[str, Any]) -> Dict[str, Any]:
        """Construir filtros de búsqueda a partir de parámetros."""
        filters = {}
        
        # Filtros básicos
        if search_params.get("estado"):
            filters["estado"] = search_params["estado"]
        
        if search_params.get("prioridad"):
            filters["prioridad"] = search_params["prioridad"]
        
        if search_params.get("patologo_codigo"):
            filters["patologo_asignado.codigo"] = search_params["patologo_codigo"]
        
        # Filtros de fecha
        if search_params.get("fecha_desde") or search_params.get("fecha_hasta"):
            fecha_query = {}
            if search_params.get("fecha_desde"):
                fecha_query["$gte"] = search_params["fecha_desde"]
            if search_params.get("fecha_hasta"):
                fecha_query["$lte"] = search_params["fecha_hasta"]
            filters["fecha_creacion"] = fecha_query
        
        # Filtros especiales
        if search_params.get("solo_vencidos"):
            from datetime import datetime, timedelta
            fecha_limite = datetime.utcnow() - timedelta(days=15)
            filters.update({
                "fecha_creacion": {"$lt": fecha_limite},
                "estado": {"$nin": ["Completado"]}
            })
        
        if search_params.get("solo_sin_patologo"):
            filters["$or"] = [
                {"patologo_asignado": {"$exists": False}},
                {"patologo_asignado": None}
            ]
        
        # Búsqueda de texto
        if search_params.get("query"):
            filters["$text"] = {"$search": search_params["query"]}
        
        return filters
    
    async def get_total_count(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """Obtener el conteo total de resultados para una consulta."""
        try:
            query = filters.copy() if filters else {}
            return await self.collection.count_documents(query)
        except Exception as e:
            logger.error(f"Error obteniendo conteo total: {e}")
            return 0
    
    async def paginate_with_count(
        self,
        cursor: Optional[str] = None,
        limit: int = 100,
        sort_field: str = "fecha_creacion",
        sort_direction: int = -1,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Paginación con conteo total incluido."""
        # Ejecutar paginación y conteo en paralelo
        pagination_task = self.paginate_casos(
            cursor=cursor,
            limit=limit,
            sort_field=sort_field,
            sort_direction=sort_direction,
            filters=filters
        )
        count_task = self.get_total_count(filters)
        
        pagination_result, total_count = await asyncio.gather(
            pagination_task, count_task
        )
        
        pagination_result["total_count"] = total_count
        return pagination_result


# Funciones de utilidad para integración
async def create_pagination_response(
    pagination_result: Dict[str, Any],
    base_url: str,
    endpoint: str,
    params: Dict[str, Any]
) -> Dict[str, Any]:
    """Crear respuesta de paginación con enlaces."""
    response = {
        "data": pagination_result.get("results", []),
        "pagination": {
            "count": pagination_result.get("count", 0),
            "total_count": pagination_result.get("total_count", 0),
            "has_more": pagination_result.get("has_more", False),
            "next_cursor": pagination_result.get("next_cursor")
        }
    }
    
    # Agregar enlaces de navegación si hay más resultados
    if pagination_result.get("has_more"):
        next_params = params.copy()
        next_params["cursor"] = pagination_result.get("next_cursor")
        next_url = f"{base_url}{endpoint}?" + "&".join([f"{k}={v}" for k, v in next_params.items()])
        response["pagination"]["next_url"] = next_url
    
    return response
