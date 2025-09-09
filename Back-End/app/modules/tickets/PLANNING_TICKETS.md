# Planning del Módulo de Tickets - Sistema PathSys LIME

## 1. Análisis de Arquitectura Actual

### 1.1 Estructura de Módulos Existente
Siguiendo el patrón establecido en otros módulos del proyecto:
```
app/modules/tickets/
├── models/
│   ├── __init__.py
│   └── ticket.py                 # Modelo MongoDB
├── schemas/
│   ├── __init__.py
│   └── ticket.py                 # Esquemas Pydantic para API
├── repositories/
│   ├── __init__.py
│   └── ticket_repository.py      # Operaciones CRUD y consultas
├── services/
│   ├── __init__.py
│   └── ticket_service.py         # Lógica de negocio
├── routes/
│   ├── __init__.py
│   └── ticket_routes.py          # Endpoints FastAPI
├── __init__.py
└── DOCUMENTACION_TICKETS.md      # Documentación del módulo
```

### 1.2 Capas y Responsabilidades
- **Models**: Definición de estructuras de datos para MongoDB
- **Schemas**: Validación y serialización para API REST
- **Repositories**: Acceso a datos y consultas complejas
- **Services**: Lógica de negocio, validaciones, transformaciones
- **Routes**: Definición de endpoints HTTP

## 2. Modelo de Datos

### 2.1 Estructura MongoDB (ticket.py)
```json
{
  "_id": "ObjectId (auto-generado por MongoDB, interno)",
  "ticket_code": "string (formato T-YYYY-NNN, ej: T-2025-001, consecutivo único, CLAVE PRIMARIA)",
  "titulo": "string (max 100 chars, required)",
  "categoria": "TicketCategoryEnum (bug|feature|question|technical)",
  "descripcion": "string (max 500 chars, required)",
  "imagen": "string|null (URL de la imagen adjunta, opcional)",
  "fecha_ticket": "datetime (fecha de creación del ticket)",
  "estado": "TicketStatusEnum (open|in-progress|resolved|closed)",
  "created_by": "string (user_id del creador)",
  "fecha_creacion": "datetime",
  "fecha_actualizacion": "datetime"
}
```

### 2.2 Simplificación del Modelo
- **Eliminado**: `assigned_to`, `attachments[]`, `comments[]` (se simplifica a una sola imagen)
- **Renombrado**: `title` → `titulo`, `category` → `categoria`, `description` → `descripcion`, `status` → `estado`
- **Identificador principal**: `ticket_code` (T-YYYY-NNN) - Se usa SIEMPRE en lugar de `_id`
- **Auto-generado**: `ticket_code` (consecutivo único), `fecha_ticket`
- **Nuevo**: `imagen` (single image URL)

### 2.2.1 Sistema de Consecutivos
- **Formato**: T-YYYY-NNN (ej: T-2025-001, T-2025-002)
- **Única por año**: Reinicia en 001 cada año
- **Índice único**: ticket_code debe ser único en la colección
- **Uso en API**: Todos los endpoints usan ticket_code, nunca _id

### 2.3 Enums
```python
class TicketCategoryEnum(str, Enum):
    BUG = "bug"
    FEATURE = "feature"
    QUESTION = "question"
    TECHNICAL = "technical"

class TicketStatusEnum(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in-progress"
    RESOLVED = "resolved"
    CLOSED = "closed"
```

## 3. Esquemas de API (Pydantic)

### 3.1 Request Schemas
```python
# Crear ticket
TicketCreate:
  - titulo: str (max 100)
  - categoria: TicketCategoryEnum
  - descripcion: str (max 500)
  - imagen: Optional[str] = None  # URL de imagen adjunta

# Actualizar ticket
TicketUpdate:
  - titulo: Optional[str]
  - categoria: Optional[TicketCategoryEnum]
  - descripcion: Optional[str]
  - imagen: Optional[str]
  - estado: Optional[TicketStatusEnum]  # Solo admins

# Búsqueda/filtros
TicketSearch:
  - estado: Optional[TicketStatusEnum]
  - categoria: Optional[TicketCategoryEnum]
  - created_by: Optional[str]
  - search_text: Optional[str]  # Buscar en titulo/descripcion
  - date_from: Optional[datetime]
  - date_to: Optional[datetime]
```

