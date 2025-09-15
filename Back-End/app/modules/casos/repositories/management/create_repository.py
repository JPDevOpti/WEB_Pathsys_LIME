from typing import Dict, Any, Optional
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.core.dependencies import get_database
from app.modules.casos.schemas.management.create import CreateCaseRequest, CreatedCaseInfo
from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
import logging

logger = logging.getLogger(__name__)


class CreateCaseRepository:
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.cases_collection = db.casos
        self.consecutivo_repo = ConsecutivoRepository(db)
        self.entities_repo = EntidadRepository(db)
    
    async def create_case(self, case_data: CreateCaseRequest) -> Dict[str, Any]:
        """
        Crea un nuevo caso en la base de datos con optimizaciones.
        """
        try:
            # Generar código consecutivo atómico
            consecutivo_data = await self.consecutivo_repo.get_next_consecutive()
            caso_code = consecutivo_data["codigo_consecutivo"]
            
            # Enriquecer entidad con nombre si no está presente
            if not case_data.paciente.entidad_info.nombre:
                entity_info = await self.entities_repo.get_by_code(case_data.paciente.entidad_info.id)
                if entity_info:
                    case_data.paciente.entidad_info.nombre = entity_info.entidad_name
            
            # Preparar documento optimizado para inserción
            case_document = {
                "caso_code": caso_code,
                "paciente": {
                    "paciente_code": case_data.paciente.paciente_code,
                    "nombre": case_data.paciente.nombre,
                    "edad": case_data.paciente.edad,
                    "sexo": case_data.paciente.sexo.value,
                    "entidad_info": {
                        "id": case_data.paciente.entidad_info.id,
                        "nombre": case_data.paciente.entidad_info.nombre
                    },
                    "tipo_atencion": case_data.paciente.tipo_atencion.value,
                    "observaciones": case_data.paciente.observaciones
                },
                "medico_solicitante": case_data.medico_solicitante,
                "servicio": case_data.servicio,
                "muestras": [
                    {
                        "region_cuerpo": muestra.region_cuerpo,
                        "pruebas": [
                            {
                                "id": prueba.id,
                                "nombre": prueba.nombre,
                                "cantidad": prueba.cantidad
                            }
                            for prueba in muestra.pruebas
                        ]
                    }
                    for muestra in case_data.muestras
                ],
                "estado": case_data.estado.value,
                "prioridad": case_data.prioridad.value,
                "observaciones_generales": case_data.observaciones_generales,
                "fecha_creacion": case_data.fecha_creacion if hasattr(case_data, 'fecha_creacion') else None,
                "fecha_actualizacion": case_data.fecha_actualizacion if hasattr(case_data, 'fecha_actualizacion') else None,
                "ingresado_por": "api_management",
                "actualizado_por": "api_management"
            }
            
            # Insertar documento
            result = await self.cases_collection.insert_one(case_document)
            
            if not result.inserted_id:
                raise Exception("Error al insertar el caso en la base de datos")
            
            # Retornar documento creado con proyección mínima
            created_case = await self.cases_collection.find_one(
                {"_id": result.inserted_id},
                {
                    "_id": 1,
                    "caso_code": 1,
                    "paciente": 1,
                    "medico_solicitante": 1,
                    "servicio": 1,
                    "muestras": 1,
                    "estado": 1,
                    "prioridad": 1,
                    "observaciones_generales": 1,
                    "fecha_creacion": 1,
                    "fecha_actualizacion": 1
                }
            )
            
            if not created_case:
                raise Exception("Error al recuperar el caso creado")
            
            # Convertir ObjectId a string para serialización
            created_case["id"] = str(created_case["_id"])
            del created_case["_id"]
            
            logger.info(f"Caso creado exitosamente: {caso_code}")
            return created_case
            
        except Exception as e:
            logger.error(f"Error al crear caso: {str(e)}")
            raise Exception(f"Error al crear el caso: {str(e)}")
    
    async def validate_case_uniqueness(self, caso_code: str) -> bool:
        """
        Valida que el código del caso sea único.
        """
        existing_case = await self.cases_collection.find_one(
            {"caso_code": caso_code},
            {"_id": 1}
        )
        return existing_case is None
