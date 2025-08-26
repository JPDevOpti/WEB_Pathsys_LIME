# Documentación del Módulo de Casos

## Arquitectura del Módulo

### Estructura del Módulo

El módulo de casos sigue una arquitectura en capas que separa las responsabilidades:

```
casos/
├── models/          # Modelos Pydantic para MongoDB
├── schemas/         # Esquemas de entrada/salida de la API
├── repositories/    # Capa de acceso a datos
├── services/        # Lógica de negocio
└── routes/          # Endpoints de la API
```

### Dependencias del Módulo

- **Módulo de Pruebas**: Para la gestión de pruebas médicas
- **Módulo de Auth**: Para autenticación y autorización
- **Shared**: Esquemas y utilidades comunes
- **Core**: Excepciones y dependencias del sistema

### Patrón de Diseño

- **Repository Pattern**: Abstrae el acceso a datos
- **Service Layer**: Contiene la lógica de negocio
- **DTO Pattern**: Separación entre modelos de datos y esquemas de API

## Configuración del Servidor

### Información del Servidor

- **URL Base**: `http://localhost:8000`
- **API Version**: `/api/v1`
- **Endpoint Base para Casos**: `http://localhost:8000/api/v1/casos`
- **Puerto por defecto**: 8000

## Estructura del Modelo

### Campos del Modelo Caso

```json
{
  "id": "string (ID único del caso)",
  "CasoCode": "string (formato YYYY-NNNNN, único)",
  "paciente": {
    "codigo": "string (código único del paciente)",
    "cedula": "string (máx 20 caracteres)",
    "nombre": "string (máx 200 caracteres)",
    "edad": "integer (0-150)",
    "sexo": "string (máx 20 caracteres)",
    "entidad_info": {
      "codigo": "string (código único de la entidad, máx 50 caracteres)",
      "nombre": "string (nombre de la entidad de salud, máx 200 caracteres)"
    },
    "tipo_atencion": "string (Ambulatorio, Hospitalizado - máx 50 caracteres)",
    "observaciones": "string (opcional, máx 1000 caracteres)",
    "fecha_actualizacion": "datetime"
  },
  "medico_solicitante": {
    "nombre": "string (máx 200 caracteres, opcional)"
  },
  "servicio": "string (servicio médico o especialidad, opcional, máx 100 caracteres)",
  "muestras": [
    {
      "region_cuerpo": "string (región anatómica)",
      "pruebas": [
        {
          "id": "string (ID único de la prueba)",
          "nombre": "string (nombre de la prueba)",
          "cantidad": "integer (cantidad solicitada, default: 1)"
        }
      ]
    }
  ],
  "estado": "string (En proceso, Por firmar, Por entregar, Completado, cancelado)",
  "fecha_creacion": "datetime",
  "fecha_firma": "datetime (opcional)",
  "fecha_entrega": "datetime (opcional)",
  "fecha_actualizacion": "datetime",
  "observaciones_generales": "string (opcional, máx 1000 caracteres)",
  "patologo_asignado": {
    "codigo": "string (código único del patólogo)",
    "nombre": "string (nombre completo del patólogo)"
  },
  "resultado": {
    "metodo": "string (método realizado, opcional)",
    "resultado_macro": "string (descripción macroscópica, opcional)",
    "resultado_micro": "string (descripción microscópica, opcional)",
    "diagnostico": "string (diagnóstico final, opcional)",
    "observaciones": "string (observaciones adicionales, opcional)",
    "fecha_resultado": "datetime (opcional)",
    "firmado": "boolean (default: false)",
    "fecha_firma": "datetime (opcional)"
  },
  "creado_por": "string (ID del usuario que creó el caso, opcional)",
  "actualizado_por": "string (ID del usuario que actualizó el caso, opcional)",
  "activo": "boolean (indica si el caso está activo, default: true)"
}
```

### Estados Disponibles

