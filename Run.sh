#!/bin/zsh
# Script de ejecución para WEB-LIS PathSys en macOS

set -e

# Variables de configuración
DOCKER_COMPOSE_FILE="Back-End/docker-compose.yml"
DOCKER_COMPOSE_DEV_FILE="Back-End/docker-compose.dev.yml"
DOCKER_COMPOSE_ATLAS_FILE="Back-End/docker-compose.atlas.yml"
MONGODB_ATLAS_URL=""

function setup() {
  echo "🔧 Verificando dependencias del sistema..."
  
  # Verificar Docker
  if ! command -v docker &> /dev/null; then
    echo "❌ Docker no está instalado. Instalando..."
    brew install --cask docker
    echo "✅ Docker instalado. Por favor, inicia Docker Desktop y ejecuta este script nuevamente."
    exit 1
  else
    echo "✅ Docker ya está instalado"
  fi
  
  # Verificar Docker Compose
  if ! command -v docker-compose &> /dev/null; then
    echo "❌ Docker Compose no está instalado. Instalando..."
    brew install docker-compose
  else
    echo "✅ Docker Compose ya está instalado"
  fi
  
  # Verificar MongoDB local (opcional)
  if ! command -v mongod &> /dev/null; then
    echo "⚠️  MongoDB local no está instalado. Se usará Docker para MongoDB local."
    echo "   Para instalar MongoDB local: brew tap mongodb/brew && brew install mongodb-community"
  else
    echo "✅ MongoDB local ya está instalado"
  fi
  
  echo "📦 Instalando dependencias Front-End..."
  if cd Front-End && npm install && cd ..; then
    echo "✅ Dependencias Front-End instaladas"
  else
    echo "❌ Error instalando dependencias Front-End"
    exit 1
  fi
  
  echo "🐍 Instalando dependencias Back-End..."
  if cd Back-End && pip3 install -r requirements.txt && cd ..; then
    echo "✅ Dependencias Back-End instaladas"
  else
    echo "❌ Error instalando dependencias Back-End"
    exit 1
  fi
  
  echo "✅ Configuración completada"
}

function setup_atlas() {
  echo "🌐 Configurando MongoDB Atlas..."
  
  if [ -z "$MONGODB_ATLAS_URL" ]; then
    echo "📝 Por favor, ingresa tu URL de conexión de MongoDB Atlas:"
    echo "   Formato: mongodb+srv://usuario:password@cluster.mongodb.net/database?retryWrites=true&w=majority"
    read -r MONGODB_ATLAS_URL
    
    if [ -z "$MONGODB_ATLAS_URL" ]; then
      echo "❌ URL de MongoDB Atlas requerida"
      return 1
    fi
  fi
  
  # Crear archivo de configuración para Atlas
  cat > Back-End/config.atlas.env << EOF
MONGODB_URL=$MONGODB_ATLAS_URL
DATABASE_NAME=lime_pathsys
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  
  echo "✅ Configuración de MongoDB Atlas completada"
  echo "📁 Archivo de configuración creado: Back-End/config.atlas.env"
}

function start_mongodb() {
  echo "Iniciando MongoDB..."
  # Verificar si MongoDB ya está corriendo
  if pgrep -f mongod > /dev/null; then
    echo "✅ MongoDB ya está corriendo"
  else
    brew services start mongodb/brew/mongodb-community
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 5
    echo "✅ MongoDB iniciado en puerto 27017"
  fi
}

function start_backend() {
  echo "🚀 Iniciando API FastAPI (Backend)..."
  
  # Verificar que MongoDB esté corriendo
  if ! pgrep -f mongod > /dev/null; then
    echo "⚠️  MongoDB no está corriendo. Iniciándolo..."
    start_mongodb
  fi
  
  # Verificar si el puerto ya está en uso y liberarlo completamente
  if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  El puerto 8000 ya está en uso. Deteniendo proceso..."
    pkill -f "uvicorn.*8000" || true
    pkill -f "python3.*uvicorn" || true
    # Forzar liberación del puerto
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 3
  fi
  
  cd Back-End && python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  cd ..
  
  echo "✅ Backend iniciado (PID: $BACKEND_PID)"
}

