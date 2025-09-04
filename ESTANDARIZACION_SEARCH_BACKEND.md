# Estandarización del Sistema de Búsqueda Backend

## Resumen de Cambios Implementados

Este documento describe la estandarización completa realizada en el sistema de búsqueda del backend para todos los módulos, garantizando consistencia en el manejo de parámetros de estado y funcionalidad de búsqueda.

## 1. Estandarización del Campo de Estado

### Campo Unificado: `is_active`
- **Antes**: Inconsistencias entre `activo` e `is_active` en diferentes módulos
- **Después**: Todos los módulos usan `is_active: bool` consistentemente
- **Afectados**: Entidades, Auxiliares, Patólogos, Residentes, Pruebas

### Cambios en Esquemas
```python
# Antes (en entidades)
class EntidadSearch(BaseModel):
    query: Optional[str] = None
    activo: Optional[bool] = None  # ❌ Inconsistente

# Después (estandarizado)
class EntidadSearch(BaseModel):
    query: Optional[str] = None
    is_active: Optional[bool] = None  # ✅ Consistente
```

## 2. Funciones de Búsqueda Separadas

### Arquitectura de Tres Funciones por Módulo

Cada módulo ahora tiene tres funciones de búsqueda diferenciadas:

#### A. Búsqueda General con Filtro Opcional
- **Función**: `search_[entidad]` / `get_all_[entidad]`
- **Propósito**: Búsqueda flexible con filtro opcional de estado
- **Comportamiento**: 
  - Si `is_active=True` → Solo registros activos
  - Si `is_active=False` → Solo registros inactivos
  - Si `is_active=None` → Todos los registros

#### B. Búsqueda Solo Activos
- **Función**: `search_active_[entidad]` / `get_active_[entidad]`
- **Propósito**: Búsqueda exclusiva de registros activos
- **Comportamiento**: Siempre filtra `is_active=True`

#### C. Búsqueda Incluyendo Inactivos
- **Función**: `search_all_[entidad]_including_inactive` / `get_all_[entidad]_including_inactive`
- **Propósito**: Búsqueda de todos los registros sin filtro de estado
- **Comportamiento**: No aplica filtro de `is_active`

### Implementación en Capas

#### Capa de Repositorio
```python
# Ejemplo: EntidadRepository
async def get_all_active(self, search_params: EntidadSearch) -> List[Entidad]:
    """Obtener solo entidades activas"""
    filter_dict = {"is_active": True}
    # ... aplicar filtros de búsqueda

async def get_all_including_inactive(self, search_params: EntidadSearch) -> List[Entidad]:
    """Obtener todas las entidades incluyendo inactivas"""
    filter_dict = {}  # Sin filtro de estado
    # ... aplicar filtros de búsqueda
```

#### Capa de Servicio
```python
# Ejemplo: EntidadService
async def get_active_entidades(self, search_params: EntidadSearch) -> Dict[str, Any]:
    """Obtener solo entidades activas"""
    entidades = await self.repository.get_all_active(search_params)
    total = await self.repository.count_active(search_params)

async def get_all_entidades_including_inactive(self, search_params: EntidadSearch) -> Dict[str, Any]:
    """Obtener todas las entidades incluyendo inactivas"""
    entidades = await self.repository.get_all_including_inactive(search_params)
    total = await self.repository.count_including_inactive(search_params)
```

#### Capa de Rutas (API)
```python
# Ejemplo: Rutas de Entidades
@router.get("/active", response_model=Dict[str, Any])
async def get_active_entidades(...):
    """Obtener solo entidades activas"""

@router.get("/all-including-inactive", response_model=Dict[str, Any])
async def get_all_entidades_including_inactive(...):
    """Obtener todas las entidades incluyendo inactivas"""
```

## 3. Módulos Actualizados

### ✅ Entidades
- **Repositorio**: Agregadas funciones separadas
- **Servicio**: Agregados métodos separados
- **Rutas**: Agregados endpoints separados
- **Campo**: Estandarizado a `is_active`

### ✅ Auxiliares
- **Repositorio**: Agregadas funciones separadas
- **Servicio**: Agregados métodos separados
- **Rutas**: Agregados endpoints separados
- **Campo**: Ya usaba `is_active`

