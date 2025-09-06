# Documentación del Módulo de Casos

## 1. Arquitectura de Archivos

```text
app/modules/casos/
├── models/
│   └── caso.py                 # Modelos MongoDB (Caso, ResultadoInfo, DiagnosticoCIE10/CIEO)
├── schemas/
│   └── caso.py                 # Esquemas Pydantic para API (Request/Response)
├── repositories/
│   ├── caso_repository.py      # Operaciones CRUD y consultas avanzadas
│   └── consecutivo_repository.py  # Gestión códigos consecutivos
├── services/
│   └── caso_service.py         # Lógica de negocio y transformaciones
├── routes/
│   └── caso_routes.py          # Endpoints FastAPI
└── DOCUMENTACION_CASOS.md      # Este archivo
```

### Capas y Responsabilidades

- **Models**: Definición de estructuras de datos para MongoDB
- **Schemas**: Validación y serialización para API REST
- **Repositories**: Acceso a datos y consultas complejas
- **Services**: Lógica de negocio, validaciones, transformaciones
- **Routes**: Definición de endpoints HTTP

---

## 2. Esquema Completo

### 2.1. Modelo Principal (`Caso`)

```json
{
  "_id": "ObjectId",
  "caso_code": "string (formato YYYY-NNNNN, ej: 2025-00001)",
  "paciente": {
    "paciente_code": "string (6-12 dígitos)",
    "nombre": "string (<=200 chars, capitalizado)",
    "edad": "number (0-150)",
    "sexo": "string (<=20 chars)",
    "entidad_info": {
      "id": "string (<=50 chars)",
      "nombre": "string (<=200 chars)"
    },
    "tipo_atencion": "string (Ambulatorio|Hospitalizado)",
    "observaciones": "string|null (<=1000 chars)",
    "fecha_actualizacion": "datetime"
  },
  "medico_solicitante": "string|null (<=200 chars)",
  "servicio": "string|null (<=100 chars)",
  "muestras": [
    {
      "region_cuerpo": "string",
      "pruebas": [
        {
          "id": "string",
          "nombre": "string",
          "cantidad": "number (default: 1)"
        }
      ]
    }
  ],
  "estado": "string (En proceso|Por firmar|Por entregar|Completado)",
  "prioridad": "string (Normal|Prioritario|Urgente, default: Normal)",
  "fecha_creacion": "datetime",
  "fecha_firma": "datetime|null",
  "fecha_entrega": "datetime|null",
  "fecha_actualizacion": "datetime",
  "patologo_asignado": {
    "codigo": "string",
    "nombre": "string"
  } | null,
  "resultado": {
    "metodo": "string|null",
    "resultado_macro": "string|null",
    "resultado_micro": "string|null",
    "diagnostico": "string|null",
    "diagnostico_cie10": {
      "codigo": "string (<=20 chars)",
      "nombre": "string (<=500 chars)"
    } | null,
    "diagnostico_cieo": {
      "codigo": "string (<=20 chars)",
      "nombre": "string (<=500 chars)"
    } | null,
    "observaciones": "string|null"
  } | null,
  "observaciones_generales": "string|null (<=1000 chars)",
  "ingresado_por": "string|null",
  "actualizado_por": "string|null"
}
```

### 2.2. Esquemas API

#### CasoResponse (GET requests)

```json
{
  "id": "string (ObjectId convertido)",
  "caso_code": "string",
  "paciente": {
    "paciente_code": "string",
    "nombre": "string",
    "edad": "number",
    "sexo": "string",
    "entidad_info": {
      "id": "string",
      "nombre": "string"
    },
    "tipo_atencion": "string",
    "observaciones": "string|null",
    "fecha_actualizacion": "datetime ISO"
  },
  "medico_solicitante": "string|null",
  "servicio": "string|null",
  "muestras": [
    {
      "region_cuerpo": "string",
      "pruebas": [
        {
          "id": "string",
          "nombre": "string",
          "cantidad": "number"
        }
      ]
    }
  ],
  "estado": "string",
  "prioridad": "string (Normal|Prioritario|Urgente)",
  "fecha_creacion": "datetime ISO",
  "fecha_firma": "datetime ISO|null",
  "fecha_entrega": "datetime ISO|null",
  "fecha_actualizacion": "datetime ISO",
  "patologo_asignado": {
    "codigo": "string",
    "nombre": "string"
  } | null,
  "resultado": {
    "metodo": "string|null",
    "resultado_macro": "string|null",
    "resultado_micro": "string|null",
    "diagnostico": "string|null",
    "diagnostico_cie10": {
      "codigo": "string",
      "nombre": "string"
    } | null,
    "diagnostico_cieo": {
      "codigo": "string",
      "nombre": "string"
    } | null,
    "observaciones": "string|null"
  } | null,
  "observaciones_generales": "string|null",
  "ingresado_por": "string|null",
  "actualizado_por": "string|null"
}
```

