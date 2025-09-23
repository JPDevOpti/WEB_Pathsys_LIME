from datetime import datetime
from typing import Dict, Any
from app.modules.casos.repositories.management.create_repository import CreateCaseRepository
from app.modules.casos.schemas.management.create import CreateCaseRequest, CreateCaseResponse, CreatedCaseInfo
from app.modules.casos.services.cache_service import cache_service
import logging

logger = logging.getLogger(__name__)


class CreateCaseService:
    def __init__(self, create_repo: CreateCaseRepository):
        self.create_repo = create_repo
        self.cache_service = cache_service
    
    async def create_case(self, payload: CreateCaseRequest) -> CreateCaseResponse:
        """
        Crea un nuevo caso con optimizaciones y manejo de caché.
        """
        try:
            # Validar datos de entrada
            await self._validate_create_request(payload)
            
            # Agregar timestamps
            now = datetime.utcnow()
            payload.fecha_creacion = now
            payload.fecha_actualizacion = now
            
            # Crear caso en la base de datos
            created_case_data = await self.create_repo.create_case(payload)
            
            # Construir respuesta optimizada
            created_case_info = CreatedCaseInfo(
                id=created_case_data["id"],
                caso_code=created_case_data["caso_code"],
                paciente=payload.paciente,
                medico_solicitante=created_case_data.get("medico_solicitante"),
                servicio=created_case_data.get("servicio"),
                muestras=payload.muestras,
                estado=payload.estado,
                prioridad=payload.prioridad,
                observaciones_generales=created_case_data.get("observaciones_generales"),
                fecha_creacion=created_case_data.get("fecha_creacion", now),
                fecha_actualizacion=created_case_data.get("fecha_actualizacion", now)
            )
            
            # Invalidar cachés relacionados
            await self._invalidate_related_caches(created_case_data["caso_code"])
            
            logger.info(f"Caso creado exitosamente: {created_case_data['caso_code']}")
            
            return CreateCaseResponse(
                success=True,
                message="Caso creado exitosamente",
                caso_code=created_case_data["caso_code"],
                case=created_case_info
            )
            
        except Exception as e:
            logger.error(f"Error al crear caso: {str(e)}")
            return CreateCaseResponse(
                success=False,
                message=f"Error al crear el caso: {str(e)}",
                caso_code="",
                case=None
            )
    
    async def _validate_create_request(self, payload: CreateCaseRequest) -> None:
        """
        Valida los datos de entrada para la creación del caso.
        """
        # Validar que el código del paciente no esté vacío
        if not payload.paciente.paciente_code or not payload.paciente.paciente_code.strip():
            raise ValueError("El código del paciente es obligatorio")
        
        # Validar que el nombre del paciente no esté vacío
        if not payload.paciente.nombre or not payload.paciente.nombre.strip():
            raise ValueError("El nombre del paciente es obligatorio")
        
        # Validar que la edad sea válida
        if payload.paciente.edad < 0 or payload.paciente.edad > 150:
            raise ValueError("La edad del paciente debe estar entre 0 y 150 años")
        
        # Validar que se especifique al menos una muestra
        if not payload.muestras or len(payload.muestras) == 0:
            raise ValueError("Debe especificar al menos una muestra")
        
        # Validar cada muestra
        for i, muestra in enumerate(payload.muestras):
            if not muestra.region_cuerpo or not muestra.region_cuerpo.strip():
                raise ValueError(f"La región del cuerpo es obligatoria para la muestra {i + 1}")
            
            if not muestra.pruebas or len(muestra.pruebas) == 0:
                raise ValueError(f"Debe especificar al menos una prueba para la muestra {i + 1}")
            
            # Validar cada prueba
            for j, prueba in enumerate(muestra.pruebas):
                if not prueba.id or not prueba.id.strip():
                    raise ValueError(f"El código de la prueba es obligatorio para la muestra {i + 1}, prueba {j + 1}")
                
                if not prueba.nombre or not prueba.nombre.strip():
                    raise ValueError(f"El nombre de la prueba es obligatorio para la muestra {i + 1}, prueba {j + 1}")
                
                if prueba.cantidad < 1 or prueba.cantidad > 10:
                    raise ValueError(f"La cantidad de pruebas debe estar entre 1 y 10 para la muestra {i + 1}, prueba {j + 1}")
    
    async def _invalidate_related_caches(self, caso_code: str) -> None:
        """
        Invalida cachés relacionados con la creación del caso.
        """
        try:
            # Invalidar cachés de estadísticas
            await self.cache_service.invalidate_pattern("stats:*")
            
            # Invalidar cachés de consultas
            await self.cache_service.invalidate_pattern("query:*")
            
            # Invalidar caché específico de casos
            await self.cache_service.invalidate_pattern(f"case:{caso_code}")
            
            logger.info(f"Cachés invalidados para el caso: {caso_code}")
            
        except Exception as e:
            logger.warning(f"Error al invalidar cachés para el caso {caso_code}: {str(e)}")
            # No fallar la creación por error de caché
