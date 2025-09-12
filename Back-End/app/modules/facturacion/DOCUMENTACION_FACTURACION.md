# Documentación del Módulo de Facturación

## 1. Arquitectura de Archivos

```text
app/modules/facturacion/
├── models/
│   └── facturacion.py                 # Modelos MongoDB (Facturacion)
├── schemas/
│   └── facturacion.py                 # Esquemas Pydantic para API (Request/Response)
├── repositories/
│   └── facturacion_repository.py      # Operaciones CRUD y consultas avanzadas
├── services/
│   └── facturacion_service.py         # Lógica de negocio y transformaciones
├── routes/
│   └── facturacion_routes.py          # Endpoints FastAPI
└── DOCUMENTACION_FACTURACION.md       # Este archivo
```

### Capas y Responsabilidades

- **Models**: Definición de estructuras de datos para MongoDB
- **Schemas**: Validación y serialización para API REST
- **Repositories**: Acceso a datos y consultas complejas
- **Services**: Lógica de negocio, validaciones, transformaciones, gestión de usuarios
- **Routes**: Definición de endpoints HTTP

## ⚠️ IMPORTANTE: MÓDULO CON AUTENTICACIÓN
**Este módulo SÍ requiere autenticación.** Los usuarios de facturación son usuarios del sistema con rol "facturacion" y tienen acceso a funcionalidades específicas según su nivel de permisos.

---

## 2. Esquema Completo

### 2.1. Modelo Principal (`Facturacion`)

```json
{
  "_id": "ObjectId",
  "facturacion_name": "string (<=200 chars, nombre completo del usuario de facturación)",
  "facturacion_code": "string (<=20 chars, código único del usuario de facturación)", 
  "facturacion_email": "string (email único válido)",
  "is_active": "boolean (estado activo/inactivo, default: true)",
  "observaciones": "string|null (<=500 chars, notas adicionales)",
  "fecha_creacion": "datetime",
  "fecha_actualizacion": "datetime"
}
```

### 2.2. Esquemas API

#### FacturacionResponse (GET requests)

```json
{
  "id": "string (ObjectId convertido)",
  "facturacion_name": "string",
  "facturacion_code": "string", 
  "facturacion_email": "string",
  "is_active": "boolean",
  "observaciones": "string",
  "fecha_creacion": "datetime ISO",
  "fecha_actualizacion": "datetime ISO"
}
```

#### FacturacionCreate (POST request)

```json
{
  "facturacion_name": "string (requerido, <=200 chars)",
  "facturacion_code": "string (requerido, <=20 chars, único)",
  "facturacion_email": "string (requerido, email válido, único)",
  "password": "string (requerido, <=128 chars, para usuario del sistema)",
  "is_active": "boolean (default: true)",
  "observaciones": "string|null (<=500 chars)"
}
```

#### FacturacionUpdate (PUT request)

```json
{
  "facturacion_name": "string|null (<=200 chars)",
  "facturacion_code": "string|null (<=20 chars)",
  "facturacion_email": "string|null (email válido)",
  "is_active": "boolean|null",
  "observaciones": "string|null (<=500 chars)",
  "password": "string|null (<=128 chars, opcional para cambio de contraseña)"
}
```

#### FacturacionSearch (Búsqueda avanzada)

```json
{
  "facturacion_name": "string|null (búsqueda parcial)",
  "facturacion_code": "string|null (búsqueda exacta)",
  "facturacion_email": "string|null (búsqueda exacta)",
  "is_active": "boolean|null (filtro por estado)"
}
```

#### FacturacionEstadoUpdate (PATCH estado)

```json
{
  "is_active": "boolean (requerido)"
}
```

### 2.3. Estados Disponibles

- `true` - Usuario de facturación activo y disponible para trabajar
- `false` - Usuario de facturación inactivo (temporalmente deshabilitado)

### 2.4. Validaciones y Restricciones

#### Campos Únicos
- `facturacion_code`: Debe ser único en todo el sistema
- `facturacion_email`: Debe ser único en todo el sistema

#### Reglas de Validación
- **facturacion_name**: 2-200 caracteres, solo letras, espacios y acentos
- **facturacion_code**: 8-20 caracteres alfanuméricos, único
- **facturacion_email**: Formato de email válido, único
- **password**: 6-128 caracteres (requerido para crear usuario)
- **observaciones**: Máximo 500 caracteres (opcional)
- **is_active**: Valor booleano (true/false)

---

## 3. Endpoints Completos

### 3.1. Gestión de Usuarios de Facturación

#### POST `/api/v1/facturacion/`

**Descripción**: Crear un nuevo usuario de facturación y usuario del sistema  
**Body**: `FacturacionCreate`  
**Respuesta**: `FacturacionResponse`

Body:
```json
{
  "facturacion_name": "María Elena González Pérez",
  "facturacion_code": "87654321",
  "facturacion_email": "maria.gonzalez@facturacion.com",
  "password": "contraseña123",
  "is_active": true,
  "observaciones": "Usuario de facturación con 5 años de experiencia"
}
```