- `En proceso` - Caso en análisis (estado por defecto)
- `Por firmar` - Resultado completado, esperando firma
- `Por entregar` - Resultado firmado, esperando entrega
- `Completado` - Caso completado y entregado
- `cancelado` - Caso cancelado

### Campos Requeridos para Crear

- `paciente`: Información completa del paciente (código, cedula, nombre, edad, sexo, entidad_info, tipo_atencion)
- `muestras`: Al menos una muestra con sus pruebas
- **Nota**: El `CasoCode` se genera automáticamente si no se proporciona

### Validaciones Importantes

- **CasoCode**: Formato YYYY-NNNNN (ejemplo: 2025-00001), año entre 2020-2100
- **Edad del paciente**: Entre 0 y 150 años
- **Tipo de atención**: Solo "Ambulatorio" o "Hospitalizado"
- **Fecha de firma**: No puede ser anterior a la fecha de creación

## Endpoints de la API

### 1. GET http://localhost:8000/api/v1/casos/siguiente-consecutivo

**Consultar el siguiente código consecutivo disponible**

**Descripción**: Consulta el próximo código consecutivo sin consumirlo.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200):

```json
{
  "codigo_consecutivo": "2025-00003",
  "mensaje": "Este es el próximo código disponible. No se ha consumido."
}
```

### 2. POST http://localhost:8000/api/v1/casos/

**Crear nuevo caso con código automático**

**Descripción**: Crea un caso y genera automáticamente el código consecutivo.

**Autenticación**: Requerida

#### Ejemplo: Crear caso sin especificar código

```json
{
  "paciente": {
    "codigo": "PAC002",
    "cedula": "11223344",
    "nombre": "Ana Torres",
    "edad": 45,
    "sexo": "Femenino",
    "entidad_info": {
      "codigo": "EPS002",
      "nombre": "Coomeva EPS"
    },
    "tipo_atencion": "Ambulatorio",
    "observaciones": "Ingresa por dolor abdominal."
  },
  "medico_solicitante": {
    "nombre": "Dr. Luis Mendoza"
  },
  "servicio": "Patología",
  "muestras": [
    {
      "region_cuerpo": "Apéndice cecal",
      "pruebas": [
        {
          "id": "HIST005",
          "nombre": "Estudio histopatológico de apéndice",
          "cantidad": 2
        }
      ]
    }
  ],
  "estado": "En proceso",
  "observaciones_generales": "Caso urgente."
}
```

Respuesta (201):

```json
{
  "id": "507f1f77bcf86cd799439011",
  "CasoCode": "2025-00003",
  "paciente": {
    "codigo": "PAC002",
    "cedula": "11223344",
    "nombre": "Ana Torres",
    "edad": 45,
    "sexo": "Femenino",
    "entidad_info": {
      "codigo": "EPS002",
      "nombre": "Coomeva EPS"
    },
    "tipo_atencion": "Ambulatorio",
    "observaciones": "Ingresa por dolor abdominal.",
    "fecha_actualizacion": "2025-01-15T10:30:00.000Z"
  },
  "medico_solicitante": {
    "nombre": "Dr. Luis Mendoza"
  },
  "servicio": "Patología",
  "muestras": [
    {
      "region_cuerpo": "Apéndice cecal",
      "pruebas": [
        {
          "id": "HIST005",
          "nombre": "Estudio histopatológico de apéndice",
          "cantidad": 2
        }
      ]
    }
  ],
  "estado": "En proceso",
  "fecha_creacion": "2025-01-15T10:30:00Z",
  "fecha_firma": null,
  "fecha_entrega": null,
  "fecha_actualizacion": "2025-01-15T10:30:00Z",
  "observaciones_generales": "Caso urgente.",
  "patologo_asignado": null,
  "resultado": null,
  "creado_por": "sistema",
  "actualizado_por": "sistema",
  "activo": true
}
```

### 3. POST http://localhost:8000/api/v1/casos/con-codigo

**Crear nuevo caso con código específico**

**Descripción**: Crea un caso con un código específico proporcionado.

