# Documentación del Módulo de Tickets - Sistema PathSys LIME

## Descripción General

El módulo de tickets proporciona un sistema completo de gestión de tickets de soporte para el sistema PathSys LIME. Permite a los usuarios crear, gestionar y dar seguimiento a tickets de soporte con diferentes categorías y estados.

## Características Principales

### ✅ Sistema de Consecutivos
- **Formato único**: T-YYYY-NNN (ej: T-2025-001, T-2025-002)
- **Reinicio anual**: Los consecutivos reinician cada año
- **Identificador principal**: Se usa `ticket_code` en lugar de ObjectId

### ✅ Categorías de Tickets
- **bug**: Errores o problemas en el sistema
- **feature**: Solicitudes de nuevas características
- **question**: Preguntas sobre el uso del sistema
- **technical**: Problemas técnicos generales

### ✅ Estados de Tickets
- **open**: Ticket recién creado, pendiente de atención
- **in-progress**: Ticket siendo trabajado
- **resolved**: Ticket resuelto, pendiente de verificación
- **closed**: Ticket cerrado definitivamente

### ✅ Gestión de Imágenes
- **Una imagen por ticket**: Simplificado del sistema original de múltiples archivos
- **Formatos soportados**: JPG, PNG, GIF, WEBP
- **Tamaño máximo**: 5MB por imagen
- **Validación automática**: Tipo MIME y extensión

### ✅ Permisos y Seguridad
- **Usuarios autenticados**: Pueden crear tickets y ver solo los suyos
- **Administradores**: Pueden ver todos los tickets y cambiar estados
- **Protección de archivos**: Solo el creador o admins pueden gestionar imágenes

## Endpoints de la API

### Base URL: `/api/v1/tickets`

#### 🔓 Endpoints Públicos (usuarios autenticados)