#### CasoCreateRequest (POST sin código)

```json
{
  "paciente": {
    "paciente_code": "string (requerido)",
    "nombre": "string (requerido)",
    "edad": "number (requerido)",
    "sexo": "string (requerido)",
    "entidad_info": {
      "id": "string (requerido)",
      "nombre": "string (requerido)"
    },
    "tipo_atencion": "string (requerido)",
    "observaciones": "string|null"
  },
  "medico_solicitante": "string|null (<=200 chars)",
  "servicio": "string|null",
  "muestras": [
    {
      "region_cuerpo": "string (requerido)",
      "pruebas": [
        {
          "id": "string (requerido)",
          "nombre": "string (requerido)",
          "cantidad": "number (default: 1)"
        }
      ]
    }
  ],
  "estado": "string (default: En proceso)",
  "prioridad": "string (Normal|Prioritario|Urgente, default: Normal)",
  "observaciones_generales": "string|null"
}
```

#### CasoCreateWithCode (POST con código específico)

```json
{
  "caso_code": "string (formato YYYY-NNNNN validado)",
  "paciente": {
    "paciente_code": "string",
    "nombre": "string",
    "edad": "number",
    "sexo": "string",
    "entidad_info": {
      "id": "string",
      "nombre": "string"
    },
    "tipo_atencion": "string",
    "observaciones": "string|null"
  },
  "medico_solicitante": "string|null (<=200 chars)",
  "servicio": "string|null",
  "muestras": [
    {
      "region_cuerpo": "string",
      "pruebas": [
        {
          "id": "string",
          "nombre": "string",
          "cantidad": "number"
        }
      ]
    }
  ],
  "estado": "string (default: En proceso)",
  "prioridad": "string (Normal|Prioritario|Urgente, default: Normal)",
  "observaciones_generales": "string|null"
}
```

#### ResultadoInfo (Resultado del caso)

```json
{
  "metodo": "string|null",
  "resultado_macro": "string|null",
  "resultado_micro": "string|null",
  "diagnostico": "string|null",
  "diagnostico_cie10": {
    "codigo": "string",
    "nombre": "string"
  } | null,
  "diagnostico_cieo": {
    "codigo": "string",
    "nombre": "string"
  } | null,
  "observaciones": "string|null"
}
```

---

## 3. Endpoints Completos

### 3.1. Gestión de Casos

#### GET `/api/v1/casos/{caso_code}`

**Descripción**: Obtener un caso específico por código  
**Parámetros**: `caso_code` (path)  
**Respuesta**: `CasoResponse`

#### GET `/api/v1/casos`

**Descripción**: Listar casos con filtros y paginación  
**Query Params**:

- `skip` (int, default: 0)
- `limit` (int, default: 100, max: 1000)
- `estado` (string, opcional)
- `prioridad` (string, opcional: Normal|Prioritario|Urgente)
- `patologo_codigo` (string, opcional)
- `fecha_desde` (datetime, opcional)
- `fecha_hasta` (datetime, opcional)

**Respuesta**: `Array<CasoResponse>`

#### POST `/api/v1/casos`

**Descripción**: Crear caso con código auto-generado  
**Body**: `CasoCreateRequest`  
**Respuesta**: `CasoResponse`

#### POST `/api/v1/casos/con-codigo`

