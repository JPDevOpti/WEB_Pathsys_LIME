# Guía de Pruebas - Postman

## ⚠️ **IMPORTANTE: AUTENTICACIÓN REQUERIDA**
Este módulo **SÍ requiere autenticación** para todas las operaciones. Incluye el header `Authorization: Bearer {token}` en todas las peticiones.

## Estructura del Modelo

### Campos del Modelo Prueba
```json
{
    "_id": "ObjectId MongoDB",
    "prueba_name": "string (nombre de la prueba)",
    "prueba_code": "string (código único)",
    "prueba_description": "string (descripción)",
    "tiempo": "int (tiempo en minutos)",
    "is_active": "boolean (estado activo/inactivo)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear
- `prueba_name`: Nombre de la prueba (2-200 caracteres)
- `prueba_code`: Código único (2-20 caracteres, no puede repetirse)
- `prueba_description`: Descripción de la prueba (opcional, max 500 caracteres)
- `tiempo`: Tiempo estimado en minutos (debe ser > 0 y ≤ 1440)
- `is_active`: Estado activo (true/false, por defecto: true)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/pruebas/
**Crear nueva prueba**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Body:
```json
{
    "prueba_name": "Hemoglobina",
    "prueba_code": "HB001",
    "prueba_description": "Análisis de hemoglobina en sangre",
    "tiempo": 30,
    "is_active": true
}
```

Respuesta (201):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "prueba_name": "Hemoglobina",
    "prueba_code": "HB001", 
    "prueba_description": "Análisis de hemoglobina en sangre",
    "tiempo": 30,
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": null
}
```

### 2. GET http://localhost:8000/api/v1/pruebas/
**Listar pruebas con filtros**

Headers:
```
Authorization: Bearer {token}
```

URL con parámetros:
- `http://localhost:8000/api/v1/pruebas/` (solo pruebas activas - por defecto)
- `http://localhost:8000/api/v1/pruebas/?query=hemoglobina` (buscar por término - solo activas)
- `http://localhost:8000/api/v1/pruebas/?activo=true&limit=5` (filtrar activas explícitamente, límite 5)
- `http://localhost:8000/api/v1/pruebas/?activo=false` (mostrar solo pruebas desactivadas)
- `http://localhost:8000/api/v1/pruebas/?query=inmuno&activo=false` (buscar en desactivadas)

Parámetros de consulta:
- `query`: Término de búsqueda (opcional)
- `activo`: Filtrar por estado activo (opcional, por defecto: true)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 1000)

**⚠️ IMPORTANTE**: Por defecto solo se muestran pruebas activas (`is_active: true`). Para ver desactivadas usar `activo=false`.

Body: (sin body)

Respuesta (200):
```json
{
    "pruebas": [
        {
            "id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "prueba_name": "Hemoglobina",
            "prueba_code": "HB001",
            "prueba_description": "Análisis de hemoglobina en sangre",
            "tiempo": 30,
            "is_active": true,
            "fecha_creacion": "2023-09-07T10:30:00Z",
            "fecha_actualizacion": null
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10,
    "has_next": false,
    "has_prev": false
}
```

### 3. GET http://localhost:8000/api/v1/pruebas/code/{code}
**Obtener prueba por código**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body: (sin body)

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "prueba_name": "Hemoglobina",
    "prueba_code": "HB001",
    "prueba_description": "Análisis de hemoglobina en sangre", 
    "tiempo": 30,
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": null
}
```

### 4. PUT http://localhost:8000/api/v1/pruebas/code/{code}
**Actualizar prueba por código**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body:
```json
{
    "prueba_name": "Hemoglobina Actualizada",
    "tiempo": 45,
    "prueba_description": "Análisis completo de hemoglobina"
}
```

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "prueba_name": "Hemoglobina Actualizada",
    "prueba_code": "HB001",
    "prueba_description": "Análisis completo de hemoglobina",
    "tiempo": 45,
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/pruebas/code/{code}
**Eliminar prueba por código (eliminación permanente)**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body: (sin body)

Respuesta (200):
```json
{
    "message": "Prueba eliminada exitosamente"
}
```

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. PATCH http://localhost:8000/api/v1/pruebas/code/{code}/toggle-active
**Cambiar estado activo/inactivo de una prueba**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001/toggle-active`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001/toggle-active`

Body: (sin body)

Respuesta (200):
```json
{
    "message": "Estado de la prueba cambiado exitosamente"
}
```

**Funcionamiento**: 
- Si la prueba está activa (`is_active: true`) → la desactiva (`is_active: false`)
- Si la prueba está inactiva (`is_active: false`) → la activa (`is_active: true`)

## Casos de Error

### Código Duplicado (400)
```json
{
    "detail": "Ya existe una prueba con el código HB001"
}
```

### Prueba No Encontrada (404)
```json
{
    "detail": "Prueba no encontrada"
}
```

### Datos Inválidos (422)
```json
{
    "detail": [
        {
            "loc": ["body", "prueba_name"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "tiempo"],
            "msg": "ensure this value is greater than 0",
            "type": "value_error.number.not_gt"
        }
    ]
}
```

### Error Interno (500)
```json
{
    "detail": "Error interno del servidor"
}
```

### No Autorizado (401)
```json
{
    "detail": "Not authenticated"
}
```

## Casos de Uso

1. **Crear una nueva prueba**: POST con todos los campos requeridos
2. **Listar pruebas activas**: GET sin parámetros (muestra solo activas por defecto)
3. **Buscar pruebas activas**: GET con parámetro `query` (busca solo en activas por defecto)
4. **Ver pruebas desactivadas**: GET con `activo=false` para mostrar solo pruebas desactivadas
5. **Buscar en desactivadas**: GET con `query` y `activo=false` para buscar en pruebas desactivadas
6. **Obtener prueba específica**: GET `/code/{codigo}` para obtener una prueba por su código
7. **Actualizar información**: PUT `/code/{codigo}` con los campos a modificar
8. **Cambiar estado**: PATCH `/code/{codigo}/toggle-active` para alternar entre activo/inactivo
9. **Eliminar prueba**: DELETE `/code/{codigo}` para eliminación permanente (no se puede deshacer)

## Validaciones

- **prueba_name**: 2-200 caracteres, no puede estar vacío
- **prueba_code**: 2-20 caracteres, no puede estar vacío, se convierte a mayúsculas
- **prueba_description**: Opcional, máximo 500 caracteres
- **tiempo**: Debe ser > 0 y ≤ 1440 minutos (24 horas)
- **is_active**: Boolean, por defecto true 