function start_frontend() {
  echo "🌐 Iniciando Front-End..."
  
  # Verificar si el puerto 5174 está en uso y liberarlo
  if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Puerto 5174 en uso. Deteniendo proceso..."
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    # Forzar liberación del puerto
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    sleep 2
  fi
  
  # Verificar que estemos en el directorio correcto y que npm esté disponible
  if [ ! -f "Front-End/package.json" ]; then
    echo "❌ Error: No se encontró package.json en Front-End/"
    return 1
  fi
  
  cd Front-End
  # Verificar que vite esté instalado
  if ! npx vite --version >/dev/null 2>&1; then
    echo "⚠️  Vite no encontrado. Instalando dependencias..."
    npm install --legacy-peer-deps
  fi
  
  npm run dev &
  FRONTEND_PID=$!
  cd ..
  
  echo "✅ Frontend iniciado (PID: $FRONTEND_PID)"
}

function start_docker() {
  echo "🐳 Iniciando servicios con Docker..."
  
  # Verificar que Docker esté corriendo
  if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop."
    return 1
  fi
  
  # Detener contenedores existentes
  echo "🛑 Deteniendo contenedores existentes..."
  docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
  
  # Construir e iniciar servicios
  echo "🔨 Construyendo e iniciando servicios..."
  docker-compose -f "$DOCKER_COMPOSE_FILE" up --build -d
  
  echo "⏳ Esperando que los servicios estén listos..."
  sleep 10
  
  echo "✅ Servicios Docker iniciados"
  echo "📊 MongoDB: mongodb://localhost:27017"
  echo "🔧 API: http://localhost:8000"
  echo "📖 API Docs: http://localhost:8000/docs"
  echo "🗄️  Mongo Express: http://localhost:8081"
}

function start_docker_dev() {
  echo "🐳 Iniciando servicios de desarrollo con Docker..."
  
  # Verificar que Docker esté corriendo
  if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop."
    return 1
  fi
  
  # Detener contenedores existentes
  echo "🛑 Deteniendo contenedores existentes..."
  docker-compose -f "$DOCKER_COMPOSE_DEV_FILE" down 2>/dev/null || true
  
  # Construir e iniciar servicios
  echo "🔨 Construyendo e iniciando servicios de desarrollo..."
  docker-compose -f "$DOCKER_COMPOSE_DEV_FILE" up --build -d
  
  echo "⏳ Esperando que los servicios estén listos..."
  sleep 10
  
  echo "✅ Servicios Docker de desarrollo iniciados"
  echo "📊 MongoDB: mongodb://localhost:27017"
  echo "🔧 API: http://localhost:8000"
  echo "📖 API Docs: http://localhost:8000/docs"
  echo "🗄️  Mongo Express: http://localhost:8081"
}

function start_atlas() {
  echo "🌐 Iniciando con MongoDB Atlas..."
  
  # Verificar configuración de Atlas
  if [ ! -f "Back-End/config.atlas.env" ]; then
    echo "❌ Configuración de MongoDB Atlas no encontrada."
    echo "   Ejecuta: ./Run.sh setup-atlas"
    return 1
  fi
  
  # Cargar variables de entorno de Atlas
  export $(cat Back-End/config.atlas.env | xargs)
  
  # Verificar si el puerto ya está en uso
  if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  El puerto 8000 ya está en uso. Deteniendo proceso..."
    pkill -f "uvicorn.*8000" || true
    pkill -f "python3.*uvicorn" || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 3
  fi
  
  # Iniciar backend con configuración de Atlas
  cd Back-End
  python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  cd ..
  
  echo "✅ Backend iniciado con MongoDB Atlas (PID: $BACKEND_PID)"
  echo "🌐 Conectado a: MongoDB Atlas"
  echo "🔧 API: http://localhost:8000"
  echo "📖 API Docs: http://localhost:8000/docs"
}

function start_docker_atlas() {
  echo "🐳 Iniciando servicios con Docker y MongoDB Atlas..."
  
  # Verificar configuración de Atlas
  if [ ! -f "Back-End/config.atlas.env" ]; then
    echo "❌ Configuración de MongoDB Atlas no encontrada."
    echo "   Ejecuta: ./Run.sh setup-atlas"
    return 1
  fi
  
  # Verificar que Docker esté corriendo
  if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop."
    return 1
  fi
  
  # Detener contenedores existentes
  echo "🛑 Deteniendo contenedores existentes..."
  docker-compose -f "$DOCKER_COMPOSE_ATLAS_FILE" down 2>/dev/null || true
  
  # Construir e iniciar servicios
  echo "🔨 Construyendo e iniciando servicios con MongoDB Atlas..."
  docker-compose -f "$DOCKER_COMPOSE_ATLAS_FILE" up --build -d
  
  echo "⏳ Esperando que los servicios estén listos..."
  sleep 10
  
  echo "✅ Servicios Docker con MongoDB Atlas iniciados"
  echo "🌐 MongoDB: MongoDB Atlas"
  echo "🔧 API: http://localhost:8000"
  echo "📖 API Docs: http://localhost:8000/docs"
}

