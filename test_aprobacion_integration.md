# Prueba de Integración - Módulo de Aprobación

## Pasos para probar la integración

### 1. Verificar Backend
```bash
cd Back-End
python -m uvicorn app.main:app --reload --port 8000
```

### 2. Verificar Endpoints Disponibles
Abrir: http://localhost:8000/docs

Buscar el grupo "Casos de Aprobación" para verificar que los endpoints estén disponibles:
- POST /api/v1/aprobacion/
- GET /api/v1/aprobacion/{caso_id}
- POST /api/v1/aprobacion/search/active
- etc.

### 3. Probar Frontend
```bash
cd Front-End
npm run dev
```

### 4. Flujo de Prueba
1. **Ir a Firmar Resultados**: Buscar un caso existente
2. **Activar Pruebas Complementarias**: Marcar el checkbox "Se necesitan pruebas complementarias"
3. **Seleccionar Pruebas**: Agregar al menos una prueba de la lista
4. **Completar Descripción**: Escribir el motivo de las pruebas
5. **Firmar con Cambios**: Hacer clic en el botón "Firmar con Cambios"

### 5. Verificar Resultado
- **Frontend**: Debe mostrar mensaje de éxito
- **Backend**: Verificar en la base de datos que se creó el registro en la colección `casos_aprobacion`
- **Logs**: Revisar logs del backend para detectar errores

### 6. Datos de Prueba Esperados

#### Caso de Aprobación Creado:
```json
{
  "caso_original_id": "673f1234567890abcdef1234",
  "caso_code": "2025-00001",
  "estado_aprobacion": "pendiente",
  "pruebas_complementarias": [
    {
      "codigo": "LAB001",
      "nombre": "Inmunohistoquímica",
      "cantidad": 1,
      "observaciones": ""
    }
  ],
  "aprobacion_info": {
    "solicitado_por": "user_id_123",
    "fecha_solicitud": "2025-09-05T...",
    "motivo": "Necesarias para confirmar diagnóstico...",
    "gestionado_por": null,
    "fecha_gestion": null
  }
}
```

### 7. Posibles Errores y Soluciones

#### Error 404 en /aprobacion/
- **Causa**: Router no incluido en main
- **Solución**: Verificar que el router esté importado y registrado

#### Error 500 en createCasoAprobacion
- **Causa**: Dependencias faltantes o ID de caso inválido
- **Solución**: Verificar dependencies.py y que el caso original exista

#### Error de CORS
- **Causa**: Frontend no puede comunicarse con backend
- **Solución**: Verificar configuración CORS en settings.py

#### Error de Autenticación
- **Causa**: Token no válido o expirado
- **Solución**: Verificar que el usuario esté logueado correctamente
