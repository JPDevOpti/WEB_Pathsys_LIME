from typing import Dict, Any, Optional
from datetime import datetime
from app.modules.casos.repositories.management.update_repository import UpdateCaseRepository
from app.modules.casos.schemas.management.update import (
    UpdateCaseRequest, 
    UpdateCaseResponse, 
    UpdatedCaseInfo
)
from app.modules.casos.services.cache_service import cache_service
from app.core.exceptions import NotFoundError, BadRequestError


class UpdateCaseService:
    """Servicio para actualización de casos con validaciones y caché"""
    
    def __init__(self, update_repo: UpdateCaseRepository):
        self.update_repo = update_repo
        self.cache_service = cache_service
    
    async def update_case(self, caso_code: str, update_data: UpdateCaseRequest, usuario_id: str) -> UpdateCaseResponse:
        """Actualizar un caso con validaciones completas"""
        try:
            # Validar que el caso existe
            if not await self.update_repo.validate_case_exists(caso_code):
                raise NotFoundError(f"Caso {caso_code} no encontrado")
            
            # Validar datos de actualización
            await self._validate_update_request(update_data)
            
            # Actualizar el caso
            updated_case = await self.update_repo.update_case(caso_code, update_data)
            
            if not updated_case:
                raise BadRequestError(f"No se pudo actualizar el caso {caso_code}")
            
            # Invalidar caché relacionado
            await self._invalidate_related_caches(caso_code)
            
            # Construir respuesta con todos los campos
            case_info = UpdatedCaseInfo(
                id=updated_case['_id'],
                caso_code=updated_case['caso_code'],
                paciente=updated_case['paciente'],
                medico_solicitante=updated_case.get('medico_solicitante'),
                servicio=updated_case.get('servicio'),
                muestras=updated_case['muestras'],
                estado=updated_case['estado'],
                prioridad=updated_case['prioridad'],
                observaciones_generales=updated_case.get('observaciones_generales'),
                entregado_a=updated_case.get('entregado_a'),
                oportunidad=updated_case.get('oportunidad'),
                patologo_asignado=updated_case.get('patologo_asignado'),
                resultado=updated_case.get('resultado'),
                notas_adicionales=updated_case.get('notas_adicionales', []),
                fecha_creacion=updated_case['fecha_creacion'],
                fecha_actualizacion=updated_case['fecha_actualizacion'],
                fecha_firma=updated_case.get('fecha_firma'),
                fecha_entrega=updated_case.get('fecha_entrega'),
                ingresado_por=updated_case.get('ingresado_por'),
                actualizado_por=updated_case.get('actualizado_por')
            )
            
            return UpdateCaseResponse(
                success=True,
                message=f"Caso {caso_code} actualizado exitosamente",
                caso_code=caso_code,
                case=case_info
            )
            
        except (NotFoundError, BadRequestError):
            raise
        except Exception as e:
            raise BadRequestError(f"Error actualizando caso {caso_code}: {str(e)}")
    
    async def _validate_update_request(self, update_data: UpdateCaseRequest) -> None:
        """Validar datos de actualización"""
        # Validar que al menos un campo se esté actualizando
        if not any(update_data.dict(exclude_unset=True).values()):
            raise BadRequestError("Debe especificar al menos un campo para actualizar")
        
        # Validar muestras si se proporcionan
        if update_data.muestras is not None:
            if not update_data.muestras:
                raise BadRequestError("Si se especifican muestras, debe haber al menos una")
        
        # Validar información del paciente si se proporciona
        if update_data.paciente is not None:
            # Validar edad
            if update_data.paciente.edad < 0 or update_data.paciente.edad > 150:
                raise BadRequestError("La edad del paciente debe estar entre 0 y 150 años")
            
            # Validar nombre
            if not update_data.paciente.nombre or not update_data.paciente.nombre.strip():
                raise BadRequestError("El nombre del paciente no puede estar vacío")
        
        # Validar oportunidad si se proporciona
        if update_data.oportunidad is not None and update_data.oportunidad < 0:
            raise BadRequestError("La oportunidad no puede ser negativa")
    
    async def _invalidate_related_caches(self, caso_code: str) -> None:
        """Invalidar caché relacionado con el caso"""
        try:
            # Invalidar caché del caso específico
            await self.cache_service.invalidate_caso_cache(caso_code)
            
            # Invalidar caché de estadísticas
            await self.cache_service.invalidate_stats_cache()
            
        except Exception as e:
            # Log error but don't fail the update
            print(f"Error invalidando caché para caso {caso_code}: {str(e)}")