Response 201:
```json
{
  "_id": "507f1f77bcf86cd799439011",
  "facturacion_name": "María Elena González Pérez",
  "facturacion_code": "87654321",
  "facturacion_email": "maria.gonzalez@facturacion.com",
  "is_active": true,
  "observaciones": "Usuario de facturación con 5 años de experiencia",
  "fecha_creacion": "2024-01-15T10:30:00Z",
  "fecha_actualizacion": "2024-01-15T10:30:00Z"
}
```

#### GET `/api/v1/facturacion/`

**Descripción**: Listar usuarios de facturación activos con paginación y filtros  
**Query Params**:

- `skip` (int, default: 0) - Registros a omitir
- `limit` (int, default: 10, max: 100) - Máximo registros a devolver
- `facturacion_name` (string, opcional) - Filtrar por nombre (búsqueda parcial)
- `facturacion_code` (string, opcional) - Filtrar por código exacto
- `facturacion_email` (string, opcional) - Filtrar por email exacto
- `is_active` (boolean, opcional) - Filtrar por estado

**Respuesta**: `Array<FacturacionResponse>` con metadatos de paginación

Respuesta (200):
```json
{
  "facturacion": [
    {
      "_id": "507f1f77bcf86cd799439011",
      "facturacion_name": "María Elena González Pérez",
      "facturacion_code": "87654321",
      "facturacion_email": "maria.gonzalez@facturacion.com",
      "is_active": true,
      "observaciones": "Usuario de facturación con 5 años de experiencia",
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

#### GET `/api/v1/facturacion/{facturacion_code}`

**Descripción**: Obtener usuario de facturación específico por código  
**Parámetros**: `facturacion_code` (path)  
**Respuesta**: `FacturacionResponse`

#### PUT `/api/v1/facturacion/{facturacion_code}`

**Descripción**: Actualizar datos completos del usuario de facturación  
**Parámetros**: `facturacion_code` (path)  
**Body**: `FacturacionUpdate` (campos opcionales)  
**Respuesta**: `FacturacionResponse`

#### DELETE `/api/v1/facturacion/{facturacion_code}`

**Descripción**: Eliminar usuario de facturación permanentemente  
**Parámetros**: `facturacion_code` (path)  
**Respuesta**: `{"message": "string", "facturacion_code": "string", "eliminado": true}`

⚠️ **ADVERTENCIA**: Esta operación elimina permanentemente el registro y no se puede deshacer.

#### PATCH `/api/v1/facturacion/{facturacion_code}/estado`

**Descripción**: Cambiar solo el estado activo/inactivo del usuario de facturación  
**Parámetros**: `facturacion_code` (path)  
**Body**: `FacturacionEstadoUpdate`  
**Respuesta**: `FacturacionResponse`

### 3.2. Búsquedas Avanzadas

#### GET `/api/v1/facturacion/search`

**Descripción**: Búsqueda general con filtros avanzados  
**Query Params**:

- `q` (string, opcional) - Término de búsqueda general (busca en nombre, código, email, observaciones)
- `facturacion_name` (string, opcional) - Filtrar por nombre específico
- `facturacion_code` (string, opcional) - Filtrar por código específico
- `facturacion_email` (string, opcional) - Filtrar por email específico
- `is_active` (boolean, opcional) - Filtrar por estado
- `skip` (int, default: 0) - Registros a omitir
- `limit` (int, default: 10, max: 100) - Máximo registros

**Respuesta**: Objeto con usuarios de facturación y metadatos de búsqueda

#### GET `/api/v1/facturacion/search/active`

**Descripción**: Búsqueda solo entre usuarios de facturación activos  
**Query Params**: Mismos que `/search` pero forzando `is_active=true`  
**Respuesta**: Objeto con usuarios de facturación activos y metadatos

#### GET `/api/v1/facturacion/search/all-including-inactive`

**Descripción**: Búsqueda incluyendo usuarios de facturación inactivos  
**Query Params**: Mismos que `/search` pero incluye todos los estados  
**Respuesta**: Objeto con todos los usuarios de facturación y metadatos

### 3.3. Filtros por Estado

#### GET `/api/v1/facturacion/activos`

**Descripción**: Obtener todos los usuarios de facturación activos  
**Respuesta**: `Array<FacturacionResponse>`

#### GET `/api/v1/facturacion/inactivos`

**Descripción**: Obtener todos los usuarios de facturación inactivos  
**Respuesta**: `Array<FacturacionResponse>`

---

## 4. Códigos de Error

### 4.1. Errores Comunes

#### 400 Bad Request

```json
{
  "detail": "Datos de entrada inválidos"
}
```

#### 404 Not Found

```json
{
  "detail": "Usuario de facturación no encontrado"
}
```

#### 409 Conflict

```json
{
  "detail": "El código de usuario de facturación ya existe"
}
```

#### 422 Validation Error

```json
{
  "detail": [
    {
      "loc": ["body", "facturacion_name"],
      "msg": "field required",
      "type": "value_error.missing"
    }
  ]
}
```

#### 500 Internal Server Error

```json
{
  "detail": "Error interno del servidor"
}
```

---

## 5. Casos de Uso

### 5.1. Gestión de Personal de Facturación

- Registro de nuevos usuarios de facturación
- Control de acceso por estado activo/inactivo
- Mantenimiento de información básica del personal
- Sincronización automática con sistema de usuarios

### 5.2. Control de Estado y Disponibilidad

- Activación/desactivación temporal de usuarios de facturación
- Gestión de personal temporal o permanente
- Mantenimiento de registros históricos
- Control de acceso al sistema

### 5.3. Administración de Contactos

- Gestión de información de contacto
- Actualización de datos personales
- Seguimiento de cambios en la información
- Validación de unicidad de códigos y emails

### 5.4. Gestión Integral de Usuarios

- Creación automática de usuarios con rol "facturacion"
- Sincronización entre colecciones facturación y usuarios
- Gestión de contraseñas y acceso al sistema
- Control de permisos por rol

---

## 6. Características Especiales

### 6.1. Integración con Sistema de Usuarios

- **Creación Automática**: Al crear un usuario de facturación, se genera automáticamente un usuario del sistema
- **Sincronización**: Los cambios se propagan entre las colecciones facturación y usuarios
- **Roles**: Los usuarios de facturación tienen rol "facturacion" en el sistema de autenticación
- **Contraseñas**: Se pueden actualizar las contraseñas a través del endpoint de actualización

### 6.2. Validaciones Avanzadas

- **Códigos Únicos**: El sistema valida que no existan códigos duplicados
- **Emails Únicos**: Cada usuario de facturación debe tener un email único en todo el sistema
- **Formato de Email**: Validación automática del formato de email
- **Longitudes**: Validación de longitudes mínimas y máximas en todos los campos

### 6.3. Búsquedas Inteligentes

- **Búsqueda Global**: El término de búsqueda se aplica a nombre, código, email y observaciones
- **Filtros Específicos**: Posibilidad de filtrar por campos específicos
- **Estado Flexible**: Búsquedas que incluyen o excluyen usuarios de facturación inactivos
- **Paginación**: Soporte completo para paginación en todas las consultas

---

## 7. Ejemplos de Integración

### 7.1. Operaciones Básicas

#### Crear un usuario de facturación

```bash
curl -X POST "http://localhost:8000/api/v1/facturacion/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "facturacion_name": "María Elena González Pérez",
    "facturacion_code": "87654321", 
    "facturacion_email": "maria.gonzalez@facturacion.com",
    "password": "contraseña123",
    "observaciones": "Usuario de facturación con 5 años de experiencia"
  }'