### ✅ Patólogos
- **Repositorio**: Agregadas funciones separadas
- **Servicio**: Agregados métodos separados
- **Rutas**: Agregados endpoints separados
- **Campo**: Ya usaba `is_active`

### ✅ Residentes
- **Servicio**: Agregados métodos separados
- **Campo**: Ya usaba `is_active`
- **Pendiente**: Repositorio y rutas (requieren implementación específica)

### ✅ Pruebas
- **Servicio**: Agregados métodos separados
- **Campo**: Ya usaba `is_active`
- **Pendiente**: Repositorio y rutas (requieren implementación específica)

## 4. Nuevos Endpoints de API

### Estructura de URLs Estandarizada

Para cada módulo (`entidades`, `auxiliares`, `patologos`, `residentes`, `pruebas`):

```
GET /{modulo}/                           # Búsqueda general con filtro opcional
GET /{modulo}/active                     # Solo registros activos
GET /{modulo}/all-including-inactive     # Todos los registros
GET /{modulo}/search/active              # Búsqueda avanzada solo activos
GET /{modulo}/search/all-including-inactive  # Búsqueda avanzada todos
```

### Parámetros de Query Estandarizados

```
?query=texto                    # Búsqueda de texto general
?is_active=true|false|null      # Filtro de estado (solo en endpoint general)
?skip=0                         # Paginación: registros a omitir
?limit=10                       # Paginación: máximo de registros
```

## 5. Beneficios de la Estandarización

### Para el Frontend
- **Predictibilidad**: Misma estructura de API para todos los módulos
- **Flexibilidad**: Opciones claras para diferentes casos de uso
- **Consistencia**: Mismo manejo de parámetros en todos lados

### Para el Backend
- **Mantenibilidad**: Código consistente y predecible
- **Escalabilidad**: Fácil agregar nuevos módulos siguiendo el patrón
- **Debugging**: Estructura uniforme facilita la detección de problemas

### Para la Aplicación
- **Rendimiento**: Consultas optimizadas según necesidad específica
- **UX**: Búsquedas rápidas de solo activos vs búsquedas completas
- **Funcionalidad**: Soporte completo para reactivación de registros

## 6. Casos de Uso

### Caso 1: Lista Desplegable (Solo Activos)
```javascript
// Frontend usa endpoint específico
GET /api/entidades/active
```

### Caso 2: Búsqueda para Reactivar (Incluyendo Inactivos)
```javascript
// Frontend usa endpoint específico
GET /api/entidades/all-including-inactive?query=texto
```

### Caso 3: Administración General (Con Filtro)
```javascript
// Frontend usa endpoint general con filtro
GET /api/entidades/?is_active=true    // Solo activos
GET /api/entidades/?is_active=false   // Solo inactivos
GET /api/entidades/                   // Todos
```

## 7. Estado Actual

### Completamente Implementado
- ✅ Entidades: Repositorio, Servicio, Rutas
- ✅ Auxiliares: Repositorio, Servicio, Rutas
- ✅ Patólogos: Repositorio, Servicio, Rutas

### Parcialmente Implementado
- 🔄 Residentes: Servicio (Repositorio y Rutas pendientes)
- 🔄 Pruebas: Servicio (Repositorio y Rutas pendientes)

### Próximos Pasos
1. Completar implementación en Repositorios de Residentes y Pruebas
2. Agregar rutas separadas para Residentes y Pruebas
3. Actualizar Frontend para usar nuevos endpoints
4. Documentar APIs en Swagger/OpenAPI

## 8. Consideraciones de Migración

### Compatibilidad hacia Atrás
- Los endpoints existentes se mantienen funcionales
- Los nuevos endpoints son adicionales, no reemplazan los existentes
- El frontend puede migrar gradualmente

### Testing
- Cada función de búsqueda debe ser probada independientemente
- Verificar que los filtros de estado funcionan correctamente
- Validar paginación y conteos en todas las variantes

### Documentación
- Actualizar documentación de API
- Crear guías de uso para desarrolladores frontend
- Documentar mejores prácticas para cada tipo de búsqueda

---

**Fecha de Implementación**: 4 de septiembre de 2025
**Implementado por**: GitHub Copilot
**Estado**: En progreso - Backend estandarizado, Frontend pendiente
