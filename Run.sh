#!/bin/zsh
# Script de ejecución para WEB-LIS PathSys en macOS

set -e

# Variables de configuración
DOCKER_COMPOSE_FILE="Back-End/docker-compose.dev.yml"
DOCKER_COMPOSE_ATLAS_FILE="docker-compose.atlas.yml"

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
  
  # URL fija de MongoDB Atlas
  MONGODB_ATLAS_URL="mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/"
  
  echo "  • URL configurada: $MONGODB_ATLAS_URL"
  
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
  echo "🌐 Frontend: http://localhost:5174"
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
  echo "🌐 Frontend: http://localhost:5174"
}

function start_local() {
  echo "🚀 Iniciando sistema completo en LOCAL (Frontend + Backend + MongoDB Local)..."
  
  # Verificar que MongoDB esté instalado
  if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB no está instalado. Instalando..."
    brew tap mongodb/brew && brew install mongodb-community
  fi
  
  # Verificar dependencias del frontend
  if [ ! -d "Front-End/node_modules" ]; then
    echo "📦 Instalando dependencias del Frontend..."
    cd Front-End && npm install && cd ..
  fi
  
  # Verificar dependencias del backend
  if [ ! -d "Back-End/__pycache__" ]; then
    echo "🐍 Instalando dependencias del Backend..."
    cd Back-End && pip3 install -r requirements.txt && cd ..
  fi
  
  # Iniciar MongoDB local
  echo "🗄️  Iniciando MongoDB local..."
  if ! pgrep -f mongod > /dev/null; then
    brew services start mongodb/brew/mongodb-community
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 5
    echo "✅ MongoDB iniciado en puerto 27017"
  else
    echo "✅ MongoDB ya está corriendo"
  fi
  
  # Verificar si el puerto 8000 ya está en uso
  if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  El puerto 8000 ya está en uso. Deteniendo proceso..."
    pkill -f "uvicorn.*8000" || true
    pkill -f "python3.*uvicorn" || true
    lsof -ti:8000 | xargs kill -9 2>/dev/null || true
    sleep 3
  fi
  
  # Iniciar backend local
  echo "🔧 Iniciando Backend local..."
  cd Back-End
  python3 -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
  BACKEND_PID=$!
  cd ..
  
  # Verificar si el puerto 5174 ya está en uso
  if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Puerto 5174 en uso. Deteniendo proceso..."
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    sleep 2
  fi
  
  # Iniciar frontend local
  echo "🌐 Iniciando Frontend local..."
  cd Front-End
  npm run dev &
  FRONTEND_PID=$!
  cd ..
  
  echo "⏳ Esperando que los servicios estén listos..."
  sleep 5
  
  echo ""
  echo "✅ Sistema completo iniciado en LOCAL."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 MongoDB:   mongodb://localhost:27017"
  echo "🔧 API:       http://localhost:8000"
  echo "📖 Docs API:  http://localhost:8000/docs"
  echo "🌐 Frontend:  http://localhost:5174"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
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
    elif docker-compose -f "$DOCKER_COMPOSE_ATLAS_FILE" ps | grep -q "Up"; then
      echo "✅ Docker Compose: Stack Atlas activo"
    else
      echo "❌ Docker Compose: Sin contenedores activos"
    fi
  else
    echo "❌ Docker: No disponible"
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
  if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo "✅ Frontend: Corriendo (puerto 5174)"
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

function stop() {
  echo "🛑 Deteniendo procesos WEB-LIS PathSys..."
  
  # Detener contenedores Docker
  echo "  • Deteniendo contenedores Docker..."
  docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
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
  
  # Detener MongoDB local
  echo "  • Deteniendo MongoDB local..."
  brew services stop mongodb/brew/mongodb-community >/dev/null 2>&1 || true
  pkill -f mongod >/dev/null 2>&1 || true
  lsof -ti:27017 | xargs kill -9 2>/dev/null || true
  
  echo "✅ Todos los procesos detenidos."
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
  echo "🚀 Inicio:"
  echo "  local        - Inicia servicios en LOCAL (MongoDB local)"
  echo "  docker       - Inicia servicios Docker (MongoDB local)"
  echo "  docker-atlas - Inicia servicios Docker con MongoDB Atlas"
  echo ""
  echo "🛠️  Utilidades:"
  echo "  status       - Muestra el estado del sistema"
  echo "  stop         - Detiene todos los procesos"
  echo "  help         - Muestra esta ayuda"
  echo ""
  echo "🌐 URLs del sistema:"
  echo "  Frontend:     http://localhost:5174"
  echo "  API:          http://localhost:8000"
  echo "  API Docs:     http://localhost:8000/docs"
  echo "  MongoDB:      mongodb://localhost:27017 (local) / MongoDB Atlas (cloud)"
  echo "  Mongo Express: http://localhost:8081 (solo local)"
  echo ""
  echo "💡 Ejemplos de uso:"
  echo "  ./Run.sh setup        # Primera vez - instalar todo"
  echo "  ./Run.sh setup-atlas  # Configurar MongoDB Atlas"
  echo "  ./Run.sh local        # Iniciar todo en LOCAL"
  echo "  ./Run.sh docker       # Iniciar con Docker (MongoDB local)"
  echo "  ./Run.sh docker-atlas # Iniciar con Docker + MongoDB Atlas"
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
  local)
    start_local
    ;;
  docker)
    start_docker
    ;;
  docker-atlas)
    start_docker_atlas
    ;;
  status)
    status
    ;;
  stop)
    stop
    ;;
  help|*)
    help
    ;;
esac
