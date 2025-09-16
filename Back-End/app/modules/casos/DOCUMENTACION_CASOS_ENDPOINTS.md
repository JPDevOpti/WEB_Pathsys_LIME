### Endpoints de Casos (Arquitectura nueva) — prefijo base: `/api/v1/casos`

#### Gestión (creación/actualización)
- POST `/` — Crear caso
- PUT `/{caso_code}` — Actualizar caso (cualquier campo)
- GET `/{caso_code}/validate` — Validar existencia de caso

#### Búsqueda/Listado
- GET `/recientes` — Casos de los últimos N meses (por defecto 2)
- POST `/buscar` — Búsqueda avanzada en todo el histórico

#### Estadísticas (Dashboard)
- GET `/estadisticas/por-mes/{year}` — Casos por mes (con `no_cache`)
- GET `/estadisticas/por-mes/patologo/{year}` — Casos por mes por patólogo (con `no_cache`)
- GET `/estadisticas/mes-actual` — Métricas mes actual (con `no_cache`)
- GET `/estadisticas/mes-actual/patologo` — Métricas mes actual por patólogo (con `no_cache`)
- GET `/estadisticas/oportunidad/mes-anterior` — Oportunidad (mes anterior)
- GET `/estadisticas/oportunidad/mes-anterior/patologo` — Oportunidad (mes anterior) por patólogo