**Autenticación**: Requerida

#### Ejemplo: Crear caso con código específico

```json
{
  "CasoCode": "2025-00005",
  "paciente": {
    "codigo": "PAC003",
    "cedula": "55667788",
    "nombre": "Carlos Ruiz",
    "edad": 35,
    "sexo": "Masculino",
    "entidad_info": {
      "codigo": "EPS003",
      "nombre": "Sanitas EPS"
    },
    "tipo_atencion": "Hospitalizado"
  },
  "muestras": [
    {
      "region_cuerpo": "Piel brazo derecho",
      "pruebas": [
        {
          "id": "HIST001",
          "nombre": "Biopsia de piel",
          "cantidad": 1
        }
      ]
    }
  ]
}
```

Respuesta (201): (similar al endpoint anterior pero con el código especificado)

### 4. GET http://localhost:8000/api/v1/casos/

**Listar casos con filtros básicos**

**Descripción**: Lista casos con paginación y filtros básicos.

**Autenticación**: Requerida

URL con parámetros:

- `http://localhost:8000/api/v1/casos/` (todos los casos)
- `http://localhost:8000/api/v1/casos/?skip=0&limit=10` (paginación)
- `http://localhost:8000/api/v1/casos/?estado=En%20proceso&limit=20` (solo en proceso)

Parámetros de consulta:

- `skip`: Registros a omitir (default: 0, mínimo: 0)
- `limit`: Máximo registros (default: 100, rango: 1-1000)
- `estado`: Filtrar por estado (En proceso, Por firmar, Por entregar, Completado, cancelado)

Body: (sin body)

Respuesta (200):

```json
[
  {
    "id": "507f1f77bcf86cd799439011",
    "CasoCode": "2025-00002",
    "paciente": {
      "codigo": "PAC002",
      "cedula": "11223344",
      "nombre": "Ana Torres",
      "edad": 45,
      "sexo": "Femenino",
      "entidad_info": {
        "codigo": "EPS002",
        "nombre": "Coomeva EPS"
      },
      "tipo_atencion": "Ambulatorio",
      "fecha_actualizacion": "2025-01-15T10:30:00Z"
    },
    "estado": "En proceso",
    "fecha_creacion": "2025-01-15T10:30:00Z",
    "fecha_actualizacion": "2025-01-15T10:30:00Z",
    "muestras": [...],
    "activo": true
  }
]
```

### 5. POST http://localhost:8000/api/v1/casos/buscar

**Búsqueda avanzada de casos**

**Descripción**: Búsqueda avanzada con múltiples criterios y paginación.

**Autenticación**: Requerida

**Query Parameters**:

- `skip`: Registros a omitir (default: 0, mínimo: 0)
- `limit`: Máximo registros (default: 1000, rango: 1-5000)

Body:

```json
{
  "query": "Ana Torres",
  "CasoCode": "2025-00002",
  "estado": "En proceso",
  "paciente_cedula": "11223344",
  "paciente_nombre": "Ana",
  "medico_nombre": "Luis",
  "patologo_codigo": "PAT001",
  "fecha_ingreso_desde": "2025-01-01T00:00:00",
  "fecha_ingreso_hasta": "2025-12-31T23:59:59",
  "fecha_firma_desde": "2025-01-01T00:00:00",
  "fecha_firma_hasta": "2025-12-31T23:59:59",
  "solo_vencidos": false,
  "solo_sin_patologo": true,
  "solo_firmados": false
}
```

Respuesta (200): (array de casos que coinciden con los criterios de búsqueda)

### 6. GET http://localhost:8000/api/v1/casos/caso-code/{CasoCode}

**Obtener caso específico por código de caso**

**Descripción**: Obtiene un caso específico usando su código único.

**Autenticación**: Requerida

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/caso-code/2025-00002`
- `http://localhost:8000/api/v1/casos/caso-code/2025-00001`

Body: (sin body)

Respuesta (200): (caso completo con toda la información)
Respuesta (404): Si el caso no existe

