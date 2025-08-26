# Documentación del Módulo de Auxiliares

## ⚠️ IMPORTANTE: MÓDULO SIN AUTENTICACIÓN
**Este módulo NO requiere autenticación.** Todos los endpoints están disponibles sin necesidad de tokens de acceso o credenciales de usuario. Esto facilita las pruebas y la integración, pero debe considerarse la seguridad en entornos de producción.

## Estructura del Modelo

### Campos del Modelo Auxiliar
```json
{
    "_id": "ObjectId MongoDB",
    "auxiliarName": "string (nombre completo del auxiliar)",
    "auxiliarCode": "string (cédula única del auxiliar)",
    "AuxiliarEmail": "string (email único)",
    "isActive": "boolean (estado activo/inactivo)",
    "observaciones": "string (notas adicionales, opcional)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Estados Disponibles
- `true` - Auxiliar activo y disponible
- `false` - Auxiliar inactivo



### Campos Requeridos para Crear
- `auxiliarName`: Nombre completo del auxiliar (2-200 caracteres)
- `auxiliarCode`: Cédula única del auxiliar (8-20 caracteres)
- `AuxiliarEmail`: Email único válido
- `isActive`: Estado activo (true/false, por defecto: true)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/auxiliares/
**Crear nuevo auxiliar**

Body:
```json
{
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez@hospital.com",
    "isActive": true,
    "observaciones": "Auxiliar de laboratorio con 5 años de experiencia"
}
```

Response 201:
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez@hospital.com",
    "isActive": true,
    "observaciones": "Auxiliar de laboratorio con 5 años de experiencia",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/auxiliares/
**Listar auxiliares con filtros**

URL con parámetros:
- `http://localhost:8000/api/v1/auxiliares/` (todos los auxiliares)
- `http://localhost:8000/api/v1/auxiliares/?skip=0&limit=10` (paginación)
- `http://localhost:8000/api/v1/auxiliares/?isActive=true&limit=20` (solo activos)
- `http://localhost:8000/api/v1/auxiliares/?auxiliarName=María` (filtrar por nombre)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)
- `auxiliarName`: Filtrar por nombre (búsqueda parcial)
- `auxiliarCode`: Filtrar por código exacto
- `AuxiliarEmail`: Filtrar por email exacto
- `isActive`: Filtrar por estado (true/false)

Body: (sin body)

Respuesta (200):
```json
{
    "auxiliares": [
        {
            "_id": "507f1f77bcf86cd799439011",
            "auxiliarName": "María Elena González Pérez",
            "auxiliarCode": "87654321",
            "AuxiliarEmail": "maria.gonzalez@hospital.com",
            "isActive": true,
            "observaciones": "Auxiliar de laboratorio con 5 años de experiencia",
            "fecha_creacion": "2024-01-15T10:30:00Z",
            "fecha_actualizacion": "2024-01-15T10:30:00Z"
        },
        {
            "_id": "507f1f77bcf86cd799439012",
            "auxiliarName": "Ana María Rodríguez López",
            "auxiliarCode": "12345678",
            "AuxiliarEmail": "ana.rodriguez@hospital.com",
            "isActive": true,
            "observaciones": "Especialista en análisis de sangre",
            "fecha_creacion": "2024-01-15T11:00:00Z",
            "fecha_actualizacion": "2024-01-15T11:00:00Z"
        }
    ],
    "total": 2,
    "skip": 0,
    "limit": 10,
    "has_next": false,
    "has_prev": false
}
```

### 3. GET http://localhost:8000/api/v1/auxiliares/{auxiliar_code}
**Obtener auxiliar específico por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/auxiliares/87654321`
- `http://localhost:8000/api/v1/auxiliares/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez@hospital.com",
    "isActive": true,
    "observaciones": "Auxiliar de laboratorio",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T10:30:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/auxiliares/{auxiliar_code}
