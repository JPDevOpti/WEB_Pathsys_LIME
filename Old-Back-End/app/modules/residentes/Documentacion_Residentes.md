# Documentación del Módulo Residentes

## ⚠️ **IMPORTANTE: AUTENTICACIÓN REQUERIDA**
Este módulo **SÍ requiere autenticación** para todas las operaciones. Incluye el header `Authorization: Bearer {token}` en todas las peticiones.

**Nota**: Al crear residentes, el sistema también crea usuarios en la colección `usuarios` con rol "residente", lo que requiere permisos de administrador.

## Estructura del Modelo

### Campos del Modelo Residente
```json
{
    "_id": "ObjectId MongoDB",
    "residente_name": "string (nombre completo del residente)",
    "iniciales_residente": "string (iniciales del residente)",
    "residente_code": "string (cédula única del residente)",
    "residente_email": "string (email único)",
    "registro_medico": "string (registro médico único)",
    "is_active": "boolean (estado activo/inactivo)",
    "observaciones": "string (notas adicionales, opcional)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Estados Disponibles
- `true` - Residente activo y disponible
- `false` - Residente inactivo

### Campos Requeridos para Crear
- `residente_name`: Nombre completo del residente (2-100 caracteres)
- `iniciales_residente`: Iniciales del residente (2-10 caracteres)
- `residente_code`: Cédula única del residente (8-20 caracteres)
- `residente_email`: Email único válido
- `registro_medico`: Registro médico único (3-50 caracteres)
- `password`: Contraseña para el usuario del residente (6-100 caracteres)
- `is_active`: Estado activo (true/false, por defecto: true)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/residentes/
**Crear nuevo residente**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Body:
```json
{
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "password": "residente123",
    "is_active": true,
    "observaciones": "Residente de patología con 2 años de experiencia"
}
```

Respuesta (201):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/residentes/
**Listar residentes activos con paginación**

Headers:
```
Authorization: Bearer {token}
```

URL con parámetros:
- `http://localhost:8000/api/v1/residentes/` (residentes activos)
- `http://localhost:8000/api/v1/residentes/?skip=0&limit=10` (paginación)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200):
```json
[
    {
        "id": "64f8a1b2c3d4e5f6a7b8c9d0",
        "residente_name": "Carlos Eduardo Rodríguez Martínez",
        "iniciales_residente": "CERM",
        "residente_code": "12345678",
        "residente_email": "carlos.rodriguez@hospital.com",
        "registro_medico": "RM12345",
        "is_active": true,
        "observaciones": "Residente de patología con 2 años de experiencia",
        "fecha_creacion": "2023-09-07T10:30:00Z",
        "fecha_actualizacion": "2023-09-07T10:30:00Z"
    }
]
```

### 3. GET http://localhost:8000/api/v1/residentes/search
**Búsqueda avanzada de residentes**

Headers:
```
Authorization: Bearer {token}
```

URL con parámetros:
- `http://localhost:8000/api/v1/residentes/search?q=carlos` (búsqueda general)
- `http://localhost:8000/api/v1/residentes/search?q=12345678` (búsqueda por código)
- `http://localhost:8000/api/v1/residentes/search?q=carlos.rodriguez@hospital.com` (búsqueda por email)
- `http://localhost:8000/api/v1/residentes/search?q=RM12345` (búsqueda por registro médico)

Parámetros de consulta:
- `q`: Término de búsqueda que busca en nombre, código, email y registro médico (opcional)
- `residente_name`: Filtrar por nombre específico
- `iniciales_residente`: Filtrar por iniciales
- `residente_code`: Filtrar por código
- `residente_email`: Filtrar por email
- `registro_medico`: Filtrar por registro médico
- `is_active`: Filtrar por estado activo
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200):
```json
{
    "residentes": [
        {
            "id": "64f8a1b2c3d4e5f6a7b8c9d0",
            "residente_name": "Carlos Eduardo Rodríguez Martínez",
            "iniciales_residente": "CERM",
            "residente_code": "12345678",
            "residente_email": "carlos.rodriguez@hospital.com",
            "registro_medico": "RM12345",
            "is_active": true,
            "observaciones": "Residente de patología con 2 años de experiencia",
            "fecha_creacion": "2023-09-07T10:30:00Z",
            "fecha_actualizacion": "2023-09-07T10:30:00Z"
        }
    ],
    "total": 1,
    "skip": 0,
    "limit": 10
}
```