**POST /** - Crear ticket
```json
{
  "titulo": "Error al cargar casos",
  "categoria": "bug",
  "descripcion": "Descripción detallada del problema",
  "imagen": "URL opcional de imagen"
}
```

**GET /** - Listar tickets (paginado)
- Usuarios: Solo sus tickets
- Admins: Todos los tickets
- Parámetros: `skip`, `limit`, `sort_by`, `sort_order`

**POST /search** - Búsqueda avanzada
```json
{
  "estado": "open",
  "categoria": "bug",
  "search_text": "texto a buscar",
  "date_from": "2025-01-01T00:00:00Z",
  "date_to": "2025-12-31T23:59:59Z"
}
```

**GET /{ticket_code}** - Obtener ticket específico
- Verificación de permisos automática

**PUT /{ticket_code}** - Actualizar ticket
- Solo campos permitidos según permisos

#### 🔒 Endpoints Solo Administradores

**DELETE /{ticket_code}** - Eliminar ticket

**PATCH /{ticket_code}/status** - Cambiar estado
```json
{
  "estado": "resolved"
}
```

#### 📎 Endpoints de Gestión de Imágenes

**POST /{ticket_code}/upload-image** - Subir imagen
- Multipart/form-data con archivo

**DELETE /{ticket_code}/image** - Eliminar imagen

#### 🛠️ Endpoints Utilitarios

**GET /siguiente-consecutivo** - Consultar próximo código
**GET /test** - Endpoint de prueba

## Modelo de Datos

### Ticket (MongoDB)
```python
{
  "_id": ObjectId,                          # ID interno MongoDB
  "ticket_code": "T-2025-001",            # IDENTIFICADOR PRINCIPAL
  "titulo": "Título del ticket",           # max 100 chars
  "categoria": "bug|feature|question|technical",
  "descripcion": "Descripción detallada",  # max 500 chars
  "imagen": "URL opcional",                # Single image URL
  "fecha_ticket": datetime,                # Fecha de creación
  "estado": "open|in-progress|resolved|closed",
  "created_by": "user_id",                 # ID del creador
  "fecha_creacion": datetime,
  "fecha_actualizacion": datetime
}
```

### Consecutivos (MongoDB)
```python
{
  "year": 2025,                           # Año
  "last_number": 15,                      # Último número usado
  "fecha_actualizacion": datetime
}
```

## Validaciones y Reglas de Negocio

### ✅ Validaciones de Entrada
- **Título**: Requerido, 1-100 caracteres, sin espacios en blanco
- **Descripción**: Requerida, 1-500 caracteres, sin espacios en blanco
- **Categoría**: Debe ser un valor válido del enum
- **Código**: Formato automático T-YYYY-NNN, validación estricta

### ✅ Permisos
- **Creación**: Todos los usuarios autenticados
- **Visualización**: Solo creador o administradores
- **Actualización**: Solo creador (campos limitados) o administradores
- **Eliminación**: Solo administradores
- **Cambio de estado**: Solo administradores

### ✅ Gestión de Archivos
- **Validación automática**: Tipo MIME, extensión, tamaño
- **Reemplazo**: Nueva imagen reemplaza la anterior automáticamente
- **Limpieza**: Eliminación de archivos huérfanos al eliminar tickets

## Integración con Frontend

### Campos Actualizados
- `title` → `titulo` (español)
- `category` → `categoria` (español)
- `description` → `descripcion` (español)
- `status` → `estado` (español)
- `createdAt` → `fecha_ticket` (español)
- `id` → `ticket_code` (identificador principal)
- `attachments[]` → `imagen` (imagen única)

### Servicios API
- Nuevo servicio `TicketsService` con métodos para todos los endpoints
- Integración con sistema de autenticación existente
- Manejo de errores centralizado

### Componentes Actualizados
- **NewTicket.vue**: Formulario simplificado con imagen única
- **ActualTickets.vue**: Lista con búsqueda y filtros
- **TicketDetailModal.vue**: Vista de detalle con imagen única
- **SupportView.vue**: Integración con API real

## Configuración

### Variables de Entorno
```bash
TICKETS_UPLOAD_DIR=/app/uploads/tickets/images
TICKETS_MAX_IMAGE_SIZE=5242880  # 5MB
TICKETS_ALLOWED_TYPES=image/*
TICKETS_RATE_LIMIT=10  # tickets per hour per user
```

### Índices MongoDB Requeridos
```javascript
// Índice único principal
db.tickets.createIndex({"ticket_code": 1}, {"unique": true})

// Índices de consulta optimizada
db.tickets.createIndex({"created_by": 1, "fecha_ticket": -1})
db.tickets.createIndex({"estado": 1, "categoria": 1})
db.tickets.createIndex({"titulo": "text", "descripcion": "text"})

// Índice para consecutivos
db.consecutivos_tickets.createIndex({"year": 1}, {"unique": true})
```

## Logs y Monitoreo

### Eventos Registrados
- Creación de tickets con detalles del usuario
- Cambios de estado por administradores
- Upload/eliminación de imágenes
- Eliminación de tickets
- Errores y excepciones

### Métricas Disponibles
- Tickets por categoría y estado
- Tiempo promedio de resolución
- Usuarios más activos
- Errores por endpoint

## Seguridad

### Protecciones Implementadas
- **Autenticación obligatoria**: Todos los endpoints requieren token válido
- **Autorización granular**: Verificación de permisos por endpoint
- **Validación de archivos**: Prevención de upload de archivos maliciosos
- **Rate limiting**: Prevención de spam de tickets
- **Sanitización**: Limpieza automática de campos de texto

### Consideraciones Adicionales
- Los archivos se almacenan con nombres únicos para evitar conflictos
- Validación de tamaño para prevenir ataques de negación de servicio
- Logging completo para auditoría y debugging

## Estado del Módulo

### ✅ Completado
- Modelos y esquemas de datos
- Repositorios con operaciones CRUD
- Servicios con lógica de negocio
- Endpoints de API con autenticación
- Sistema de consecutivos
- Gestión de imágenes
- Validaciones y permisos
- Documentación completa

### 🔄 En Progreso
- Integración con frontend existente
- Pruebas de integración completas

### 📋 Pendiente
- Notificaciones por email
- Dashboard de administración
- Reportes y estadísticas
- Migración de datos existentes

---

**Fecha de creación**: Enero 2025  
**Versión**: 1.0  
**Estado**: Desarrollo Activo
