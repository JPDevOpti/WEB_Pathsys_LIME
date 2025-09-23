# Documentación del Módulo de Pacientes

## Arquitectura del Módulo

### Estructura del Módulo
El módulo de pacientes sigue una arquitectura en capas que separa las responsabilidades:

```
pacientes/
├── models/          # Modelos Pydantic para MongoDB
├── schemas/         # Esquemas de entrada/salida de la API
├── repositories/    # Capa de acceso a datos
├── services/        # Lógica de negocio
└── routes/          # Endpoints de la API
```

### Dependencias del Módulo
- **Módulo de Casos**: Para la gestión de casos asociados
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
- **Endpoint Base para Pacientes**: `http://localhost:8000/api/v1/pacientes`
- **Puerto por defecto**: 8000

### Iniciar el Servidor
```bash
cd Back-End
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Estructura del Modelo

### Campos del Modelo Paciente
```json
{
    "id": "string (ID automático de MongoDB)",
    "paciente_code": "string (código único del paciente, 6-12 dígitos)",
    "nombre": "string (2-200 caracteres)",
    "edad": "integer (0-150)",
    "sexo": "string (Masculino, Femenino)",
    "entidad_info": {
        "id": "string (ID único de la entidad)",
        "nombre": "string (nombre de la entidad de salud)"
    },
    "tipo_atencion": "string (Ambulatorio, Hospitalizado)",
    "observaciones": "string (opcional, máx 500 caracteres)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear
- `paciente_code`: Código único del paciente (6-12 dígitos)
- `nombre`: Nombre completo del paciente
- `edad`: Edad del paciente (0-150 años)
- `sexo`: Género del paciente
- `entidad_info`: Información de la entidad de salud
- `tipo_atencion`: Tipo de atención médica

### Campos Opcionales
- `observaciones`: Observaciones adicionales del paciente

## Endpoints de la API

### 1. POST http://localhost:8000/api/v1/pacientes/
**Crear nuevo paciente**

**Autenticación**: Requerida  
**Roles permitidos**: admin, auxiliar

#### Ejemplo: Crear paciente básico
```json
{
  "paciente_code": "12345678",
  "nombre": "Juan Carlos Pérez",
  "edad": 35,
  "sexo": "Masculino",
  "entidad_info": {
    "id": "ent_001",
    "nombre": "EPS Sanitas"
  },
  "tipo_atencion": "Ambulatorio",
  "observaciones": "Paciente con antecedentes de hipertensión"
}
```

#### Ejemplo: Crear paciente mínimo
```json
{
  "paciente_code": "87654321",
  "nombre": "María González",
  "edad": 28,
  "sexo": "Femenino",
  "entidad_info": {
    "id": "ent_002",
    "nombre": "Sura"
  },
  "tipo_atencion": "Hospitalizado"
}
```

Respuesta (201):
```json
{
  "id": "64f8a1b2c3d4e5f6a7b8c9d0",
  "paciente_code": "12345678",
  "nombre": "Juan Carlos Pérez",
  "edad": 35,
  "sexo": "Masculino",
  "entidad_info": {
    "id": "ent_001",
    "nombre": "EPS Sanitas"
  },
  "tipo_atencion": "Ambulatorio",
  "observaciones": "Paciente con antecedentes de hipertensión",
  "fecha_creacion": "2024-01-15T10:30:00.000Z",
  "fecha_actualizacion": "2024-01-15T10:30:00.000Z"
}
```

### 2. GET http://localhost:8000/api/v1/pacientes/
**Listar pacientes con filtros**

**Autenticación**: Requerida  
**Roles permitidos**: admin, patologo, auxiliar

URL con parámetros:
- `http://localhost:8000/api/v1/pacientes/` (todos los pacientes)
- `http://localhost:8000/api/v1/pacientes/?skip=0&limit=10` (paginación)
- `http://localhost:8000/api/v1/pacientes/?sexo=Masculino&limit=20` (solo masculinos)
- `http://localhost:8000/api/v1/pacientes/?entidad=Sanitas` (por entidad)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 100, max: 1000)
- `buscar`: Buscar por nombre o código
- `entidad`: Filtrar por nombre de entidad
- `sexo`: Filtrar por sexo (Masculino, Femenino)
- `tipo_atencion`: Filtrar por tipo (Ambulatorio, Hospitalizado)