**Descripción**: Crear caso con código específico  
**Body**: `CasoCreateWithCode`  
**Respuesta**: `CasoResponse`

#### PUT `/api/v1/casos/{caso_code}`

**Descripción**: Actualizar datos del caso  
**Parámetros**: `caso_code` (path)  
**Body**: `CasoUpdate` (campos opcionales)  
**Respuesta**: `CasoResponse`

#### DELETE `/api/v1/casos/{caso_code}`

**Descripción**: Eliminar caso  
**Parámetros**: `caso_code` (path)  
**Respuesta**: `{"message": "string", "caso_code": "string", "eliminado": true}`

### 3.2. Gestión de Patólogos

#### PUT `/api/v1/casos/{caso_code}/asignar-patologo`

**Descripción**: Asignar patólogo a un caso  
**Parámetros**: `caso_code` (path)  
**Body**: `PatologoInfo`

```json
{
  "codigo": "string",
  "nombre": "string"
}
```

**Respuesta**: `CasoResponse`

#### PUT `/api/v1/casos/{caso_code}/desasignar-patologo`

**Descripción**: Quitar patólogo asignado  
**Parámetros**: `caso_code` (path)  
**Respuesta**: `CasoResponse`

### 3.3. Gestión de Resultados

#### GET `/api/v1/casos/{caso_code}/resultado`

**Descripción**: Obtener resultado de un caso  
**Parámetros**: `caso_code` (path)  
**Respuesta**: `ResultadoInfo`

#### PUT `/api/v1/casos/{caso_code}/resultado`

**Descripción**: Crear o actualizar resultado  
**Parámetros**: `caso_code` (path)  
**Body**: `ResultadoInfo`  
**Respuesta**: `CasoResponse`

#### POST `/api/v1/casos/{caso_code}/resultado/firmar`

**Descripción**: Firmar resultado sin modificar diagnósticos  
**Parámetros**: `caso_code` (path)  
**Query Params**: `patologo_codigo` (string)  
**Respuesta**: `CasoResponse`

#### POST `/api/v1/casos/{caso_code}/resultado/firmar-con-diagnosticos`

**Descripción**: Firmar resultado y actualizar diagnósticos  
**Parámetros**: `caso_code` (path)  
**Query Params**: `patologo_codigo` (string)  
**Body**:

```json
{
  "diagnostico_cie10": {
    "codigo": "string",
    "nombre": "string"
  } | null,
  "diagnostico_cieo": {
    "codigo": "string",
    "nombre": "string"
  } | null
}
```

**Respuesta**: `CasoResponse`

### 3.4. Búsquedas Avanzadas

#### POST `/api/v1/casos/buscar`

**Descripción**: Búsqueda avanzada con múltiples criterios  
**Body**: `CasoSearch`

```json
{
  "query": "string|null (búsqueda general)",
  "caso_code": "string|null",
  "paciente_code": "string|null",
  "paciente_nombre": "string|null",
  "medico_nombre": "string|null",
  "patologo_codigo": "string|null",
  "estado": "EstadoCasoEnum|null",
  "prioridad": "PrioridadCasoEnum|null (Normal|Prioritario|Urgente)",
  "fecha_ingreso_desde": "datetime|null",
  "fecha_ingreso_hasta": "datetime|null",
  "fecha_firma_desde": "datetime|null",
  "fecha_firma_hasta": "datetime|null",
  "solo_vencidos": "boolean (default: false)",
  "solo_sin_patologo": "boolean (default: false)",
  "solo_firmados": "boolean (default: false)"
}
```

**Query Params**: `skip`, `limit`  
**Respuesta**: `Array<CasoResponse>`

#### GET `/api/v1/casos/paciente/{paciente_code}`

**Descripción**: Obtener todos los casos de un paciente  
**Parámetros**: `paciente_code` (path)  
**Respuesta**: `Array<CasoResponse>`

#### GET `/api/v1/casos/patologo/{patologo_codigo}`

**Descripción**: Obtener casos asignados a un patólogo  
**Parámetros**: `patologo_codigo` (path)  
**Query Params**: `skip`, `limit`  
**Respuesta**: `Array<CasoResponse>`

