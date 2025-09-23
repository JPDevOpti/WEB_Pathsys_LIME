from typing import List
from app.modules.casos.services.query.base_query_service import BaseQueryService
from app.modules.casos.repositories.query.urgent_cases_repository import UrgentCasesRepository
from app.modules.casos.schemas.query.urgent_cases import UrgentCasesRequest, UrgentCasesResponse, UrgentCaseRow


class UrgentCasesService(BaseQueryService):
    """Servicio para casos urgentes con caché"""
    
    def __init__(self, repository: UrgentCasesRepository, cache_service):
        super().__init__(cache_service)
        self.repository = repository
    
    async def get_urgent_cases(self, request: UrgentCasesRequest) -> UrgentCasesResponse:
        """Obtiene casos urgentes con caché TTL corto"""
        # Generar clave de caché
        cache_key = self._get_cache_key(
            "urgent_cases",
            patologo_codigo=request.patologo_codigo,
            estado=request.estado,
            limite=request.limite
        )
        
        # Intentar obtener del caché
        cached_result = await self.cache_service.get(cache_key)
        if cached_result:
            return UrgentCasesResponse(**cached_result)
        
        # Obtener datos del repositorio
        casos = await self.repository.get_urgent_cases(request)
        
        # Crear respuesta
        response = UrgentCasesResponse(
            casos=casos,
            total=len(casos),
            limite_aplicado=request.limite
        )
        
        # Guardar en caché (TTL corto para datos operativos)
        await self.cache_service.set(cache_key, response.dict(), ttl=300)  # 5 minutos
        
        return response