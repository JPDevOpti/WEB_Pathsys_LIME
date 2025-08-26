# Documentación del Módulo Residentes

## ⚠️ IMPORTANTE: MÓDULO SIN AUTENTICACIÓN
**Este módulo NO requiere autenticación.** Todos los endpoints están disponibles sin necesidad de tokens de acceso o credenciales de usuario. Esto facilita las pruebas y la integración, pero debe considerarse la seguridad en entornos de producción.

## Estructura del Modelo

### Campos del Modelo Residente
```json
{
    "_id": "ObjectId MongoDB",
    "residenteName": "string (nombre completo del residente)",
    "residenteCode": "string (cédula única del residente)",
    "ResidenteEmail": "string (email único)",
    "registro_medico": "string (registro médico único)",
    "isActive": "boolean (estado activo/inactivo)",
    "observaciones": "string (notas adicionales, opcional)",
    "fecha_creacion": "datetime",
    "fecha_actualizacion": "datetime"
}
```

### Estados Disponibles
- `true` - Residente activo y disponible
- `false` - Residente inactivo

### Campos Requeridos para Crear
- `residenteName`: Nombre completo del residente (2-200 caracteres)
- `residenteCode`: Cédula única del residente (8-20 caracteres)
- `ResidenteEmail`: Email único válido
- `registro_medico`: Registro médico único (5-50 caracteres)
- `isActive`: Estado activo (true/false, por defecto: true)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/residentes/
**Crear nuevo residente**

Body:
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "residenteCode": "12345678",
    "ResidenteEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "observaciones": "Residente de patología con 2 años de experiencia"
}
```

Respuesta (201):
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "residenteCode": "12345678",
    "ResidenteEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/residentes/
**Listar residentes con filtros**

URL con parámetros:
- `http://localhost:8000/api/v1/residentes/` (todos los residentes)
- `http://localhost:8000/api/v1/residentes/?skip=0&limit=10` (paginación)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200):
```json
{
    "residentes": [
        {
            "residenteName": "Carlos Eduardo Rodríguez Martínez",
            "residenteCode": "12345678",
            "ResidenteEmail": "carlos.rodriguez@hospital.com",
            "registro_medico": "RM12345",
            "isActive": true,
            "observaciones": "Residente de patología con 2 años de experiencia",
            "fecha_creacion": "2023-09-07T10:30:00Z",
            "fecha_actualizacion": "2023-09-07T10:30:00Z"
        },
        {
            "residenteName": "Dr. Juan Carlos Pérez González",
            "residenteCode": "87654321",
            "ResidenteEmail": "juan.perez@hospital.com",
            "registro_medico": "MP-2024-001",
            "isActive": true,
            "observaciones": "Residente de anatomía patológica",
            "fecha_creacion": "2023-09-07T10:30:00Z",
            "fecha_actualizacion": "2023-09-07T10:30:00Z"
        }
    ],
    "total": 2,
    "skip": 0,
    "limit": 10,
    "has_next": false,
    "has_prev": false
}
```

### 3. GET http://localhost:8000/api/v1/residentes/{residente_code}
**Obtener residente específico por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "residenteCode": "12345678",
    "ResidenteEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/residentes/{residente_code}
**Actualizar residente por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body:
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "observaciones": "Residente de patología y neuropatología con 2 años de experiencia"
}
```

Respuesta (200):
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "residenteCode": "12345678",
    "ResidenteEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "observaciones": "Residente de patología y neuropatología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T12:45:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/residentes/{residente_code}
**Eliminar residente por código (eliminación permanente)**

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678`

Body: (sin body)

Respuesta (204): (sin contenido)

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. GET http://localhost:8000/api/v1/residentes/search
**Búsqueda avanzada de residentes**

URL con parámetros:
- `http://localhost:8000/api/v1/residentes/search?q=carlos` (búsqueda general)
- `http://localhost:8000/api/v1/residentes/search?q=12345678` (búsqueda por código)
- `http://localhost:8000/api/v1/residentes/search?q=carlos.rodriguez@hospital.com` (búsqueda por email)
- `http://localhost:8000/api/v1/residentes/search?q=RM12345` (búsqueda por registro médico)

Parámetros de consulta:
- `q`: Término de búsqueda que busca en nombre, código, email y registro médico (opcional)
- `especialidad`: Filtrar por especialidad (opcional)
- `estado`: Filtrar por estado (opcional)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200): (similar al endpoint GET principal)