#### GET `/api/v1/casos/estado/{estado}`

**Descripción**: Obtener casos por estado  
**Parámetros**: `estado` (path)  
**Query Params**: `skip`, `limit`  
**Respuesta**: `Array<CasoResponse>`

#### GET `/api/v1/casos/sin-patologo`

**Descripción**: Obtener casos sin patólogo asignado  
**Query Params**: `skip`, `limit`  
**Respuesta**: `Array<CasoResponse>`

#### GET `/api/v1/casos/vencidos`

**Descripción**: Obtener casos vencidos (>15 días sin completar)  
**Respuesta**: `Array<CasoResponse>`

### 3.5. Estadísticas y Reportes

#### GET `/api/v1/casos/estadisticas`

**Descripción**: Estadísticas generales del sistema  
**Respuesta**: `CasoStats`

```json
{
  "total_casos": "number",
  "casos_en_proceso": "number",
  "casos_por_firmar": "number",
  "casos_por_entregar": "number",
  "casos_completados": "number",
  "casos_vencidos": "number",
  "casos_sin_patologo": "number",
  "tiempo_promedio_procesamiento": "number|null (días)",
  "casos_mes_actual": "number",
  "casos_mes_anterior": "number",
  "casos_semana_actual": "number",
  "cambio_porcentual": "number",
  "casos_por_patologo": "object",
  "casos_por_tipo_prueba": "object"
}
```

#### GET `/api/v1/casos/estadisticas-muestras`

**Descripción**: Estadísticas específicas de muestras  
**Respuesta**: `MuestraStats`

```json
{
  "total_muestras": "number",
  "muestras_mes_anterior": "number",
  "muestras_mes_anterior_anterior": "number",
  "cambio_porcentual": "number",
  "muestras_por_region": "object",
  "muestras_por_tipo_prueba": "object",
  "tiempo_promedio_procesamiento": "number"
}
```

#### GET `/api/v1/casos/casos-por-mes/{year}`

**Descripción**: Casos agrupados por mes del año  
**Parámetros**: `year` (path, range: 2020-2030)  
**Respuesta**:

```json
{
  "datos": "[number] (12 elementos, índices 0-11)",
  "total": "number",
  "año": "number"
}
```

#### GET `/api/v1/casos/estadisticas-oportunidad-mensual`

**Descripción**: Métricas de oportunidad del mes anterior  
**Respuesta**:

```json
{
  "porcentaje_oportunidad": "number",
  "cambio_porcentual": "number",
  "tiempo_promedio": "number",
  "casos_dentro_oportunidad": "number",
  "casos_fuera_oportunidad": "number",
  "total_casos_mes_anterior": "number",
  "mes_anterior": {
    "nombre": "string",
    "inicio": "datetime ISO",
    "fin": "datetime ISO"
  }
}
```

#### GET `/api/v1/casos/oportunidad-detalle`

**Descripción**: Detalle de oportunidad por pruebas y patólogos  
**Query Params**: `year` (optional), `month` (optional)  
**Respuesta**:

```json
{
  "pruebas": "[object] (estadísticas por tipo de prueba)",
  "patologos": "[object] (estadísticas por patólogo)",
  "resumen": {
    "total": "number",
    "dentro": "number",
    "fuera": "number"
  },
  "periodo": {
    "inicio": "datetime ISO",
    "fin": "datetime ISO"
  }
}
```

### 3.6. Utilidades

#### GET `/api/v1/casos/siguiente-consecutivo`

**Descripción**: Consultar próximo código consecutivo (sin consumir)  
**Respuesta**: `{"codigo": "string (YYYY-NNNNN)"}`

#### GET `/api/v1/casos/entidades-por-patologo/{patologo_codigo}`

**Descripción**: Entidades donde ha trabajado un patólogo  
**Parámetros**: `patologo_codigo` (path)  
**Query Params**: `year`, `month` (opcionales)  
**Respuesta**:

```json
{
  "patologo": "string",
  "entidades": "[object]",
  "total_entidades": "number",
  "periodo": {
    "month": "number|null",
    "year": "number|null",
    "filtrado": "boolean"
  }
}
```
