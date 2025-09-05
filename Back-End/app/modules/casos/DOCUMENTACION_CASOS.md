# Documentación del Módulo de Casos

## 1. Modelo y Esquemas (Actualizado)

La siguiente estructura refleja el estado REAL del código (`models/caso.py` y `schemas/caso.py`).

### 1.1 Modelo Persistido (MongoDB) `Caso` (models)

```json
{
  "_id": "string (ObjectId)",
  "caso_code": "string (formato 20YY-NNNNN, ejemplo 2025-00001, único)",
  "paciente": {
    "paciente_code": "string (6-12 dígitos, se normaliza a solo números)",
    "nombre": "string (capitalizado, máx 200)",
    "edad": "int (0-150)",
    "sexo": "string (máx 20)",
    "entidad_info": {"id": "string (máx 50)", "nombre": "string (máx 200)"},
    "tipo_atencion": "Ambulatorio | Hospitalizado",
    "observaciones": "string | null (máx 1000)",
    "fecha_actualizacion": "datetime ISO"
  },
  "medico_solicitante": {"nombre": "string (máx 200)"} | null,
  "servicio": "string | null (máx 100)",
  "muestras": [
    {
      "region_cuerpo": "string",
      "pruebas": [
        {"id": "string", "nombre": "string", "cantidad": "int (default 1)"}
      ]
    }
  ],
  "estado": "En proceso | Por firmar | Por entregar | Completado | cancelado",
  "fecha_creacion": "datetime ISO",
  "fecha_firma": "datetime ISO | null (firma global del caso, se establece al firmar resultado)",
  "fecha_entrega": "datetime ISO | null",
  "fecha_actualizacion": "datetime ISO",
  "patologo_asignado": {"codigo": "string", "nombre": "string"} | null,
  "resultado": {
    "tipo_resultado": "histopatologia | citologia | inmunohistoquimica | null",
    "metodo": "string | null",
    "resultado_macro": "string | null",
    "resultado_micro": "string | null",
    "diagnostico": "string | null",
    "diagnostico_cie10": {"id": "string", "codigo": "string (<=20)", "nombre": "string (<=500)"} | null,
    "diagnostico_cieo": {"id": "string", "codigo": "string (<=20)", "nombre": "string (<=500)"} | null,
    "observaciones": "string | null",
    "fecha_resultado": "datetime ISO | null",
    "firmado": "bool (default false)",
    "fecha_firma": "datetime ISO | null"
  } | null,
  "observaciones_generales": "string | null (<=1000)",
  "creado_por": "string | null",
  "actualizado_por": "string | null",
  "activo": true
}
```

### 1.2 Esquema de Entrada/Salida Principal (API) `CasoResponse` (schemas)

El esquema expuesto por la API omite `_id` y utiliza `id` como string:

```json
{
  "id": "string (ObjectId como texto)",
  "caso_code": "2025-00001",
  "paciente": { "paciente_code": "123456", "nombre": "Juan Perez", "edad": 45, "sexo": "Masculino", "entidad_info": {"id": "EPS001", "nombre": "Entidad Salud"}, "tipo_atencion": "Ambulatorio", "observaciones": null, "fecha_actualizacion": "2025-01-15T10:30:00Z" },
  "medico_solicitante": {"nombre": "Dra. Ana Gómez"},

### 20. GET http://localhost:8000/api/v1/casos/estadisticas

**Obtener estadísticas generales de casos**

**Descripción**: Obtiene estadísticas completas del sistema de casos.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200):

```json
{
  "total_casos": 150,
  "casos_en_proceso": 45,
  "casos_por_firmar": 30,
  "casos_por_entregar": 25,
  "casos_completados": 40,
  "casos_cancelados": 10,
  "casos_vencidos": 8,
  "casos_sin_patologo": 25,
  "tiempo_promedio_procesamiento": 5.2,
  "casos_mes_actual": 45,
  "casos_mes_anterior": 38,
  "casos_semana_actual": 12,
  "cambio_porcentual": 18.4,
  "casos_por_patologo": {
    "PAT001": 25,
    "PAT002": 20,
    "PAT003": 15
  },
  "casos_por_tipo_prueba": {
    "Histopatología": 80,
    "Citología": 45,
    "Inmunohistoquímica": 25
  }
}
```

### 21. GET <http://localhost:8000/api/v1/casos/estadisticas-muestras>

Descripción: Obtiene estadísticas específicas sobre las muestras procesadas.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200):

```json
{
  "total_muestras": 200,
  "muestras_mes_anterior": 45,
  "muestras_mes_anterior_anterior": 38,
  "cambio_porcentual": 18.4,
  "muestras_por_region": {
    "Piel": 50,
    "Colon": 30,
    "Mama": 25,
    "Próstata": 20
  },
  "muestras_por_tipo_prueba": {
    "Histopatología": 120,
    "Citología": 50,
    "Inmunohistoquímica": 30
  },
  "tiempo_promedio_procesamiento": 4.8
}
```

### 22. GET <http://localhost:8000/api/v1/casos/casos-por-mes/{year}>

Descripción: Obtiene estadísticas mensuales de casos para un año determinado.

**Autenticación**: Requerida

**Path Parameters**:

- `year`: Año para consultar (rango: 2020-2030)

Ejemplo: `http://localhost:8000/api/v1/casos/casos-por-mes/2025`