### 3.2 Response Schemas
```python
TicketResponse:
  - ticket_code: str  # IDENTIFICADOR PRINCIPAL (T-YYYY-NNN)
  - titulo: str
  - categoria: TicketCategoryEnum
  - descripcion: str
  - imagen: Optional[str]
  - fecha_ticket: datetime
  - estado: TicketStatusEnum

TicketListResponse:
  - ticket_code: str  # IDENTIFICADOR PRINCIPAL (T-YYYY-NNN)
  - titulo: str
  - categoria: TicketCategoryEnum
  - estado: TicketStatusEnum
  - imagen: Optional[str]
  - fecha_ticket: datetime
```

## 4. Endpoints API

### 4.1 Base URL
`/api/v1/tickets`

### 4.2 Endpoints Principales
```
POST   /                          # Crear ticket
GET    /                          # Listar tickets (paginado + filtros)
POST   /search                    # Búsqueda avanzada (paginado)
GET    /{ticket_code}             # Obtener ticket por CODE (ej: T-2025-001)
PUT    /{ticket_code}             # Actualizar ticket
DELETE /{ticket_code}             # Eliminar ticket (solo admins)

# Gestión de estado (solo admins)
PATCH  /{ticket_code}/status      # Cambiar estado

# Upload de imagen
POST   /{ticket_code}/upload-image     # Subir imagen del ticket
DELETE /{ticket_code}/image            # Eliminar imagen del ticket
```

### 4.3 Parámetros de Paginación
```
?skip=0&limit=20&sort_by=fecha_creacion&sort_order=desc
```

## 5. Permisos y Autenticación

### 5.1 Roles y Permisos
- **Todos los usuarios autenticados**:
  - Crear tickets
  - Ver sus propios tickets
  - Subir/eliminar imagen de sus tickets

- **Administradores**:
  - Ver todos los tickets
  - Cambiar estado de tickets
  - Eliminar tickets

### 5.2 Middleware de Autenticación
- Todos los endpoints requieren autenticación (`requiresAuth: true`)
- Validación de roles mediante `AuthUser` del módulo auth
- Rate limiting para prevenir spam de tickets

## 6. Almacenamiento de Archivos

### 6.1 Estrategia de Imagen
- **Directorio**: `uploads/tickets/images/`
- **Tipos permitidos**: `image/*` (jpg, png, gif, webp)
- **Tamaño máximo**: 5MB por imagen
- **Naming**: `{ticket_code}_{timestamp}.{ext}`

### 6.2 Validaciones
- Tipo MIME validation (solo imágenes)
- Extensión whitelist
- Tamaño de imagen
- Compresión automática si es muy grande

## 7. Notificaciones

### 7.1 Eventos de Notificación
- Ticket creado → Notificar a admins
- Estado cambiado → Notificar al creador

### 7.2 Integración
- Usar servicio de notificaciones existente (`shared/services/notification.py`)
- Email notifications para eventos importantes

## 8. Integración con Frontend

### 8.1 Análisis de Inconsistencias Actuales

**Frontend actual (`@support/`) vs Planning Backend:**

#### 8.1.1 Campos no coincidentes:
```typescript
// ❌ ACTUAL en support.types.ts
interface SupportTicket {
  id: string              // NO existe en planning
  title: string           // Planning usa "titulo"
  category: string        // Planning usa "categoria"
  description: string     // Planning usa "descripcion"
  status: string          // Planning usa "estado"
  createdAt: string       // Planning usa "fecha_ticket"
  attachments: Array      // Planning usa "imagen" (single)
}

// ✅ REQUERIDO para coherencia
interface SupportTicket {
  ticket_code: string     // IDENTIFICADOR PRINCIPAL
  titulo: string          // Español
  categoria: string       // Español
  descripcion: string     // Español
  imagen?: string         // Single image URL
  fecha_ticket: string    // Nuevo nombre
  estado: string          // Español
}
```

#### 8.1.2 Sistema de identificación:
- ❌ **Actual**: Usa `id` y arrays de `attachments`
- ✅ **Requerido**: Usa `ticket_code` como identificador principal

#### 8.1.3 Adjuntos vs imagen:
- ❌ **Actual**: Sistema complejo de múltiples archivos
- ✅ **Requerido**: Una sola imagen opcional

### 8.2 Modificaciones Requeridas en Frontend

