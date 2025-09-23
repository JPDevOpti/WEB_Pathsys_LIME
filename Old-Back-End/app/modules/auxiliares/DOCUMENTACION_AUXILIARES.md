# Documentación del Módulo de Auxiliares

## 1. Arquitectura de Archivos

```text
app/modules/auxiliares/
├── models/
│   └── auxiliar.py                 # Modelos MongoDB (Auxiliar)
├── schemas/
│   └── auxiliar.py                 # Esquemas Pydantic para API (Request/Response)
├── repositories/
│   └── auxiliar_repository.py      # Operaciones CRUD y consultas avanzadas
├── services/
│   └── auxiliar_service.py         # Lógica de negocio y transformaciones
├── routes/
│   └── auxiliar_routes.py          # Endpoints FastAPI
└── DOCUMENTACION_AUXILIARES.md     # Este archivo
```

### Capas y Responsabilidades

- **Models**: Definición de estructuras de datos para MongoDB
- **Schemas**: Validación y serialización para API REST
- **Repositories**: Acceso a datos y consultas complejas
- **Services**: Lógica de negocio, validaciones, transformaciones, gestión de usuarios
- **Routes**: Definición de endpoints HTTP

## ⚠️ IMPORTANTE: MÓDULO CON AUTENTICACIÓN
**Este módulo SÍ requiere autenticación.** Los auxiliares son usuarios del sistema con rol "auxiliar" y tienen acceso a funcionalidades específicas según su nivel de permisos.

---

## 2. Esquema Completo

### 2.1. Modelo Principal (`Auxiliar`)

```json
{
  "_id": "ObjectId",
  "auxiliar_name": "string (<=200 chars, nombre completo del auxiliar)",
  "auxiliar_code": "string (<=20 chars, código único del auxiliar)", 
  "auxiliar_email": "string (email único válido)",
  "is_active": "boolean (estado activo/inactivo, default: true)",
  "observaciones": "string|null (<=500 chars, notas adicionales)",
  "fecha_creacion": "datetime",
  "fecha_actualizacion": "datetime"
}
```

### 2.2. Esquemas API

#### AuxiliarResponse (GET requests)

```json
{
  "id": "string (ObjectId convertido)",
  "auxiliar_name": "string",
  "auxiliar_code": "string", 
  "auxiliar_email": "string",
  "is_active": "boolean",
  "observaciones": "string",
  "fecha_creacion": "datetime ISO",
  "fecha_actualizacion": "datetime ISO"
}
```

#### AuxiliarCreate (POST request)

```json
{
  "auxiliar_name": "string (requerido, <=200 chars)",
  "auxiliar_code": "string (requerido, <=20 chars, único)",
  "auxiliar_email": "string (requerido, email válido, único)",
  "password": "string (requerido, <=128 chars, para usuario del sistema)",
  "is_active": "boolean (default: true)",
  "observaciones": "string|null (<=500 chars)"
}
```

#### AuxiliarUpdate (PUT request)

```json
{
  "auxiliar_name": "string|null (<=200 chars)",
  "auxiliar_code": "string|null (<=20 chars)",
  "auxiliar_email": "string|null (email válido)",
  "is_active": "boolean|null",
  "observaciones": "string|null (<=500 chars)",
  "password": "string|null (<=128 chars, opcional para cambio de contraseña)"
}
```

#### AuxiliarSearch (Búsqueda avanzada)

```json
{
  "auxiliar_name": "string|null (búsqueda parcial)",
  "auxiliar_code": "string|null (búsqueda exacta)",
  "auxiliar_email": "string|null (búsqueda exacta)",
  "is_active": "boolean|null (filtro por estado)"
}
```

#### AuxiliarEstadoUpdate (PATCH estado)

```json
{
  "is_active": "boolean (requerido)"
}
```

### 2.3. Estados Disponibles

- `true` - Auxiliar activo y disponible para trabajar
- `false` - Auxiliar inactivo (temporalmente deshabilitado)

### 2.4. Validaciones y Restricciones

