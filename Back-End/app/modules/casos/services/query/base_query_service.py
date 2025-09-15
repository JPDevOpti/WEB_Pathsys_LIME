from typing import Dict, Any, Optional
from app.modules.casos.services.cache_service import CacheService


class BaseQueryService:
    """Servicio base con utilidades comunes para consultas"""
    
    def __init__(self, cache_service: CacheService):
        self.cache_service = cache_service
    
    def _normalize_filters(self, filtros: Optional[Dict[str, Any]]) -> Dict[str, Any]:
        """Normaliza y valida filtros de entrada"""
        if not filtros:
            return {}
        
        normalized = {}
        
        # Mapear alias de frontend a campos de BD
        field_mapping = {
            "estado": "estado",
            "estados": "estados",
            "fecha_desde": "fecha_desde",
            "fecha_hasta": "fecha_hasta",
            "entidad": "entidad_id",
            "patologo": "patologo_codigo",
            "prioridad": "prioridad",
            "busqueda": "texto_busqueda",
            "medico": "medico_solicitante",
            "servicio": "servicio"
        }
        
        for key, value in filtros.items():
            if key in field_mapping and value is not None:
                normalized[field_mapping[key]] = value
        
        return normalized
    
    def _get_cache_key(self, operation: str, **kwargs) -> str:
        """Genera clave de caché para operación"""
        key_parts = [operation]
        for k, v in sorted(kwargs.items()):
            if v is not None:
                key_parts.append(f"{k}:{v}")
        return ":".join(key_parts)
    
    def _apply_defaults(self, filtros: Dict[str, Any]) -> Dict[str, Any]:
        """Aplica valores por defecto a filtros"""
        defaults = {
            "estado": None,
            "fecha_desde": None,
            "fecha_hasta": None,
            "entidad_id": None,
            "patologo_codigo": None,
            "prioridad": None,
            "texto_busqueda": None
        }
        
        for key, default_value in defaults.items():
            if key not in filtros:
                filtros[key] = default_value
        
        return filtros
    
    def _validate_pagination(self, pagina: int, tamaño: int) -> tuple[int, int]:
        """Valida y ajusta parámetros de paginación"""
        pagina = max(1, pagina)
        tamaño = max(1, min(100, tamaño))  # Límite máximo de 100
        return pagina, tamaño