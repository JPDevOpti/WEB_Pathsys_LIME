# Documentación del Módulo de Autenticación

## 🔐 IMPORTANTE: MÓDULO DE SEGURIDAD
**Este módulo maneja la autenticación y autorización del sistema.** Todos los endpoints relacionados con login, tokens y gestión de usuarios están centralizados aquí. Es fundamental para la seguridad del sistema.

## Estructura del Modelo

### Campos del Modelo AuthUser
```json
{
    "id": "string (ID único del usuario)",
    "email": "string (email único del usuario)",
    "rol": "string (rol único: admin, patologo, recepcionista)",
    "activo": "boolean (estado activo/inactivo)",
    "ultimo_acceso": "datetime (fecha del último acceso, opcional)"
}
```

### Roles Disponibles
- `admin` - Administrador del sistema con acceso completo
- `patologo` - Patólogo que realiza diagnósticos
- `recepcionista` - Personal de recepción

### Estados Disponibles
- `true` - Usuario activo y puede acceder al sistema
- `false` - Usuario inactivo, acceso denegado

### Campos Requeridos para Login
- `email`: Email único válido del usuario
- `password`: Contraseña del usuario (mínimo 6 caracteres)

## Endpoints Disponibles

### 1. POST http://localhost:8000/api/v1/auth/login
**Iniciar sesión en el sistema**

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
    "token_type": "bearer",
    "expires_in": 3600,
    "user": {
        "id": "507f1f77bcf86cd799439011",
        "email": "usuario@ejemplo.com",
        "rol": "patologo",
        "activo": true,
        "ultimo_acceso": "2024-01-15T10:30:00Z"
    }
}
```

### 2. POST http://localhost:8000/api/v1/auth/refresh
**Renovar token de acceso**

Headers:
```
Authorization: Bearer {access_token}
```

Body: (sin body)

Response 200:
```json
{
    "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
    "token_type": "bearer",
    "expires_in": 3600
}
```

### 3. POST http://localhost:8000/api/v1/auth/logout
**Cerrar sesión**

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
    "rol": "patologo",
    "activo": true,
    "ultimo_acceso": "2024-01-15T10:30:00Z"
}
```

### 5. POST http://localhost:8000/api/v1/auth/verify-token
**Verificar validez del token**

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
    "rol": "patologo",
    "expires_at": "2024-01-15T11:30:00Z"
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

### 500 Internal Server Error
```json
{
    "detail": "Error interno del servidor"
}
```

## Validaciones

### Campos Únicos
- `email`: Debe ser único en todo el sistema

### Reglas de Validación

1. **email**: Formato de email válido, único en el sistema
2. **password**: Mínimo 6 caracteres para login
3. **rol**: Debe ser uno de los valores permitidos (admin, patologo, recepcionista)
4. **activo**: Valor booleano (true/false)

### Seguridad del Token

1. **Expiración**: Los tokens tienen una duración de 1 hora (3600 segundos)
2. **Algoritmo**: JWT con algoritmo HS256
3. **Payload**: Contiene user_id, email, rol, fecha de emisión y expiración
4. **Renovación**: Los tokens pueden renovarse antes de su expiración

## Casos de Uso

1. **Autenticación de Usuarios**
   - Login con email y contraseña
   - Verificación de credenciales
   - Generación de tokens de acceso

2. **Gestión de Sesiones**
   - Mantenimiento de sesiones activas
   - Renovación automática de tokens
   - Cierre de sesión seguro

3. **Control de Acceso**
   - Verificación de permisos por rol
   - Validación de tokens en cada request
   - Control de usuarios activos/inactivos

4. **Seguridad**
   - Protección contra accesos no autorizados
   - Gestión segura de contraseñas
   - Auditoría de accesos

## Notas Importantes

1. **Tokens JWT**: Se utilizan tokens JWT para mantener la sesión
2. **Expiración**: Los tokens expiran en 1 hora y deben renovarse
3. **Roles**: Cada usuario tiene un único rol que determina sus permisos
4. **Estado Activo**: Solo usuarios activos pueden iniciar sesión
5. **Email Único**: Cada usuario debe tener un email único
6. **Último Acceso**: Se registra automáticamente en cada login exitoso

## Ejemplos de Integración

### 1. Login de usuario
```bash
curl -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "patologo@hospital.com",
    "password": "contraseña123"
  }'
```

### 2. Obtener información del usuario actual
```bash
curl "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 3. Renovar token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 4. Verificar token
```bash
curl -X POST "http://localhost:8000/api/v1/auth/verify-token" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 5. Cerrar sesión
```bash
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9..."
```

### 6. Ejemplo de flujo completo de autenticación
```bash
# 1. Login y obtener token
TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@hospital.com",
    "password": "admin123"
  }' | jq -r '.access_token')

# 2. Usar token para obtener información del usuario
curl "http://localhost:8000/api/v1/auth/me" \
  -H "Authorization: Bearer $TOKEN"

# 3. Verificar que el token es válido
curl -X POST "http://localhost:8000/api/v1/auth/verify-token" \
  -H "Authorization: Bearer $TOKEN"

# 4. Renovar token antes de que expire
NEW_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/refresh" \
  -H "Authorization: Bearer $TOKEN" | jq -r '.access_token')

# 5. Cerrar sesión
curl -X POST "http://localhost:8000/api/v1/auth/logout" \
  -H "Authorization: Bearer $NEW_TOKEN"
```

## Estructura de Datos del Token

### Payload del JWT
```json
{
    "user_id": "507f1f77bcf86cd799439011",
    "email": "usuario@ejemplo.com",
    "rol": "patologo",
    "exp": 1642680000,
    "iat": 1642676400
}
```

### Headers del JWT
```json
{
    "typ": "JWT",
    "alg": "HS256"
}
```

## Middleware de Autenticación

Para proteger endpoints, se debe incluir el header de autorización:

```
Authorization: Bearer {access_token}
```

El sistema validará automáticamente:
1. Formato correcto del token
2. Firma válida del token
3. Token no expirado
4. Usuario activo en el sistema
5. Permisos adecuados según el rol

## Roles y Permisos

### Admin
- Acceso completo al sistema
- Gestión de usuarios
- Configuración del sistema
- Todos los módulos disponibles

### Patologo
- Gestión de casos y diagnósticos
- Firma de resultados
- Consulta de información de pacientes
- Acceso a módulos de patología

### Recepcionista
- Registro de pacientes
- Gestión de citas
- Consulta básica de información
- Módulos de recepción y administración básica