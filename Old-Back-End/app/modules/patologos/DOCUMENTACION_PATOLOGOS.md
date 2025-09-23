# Guía de Patólogos - Postman

## ⚠️ **IMPORTANTE: AUTENTICACIÓN REQUERIDA**
Este módulo **SÍ requiere autenticación** para todas las operaciones. Incluye el header `Authorization: Bearer {token}` en todas las peticiones.

**Nota**: Al crear patólogos, el sistema también crea usuarios en la colección `usuarios` con rol "patologo", lo que requiere permisos de administrador.

## Estructura del Modelo

### Campos del Modelo Patologo
```json
{
    "_id": "ObjectId MongoDB",
    "patologo_name": "string (nombre completo del patólogo)",
    "iniciales_patologo": "string (iniciales del patólogo)",
    "patologo_code": "string (cédula única del patólogo)",
    "patologo_email": "string (email único)",
    "registro_medico": "string (registro médico único)",
    "is_active": "boolean (estado activo/inactivo)",
    "firma": "string (URL de firma digital, por defecto vacío)",
    "observaciones": "string (notas adicionales, opcional)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Estados Disponibles
- `true` - Patólogo activo y disponible
- `false` - Patólogo inactivo

### Campos Requeridos para Crear
- `patologo_name`: Nombre completo del patólogo (2-100 caracteres)
- `iniciales_patologo`: Iniciales del patólogo (2-10 caracteres)
- `patologo_code`: Cédula única del patólogo (6-10 caracteres)
- `patologo_email`: Email único válido
- `registro_medico`: Registro médico único (5-50 caracteres)
- `password`: Contraseña para el usuario del patólogo (6-100 caracteres)
- `is_active`: Estado activo (true/false, por defecto: true)
- `firma`: URL de firma digital (opcional, por defecto vacío)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/patologos/
**Crear nuevo patólogo**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Body:
```json
{
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "password": "patologo123",
    "is_active": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia"
}
```

Respuesta (201):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/patologos/
**Listar patólogos activos con paginación**

Headers:
```
Authorization: Bearer {token}
```

URL con parámetros:
- `http://localhost:8000/api/v1/patologos/` (patólogos activos)
- `http://localhost:8000/api/v1/patologos/?skip=0&limit=10` (paginación)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200):
```json
[
    {
        "id": "64f8a1b2c3d4e5f6a7b8c9d0",
        "patologo_name": "Carlos Eduardo Rodríguez Martínez",
        "iniciales_patologo": "CERM",
        "patologo_code": "12345678",
        "patologo_email": "carlos.rodriguez@hospital.com",
        "registro_medico": "RM12345",
        "is_active": true,
        "firma": "https://storage.com/firmas/carlos_rodriguez.png",
        "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
        "fecha_creacion": "2023-09-07T10:30:00Z",
        "fecha_actualizacion": "2023-09-07T10:30:00Z"
    }
]
```

### 3. GET http://localhost:8000/api/v1/patologos/search
**Búsqueda avanzada de patólogos**

Headers:
```
Authorization: Bearer {token}
```

URL con parámetros:
- `http://localhost:8000/api/v1/patologos/search?q=carlos` (búsqueda general)
- `http://localhost:8000/api/v1/patologos/search?q=12345678` (búsqueda por código)
- `http://localhost:8000/api/v1/patologos/search?q=carlos.rodriguez@hospital.com` (búsqueda por email)
- `http://localhost:8000/api/v1/patologos/search?q=RM12345` (búsqueda por registro médico)

Parámetros de consulta:
- `q`: Término de búsqueda que busca en nombre, código, email y registro médico (opcional)
- `patologo_name`: Filtrar por nombre específico
- `iniciales_patologo`: Filtrar por iniciales
- `patologo_code`: Filtrar por código
- `patologo_email`: Filtrar por email
- `registro_medico`: Filtrar por registro médico
- `is_active`: Filtrar por estado activo
- `observaciones`: Filtrar por observaciones
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 100, max: 1000)

Body: (sin body)

Respuesta (200):
```json
[
    {
        "id": "64f8a1b2c3d4e5f6a7b8c9d0",
        "patologo_name": "Carlos Eduardo Rodríguez Martínez",
        "iniciales_patologo": "CERM",
        "patologo_code": "12345678",
        "patologo_email": "carlos.rodriguez@hospital.com",
        "registro_medico": "RM12345",
        "is_active": true,
        "firma": "https://storage.com/firmas/carlos_rodriguez.png",
        "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
        "fecha_creacion": "2023-09-07T10:30:00Z",
        "fecha_actualizacion": "2023-09-07T10:30:00Z"
    }
]
```