#### 8.2.1 Actualizar Types (`support.types.ts`)
```typescript
// REEMPLAZAR support.types.ts COMPLETO
export interface SupportTicket {
  ticket_code: string                    // NUEVO - Identificador principal (T-YYYY-NNN)
  titulo: string                         // Renombrado de "title"
  categoria: TicketCategoryEnum          // Renombrado + enum
  descripcion: string                    // Renombrado de "description"  
  imagen?: string                        // NUEVO - Single image URL
  fecha_ticket: string                   // Renombrado de "createdAt"
  estado: TicketStatusEnum               // Renombrado + enum
  created_by?: string                    // NUEVO - ID del creador
}

export interface NewTicketForm {
  titulo: string                         // Renombrado de "title"
  categoria: TicketCategoryEnum          // Renombrado + enum
  descripcion: string                    // Renombrado de "description"
  imagen?: File                          // Simplificado - un solo archivo
}

// NUEVOS ENUMS
export enum TicketCategoryEnum {
  BUG = 'bug',
  FEATURE = 'feature',
  QUESTION = 'question', 
  TECHNICAL = 'technical'
}

export enum TicketStatusEnum {
  OPEN = 'open',
  IN_PROGRESS = 'in-progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed'
}

export interface TicketFilters {
  estado: TicketStatusEnum | 'all'       // Renombrado de "status"
  categoria: TicketCategoryEnum | 'all'  // Renombrado de "category"
  search: string
}

// ELIMINAR: TicketAttachment (ya no se usa)
```

#### 8.2.2 Crear Servicio API (`@services/tickets.service.ts`)
```typescript
// NUEVO ARCHIVO - No existe en módulo actual
import { apiClient } from '@/core/config/axios.config'
import type { 
  SupportTicket, 
  NewTicketForm, 
  TicketFilters, 
  TicketStatusEnum 
} from '@/modules/support/types/support.types'

export class TicketsService {
  private baseURL = '/api/v1/tickets'

  async getTickets(filters?: TicketFilters): Promise<SupportTicket[]> {
    const response = await apiClient.get(this.baseURL, { params: filters })
    return response.data.data
  }

  async getTicketByCode(ticketCode: string): Promise<SupportTicket> {
    const response = await apiClient.get(`${this.baseURL}/${ticketCode}`)
    return response.data.data
  }

  async createTicket(data: NewTicketForm): Promise<SupportTicket> {
    const response = await apiClient.post(this.baseURL, data)
    return response.data.data
  }

  async updateTicket(ticketCode: string, data: Partial<NewTicketForm>): Promise<SupportTicket> {
    const response = await apiClient.put(`${this.baseURL}/${ticketCode}`, data)
    return response.data.data
  }

  async deleteTicket(ticketCode: string): Promise<void> {
    await apiClient.delete(`${this.baseURL}/${ticketCode}`)
  }

  async changeStatus(ticketCode: string, estado: TicketStatusEnum): Promise<SupportTicket> {
    const response = await apiClient.patch(`${this.baseURL}/${ticketCode}/status`, { estado })
    return response.data.data
  }

  async uploadImage(ticketCode: string, file: File): Promise<string> {
    const formData = new FormData()
    formData.append('image', file)
    const response = await apiClient.post(`${this.baseURL}/${ticketCode}/upload-image`, formData, {
      headers: { 'Content-Type': 'multipart/form-data' }
    })
    return response.data.data.imageUrl
  }

  async deleteImage(ticketCode: string): Promise<void> {
    await apiClient.delete(`${this.baseURL}/${ticketCode}/image`)
  }
}

export const ticketsService = new TicketsService()
```

#### 8.2.3 Actualizar Componentes

**A. `NewTicket.vue` - Cambios requeridos:**
```vue
<!-- CAMBIOS EN TEMPLATE -->
<FormInputField
  v-model="formData.titulo"          <!-- ✅ Cambio: title → titulo -->
  label="Título del ticket"
  placeholder="Describe brevemente el problema..."
  :required="true"
  :maxLength="100"
  :showCounter="true"
/>

<FormSelect
  v-model="formData.categoria"       <!-- ✅ Cambio: category → categoria -->
  label="Categoría"
  placeholder="Selecciona una categoría"
  :required="true"
  :options="categoryOptions"
/>

<FormTextarea
  v-model="formData.descripcion"     <!-- ✅ Cambio: description → descripcion -->
  label="Descripción"
  placeholder="Describe detalladamente el problema..."
  :required="true"
  :rows="4"
  :maxLength="500"
  :showCounter="true"
/>

<!-- ✅ SIMPLIFICAR: Una sola imagen en lugar de múltiples archivos -->
<div>
  <label class="block text-sm font-medium text-gray-700 mb-1">
    Imagen adjunta (opcional)
  </label>
  <div class="mt-1 flex justify-center px-6 pt-5 pb-6 border-2 border-gray-300 border-dashed rounded-md">
    <input
      ref="fileInput"
      type="file"
      accept="image/*"
      @change="handleImageUpload"
      class="hidden"
    />
    <!-- Resto del UI simplificado -->
  </div>
</div>
```

