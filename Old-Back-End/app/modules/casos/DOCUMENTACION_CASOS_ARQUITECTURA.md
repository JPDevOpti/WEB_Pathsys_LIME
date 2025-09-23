### Arquitectura del módulo de casos

Este documento describe la organización propuesta del módulo `casos`, separada en tres áreas: Gestión (CRUD y estados), Consulta/Listado (endpoints de lectura por vista/uso) y Estadísticas (ya modularizada). El objetivo es eliminar archivos monolíticos, mejorar mantenibilidad, rendimiento y permisos por endpoint.

## Estructura de carpetas

```
app/modules/casos/
  models/                               # Modelos de dominio
    caso.py                             # Entidad caso (campos/validaciones)
    consecutivo.py                      # Lógica de consecutivos

  schemas/                              # Esquemas Pydantic (IO)
    case_management.py                  # DTOs de crear/editar/eliminar/estado/adjuntos
    stats.py                            # DTOs de estadísticas
    query/                              # DTOs específicos de listados/consulta
      filters.py                        # Filtros tipados (estado, fechas, entidad, patólogo, texto)
      pagination.py                     # PageRequest/PageResponse/Sort
      urgent_cases.py                   # Fila mínima para “Casos urgentes”
      case_list.py                      # Fila estándar del listado general
      delivery_queue.py                 # Fila de colas (por firmar/por entregar)
      search.py                         # Búsqueda avanzada y resultados (facetado)

  repositories/                         # Acceso a datos (Mongo pipelines)
    caso_repository.py                  # Operaciones básicas sobre casos
    consecutivo_repository.py           # Persistencia de consecutivos
    stats/                              # Repos de estadísticas por métrica
      monthly_stats_repository.py       # Estadísticas mensuales
      opportunity_stats_repository.py   # Estadísticas de oportunidad
      cases_stats_repository.py         # Otras métricas de casos
      entities_stats_repository.py      # Métricas por entidad
      samples_stats_repository.py       # Métricas de muestras
      tests_stats_repository.py         # Métricas de pruebas
    management/                         # Repos de gestión subdivididos
      create_repository.py              # Crear caso, asignaciones iniciales, consecutivo
      update_repository.py              # Editar campos del caso, adjuntos
      delete_repository.py              # Eliminar caso/adjuntos, borrado lógico/duro
      state_repository.py               # Cambios de estado (en proceso, por firmar, entregar, completado)
    query/                              # Repos por vista/uso de consulta
      base_query_repository.py          # Helpers comunes: match/proyección/sort/paginación
      urgent_cases_repository.py        # Pipeline de “Casos urgentes” (>=5 días, no completados)
      case_list_repository.py           # Listado general con filtros combinables
      pathologist_cases_repository.py   # Listados por patólogo (asignados/pendientes)
      entity_cases_repository.py        # Listados por entidad
      delivery_queue_repository.py      # Colas operativas (por firmar/por entregar)
      search_repository.py              # Búsqueda avanzada (texto/filtros)

  services/                             # Reglas de negocio/orquestación
    cache_service.py                    # Caché (TTL, invalidación)
    pagination_service.py               # Utilidades de paginación
    index_optimizer.py                  # Sugerencia/creación de índices
    stats/                              # Servicios de estadísticas por métrica
      monthly_stats_service.py          # Orquestación mensual (con caché)
      opportunity_stats_service.py      # Orquestación oportunidad
      cases_stats_service.py            # Otras métricas de casos
      entities_stats_service.py         # Métricas por entidad
      samples_stats_service.py          # Métricas de muestras
      tests_stats_service.py            # Métricas de pruebas
    management/                         # Servicios de gestión subdivididos
      create_service.py                 # Validaciones de creación, consecutivo, side-effects, invalidación caché
      update_service.py                 # Reglas de edición, integridad referencial, invalidación caché
      delete_service.py                 # Reglas de eliminación, auditoría, invalidación caché
      state_service.py                  # Reglas de transición de estados y SLA
    query/                              # Servicios por vista/uso de consulta
      base_query_service.py             # Normalización de filtros, defaults, alias, caché
      urgent_cases_service.py           # Orquestación de urgentes (TTL corto, límites)
      case_list_service.py              # Listado general, sort/paginación, exportación
      pathologist_cases_service.py      # Deriva role_code, permisos por patólogo
      entity_cases_service.py           # Reglas y límites por entidad
      delivery_queue_service.py         # Lógica de colas y SLA
      search_service.py                 # Búsqueda avanzada/facetado

  routes/                               # Endpoints HTTP
    caso_routes.py               # Compatibilidad temporal (proxy a nuevas rutas)
    stats_routes.py              # Rutas de estadísticas centralizadas
    management/                  # Rutas de gestión subdivididas
      create_routes.py           # POST /casos
      update_routes.py           # PUT /casos/{caso_code}, PATCH /casos/{caso_code}
      delete_routes.py           # DELETE /casos/{caso_code}
      state_routes.py            # PATCH /casos/{caso_code}/estado
    query/                       # Rutas segmentadas por vista/uso
      urgent_cases_routes.py     # GET /casos/consulta/urgentes
      case_list_routes.py        # GET /casos, POST /casos/buscar, GET /casos/export
      pathologist_cases_routes.py # GET /casos/patologo/{code}, GET /casos/patologo/mios
      entity_cases_routes.py     # GET /casos/entidad/{entidad_id}
      delivery_queue_routes.py   # GET /casos/cola/por-firmar, /cola/por-entregar
      search_routes.py           # POST /casos/busqueda-avanzada

  DOCUMENTACION_CASOS.md               # Documentación general del módulo
  DOCUMENTACION_CASOS_STATS.md         # Documentación de estadísticas
  DOCUMENTACION_CASOS_ARQUITECTURA.md  # Este documento (arquitectura)
```