### 4. GET http://localhost:8000/api/v1/patologos/{patologo_code}
**Obtener patólogo específico por código**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. PUT http://localhost:8000/api/v1/patologos/{patologo_code}
**Actualizar patólogo por código**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body:
```json
{
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "observaciones": "Especialista en patología oncológica y neuropatología con 15 años de experiencia"
}
```

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica y neuropatología con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T12:45:00Z"
}
```

### 6. DELETE http://localhost:8000/api/v1/patologos/{patologo_code}
**Eliminar patólogo por código (eliminación permanente)**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "message": "Patólogo con código 12345678 ha sido eliminado correctamente"
}
```

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 7. PUT http://localhost:8000/api/v1/patologos/{patologo_code}/estado
**Cambiar estado activo/inactivo de un patólogo**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678/estado`

Body:
```json
{
    "is_active": false
}
```

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": false,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T14:10:00Z"
}
```

### 8. PUT http://localhost:8000/api/v1/patologos/{patologo_code}/firma
**Actualizar la firma digital de un patólogo**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678/firma`

Body:
```json
{
    "firma": "https://storage.com/firmas/carlos_rodriguez_updated.png"
}
```

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "patologo_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_patologo": "CERM",
    "patologo_code": "12345678",
    "patologo_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez_updated.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T15:20:00Z"
}
```

## Casos de Error

### Cédula Duplicada (409)
```json
{
    "detail": "El código ya está registrado"
}
```

### Email Duplicado (409)
```json
{
    "detail": "El email ya está registrado en patólogos"
}
```

### Registro Médico Duplicado (409)
```json
{
    "detail": "El registro médico ya está registrado"
}
```

### Patólogo No Encontrado (404)
```json
{
    "detail": "Patólogo no encontrado"
}
```