```typescript
// CAMBIOS EN SCRIPT
import { ticketsService } from '@/shared/services/tickets.service'  // ✅ NUEVO
import type { NewTicketForm } from '../types/support.types'

const formData = reactive<NewTicketForm>({
  titulo: '',          // ✅ Cambio: title → titulo
  categoria: '',       // ✅ Cambio: category → categoria
  descripcion: '',     // ✅ Cambio: description → descripcion
  imagen: undefined    // ✅ Cambio: attachments → imagen (File)
})

// ✅ NUEVO: Función para manejar una sola imagen
const handleImageUpload = (event: Event) => {
  const target = event.target as HTMLInputElement
  const file = target.files?.[0]
  if (file) {
    // Validar que sea imagen y tamaño
    if (!file.type.startsWith('image/')) {
      // Notificación centrada en lugar de alert
      return
    }
    if (file.size > 5 * 1024 * 1024) { // 5MB
      // Notificación centrada en lugar de alert
      return
    }
    formData.imagen = file
  }
}

// ✅ ACTUALIZAR: Función para enviar ticket
const submitTicket = async () => {
  try {
    const newTicket = await ticketsService.createTicket(formData)
    emit('ticketCreated', newTicket)
    clearForm()
    // ✅ Notificación centrada en lugar de alert
  } catch (error) {
    // ✅ Manejo de errores con notificación centrada
  }
}
```

**B. `ActualTickets.vue` - Cambios requeridos:**
```vue
<!-- AÑADIR: Campo de búsqueda que falta -->
<div class="flex items-center space-x-3">
  <div class="w-48">                    <!-- ✅ NUEVO -->
    <FormInputField
      v-model="filters.search"
      placeholder="Buscar tickets..."
      :showIcon="true"
    />
  </div>
  <div class="w-40">
    <FormSelect
      v-model="filters.estado"          <!-- ✅ Cambio: status → estado -->
      :options="statusOptions"
      placeholder="Estado"
    />
  </div>
  <div class="w-44">
    <FormSelect
      v-model="filters.categoria"      <!-- ✅ Cambio: category → categoria -->
      :options="categoryOptions"
      placeholder="Categoría"
    />
  </div>
</div>

<!-- EN LA LISTA DE TICKETS -->
<div class="flex items-center gap-2 mb-2">
  <h3 class="font-medium text-gray-900">{{ ticket.titulo }}</h3>  <!-- ✅ Cambio -->
  <span :class="getStatusBadgeClass(ticket.estado)" class="text-xs font-medium px-2 py-1 rounded-full">
    {{ getStatusLabel(ticket.estado) }}                           <!-- ✅ Cambio -->
  </span>
  <span class="text-xs text-gray-500 bg-gray-100 px-2 py-1 rounded-full">
    {{ getCategoryLabel(ticket.categoria) }}                      <!-- ✅ Cambio -->
  </span>
</div>
<p class="text-sm text-gray-600 mb-2">{{ ticket.descripcion.substring(0, 100) }}...</p>  <!-- ✅ Cambio -->
<div class="flex items-center gap-4 text-xs text-gray-500">
  <span>Ticket {{ ticket.ticket_code }}</span>                    <!-- ✅ Cambio: id → ticket_code -->
  <span>{{ formatDate(ticket.fecha_ticket) }}</span>              <!-- ✅ Cambio: createdAt → fecha_ticket -->
  <span v-if="ticket.imagen">1 imagen adjunta</span>              <!-- ✅ Cambio: attachments → imagen -->
</div>
```

```typescript
// CAMBIOS EN SCRIPT
import { ticketsService } from '@/shared/services/tickets.service'  // ✅ NUEVO

// ✅ ACTUALIZAR: Opciones de filtros con nombres en español
const statusOptions = [
  { value: 'all', label: 'Estados' },
  { value: 'open', label: 'Abiertos' },
  { value: 'in-progress', label: 'En progreso' },
  { value: 'resolved', label: 'Resueltos' },
  { value: 'closed', label: 'Cerrados' }
]

// ✅ ACTUALIZAR: Funciones con nuevos nombres
const changeTicketStatus = async (ticketCode: string, newStatus: string) => {  // ✅ Cambio parámetro
  try {
    await ticketsService.changeStatus(ticketCode, newStatus as TicketStatusEnum)
    emit('ticketStatusChanged', ticketCode, newStatus)
  } catch (error) {
    // Manejo de errores
  }
}

const deleteTicket = async (ticketCode: string) => {  // ✅ Cambio parámetro
  // ✅ Usar modal de confirmación centrado en lugar de confirm()
  try {
    await ticketsService.deleteTicket(ticketCode)
    emit('ticketDeleted', ticketCode)
  } catch (error) {
    // Manejo de errores
  }
}
```