Respuesta (200):
```json
[
  {
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "paciente_code": "12345678",
    "nombre": "Juan Carlos Pérez",
    "edad": 35,
    "sexo": "Masculino",
    "entidad_info": {
      "id": "ent_001",
      "nombre": "EPS Sanitas"
    },
    "tipo_atencion": "Ambulatorio",
    "observaciones": "Paciente con antecedentes de hipertensión",
    "fecha_creacion": "2024-01-15T10:30:00.000Z",
    "fecha_actualizacion": "2024-01-15T10:30:00.000Z"
  }
]
```

### 3. GET http://localhost:8000/api/v1/pacientes/buscar/avanzada
**Búsqueda avanzada de pacientes**

**Autenticación**: Requerida  
**Roles permitidos**: admin, patologo, auxiliar

**Query Parameters**:
- `nombre`: Buscar por nombre del paciente
- `paciente_code`: Buscar por código del paciente
- `edad_min`: Edad mínima (0-150)
- `edad_max`: Edad máxima (0-150)
- `entidad`: Filtrar por entidad de salud
- `sexo`: Filtrar por sexo (Masculino, Femenino)
- `tipo_atencion`: Filtrar por tipo de atención
- `fecha_desde`: Fecha de creación desde (formato: YYYY-MM-DD)
- `fecha_hasta`: Fecha de creación hasta (formato: YYYY-MM-DD)
- `skip`: Registros a omitir para paginación
- `limit`: Límite de resultados (1-1000)

**Ejemplos de uso**:
```bash
# Buscar pacientes masculinos entre 30 y 50 años
GET /api/v1/pacientes/buscar/avanzada?sexo=Masculino&edad_min=30&edad_max=50

# Buscar pacientes de una entidad específica
GET /api/v1/pacientes/buscar/avanzada?entidad=Sanitas&limit=50

# Buscar pacientes creados en un rango de fechas
GET /api/v1/pacientes/buscar/avanzada?fecha_desde=2024-01-01&fecha_hasta=2024-01-31
```

Respuesta (200):
```json
{
  "pacientes": [
    {
      "id": "64f8a1b2c3d4e5f6a7b8c9d0",
      "paciente_code": "12345678",
      "nombre": "Juan Carlos Pérez",
      "edad": 35,
      "sexo": "Masculino",
      "entidad_info": {
        "id": "ent_001",
        "nombre": "EPS Sanitas"
      },
      "tipo_atencion": "Ambulatorio",
      "observaciones": "Paciente con antecedentes de hipertensión",
      "fecha_creacion": "2024-01-15T10:30:00.000Z",
      "fecha_actualizacion": "2024-01-15T10:30:00.000Z"
    }
  ],
  "total": 1,
  "skip": 0,
  "limit": 5
}
```

### 4. GET http://localhost:8000/api/v1/pacientes/{paciente_id}
**Obtener paciente por ID**

**Autenticación**: Requerida  
**Roles permitidos**: admin, patologo, auxiliar

Ejemplos de URL:
- `http://localhost:8000/api/v1/pacientes/64f8a1b2c3d4e5f6a7b8c9d0`
- `http://localhost:8000/api/v1/pacientes/64f8a1b2c3d4e5f6a7b8c9d1`

Respuesta (200): (paciente completo como en la respuesta de creación)

### 5. PUT http://localhost:8000/api/v1/pacientes/{paciente_id}
**Actualizar paciente**

**Autenticación**: Requerida  
**Roles permitidos**: admin, auxiliar