#### Campos Únicos
- `auxiliar_code`: Debe ser único en todo el sistema
- `auxiliar_email`: Debe ser único en todo el sistema

#### Reglas de Validación
- **auxiliar_name**: 2-200 caracteres, solo letras, espacios y acentos
- **auxiliar_code**: 8-20 caracteres alfanuméricos, único
- **auxiliar_email**: Formato de email válido, único
- **password**: 6-128 caracteres (requerido para crear usuario)
- **observaciones**: Máximo 500 caracteres (opcional)
- **is_active**: Valor booleano (true/false)

---

## 3. Endpoints Completos

### 3.1. Gestión de Auxiliares

#### POST `/api/v1/auxiliares/`

**Descripción**: Crear un nuevo auxiliar y usuario del sistema  
**Body**: `AuxiliarCreate`  
**Respuesta**: `AuxiliarResponse`

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

#### GET `/api/v1/auxiliares/`

**Descripción**: Listar auxiliares activos con paginación y filtros  
**Query Params**:

- `skip` (int, default: 0) - Registros a omitir
- `limit` (int, default: 10, max: 100) - Máximo registros a devolver
- `auxiliar_name` (string, opcional) - Filtrar por nombre (búsqueda parcial)
- `auxiliar_code` (string, opcional) - Filtrar por código exacto
- `auxiliar_email` (string, opcional) - Filtrar por email exacto
- `is_active` (boolean, opcional) - Filtrar por estado

**Respuesta**: `Array<AuxiliarResponse>` con metadatos de paginación

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

#### GET `/api/v1/auxiliares/{auxiliar_code}`

**Descripción**: Obtener auxiliar específico por código  
**Parámetros**: `auxiliar_code` (path)  
**Respuesta**: `AuxiliarResponse`

#### PUT `/api/v1/auxiliares/{auxiliar_code}`

**Descripción**: Actualizar datos completos del auxiliar  
**Parámetros**: `auxiliar_code` (path)  
**Body**: `AuxiliarUpdate` (campos opcionales)  
**Respuesta**: `AuxiliarResponse`

#### DELETE `/api/v1/auxiliares/{auxiliar_code}`

**Descripción**: Eliminar auxiliar permanentemente  
**Parámetros**: `auxiliar_code` (path)  
**Respuesta**: `{"message": "string", "auxiliar_code": "string", "eliminado": true}`

⚠️ **ADVERTENCIA**: Esta operación elimina permanentemente el registro y no se puede deshacer.

#### PATCH `/api/v1/auxiliares/{auxiliar_code}/estado`

**Descripción**: Cambiar solo el estado activo/inactivo del auxiliar  
**Parámetros**: `auxiliar_code` (path)  
**Body**: `AuxiliarEstadoUpdate`  
**Respuesta**: `AuxiliarResponse`

### 3.2. Búsquedas Avanzadas

#### GET `/api/v1/auxiliares/search`

**Descripción**: Búsqueda general con filtros avanzados  
**Query Params**:

- `q` (string, opcional) - Término de búsqueda general (busca en nombre, código, email, observaciones)
- `auxiliar_name` (string, opcional) - Filtrar por nombre específico
- `auxiliar_code` (string, opcional) - Filtrar por código específico
- `auxiliar_email` (string, opcional) - Filtrar por email específico
- `is_active` (boolean, opcional) - Filtrar por estado
- `skip` (int, default: 0) - Registros a omitir
- `limit` (int, default: 10, max: 100) - Máximo registros

**Respuesta**: Objeto con auxiliares y metadatos de búsqueda

#### GET `/api/v1/auxiliares/search/active`

**Descripción**: Búsqueda solo entre auxiliares activos  
**Query Params**: Mismos que `/search` pero forzando `is_active=true`  
**Respuesta**: Objeto con auxiliares activos y metadatos

#### GET `/api/v1/auxiliares/search/all-including-inactive`

