"""Servicio para casos de aprobación"""

from typing import List, Optional, Dict, Any
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

    async def create_caso_aprobacion(self, caso_data: CasoAprobacionCreate, usuario_id: str) -> CasoAprobacionResponse:
        """Crear un nuevo caso de aprobación"""
        
        # Verificar que el caso original existe
        caso_original = await self.caso_repository.get_by_codigo(caso_data.caso_original)
        if not caso_original:
            raise NotFoundError(f"Caso {caso_data.caso_original} no encontrado")
        
        # Verificar si ya existe un caso de aprobación para este caso
        caso_existente = await self.repository.find_by_caso_original(caso_data.caso_original)
        if caso_existente and caso_existente.is_active:
            raise ConflictError(f"Ya existe un caso de aprobación activo para el caso {caso_data.caso_original}")
        
        # Crear la información de aprobación
        aprobacion_info = AprobacionInfo(
            solicitado_por=caso_data.solicitado_por,
            motivo=caso_data.motivo
        )
        
        # Crear el caso de aprobación con toda la información del caso original
        # Convertir todos los objetos Pydantic a diccionarios para evitar problemas de validación
        paciente_data = None
        if caso_original.paciente:
            if hasattr(caso_original.paciente, 'model_dump'):
                paciente_data = caso_original.paciente.model_dump()
            else:
                paciente_data = caso_original.paciente
                
        medico_data = None
        if caso_original.medico_solicitante:
            if hasattr(caso_original.medico_solicitante, 'model_dump'):
                medico_data = caso_original.medico_solicitante.model_dump()
            else:
                medico_data = caso_original.medico_solicitante
                
        muestras_data = []
        if caso_original.muestras:
            for muestra in caso_original.muestras:
                if hasattr(muestra, 'model_dump'):
                    muestras_data.append(muestra.model_dump())
                else:
                    muestras_data.append(muestra)
                    
        patologo_data = None
        if caso_original.patologo_asignado:
            if hasattr(caso_original.patologo_asignado, 'model_dump'):
                patologo_data = caso_original.patologo_asignado.model_dump()
            else:
                patologo_data = caso_original.patologo_asignado
                
        resultado_data = None
        if caso_original.resultado:
            if hasattr(caso_original.resultado, 'model_dump'):
                resultado_dict = caso_original.resultado.model_dump()
                # Mapear los diagnósticos al formato esperado por el módulo de aprobación
                if resultado_dict.get('diagnostico_cie10'):
                    cie10 = resultado_dict['diagnostico_cie10']
                    print(f"🔄 DEBUG: Mapeando CIE10 - Original: {cie10}")
                    resultado_dict['diagnostico_cie10'] = {
                        'codigo': cie10.get('codigo', ''),
                        'descripcion': cie10.get('nombre', '')  # 'nombre' en casos -> 'descripcion' en aprobación
                    }
                    print(f"✅ DEBUG: CIE10 mapeado: {resultado_dict['diagnostico_cie10']}")
                
                if resultado_dict.get('diagnostico_cieo'):
                    cieo = resultado_dict['diagnostico_cieo']
                    print(f"🔄 DEBUG: Mapeando CIEO - Original: {cieo}")
                    resultado_dict['diagnostico_cieo'] = {
                        'codigo': cieo.get('codigo', ''),
                        'descripcion': cieo.get('nombre', '')  # 'nombre' en casos -> 'descripcion' en aprobación
                    }
                    print(f"✅ DEBUG: CIEO mapeado: {resultado_dict['diagnostico_cieo']}")
                    
                resultado_data = resultado_dict
            else:
                resultado_data = caso_original.resultado

        # Generar código de aprobación con prefijo A-
        caso_aprobacion_code = f"A-{caso_data.caso_original}"

        nuevo_caso = CasoAprobacion(
            caso_original=caso_data.caso_original,
            caso_aprobacion=caso_aprobacion_code,
            paciente=paciente_data,
            medico_solicitante=medico_data,
            servicio=caso_original.servicio,
            muestras=muestras_data,
            estado_caso_original=caso_original.estado,
            patologo_asignado=patologo_data,
            resultado=resultado_data,
            pruebas_complementarias=caso_data.pruebas_complementarias,
            aprobacion_info=aprobacion_info,
            creado_por=usuario_id
        )
        
        caso_creado = await self.repository.create(nuevo_caso)
        return CasoAprobacionResponse.model_validate(caso_creado)

    async def get_caso_by_id(self, caso_id: str) -> Optional[CasoAprobacionResponse]:
        """Obtener caso de aprobación por ID"""
        caso = await self.repository.get(caso_id)
        if caso:
            return CasoAprobacionResponse.model_validate(caso)
        return None

    async def get_caso_by_codigo(self, caso_aprobacion: str) -> Optional[CasoAprobacionResponse]:
        """Obtener caso de aprobación por código de aprobación"""
        caso = await self.repository.find_by_caso_aprobacion(caso_aprobacion)
        if caso:
            return CasoAprobacionResponse.model_validate(caso)
        return None

    async def search_casos_active_only(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacionResponse]:
        """Buscar casos de aprobación activos"""
        casos = await self.repository.search_active_only(search_params, skip, limit)
        return [CasoAprobacionResponse.model_validate(caso) for caso in casos]

    async def search_casos_all(self, search_params: CasoAprobacionSearch, skip: int = 0, limit: int = 50) -> List[CasoAprobacionResponse]:
        """Buscar todos los casos de aprobación (incluye inactivos)"""
        casos = await self.repository.search_all(search_params, skip, limit)
        return [CasoAprobacionResponse.model_validate(caso) for caso in casos]

    async def count_casos_active_only(self, search_params: CasoAprobacionSearch) -> int:
        """Contar casos de aprobación activos"""
        return await self.repository.count_active_only(search_params)

    async def count_casos_all(self, search_params: CasoAprobacionSearch) -> int:
        """Contar todos los casos de aprobación"""
        return await self.repository.count_all(search_params)

    async def get_casos_by_estado(self, estado: EstadoAprobacionEnum, limit: int = 50) -> List[CasoAprobacionResponse]:
        """Obtener casos por estado de aprobación"""
        casos = await self.repository.get_by_estado(estado, limit)
        return [CasoAprobacionResponse.model_validate(caso) for caso in casos]

    async def get_casos_pendientes_usuario(self, usuario_id: str, limit: int = 50) -> List[CasoAprobacionResponse]:
        """Obtener casos pendientes para un usuario"""
        casos = await self.repository.get_pendientes_por_usuario(usuario_id, limit)
        return [CasoAprobacionResponse.model_validate(caso) for caso in casos]

    async def gestionar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        """Cambiar estado a gestionando"""
        success = await self.repository.update_estado(
            caso_id, 
            EstadoAprobacionEnum.GESTIONANDO, 
            usuario_id, 
            comentarios
        )
        
        if success:
            return await self.get_caso_by_id(caso_id)
        return None

    async def aprobar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        """Aprobar un caso"""
        success = await self.repository.update_estado(
            caso_id, 
            EstadoAprobacionEnum.APROBADO, 
            usuario_id, 
            comentarios
        )
        
        if success:
            return await self.get_caso_by_id(caso_id)
        return None

    async def rechazar_caso(self, caso_id: str, usuario_id: str, comentarios: Optional[str] = None) -> Optional[CasoAprobacionResponse]:
        """Rechazar un caso"""
        success = await self.repository.update_estado(
            caso_id, 
            EstadoAprobacionEnum.RECHAZADO, 
            usuario_id, 
            comentarios
        )
        
        if success:
            return await self.get_caso_by_id(caso_id)
        return None

    async def update_caso(self, caso_id: str, caso_data: CasoAprobacionUpdate, usuario_id: str) -> Optional[CasoAprobacionResponse]:
        """Actualizar un caso de aprobación"""
        caso_data.actualizado_por = usuario_id
        caso_data.fecha_actualizacion = datetime.utcnow()
        
        caso_actualizado = await self.repository.update(caso_id, caso_data)
        if caso_actualizado:
            return CasoAprobacionResponse.model_validate(caso_actualizado)
        return None

    async def soft_delete_caso(self, caso_id: str, usuario_id: str) -> bool:
        """Eliminación suave de un caso de aprobación"""
        update_data = CasoAprobacionUpdate(
            is_active=False,
            actualizado_por=usuario_id,
            fecha_actualizacion=datetime.utcnow()
        )
        
        caso_actualizado = await self.repository.update(caso_id, update_data)
        return caso_actualizado is not None

    async def get_estadisticas(self) -> CasoAprobacionStats:
        """Obtener estadísticas de casos de aprobación"""
        stats_data = await self.repository.get_stats()
        
        # Crear estadísticas básicas
        stats = CasoAprobacionStats(
            total_casos=stats_data.get("total_casos", 0),
            casos_pendientes=stats_data.get("casos_pendientes", 0),
            casos_gestionando=stats_data.get("casos_gestionando", 0),
            casos_aprobados=stats_data.get("casos_aprobados", 0),
            casos_rechazados=stats_data.get("casos_rechazados", 0)
        )
        
        return stats