function init_database() {
  echo "🔄 Inicializando base de datos completa..."
  
  # Verificar que MongoDB esté corriendo
  if ! pgrep -f mongod > /dev/null; then
    echo "❌ MongoDB no está corriendo. Iniciando..."
    start_mongodb
  fi
  
  echo "ℹ️  No hay script de inicialización automática."
  echo "    Scripts disponibles: Back-End/scripts/import_tests.py, import_entities.py, seed_cases.py, seed_patients.py"
  
  echo "✅ Inicialización completada."
}

function status() {
  echo "📊 Estado del sistema WEB-LIS PathSys:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Verificar Docker
  if docker info >/dev/null 2>&1; then
    echo "✅ Docker: Corriendo"
    
    # Verificar contenedores Docker
    if docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
      echo "✅ Docker Compose: Contenedores activos"
    else
      echo "❌ Docker Compose: Sin contenedores activos"
    fi
  else
    echo "❌ Docker: No disponible"
  fi
  
  # Verificar MongoDB local
  if pgrep -f mongod > /dev/null; then
    echo "✅ MongoDB Local: Corriendo"
    # Verificar conexión
    if mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
      echo "   └─ Conexión: OK"
    else
      echo "   └─ Conexión: Error"
    fi
  else
    echo "❌ MongoDB Local: Detenido"
  fi
  
  # Verificar Backend
  if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Backend API: Corriendo (puerto 8000)"
    # Verificar endpoint
    if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
      echo "   └─ API: Respondiendo"
    else
      echo "   └─ API: No responde"
    fi
  else
    echo "❌ Backend API: Detenido"
  fi
  
  # Verificar Frontend
  frontend_port=""
  for port in 5173 5174 5175 5176; do
    if lsof -Pi :$port -sTCP:LISTEN -t >/dev/null 2>&1; then
      frontend_port=$port
      break
    fi
  done
  
  if [ -n "$frontend_port" ]; then
    echo "✅ Frontend: Corriendo (puerto $frontend_port)"
  else
    echo "❌ Frontend: Detenido"
  fi
  
  # Verificar MongoDB Atlas
  if [ -f "Back-End/config.atlas.env" ]; then
    echo "✅ MongoDB Atlas: Configurado"
  else
    echo "❌ MongoDB Atlas: No configurado"
  fi
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

function import_pruebas() {
  if [ -z "$1" ]; then
    echo "Uso: ./Run.sh import-pruebas <archivo.xlsx> [--tiempo N] [--activate true|false] [--dry-run]"
    return 1
  fi
  # Asegurar MongoDB corriendo
  if ! pgrep -f mongod > /dev/null; then
    start_mongodb
  fi
  echo "📥 Importando pruebas desde lista embebida (ver scripts/import_tests.py)..."
  # Ejecutar script de importación disponible
  if cd Back-End && python3 scripts/import_tests.py "$@" && cd ..; then
    echo "✅ Importación finalizada"
  else
    echo "❌ Error en la importación"
    return 1
  fi
}

function full() {
  echo "🚀 Iniciando sistema completo WEB-LIS PathSys (Local)..."
  
  start_mongodb
  start_backend
  start_frontend
  
  echo ""
  echo "✅ Sistema completo iniciado."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 MongoDB:   mongodb://localhost:27017"
  echo "🔧 API:       http://localhost:8000"
  echo "📖 Docs API:  http://localhost:8000/docs"
  echo "🌐 Frontend:  http://localhost:5174 (o puerto disponible)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
}

function full_docker() {
  echo "🚀 Iniciando sistema completo WEB-LIS PathSys (Docker)..."
  
  start_docker
  start_frontend
  
  echo ""
  echo "✅ Sistema completo iniciado con Docker."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 MongoDB:   mongodb://localhost:27017"
  echo "🔧 API:       http://localhost:8000"
  echo "📖 Docs API:  http://localhost:8000/docs"
  echo "🗄️  Mongo Express: http://localhost:8081"
  echo "🌐 Frontend:  http://localhost:5174 (o puerto disponible)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
}

function full_atlas() {
  echo "🚀 Iniciando sistema completo WEB-LIS PathSys (MongoDB Atlas)..."
  
  start_atlas
  start_frontend
  
  echo ""
  echo "✅ Sistema completo iniciado con MongoDB Atlas."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🌐 MongoDB:   MongoDB Atlas"
  echo "🔧 API:       http://localhost:8000"
  echo "📖 Docs API:  http://localhost:8000/docs"
  echo "🌐 Frontend:  http://localhost:5174 (o puerto disponible)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
}

function full_docker_atlas() {
  echo "🚀 Iniciando sistema completo WEB-LIS PathSys (Docker + MongoDB Atlas)..."
  
  start_docker_atlas
  start_frontend
  
  echo ""
  echo "✅ Sistema completo iniciado con Docker y MongoDB Atlas."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "🌐 MongoDB:   MongoDB Atlas"
  echo "🔧 API:       http://localhost:8000"
  echo "📖 Docs API:  http://localhost:8000/docs"
  echo "🌐 Frontend:  http://localhost:5174 (o puerto disponible)"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
}

function stop() {
  echo "🛑 Deteniendo procesos WEB-LIS PathSys..."
  
  # Detener contenedores Docker
  echo "  • Deteniendo contenedores Docker..."
  docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
  docker-compose -f "$DOCKER_COMPOSE_DEV_FILE" down 2>/dev/null || true
  docker-compose -f "$DOCKER_COMPOSE_ATLAS_FILE" down 2>/dev/null || true
  
  # Detener procesos específicos por puerto
  echo "  • Deteniendo Backend (puerto 8000)..."
  pkill -f "uvicorn.*8000" || true
  pkill -f "python3.*uvicorn" || true
  lsof -ti:8000 | xargs kill -9 2>/dev/null || true
  
  echo "  • Deteniendo Frontend (puerto 5174)..."
  pkill -f "npm run dev" || true
  pkill -f "vite" || true
  lsof -ti:5174 | xargs kill -9 2>/dev/null || true
  
  echo "  • Deteniendo MongoDB..."
  # Intentar detener con brew services
  brew services stop mongodb/brew/mongodb-community >/dev/null 2>&1 || true
  brew services stop mongodb-community >/dev/null 2>&1 || true
  
  # Forzar terminación de procesos mongod
  pkill -f mongod >/dev/null 2>&1 || true
  lsof -ti:27017 | xargs kill -9 2>/dev/null || true
  
  # Esperar un momento para que los procesos se detengan
  sleep 3
  
  # Verificación final y limpieza si es necesario
  if pgrep -f mongod > /dev/null; then
    echo "  ⚠️  MongoDB aún corriendo, forzando detención..."
    pkill -9 -f mongod >/dev/null 2>&1 || true
    
    # Limpiar archivos de bloqueo
    rm -f /usr/local/var/mongodb/mongod.lock >/dev/null 2>&1 || true
    rm -f /opt/homebrew/var/mongodb/mongod.lock >/dev/null 2>&1 || true
  fi
  
  echo "✅ Todos los procesos detenidos."
}

function force_clean_mongodb() {
  echo "🧹 Limpieza forzada de MongoDB..."
  
  # Detener todos los servicios
  brew services stop mongodb/brew/mongodb-community >/dev/null 2>&1 || true
  brew services stop mongodb-community >/dev/null 2>&1 || true
  
  # Matar todos los procesos
  pkill -f mongod >/dev/null 2>&1 || true
  pkill -9 -f mongod >/dev/null 2>&1 || true
  
  sleep 3
  
  # Limpiar archivos de bloqueo
  echo "  • Limpiando archivos de bloqueo..."
  rm -f /usr/local/var/mongodb/mongod.lock >/dev/null 2>&1 || true
  rm -f /opt/homebrew/var/mongodb/mongod.lock >/dev/null 2>&1 || true
  rm -f /data/db/mongod.lock >/dev/null 2>&1 || true
  
  # Liberar puerto
  if lsof -Pi :27017 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "  • Liberando puerto 27017..."
    lsof -ti:27017 | xargs kill -9 >/dev/null 2>&1 || true
  fi
  
  sleep 2
  
  if pgrep -f mongod > /dev/null; then
    echo "❌ MongoDB aún corriendo después de limpieza"
  else
    echo "✅ MongoDB completamente limpio"
  fi
}

function help() {
  echo "🔧 WEB-LIS PathSys - Script de Control"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📋 Comandos disponibles:"
  echo ""
  echo "🔧 Configuración:"
  echo "  setup        - Instala dependencias del sistema"
  echo "  setup-atlas  - Configura MongoDB Atlas"
  echo ""
  echo "🚀 Inicio completo:"
  echo "  full         - Inicia sistema completo (Local)"
  echo "  full-docker  - Inicia sistema completo (Docker)"
  echo "  full-atlas   - Inicia sistema completo (MongoDB Atlas)"
  echo "  full-docker-atlas - Inicia sistema completo (Docker + MongoDB Atlas)"
  echo ""
  echo "🔧 Servicios individuales:"
  echo "  backend      - Solo inicia el Backend (Local)"
  echo "  frontend     - Solo inicia el Frontend"
  echo "  mongodb      - Solo inicia MongoDB (Local)"
  echo "  docker       - Solo inicia servicios Docker"
  echo "  docker-dev   - Solo inicia servicios Docker (Desarrollo)"
  echo "  docker-atlas - Solo inicia servicios Docker con MongoDB Atlas"
  echo "  atlas        - Solo inicia Backend con MongoDB Atlas"
  echo ""
  echo "🛠️  Utilidades:"
  echo "  init         - Inicializa esquemas de la BD"
  echo "  status       - Muestra el estado del sistema"
  echo "  stop         - Detiene todos los procesos"
  echo "  clean        - Limpieza forzada de MongoDB"
  echo ""
  echo "📥 Importación:"
  echo "  import-pruebas <archivo.xlsx> [--tiempo N] [--activate true|false] [--dry-run]"
  echo "               - Importa pruebas desde un Excel al Backend"
  echo "  import-patologos <archivo.xlsx> [--sheet Docentes] [--domain dominio] [--password Pwd] [--rm-prefix RM-] [--dry-run]"
  echo "               - Importa patólogos (Docentes) desde un Excel"
  echo ""
  echo "❓ Ayuda:"
  echo "  help         - Muestra esta ayuda"
  echo ""
  echo "🌐 URLs del sistema:"
  echo "  Frontend:     http://localhost:5174"
  echo "  API:          http://localhost:8000"
  echo "  API Docs:     http://localhost:8000/docs"
  echo "  MongoDB:      mongodb://localhost:27017"
  echo "  Mongo Express: http://localhost:8081 (Docker)"
  echo ""
  echo "💡 Ejemplos de uso:"
  echo "  ./Run.sh setup        # Primera vez - instalar todo"
  echo "  ./Run.sh setup-atlas  # Configurar MongoDB Atlas"
  echo "  ./Run.sh full         # Iniciar sistema completo (Local)"
  echo "  ./Run.sh full-docker  # Iniciar sistema completo (Docker)"
  echo "  ./Run.sh full-atlas   # Iniciar sistema completo (MongoDB Atlas)"
  echo "  ./Run.sh full-docker-atlas # Iniciar sistema completo (Docker + MongoDB Atlas)"
  echo "  ./Run.sh status       # Ver estado actual"
  echo "  ./Run.sh stop         # Detener todo"
}

case "$1" in
  setup)
    setup
    ;;
  setup-atlas)
    setup_atlas
    ;;
  full)
    full
    ;;
  full-docker)
    full_docker
    ;;
  full-atlas)
    full_atlas
    ;;
  full-docker-atlas)
    full_docker_atlas
    ;;
  backend)
    start_backend
    ;;
  frontend)
    start_frontend
    ;;
  mongodb)
    start_mongodb
    ;;
  docker)
    start_docker
    ;;
  docker-dev)
    start_docker_dev
    ;;
  docker-atlas)
    start_docker_atlas
    ;;
  atlas)
    start_atlas
    ;;
  init)
    init_database
    ;;
  status)
    status
    ;;
  stop)
    stop
    ;;
  clean)
    force_clean_mongodb
    ;;
  import-pruebas)
    shift
    import_pruebas "$@"
    ;;
  help|*)
    help
    ;;
esac
