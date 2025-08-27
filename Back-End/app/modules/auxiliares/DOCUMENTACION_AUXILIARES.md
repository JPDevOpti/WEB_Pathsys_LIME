# Documentación del Módulo de Auxiliares

## ⚠️ IMPORTANTE: MÓDULO CON AUTENTICACIÓN
**Este módulo SÍ requiere autenticación.** Los auxiliares son usuarios del sistema con rol "auxiliar" y tienen acceso a funcionalidades específicas según su nivel de permisos.

## Estructura del Modelo

### Campos del Modelo Auxiliar
```json
{
    "_id": "ObjectId MongoDB",
    "auxiliar_name": "string (nombre completo del auxiliar)",
    "auxiliar_code": "string (código único del auxiliar)",
    "auxiliar_email": "string (email único)",
    "is_active": "boolean (estado activo/inactivo)",
    "observaciones": "string (notas adicionales, opcional)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Estados Disponibles
- `true` - Auxiliar activo y disponible
- `false` - Auxiliar inactivo

### Campos Requeridos para Crear
- `auxiliar_name`: Nombre completo del auxiliar (2-200 caracteres)
- `auxiliar_code`: Código único del auxiliar (8-20 caracteres)
- `auxiliar_email`: Email único válido
- `password`: Contraseña para el usuario del sistema (6-128 caracteres)
- `is_active`: Estado activo (true/false, por defecto: true)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/auxiliares/
**Crear nuevo auxiliar**

Body:
```json
{
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez@hospital.com",
    "password": "contraseña123",
    "is_active": true,
    "observaciones": "Auxiliar de laboratorio con 5 años de experiencia"
}
```

Response 201:
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez@hospital.com",
    "is_active": true,
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
- `http://localhost:8000/api/v1/auxiliares/?is_active=true&limit=20` (solo activos)
- `http://localhost:8000/api/v1/auxiliares/?auxiliar_name=María` (filtrar por nombre)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)
- `auxiliar_name`: Filtrar por nombre (búsqueda parcial)
- `auxiliar_code`: Filtrar por código exacto
- `auxiliar_email`: Filtrar por email exacto
- `is_active`: Filtrar por estado (true/false)

Body: (sin body)

Respuesta (200):
```json
{
    "auxiliares": [
        {
            "_id": "507f1f77bcf86cd799439011",
            "auxiliar_name": "María Elena González Pérez",
            "auxiliar_code": "87654321",
            "auxiliar_email": "maria.gonzalez@hospital.com",
            "is_active": true,
            "observaciones": "Auxiliar de laboratorio con 5 años de experiencia",
            "fecha_creacion": "2024-01-15T10:30:00Z",
            "fecha_actualizacion": "2024-01-15T10:30:00Z"
        }
    ],
    "total": 1,
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
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez@hospital.com",
    "is_active": true,
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
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez.nuevo@hospital.com",
    "is_active": true,
    "observaciones": "Auxiliar con email actualizado"
}
```

Respuesta (200):
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez.nuevo@hospital.com",
    "is_active": true,
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

Respuesta (200): 
```json
{
    "message": "Auxiliar con código 87654321 ha sido eliminado correctamente"
}
```

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
- `is_active`: Filtrar por estado (opcional)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200): (similar al endpoint GET principal)

### 7. PATCH http://localhost:8000/api/v1/auxiliares/{auxiliar_code}/estado
**Cambiar estado activo/inactivo por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/auxiliares/87654321/estado`
- `http://localhost:8000/api/v1/auxiliares/12345678/estado`

Body:
```json
{
    "is_active": false
}
```