**C. `TicketDetailModal.vue` - Cambios requeridos:**
```vue
<!-- CAMBIOS EN TEMPLATE -->
<h3 class="text-xl font-semibold text-gray-900">{{ ticket.titulo }}</h3>  <!-- ✅ Cambio -->

<div class="grid grid-cols-2 gap-4 bg-gray-50 rounded-xl p-4">
  <div>
    <p class="text-sm text-gray-500">Código del Ticket</p>
    <p class="text-base font-medium text-gray-900">{{ ticket.ticket_code }}</p>  <!-- ✅ Cambio -->
  </div>
  <div>
    <p class="text-sm text-gray-500">Estado</p>
    <span :class="getStatusBadgeClass(ticket.estado)">                           <!-- ✅ Cambio -->
      {{ getStatusLabel(ticket.estado) }}                                        <!-- ✅ Cambio -->
    </span>
  </div>
  <div>
    <p class="text-sm text-gray-500">Categoría</p>
    <p class="text-base font-medium text-gray-900">{{ getCategoryLabel(ticket.categoria) }}</p>  <!-- ✅ Cambio -->
  </div>
  <div>
    <p class="text-sm text-gray-500">Fecha de Creación</p>
    <p class="text-base font-medium text-gray-900">{{ formatDate(ticket.fecha_ticket) }}</p>  <!-- ✅ Cambio -->
  </div>
</div>

<div class="bg-gray-50 rounded-xl p-4">
  <h5 class="text-sm font-medium text-gray-700 mb-3">Descripción</h5>
  <div class="bg-white border border-gray-200 rounded-lg p-3">
    <p class="text-sm text-gray-800 whitespace-pre-wrap">{{ ticket.descripcion }}</p>  <!-- ✅ Cambio -->
  </div>
</div>

<!-- ✅ SIMPLIFICAR: Una sola imagen -->
<div v-if="ticket.imagen" class="bg-gray-50 rounded-xl p-4">
  <h5 class="text-sm font-medium text-gray-700 mb-3">Imagen Adjunta</h5>
  <div class="cursor-pointer" @click="openImageModal(ticket.imagen)">
    <img
      :src="ticket.imagen"
      alt="Imagen del ticket"
      class="max-w-xs h-40 object-cover rounded-lg border border-gray-200 hover:border-blue-300 transition-colors"
    />
  </div>
</div>
```

**D. `SupportView.vue` - Cambios requeridos:**
```typescript
// ACTUALIZAR datos dummy con nueva estructura
const tickets = ref<SupportTicket[]>([
  {
    ticket_code: 'T-2025-001',        // ✅ Cambio: id → ticket_code
    titulo: 'Error al cargar lista de casos',      // ✅ Cambio: title → titulo
    categoria: 'bug',                 // ✅ Cambio: category → categoria
    descripcion: 'Cuando intento acceder...',     // ✅ Cambio: description → descripcion
    estado: 'open',                   // ✅ Cambio: status → estado
    fecha_ticket: '2024-01-15T10:30:00Z',        // ✅ Cambio: createdAt → fecha_ticket
    imagen: undefined                 // ✅ Cambio: attachments → imagen
  }
])

// ✅ INTEGRAR: Usar servicio real en lugar de datos dummy
onMounted(async () => {
  try {
    tickets.value = await ticketsService.getTickets()
  } catch (error) {
    // Manejo de errores
  }
})
```

### 8.3 Componentes de Notificación Centrada

#### 8.3.1 Crear NotificationService
```typescript
// NUEVO: @services/notifications.service.ts
export class NotificationService {
  static success(message: string) {
    // Implementar notificación centrada verde
  }
  
  static error(message: string) {
    // Implementar notificación centrada roja
  }
  
  static confirm(message: string): Promise<boolean> {
    // Implementar modal de confirmación centrado
  }
}
```

