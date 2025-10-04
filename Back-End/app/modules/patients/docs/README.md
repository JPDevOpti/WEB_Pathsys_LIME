# Módulo Pacientes (Documentación General)

Este módulo gestiona la información de pacientes en el backend de PathSys. Proporciona esquemas de datos, servicios de negocio, repositorio de acceso a base de datos y rutas HTTP para exponer una API REST.

## Objetivos
- Crear, consultar, actualizar, cambiar identificación y eliminar pacientes.
- Permitir listados con filtros y búsqueda avanzada.
- Garantizar validaciones de entrada consistentes mediante Pydantic.

## Arquitectura del módulo
- Esquemas (schemas): definen la forma y validaciones de los datos (entrada/salida).
- Repositorio (repositories): interactúa con la base de datos (colección `patients`).
- Servicio (services): contiene la lógica de negocio y orquesta repositorio y validaciones.
- Rutas (routes): exponen endpoints FastAPI que usan el servicio.

## Esquemas y modelos principales
- PatientBase: base común con los campos del paciente.
- PatientCreate: hereda de PatientBase; permite `patient_code` opcional (se puede generar).
- PatientUpdate: solo campos opcionales para actualización parcial.
- PatientResponse: hereda de PatientBase y añade `id`, `created_at`, `updated_at`.
- Enums:
  - IdentificationType (int): tipos de documento (1=Cédula, 2=CE, 3=TI, 4=Pasaporte, 5=Registro Civil, 6=Doc. Extranjero, 7=NIT, 8=Carnet Diplomático, 9=Salvoconducto).
  - Gender (str): Masculino, Femenino.
  - CareType (str): Ambulatorio, Hospitalizado.

## Validaciones claves
- identification_number: solo dígitos, longitud entre 5 y 12.
- Nombres y apellidos: no vacíos, caracteres válidos y capitalización.
- birth_date: formato YYYY-MM-DD válido, no futuro, edad máxima 150 años.
- observations: longitud máxima 500.
- Los enums se serializan usando sus valores (`use_enum_values`).

## Reglas de negocio
- `patient_code` se compone como: `identification_type` (valor numérico) + "-" + `identification_number`.
- Cambio de identificación: actualiza `identification_type`, `identification_number` y recomputa `patient_code`. El servicio se asegura de usar el valor numérico del enum.
- Paginación y límites: `skip≥0`, `limit` por defecto 100 (máx. 1000) para listados.

## Errores y manejo de excepciones
- BadRequestError: datos inválidos o reglas de negocio incumplidas.
- NotFoundError: paciente no encontrado.
- ConflictError: intentos de crear/actualizar que violan unicidad.
- Las rutas capturan estas excepciones y devuelven códigos HTTP 400/404/409/500 según corresponda.

## Base de datos
- Colección principal: `patients`.
- Durante el cambio de identificación, se puede requerir acceso a `cases` para mantener integridad referencial cuando existan casos asociados.

## Consideraciones
- Mantener consistencia de `patient_code` en toda la app (backend y frontend).
- Usar filtros de lista para mejorar rendimiento en grandes volúmenes.
- Evitar loguear datos sensibles.

## Puesta en marcha rápida
- Desarrollo: `python3 -m uvicorn app.main:app --port 8000`.
- Base de ruta API v1: `/api/v1/patients`.