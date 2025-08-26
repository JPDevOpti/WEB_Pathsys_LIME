# Documentación del Módulo de Enfermedades

## Estructura del modelo

El módulo de enfermedades maneja la información de enfermedades y códigos de clasificación médica (CIE10, etc.) con la siguiente estructura:

### Campos principales:
- **tabla**: Tabla de referencia (ej: "CIE10")
- **codigo**: Código único de la enfermedad (ej: "A000")
- **nombre**: Nombre completo de la enfermedad
- **descripcion**: Descripción general o categoría de la enfermedad
- **isActive**: Estado activo de la enfermedad
- **created_at**: Fecha de creación
- **updated_at**: Fecha de última actualización

## Endpoints disponibles

### 1. Crear enfermedad
**POST** `/api/v1/enfermedades/`

**Ejemplo de uso:**
```bash
curl -X POST "http://localhost:8000/api/v1/enfermedades/" \
  -H "Content-Type: application/json" \
  -d '{
    "tabla": "CIE10",
    "codigo": "A000",
    "nombre": "COLERA DEBIDO A VIBRIO CHOLERAE 01, BIOTIPO CHOLERAE",
    "descripcion": "COLERA",
    "isActive": true
  }'
```

### 2. Obtener enfermedad por ID
**GET** `/api/v1/enfermedades/{enfermedad_id}`

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/507f1f77bcf86cd799439011"
```

### 3. Obtener enfermedad por código
**GET** `/api/v1/enfermedades/codigo/{codigo}`

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/codigo/A000"
```

### 4. Obtener todas las enfermedades
**GET** `/api/v1/enfermedades/`

**Parámetros de consulta:**
- `skip`: Número de elementos a omitir (default: 0)
- `limit`: Número máximo de elementos a retornar (default: 100, max: 1000)
- `is_active`: Filtrar por estado activo (opcional)

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/?skip=0&limit=50&is_active=true"
```

### 5. Buscar enfermedades por nombre
**GET** `/api/v1/enfermedades/search/nombre`

**Parámetros de consulta:**
- `q`: Término de búsqueda por nombre (requerido)
- `skip`: Número de elementos a omitir (default: 0)
- `limit`: Número máximo de elementos a retornar (default: 100, max: 1000)

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/search/nombre?q=COLERA&skip=0&limit=20"
```

### 6. Buscar enfermedades por código
**GET** `/api/v1/enfermedades/search/codigo`

**Parámetros de consulta:**
- `q`: Término de búsqueda por código (requerido)
- `skip`: Número de elementos a omitir (default: 0)
- `limit`: Número máximo de elementos a retornar (default: 100, max: 1000)

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/search/codigo?q=A00&skip=0&limit=20"
```

### 7. Obtener enfermedades por tabla
**GET** `/api/v1/enfermedades/tabla/{tabla}`

**Parámetros de consulta:**
- `skip`: Número de elementos a omitir (default: 0)
- `limit`: Número máximo de elementos a retornar (default: 100, max: 1000)

**Ejemplo de uso:**
```bash
curl -X GET "http://localhost:8000/api/v1/enfermedades/tabla/CIE10?skip=0&limit=50"
```

### 8. Actualizar enfermedad
**PUT** `/api/v1/enfermedades/{enfermedad_id}`

**Ejemplo de uso:**
```bash
curl -X PUT "http://localhost:8000/api/v1/enfermedades/507f1f77bcf86cd799439011" \
  -H "Content-Type: application/json" \
  -d '{
    "nombre": "Nuevo nombre de la enfermedad",
    "descripcion": "Nueva descripción"
  }'
```

### 9. Eliminar enfermedad (soft delete)
**DELETE** `/api/v1/enfermedades/{enfermedad_id}`

**Ejemplo de uso:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/enfermedades/507f1f77bcf86cd799439011"
```

### 10. Eliminar enfermedad permanentemente
**DELETE** `/api/v1/enfermedades/{enfermedad_id}/permanent`

**Ejemplo de uso:**
```bash
curl -X DELETE "http://localhost:8000/api/v1/enfermedades/507f1f77bcf86cd799439011/permanent"
```

## Casos de uso

### 1. Importación masiva de enfermedades desde Excel
El módulo incluye un script de importación que permite cargar enfermedades desde archivos Excel con las columnas:
- Tabla
- Codigo  
- Nombre
- Descripcion

**Ejemplo de uso del script:**
```bash
# Modo dry-run (solo previsualizar)
python Back-End/scripts/import_diseases.py --dry-run

# Importación real
python Back-End/scripts/import_diseases.py

# Especificar archivo directamente
python Back-End/scripts/import_diseases.py --file "ruta/al/archivo.xlsx"
```

### 2. Búsqueda de enfermedades para diagnósticos
Los endpoints de búsqueda permiten encontrar enfermedades rápidamente por nombre o código, facilitando la selección de diagnósticos en el sistema.

### 3. Gestión de códigos CIE10
El módulo está diseñado para manejar códigos de clasificación internacional de enfermedades, permitiendo:
- Organización por tabla de referencia
- Búsqueda por código específico
- Validación de códigos únicos

### 4. Mantenimiento de catálogos de enfermedades
Permite la gestión completa del catálogo de enfermedades con:
- Creación y actualización de registros
- Desactivación temporal (soft delete)
- Eliminación permanente cuando sea necesario
- Control de versiones con timestamps