#### 8.3.2 Reemplazar alertas nativas
- ✅ `alert('¡Ticket creado exitosamente!')` → `NotificationService.success('...')`
- ✅ `confirm('¿Estás seguro...')` → `await NotificationService.confirm('...')`

### 8.4 Resumen de Archivos a Modificar

**Archivos a CREAR:**
1. `@services/tickets.service.ts` (NUEVO)
2. `@services/notifications.service.ts` (NUEVO)

**Archivos a MODIFICAR:**
1. `support.types.ts` - Reemplazar completamente
2. `NewTicket.vue` - Campos, imagen única, servicio API
3. `ActualTickets.vue` - Campos, búsqueda, servicio API
4. `TicketDetailModal.vue` - Campos, imagen única
5. `SupportView.vue` - Datos dummy → servicio real
6. `supportRoutes.ts` - Sin cambios necesarios

**Funcionalidades a IMPLEMENTAR:**
1. Sistema de notificaciones centradas
2. Manejo de errores de API
3. Upload de imagen única
4. Filtros con búsqueda por texto

## 9. Testing

### 9.1 Tests Backend
- Unit tests para cada repository/service
- Integration tests para endpoints
- Tests de permisos y autenticación
- Tests de upload de imagen

### 9.2 Tests Frontend
- Componente testing con Jest/Vitest
- E2E testing con Cypress/Playwright
- API integration tests

## 10. Cronograma de Implementación

### Fase 1: Backend Core (Día 1)
1. ✅ Crear estructura de directorios
2. ✅ Implementar modelos MongoDB
3. ✅ Crear esquemas Pydantic
4. ✅ Implementar repository CRUD básico
5. ✅ Crear service con lógica de negocio básica

### Fase 2: Backend API (Día 1-2)
1. ✅ Implementar endpoints principales
2. ✅ Añadir middleware de autenticación
3. ✅ Implementar upload de archivos
4. ✅ Agregar validaciones y manejo de errores
5. ✅ Testing básico

### Fase 3: Frontend Integration (Día 2)
1. ✅ Crear servicio API frontend
2. ✅ Integrar con componentes existentes
3. ✅ Reemplazar notificaciones nativas
4. ✅ Mejorar UX de adjuntos
5. ✅ Añadir filtro de búsqueda

### Fase 4: Features Avanzadas (Día 3)
1. Sistema de comentarios
2. Notificaciones por email
3. Dashboard de tickets para admins
4. Reportes y estadísticas

### Fase 5: Testing y Deploy (Día 3)
1. Testing completo
2. Documentación final
3. Deploy a staging
4. Pruebas de usuario

## 11. Consideraciones Técnicas

### 11.1 Performance
- Indexado MongoDB: `created_by`, `estado`, `categoria`, `fecha_ticket`
- Paginación eficiente con cursor-based pagination para listas grandes
- Compresión automática de imágenes

### 11.2 Seguridad
- Validación estricta de tipos de imagen
- Sanitización de nombres de archivo
- Rate limiting para creación de tickets
- Validación de tamaño de imagen

### 11.3 Escalabilidad
- Separación de imágenes a storage externo (S3/MinIO) en futuro
- Cache de respuestas frecuentes
- Archivo de tickets antiguos

## 12. Configuración

### 12.1 Variables de Entorno
```
TICKETS_UPLOAD_DIR=/app/uploads/tickets/images
TICKETS_MAX_IMAGE_SIZE=5242880  # 5MB
TICKETS_ALLOWED_TYPES=image/*
TICKETS_RATE_LIMIT=10  # tickets per hour per user
```

### 12.2 Configuración MongoDB
```python
# Índices requeridos
db.tickets.createIndex({"ticket_code": 1}, {"unique": true})  # PRINCIPAL - único
db.tickets.createIndex({"created_by": 1, "fecha_ticket": -1})
db.tickets.createIndex({"estado": 1, "categoria": 1})
db.tickets.createIndex({"$text": {"titulo": 1, "descripcion": 1}})

# Sistema de consecutivos
db.consecutivos_tickets.createIndex({"year": 1}, {"unique": true})
```

### 12.3 Repositorio de Consecutivos
Similar al módulo de casos, necesitamos un repository para manejar consecutivos:
- **Colección**: `consecutivos_tickets`
- **Documento**: `{year: 2025, last_number: 15}` 
- **Generación**: T-{YEAR}-{CONSECUTIVE_3_DIGITS}

---

**Próximos pasos**: Implementar Fase 1 (Backend Core) siguiendo este planning, manteniendo consistencia con arquitectura existente del proyecto.