**Actualizar auxiliar por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/auxiliares/87654321`
- `http://localhost:8000/api/v1/auxiliares/12345678`

Body:
```json
{
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez.nuevo@hospital.com",
    "isActive": true,
    "observaciones": "Auxiliar con email actualizado"
}
```

Respuesta (200):
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez.nuevo@hospital.com",
    "isActive": true,
    "observaciones": "Auxiliar con email actualizado",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T14:45:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/auxiliares/{auxiliar_code}
**Eliminar auxiliar por código (eliminación permanente)**

Ejemplos de URL:
- `http://localhost:8000/api/v1/auxiliares/87654321`
- `http://localhost:8000/api/v1/auxiliares/12345678`

Body: (sin body)

Respuesta (204): (sin contenido)

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.



### 6. GET http://localhost:8000/api/v1/auxiliares/search
**Búsqueda avanzada de auxiliares**

URL con parámetros:
- `http://localhost:8000/api/v1/auxiliares/search?q=maría` (búsqueda general)
- `http://localhost:8000/api/v1/auxiliares/search?q=87654321` (búsqueda por código)
- `http://localhost:8000/api/v1/auxiliares/search?q=maria.gonzalez@hospital.com` (búsqueda por email)
- `http://localhost:8000/api/v1/auxiliares/search?q=laboratorio` (búsqueda en observaciones)

Parámetros de consulta:
- `q`: Término de búsqueda que busca en nombre, código, email y observaciones (opcional)
- `isActive`: Filtrar por estado (opcional)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200): (similar al endpoint GET principal)

### 6.2. PUT http://localhost:8000/api/v1/auxiliares/{auxiliar_code}/estado
**Cambiar estado activo/inactivo por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/auxiliares/87654321/estado`
- `http://localhost:8000/api/v1/auxiliares/12345678/estado`

Body:
```json
{
    "isActive": false
}
```