### 7. GET http://localhost:8000/api/v1/casos/paciente/{numero_documento}

**Obtener casos por paciente**

**Descripción**: Obtiene todos los casos de un paciente específico por su documento.

**Autenticación**: Requerida

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/paciente/11223344`
- `http://localhost:8000/api/v1/casos/paciente/87654321`

Body: (sin body)

Respuesta (200): (array de casos del paciente)

### 8. GET http://localhost:8000/api/v1/casos/patologo/{patologo_codigo}

**Obtener casos por patólogo**

**Descripción**: Obtiene todos los casos asignados a un patólogo específico.

**Autenticación**: Requerida

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/patologo/PAT001`
- `http://localhost:8000/api/v1/casos/patologo/PAT002`

Body: (sin body)

Respuesta (200): (array de casos asignados al patólogo)

### 9. GET http://localhost:8000/api/v1/casos/estado/{estado}

**Obtener casos por estado**

**Descripción**: Obtiene todos los casos con un estado específico.

**Autenticación**: Requerida

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/estado/En%20proceso`
- `http://localhost:8000/api/v1/casos/estado/Por%20firmar`
- `http://localhost:8000/api/v1/casos/estado/Completado`

Body: (sin body)

Respuesta (200): (array de casos con el estado especificado)

### 10. GET http://localhost:8000/api/v1/casos/sin-patologo

**Obtener casos sin patólogo asignado**

**Descripción**: Obtiene todos los casos que no tienen patólogo asignado.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200): (array de casos sin patólogo)

### 11. GET http://localhost:8000/api/v1/casos/vencidos

**Obtener casos vencidos**

**Descripción**: Obtiene todos los casos que están vencidos según los criterios del sistema.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200): (array de casos vencidos)

### 12. GET http://localhost:8000/api/v1/casos/firmados

**Obtener casos con resultados firmados**

**Descripción**: Obtiene todos los casos que tienen resultados firmados.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200): (array de casos firmados)

## Endpoints de Gestión de Patólogos

### 13. PUT http://localhost:8000/api/v1/casos/caso-code/{CasoCode}/asignar-patologo

**Asignar patólogo a un caso**

**Descripción**: Asigna un patólogo específico a un caso.

**Autenticación**: Requerida

Body:

```json
{
  "codigo": "PAT001",
  "nombre": "Dra. Isabel Correa"
}
```

Respuesta (200): (caso actualizado con patólogo asignado)

### 14. DELETE http://localhost:8000/api/v1/casos/caso-code/{CasoCode}/desasignar-patologo

**Desasignar patólogo de un caso**

**Descripción**: Remueve la asignación de patólogo de un caso.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200): (caso actualizado sin patólogo asignado)

## Endpoints de Actualización de Casos

### 15. PUT http://localhost:8000/api/v1/casos/caso-code/{CasoCode}

**Actualizar caso completo**

**Descripción**: Endpoint único para todas las actualizaciones de casos.

**Autenticación**: Requerida

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/caso-code/2025-00002`
- `http://localhost:8000/api/v1/casos/caso-code/2025-00001`

#### Ejemplo 1: Asignar patólogo y cambiar estado

```json
{
  "patologo_asignado": {
    "codigo": "PAT001",
    "nombre": "Dra. Isabel Correa"
  },
  "estado": "En proceso"
}
```

#### Ejemplo 2: Agregar resultado

```json
{
  "resultado": {
    "metodo": "Histopatología",
    "diagnostico": "Adenocarcinoma de colon",
    "resultado_macro": "Fragmento de mucosa colónica de 3cm",
    "resultado_micro": "Se observa infiltración neoplásica",
    "observaciones": "Adenocarcinoma moderadamente diferenciado. Control oncológico recomendado"
  },
  "estado": "Por firmar"
}
```

#### Ejemplo 3: Firmar resultado

```json
{
  "resultado": {
    "firmado": true,
    "fecha_firma": "2025-01-15T16:00:00Z"
  },
  "estado": "Por entregar"
}
```