### 4. GET http://localhost:8000/api/v1/residentes/{residente_code}
**Obtener residente específico por código**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 5. PUT http://localhost:8000/api/v1/residentes/{residente_code}
**Actualizar residente por código**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body:
```json
{
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "observaciones": "Residente de patología y neuropatología con 2 años de experiencia"
}
```

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": true,
    "observaciones": "Residente de patología y neuropatología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T12:45:00Z"
}
```

### 6. DELETE http://localhost:8000/api/v1/residentes/{residente_code}
**Eliminar residente por código (eliminación permanente)**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "message": "Residente con código 12345678 ha sido eliminado correctamente"
}
```

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 7. PATCH http://localhost:8000/api/v1/residentes/{residente_code}/toggle-estado
**Cambiar estado activo/inactivo de un residente (toggle)**

Headers:
```
Authorization: Bearer {token}
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678/toggle-estado`

Body: (sin body)

Respuesta (200):
```json
{
    "id": "64f8a1b2c3d4e5f6a7b8c9d0",
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": false,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T14:10:00Z"
}
```

**Funcionamiento**: 
- Si el residente está activo (`is_active: true`) → lo desactiva (`is_active: false`)
- Si el residente está inactivo (`is_active: false`) → lo activa (`is_active: true`)

### 8. PUT http://localhost:8000/api/v1/residentes/{residente_code}/estado
**Cambiar estado activo/inactivo de un residente (específico)**

Headers:
```
Authorization: Bearer {token}
Content-Type: application/json
```

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678/estado`

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
    "residente_name": "Carlos Eduardo Rodríguez Martínez",
    "iniciales_residente": "CERM",
    "residente_code": "12345678",
    "residente_email": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "is_active": false,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T14:10:00Z"
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
    "detail": "El email ya está registrado en residentes"
}
```

### Registro Médico Duplicado (409)
```json
{
    "detail": "El registro médico ya está registrado"
}
```

### Residente No Encontrado (404)
```json
{
    "detail": "Residente no encontrado"
}
```