Ejemplos de URL:
- `http://localhost:8000/api/v1/pacientes/12345678`
- `http://localhost:8000/api/v1/pacientes/87654321`

#### Ejemplo: Actualización parcial
```json
{
  "edad": 36,
  "observaciones": "Paciente con hipertensión controlada"
}
```

#### Ejemplo: Actualización completa
```json
{
  "nombre": "Juan Carlos Pérez Rodríguez",
  "edad": 36,
  "sexo": "Masculino",
  "entidad_info": {
    "id": "ent_003",
    "nombre": "Nueva EPS"
  },
  "tipo_atencion": "Hospitalizado",
  "observaciones": "Paciente con hipertensión controlada y diabetes tipo 2"
}
```

Respuesta (200):
```json
{
  "id": "64f8a1b2c3d4e5f6a7b8c9d0",
  "paciente_code": "12345678",
  "nombre": "Juan Carlos Pérez Rodríguez",
  "edad": 36,
  "sexo": "Masculino",
  "entidad_info": {
    "id": "ent_003",
    "nombre": "Nueva EPS"
  },
  "tipo_atencion": "Hospitalizado",
  "observaciones": "Paciente con hipertensión controlada y diabetes tipo 2",
  "fecha_creacion": "2024-01-15T10:30:00.000Z",
  "fecha_actualizacion": "2024-01-15T11:15:00.000Z"
}
```

### 6. PUT http://localhost:8000/api/v1/pacientes/{paciente_id}/change-code
**Cambiar código del paciente**

**Autenticación**: Requerida  
**Roles permitidos**: admin, auxiliar

Ejemplos de URL:
- `http://localhost:8000/api/v1/pacientes/12345678/change-code?new_code=87654321`
- `http://localhost:8000/api/v1/pacientes/87654321/change-code?new_code=11223344`

Respuesta (200): (paciente actualizado con nuevo código)

### 7. DELETE http://localhost:8000/api/v1/pacientes/{paciente_id}
**Eliminar paciente**

**Autenticación**: Requerida  
**Roles permitidos**: admin

Ejemplos de URL:
- `http://localhost:8000/api/v1/pacientes/12345678`
- `http://localhost:8000/api/v1/pacientes/87654321`

Respuesta (200):
```json
{
  "message": "Paciente 12345678 eliminado exitosamente"
}
```

⚠️ **IMPORTANTE**: No se puede eliminar un paciente que tiene casos asociados. Primero debe eliminar o reasignar los casos.

### 8. GET http://localhost:8000/api/v1/pacientes/count
**Obtener total de pacientes**

**Autenticación**: Requerida  
**Roles permitidos**: admin, patologo, auxiliar

Respuesta (200):
```json
{
  "total": 150
}
```

### 9. GET http://localhost:8000/api/v1/pacientes/entidades/lista
**Listar entidades únicas**

**Autenticación**: Requerida  
**Roles permitidos**: admin, patologo, auxiliar

Respuesta (200):
```json
[
  "EPS Sanitas",
  "Sura",
  "Nueva EPS",
  "Medimás",
  "Coomeva"
]
```

## Valores de Enumeraciones

#### Sexo del Paciente
- `Masculino` - Paciente masculino
- `Femenino` - Paciente femenino

⚠️ **IMPORTANTE**: Los valores deben enviarse exactamente como se muestran (con mayúscula inicial).

#### Tipo de Atención
- `Ambulatorio` - Atención ambulatoria
- `Hospitalizado` - Paciente hospitalizado

⚠️ **IMPORTANTE**: Los valores deben enviarse exactamente como se muestran (con mayúscula inicial).

## Reglas de Validación

#### Campos Obligatorios
- **paciente_code**: Requerido, 6-12 dígitos, único en el sistema
- **nombre**: Requerido, 2-200 caracteres
- **edad**: Requerido, 0-150 años
- **sexo**: Requerido, "Masculino" o "Femenino"
- **entidad_info**: Requerido (objeto completo)
- **tipo_atencion**: Requerido, "Ambulatorio" o "Hospitalizado"