#### Ejemplo 4: Cambiar solo el estado

```json
{
  "estado": "Completado"
}
```

#### Ejemplo 5: Actualizar información del paciente

```json
{
  "paciente": {
    "codigo": "PAC002",
    "cedula": "11223344",
    "nombre": "Ana Torres Modificado",
    "edad": 46,
    "sexo": "Femenino",
    "entidad_info": {
      "codigo": "EPS002",
      "nombre": "Coomeva EPS"
    },
    "tipo_atencion": "Hospitalizado",
    "observaciones": "Información actualizada"
  }
}
```

Respuesta (200): (caso completo actualizado)

## Endpoints de Gestión de Resultados

### 16. GET http://localhost:8000/api/v1/casos/caso-code/{CasoCode}/resultado

**Obtener resultado del caso**

**Descripción**: Obtiene únicamente la información del resultado de un caso.

**Autenticación**: Requerida

Body: (sin body)

Respuesta (200):

```json
{
  "metodo": "Histopatología",
  "resultado_macro": "Fragmento de mucosa colónica de 3cm",
  "resultado_micro": "Se observa infiltración neoplásica",
  "diagnostico": "Adenocarcinoma de colon",
  "observaciones": "Adenocarcinoma moderadamente diferenciado",
  "fecha_resultado": "2025-01-15T14:00:00Z",
  "firmado": true,
  "fecha_firma": "2025-01-15T16:00:00Z"
}
```

### 17. PUT http://localhost:8000/api/v1/casos/caso-code/{CasoCode}/resultado

**Crear o actualizar resultado del caso**

**Descripción**: Crea o actualiza el resultado de un caso específico.

**Autenticación**: Requerida

Body:

```json
{
  "metodo": "Histopatología",
  "resultado_macro": "Fragmento de mucosa colónica de 3cm",
  "resultado_micro": "Se observa infiltración neoplásica",
  "diagnostico": "Adenocarcinoma de colon",
  "observaciones": "Adenocarcinoma moderadamente diferenciado"
}
```

Respuesta (200): (caso completo con resultado actualizado)

### 18. POST http://localhost:8000/api/v1/casos/caso-code/{CasoCode}/resultado/firmar

**Firmar resultado del caso**

**Descripción**: Firma el resultado de un caso con el código del patólogo.

**Autenticación**: Requerida

**Query Parameters**:

- `patologo_codigo`: Código del patólogo que firma (requerido)

Body: (sin body)

Respuesta (200): (caso completo con resultado firmado)

## Endpoints de Eliminación

### 19. DELETE http://localhost:8000/api/v1/casos/caso-code/{CasoCode}

**Eliminar caso (eliminación permanente)**

**Descripción**: Elimina permanentemente un caso del sistema.

**Autenticación**: Requerida
**Roles permitidos**: admin

Ejemplos de URL:

- `http://localhost:8000/api/v1/casos/caso-code/2025-00002`
- `http://localhost:8000/api/v1/casos/caso-code/2025-00001`

Body: (sin body)

Respuesta (200):

```json
{
  "message": "El caso 2025-00002 ha sido eliminado exitosamente",
  "caso_code": "2025-00002"
}
```

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

## Endpoints de Estadísticas

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

### 21. GET http://localhost:8000/api/v1/casos/estadisticas-muestras

**Obtener estadísticas de muestras**

**Descripción**: Obtiene estadísticas específicas sobre las muestras procesadas.

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

### 22. GET http://localhost:8000/api/v1/casos/casos-por-mes/{year}

**Obtener casos por mes para un año específico**

**Descripción**: Obtiene estadísticas mensuales de casos para un año determinado.

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

### 23. GET http://localhost:8000/api/v1/casos/estadisticas-oportunidad-mensual

**Obtener estadísticas de oportunidad mensual**

**Descripción**: Obtiene estadísticas de oportunidad del mes anterior comparado con el mes anterior a este.

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
