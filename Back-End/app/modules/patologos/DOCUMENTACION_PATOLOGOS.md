# Guía de Patólogos - Postman

## ⚠️ IMPORTANTE: MÓDULO SIN AUTENTICACIÓN
**Este módulo NO requiere autenticación.** Todos los endpoints están disponibles sin necesidad de tokens de acceso o credenciales de usuario. Esto facilita las pruebas y la integración, pero debe considerarse la seguridad en entornos de producción.

## Estructura del Modelo

### Campos del Modelo Patologo
```json
{
    "_id": "ObjectId MongoDB",
    "patologoName": "string (nombre completo del patólogo)",
    "patologoCode": "string (cédula única del patólogo)",
    "PatologoEmail": "string (email único)",
    "registro_medico": "string (registro médico único)",
    "isActive": "boolean (estado activo/inactivo)",
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
- `patologoName`: Nombre completo del patólogo (2-200 caracteres)
- `patologoCode`: Cédula única del patólogo (6-10 caracteres)
- `PatologoEmail`: Email único válido
- `registro_medico`: Registro médico único (5-50 caracteres)
- `isActive`: Estado activo (true/false, por defecto: true)
- `observaciones`: Notas adicionales (opcional, máx 500 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/patologos/
**Crear nuevo patólogo**

Body:
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "patologoCode": "12345678",
    "PatologoEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia"
}
```

Respuesta (201):
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "patologoCode": "12345678",
    "PatologoEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T10:30:00Z"
}
```

### 2. GET http://localhost:8000/api/v1/patologos/
**Listar patólogos con filtros**

URL con parámetros:
- `http://localhost:8000/api/v1/patologos/` (todos los patólogos)
- `http://localhost:8000/api/v1/patologos/?skip=0&limit=10` (paginación)

Parámetros de consulta:
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200):
```json
{
    "patologos": [
        {
            "patologoName": "Carlos Eduardo Rodríguez Martínez",
            "patologoCode": "12345678",
            "PatologoEmail": "carlos.rodriguez@hospital.com",
            "registro_medico": "RM12345",
            "isActive": true,
            "firma": "https://storage.com/firmas/carlos_rodriguez.png",
            "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
            "fecha_creacion": "2023-09-07T10:30:00Z",
            "fecha_actualizacion": "2023-09-07T10:30:00Z"
        },
        {
            "patologoName": "Dr. Juan Carlos Pérez González",
            "patologoCode": "12345678",
            "PatologoEmail": "juan.perez@hospital.com",
            "registro_medico": "MP-2024-001",
            "isActive": true,
            "firma": "",
            "observaciones": "Especialista en anatomía patológica",
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

### 3. GET http://localhost:8000/api/v1/patologos/{patologo_code}
**Obtener patólogo específico por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body: (sin body)

Respuesta (200):
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "patologoCode": "12345678",
    "PatologoEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T11:15:00Z"
}
```

### 4. PUT http://localhost:8000/api/v1/patologos/{patologo_code}
**Actualizar patólogo por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body:
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "firma": "https://storage.com/firmas/carlos_rodriguez_updated.png",
    "observaciones": "Especialista en patología oncológica y neuropatología con 15 años de experiencia"
}
```

Respuesta (200):
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "patologoCode": "12345678",
    "PatologoEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": true,
    "firma": "https://storage.com/firmas/carlos_rodriguez_updated.png",
    "observaciones": "Especialista en patología oncológica y neuropatología con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T12:45:00Z"
}
```

### 5. DELETE http://localhost:8000/api/v1/patologos/{patologo_code}
**Eliminar patólogo por código (eliminación permanente)**

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678`

Body: (sin body)

Respuesta (204): (sin contenido)

⚠️ **IMPORTANTE**: Esta operación elimina permanentemente el registro de la base de datos. No se puede deshacer.

### 6. GET http://localhost:8000/api/v1/patologos/search
**Búsqueda avanzada de patólogos**

URL con parámetros:
- `http://localhost:8000/api/v1/patologos/search?q=carlos` (búsqueda general)
- `http://localhost:8000/api/v1/patologos/search?q=12345678` (búsqueda por código)
- `http://localhost:8000/api/v1/patologos/search?q=carlos.rodriguez@hospital.com` (búsqueda por email)
- `http://localhost:8000/api/v1/patologos/search?q=RM12345` (búsqueda por registro médico)

Parámetros de consulta:
- `q`: Término de búsqueda que busca en nombre, código, email y registro médico (opcional)
- `especialidad`: Filtrar por especialidad (opcional)
- `estado`: Filtrar por estado (opcional)
- `skip`: Registros a omitir (default: 0)
- `limit`: Máximo registros (default: 10, max: 100)

Body: (sin body)

Respuesta (200): (similar al endpoint GET principal)



### 6.2. PUT http://localhost:8000/api/v1/patologos/{patologo_code}/estado
**Cambiar estado activo/inactivo por código**

Ejemplos de URL:
- `http://localhost:8000/api/v1/patologos/12345678/estado`

Body:
```json
{
    "isActive": false
}
```

Respuesta (200):
```json
{
    "patologoName": "Carlos Eduardo Rodríguez Martínez",
    "patologoCode": "12345678",
    "PatologoEmail": "carlos.rodriguez@hospital.com",
    "registro_medico": "RM12345",
    "isActive": false,
    "firma": "https://storage.com/firmas/carlos_rodriguez.png",
    "observaciones": "Especialista en patología oncológica con 15 años de experiencia",
    "fecha_creacion": "2023-09-07T10:30:00Z",
    "fecha_actualizacion": "2023-09-07T14:10:00Z"
}
```





## Casos de Error

### Cédula Duplicada (400)
```json
{
    "detail": "Ya existe un patólogo con la cédula 12345678"
}
```