### Datos Inválidos (422)
```json
{
    "detail": [
        {
            "loc": ["body", "residente_name"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "residente_code"],
            "msg": "ensure this value has at least 8 characters",
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

### 1. Registro de Nuevo Residente
**Escenario:** Registrar un nuevo residente en el sistema

**Pasos:**
1. Hacer POST a `/api/v1/residentes/` con autenticación
2. Incluir campos requeridos: `residente_name`, `residente_code`, `residente_email`, `registro_medico`, `password`
3. Verificar que email, cédula y registro médico sean únicos
4. El sistema crea automáticamente un usuario en la colección `usuarios`

### 2. Búsqueda de Residentes
**Escenario:** Obtener lista de residentes disponibles

**Pasos:**
1. Hacer GET a `/api/v1/residentes/` (muestra residentes activos)
2. Usar búsqueda avanzada con `/api/v1/residentes/search?q=término`

### 3. Actualización de Estado
**Escenario:** Activar o desactivar residente

**Pasos:**
1. Hacer PATCH a `/api/v1/residentes/{residente_code}/toggle-estado` para alternar
2. O hacer PUT a `/api/v1/residentes/{residente_code}/estado` para estado específico
3. El sistema sincroniza automáticamente con la colección `usuarios`

### 4. Búsqueda Avanzada
**Escenario:** Encontrar residentes con criterios específicos

**Pasos:**
1. Usar GET `/api/v1/residentes/search?q=término` para búsqueda general
2. El parámetro `q` busca en nombre, código, email y registro médico
3. Aplicar paginación con `skip` y `limit` si es necesario

### 5. Eliminación Permanente
**Escenario:** Remover residente del sistema (usar con EXTREMA precaución)

**⚠️ ADVERTENCIA:** Esta operación elimina permanentemente el registro de la base de datos y NO se puede deshacer.

**Pasos:**
1. Hacer DELETE a `/api/v1/residentes/{residente_code}`
2. Confirmar que no hay casos pendientes asociados
3. Operación irreversible - el registro se elimina completamente
4. Para activar/desactivar usar PATCH `/api/v1/residentes/{residente_code}/toggle-estado`

### 6. Consulta por Código
**Escenario:** Buscar residente específico usando su cédula

**Pasos:**
1. Hacer GET a `/api/v1/residentes/{residente_code}`
2. Usar la cédula del residente como identificador
3. Natural y directo usando código
4. Útil para integraciones externas

## Ejemplos de Residentes

### Residente de Anatomía Patológica
```json
{
    "residente_name": "María Elena García López",
    "iniciales_residente": "MEGL",
    "residente_code": "87654321",
    "residente_email": "maria.garcia@hospital.com",
    "registro_medico": "RM54321",
    "is_active": true,
    "observaciones": "Residente de anatomía patológica - segundo año"
}
```

### Residente de Patología Forense
```json
{
    "residente_name": "Juan Carlos Mendoza Silva",
    "iniciales_residente": "JCMS",
    "residente_code": "11223344",
    "residente_email": "juan.mendoza@medicina-legal.gov.co",
    "registro_medico": "RM11223",
    "is_active": true,
    "observaciones": "Residente de patología forense - primer año"
}
```

### Residente de Neuropatología
```json
{
    "residente_name": "Ana Sofía Ramírez Torres",
    "iniciales_residente": "ASRT",
    "residente_code": "55667788",
    "residente_email": "ana.ramirez@neurologia.com",
    "registro_medico": "RM55667",
    "is_active": true,
    "observaciones": "Residente de neuropatología - tercer año"
}
```

### Residente de Citopatología
```json
{
    "residente_name": "Luis Fernando Vargas Herrera",
    "iniciales_residente": "LFVH",
    "residente_code": "99887766",
    "residente_email": "luis.vargas@laboratorio.com",
    "registro_medico": "RM99887",
    "is_active": false,
    "observaciones": "Residente de citopatología - actualmente en rotación externa"
}
```

## Resumen de Características del Módulo

### ✅ Funcionalidades Implementadas
- **CRUD Completo**: Crear, leer, actualizar y eliminar residentes
- **Autenticación Requerida**: Todos los endpoints requieren JWT Bearer token
- **Creación de Usuarios**: Automáticamente crea usuarios en la colección `usuarios`
- **Búsqueda Avanzada**: Búsqueda por múltiples campos con un solo parámetro
- **Gestión de Estados**: Activar/desactivar residentes
- **Sincronización**: Cambios se reflejan automáticamente en la colección `usuarios`
- **Eliminación Permanente**: Eliminación real de registros (no soft delete)

### 🔧 Endpoints Disponibles
1. `POST /api/v1/residentes/` - Crear residente
2. `GET /api/v1/residentes/` - Listar residentes activos
3. `GET /api/v1/residentes/search` - Búsqueda avanzada
4. `GET /api/v1/residentes/{code}` - Obtener residente específico
5. `PUT /api/v1/residentes/{code}` - Actualizar residente
6. `PATCH /api/v1/residentes/{code}/toggle-estado` - Alternar estado activo/inactivo
7. `PUT /api/v1/residentes/{code}/estado` - Cambiar estado específico
8. `DELETE /api/v1/residentes/{code}` - Eliminación permanente

### ⚠️ Consideraciones Importantes
- **Autenticación Requerida**: Todos los endpoints requieren JWT Bearer token
- **Creación de Usuarios**: Al crear residentes se crean usuarios automáticamente
- **Eliminación Permanente**: La operación DELETE es irreversible
- **Sincronización**: Cambios se reflejan en ambas colecciones (residentes y usuarios)
- **Validaciones**: Campos únicos (email, código, registro médico)
- **Búsqueda Unificada**: Un solo parámetro `q` para búsqueda general
- **Nombres de Campos**: Todos en snake_case para consistencia

## Validaciones

- **residente_name**: 2-100 caracteres, no puede estar vacío
- **iniciales_residente**: 2-10 caracteres, no puede estar vacío
- **residente_code**: 8-20 caracteres, no puede estar vacío, debe ser único
- **residente_email**: Email válido, debe ser único
- **registro_medico**: 3-50 caracteres, debe ser único
- **password**: 6-100 caracteres (solo para creación)
- **is_active**: Boolean, por defecto true
- **observaciones**: Opcional, máximo 500 caracteres