### Datos Inválidos (422)
```json
{
    "detail": [
        {
            "loc": ["body", "patologo_name"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "patologo_code"],
            "msg": "ensure this value has at least 6 characters",
            "type": "value_error.any_str.min_length"
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

### 1. Registro de Nuevo Patólogo
**Escenario:** Registrar un nuevo patólogo en el sistema

**Pasos:**
1. Hacer POST a `/api/v1/patologos/` con autenticación
2. Incluir campos requeridos: `patologo_name`, `patologo_code`, `patologo_email`, `registro_medico`, `password`
3. Verificar que email, cédula y registro médico sean únicos
4. El sistema crea automáticamente un usuario en la colección `usuarios`

### 2. Búsqueda de Patólogos
**Escenario:** Obtener lista de patólogos disponibles

**Pasos:**
1. Hacer GET a `/api/v1/patologos/` (muestra patólogos activos)
2. Usar búsqueda avanzada con `/api/v1/patologos/search?q=término`

### 3. Actualización de Estado
**Escenario:** Activar o desactivar patólogo

**Pasos:**
1. Hacer PUT a `/api/v1/patologos/{patologo_code}/estado`
2. El sistema sincroniza automáticamente con la colección `usuarios`
3. Eficiente y directo usando código de patólogo

### 4. Búsqueda Avanzada
**Escenario:** Encontrar patólogos con criterios específicos

**Pasos:**
1. Usar GET `/api/v1/patologos/search?q=término` para búsqueda general
2. El parámetro `q` busca en nombre, código, email y registro médico
3. Aplicar paginación con `skip` y `limit` si es necesario

### 5. Eliminación Permanente
**Escenario:** Remover patólogo del sistema (usar con EXTREMA precaución)

**⚠️ ADVERTENCIA:** Esta operación elimina permanentemente el registro de la base de datos y NO se puede deshacer.

**Pasos:**
1. Hacer DELETE a `/api/v1/patologos/{patologo_code}`
2. Confirmar que no hay casos pendientes asociados
3. Operación irreversible - el registro se elimina completamente
4. Para activar/desactivar usar PUT `/api/v1/patologos/{patologo_code}/estado`

### 6. Consulta por Código
**Escenario:** Buscar patólogo específico usando su cédula

**Pasos:**
1. Hacer GET a `/api/v1/patologos/{patologo_code}`
2. Usar la cédula del patólogo como identificador
3. Natural y directo usando código
4. Útil para integraciones externas

### 7. Gestión de Firmas Digitales
**Escenario:** Actualizar la firma digital de un patólogo

**Pasos:**
1. Hacer PUT a `/api/v1/patologos/{patologo_code}/firma`
2. Solo se actualiza el campo `firma`
3. Útil para sistemas de firma digital

## Ejemplos de Patólogos

### Patólogo de Anatomía Patológica
```json
{
    "patologo_name": "María Elena García López",
    "iniciales_patologo": "MEGL",
    "patologo_code": "87654321",
    "patologo_email": "maria.garcia@hospital.com",
    "registro_medico": "RM54321",
    "is_active": true,
    "firma": "",
    "observaciones": "Especialista en anatomía patológica"
}
```

### Patólogo Forense
```json
{
    "patologo_name": "Juan Carlos Mendoza Silva",
    "iniciales_patologo": "JCMS",
    "patologo_code": "11223344",
    "patologo_email": "juan.mendoza@medicina-legal.gov.co",
    "registro_medico": "RM11223",
    "is_active": true,
    "firma": "",
    "observaciones": "Especialista en patología forense y anatomía patológica"
}
```

### Neuropatólogo
```json
{
    "patologo_name": "Ana Sofía Ramírez Torres",
    "iniciales_patologo": "ASRT",
    "patologo_code": "55667788",
    "patologo_email": "ana.ramirez@neurologia.com",
    "registro_medico": "RM55667",
    "is_active": true,
    "firma": "",
    "observaciones": "Especialista en neuropatología y anatomía patológica"
}
```

### Citopatólogo
```json
{
    "patologo_name": "Luis Fernando Vargas Herrera",
    "iniciales_patologo": "LFVH",
    "patologo_code": "99887766",
    "patologo_email": "luis.vargas@laboratorio.com",
    "registro_medico": "RM99887",
    "is_active": false,
    "firma": "",
    "observaciones": "Especialista en citopatología - actualmente en vacaciones"
}
```

## Resumen de Características del Módulo

### ✅ Funcionalidades Implementadas
- **CRUD Completo**: Crear, leer, actualizar y eliminar patólogos
- **Autenticación Requerida**: Todos los endpoints requieren JWT Bearer token
- **Creación de Usuarios**: Automáticamente crea usuarios en la colección `usuarios`
- **Búsqueda Avanzada**: Búsqueda por múltiples campos con un solo parámetro
- **Gestión de Estados**: Activar/desactivar patólogos
- **Gestión de Firmas**: Actualización específica de firmas digitales
- **Sincronización**: Cambios se reflejan automáticamente en la colección `usuarios`
- **Eliminación Permanente**: Eliminación real de registros (no soft delete)

### 🔧 Endpoints Disponibles
1. `POST /api/v1/patologos/` - Crear patólogo
2. `GET /api/v1/patologos/` - Listar patólogos activos
3. `GET /api/v1/patologos/search` - Búsqueda avanzada
4. `GET /api/v1/patologos/{code}` - Obtener patólogo específico
5. `PUT /api/v1/patologos/{code}` - Actualizar patólogo
6. `PUT /api/v1/patologos/{code}/estado` - Cambiar estado activo/inactivo
7. `PUT /api/v1/patologos/{code}/firma` - Actualizar firma digital
8. `DELETE /api/v1/patologos/{code}` - Eliminación permanente

### ⚠️ Consideraciones Importantes
- **Autenticación Requerida**: Todos los endpoints requieren JWT Bearer token
- **Creación de Usuarios**: Al crear patólogos se crean usuarios automáticamente
- **Eliminación Permanente**: La operación DELETE es irreversible
- **Sincronización**: Cambios se reflejan en ambas colecciones (patólogos y usuarios)
- **Validaciones**: Campos únicos (email, código, registro médico)
- **Búsqueda Unificada**: Un solo parámetro `q` para búsqueda general
- **Nombres de Campos**: Todos en snake_case para consistencia
- **Gestión de Firmas**: Endpoint específico para actualizar firmas digitales

## Validaciones

- **patologo_name**: 2-100 caracteres, no puede estar vacío
- **iniciales_patologo**: 2-10 caracteres, no puede estar vacío
- **patologo_code**: 6-10 caracteres, no puede estar vacío, debe ser único
- **patologo_email**: Email válido, debe ser único
- **registro_medico**: 5-50 caracteres, debe ser único
- **password**: 6-100 caracteres (solo para creación)
- **is_active**: Boolean, por defecto true
- **firma**: String, opcional, por defecto vacío
- **observaciones**: Opcional, máximo 500 caracteres