### 6.2. PUT http://localhost:8000/api/v1/residentes/{residente_code}/estado
**Cambiar estado activo/inactivo por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/residentes/12345678/estado`

Body:
```json
{
    "isActive": false
}
```

Respuesta (200):
```json
{
    "residenteName": "Carlos Eduardo Rodríguez Martínez",
    "residenteCode": "12345678",
    "ResidenteEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": false,
    "observaciones": "Residente de patología con 2 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T14:10:00Z"
}
```

## Casos de Error

### Cédula Duplicada (400)
```json
{
    "detail": "Ya existe un residente con la cédula 12345678"
}
```

### Email Duplicado (400)
```json
{
    "detail": "Ya existe un residente con el email carlos.rodriguez@hospital.com"
}
```

### Registro Médico Duplicado (400)
```json
{
    "detail": "Ya existe un residente con el registro médico RM12345"
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
            "loc": ["body", "residenteName"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "residenteCode"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "ResidenteEmail"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "registro_medico"],
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

### 1. Registro de Nuevo Residente
**Escenario:** Registrar un nuevo residente en el sistema

**Pasos:**
1. Hacer POST a `/api/v1/residentes/` (sin autenticación requerida)
2. Incluir campos requeridos: `residenteName`, `residenteCode`, `ResidenteEmail`, `registro_medico`
3. Verificar que email, cédula y registro médico sean únicos
4. Establecer `isActive` como `true` por defecto

### 2. Búsqueda de Residentes
**Escenario:** Obtener lista de residentes disponibles

**Pasos:**
1. Hacer GET a `/api/v1/residentes/` (muestra residentes activos)
2. Usar búsqueda avanzada con `/api/v1/residentes/search?q=término`

### 3. Actualización de Estado
**Escenario:** Activar o desactivar residente

**Pasos:**
1. Hacer PUT a `/api/v1/residentes/{residente_code}/estado`
2. El sistema alterna automáticamente entre activo/inactivo
3. Eficiente y directo usando código de residente

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
4. Para activar/desactivar usar PUT `/api/v1/residentes/{residente_code}/estado`

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
    "residenteName": "María Elena García López",
    "residenteCode": "87654321",
    "ResidenteEmail": "maria.garcia@hospital.com",
    "registro_medico": "RM54321",
    "isActive": true,
    "observaciones": "Residente de anatomía patológica - segundo año"
}
```

### Residente de Patología Forense
```json
{
    "residenteName": "Juan Carlos Mendoza Silva",
    "residenteCode": "11223344",
    "ResidenteEmail": "juan.mendoza@medicina-legal.gov.co",
    "registro_medico": "RM11223",
    "isActive": true,
    "observaciones": "Residente de patología forense - primer año"
}
```

### Residente de Neuropatología
```json
{
    "residenteName": "Ana Sofía Ramírez Torres",
    "residenteCode": "55667788",
    "ResidenteEmail": "ana.ramirez@neurologia.com",
    "registro_medico": "RM55667",
    "isActive": true,
    "observaciones": "Residente de neuropatología - tercer año"
}
```

### Residente de Citopatología
```json
{
    "residenteName": "Luis Fernando Vargas Herrera",
    "residenteCode": "99887766",
    "ResidenteEmail": "luis.vargas@laboratorio.com",
    "registro_medico": "RM99887",
    "isActive": false,
    "observaciones": "Residente de citopatología - actualmente en rotación externa"
}
```

## Resumen de Características del Módulo

### ✅ Funcionalidades Implementadas
- **CRUD Completo**: Crear, leer, actualizar y eliminar residentes
- **Sin Autenticación**: Todos los endpoints son públicos
- **Búsqueda Avanzada**: Búsqueda por múltiples campos con un solo parámetro
- **Gestión de Estados**: Activar/desactivar residentes
- **Estadísticas**: Métricas generales del sistema
- **Eliminación Permanente**: Eliminación real de registros (no soft delete)

### 🔧 Endpoints Disponibles
1. `POST /api/v1/residentes/` - Crear residente
2. `GET /api/v1/residentes/` - Listar residentes activos
3. `GET /api/v1/residentes/search` - Búsqueda avanzada
4. `GET /api/v1/residentes/{code}` - Obtener residente específico
5. `PUT /api/v1/residentes/{code}` - Actualizar residente
6. `PUT /api/v1/residentes/{code}/estado` - Cambiar estado activo/inactivo
7. `DELETE /api/v1/residentes/{code}` - Eliminación permanente

### ⚠️ Consideraciones Importantes
- **Sin Autenticación**: Considerar implementar seguridad en producción
- **Eliminación Permanente**: La operación DELETE es irreversible
- **Separación de Funciones**: Eliminación vs Activación/Desactivación
- **Validaciones**: Campos únicos (email, código, registro médico)
- **Búsqueda Unificada**: Un solo parámetro `q` para búsqueda general
- **Sin Campo Firma**: A diferencia del módulo patólogos, los residentes no manejan firmas digitales