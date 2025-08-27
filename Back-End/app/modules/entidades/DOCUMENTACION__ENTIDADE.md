# Guía de Entidades - Postman

## ⚠️ IMPORTANTE: MÓDULO CON AUTENTICACIÓN
**Este módulo SÍ requiere autenticación.** Las entidades son elementos críticos del sistema y requieren permisos adecuados para su gestión.

## Estructura del Modelo

### Campos del Modelo Entidad
```json
{
    "_id": "ObjectId MongoDB",
    "entidad_name": "string (nombre de la entidad)",
    "entidad_code": "string (código único)",
    "observaciones": "string (descripción/comentarios)",
    "is_active": "boolean (estado activo/inactivo)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Campos Requeridos para Crear
- `entidad_name`: Nombre de la entidad (2-200 caracteres)
- `entidad_code`: Código único de la entidad (no puede repetirse)
- `observaciones`: Descripción o comentarios (opcional, máx 500 caracteres)
- `is_active`: Estado activo (true/false, por defecto: true)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/entidades/
**Crear nueva entidad**

**Autenticación:** ✅ Requerida

Body:
```json
{
    "entidad_name": "Hospital Universitario San Vicente de Paúl",
    "entidad_code": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "is_active": true
}
```

Respuesta (201):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "entidad_name": "Hospital Universitario San Vicente de Paúl",
    "entidad_code": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/entidades/
**Listar entidades con filtros**

**Autenticación:** ✅ Requerida

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

**⚠️ IMPORTANTE**: Por defecto solo se muestran entidades activas (`is_active: true`). Para ver desactivadas usar `activo=false`.

Body: (sin body)

Respuesta (200):
```json
{
    "entidades": [
        {
            "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "entidad_name": "Hospital Universitario San Vicente de Paúl",
            "entidad_code": "HSVP001",
            "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
            "is_active": true,
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

**Autenticación:** ✅ Requerida

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body: (sin body)

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "entidad_name": "Hospital Universitario San Vicente de Paúl",
    "entidad_code": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad especializado en atención médica integral",
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/entidades/code/{code}
**Actualizar entidad por código**

**Autenticación:** ✅ Requerida

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body:
```json
{
    "entidad_name": "Hospital Universitario San Vicente de Paúl - Sede Principal",
    "observaciones": "Hospital universitario de alta complejidad con servicios ampliados"
}
```

Respuesta (200):
```json
{
    "_id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "entidad_name": "Hospital Universitario San Vicente de Paúl - Sede Principal",
    "entidad_code": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad con servicios ampliados",
    "is_active": true,
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/entidades/code/{code}
**Eliminar entidad por código (eliminación permanente)**

**Autenticación:** ✅ Requerida

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001`
- `http://localhost:8000/api/v1/entidades/code/PABLO001`

Body: (sin body)

Respuesta (200): 
```json
{
    "message": "Entidad con código HSVP001 ha sido eliminada correctamente"
}
```

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. PATCH http://localhost:8000/api/v1/entidades/code/{code}/toggle-active
**Cambiar estado activo/inactivo de una entidad**

**Autenticación:** ✅ Requerida

Ejemplos de URL:
- `http://localhost:8000/api/v1/entidades/code/HSVP001/toggle-active`
- `http://localhost:8000/api/v1/entidades/code/PABLO001/toggle-active`

Body: (sin body)

Respuesta (200): 
```json
{
    "message": "Estado de entidad HSVP001 cambiado correctamente"
}
```

**Funcionamiento**: 
- Si la entidad está activa (`is_active: true`) → la desactiva (`is_active: false`)
- Si la entidad está inactiva (`is_active: false`) → la activa (`is_active: true`)

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
            "loc": ["body", "entidad_name"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "entidad_code"],
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

## Autenticación

**Todos los endpoints requieren el header:**
```
Authorization: Bearer YOUR_JWT_TOKEN
```

## Ejemplos de Integración

### 1. Crear entidad
```bash
curl -X POST "http://localhost:8000/api/v1/entidades/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "entidad_name": "Hospital Universitario San Vicente de Paúl",
    "entidad_code": "HSVP001",
    "observaciones": "Hospital universitario de alta complejidad",
    "is_active": true
  }'
```

### 2. Listar entidades activas
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/entidades/?skip=0&limit=10"
```

### 3. Buscar entidades
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/entidades/?query=hospital&activo=true"
```

### 4. Obtener entidad específica
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/entidades/code/HSVP001"
```

### 5. Actualizar entidad
```bash
curl -X PUT "http://localhost:8000/api/v1/entidades/code/HSVP001" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "entidad_name": "Hospital Universitario San Vicente de Paúl - Sede Principal",
    "observaciones": "Hospital con servicios ampliados"
  }'
```

### 6. Cambiar estado
```bash
curl -X PATCH "http://localhost:8000/api/v1/entidades/code/HSVP001/toggle-active" \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### 7. Eliminar entidad
```bash
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/entidades/code/HSVP001"
``` 