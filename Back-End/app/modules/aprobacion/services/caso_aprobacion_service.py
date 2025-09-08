"""Servicio para casos de aprobación"""

from typing import List, Optional
from datetime import datetime
from app.modules.aprobacion.models.caso_aprobacion import CasoAprobacion, EstadoAprobacionEnum, AprobacionInfo, PatologoAsignadoInfo
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
from app.modules.casos.schemas.caso import CasoCreate, MuestraInfo as CasoMuestraInfo, PacienteInfo as CasoPacienteInfo
from app.modules.pruebas.schemas.prueba import PruebasItem
from app.modules.casos.models.caso import PrioridadCasoEnum
from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository


class CasoAprobacionService:
    def __init__(self, repository: CasoAprobacionRepository, caso_repository: CasoRepository):
        self.repository = repository
        self.caso_repository = caso_repository

    def _map(self, c: CasoAprobacion) -> CasoAprobacionResponse:
        data = {
            "id": c.id or str(getattr(c, '_id', '')),
            "caso_original": c.caso_original,
            "estado_aprobacion": c.estado_aprobacion,
            "pruebas_complementarias": [p.model_dump() if hasattr(p, 'model_dump') else p for p in c.pruebas_complementarias],
            "aprobacion_info": c.aprobacion_info.model_dump() if c.aprobacion_info else None,
            "fecha_creacion": c.fecha_creacion,
        }
        return CasoAprobacionResponse.model_validate(data)

    async def create_caso_aprobacion(self, caso_data: CasoAprobacionCreate, usuario_id: str) -> CasoAprobacionResponse:
        caso_original = await self.caso_repository.get_by_codigo(caso_data.caso_original)
        if not caso_original: raise NotFoundError(f"Caso {caso_data.caso_original} no encontrado")
        existente = await self.repository.find_by_caso_original(caso_data.caso_original)
        if existente: raise ConflictError(f"Ya existe un caso de aprobación para el caso {caso_data.caso_original}")
        
        # Obtener información del patólogo del caso original
        patologo_asignado_info = None
        if caso_original.patologo_asignado:
            patologo_asignado_info = PatologoAsignadoInfo(
                codigo=caso_original.patologo_asignado.codigo,
                nombre=caso_original.patologo_asignado.nombre,
                firma=caso_original.patologo_asignado.firma
            )
        
        aprobacion_info = AprobacionInfo(
            motivo=caso_data.motivo,
            patologo_asignado=patologo_asignado_info
        )
        nuevo = CasoAprobacion(
            caso_original=caso_data.caso_original,
            estado_aprobacion=EstadoAprobacionEnum.SOLICITUD_HECHA,
            pruebas_complementarias=caso_data.pruebas_complementarias,
            aprobacion_info=aprobacion_info
        )
        creado = await self.repository.create(nuevo)
        return self._map(creado)

    async def get_caso_by_id(self, caso_id: str) -> Optional[CasoAprobacionResponse]:
        c = await self.repository.get(caso_id)
        return self._map(c) if c else None

    async def search_casos(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacionResponse]:
        casos = await self.repository.search(search_params, skip, limit)
        return [self._map(c) for c in casos]

    async def count_casos(self, search_params: CasoAprobacionSearch) -> int:
        return await self.repository.count(search_params)

    async def get_casos_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacionResponse]:
        casos = await self.repository.get_by_estado(estado, limit)
        return [self._map(c) for c in casos]

    async def gestionar_caso(self, caso_id: str) -> Optional[CasoAprobacionResponse]:
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.PENDIENTE_APROBACION)
        return await self.get_caso_by_id(caso_id) if ok else None

    async def aprobar_caso(self, caso_id: str) -> Optional[dict]:
        # Actualizar fecha de aprobación y estado
        await self.repository.update_fecha_aprobacion(caso_id)
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.APROBADO)
        if not ok:
            return None

        # Crear automáticamente un nuevo caso heredando datos del caso original
        try:
            aprobacion = await self.repository.get(caso_id)
            if not aprobacion:
                aprobacion_resp = await self.get_caso_by_id(caso_id)
                return {"aprobacion": aprobacion_resp, "nuevo_caso": None}

            # Obtener caso original por código
            caso_original = await self.caso_repository.get_by_codigo(aprobacion.caso_original)
            if not caso_original:
                aprobacion_resp = await self.get_caso_by_id(caso_id)
                return {"aprobacion": aprobacion_resp, "nuevo_caso": None}

            # Generar nuevo código de caso
            db = self.caso_repository.database
            consecutivo_repo = ConsecutivoRepository(db)
            ano_actual = datetime.utcnow().year
            nuevo_codigo = await consecutivo_repo.generar_codigo_caso(ano_actual)

            # Preparar muestras y pruebas desde la aprobación
            region = (caso_original.muestras[0].region_cuerpo if getattr(caso_original, 'muestras', None) and len(caso_original.muestras) > 0 else "General")
            pruebas = [
                PruebasItem(id=p.codigo, nombre=p.nombre, cantidad=getattr(p, 'cantidad', 1))
                for p in aprobacion.pruebas_complementarias
            ]

            muestras_nuevo = [
                CasoMuestraInfo(region_cuerpo=region, pruebas=pruebas)
            ]

            # Construir objeto de creación del nuevo caso
            paciente_info: CasoPacienteInfo = CasoPacienteInfo.model_validate(caso_original.paciente.model_dump())
            observaciones_generales = (aprobacion.aprobacion_info.motivo if aprobacion.aprobacion_info else None)

            caso_nuevo = CasoCreate(
                caso_code=nuevo_codigo,
                paciente=paciente_info,
                medico_solicitante=getattr(caso_original, 'medico_solicitante', None),
                servicio=getattr(caso_original, 'servicio', None),
                muestras=muestras_nuevo,
                prioridad=PrioridadCasoEnum.NORMAL,
                observaciones_generales=observaciones_generales
            )

            # Crear el caso
            creado = await self.caso_repository.create(caso_nuevo)

            # Asignar patólogo igual al del caso original si existe
            if getattr(caso_original, 'patologo_asignado', None):
                try:
                    await self.caso_repository.asignar_patologo_por_caso_code(
                        creado.caso_code,
                        {
                            "codigo": caso_original.patologo_asignado.codigo,
                            "nombre": caso_original.patologo_asignado.nombre,
                            "firma": getattr(caso_original.patologo_asignado, 'firma', None)
                        }
                    )
                except Exception:
                    pass
            aprobacion_resp = await self.get_caso_by_id(caso_id)
            return {"aprobacion": aprobacion_resp, "nuevo_caso": creado}
        except Exception:
            # No bloquear la aprobación si la creación del caso falla
            aprobacion_resp = await self.get_caso_by_id(caso_id)
            return {"aprobacion": aprobacion_resp, "nuevo_caso": None}

    async def rechazar_caso(self, caso_id: str) -> Optional[CasoAprobacionResponse]:
        ok = await self.repository.update_estado(caso_id, EstadoAprobacionEnum.RECHAZADO)
        return await self.get_caso_by_id(caso_id) if ok else None

    async def update_caso(self, caso_id: str, caso_data: CasoAprobacionUpdate) -> Optional[CasoAprobacionResponse]:
        updated = await self.repository.update(caso_id, caso_data)
        return await self.get_caso_by_id(caso_id) if updated else None

    async def update_pruebas_complementarias(self, caso_id: str, pruebas_complementarias: list) -> Optional[CasoAprobacionResponse]:
        # Verificar que el caso existe y está en estado correcto para edición
        caso = await self.repository.get(caso_id)
        if not caso:
            return None
        
        # Solo permitir edición si está en estado "solicitud_hecha"
        if caso.estado_aprobacion != EstadoAprobacionEnum.SOLICITUD_HECHA:
            raise ValueError("Solo se pueden editar las pruebas cuando el caso está en estado 'solicitud_hecha'")
        
        # Actualizar las pruebas complementarias
        updated = await self.repository.update_pruebas_complementarias(caso_id, pruebas_complementarias)
        return await self.get_caso_by_id(caso_id) if updated else None

    async def update_pruebas_complementarias_by_caso_original(self, caso_original: str, pruebas_complementarias: list) -> Optional[CasoAprobacionResponse]:
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
        return await self.get_caso_by_id(case_id) if updated else None

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