#### Validaciones Específicas
1. **paciente_code**: Se limpia automáticamente (solo números), debe ser único, 6-12 dígitos
2. **nombre**: Se capitaliza automáticamente, solo letras, espacios y acentos
3. **edad**: Número entero entre 0 y 150
4. **sexo**: Valores válidos: "Masculino", "Femenino"
5. **tipo_atencion**: Valores válidos: "Ambulatorio", "Hospitalizado"
6. **entidad_info.id**: Requerido cuando se proporciona entidad_info
7. **entidad_info.nombre**: Requerido cuando se proporciona entidad_info
8. **observaciones**: Opcional, máximo 500 caracteres

## Casos de Error Comunes

### 1. Código Duplicado (400 Bad Request)
```json
{
  "detail": "Ya existe un paciente con este código"
}
```

### 2. Datos Inválidos (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "edad"],
      "msg": "ensure this value is greater than or equal to 0",
      "type": "value_error.number.not_ge",
      "ctx": {"limit_value": 0}
    }
  ]
}
```

### 3. Campos Requeridos Faltantes (422 Unprocessable Entity)
```json
{
  "detail": [
    {
      "loc": ["body", "nombre"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

### 4. Paciente No Encontrado (404 Not Found)
```json
{
  "detail": "Paciente con ID 99999999 no encontrado"
}
```

### 5. Paciente con Casos No Puede Eliminarse (400 Bad Request)
```json
{
  "detail": "No se puede eliminar un paciente que tiene casos asociados. Primero debe eliminar o reasignar los casos."
}
```

### 6. Formato de Fecha Inválido en Búsqueda Avanzada (400 Bad Request)
```json
{
  "detail": "Formato de fecha inválido. Use YYYY-MM-DD"
}
```

### 7. Rango de Fechas Inválido (400 Bad Request)
```json
{
  "detail": "La fecha de inicio no puede ser posterior a la fecha de fin"
}
```

## Documentación Interactiva

Una vez que el servidor esté ejecutándose, puedes acceder a:
- **Swagger UI**: `http://localhost:8000/docs`
- **ReDoc**: `http://localhost:8000/redoc`

Estas interfaces proporcionan documentación interactiva y permiten probar los endpoints directamente desde el navegador.

## Notas Importantes

1. **Validación de Código**: El `paciente_code` se usa como identificador principal del paciente y debe ser único en el sistema
2. **Capitalización Automática**: Los nombres se capitalizan automáticamente
3. **Limpieza de Datos**: El código del paciente se limpia automáticamente removiendo caracteres no numéricos
4. **Campos Opcionales**: Solo "observaciones" es opcional en la creación
5. **Respuestas Consistentes**: Todas las respuestas incluyen timestamps
6. **Búsqueda Avanzada**: Endpoint especializado con múltiples filtros y paginación completa
7. **Filtros Flexibles**: Los endpoints de listado soportan múltiples filtros combinables
8. **Validación de Fechas**: Las fechas de búsqueda deben usar formato ISO (YYYY-MM-DD)
9. **Paginación**: Todos los endpoints de listado soportan paginación con skip/limit
10. **Entidades**: Sistema de gestión de entidades de salud separado del modelo de paciente
11. **Filtros de Entidad**: Los filtros de entidad buscan en el campo `entidad_info.nombre`

## Troubleshooting

### Si el servidor no inicia:
1. Verificar que MongoDB esté ejecutándose
2. Verificar las variables de entorno en `.env`
3. Verificar que el puerto 8000 no esté en uso

### Si hay errores de conexión:
1. Verificar la URL de MongoDB en la configuración
2. Verificar que la base de datos "lime_pathsys" exista
3. Verificar permisos de conexión a MongoDB