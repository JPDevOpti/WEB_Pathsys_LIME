"""Esquemas Pydantic para el módulo de casos"""

from typing import Optional, List, Dict, Any
from datetime import datetime
from pydantic import BaseModel, Field, validator
from app.shared.schemas.common import (
    EstadoCasoEnum,
    TipoDocumentoEnum,
    GeneroEnum
)
from app.modules.pruebas.schemas.prueba import PruebasItem
from app.modules.casos.models.caso import PrioridadCasoEnum


class DiagnosticoCIE10(BaseModel):
    """Información del diagnóstico CIE-10."""
    codigo: str = Field(..., max_length=20, description="Código CIE-10 de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIE-10")


class DiagnosticoCIEO(BaseModel):
    """Información del diagnóstico CIEO (cáncer)."""
    codigo: str = Field(..., max_length=20, description="Código CIEO de la enfermedad")
    nombre: str = Field(..., max_length=500, description="Nombre de la enfermedad CIEO")


class EntidadInfo(BaseModel):
    """Información de la entidad asignada"""
    id: str = Field(..., max_length=50, description="ID único de la entidad")
    nombre: str = Field(..., max_length=200, description="Nombre de la entidad")

class MuestraInfo(BaseModel):
    """Información de una muestra dentro de un caso"""
    region_cuerpo: str = Field(..., description="Región del cuerpo de donde se tomó la muestra")
    pruebas: List[PruebasItem] = Field(default_factory=list, description="Lista de pruebas a realizar")

class PacienteInfo(BaseModel):
    """Información básica del paciente en un caso"""
    paciente_code: str = Field(..., max_length=50, description="Código único del paciente")
    nombre: str = Field(..., max_length=200, description="Nombre completo del paciente")
    edad: int = Field(..., ge=0, le=150, description="Edad del paciente")
    sexo: str = Field(..., max_length=20, description="Sexo del paciente")
    entidad_info: EntidadInfo = Field(..., description="Información de la entidad de salud")
    tipo_atencion: str = Field(..., max_length=50, description="Tipo de atención")
    observaciones: Optional[str] = Field(None, max_length=1000, description="Observaciones del paciente")
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow)

    @validator('tipo_atencion')
    def validate_tipo_atencion(cls, v):
        """Validar tipo de atención"""
        if not v or not v.strip():
            raise ValueError('El tipo de atención no puede estar vacío')
        tipo = v.strip()
        tipos_validos = ['Ambulatorio', 'Hospitalizado']
        if tipo not in tipos_validos:
            raise ValueError(f'El tipo de atención debe ser uno de: {", ".join(tipos_validos)}')
        return tipo

    @validator('nombre', pre=True)
    def validate_nombre(cls, v):
        """Validar y normalizar nombre del paciente"""
        if not v or not v.strip():
            raise ValueError('El nombre del paciente no puede estar vacío')
        # Capitalizar cada palabra del nombre
        return ' '.join(word.capitalize() for word in v.strip().split())

    @validator('paciente_code', pre=True)
    def validate_paciente_code(cls, v):
        """Validar código del paciente"""
        if not v or not v.strip():
            raise ValueError('El código del paciente no puede estar vacío')
        # Remover espacios y caracteres no numéricos
        codigo_clean = ''.join(c for c in v if c.isdigit())
        if not codigo_clean:
            raise ValueError('El código del paciente debe contener al menos un dígito')
        if len(codigo_clean) < 6 or len(codigo_clean) > 12:
            raise ValueError('El código del paciente debe tener entre 6 y 12 dígitos')
        return codigo_clean

class PatologoInfo(BaseModel):
    """Información del patólogo asignado"""
    codigo: str = Field(..., description="Código único del patólogo")
    nombre: str = Field(..., description="Nombre completo del patólogo")

    class Config:
        populate_by_name = True

