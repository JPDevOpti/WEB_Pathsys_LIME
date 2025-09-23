from pydantic import Field
from app.shared.models.base import BaseDocument
from app.modules.pacientes.schemas.paciente import Sexo, TipoAtencion, EntidadInfo

class Paciente(BaseDocument):
    paciente_code: str = Field(..., min_length=6, max_length=12)
    nombre: str = Field(..., min_length=2, max_length=200)
    edad: int = Field(..., ge=0, le=150)
    sexo: Sexo = Field(...)
    entidad_info: EntidadInfo = Field(...)
    tipo_atencion: TipoAtencion = Field(...)
    observaciones: str = Field(None, max_length=500)