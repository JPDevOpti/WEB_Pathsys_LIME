# 🧬 WEB-LIS PathSys

Sistema de gestión de muestras para laboratorio patológico.  
Tecnologías: **Vue 3** + **FastAPI** + **MongoDB**

## 🚀 Uso rápido (macOS/Linux)

Este repositorio incluye el script `Run.sh` para orquestar Front-end, Back-end y MongoDB.

```bash
# Primera vez (instala dependencias y prepara entorno)
./Run.sh setup

# Iniciar todo (MongoDB + API + Front)
./Run.sh full

# Ver estado
./Run.sh status

# Detener servicios
./Run.sh stop
```

### Acceso

- **App (Frontend)**: <http://localhost:5174>
- **API Docs (Swagger)**: <http://localhost:8000/docs>

Notas:

- El Front-end corre por defecto en el puerto 5174 (configurado en Vite).
- La API corre por defecto en el puerto 8000 (Uvicorn).

## 📋 Comandos disponibles (Run.sh)

| Comando | Descripción |
|---------|-------------|
| `./Run.sh setup` | Instala dependencias Front-end y Back-end; prepara MongoDB |
| `./Run.sh full` | Inicia MongoDB, API y Front-end |
| `./Run.sh backend` | Inicia solo la API (FastAPI en 8000) |
| `./Run.sh frontend` | Inicia solo el Front-end (Vite en 5174) |
| `./Run.sh mongodb` | Inicia solo MongoDB |
| `./Run.sh init` | Muestra opciones para inicializar datos (scripts disponibles) |
| `./Run.sh status` | Muestra el estado de servicios y puertos |
| `./Run.sh stop` | Detiene todos los procesos |
| `./Run.sh clean` | Limpieza forzada de MongoDB |
| `./Run.sh import-pruebas ...` | Importa pruebas desde un Excel al Backend |

Para ver todas las opciones con ejemplos: `./Run.sh help`.

## 💡 Prerrequisitos

- **Node.js** 18+
- **Python** 3.8+
- **MongoDB** 4.4+

Variables de entorno recomendadas (Back-end):

- `SECRET_KEY`: clave JWT para producción (obligatoria en prod).
- `MONGODB_URL`: URL de conexión a MongoDB (por defecto `mongodb://localhost:27017`).
- `DATABASE_NAME`: nombre de la base (por defecto `lime_pathsys`).

## 🧱 Arquitectura

- `Back-End/`: FastAPI + Motor (MongoDB). Módulos por dominio (`auth`, `pacientes`, `casos`, `pruebas`, etc.) con capas `models`, `repositories`, `routes`, `schemas`, `services` y utilidades en `shared/`.
- `Front-end/`: Vue 3 + Pinia + Vue Router + Tailwind. Módulos por feature (`dashboard`, `cases`, `profile`, `results`, `reports`, etc.).
- Orquestación local con `Run.sh`.


Si necesitas guía para poblar datos (scripts de importación) o ejecutar con Docker, abre `./Run.sh help` y revisa la carpeta `Back-End/scripts/`.