```

#### Listar usuarios de facturación con paginación

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/?skip=0&limit=5"
```

#### Obtener usuario de facturación específico

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/87654321"
```

### 7.2. Búsquedas y Filtros

#### Búsqueda general

```bash
# Buscar por término general
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/search?q=facturacion&limit=10"

# Buscar por código específico
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/search?q=87654321"

# Buscar solo usuarios de facturación activos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/search/active?q=maría"
```

#### Filtros específicos

```bash
# Filtrar por nombre
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/?facturacion_name=María&is_active=true"

# Obtener solo usuarios de facturación activos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/activos"

# Obtener solo usuarios de facturación inactivos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/facturacion/inactivos"
```

### 7.3. Actualizaciones y Gestión de Estado

#### Actualizar información completa

```bash
curl -X PUT "http://localhost:8000/api/v1/facturacion/87654321" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "facturacion_name": "María Elena González López",
    "facturacion_email": "maria.gonzalez.nuevo@facturacion.com",
    "observaciones": "Usuario de facturación con mayor experiencia en contabilidad"
  }'
```

#### Cambiar estado (activar/desactivar)

```bash
# Desactivar usuario de facturación
curl -X PATCH "http://localhost:8000/api/v1/facturacion/87654321/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": false}'

# Reactivar usuario de facturación
curl -X PATCH "http://localhost:8000/api/v1/facturacion/87654321/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": true}'
```

---

## 8. Notas Importantes

1. **Eliminación Permanente**: Los usuarios de facturación eliminados se borran físicamente de la base de datos y no se pueden recuperar
2. **Sincronización Automática**: Los cambios se sincronizan automáticamente entre las colecciones facturación y usuarios
3. **Autenticación Requerida**: Este módulo requiere autenticación válida para todas las operaciones
4. **Validación Estricta**: El sistema valida unicidad de códigos y emails antes de cualquier operación
5. **Búsquedas Inteligentes**: Las búsquedas por texto son case-insensitive y buscan en múltiples campos
6. **Paginación Consistente**: Todos los listados soportan paginación con skip/limit
7. **Estados Flexibles**: Los usuarios de facturación pueden estar activos o inactivos sin perder la información
8. **Gestión de Contraseñas**: Las contraseñas se gestionan de forma segura y se pueden actualizar