**Descripción**: Búsqueda incluyendo auxiliares inactivos  
**Query Params**: Mismos que `/search` pero incluye todos los estados  
**Respuesta**: Objeto con todos los auxiliares y metadatos

### 3.3. Filtros por Estado

#### GET `/api/v1/auxiliares/activos`

**Descripción**: Obtener todos los auxiliares activos  
**Respuesta**: `Array<AuxiliarResponse>`

#### GET `/api/v1/auxiliares/inactivos`

**Descripción**: Obtener todos los auxiliares inactivos  
**Respuesta**: `Array<AuxiliarResponse>`

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
  "detail": "Auxiliar no encontrado"
}
```

#### 409 Conflict

```json
{
  "detail": "El código de auxiliar ya existe"
}
```

#### 422 Validation Error

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

#### 500 Internal Server Error

```json
{
  "detail": "Error interno del servidor"
}
```

---

## 5. Casos de Uso

### 5.1. Gestión de Personal de Laboratorio

- Registro de nuevos auxiliares de laboratorio
- Control de acceso por estado activo/inactivo
- Mantenimiento de información básica del personal
- Sincronización automática con sistema de usuarios

### 5.2. Control de Estado y Disponibilidad

- Activación/desactivación temporal de auxiliares
- Gestión de personal temporal o permanente
- Mantenimiento de registros históricos
- Control de acceso al sistema

### 5.3. Administración de Contactos

- Gestión de información de contacto
- Actualización de datos personales
- Seguimiento de cambios en la información
- Validación de unicidad de códigos y emails

### 5.4. Gestión Integral de Usuarios

- Creación automática de usuarios con rol "auxiliar"
- Sincronización entre colecciones auxiliares y usuarios
- Gestión de contraseñas y acceso al sistema
- Control de permisos por rol

---

## 6. Características Especiales

### 6.1. Integración con Sistema de Usuarios

- **Creación Automática**: Al crear un auxiliar, se genera automáticamente un usuario del sistema
- **Sincronización**: Los cambios se propagan entre las colecciones auxiliares y usuarios
- **Roles**: Los auxiliares tienen rol "auxiliar" en el sistema de autenticación
- **Contraseñas**: Se pueden actualizar las contraseñas a través del endpoint de actualización

### 6.2. Validaciones Avanzadas

- **Códigos Únicos**: El sistema valida que no existan códigos duplicados
- **Emails Únicos**: Cada auxiliar debe tener un email único en todo el sistema
- **Formato de Email**: Validación automática del formato de email
- **Longitudes**: Validación de longitudes mínimas y máximas en todos los campos

### 6.3. Búsquedas Inteligentes

- **Búsqueda Global**: El término de búsqueda se aplica a nombre, código, email y observaciones
- **Filtros Específicos**: Posibilidad de filtrar por campos específicos
- **Estado Flexible**: Búsquedas que incluyen o excluyen auxiliares inactivos
- **Paginación**: Soporte completo para paginación en todas las consultas

---

## 7. Ejemplos de Integración

### 7.1. Operaciones Básicas

#### Crear un auxiliar

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

#### Listar auxiliares con paginación

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/?skip=0&limit=5"
```

#### Obtener auxiliar específico

```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/87654321"
```

### 7.2. Búsquedas y Filtros

#### Búsqueda general

```bash
# Buscar por término general
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?q=laboratorio&limit=10"

# Buscar por código específico
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?q=87654321"

# Buscar solo auxiliares activos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search/active?q=maría"
```

#### Filtros específicos

```bash
# Filtrar por nombre
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/?auxiliar_name=María&is_active=true"

# Obtener solo auxiliares activos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/activos"

# Obtener solo auxiliares inactivos
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/inactivos"
```

### 7.3. Actualizaciones y Gestión de Estado

#### Actualizar información completa

```bash
curl -X PUT "http://localhost:8000/api/v1/auxiliares/87654321" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "María Elena González López",
    "auxiliar_email": "maria.gonzalez.nuevo@hospital.com",
    "observaciones": "Auxiliar con mayor experiencia en microbiología"
  }'
```

