from typing import Optional, List
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from enum import Enum

class RolEnum(str, Enum):
    """Roles disponibles en el sistema"""
    ADMINISTRADOR = "administrador"
    AUXILIAR = "auxiliar"
    PATOLOGO = "patologo"
    RESIDENTE = "residente"
    PACIENTE = "paciente"

class EstadoCasoEnum(str, Enum):
    """Estados de un caso"""
    EN_PROCESO = "En proceso"
    POR_FIRMAR = "Por firmar"
    POR_ENTREGAR = "Por entregar"
    COMPLETADO = "Completado"

class TipoDocumentoEnum(str, Enum):
    """Tipos de documento de identidad"""
    CEDULA = "cedula"
    PASAPORTE = "pasaporte"
    TARJETA_IDENTIDAD = "tarjeta_identidad"
    CEDULA_EXTRANJERIA = "cedula_extranjeria"

class GeneroEnum(str, Enum):
    """Géneros disponibles"""
    MASCULINO = "masculino"
    FEMENINO = "femenino"
    OTRO = "otro"
    NO_ESPECIFICA = "no_especifica"

class TipoPruebaEnum(str, Enum):
    """Tipos de prueba"""
    BIOPSIA = "biopsia"
    CITOLOGIA = "citologia"
    INMUNOHISTOQUIMICA = "inmunohistoquimica"
    MOLECULAR = "molecular"
    ESPECIAL = "especial"

class PrioridadEnum(str, Enum):
    """Niveles de prioridad"""
    BAJA = "baja"
    NORMAL = "normal"
    ALTA = "alta"
    URGENTE = "urgente"

class SearchParams(BaseModel):
    """Parámetros de búsqueda comunes"""
    query: Optional[str] = Field(None, description="Término de búsqueda")
    skip: int = Field(0, ge=0, description="Número de registros a omitir")
    limit: int = Field(100, ge=1, le=1000, description="Número máximo de registros")
    sort_by: Optional[str] = Field(None, description="Campo por el cual ordenar")
    sort_order: Optional[str] = Field("asc", pattern="^(asc|desc)$", description="Orden ascendente o descendente")

class DateRangeFilter(BaseModel):
    """Filtro por rango de fechas"""
    fecha_inicio: Optional[datetime] = Field(None, description="Fecha de inicio")
    fecha_fin: Optional[datetime] = Field(None, description="Fecha de fin")

class ContactInfo(BaseModel):
    """Información de contacto"""
    telefono: Optional[str] = Field(None, max_length=20)
    email: Optional[EmailStr] = None
    direccion: Optional[str] = Field(None, max_length=500)
    ciudad: Optional[str] = Field(None, max_length=100)
    departamento: Optional[str] = Field(None, max_length=100)
    codigo_postal: Optional[str] = Field(None, max_length=10)

class PersonaInfo(BaseModel):
    """Información básica de una persona"""
    nombre: str = Field(..., min_length=2, max_length=100)
    apellido: str = Field(..., min_length=2, max_length=100)
    tipo_documento: TipoDocumentoEnum
    numero_documento: str = Field(..., min_length=5, max_length=20)
    fecha_nacimiento: Optional[datetime] = None
    genero: Optional[GeneroEnum] = None
    contacto: Optional[ContactInfo] = None

class AuditInfo(BaseModel):
    """Información de auditoría"""
    creado_por: Optional[str] = None
    actualizado_por: Optional[str] = None
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow)
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)
    ip_creacion: Optional[str] = None
    ip_actualizacion: Optional[str] = None

class FileInfo(BaseModel):
    """Información de archivo"""
    nombre: str
    ruta: str
    tamaño: int
    tipo_mime: str
    fecha_subida: datetime = Field(default_factory=datetime.utcnow)
    subido_por: Optional[str] = None

class CodigoGenerado(BaseModel):
    """Código generado automáticamente"""
    prefijo: str
    numero: int
    año: int
    codigo_completo: str

class NotificationSettings(BaseModel):
    """Configuración de notificaciones"""
    email_enabled: bool = True
    sms_enabled: bool = False
    push_enabled: bool = True
    casos_nuevos: bool = True
    casos_completados: bool = True
    casos_urgentes: bool = True

class SystemSettings(BaseModel):
    """Configuración del sistema"""
    mantenimiento: bool = False
    mensaje_mantenimiento: Optional[str] = None
    version: str = "2.0.0"
    ultima_actualizacion: datetime = Field(default_factory=datetime.utcnow)