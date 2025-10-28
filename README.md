# 🧬 WEB-LIS PathSys

Sistema de gestión de muestras para laboratorio patológico.

- Frontend: Vue 3 + Vite + Pinia + Vue Router + TailwindCSS
- Backend: FastAPI (Python 3.12) + Motor (MongoDB)
- Base de datos: MongoDB (local o Atlas)

Este repositorio incluye `Run.sh` para orquestar entornos de ejecución, utilidades y pruebas.

---

## 🚀 Inicio rápido (macOS)

```bash
# 1) Instalar dependencias del sistema y del proyecto
./Run.sh setup

# 2) Ejecutar en local con MongoDB local (API + Frontend)
./Run.sh local

# 3) Ver estado general
./Run.sh status

# 4) Detener todos los servicios
./Run.sh stop
```

Accesos por defecto:
- Frontend: http://localhost:5174
- API Docs (Swagger): http://localhost:8000/docs

Notas:
- `Run.sh` está optimizado para macOS y usa Homebrew. En Linux puedes reutilizar los pasos, pero algunos comandos (brew, rutas de Python 3.12) pueden variar.

---

## 📦 Prerrequisitos

- Node.js 18+
- Docker Desktop (opcional, para modo Docker)
- Python 3.12 (el script lo instalará vía Homebrew si no está presente)

---

## 🧰 Comandos disponibles (Run.sh)

Uso general: `./Run.sh <comando>`

Configuración
- `setup`         Instala dependencias Frontend y Backend, crea venv con Python 3.12
- `setup-atlas`   Crea `.env` para usar MongoDB Atlas (sin Docker)
- `update-venv`   Regenera el entorno virtual a Python 3.12

Inicio de servicios
- `local`         Inicia Frontend + Backend + MongoDB local (brew services)
- `local-atlas`   Inicia Frontend + Backend usando MongoDB Atlas (sin Docker)
- `docker`        Levanta todo con Docker Compose (MongoDB local en contenedor)
- `docker-atlas`  No soportado actualmente (mensaje informativo en el script)
- `local-new`     Inicia un Backend alternativo en puerto 8001 + Frontend (experimental)

Utilidades
- `status`        Muestra el estado de Docker, API, Frontend y configuración
- `stop`          Detiene procesos (Docker, API, Frontend, Mongo local)
- `clean`         Elimina todos los `.env` del Frontend y Backend
- `restart-fe`    Reinicia únicamente el Frontend con `.env` local
- `debug`         Muestra y verifica configuración `.env` y conectividad
- `tests [ops]`   Ejecuta la suite de tests del Backend (pytest) pasando flags

Ayuda
- `help`          Muestra ayuda y ejemplos

---

## 🔬 Pruebas (pytest)

Los tests del Backend se integran en `Run.sh` y ejecutan pytest directamente con configuración consistente.

Comandos útiles:
```bash
# Suite completa (salida concisa)
./Run.sh tests

# Modo detallado (muestra todos los estados y verbose)
./Run.sh tests --full

# Pasar flags a pytest (se reenvían sin modificar)
./Run.sh tests -v -k auth
```

Detalles técnicos:
- Import mode: `--import-mode=importlib` (configurado también en `pytest.ini`).
- Filtros de warnings comunes (Pydantic v2, crypt, utcnow, argon2 version).
- Muestra top de tests más lentos (`--durations=10`).
- Ruta de pruebas apuntada por defecto a `Back-End/app/modules`.

---

## 🌍 Variables de entorno generadas por Run.sh

Backend (`Back-End/.env`):
```
MONGODB_URL=...           # mongodb://localhost:27017 (local) o cadena SRV de Atlas
DATABASE_NAME=lime_pathsys
ENVIRONMENT=development | production
DEBUG=True | False
SECRET_KEY=...
ACCESS_TOKEN_EXPIRE_MINUTES=30
```

Frontend (`Front-End/.env`):
```
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (...)
VITE_APP_ENV=development | production
VITE_DEV_MODE=true | false
```

El script siempre crea un único `.env` por carpeta y limpia archivos previos para evitar confusiones.

---

## 🗺️ Modos de ejecución y URLs

- `local`
  - MongoDB local (brew services)
  - API: http://localhost:8000
  - Frontend: http://localhost:5174

- `local-atlas`
  - Usa MongoDB Atlas (requiere cadena SRV válida)
  - API: http://localhost:8000
  - Frontend: http://localhost:5174

- `docker`
  - Usa `Back-End/docker-compose.dev.yml`
  - MongoDB: mongodb://localhost:27017 (mapeado)
  - API: http://localhost:8000
  - Frontend: http://localhost:5174

- `local-new` (experimental)
  - API alternativa: http://localhost:8001
  - Frontend: http://localhost:5174

---

## 📥 Scripts de importación (datos)

Ubicación: `Back-End/Scripts/`

Disponibles, entre otros:
- `import_tests.py`
- `import_diseases.py` / `import_cancer_diseases.py`
- `import_entities.py`
- `import_pathologists.py`
- `Import_patients.py` / `Import_cases.py`

Ejemplo de uso (con venv activado):
```bash
source Back-End/venv/bin/activate
python Back-End/Scripts/import_tests.py
```

Nota: Algunos scripts requieren archivos Excel en la misma carpeta (ej. `CIE-10.xlsx`, `CIE-O.xlsx`).

---

## 🧩 Solución de problemas

- Docker no corre: abre Docker Desktop y reintenta `./Run.sh docker`.
- Puertos ocupados (8000/5174): usa `./Run.sh stop` y reintenta.
- MongoDB local no responde: `brew services restart mongodb/brew/mongodb-community`.
- Python 3.12 no disponible: `./Run.sh setup` lo instalará con Homebrew.
- Warnings Pydantic v2: son esperados (el proyecto migra gradualmente a `model_dump`).

---

## 📜 Licencia

Este proyecto se distribuye bajo la licencia incluida en el archivo `LICENSE`.