"""Servicio para casos de aprobación"""

from typing import List, Optional
from datetime import datetime
from app.modules.aprobacion.models.caso_aprobacion import CasoAprobacion, EstadoAprobacionEnum, AprobacionInfo
from app.modules.aprobacion.schemas.caso_aprobacion import (
    CasoAprobacionCreate,
    CasoAprobacionUpdate,
    CasoAprobacionResponse,
    CasoAprobacionSearch,
    CasoAprobacionStats
)
from app.modules.aprobacion.repositories.caso_aprobacion_repository import CasoAprobacionRepository
from app.modules.casos.repositories.caso_repository import CasoRepository
from app.core.exceptions import NotFoundError, ConflictError


class CasoAprobacionService:
    def __init__(self, repository: CasoAprobacionRepository, caso_repository: CasoRepository):
        self.repository = repository
        self.caso_repository = caso_repository

    def _map(self, c: CasoAprobacion) -> CasoAprobacionResponse:
        # Obtener el _id de MongoDB y convertirlo a string para el campo id de respuesta
        doc_id = str(getattr(c, '_id', ''))
        
        data = {
            "id": doc_id,
            "caso_original": c.caso_original,
            "estado_aprobacion": c.estado_aprobacion,
            "pruebas_complementarias": [p.model_dump() if hasattr(p, 'model_dump') else p for p in c.pruebas_complementarias],
            "aprobacion_info": c.aprobacion_info.model_dump() if c.aprobacion_info else None,
            "fecha_creacion": c.fecha_creacion,
            "fecha_actualizacion": c.fecha_actualizacion,
        }
        return CasoAprobacionResponse.model_validate(data)

    async def create_caso_aprobacion(self, caso_data: CasoAprobacionCreate, usuario_id: str) -> CasoAprobacionResponse:
        caso_original = await self.caso_repository.get_by_codigo(caso_data.caso_original)
        if not caso_original: raise NotFoundError(f"Caso {caso_data.caso_original} no encontrado")
        existente = await self.repository.find_by_caso_original(caso_data.caso_original)
        if existente: raise ConflictError(f"Ya existe un caso de aprobación para el caso {caso_data.caso_original}")
        aprobacion_info = AprobacionInfo(solicitado_por=usuario_id, motivo=caso_data.motivo)
        nuevo = CasoAprobacion(
            caso_original=caso_data.caso_original,
            estado_aprobacion=EstadoAprobacionEnum.SOLICITUD_HECHA,
            pruebas_complementarias=caso_data.pruebas_complementarias,
            aprobacion_info=aprobacion_info,
            creado_por=usuario_id
        )
        creado = await self.repository.create(nuevo)
        return self._map(creado)

    async def get_caso_by_id(self, caso_id: str) -> Optional[CasoAprobacionResponse]:
        c = await self.repository.get(caso_id)
        return self._map(c) if c else None

    async def search_casos(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacionResponse]:
        cs = await self.repository.search(search_params, skip, limit)
        return [self._map(c) for c in cs]

    async def count_casos(self, search_params: CasoAprobacionSearch) -> int:
        return await self.repository.count(search_params)

    async def get_casos_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacionResponse]:
        cs = await self.repository.get_by_estado(estado, limit)
        return [self._map(c) for c in cs]

    async def gestionar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.PENDIENTE_APROBACION, usuario_id, comentarios)
        return await self.get_caso_by_id(caso_id) if ok else None

    async def aprobar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.APROBADO, usuario_id, comentarios)
        return await self.get_caso_by_id(caso_id) if ok else None

    async def rechazar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.RECHAZADO, usuario_id, comentarios)
        return await self.get_caso_by_id(caso_id) if ok else None

    async def update_caso(self, caso_id: str, caso_data: CasoAprobacionUpdate, usuario_id: str) -> Optional[CasoAprobacionResponse]:
        caso_data.fecha_actualizacion = datetime.utcnow()
        updated = await self.repository.update(caso_id, caso_data)
        return self._map(updated) if updated else None

    async def update_pruebas_complementarias(self, caso_id: str, pruebas_complementarias: list, usuario_id: str) -> Optional[CasoAprobacionResponse]:
        # Verificar que el caso existe y está en estado correcto para edición
        caso = await self.repository.get(caso_id)
        if not caso:
            return None
        
        # Solo permitir edición si está en estado "solicitud_hecha"
        if caso.estado_aprobacion != EstadoAprobacionEnum.SOLICITUD_HECHA:
            raise ValueError("Solo se pueden editar las pruebas cuando el caso está en estado 'solicitud_hecha'")
        
        # Actualizar las pruebas complementarias
        updated = await self.repository.update_pruebas_complementarias(caso_id, pruebas_complementarias)
        return self._map(updated) if updated else None

    async def update_pruebas_complementarias_by_caso_original(self, caso_original: str, pruebas_complementarias: list, usuario_id: str) -> Optional[CasoAprobacionResponse]:
        # Buscar el caso por caso_original y obtener tanto el documento como el objeto
        caso_doc, caso = await self.repository.find_by_caso_original_with_id(caso_original)
        if not caso or not caso_doc:
            return None
        
        # Solo permitir edición si está en estado "solicitud_hecha"
        if caso.estado_aprobacion != EstadoAprobacionEnum.SOLICITUD_HECHA:
            raise ValueError("Solo se pueden editar las pruebas cuando el caso está en estado 'solicitud_hecha'")
        
        # Actualizar las pruebas complementarias usando el _id del documento
        case_id = str(caso_doc['_id'])
        updated = await self.repository.update_pruebas_complementarias(case_id, pruebas_complementarias)
        return self._map(updated) if updated else None

    async def delete_caso(self, caso_id: str) -> bool:
        return await self.repository.delete(caso_id)

    async def get_estadisticas(self) -> CasoAprobacionStats:
        raw = await self.repository.get_stats()
        return CasoAprobacionStats(
            total_casos=raw.get("total_casos", 0),
            casos_solicitud_hecha=raw.get("casos_solicitud_hecha", 0),
            casos_pendientes_aprobacion=raw.get("casos_pendientes_aprobacion", 0),
            casos_aprobados=raw.get("casos_aprobados", 0),
            casos_rechazados=raw.get("casos_rechazados", 0)
        )