### Email Duplicado (400)
```json
{
    "detail": "Ya existe un patólogo con el email carlos.rodriguez@hospital.com"
}
```

### Registro Médico Duplicado (400)
```json
{
    "detail": "Ya existe un patólogo con el registro médico RM12345"
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
            "loc": ["body", "patologoName"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "patologoCode"],
            "msg": "field required",
            "type": "value_error.missing"
        },
        {
            "loc": ["body", "PatologoEmail"],
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

### 1. Registro de Nuevo Patólogo
**Escenario:** Registrar un nuevo patólogo en el sistema

**Pasos:**
1. Hacer POST a `/api/v1/patologos/` (sin autenticación requerida)
2. Incluir campos requeridos: `patologoName`, `patologoCode`, `PatologoEmail`, `registro_medico`
3. Verificar que email, cédula y registro médico sean únicos
4. Establecer `isActive` como `true` por defecto
5. Dejar `firma` vacío inicialmente

### 2. Búsqueda de Patólogos
**Escenario:** Obtener lista de patólogos disponibles

**Pasos:**
1. Hacer GET a `/api/v1/patologos/` (muestra patólogos activos)
2. Usar búsqueda avanzada con `/api/v1/patologos/search?q=término`

### 3. Actualización de Estado
**Escenario:** Activar o desactivar patólogo

**Pasos:**
1. Hacer PUT a `/api/v1/patologos/{patologo_code}/estado`
2. El sistema alterna automáticamente entre activo/inactivo
3. Eficiente y directo usando código de patólogo



### 5. Búsqueda Avanzada
**Escenario:** Encontrar patólogos con criterios específicos

**Pasos:**
1. Usar GET `/api/v1/patologos/search?q=término` para búsqueda general
2. El parámetro `q` busca en nombre, código, email y registro médico
3. Aplicar paginación con `skip` y `limit` si es necesario



### 7. Eliminación Permanente
**Escenario:** Remover patólogo del sistema (usar con EXTREMA precaución)

**⚠️ ADVERTENCIA:** Esta operación elimina permanentemente el registro de la base de datos y NO se puede deshacer.

**Pasos:**
1. Hacer DELETE a `/api/v1/patologos/{patologo_code}`
2. Confirmar que no hay casos pendientes asociados
3. Operación irreversible - el registro se elimina completamente
4. Para activar/desactivar usar PUT `/api/v1/patologos/{patologo_code}/estado`

### 8. Consulta por Código
**Escenario:** Buscar patólogo específico usando su cédula

**Pasos:**
1. Hacer GET a `/api/v1/patologos/{patologo_code}`
2. Usar la cédula del patólogo como identificador
3. Natural y directo usando código
4. Útil para integraciones externas

## Ejemplos de Patólogos

### Patólogo de Anatomía Patológica
```json
{
    "patologoName": "María Elena García López",
    "patologoCode": "87654321",
    "PatologoEmail": "maria.garcia@hospital.com",
    "registro_medico": "RM54321",
    "isActive": true,
    "firma": "",
    "observaciones": "Especialista en anatomía patológica"
}
```

### Patólogo Forense
```json
{
    "patologoName": "Juan Carlos Mendoza Silva",
    "patologoCode": "11223344",
    "PatologoEmail": "juan.mendoza@medicina-legal.gov.co",
    "registro_medico": "RM11223",
    "isActive": true,
    "firma": "",
    "observaciones": "Especialista en patología forense y anatomía patológica"
}
```

### Neuropatólogo
```json
{
    "patologoName": "Ana Sofía Ramírez Torres",
    "patologoCode": "55667788",
    "PatologoEmail": "ana.ramirez@neurologia.com",
    "registro_medico": "RM55667",
    "isActive": true,
    "firma": "",
    "observaciones": "Especialista en neuropatología y anatomía patológica"
}
```

### Citopatólogo
```json
{
    "patologoName": "Luis Fernando Vargas Herrera",
    "patologoCode": "99887766",
    "PatologoEmail": "luis.vargas@laboratorio.com",
    "registro_medico": "RM99887",
    "isActive": false,
    "firma": "",
    "observaciones": "Especialista en citopatología - actualmente en vacaciones"
}
```

## Resumen de Características del Módulo

### ✅ Funcionalidades Implementadas
- **CRUD Completo**: Crear, leer, actualizar y eliminar patólogos
- **Sin Autenticación**: Todos los endpoints son públicos
- **Búsqueda Avanzada**: Búsqueda por múltiples campos con un solo parámetro
- **Gestión de Estados**: Activar/desactivar patólogos
- **Gestión de Firmas**: Actualización específica de firmas digitales
- **Estadísticas**: Métricas generales del sistema
- **Eliminación Permanente**: Eliminación real de registros (no soft delete)
### 🔧 Endpoints Disponibles
1. `POST /api/v1/patologos/` - Crear patólogo
2. `GET /api/v1/patologos/` - Listar patólogos activos
3. `GET /api/v1/patologos/search` - Búsqueda avanzada
4. `GET /api/v1/patologos/{code}` - Obtener patólogo específico
5. `PUT /api/v1/patologos/{code}` - Actualizar patólogo
6. `PUT /api/v1/patologos/{code}/estado` - Cambiar estado activo/inactivo
7. `DELETE /api/v1/patologos/{code}` - Eliminación permanente

### ⚠️ Consideraciones Importantes
- **Sin Autenticación**: Considerar implementar seguridad en producción
- **Eliminación Permanente**: La operación DELETE es irreversible
- **Separación de Funciones**: Eliminación vs Activación/Desactivación
- **Validaciones**: Campos únicos (email, código, registro médico)
- **Búsqueda Unificada**: Un solo parámetro `q` para búsqueda general