#!/bin/zsh
# Script de ejecución para WEB-LIS PathSys en macOS

set -e

function setup() {
  echo "🔧 Verificando MongoDB..."
  if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB no está instalado. Instalando..."
    brew tap mongodb/brew
    brew install mongodb-community
  else
    echo "✅ MongoDB ya está instalado"
  fi
  
  echo "📦 Instalando dependencias Front-End..."
  if cd Front-end && npm install && cd ..; then
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
  
  echo "🗄️  Iniciando MongoDB para configuración..."
  # Iniciar MongoDB si no está corriendo
  if ! pgrep -f mongod > /dev/null; then
    brew services start mongodb/brew/mongodb-community
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 5
  fi
  
  echo "ℹ️  Inicialización de base de datos: no se encontró 'Back-End/scripts/init_database.py'."
  echo "    Omitiendo este paso. Usa scripts en 'Back-End/scripts' si lo necesitas."
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
  if [ ! -f "Front-end/package.json" ]; then
    echo "❌ Error: No se encontró package.json en Front-end/"
    return 1
  fi
  
  cd Front-end
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
  
  # Verificar MongoDB
  if pgrep -f mongod > /dev/null; then
    echo "✅ MongoDB: Corriendo"
    # Verificar conexión
    if mongosh --quiet --eval "db.adminCommand('ping')" >/dev/null 2>&1; then
      echo "   └─ Conexión: OK"
    else
      echo "   └─ Conexión: Error"
    fi
  else
    echo "❌ MongoDB: Detenido"
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
  echo "🚀 Iniciando sistema completo WEB-LIS PathSys..."
  
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

function stop() {
  echo "🛑 Deteniendo procesos WEB-LIS PathSys..."
  
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
  echo "  setup        - Instala dependencias del sistema"
  echo "  full         - Inicia MongoDB, Backend y Front-End"
  echo "  backend      - Solo inicia el Backend"
  echo "  frontend     - Solo inicia el Frontend"
  echo "  mongodb      - Solo inicia MongoDB"
  echo "  init         - Inicializa esquemas de la BD"
  echo "  status       - Muestra el estado del sistema"
  echo "  stop         - Detiene todos los procesos"
  echo "  clean        - Limpieza forzada de MongoDB"
  echo "  import-pruebas <archivo.xlsx> [--tiempo N] [--activate true|false] [--dry-run]"
  echo "               - Importa pruebas desde un Excel al Backend"
  echo "  import-patologos <archivo.xlsx> [--sheet Docentes] [--domain dominio] [--password Pwd] [--rm-prefix RM-] [--dry-run]"
  echo "               - Importa patólogos (Docentes) desde un Excel"
  echo "  help         - Muestra esta ayuda"
  echo ""
  echo "🌐 URLs del sistema:"
  echo "  Frontend:     http://localhost:5174"
  echo "  API:          http://localhost:8000"
  echo "  API Docs:     http://localhost:8000/docs"
  echo "  MongoDB:      mongodb://localhost:27017"
  echo ""
  echo "💡 Ejemplos de uso:"
  echo "  ./Run.sh setup       # Primera vez - instalar todo"
  echo "  ./Run.sh init        # Inicializar esquemas de BD"
  echo "  ./Run.sh full        # Iniciar sistema completo"
  echo "  ./Run.sh backend     # Solo iniciar Backend"
  echo "  ./Run.sh frontend    # Solo iniciar Frontend"
  echo "  ./Run.sh status      # Ver estado actual"
  echo "  ./Run.sh stop        # Detener todo"
}

case "$1" in
  setup)
    setup
    ;;
  full)
    full
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