#### Cambiar estado (activar/desactivar)

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

### 7.4. Flujo Completo de Gestión

```bash
# 1. Crear auxiliar
AUXILIAR_RESPONSE=$(curl -s -X POST "http://localhost:8000/api/v1/auxiliares/" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "Ana María Rodríguez",
    "auxiliar_code": "12345678",
    "auxiliar_email": "ana.rodriguez@hospital.com",
    "password": "auxiliar123",
    "observaciones": "Especialista en análisis de sangre"
  }')

echo "Auxiliar creado: $AUXILIAR_RESPONSE"

# 2. Verificar creación
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/12345678"

# 3. Actualizar información
curl -X PUT "http://localhost:8000/api/v1/auxiliares/12345678" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "auxiliar_name": "Ana María Rodríguez López",
    "observaciones": "Especialista en análisis de sangre y microbiología"
  }'

# 4. Realizar búsqueda para verificar cambios
curl -H "Authorization: Bearer YOUR_TOKEN" \
  "http://localhost:8000/api/v1/auxiliares/search?auxiliar_name=Ana&is_active=true"

# 5. Desactivar temporalmente si es necesario
curl -X PATCH "http://localhost:8000/api/v1/auxiliares/12345678/estado" \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"is_active": false}'
```

### 7.5. Integración con JavaScript/TypeScript

```typescript
// Ejemplo usando axios en TypeScript
import axios, { AxiosResponse } from 'axios';

interface Auxiliar {
  auxiliar_name: string;
  auxiliar_code: string;
  auxiliar_email: string;
  is_active: boolean;
  observaciones?: string;
}

interface AuxiliarCreate extends Auxiliar {
  password: string;
}

class AuxiliarService {
  private baseURL = 'http://localhost:8000/api/v1/auxiliares';
  private token: string;

  constructor(token: string) {
    this.token = token;
  }

  private getHeaders() {
    return {
      'Content-Type': 'application/json',
      'Authorization': `Bearer ${this.token}`
    };
  }

  async createAuxiliar(data: AuxiliarCreate): Promise<Auxiliar> {
    const response: AxiosResponse<Auxiliar> = await axios.post(
      this.baseURL,
      data,
      { headers: this.getHeaders() }
    );
    return response.data;
  }

  async getAuxiliares(skip = 0, limit = 10): Promise<Auxiliar[]> {
    const response = await axios.get(
      `${this.baseURL}?skip=${skip}&limit=${limit}`,
      { headers: this.getHeaders() }
    );
    return response.data.auxiliares;
  }

  async searchAuxiliares(query: string): Promise<Auxiliar[]> {
    const response = await axios.get(
      `${this.baseURL}/search?q=${encodeURIComponent(query)}`,
      { headers: this.getHeaders() }
    );
    return response.data.auxiliares;
  }

  async updateAuxiliarStatus(code: string, isActive: boolean): Promise<Auxiliar> {
    const response: AxiosResponse<Auxiliar> = await axios.patch(
      `${this.baseURL}/${code}/estado`,
      { is_active: isActive },
      { headers: this.getHeaders() }
    );
    return response.data;
  }
}
```

---

## 8. Notas Importantes

1. **Eliminación Permanente**: Los auxiliares eliminados se borran físicamente de la base de datos y no se pueden recuperar
2. **Sincronización Automática**: Los cambios se sincronizan automáticamente entre las colecciones auxiliares y usuarios
3. **Autenticación Requerida**: Este módulo requiere autenticación válida para todas las operaciones
4. **Validación Estricta**: El sistema valida unicidad de códigos y emails antes de cualquier operación
5. **Búsquedas Inteligentes**: Las búsquedas por texto son case-insensitive y buscan en múltiples campos
6. **Paginación Consistente**: Todos los listados soportan paginación con skip/limit
7. **Estados Flexibles**: Los auxiliares pueden estar activos o inactivos sin perder la información
8. **Gestión de Contraseñas**: Las contraseñas se gestionan de forma segura y se pueden actualizar