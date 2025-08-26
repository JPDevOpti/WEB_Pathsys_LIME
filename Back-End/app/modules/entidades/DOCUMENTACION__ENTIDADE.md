# Guía de Entidades - Postman

## Estructura del Modelo

### Campos del Modelo Entidad
```json
{
    "_id": "ObjectId MongoDB",
    "EntidadName": "string (nombre de la entidad)",
    "EntidadCode": "string (código único)",
    "observaciones": "string (descripción/comentarios)",
    "isActive": "boolean (estado activo/inactivo)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear
- `EntidadName`: Nombre de la entidad (2-200 caracteres)
- `EntidadCode`: Código único de la entidad (no puede repetirse)
- `observaciones`: Descripción o comentarios (opcional, máx 500 caracteres)
- `isActive`: Estado activo (true/false, por defecto: true)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/entidades/
**Crear nueva entidad**

Body:
```json
{
    "EntidadName": "Hospital Universitario San Vicente de Paúl",
    "EntidadCode": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "isActive": true
}
```

Respuesta (201):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "EntidadName": "Hospital Universitario San Vicente de Paúl",
    "EntidadCode": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/entidades/
**Listar entidades con filtros**

URL con parámetros:
- `http://localhost:8000/api/v1/entidades/` (solo entidades activas - por defecto)
- `http://localhost:8000/api/v1/entidades/?query=hospital` (buscar por término - solo activas)
- `http://localhost:8000/api/v1/entidades/?activo=true&limit=5` (filtrar activas explícitamente, límite 5)
- `http://localhost:8000/api/v1/entidades/?activo=false` (mostrar solo entidades desactivadas)
- `http://localhost:8000/api/v1/entidades/?query=clinica&activo=false` (buscar en desactivadas)

Parámetros de consulta:
- `query`: Término de búsqueda (opcional)
- `activo`: Filtrar por estado activo (opcional, por defecto: true)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

**⚠️ IMPORTANTE**: Por defecto solo se muestran entidades activas (`isActive: true`). Para ver desactivadas usar `activo=false`.

Body: (sin body)

Respuesta (200):
```json
{
    "entidades": [
        {
            "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "EntidadName": "Hospital Universitario San Vicente de Paúl",
            "EntidadCode": "HSVP001",
            "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
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

### 3. GET http://localhost:8000/api/v1/entidades/code/{code}
**Obtener entidad por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body: (sin body)

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "EntidadName": "Hospital Universitario San Vicente de Paúl",
    "EntidadCode": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/entidades/code/{code}
**Actualizar entidad por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body:
```json
{
    "EntidadName": "Hospital Universitario San Vicente de Paúl - Sede Principal",
    "observaciones": "Hospital universitario de alta complejidad con servicios ampliados"
}
```

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "EntidadName": "Hospital Universitario San Vicente de Paúl - Sede Principal",
    "EntidadCode": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad con servicios ampliados",
    "isActive": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/entidades/code/{code}
**Eliminar entidad por código (eliminación permanente)**

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body: (sin body)

Respuesta (204): (sin contenido)

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. PATCH http://localhost:8000/api/v1/entidades/code/{code}/toggle-active
**Cambiar estado activo/inactivo de una entidad**

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001/toggle-active`
- `http://localhost:8000/api/v1/entidades/code/PABLO001/toggle-active`

Body: (sin body)

Respuesta (204): (sin contenido)

**Funcionamiento**: 
- Si la entidad está activa (`isActive: true`) → la desactiva (`isActive: false`)
- Si la entidad está inactiva (`isActive: false`) → la activa (`isActive: true`)

## Casos de Error

### Código Duplicado (400)
```json
{
    "detail": "Ya existe una entidad con el código HSVP001"
}
```

### Entidad No Encontrada (404)
```json
{
    "detail": "Entidad no encontrada"
}
```

### Datos Inválidos (422)
```json
{
    "detail": [
        {
            "loc": ["body", "EntidadName"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "EntidadCode"],
            "msg": "field required",
            "type": "value_error.missing"
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

1. **Crear una nueva entidad**: POST con todos los campos requeridos
2. **Listar entidades activas**: GET sin parámetros (muestra solo activas por defecto)
3. **Buscar entidades activas**: GET con parámetro `query` (busca solo en activas por defecto)
4. **Ver entidades desactivadas**: GET con `activo=false` para mostrar solo entidades desactivadas
5. **Buscar en desactivadas**: GET con `query` y `activo=false` para buscar en entidades desactivadas
6. **Obtener entidad específica**: GET `/code/{codigo}` para obtener una entidad por su código
7. **Actualizar información**: PUT `/code/{codigo}` con los campos a modificar
8. **Cambiar estado**: PATCH `/code/{codigo}/toggle-active` para alternar entre activo/inactivo
9. **Eliminar entidad**: DELETE `/code/{codigo}` para eliminación permanente (no se puede deshacer)

## Ejemplos de Códigos de Entidades

### Hospitales
- `HSVP001` - Hospital Universitario San Vicente de Paúl
- `PABLO001` - Hospital Pablo Tobón Uribe
- `HGMED001` - Hospital General de Medellín

### Clínicas
- `CARDIO001` - Clínica Cardiovascular Santa María
- `VID001` - Clínica VID - Fundación Santa María
- `AMERICAS001` - Clínica Las Américas

### Laboratorios
- `PROLAB001` - ProLab S.A.S
- `PATSUESC001` - Patología Suescún S.A.S
- `PATINTE001` - Patología Integral S.A

### EPS y Aseguradoras
- `SURA001` - Sura
- `SANITAS001` - Sanitas
- `NUEVAEPS001` - Nueva EPS
- `COOMEVA001` - Coomeva

### Centros Especializados
- `CENTROHS001` - Centros Especializados HSVF Rionegro
- `NEURO001` - Neurocentro - Pereira
- `RENALES001` - Renales IPS Clínica León XIII

### Especiales
- `PARTICULAR` - Particular (pacientes privados)
- `INVEST001` - Investigación (estudios médicos)
- `AMBULAT001` - Hospitales Ambulatorios (red de atención primaria) 