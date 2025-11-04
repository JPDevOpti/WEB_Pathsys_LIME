#!/bin/zsh
# Script de ejecución para WEB-LIS PathSys en macOS

set -e

ensure_python() {
  if ! command -v /opt/homebrew/bin/python3.12 >/dev/null 2>&1; then
    echo "❌ Python 3.12 no está instalado. Instalando..."
    brew install python@3.12
  fi
}

clean_env_files() {
  setopt localoptions null_glob
  local targets=(Back-End/.env Back-End/.env.* Front-End/.env Front-End/.env.*)
  if (( ${#targets[@]} )); then
    rm -f "${targets[@]}"
  fi
}

write_env_files() {
  clean_env_files
  local mode=${1:-local}
  local mongo_url
  if [ "$mode" = "atlas" ]; then
    mongo_url="mongodb+srv://juanrestrepo183:whbyaZSbhn4H7PpO@cluster0.o8uta.mongodb.net/"
  else
    mongo_url="mongodb://localhost:27017/"
  fi
  cat > Back-End/.env <<EOF
MONGODB_URL=${mongo_url}
DATABASE_NAME=lime_pathsys
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-please-change-in-prod-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  cat > Front-End/.env <<'EOF'
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Local)
VITE_APP_ENV=development
VITE_DEV_MODE=true
EOF
}

ensure_frontend_deps() {
  local mode=${1:-ensure}
  if [ "$mode" = "force" ] || [ ! -d "Front-End/node_modules" ]; then
    echo "📦 Instalando dependencias Front-End..."
    (cd Front-End && npm install --legacy-peer-deps || npm install --force)
  fi
}

ensure_backend_deps() {
  local mode=${1:-ensure}
  ensure_python
  local refresh=0
  if [ ! -d "Back-End/venv" ]; then
    echo "🐍 Creando entorno virtual del Back-End..."
    /opt/homebrew/bin/python3.12 -m venv Back-End/venv
    refresh=1
  fi
  if [ "$mode" = "force" ]; then
    refresh=1
  fi
  if (( refresh )); then
    echo "🐍 Instalando dependencias del Back-End..."
    (cd Back-End && . venv/bin/activate && pip install --upgrade pip && [ -f requirements.txt ] && pip install -r requirements.txt)
  fi
}

ensure_mongo_local() {
  local mode=${1:-local}
  if [ "$mode" = "atlas" ]; then
    return
  fi

  if lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ MongoDB local ya está activo (puerto 27017)"
    return
  fi

  if command -v brew >/dev/null 2>&1; then
    echo "🍃 Iniciando MongoDB local con brew services..."
    if brew services start mongodb/brew/mongodb-community >/dev/null 2>&1 || \
       brew services start mongodb-community >/dev/null 2>&1; then
      sleep 2
      if lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ MongoDB local iniciado"
        return
      fi
    fi
  fi

  if command -v mongod >/dev/null 2>&1; then
    echo "🍃 Ejecutando mongod en segundo plano..."
    local log_file="${TMPDIR:-/tmp}/mongod-pathsys.log"
    mkdir -p "${HOME}/data/db" >/dev/null 2>&1 || true
    if mongod --config /opt/homebrew/etc/mongod.conf --fork --logpath "$log_file" >/dev/null 2>&1 || \
       mongod --dbpath "${HOME}/data/db" --fork --logpath "$log_file" >/dev/null 2>&1; then
      sleep 2
      if lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null 2>&1; then
        echo "✅ MongoDB local iniciado (log: $log_file)"
        return
      fi
    fi
  fi

  echo "❌ No fue posible iniciar MongoDB automáticamente. Inicia el servicio manualmente o instala mongodb-community." >&2
  exit 1
}

kill_port() {
  local port=$1
  local label=$2
  local pids
  pids=$(lsof -ti:$port 2>/dev/null || true)
  if [ -n "$pids" ]; then
    echo "⚠️  Liberando puerto $port (${label})..."
    echo "$pids" | xargs kill -9 2>/dev/null || true
    sleep 1
  fi
}

wait_http() {
  local url=$1
  local label=$2
  for _ in {1..10}; do
    if curl -s "$url" >/dev/null 2>&1; then
      echo "✅ $label operativo"
      return 0
    fi
    sleep 1
  done
  echo "⚠️  $label no respondió"
  return 1
}

report_port() {
  local port=$1
  local label=$2
  if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ $label activo (puerto $port)"
  else
    echo "❌ $label detenido"
  fi
}

wait_for_docker() {
  local retries=${1:-15}
  local delay=${2:-2}
  local silent=${3:-false}
  local attempt=1
  while [ $attempt -le $retries ]; do
    if docker info >/dev/null 2>&1; then
      return 0
    fi
    if [ "$silent" != "true" ]; then
      echo "⏳ Esperando Docker (${attempt}/${retries})..."
    fi
    sleep "$delay"
    attempt=$((attempt + 1))
  done
  return 1
}

ensure_docker() {
  if ! command -v docker >/dev/null 2>&1; then
    echo "❌ Docker no está instalado"
    exit 1
  fi
  if ! wait_for_docker; then
    echo "❌ Docker daemon no responde tras varios intentos. Inicia Docker Desktop y vuelve a intentarlo"
    exit 1
  fi
}

start_backend_service() {
  local port=$1
  ensure_backend_deps
  kill_port "$port" "Backend"
  (cd Back-End && ./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port "$port" &) >/dev/null 2>&1
}

start_frontend_service() {
  ensure_frontend_deps
  kill_port 5174 "Frontend"
  (cd Front-End && npm run dev &) >/dev/null 2>&1
}

show_summary() {
  local api_port=$1
  local mongo_label=$2
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 MongoDB:     $mongo_label"
  echo "🔧 API:         http://localhost:${api_port}"
  echo "📖 Docs API:    http://localhost:${api_port}/docs"
  echo "🌐 Frontend:    http://localhost:5174"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todo"
}

start_stack() {
  local api_port=${1:-8000}
  local mongo_label=${2:-"MongoDB"}
  local env_mode=${3:-local}
  write_env_files "$env_mode"
  ensure_mongo_local "$env_mode"
  start_backend_service "$api_port"
  start_frontend_service
  sleep 2
  wait_http "http://localhost:${api_port}/docs" "Backend"
  wait_http "http://localhost:5174" "Frontend"
  show_summary "$api_port" "$mongo_label"
}

start_docker_stack() {
  ensure_docker
  echo "🐳 Iniciando entorno DOCKER..."
  local root_dir
  root_dir=$(cd "$(dirname "$0")" && pwd)
  docker compose -f "$root_dir/docker-compose.yml" up -d --build
  echo "✅ Entorno DOCKER activo"
  echo "🌐 Frontend:    http://localhost:5174"
  echo "🔧 API:         http://localhost:8000"
  echo "📦 MongoDB:     MongoDB Atlas"
}

function setup() {
  echo "🔧 Preparando entorno..."
  ensure_python
  ensure_frontend_deps force
  ensure_backend_deps force
  echo "✅ Configuración completada"
}

# Ejecutar tests directamente con pytest (sin script externo)
function run_tests() {
  echo "🧪 Ejecutando suite de tests..."

  local venv_used=""
  if [ -d "Back-End/venv" ]; then
    . Back-End/venv/bin/activate
    venv_used="Back-End/venv"
  elif [ -d ".venv" ]; then
    . .venv/bin/activate
    venv_used=".venv"
  else
    echo "⚠️  Sin entorno virtual; se usará Python del sistema"
  fi

  local extra_args=()
  local pytest_default=(-q --color=yes --durations=10 --import-mode=importlib \
    -W "ignore:.*Pydantic.*Migration Guide.*:DeprecationWarning" \
    -W "ignore:.*'crypt' is deprecated.*:DeprecationWarning" \
    -W "ignore:.*datetime\\.datetime\\.utcnow\\(\\).*:DeprecationWarning" \
    -W "ignore:.*argon2\.__version__ is deprecated.*:DeprecationWarning" \
    Back-End/app/modules)
  local pytest_full=(-vv --color=yes --durations=10 --import-mode=importlib \
    -W "ignore:.*Pydantic.*Migration Guide.*:DeprecationWarning" \
    -W "ignore:.*'crypt' is deprecated.*:DeprecationWarning" \
    -W "ignore:.*datetime\\.datetime\\.utcnow\\(\\).*:DeprecationWarning" \
    -W "ignore:.*argon2\.__version__ is deprecated.*:DeprecationWarning" \
    Back-End/app/modules)
  local pytest_args=(${pytest_default[@]})

  for arg in "$@"; do
    if [ "$arg" = "--full" ]; then
      pytest_args=(${pytest_full[@]})
    else
      extra_args+=("$arg")
    fi
  done

  set +e
  pytest "${pytest_args[@]}" "${extra_args[@]}"
  local status=$?
  set -e

  if [ $status -eq 0 ]; then
    echo "✅ Tests finalizados sin errores"
  else
    echo "❌ Tests finalizaron con código $status"
  fi

  if [ -n "$venv_used" ] && command -v deactivate >/dev/null 2>&1; then
    deactivate || true
  fi

  return $status
}

function start_local() {
  echo "🚀 Iniciando entorno LOCAL..."
  start_stack 8000 "MongoDB Local" local
}

function start_atlas() {
  echo "🚀 Iniciando entorno LOCAL con MongoDB Atlas..."
  start_stack 8000 "MongoDB Atlas" atlas
}

function status() {
  echo "📊 Estado del sistema WEB-LIS PathSys:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  report_port 8000 "Backend API"
  report_port 5174 "Frontend"

  if [ -f "Back-End/.env" ]; then
    echo "✅ Back-End/.env presente"
    local mongo_url
    mongo_url=$(grep -m1 'MONGODB_URL' Back-End/.env | cut -d'=' -f2-)
    [ -n "$mongo_url" ] && echo "   └─ Base de datos: $mongo_url"
  else
    echo "❌ Falta Back-End/.env"
  fi

  if [ -f "Front-End/.env" ]; then
    echo "✅ Front-End/.env presente"
    grep -q "VITE_API_BASE_URL" Front-End/.env && \
      echo "   └─ API configurada: $(grep -m1 'VITE_API_BASE_URL' Front-End/.env | cut -d'=' -f2)"
  else
    echo "❌ Falta Front-End/.env"
  fi

  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

function stop() {
  echo "🛑 Deteniendo servicios..."
  kill_port 8000 "Backend 8000"
  kill_port 5174 "Frontend"
  kill_port 27017 "MongoDB"
  brew services stop mongodb/brew/mongodb-community >/dev/null 2>&1 || true
  local docker_down_status="skipped"
  if command -v docker >/dev/null 2>&1; then
    if wait_for_docker 10 2 true; then
      local root_dir
      root_dir=$(cd "$(dirname "$0")" && pwd)
      if docker compose -f "$root_dir/docker-compose.yml" down --remove-orphans --volumes >/dev/null 2>&1; then
        docker_down_status="ok"
      else
        docker_down_status="error"
      fi
    else
      echo "⚠️  Docker no está iniciado; no se detuvieron contenedores"
      docker_down_status="unavailable"
    fi
  fi

  case "$docker_down_status" in
    ok)
      echo "✅ Servicios detenidos"
      ;;
    skipped)
      echo "✅ Servicios locales detenidos"
      ;;
    unavailable)
      echo "⚠️  Servicios locales detenidos; inicia Docker si necesitas bajar contenedores"
      ;;
    error)
      echo "⚠️  Error al detener contenedores Docker"
      ;;
  esac
}