Body: (sin body)

Respuesta (200):

```json
{
  "year": 2025,
  "casos_por_mes": {
    "enero": 45,
    "febrero": 38,
    "marzo": 52,
    "abril": 41,
    "mayo": 48,
    "junio": 35,
    "julio": 42,
    "agosto": 39,
    "septiembre": 44,
    "octubre": 47,
    "noviembre": 41,
    "diciembre": 38
  },
  "total_año": 510
}
```

### 23. GET <http://localhost:8000/api/v1/casos/estadisticas-oportunidad-mensual>

Descripción: Obtiene estadísticas de oportunidad del mes anterior comparado con el mes anterior a este.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200):

```json
{
  "mes_anterior": {
    "mes": "diciembre",
    "año": 2024,
    "total_casos": 45,
    "casos_completados": 42,
    "tiempo_promedio_dias": 4.2,
    "casos_vencidos": 3
  },
  "mes_anterior_anterior": {
    "mes": "noviembre",
    "año": 2024,
    "total_casos": 38,
    "casos_completados": 35,
    "tiempo_promedio_dias": 5.1,
    "casos_vencidos": 5
  },
  "comparacion": {
    "cambio_casos": 18.4,
    "cambio_completados": 20.0,
    "mejora_tiempo": -17.6,
    "reduccion_vencidos": -40.0
  }
}
```

## Estructura del modelo

### Modelos de Diagnóstico

#### DiagnosticoCIE10

```python
class DiagnosticoCIE10(BaseModel):
    id: str                    # ID único de la enfermedad CIE-10
    codigo: str               # Código CIE-10 (ej: "A000")
    nombre: str               # Nombre completo de la enfermedad
```

#### DiagnosticoCIEO

```python
class DiagnosticoCIEO(BaseModel):
    id: str                    # ID único de la enfermedad CIEO
    codigo: str               # Código CIEO (ej: "C000")
    nombre: str               # Nombre completo de la enfermedad
```

### Modelo de Resultado (Actualizado)

#### ResultadoInfo

```python
class ResultadoInfo(BaseModel):
    metodo: Optional[str]                    # Método realizado
    resultado_macro: Optional[str]           # Descripción macroscópica
    resultado_micro: Optional[str]           # Descripción microscópica
    diagnostico: Optional[str]               # Diagnóstico final (texto libre)
    diagnostico_cie10: Optional[DiagnosticoCIE10]  # Diagnóstico CIE-10 estructurado
    diagnostico_cieo: Optional[DiagnosticoCIEO]    # Diagnóstico CIEO estructurado
    observaciones: Optional[str]             # Observaciones adicionales
    fecha_resultado: Optional[datetime]      # Fecha del resultado
    firmado: bool                            # Si el resultado está firmado
    fecha_firma: Optional[datetime]          # Fecha de firma
```

## Endpoints Disponibles

### Gestión de Resultados

#### Obtener Resultado

```http
GET /api/v1/casos/caso-code/{CasoCode}/resultado
```

**Respuesta:**
 
```json
{
  "metodo": "Histopatología",
  "resultado_macro": "Muestra de tejido del labio superior",
  "resultado_micro": "Presencia de células neoplásicas",
  "diagnostico": "Carcinoma del labio superior",
  "diagnostico_cie10": {
    "id": "68a87f6f77c035944761c564",
    "codigo": "A000",
    "nombre": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE"
  },
  "diagnostico_cieo": {
    "id": "68a89325a8937355a92cc019",
    "codigo": "C000",
    "nombre": "Tumor maligno del labio superior, cara externa"
  },
  "observaciones": "Caso complejo que requiere seguimiento",
  "fecha_resultado": "2025-01-22T10:30:00Z",
  "firmado": true,
  "fecha_firma": "2025-01-22T15:45:00Z"
}
```

#### Crear/Actualizar Resultado

```http
PUT /api/v1/casos/caso-code/{CasoCode}/resultado
```

**Cuerpo de la petición:**
 
