# Guía de Consistencia para Scripts de Importación

Esta guía documenta las reglas de consistencia que deben seguir los scripts de importación para mantener la integridad de los datos con los módulos de la aplicación.

## 📋 Reglas Generales

### 1. Validación de Campos
- Todos los scripts deben validar las restricciones de longitud de campos antes de insertar datos
- Usar los esquemas de validación de los módulos correspondientes
- Manejar errores de validación de forma consistente

### 2. Estructura de Datos
- Los datos insertados deben coincidir exactamente con la estructura esperada por los modelos
- Validar tipos de datos antes de la inserción
- Asegurar que campos requeridos no estén vacíos

### 3. Manejo de Errores
- Implementar validación en modo `dry-run` para detectar problemas antes de la inserción
- Proporcionar mensajes de error claros y específicos
- Continuar procesando otros registros cuando sea posible

## 🔧 Módulos Específicos

### Entidades (`import_entities.py`)

**Restricciones:**
- `entidad_name`: 2-200 caracteres
- `entidad_code`: 2-20 caracteres
- `observaciones`: opcional, máximo 500 caracteres

**Validaciones:**
```python
# Validar longitud del nombre
if len(entidad_name) < 2 or len(entidad_name) > 200:
    raise ValueError("Nombre debe tener entre 2 y 200 caracteres")

# Validar longitud del código
if len(entidad_code) < 2 or len(entidad_code) > 20:
    raise ValueError("Código debe tener entre 2 y 20 caracteres")
```

### Patólogos (`import_pathologists.py`)

**Restricciones:**
- `patologo_name`: 2-100 caracteres
- `iniciales_patologo`: 2-10 caracteres
- `patologo_code`: 6-10 caracteres
- `patologo_email`: formato de email válido
- `registro_medico`: 5-50 caracteres

**Validaciones:**
```python
# Validar longitud del código
if len(patologo_code) < 6 or len(patologo_code) > 10:
    print(f"[SKIP] {patologo_name} ({patologo_code}) -> Código debe tener entre 6 y 10 caracteres")
    continue
```

### Residentes (`import_residents.py`)

**Restricciones:**
- `residente_name`: 2-100 caracteres
- `iniciales_residente`: 2-10 caracteres
- `residente_code`: 8-20 caracteres
- `residente_email`: formato de email válido
- `registro_medico`: 3-50 caracteres

**Validaciones:**
```python
# Validar longitud del código
if len(residente_code) < 8 or len(residente_code) > 20:
    print(f"[SKIP] {residente_name} ({residente_code}) -> Código debe tener entre 8 y 20 caracteres")
    continue
```

### Pruebas (`import_tests.py`)

**Restricciones:**
- `prueba_name`: 2-200 caracteres
- `prueba_code`: 2-20 caracteres
- `prueba_description`: opcional, máximo 500 caracteres
- `tiempo`: > 0 y <= 1440 minutos (24 horas)

**Validaciones:**
```python
# Convertir horas a minutos
tiempo_minutes = 360  # 6 horas en minutos

# Validar tiempo
if tiempo_minutes <= 0 or tiempo_minutes > 1440:
    raise ValueError("Tiempo debe ser > 0 y <= 1440 minutos")
```

### Enfermedades (`import_diseases.py`, `import_cancer_diseases.py`)

**Restricciones:**
- `tabla`: campo requerido
- `codigo`: campo requerido
- `nombre`: campo requerido
- `descripcion`: opcional

**Validaciones:**
```python
# Validar campos requeridos
if not codigo or not nombre:
    print(f"Fila {index + 1}: Saltada - código o nombre vacío")
    continue
```

### Pacientes (`seed_patients.py`)

**Restricciones:**
- `nombre`: 2-200 caracteres
- `edad`: 0-150 años
- `sexo`: valores válidos del enum
- `entidad_info`: estructura con `id` y `nombre`
- `tipo_atencion`: valores válidos del enum

**Validaciones:**
```python
# Asegurar estructura correcta de entidad_info
entidad_info = {
    "id": str(entidad.get("_id") or entidad.get("id")), 
    "nombre": entidad.get("entidad_name") or entidad.get("EntidadName") or "Entidad Desconocida"
}
```

## 🧪 Script de Validación

Se incluye un script de validación (`validate_consistency.py`) que verifica automáticamente la consistencia entre los scripts y los módulos.

**Uso:**
```bash
cd Back-End
python3 scripts/validate_consistency.py
```

## 📝 Checklist de Consistencia

Antes de ejecutar cualquier script de importación, verificar:

- [ ] Los campos tienen las longitudes correctas según los esquemas
- [ ] Los tipos de datos coinciden con los modelos
- [ ] Los campos requeridos están presentes
- [ ] Las validaciones están implementadas
- [ ] El manejo de errores es consistente
- [ ] Los datos de prueba pasan la validación

## 🚨 Problemas Comunes

### 1. Longitud de Códigos
- **Patólogos**: Códigos de 8 caracteres exceden el límite de 6-10
- **Residentes**: Códigos de 10 caracteres están dentro del rango 8-20
- **Solución**: Validar longitud antes de insertar

### 2. Unidades de Tiempo
- **Pruebas**: El campo `tiempo` debe estar en minutos, no en horas
- **Solución**: Convertir horas a minutos (6 horas = 360 minutos)

### 3. Estructura de Datos
- **Pacientes**: `entidad_info` debe tener estructura `{id, nombre}`
- **Solución**: Validar y corregir estructura antes de insertar

### 4. Campos Opcionales
- **Observaciones**: Pueden ser `None` o string vacío
- **Solución**: Manejar ambos casos consistentemente

## 🔄 Proceso de Actualización

Cuando se modifiquen los esquemas de validación:

1. Actualizar esta guía con las nuevas restricciones
2. Modificar los scripts de importación correspondientes
3. Ejecutar el script de validación
4. Probar con datos de ejemplo
5. Documentar los cambios

## 📊 Monitoreo

- Ejecutar validaciones regularmente
- Revisar logs de errores de importación
- Mantener datos de prueba actualizados
- Documentar casos edge encontrados