class ResultadoInfo(BaseModel):
    """Información de resultados del caso"""
    metodo: Optional[List[str]] = Field(default_factory=list, description="Lista de métodos utilizados")
    resultado_macro: Optional[str] = Field(None, description="Descripción macroscópica")
    resultado_micro: Optional[str] = Field(None, description="Descripción microscópica")
    diagnostico: Optional[str] = Field(None, description="Diagnóstico final")
    diagnostico_cie10: Optional[DiagnosticoCIE10] = Field(None, description="Diagnóstico CIE-10")
    diagnostico_cieo: Optional[DiagnosticoCIEO] = Field(None, description="Diagnóstico CIEO (cáncer)")
    observaciones: Optional[str] = Field(None, description="Observaciones adicionales")
    # Eliminados campos internos de control: fecha_resultado, firmado, fecha_firma interna.

class CasoBase(BaseModel):
    """Modelo base para casos"""
    caso_code: str = Field(..., max_length=50, description="Código único del caso")
    paciente: PacienteInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico que solicita (opcional)")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico o especialidad")
    muestras: List[MuestraInfo] = Field(..., description="Muestras del caso")
    estado: EstadoCasoEnum = Field(default=EstadoCasoEnum.EN_PROCESO)
    prioridad: PrioridadCasoEnum = Field(default=PrioridadCasoEnum.NORMAL, description="Prioridad del caso")
    oportunidad: Optional[int] = Field(None, description="Días hábiles transcurridos al completar el caso", ge=0)
    entregado_a: Optional[str] = Field(None, max_length=100, description="Persona que recibe el caso al ser entregado")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del caso")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma del resultado")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega del caso")
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    observaciones_generales: Optional[str] = Field(None, max_length=1000, description="Observaciones generales del caso")
    
    @validator('caso_code')
    def validate_caso_code(cls, v):
        if not v or not v.strip():
            raise ValueError('El código del caso es requerido')
        
        caso_code = v.strip()
        
        # Validar formato YYYY-NNNNN
        import re
        pattern = r'^20\d{2}-\d{5}$'
        if not re.match(pattern, caso_code):
            raise ValueError('El código del caso debe tener el formato YYYY-NNNNN (ejemplo: 2025-00001)')
        
        # Validar que el año sea razonable (entre 2020 y 2100)
        year = int(caso_code.split('-')[0])
        if year < 2020 or year > 2100:
            raise ValueError('El año del código de caso debe estar entre 2020 y 2100')
        
        # Validar que el número esté en el rango correcto
        number = int(caso_code.split('-')[1])
        if number < 1 or number > 99999:
            raise ValueError('El número consecutivo debe estar entre 00001 y 99999')
        
        return caso_code

class CasoCreateRequest(BaseModel):
    """Modelo para crear un nuevo caso - SIN código (se genera automáticamente)"""
    paciente: PacienteInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico que solicita (opcional)")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico o especialidad")
    muestras: List[MuestraInfo] = Field(..., description="Muestras del caso")
    estado: EstadoCasoEnum = Field(default=EstadoCasoEnum.EN_PROCESO)
    prioridad: PrioridadCasoEnum = Field(default=PrioridadCasoEnum.NORMAL, description="Prioridad del caso")
    oportunidad: Optional[int] = Field(None, description="Días hábiles transcurridos al completar el caso", ge=0)
    entregado_a: Optional[str] = Field(None, max_length=100, description="Persona que recibe el caso al ser entregado")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del caso")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma del resultado")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega del caso")
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    observaciones_generales: Optional[str] = Field(None, max_length=1000, description="Observaciones generales del caso")

