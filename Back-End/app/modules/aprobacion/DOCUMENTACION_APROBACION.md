# Módulo de Aprobación de Casos con Pruebas Complementarias

## Descripción

Este módulo gestiona el proceso de aprobación de casos que requieren pruebas complementarias. Se activa cuando un patólogo, al firmar un caso, selecciona pruebas complementarias que necesitan autorización administrativa.

## Funcionalidades

### Estados del Proceso de Aprobación

1. **PENDIENTE**: Estado inicial cuando se crea la solicitud
2. **GESTIONANDO**: Estado intermedio cuando un administrador comienza a revisar el caso
3. **APROBADO**: Estado final cuando se autoriza la realización de las pruebas
4. **RECHAZADO**: Estado final cuando se deniega la solicitud

### Características Principales

- **Copia completa del caso original**: Incluye toda la información del caso (paciente, muestras, resultados, etc.)
- **Gestión de pruebas complementarias**: Lista detallada de pruebas solicitadas con cantidades y observaciones
- **Workflow de aprobación**: Proceso estructurado con estados y comentarios
- **Auditoría completa**: Seguimiento de quién solicita, gestiona y aprueba
- **Búsqueda avanzada**: Filtros por estado, usuario, fechas, etc.

## Estructura de Datos

### CasoAprobacion
```python
{
    "caso_original_id": "string",
    "caso_code": "2025-00001",
    "paciente": { /* información completa del paciente */ },
    "muestras": [ /* array de muestras */ ],
    "resultado": { /* resultado del caso original */ },
    "pruebas_complementarias": [
        {
            "codigo": "LAB001",
            "nombre": "Inmunohistoquímica",
            "cantidad": 2,
            "costo": 150.00,
            "observaciones": "Para confirmar diagnóstico"
        }
    ],
    "estado_aprobacion": "pendiente",
    "aprobacion_info": {
        "solicitado_por": "patologo_123",
        "fecha_solicitud": "2025-01-15T10:30:00Z",
        "motivo": "Necesarias para confirmar diagnóstico de linfoma",
        "gestionado_por": null,
        "fecha_gestion": null,
        "aprobado_por": null,
        "fecha_aprobacion": null,
        "comentarios_aprobacion": null
    }
}
```

## API Endpoints

### Crear caso de aprobación
- **POST** `/aprobacion/`
- Crea un nuevo caso de aprobación basado en un caso existente

### Buscar casos
- **POST** `/aprobacion/search/active` - Solo casos activos
- **POST** `/aprobacion/search/all` - Incluye inactivos

### Gestión de estados
- **PATCH** `/aprobacion/{id}/gestionar` - Cambiar a estado "gestionando"
- **PATCH** `/aprobacion/{id}/aprobar` - Aprobar el caso
- **PATCH** `/aprobacion/{id}/rechazar` - Rechazar el caso

### Consultas específicas
- **GET** `/aprobacion/estado/{estado}` - Casos por estado
- **GET** `/aprobacion/usuario/{usuario_id}/pendientes` - Casos pendientes de un usuario

### Estadísticas
- **GET** `/aprobacion/estadisticas/general` - Estadísticas generales

## Integración con el Frontend

### Flujo de Trabajo

1. **Patólogo firma caso**: En el componente SignResults, al seleccionar pruebas complementarias
2. **Creación automática**: Se crea el caso de aprobación automáticamente
3. **Notificación**: Se notifica a los administradores
4. **Gestión**: Administrador revisa y gestiona el caso
5. **Decisión**: Se aprueba o rechaza con comentarios
6. **Seguimiento**: Ambas partes pueden ver el estado y comentarios

### Componentes Recomendados

- **CasesToApproveList**: Lista de casos pendientes de aprobación (ya implementado)
- **ApprovalRequestForm**: Formulario para crear solicitudes
- **ApprovalDetailsModal**: Modal con detalles del caso y proceso
- **ApprovalManagementPanel**: Panel administrativo para gestionar aprobaciones

## Consideraciones de Seguridad

- Solo patólogos pueden crear solicitudes
- Solo administradores pueden gestionar y aprobar
- Auditoría completa de todas las acciones
- Validación de permisos en cada endpoint

## Base de Datos

### Colección: `casos_aprobacion`
- Índices en: `caso_original_id`, `caso_code`, `estado_aprobacion`, `solicitado_por`
- TTL opcional para casos antiguos
- Respaldo automático por importancia de los datos

## Próximos Pasos

1. **Notificaciones**: Sistema de notificaciones en tiempo real
2. **Reportes**: Generación de reportes de aprobaciones
3. **Límites presupuestarios**: Control de costos por período
4. **Integración con facturación**: Conexión con sistema de costos
5. **Aprobaciones automáticas**: Reglas para casos de bajo costo
