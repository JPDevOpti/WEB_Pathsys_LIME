"""Servicio para el módulo de pacientes"""

import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

from ..models import Paciente
from ..schemas import (
    PacienteCreate,
    PacienteUpdate,
    PacienteResponse,
    PacienteSearch
)
from ..schemas import PacienteStats
from ..repositories import PacienteRepository
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError


class PacienteService:
    """Servicio para la lógica de negocio de pacientes"""

    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = PacienteRepository(database)

    async def create_paciente(self, paciente: PacienteCreate) -> PacienteResponse:
        """Crear un nuevo paciente"""
        logger.info(f"Creando nuevo paciente: {paciente.paciente_code}")
        
        try:
            # Validaciones adicionales de negocio
            await self._validate_paciente_data(paciente)
            
            # Crear el paciente
            paciente_data = await self.repository.create(paciente)
            logger.info(f"Paciente creado exitosamente: {paciente.paciente_code}")
            return PacienteResponse(**paciente_data)
        except ConflictError as e:
            logger.warning(f"Conflicto al crear paciente {paciente.paciente_code}: {str(e)}")
            raise
        except Exception as e:
            logger.error(f"Error inesperado creando paciente {paciente.paciente_code}: {str(e)}")
            raise

    async def get_paciente_by_id(self, paciente_id: str) -> PacienteResponse:
        """Obtener un paciente por su ID"""
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        return PacienteResponse(**paciente_data)

    async def get_paciente_by_paciente_code(self, paciente_code: str) -> PacienteResponse:
        """Buscar un paciente por su código"""
        paciente_data = await self.repository.get_by_paciente_code(paciente_code)
        if not paciente_data:
            raise NotFoundError(f"Paciente con código {paciente_code} no encontrado")
        return PacienteResponse(**paciente_data)

    async def update_paciente(self, paciente_id: str, paciente_update: PacienteUpdate) -> PacienteResponse:
        """Actualizar un paciente existente"""
        # Validaciones adicionales si es necesario
        if paciente_update.edad is not None and (paciente_update.edad < 0 or paciente_update.edad > 150):
            raise BadRequestError("La edad debe estar entre 0 y 150 años")
        
        paciente_data = await self.repository.update(paciente_id, paciente_update)
        return PacienteResponse(**paciente_data)

    async def delete_paciente(self, paciente_id: str) -> bool:
        """Eliminar un paciente"""
        logger.info(f"Intentando eliminar paciente: {paciente_id}")
        
        # Verificar si el paciente tiene casos asociados
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            logger.warning(f"Paciente no encontrado para eliminar: {paciente_id}")
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        
        # Si tiene casos, no permitir eliminación
        if paciente_data.get("id_casos") and len(paciente_data["id_casos"]) > 0:
            logger.warning(f"No se puede eliminar paciente {paciente_id} - tiene casos asociados")
            raise BadRequestError(
                "No se puede eliminar un paciente que tiene casos asociados. "
                "Primero debe eliminar o reasignar los casos."
            )
        
        result = await self.repository.delete(paciente_id)
        logger.info(f"Paciente eliminado exitosamente: {paciente_id}")
        return result

    async def list_pacientes(
        self,
        skip: int = 0,
        limit: int = 100,
        buscar: Optional[str] = None,
        entidad: Optional[str] = None,
        sexo: Optional[str] = None,
        tipo_atencion: Optional[str] = None
    ) -> List[PacienteResponse]:
        """Listar pacientes con filtros básicos"""
        pacientes_data = await self.repository.list_with_filters(
            skip=skip,
            limit=limit,
            buscar=buscar,
            entidad=entidad,
            sexo=sexo,
            tipo_atencion=tipo_atencion
        )
        return [PacienteResponse(**p) for p in pacientes_data]

    async def advanced_search(self, search_params: PacienteSearch) -> Dict[str, Any]:
        """Búsqueda avanzada de pacientes"""
        # Validar parámetros de fecha
        if search_params.fecha_desde or search_params.fecha_hasta:
            await self._validate_date_range(search_params.fecha_desde, search_params.fecha_hasta)
        
        result = await self.repository.advanced_search(search_params)
        
        # Convertir pacientes a PacienteResponse
        result["pacientes"] = [PacienteResponse(**p) for p in result["pacientes"]]
        
        return result

    async def get_entidades_list(self) -> List[str]:
        """Obtener lista de entidades únicas"""
        return await self.repository.get_entidades_list()

    async def add_caso_to_paciente(self, paciente_id: str, id_caso: str) -> bool:
        """Agregar un caso a un paciente"""
        # Verificar que el paciente existe
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        
        # Usar el método del repositorio
        return await self.repository.add_caso_to_paciente(paciente_id, id_caso)

    async def remove_caso_from_paciente(self, paciente_id: str, id_caso: str) -> bool:
        """Remover un caso de un paciente"""
        # Verificar que el paciente existe
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        
        # Usar el método del repositorio
        return await self.repository.remove_caso_from_paciente(paciente_id, id_caso)

    async def get_total_count(self) -> int:
        """Obtener el total de pacientes"""
        return await self.repository.count_total()

    async def exists(self, paciente_id: str) -> bool:
        """Verificar si existe un paciente"""
        paciente_data = await self.repository.get_by_id(paciente_id)
        return paciente_data is not None

    async def get_statistics(self) -> PacienteStats:
        """Obtener estadísticas generales de pacientes"""
        logger.info("Obteniendo estadísticas de pacientes")
        stats_data = await self.repository.get_statistics()
        
        # Procesar los datos para el esquema PacienteStats
        general = stats_data.get("general", {})
        por_sexo = stats_data.get("por_sexo", [])
        por_entidad = stats_data.get("por_entidad", [])
        por_tipo_atencion = stats_data.get("por_tipo_atencion", [])
        casos = stats_data.get("casos", [])
        
        # Contar por sexo
        total_hombres = 0
        total_mujeres = 0
        for sexo_stat in por_sexo:
            if sexo_stat["_id"] == "Masculino":
                total_hombres = sexo_stat["count"]
            elif sexo_stat["_id"] == "Femenino":
                total_mujeres = sexo_stat["count"]
        
        # Contar por tipo de atención
        total_ambulatorios = 0
        total_hospitalizados = 0
        for atencion_stat in por_tipo_atencion:
            if atencion_stat["_id"] == "Ambulatorio":
                total_ambulatorios = atencion_stat["count"]
            elif atencion_stat["_id"] == "Hospitalizado":
                total_hospitalizados = atencion_stat["count"]
        
        # Contar pacientes con casos
        pacientes_con_casos = 0
        for caso_stat in casos:
            if caso_stat["_id"] is True:
                pacientes_con_casos = caso_stat["count"]
        
        # Estadísticas mensuales
        mensuales = stats_data.get("mensuales", {})
        
        # Distribución por género
        distribucion_genero = {
            "masculino": total_hombres,
            "femenino": total_mujeres,
            "otro": general.get("total_pacientes", 0) - total_hombres - total_mujeres
        }
        
        stats = PacienteStats(
            total_pacientes=general.get("total_pacientes", 0),
            total_hombres=total_hombres,
            total_mujeres=total_mujeres,
            promedio_edad=round(general.get("promedio_edad", 0), 2),
            edad_min=general.get("edad_minima", 0),
            edad_max=general.get("edad_maxima", 0),
            total_ambulatorios=total_ambulatorios,
            total_hospitalizados=total_hospitalizados,
            entidades_mas_frecuentes=por_entidad,
            pacientes_con_casos=pacientes_con_casos,
            pacientes_mes_actual=mensuales.get("pacientes_mes_actual", 0),
            pacientes_mes_anterior=mensuales.get("pacientes_mes_anterior", 0),
            cambio_porcentual=mensuales.get("cambio_porcentual", 0.0),
            distribucion_genero=distribucion_genero
        )
        
        logger.info(f"Estadísticas obtenidas: {stats.total_pacientes} pacientes totales")
        return stats

    # Métodos privados para validaciones
    async def _validate_paciente_data(self, paciente: PacienteCreate) -> None:
        """Validar datos del paciente antes de crear"""
        # Validaciones adicionales de negocio
        if paciente.edad < 0 or paciente.edad > 150:
            logger.warning(f"Edad inválida para paciente {paciente.paciente_code}: {paciente.edad}")
            raise BadRequestError("La edad debe estar entre 0 y 150 años")
        
        # Validaciones adicionales pueden agregarse aquí
        logger.debug(f"Validaciones de paciente {paciente.paciente_code} completadas")

    async def _validate_date_range(self, fecha_desde: Optional[str], fecha_hasta: Optional[str]) -> None:
        """Validar rango de fechas"""
        if fecha_desde and fecha_hasta:
            try:
                from datetime import datetime
                fecha_inicio = datetime.fromisoformat(fecha_desde)
                fecha_fin = datetime.fromisoformat(fecha_hasta)
                
                if fecha_inicio > fecha_fin:
                    logger.warning(f"Rango de fechas inválido: {fecha_desde} > {fecha_hasta}")
                    raise BadRequestError("La fecha de inicio no puede ser posterior a la fecha de fin")
                    
            except ValueError:
                logger.warning(f"Formato de fecha inválido: {fecha_desde} o {fecha_hasta}")
                raise BadRequestError("Formato de fecha inválido. Use YYYY-MM-DD")

    def _is_valid_email(self, email: str) -> bool:
        """Validar formato de email básico"""
        import re
        pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
        return re.match(pattern, email) is not None

    def _is_valid_phone(self, phone: str) -> bool:
        """Validar formato de teléfono básico"""
        import re
        # Permitir números con espacios, guiones, paréntesis y signos +
        pattern = r'^[\+]?[\d\s\-\(\)]{7,15}$'
        return re.match(pattern, phone) is not None


# Instancia global del servicio (se inicializará en el router)
paciente_service: Optional[PacienteService] = None


def get_paciente_service(database: AsyncIOMotorDatabase) -> PacienteService:
    """Factory function para obtener el servicio de pacientes"""
    return PacienteService(database)