class CasoCreateWithCode(BaseModel):
    """Modelo para crear un nuevo caso CON código específico (desde frontend)"""
    caso_code: str = Field(..., max_length=50, description="Código único del caso")
    paciente: PacienteInfo = Field(..., description="Información del paciente")
    medico_solicitante: Optional[str] = Field(None, max_length=200, description="Médico que solicita (opcional)")
    servicio: Optional[str] = Field(None, max_length=100, description="Servicio médico o especialidad")
    muestras: List[MuestraInfo] = Field(..., description="Muestras del caso")
    estado: EstadoCasoEnum = Field(default=EstadoCasoEnum.EN_PROCESO)
    prioridad: PrioridadCasoEnum = Field(default=PrioridadCasoEnum.NORMAL, description="Prioridad del caso")
    oportunidad: Optional[int] = Field(None, description="Días hábiles transcurridos al completar el caso", ge=0)
    entregado_a: Optional[str] = Field(None, max_length=100, description="Persona que recibe el caso al ser entregado")
    fecha_creacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de creación del caso")
    fecha_firma: Optional[datetime] = Field(None, description="Fecha de firma del resultado")
    fecha_entrega: Optional[datetime] = Field(None, description="Fecha de entrega del caso")
    fecha_actualizacion: datetime = Field(default_factory=datetime.utcnow, description="Fecha de última actualización")
    observaciones_generales: Optional[str] = Field(None, max_length=1000, description="Observaciones generales del caso")
    
    @validator('caso_code')
    def validate_caso_code(cls, v):
        if not v or not v.strip():
            raise ValueError('El código del caso es requerido')
        
        caso_code = v.strip()
        
        # Validar formato YYYY-NNNNN
        import re
        pattern = r'^20\d{2}-\d{5}$'
        if not re.match(pattern, caso_code):
            raise ValueError('El código del caso debe tener el formato YYYY-NNNNN (ejemplo: 2025-00001)')
        
        # Validar que el año sea razonable (entre 2020 y 2100)
        year = int(caso_code.split('-')[0])
        if year < 2020 or year > 2100:
            raise ValueError('El año del código de caso debe estar entre 2020 y 2100')
        
        # Validar que el número esté en el rango correcto
        number = int(caso_code.split('-')[1])
        if number < 1 or number > 99999:
            raise ValueError('El número consecutivo debe estar entre 00001 y 99999')
        
        return caso_code

class CasoCreate(CasoBase):
    """Modelo para crear un nuevo caso"""
    pass

class CasoUpdate(BaseModel):
    """Modelo para actualizar un caso existente"""
    medico_solicitante: Optional[str] = Field(None, max_length=200)
    servicio: Optional[str] = Field(None, max_length=100)
    muestras: Optional[List[MuestraInfo]] = None
    estado: Optional[EstadoCasoEnum] = None
    prioridad: Optional[PrioridadCasoEnum] = None
    oportunidad: Optional[int] = Field(None, description="Días hábiles transcurridos al completar el caso", ge=0)
    entregado_a: Optional[str] = Field(None, max_length=100, description="Persona que recibe el caso al ser entregado")

    fecha_firma: Optional[datetime] = None
    fecha_actualizacion: Optional[datetime] = None
    observaciones_generales: Optional[str] = Field(None, max_length=1000)
    patologo_asignado: Optional[PatologoInfo] = None

    entidad_info: Optional[EntidadInfo] = None
    resultado: Optional[ResultadoInfo] = None
    # Permitir actualizar información del paciente dentro del caso
    paciente: Optional[PacienteInfo] = None

class CasoResponse(CasoBase):
    """Modelo de respuesta para casos"""
    id: str = Field(..., description="ID único del caso")
    patologo_asignado: Optional[PatologoInfo] = None

    entidad_info: Optional[EntidadInfo] = None
    resultado: Optional[ResultadoInfo] = None
    
    # Campos de auditoría
    ingresado_por: Optional[str] = None
    actualizado_por: Optional[str] = None

class CasoSearch(BaseModel):
    """Modelo para búsqueda de casos"""
    query: Optional[str] = Field(None, description="Búsqueda general")
    caso_code: Optional[str] = Field(None, description="Código específico del caso")
    paciente_code: Optional[str] = Field(None, description="Código del paciente")
    paciente_nombre: Optional[str] = Field(None, description="Nombre del paciente")
    medico_nombre: Optional[str] = Field(None, description="Nombre del médico")
    patologo_codigo: Optional[str] = Field(None, description="Código del patólogo asignado")
    estado: Optional[EstadoCasoEnum] = None
    prioridad: Optional[PrioridadCasoEnum] = None
    fecha_ingreso_desde: Optional[datetime] = None
    fecha_ingreso_hasta: Optional[datetime] = None

    fecha_firma_desde: Optional[datetime] = None
    fecha_firma_hasta: Optional[datetime] = None
    solo_vencidos: Optional[bool] = Field(default=False, description="Solo casos vencidos")
    solo_sin_patologo: Optional[bool] = Field(default=False, description="Solo casos sin patólogo")
    solo_firmados: Optional[bool] = Field(default=False, description="Solo casos firmados")

