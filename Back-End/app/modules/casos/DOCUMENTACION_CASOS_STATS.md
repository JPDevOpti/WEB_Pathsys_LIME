# Documentación de Estadísticas del Módulo de Casos

Este documento detalla la nueva organización de estadísticas, los endpoints públicos (sin cambios de path) y sus responsabilidades por capa.

## 1. Estructura de Archivos (Estadísticas)

```text
app/modules/casos/
├── schemas/
│   └── stats.py                        # Esquemas Pydantic de estadísticas
├── repositories/
│   └── stats/
│       ├── cases_stats_repository.py       # Estadísticas generales de casos
│       ├── samples_stats_repository.py     # Estadísticas de muestras
│       ├── monthly_stats_repository.py     # Casos por mes
│       ├── opportunity_stats_repository.py # Oportunidad mensual/detalle
│       ├── entities_stats_repository.py    # Entidades mensual/detalle
│       └── tests_stats_repository.py       # Pruebas mensual/detalle
├── services/
│   └── stats/
│       ├── cases_stats_service.py
│       ├── samples_stats_service.py
│       ├── monthly_stats_service.py
│       ├── opportunity_stats_service.py
│       ├── entities_stats_service.py
│       └── tests_stats_service.py
└── routes/
    └── stats_routes.py                 # Rutas de estadísticas (mismos paths)
```

## 2. Endpoints Públicos (sin cambios de path)

- GET `/api/v1/casos/estadisticas`
- GET `/api/v1/casos/estadisticas-muestras`
- GET `/api/v1/casos/casos-por-mes/{year}`
- GET `/api/v1/casos/oportunidad-por-mes/{year}`
- GET `/api/v1/casos/estadisticas-oportunidad-mensual`
- GET `/api/v1/casos/oportunidad-detalle` (params: `year`, `month`)
- GET `/api/v1/casos/estadisticas-entidades-mensual` (params: `month`, `year`, `entity`)
- GET `/api/v1/casos/detalle-entidad` (params: `entidad`, `month`, `year`)
- GET `/api/v1/casos/patologos-por-entidad` (params: `entidad`, `month`, `year`)
- GET `/api/v1/casos/estadisticas-pruebas-mensual` (params: `month`, `year`, `entity`)
- GET `/api/v1/casos/detalle-prueba/{codigo_prueba}` (params: `month`, `year`, `entity`)
- GET `/api/v1/casos/patologos-por-prueba/{codigo_prueba}` (params: `month`, `year`, `entity`)

Versiones optimizadas con caché:
- GET `/api/v1/casos/optimized/stats`
- GET `/api/v1/casos/optimized/muestras/stats`
- GET `/api/v1/casos/optimized/por-mes/{año}`
- GET `/api/v1/casos/optimized/oportunidad/{año}`

## 3. Responsabilidades por Capa

- `repositories/stats/*`: Agregaciones MongoDB, uso de índices, proyecciones y cálculos por estadística.
- `services/stats/*`: Orquestación, validación, composición de respuestas y uso de `cache_service`.
- `routes/stats_routes.py`: Declaración de endpoints y vinculación con servicios.
- `schemas/stats.py`: Esquemas Pydantic de entrada/salida específicos de estadísticas.

## 4. Caché y TTL sugeridos

- `caso_stats`: 300s
- `muestra_stats`: 300s
- `casos_por_mes`: 600s
- `oportunidad_stats`: 600s
- `entidades_stats`: 900s
- `pruebas_stats`: 900s

Gestión centralizada en `services/cache_service.py`.

## 5. Índices recomendados (resumen)

- `fecha_creacion` (+ combinados por estado/entidad) para mensuales y estadísticas de volumen.
- `fecha_entrega`, `oportunidad`, `estado` para oportunidad.
- Desglose completo en `services/index_optimizer.py`.

## 6. Backwards compatibility

- Paths públicos intactos.
- Tipos de respuesta sin cambios.
- Solo se mueve la implementación a archivos dedicados para mayor cohesión.