function help() {
  echo " WEB-LIS PathSys - Script de Control"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " Comandos disponibles:"
  echo ""
  echo " Configuración:"
  echo "  setup        - Instala dependencias del sistema"
  echo ""
  echo " Inicio:"
  echo "  local        - Inicia servicios en LOCAL (MongoDB local)"
  echo "  atlas        - Inicia servicios en LOCAL con MongoDB Atlas"
  echo "  docker       - Inicia servicios en DOCKER"
  echo ""
  echo "  Utilidades:"
  echo "  status       - Muestra el estado del sistema"
  echo "  stop         - Detiene todos los procesos"
  echo "  clean        - Limpia archivos de configuración"
  echo "  debug        - Muestra configuración de archivos .env"
  echo "  tests [ops]  - Ejecuta la suite de tests (pasa flags a pytest)"
  echo "  help         - Muestra esta ayuda"
  echo ""
  echo " URLs del sistema:"
  echo "  Frontend:     http://localhost:5174"
  echo "  API:          http://localhost:8000"
  echo "  API Docs:     http://localhost:8000/docs"
  echo "  MongoDB:      mongodb://localhost:27017"
  echo ""
  echo " Ejemplos de uso:"
  echo "  ./Run.sh setup        # Primera vez - instalar todo"
  echo "  ./Run.sh local        # Iniciar todo en LOCAL"
  echo "  ./Run.sh status       # Ver estado actual"
  echo "  ./Run.sh stop         # Detener todo"
  echo "  ./Run.sh clean        # Limpiar configuración"
  echo "  ./Run.sh debug        # Debuggear configuración"
  echo "  ./Run.sh tests        # Ejecutar suite de tests"
  echo "  ./Run.sh tests -v     # Ejecutar en modo detallado"
  echo "  ./Run.sh tests --full # Forzar ejecución completa del runner"
  echo ""
  echo " Sistema de configuración:"
  echo "  • LOCAL: MongoDB local (puerto 27017) + Frontend Development"
  echo "  • Cada comando crea UN SOLO archivo .env por directorio"
  echo "  • Se eliminan automáticamente todos los archivos .env previos"
}

case "$1" in
  setup)
    setup
    ;;
  local)
    start_local
    ;;
  docker)
    start_docker_stack
    ;;
  atlas)
    start_atlas
    ;;
  status)
    status
    ;;
  stop)
    stop
    ;;
  clean)
    echo "🧹 Limpiando configuración..."
    clean_env_files
    echo "✅ Archivos .env eliminados"
    ;;
  debug)
    echo "🔍 Debug de configuración"
    echo ""
    echo "📁 Back-End/.env:"
    if [ -f "Back-End/.env" ]; then
      cat Back-End/.env
    else
      echo "❌ No existe"
    fi
    echo ""
    echo "📁 Front-End/.env:"
    if [ -f "Front-End/.env" ]; then
      cat Front-End/.env
    else
      echo "❌ No existe"
    fi
    echo ""
    report_port 8000 "Backend API"
    if curl -s http://localhost:8000/health >/dev/null 2>&1; then
      echo "✅ Endpoint /health responde"
    else
      echo "❌ Endpoint /health no responde"
    fi
    ;;
  tests)
    # Pasar todos los argumentos desde la posición 2 en adelante al runner
    run_tests "${@:2}"
    ;;
  help|*)
    help
    ;;
esac