### routes/
- `caso_routes.py`: Compatibilidad temporal con rutas antiguas mientras se migra.
- `stats_routes.py`: Router de estadísticas (existente), ya centralizado.
- `management_routes.py`:
  - POST `/casos` crear
  - PUT `/casos/{caso_code}` actualizar
  - PATCH `/casos/{caso_code}/estado` cambiar estado
  - DELETE `/casos/{caso_code}` eliminar
  - POST `/casos/{caso_code}/adjuntos` adjuntos
- `query/urgent_cases_routes.py`:
  - GET `/casos/consulta/urgentes` (query: `patologo_code?`, `estado?`, `limit=10`)
- `query/case_list_routes.py`:
  - GET `/casos` (query: filtros simples + paginación + sort)
  - POST `/casos/buscar` (compatibilidad con body avanzado)
  - GET `/casos/export` (stream)
- `query/pathologist_cases_routes.py`:
  - GET `/casos/patologo/{patologo_code}`
  - GET `/casos/patologo/mios` (usa `role_code` autenticado por defecto)
- `query/entity_cases_routes.py`:
  - GET `/casos/entidad/{entidad_id}`
- `query/delivery_queue_routes.py`:
  - GET `/casos/cola/por-firmar`
  - GET `/casos/cola/por-entregar`
- `query/search_routes.py`:
  - POST `/casos/busqueda-avanzada`

## Índices recomendados
- `{ estado: 1, fecha_creacion: -1 }`
- `{ 'patologo_asignado.codigo': 1, fecha_creacion: -1 }`
- `{ 'paciente.entidad_info.id': 1, fecha_creacion: -1 }`
- `{ fecha_entrega: -1, estado: 1 }` (colas/entregas)
- Parcial para urgentes: `{ fecha_creacion: -1 }` con filtro `{ estado: { $ne: 'Completado' } }`
- Texto opcional (campos acotados) para `search_repository`.

## Caché
- Listados: TTL ~60s por hash de filtros+orden+paginación.
- Estadísticas: TTL acorde a cada métrica (ya definido en `stats/*`).
- Invalidación: en `management_service` tras crear/editar/borrar/cambiar estado.

## Permisos y seguridad
- Gestión: restringida según rol; registros de auditoría.
- Listados “míos”: derivan `role_code` del usuario autenticado; no exponen data de otros usuarios.
- Exportaciones: límites y filtros obligatorios; registros de solicitante.

## Migración y compatibilidad
- Mantener `caso_routes.py` como proxy temporal hacia nuevas rutas de `management` y `query` hasta completar la migración del front.
- Documentar en `DOCUMENTACION_CASOS.md` los cambios de endpoints y rutas de reemplazo.