Respuesta (200):
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez@hospital.com",
    "isActive": false,
    "observaciones": "Auxiliar desactivado temporalmente",
    "fecha_creacion": "2024-01-15T10:30:00Z",
    "fecha_actualizacion": "2024-01-15T16:20:00Z"
}
```

## Códigos de Error

### 400 Bad Request
```json
{
    "detail": "Datos de entrada inválidos"
}
```

### 404 Not Found
```json
{
    "detail": "Auxiliar no encontrado"
}
```

### 409 Conflict
```json
{
    "detail": "El código de auxiliar ya existe"
}
```

### 422 Validation Error
```json
{
    "detail": [
        {
            "loc": ["body", "auxiliarName"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### 500 Internal Server Error
```json
{
    "detail": "Error interno del servidor"
}
```

## Validaciones

### Campos Únicos
- `auxiliarCode`: Debe ser único en todo el sistema
- `AuxiliarEmail`: Debe ser único en todo el sistema

### Reglas de Validación

1. **auxiliarName**: 2-200 caracteres, solo letras, espacios y acentos
2. **auxiliarCode**: 8-20 caracteres alfanuméricos, único en el sistema
3. **AuxiliarEmail**: Formato de email válido, único en el sistema
4. **observaciones**: Máximo 500 caracteres (opcional)
5. **isActive**: Valor booleano (true/false)

## Casos de Uso

1. **Gestión de Personal de Laboratorio**
   - Registro de nuevos auxiliares de laboratorio
   - Control de acceso por estado activo/inactivo
   - Mantenimiento de información básica del personal

2. **Control de Estado**
   - Activación/desactivación de auxiliares
   - Gestión de personal temporal o permanente
   - Mantenimiento de registros históricos

3. **Administración de Contactos**
   - Gestión de información de contacto
   - Actualización de datos personales
   - Seguimiento de cambios en la información

## Notas Importantes

1. **Eliminación Permanente**: Los auxiliares eliminados se borran físicamente de la base de datos y no se pueden recuperar
2. **Códigos Únicos**: El sistema valida que no existan códigos duplicados
3. **Emails Únicos**: Cada auxiliar debe tener un email único
4. **Fechas**: Las fechas se manejan automáticamente por el sistema
5. **Búsquedas**: Las búsquedas por nombre son parciales (case-insensitive)
6. **Paginación**: Todos los listados soportan paginación con skip/limit

## Ejemplos de Integración

### 1. Crear un auxiliar
```bash
curl -X POST "http://localhost:8000/api/v1/auxiliares/" \
  -H "Content-Type: application/json" \
  -d '{
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez@hospital.com",
    "observaciones": "Auxiliar de laboratorio con 5 años de experiencia"
  }'
```

### 2. Listar todos los auxiliares con paginación
```bash
curl "http://localhost:8000/api/v1/auxiliares/?skip=0&limit=5"
```

### 3. Buscar auxiliares por nombre
```bash
curl "http://localhost:8000/api/v1/auxiliares/?auxiliarName=María&isActive=true"
```

### 4. Búsqueda avanzada
```bash
# Buscar por término general
curl "http://localhost:8000/api/v1/auxiliares/search?q=laboratorio&limit=10"

# Buscar por código específico
curl "http://localhost:8000/api/v1/auxiliares/search?q=87654321"

# Buscar solo auxiliares activos
curl "http://localhost:8000/api/v1/auxiliares/search?q=maría&isActive=true"
```

### 5. Obtener auxiliar específico por código
```bash
curl "http://localhost:8000/api/v1/auxiliares/87654321"
```

### 6. Actualizar auxiliar completo
```bash
curl -X PUT "http://localhost:8000/api/v1/auxiliares/87654321" \
  -H "Content-Type: application/json" \
  -d '{
    "auxiliarName": "María Elena González Pérez",
    "auxiliarCode": "87654321",
    "AuxiliarEmail": "maria.gonzalez.nuevo@hospital.com",
    "observaciones": "Auxiliar con email actualizado y mayor experiencia"
  }'
```

### 7. Cambiar estado del auxiliar
```bash
# Desactivar auxiliar
curl -X PUT "http://localhost:8000/api/v1/auxiliares/87654321/estado" \
  -H "Content-Type: application/json" \
  -d '{"isActive": false}'

# Reactivar auxiliar
curl -X PUT "http://localhost:8000/api/v1/auxiliares/87654321/estado" \
  -H "Content-Type: application/json" \
  -d '{"isActive": true}'
```

### 8. Eliminar auxiliar (permanente)
```bash
curl -X DELETE "http://localhost:8000/api/v1/auxiliares/87654321"
# Respuesta: 204 No Content (sin cuerpo)
# ⚠️ ADVERTENCIA: Esta operación es irreversible
```

### 9. Ejemplo de flujo completo
```bash
# 1. Crear auxiliar
AUXILIAR_ID=$(curl -s -X POST "http://localhost:8000/api/v1/auxiliares/" \
  -H "Content-Type: application/json" \
  -d '{
    "auxiliarName": "Ana María Rodríguez",
    "auxiliarCode": "12345678",
    "AuxiliarEmail": "ana.rodriguez@hospital.com",
    "observaciones": "Especialista en análisis de sangre"
  }' | jq -r '._id')

# 2. Verificar creación
curl "http://localhost:8000/api/v1/auxiliares/12345678"

# 3. Actualizar información
curl -X PUT "http://localhost:8000/api/v1/auxiliares/12345678" \
  -H "Content-Type: application/json" \
  -d '{
    "auxiliarName": "Ana María Rodríguez López",
    "auxiliarCode": "12345678",
    "AuxiliarEmail": "ana.rodriguez@hospital.com",
    "observaciones": "Especialista en análisis de sangre y microbiología"
  }'

# 4. Desactivar temporalmente
curl -X PUT "http://localhost:8000/api/v1/auxiliares/12345678/estado" \
  -H "Content-Type: application/json" \
  -d '{"isActive": false}'
```