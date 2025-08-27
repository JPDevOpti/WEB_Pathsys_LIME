# Documentación del Módulo de Autenticación

## 🔐 IMPORTANTE: MÓDULO DE SEGURIDAD
**Este módulo maneja la autenticación y autorización del sistema.** Todos los endpoints relacionados con login, tokens y gestión de usuarios están centralizados aquí. Es fundamental para la seguridad del sistema.

### Características de Seguridad
- **Rate Limiting**: Protección contra ataques de fuerza bruta (5 intentos por 5 minutos)
- **Validación de Roles**: Verificación automática contra RolEnum
- **Contraseñas Hasheadas**: Solo se permiten contraseñas con hash bcrypt
- **Logging Estructurado**: Auditoría completa de intentos de acceso
- **Validación de Tokens**: Verificación de tipo y expiración
- **Manejo de Excepciones**: Respuestas de error seguras sin información sensible

## Estructura del Modelo

### Campos del Modelo AuthUser (Coincide con la BD)
```json
{
    "id": "string (ID único del usuario)",
    "email": "string (email único del usuario)",
    "nombre": "string (nombre completo del usuario)",
    "rol": "string (rol del usuario: administrador, patologo, auxiliar, residente, paciente)",
    "is_active": "boolean (estado activo del usuario)",
    "fecha_creacion": "datetime (fecha de creación)",
    "fecha_actualizacion": "datetime (fecha de actualización)",
    "ultimo_acceso": "datetime (fecha del último acceso, opcional)"
}
```

### Estructura Real en la Base de Datos
```json
{
    "_id": "ObjectId",
    "nombre": "Leiby Alejandra Medina Zuluaica",
    "email": "32108690.lam@udea.edu.co",
    "rol": "patologo",
    "password_hash": "$2b$12$h3S8PCm75/bPWsCIhdd1bOaHVlrT6509jQFB0nEBaUM0kw6d0P8Oq",
    "is_active": true,
    "fecha_creacion": "2025-08-27T18:51:40.717Z",
    "fecha_actualizacion": "2025-08-27T18:51:40.717Z"
}
```

### Roles Disponibles (Validados contra RolEnum)
- `administrador` - Administrador del sistema con acceso completo
- `patologo` - Patólogo que realiza diagnósticos
- `auxiliar` - Personal auxiliar del laboratorio
- `residente` - Médico residente en patología
- `paciente` - Paciente del sistema (acceso limitado)

### Estados Disponibles
- `true` - Usuario activo y puede acceder al sistema
- `false` - Usuario inactivo, acceso denegado

### Campos Requeridos para Login
- `email`: Email único válido del usuario
- `password`: Contraseña del usuario (mínimo 6, máximo 128 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/auth/login
**Iniciar sesión en el sistema**

**Protección de Seguridad:**
- Rate limiting: 5 intentos por 5 minutos por email
- Validación de contraseñas hasheadas
- Verificación de usuario activo
- Validación de roles contra RolEnum

Body:
```json
{
    "email": "usuario@ejemplo.com",
    "password": "mi_contraseña_segura"
}
```

Response 200:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 86400,
    "user": {
        "id": "507f1f77bcf86cd799439011",
        "email": "usuario@ejemplo.com",
        "nombre": "Juan Pérez",
        "rol": "patologo",
        "roles": ["patologo"]
    }
}
```

Response 429 (Rate Limit):
```json
{
    "detail": "Demasiados intentos de login. Intente nuevamente en 5 minutos."
}
```

### 2. POST http://localhost:8000/api/v1/auth/refresh
**Renovar token de acceso**

**Protección de Seguridad:**
- Validación de tipo de token (debe ser "refresh")
- Verificación de usuario activo
- Validación de roles actualizados

Body:
```json
{
    "refresh_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
}
```

Response 200:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 86400
}
```

### 3. POST http://localhost:8000/api/v1/auth/logout
**Cerrar sesión**

**Protección de Seguridad:**
- Validación de token de acceso
- Logging de sesiones cerradas

Headers:
```
Authorization: Bearer {access_token}
```

Body: (sin body)

Response 200:
```json
{
    "message": "Sesión cerrada exitosamente"
}
```

### 4. GET http://localhost:8000/api/v1/auth/me
**Obtener información del usuario actual**

**Protección de Seguridad:**
- Validación de token de acceso
- Verificación de usuario activo
- Respuesta consistente con login

Headers:
```
Authorization: Bearer {access_token}
```

Body: (sin body)

Response 200:
```json
{
    "id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "nombres": "Juan",
    "apellidos": "Pérez",
    "roles": ["patologo"],
    "activo": true,
    "ultimo_acceso": "2024-01-15T10:30:00Z"
}
```

### 5. GET http://localhost:8000/api/v1/auth/verify
**Verificar validez del token**

**Protección de Seguridad:**
- Validación de token de acceso
- Cálculo de tiempo restante

Headers:
```
Authorization: Bearer {access_token}
```

Body: (sin body)

Response 200:
```json
{
    "valid": true,
    "user_id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "username": "usuario",
    "roles": ["patologo"],
    "expires_in": 7200
}
```

## Códigos de Error

### 400 Bad Request
```json
{
    "detail": "Datos de entrada inválidos"
}
```

### 401 Unauthorized
```json
{
    "detail": "Credenciales inválidas"
}
```

### 403 Forbidden
```json
{
    "detail": "Usuario inactivo o sin permisos"
}
```

### 404 Not Found
```json
{
    "detail": "Usuario no encontrado"
}
```

### 422 Validation Error
```json
{
    "detail": [
        {
            "loc": ["body", "email"],
            "msg": "field required",
            "type": "value_error.missing"
        }
    ]
}
```

### 429 Too Many Requests
```