import logging
from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import PacienteCreate, PacienteUpdate, PacienteResponse, PacienteSearch
from ..repositories import PacienteRepository
from app.core.exceptions import NotFoundError, BadRequestError, ConflictError

logger = logging.getLogger(__name__)


class PacienteService:
    def __init__(self, database: AsyncIOMotorDatabase):
        self.repository = PacienteRepository(database)

    async def create_paciente(self, paciente: PacienteCreate) -> PacienteResponse:
        try:
            await self._validate_paciente_data(paciente)
            
            # Verificar si ya existe un paciente con el mismo código
            existing_patient = await self.repository.get_by_id(paciente.paciente_code)
            if existing_patient:
                raise ConflictError(f"Ya existe un paciente con el documento {paciente.paciente_code}")
            
            paciente_data = await self.repository.create(paciente)
            return PacienteResponse(**paciente_data)
        except ConflictError as e:
            raise
        except Exception as e:
            raise

    async def get_paciente_by_id(self, paciente_id: str) -> PacienteResponse:
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        return PacienteResponse(**paciente_data)

    async def update_paciente(self, paciente_id: str, paciente_update: PacienteUpdate) -> PacienteResponse:
        if paciente_update.edad is not None and (paciente_update.edad < 0 or paciente_update.edad > 150):
            raise BadRequestError("La edad debe estar entre 0 y 150 años")
        paciente_data = await self.repository.update(paciente_id, paciente_update)
        return PacienteResponse(**paciente_data)

    async def change_patient_code(self, paciente_id: str, new_code: str) -> PacienteResponse:
        if not new_code or len(new_code.strip()) < 6 or len(new_code.strip()) > 12:
            raise BadRequestError("El código del paciente debe tener entre 6 y 12 caracteres")
        # Obtener la colección de casos desde la misma conexión del repositorio
        casos_collection = None
        try:
            casos_collection = self.repository.collection.database.casos
        except Exception:
            casos_collection = None
        paciente_data = await self.repository.change_code(paciente_id, new_code.strip(), casos_collection)
        return PacienteResponse(**paciente_data)

    async def delete_paciente(self, paciente_id: str) -> bool:
        paciente_data = await self.repository.get_by_id(paciente_id)
        if not paciente_data:
            raise NotFoundError(f"Paciente con ID {paciente_id} no encontrado")
        result = await self.repository.delete(paciente_id)
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
        pacientes_data = await self.repository.list_with_filters(
            skip=skip, limit=limit, buscar=buscar, entidad=entidad, sexo=sexo, tipo_atencion=tipo_atencion
        )
        return [PacienteResponse(**p) for p in pacientes_data]

    async def advanced_search(self, search_params: PacienteSearch) -> Dict[str, Any]:
        if search_params.fecha_desde or search_params.fecha_hasta:
            await self._validate_date_range(search_params.fecha_desde, search_params.fecha_hasta)
        result = await self.repository.advanced_search(search_params)
        result["pacientes"] = [PacienteResponse(**p) for p in result["pacientes"]]
        return result

    async def get_entidades_list(self) -> List[str]:
        return await self.repository.get_entidades_list()

    async def get_total_count(self) -> int:
        return await self.repository.count_total()

    async def exists(self, paciente_id: str) -> bool:
        paciente_data = await self.repository.get_by_id(paciente_id)
        return paciente_data is not None


    async def _validate_paciente_data(self, paciente: PacienteCreate) -> None:
        if paciente.edad < 0 or paciente.edad > 150:
            raise BadRequestError("La edad debe estar entre 0 y 150 años")

    async def _validate_date_range(self, fecha_desde: Optional[str], fecha_hasta: Optional[str]) -> None:
        if fecha_desde and fecha_hasta:
            try:
                from datetime import datetime
                fecha_inicio = datetime.fromisoformat(fecha_desde)
                fecha_fin = datetime.fromisoformat(fecha_hasta)
                if fecha_inicio > fecha_fin:
                    raise BadRequestError("La fecha de inicio no puede ser posterior a la fecha de fin")
            except ValueError:
                raise BadRequestError("Formato de fecha inválido. Use YYYY-MM-DD")


paciente_service: Optional[PacienteService] = None

def get_paciente_service(database: AsyncIOMotorDatabase) -> PacienteService:
    return PacienteService(database)