class CasoStats(BaseModel):
    """Estadísticas de casos"""
    total_casos: int = 0
    casos_en_proceso: int = 0
    casos_por_firmar: int = 0
    casos_por_entregar: int = 0
    casos_completados: int = 0
    # Eliminado casos_cancelados tras remover estado CANCELADO
    casos_vencidos: int = 0
    casos_sin_patologo: int = 0
    
    # Estadísticas de tiempo
    tiempo_promedio_procesamiento: Optional[float] = Field(None, description="Días promedio")
    casos_mes_actual: int = 0
    casos_mes_anterior: int = 0
    casos_semana_actual: int = 0
    cambio_porcentual: float = 0.0
    
    # Por patólogo
    casos_por_patologo: Dict[str, int] = Field(default_factory=dict)
    
    # Por tipo de prueba
    casos_por_tipo_prueba: Dict[str, int] = Field(default_factory=dict)

class CasoDeleteResponse(BaseModel):
    """Respuesta para la eliminación de un caso"""
    message: str = Field(..., description="Mensaje de confirmación")
    caso_code: str = Field(..., description="Código del caso eliminado")
    eliminado: bool = Field(True, description="Indica si el caso fue eliminado")

    class Config:
        from_attributes = True


class MuestraStats(BaseModel):
    """Estadísticas de muestras"""
    total_muestras: int = 0
    muestras_mes_anterior: int = 0
    muestras_mes_anterior_anterior: int = 0
    cambio_porcentual: float = 0.0
    
    # Distribución por región del cuerpo
    muestras_por_region: Dict[str, int] = Field(default_factory=dict)
    
    # Distribución por tipo de prueba
    muestras_por_tipo_prueba: Dict[str, int] = Field(default_factory=dict)
    
    # Estadísticas de tiempo
    tiempo_promedio_procesamiento: Optional[float] = Field(None, description="Días promedio")
    
    class Config:
        from_attributes = True


# ============================================================================
# ESQUEMAS PARA ESTADÍSTICAS DE PRUEBAS
# ============================================================================

class PruebaStats(BaseModel):
    """Estadísticas de una prueba específica"""
    codigo: str = Field(..., description="Código de la prueba")
    nombre: str = Field(..., description="Nombre de la prueba")
    total_solicitadas: int = Field(0, description="Total de solicitudes")
    total_completadas: int = Field(0, description="Total de casos completados")
    tiempo_promedio: float = Field(0.0, description="Tiempo promedio en días")
    porcentaje_completado: float = Field(0.0, description="Porcentaje de casos completados")
    
    class Config:
        from_attributes = True


class PruebaDetails(BaseModel):
    """Detalles completos de una prueba"""
    estadisticas_principales: Dict[str, Any] = Field(default_factory=dict)
    tiempos_procesamiento: Dict[str, Any] = Field(default_factory=dict)
    patologos: List[Dict[str, Any]] = Field(default_factory=list)
    
    class Config:
        from_attributes = True


class PruebasReportData(BaseModel):
    """Datos del reporte de pruebas"""
    pruebas: List[PruebaStats] = Field(default_factory=list)
    resumen: Dict[str, Any] = Field(default_factory=dict)
    
    class Config:
        from_attributes = True


class PatologoPorPrueba(BaseModel):
    """Información de patólogo por prueba"""
    nombre: str = Field(..., description="Nombre del patólogo")
    codigo: str = Field(..., description="Código del patólogo")
    total_procesadas: int = Field(0, description="Total de casos procesados")
    tiempo_promedio: float = Field(0.0, description="Tiempo promedio en días")
    
    class Config:
        from_attributes = True