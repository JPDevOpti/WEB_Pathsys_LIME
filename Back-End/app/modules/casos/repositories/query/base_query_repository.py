from typing import Dict, List, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.modules.casos.schemas.query.pagination import PageRequest, SortField


class BaseQueryRepository:
    """Repositorio base con utilidades comunes para consultas"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.collection = db.casos
    
    def _build_match_stage(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Construye el stage $match basado en filtros"""
        match = {}
        
        if filtros.get("estado"):
            match["estado"] = filtros["estado"]
        
        if filtros.get("estados"):
            match["estado"] = {"$in": filtros["estados"]}
        
        if filtros.get("fecha_desde") or filtros.get("fecha_hasta"):
            fecha_match = {}
            if filtros.get("fecha_desde"):
                fecha_match["$gte"] = filtros["fecha_desde"]
            if filtros.get("fecha_hasta"):
                fecha_match["$lte"] = filtros["fecha_hasta"]
            match["fecha_creacion"] = fecha_match
        
        if filtros.get("entidad_id"):
            match["paciente.entidad_info.id"] = filtros["entidad_id"]
        
        if filtros.get("patologo_codigo"):
            match["patologo_asignado.codigo"] = filtros["patologo_codigo"]
        
        if filtros.get("prioridad"):
            match["prioridad"] = filtros["prioridad"]
        
        if filtros.get("texto_busqueda"):
            match["$text"] = {"$search": filtros["texto_busqueda"]}
        
        return match
    
    def _build_sort_stage(self, ordenar_por: Optional[List[SortField]]) -> List[tuple]:
        """Construye el stage $sort"""
        if not ordenar_por:
            return [("fecha_creacion", -1)]
        
        sort_list = []
        for sort_field in ordenar_por:
            direction = 1 if sort_field.direccion == "asc" else -1
            sort_list.append((sort_field.campo, direction))
        
        return sort_list
    
    def _build_pagination_stage(self, page_request: PageRequest) -> tuple:
        """Construye skip y limit para paginación"""
        skip = (page_request.pagina - 1) * page_request.tamaño
        limit = page_request.tamaño
        return skip, limit
    
    def _build_projection(self, campos: List[str]) -> Dict[str, int]:
        """Construye proyección de campos"""
        projection = {}
        for campo in campos:
            projection[campo] = 1
        return projection
    
    async def _get_total_count(self, match_stage: Dict[str, Any]) -> int:
        """Obtiene el total de documentos que coinciden con el match"""
        return await self.collection.count_documents(match_stage)