Respuesta (200):
```json
{
    "_id": "507f1f77bcf86cd799439011",
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez@hospital.com",
    "is_active": false,
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
            "loc": ["body", "auxiliar_name"],
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
- `auxiliar_code`: Debe ser único en todo el sistema
- `auxiliar_email`: Debe ser único en todo el sistema

### Reglas de Validación

1. **auxiliar_name**: 2-200 caracteres, solo letras, espacios y acentos
2. **auxiliar_code**: 8-20 caracteres alfanuméricos, único en el sistema
3. **auxiliar_email**: Formato de email válido, único en el sistema
4. **password**: 6-128 caracteres (requerido para crear usuario)
5. **observaciones**: Máximo 500 caracteres (opcional)
6. **is_active**: Valor booleano (true/false)

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

4. **Gestión de Usuarios del Sistema**
   - Creación automática de usuarios con rol "auxiliar"
   - Sincronización entre colecciones auxiliares y usuarios
   - Gestión de contraseñas y acceso al sistema

## Notas Importantes

1. **Eliminación Permanente**: Los auxiliares eliminados se borran físicamente de la base de datos y no se pueden recuperar
2. **Códigos Únicos**: El sistema valida que no existan códigos duplicados
3. **Emails Únicos**: Cada auxiliar debe tener un email único
4. **Fechas**: Las fechas se manejan automáticamente por el sistema
5. **Búsquedas**: Las búsquedas por nombre son parciales (case-insensitive)
6. **Paginación**: Todos los listados soportan paginación con skip/limit
7. **Autenticación**: Este módulo requiere autenticación y crea usuarios del sistema
8. **Sincronización**: Los cambios se sincronizan automáticamente entre las colecciones auxiliares y usuarios

## Ejemplos de Integración

### 1. Crear un auxiliar
```bash
curl -X POST "http://localhost:8000/api/v1/auxiliares/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez@hospital.com",
    "password": "contraseña123",
    "observaciones": "Auxiliar de laboratorio con 5 años de experiencia"
  }'
```

### 2. Listar todos los auxiliares con paginación
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/?skip=0&limit=5"
```

### 3. Buscar auxiliares por nombre
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/?auxiliar_name=María&is_active=true"
```

### 4. Búsqueda avanzada
```bash
# Buscar por término general
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?q=laboratorio&limit=10"

# Buscar por código específico
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?q=87654321"

# Buscar solo auxiliares activos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?q=maría&is_active=true"
```

### 5. Obtener auxiliar específico por código
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/87654321"
```

### 6. Actualizar auxiliar completo
```bash
curl -X PUT "http://localhost:8000/api/v1/auxiliares/87654321" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "María Elena González Pérez",
    "auxiliar_code": "87654321",
    "auxiliar_email": "maria.gonzalez.nuevo@hospital.com",
    "observaciones": "Auxiliar con email actualizado y mayor experiencia"
  }'
```

### 7. Cambiar estado del auxiliar
```bash
# Desactivar auxiliar
curl -X PATCH "http://localhost:8000/api/v1/auxiliares/87654321/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": false}'

# Reactivar auxiliar
curl -X PATCH "http://localhost:8000/api/v1/auxiliares/87654321/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": true}'
```

### 8. Eliminar auxiliar (permanente)
```bash
curl -X DELETE -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/87654321"
# Respuesta: 200 OK con mensaje de confirmación
# ⚠️ ADVERTENCIA: Esta operación es irreversible
```

### 9. Ejemplo de flujo completo
```bash
# 1. Crear auxiliar
AUXILIAR_ID=$(curl -s -X POST "http://localhost:8000/api/v1/auxiliares/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "Ana María Rodríguez",
    "auxiliar_code": "12345678",
    "auxiliar_email": "ana.rodriguez@hospital.com",
    "password": "contraseña123",
    "observaciones": "Especialista en análisis de sangre"
  }' | jq -r '._id')

# 2. Verificar creación
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/12345678"

# 3. Actualizar información
curl -X PUT "http://localhost:8000/api/v1/auxiliares/12345678" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "Ana María Rodríguez López",
    "auxiliar_code": "12345678",
    "auxiliar_email": "ana.rodriguez@hospital.com",
    "observaciones": "Especialista en análisis de sangre y microbiología"
  }'

# 4. Desactivar temporalmente
curl -X PATCH "http://localhost:8000/api/v1/auxiliares/12345678/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": false}'
```