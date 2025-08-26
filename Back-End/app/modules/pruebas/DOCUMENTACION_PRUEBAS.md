# Guía de Pruebas - Postman

## Estructura del Modelo

### Campos del Modelo Prueba
```json
{
    "_id": "ObjectId MongoDB",
    "pruebasName": "string (nombre de la prueba)",
    "pruebaCode": "string (código único)",
    "pruebasDescription": "string (descripción)",
    "tiempo": "int (tiempo en minutos)",
    "isActive": "boolean (estado activo/inactivo)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear
- `pruebasName`: Nombre de la prueba
- `pruebaCode`: Código único (no puede repetirse)
- `pruebasDescription`: Descripción de la prueba
- `tiempo`: Tiempo estimado en minutos (debe ser > 0)
- `isActive`: Estado activo (true/false)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/pruebas/
**Crear nueva prueba**

Body:
```json
{
    "pruebasName": "Hemoglobina",
    "pruebaCode": "HB001",
    "pruebasDescription": "Análisis de hemoglobina en sangre",
    "tiempo": 30,
    "isActive": true
}
```

Respuesta (201):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "pruebasName": "Hemoglobina",
    "pruebaCode": "HB001", 
    "pruebasDescription": "Análisis de hemoglobina en sangre",
    "tiempo": 30,
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/pruebas/
**Listar pruebas con filtros**

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

**⚠️ IMPORTANTE**: Por defecto solo se muestran pruebas activas (`isActive: true`). Para ver desactivadas usar `activo=false`.

Body: (sin body)

Respuesta (200):
```json
{
    "pruebas": [
        {
            "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "pruebasName": "Hemoglobina",
            "pruebaCode": "HB001",
            "pruebasDescription": "Análisis de hemoglobina en sangre",
            "tiempo": 30,
            "isActive": true,
            "fecha_creacion": "2023-09-07T10:30:00Z"
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

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body: (sin body)

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "pruebasName": "Hemoglobina",
    "pruebaCode": "HB001",
    "pruebasDescription": "Análisis de hemoglobina en sangre", 
    "tiempo": 30,
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/pruebas/code/{code}
**Actualizar prueba por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body:
```json
{
    "pruebasName": "Hemoglobina Actualizada",
    "tiempo": 45,
    "pruebasDescription": "Análisis completo de hemoglobina"
}
```

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "pruebasName": "Hemoglobina Actualizada",
    "pruebaCode": "HB001",
    "pruebasDescription": "Análisis completo de hemoglobina",
    "tiempo": 45,
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/pruebas/code/{code}
**Eliminar prueba por código (eliminación permanente)**

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001`

Body: (sin body)

Respuesta (204): (sin contenido)

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. PATCH http://localhost:8000/api/v1/pruebas/code/{code}/toggle-active
**Cambiar estado activo/inactivo de una prueba**

Ejemplos de URL:
- `http://localhost:8000/api/v1/pruebas/code/HB001/toggle-active`
- `http://localhost:8000/api/v1/pruebas/code/INMUNO001/toggle-active`

Body: (sin body)

Respuesta (204): (sin contenido)

**Funcionamiento**: 
- Si la prueba está activa (`isActive: true`) → la desactiva (`isActive: false`)
- Si la prueba está inactiva (`isActive: false`) → la activa (`isActive: true`)

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
            "loc": ["body", "pruebasName"],
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