```json
{
  "metodo": "Histopatología",
  "resultado_macro": "Muestra de tejido del labio superior",
  "resultado_micro": "Presencia de células neoplásicas",
  "diagnostico": "Carcinoma del labio superior",
  "diagnostico_cie10": {
    "id": "68a87f6f77c035944761c564",
    "codigo": "A000",
    "nombre": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE"
  },
  "diagnostico_cieo": {
    "id": "68a89325a8937355a92cc019",
    "codigo": "C000",
    "nombre": "Tumor maligno del labio superior, cara externa"
  },
  "observaciones": "Caso complejo que requiere seguimiento"
}
```

#### Firmar Resultado

```http
POST /api/v1/casos/caso-code/{CasoCode}/resultado/firmar
```

**Parámetros:**
- `patologo_codigo`: Código del patólogo que firma

## Casos de Uso

### 1. Crear Resultado con Diagnóstico CIE-10
```python
from app.modules.casos.models.caso import ResultadoInfo, DiagnosticoCIE10

# Crear diagnóstico CIE-10
diagnostico_cie10 = DiagnosticoCIE10(
    id="68a87f6f77c035944761c564",
    codigo="A000",
    nombre="COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE"
)

# Crear resultado
resultado = ResultadoInfo(
    metodo="Histopatología",
    resultado_macro="Muestra de tejido",
    resultado_micro="Presencia de bacterias",
    diagnostico="Cólera confirmado",
    diagnostico_cie10=diagnostico_cie10
)
```

### 2. Crear Resultado con Ambos Diagnósticos
```python
from app.modules.casos.models.caso import ResultadoInfo, DiagnosticoCIE10, DiagnosticoCIEO

# Diagnóstico CIE-10
diagnostico_cie10 = DiagnosticoCIE10(
    id="68a87f6f77c035944761c564",
    codigo="A000",
    nombre="COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE"
)

# Diagnóstico CIEO
diagnostico_cieo = DiagnosticoCIEO(
    id="68a89325a8937355a92cc019",
    codigo="C000",
    nombre="Tumor maligno del labio superior, cara externa"
)

# Resultado con ambos diagnósticos
resultado = ResultadoInfo(
    metodo="Histopatología",
    resultado_macro="Muestra de tejido del labio superior",
    resultado_micro="Presencia de células neoplásicas",
    diagnostico="Carcinoma del labio superior",
    diagnostico_cie10=diagnostico_cie10,
    diagnostico_cieo=diagnostico_cieo
)
```

### 3. Actualizar Solo Diagnóstico CIEO
```python
# Obtener resultado existente
resultado_existente = await caso_service.obtener_resultado_por_caso_code("2025-00001")

# Actualizar solo el diagnóstico CIEO
resultado_existente.diagnostico_cieo = DiagnosticoCIEO(
    id="68a89325a8937355a92cc019",
    codigo="C000",
    nombre="Tumor maligno del labio superior, cara externa"
)

# Guardar cambios
await caso_service.agregar_o_actualizar_resultado_por_caso_code(
    "2025-00001", 
    resultado_existente, 
    "usuario_id"
)
```

## Ventajas de los Nuevos Campos

### 1. **Estructuración de Datos**
- Los diagnósticos ahora tienen campos específicos para ID, código y nombre
- Facilita la búsqueda y filtrado por códigos de enfermedad
- Permite la validación de datos

### 2. **Compatibilidad con Frontend**
- El frontend puede mostrar códigos y nombres de manera estructurada
- Facilita la creación de reportes y estadísticas
- Permite la integración con sistemas externos

### 3. **Trazabilidad**
- Se mantiene el historial de qué enfermedades específicas fueron diagnosticadas
- Facilita la auditoría y seguimiento de casos
- Permite análisis epidemiológicos

### 4. **Flexibilidad**
- Se mantiene el campo `diagnostico` para texto libre
- Los nuevos campos son opcionales, no rompen la compatibilidad
- Permite migración gradual de casos existentes

## Migración de Datos Existentes

Los casos existentes que solo tienen el campo `diagnostico` (texto libre) seguirán funcionando normalmente. Los nuevos campos `diagnostico_cie10` y `diagnostico_cieo` son opcionales y se pueden agregar gradualmente.

## Validaciones

### DiagnosticoCIE10
- `id`: Debe ser un string válido
- `codigo`: Máximo 20 caracteres
- `nombre`: Máximo 500 caracteres

### DiagnosticoCIEO
- `id`: Debe ser un string válido
- `codigo`: Máximo 20 caracteres
- `nombre`: Máximo 500 caracteres

### ResultadoInfo
- Los campos de diagnóstico son opcionales
- Se puede tener solo CIE-10, solo CIEO, ambos, o ninguno
- El campo `diagnostico` (texto libre) sigue siendo opcional
