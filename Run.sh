#!/bin/zsh
# Script de ejecución para WEB-LIS PathSys en macOS

set -e

# Variables de configuración
# Usar el docker-compose disponible en Back-End
DOCKER_COMPOSE_FILE="Back-End/docker-compose.dev.yml"

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
  
  # Verificar Python 3.12
  if ! command -v /opt/homebrew/bin/python3.12 &> /dev/null; then
    echo "❌ Python 3.12 no está instalado. Instalando..."
    brew install python@3.12
  else
    echo "✅ Python 3.12 ya está instalado"
  fi
  
  echo "📦 Instalando dependencias Front-End..."
  if cd Front-End && npm install --legacy-peer-deps || npm install --force; then
    cd ..
    echo "✅ Dependencias Front-End instaladas"
  else
    echo "❌ Error instalando dependencias Front-End"
    exit 1
  fi
  
  echo "🐍 Configurando entorno virtual para Back-End con Python 3.12..."
  if cd Back-End; then
    # Respaldar entorno virtual anterior si existe
    if [ -d "venv" ] && [ ! -d "venv_backup" ]; then
      echo "  • Respaldando entorno virtual anterior..."
      mv venv venv_backup_$(date +%Y%m%d_%H%M%S)
    fi
    
    if [ ! -d "venv" ]; then
      echo "  • Creando entorno virtual con Python 3.12..."
      /opt/homebrew/bin/python3.12 -m venv venv
    fi
    echo "  • Activando entorno virtual..."
    source venv/bin/activate
    echo "  • Actualizando pip..."
    pip install --upgrade pip
    echo "  • Instalando dependencias..."
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    fi
    cd ..
    echo "✅ Dependencias Back-End instaladas en entorno virtual con Python 3.12"
  else
    echo "❌ Error accediendo al directorio Back-End"
    exit 1
  fi
  
  
  echo "✅ Configuración completada"
}

function update_venv() {
  echo "🔄 Actualizando entorno virtual a Python 3.12..."
  
  # Detener procesos de uvicorn si están corriendo
  echo "⏹️  Deteniendo procesos de uvicorn..."
  pkill -f "uvicorn app.main:app" || true
  sleep 2
  
  # Respaldar el entorno virtual actual
  if [ -d "Back-End/venv" ]; then
    echo "💾 Respaldando entorno virtual actual..."
    mv Back-End/venv Back-End/venv_backup_$(date +%Y%m%d_%H%M%S)
  fi
  
  # Crear nuevo entorno virtual con Python 3.12
  echo "🐍 Creando nuevo entorno virtual con Python 3.12..."
  cd Back-End
  /opt/homebrew/bin/python3.12 -m venv venv
  
  # Activar el nuevo entorno
  echo "🔧 Activando entorno virtual..."
  source venv/bin/activate
  
  # Actualizar pip
  echo "⬆️  Actualizando pip..."
  pip install --upgrade pip
  
  # Instalar dependencias
  echo "📦 Instalando dependencias..."
  pip install -r requirements.txt
  
  cd ..
  echo "✅ ¡Entorno virtual actualizado exitosamente!"
  echo "🚀 Para iniciar el servidor:"
  echo "   ./Run.sh local"
}

function setup_atlas() {
  echo "🌐 Configurando MongoDB Atlas..."
  
  # LIMPIAR TODOS los archivos de configuración previos
  echo "🧹 Limpiando archivos de configuración previos..."
  rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
  
  # Crear UN SOLO archivo .env para Back-End ATLAS
  echo "🔧 Configurando Back-End ATLAS..."
  cat > Back-End/.env << EOF
MONGODB_URL=mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/
DATABASE_NAME=lime_pathsys
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  echo "✅ Back-End/.env creado para ATLAS"
  
  # Crear UN SOLO archivo .env para Front-End ATLAS
  echo "🔧 Configurando Front-End ATLAS..."
  cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Atlas)
VITE_APP_ENV=production
VITE_DEV_MODE=false
EOF
  echo "✅ Front-End/.env creado para ATLAS"
  
  echo "✅ Configuración de MongoDB Atlas completada"
  echo "📁 Archivos .env creados para ATLAS"
  echo "⚠️  Para usar Atlas, ejecuta: ./Run.sh docker-atlas"
}

function start_docker() {
  echo "🐳 Iniciando servicios con Docker..."
  
  # LIMPIAR TODOS los archivos de configuración previos
  echo "🧹 Limpiando archivos de configuración previos..."
  rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
  
  # Crear UN SOLO archivo .env para Back-End DOCKER
  echo "🔧 Configurando Back-End DOCKER..."
  cat > Back-End/.env << EOF
MONGODB_URL=mongodb://mongodb:27017
DATABASE_NAME=lime_pathsys
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-please-change-in-prod-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  echo "✅ Back-End/.env creado para DOCKER"
  
  # Crear UN SOLO archivo .env para Front-End DOCKER
  echo "🔧 Configurando Front-End DOCKER..."
  cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Docker)
VITE_APP_ENV=development
VITE_DEV_MODE=true
EOF
  echo "✅ Front-End/.env creado para DOCKER"
  
  # Verificar que Docker esté corriendo
  if ! docker info >/dev/null 2>&1; then
    echo "❌ Docker no está corriendo. Por favor, inicia Docker Desktop."
    return 1
  fi
  
  # Verificar que el archivo docker-compose exista
  if [ ! -f "$DOCKER_COMPOSE_FILE" ]; then
    echo "❌ No se encontró $DOCKER_COMPOSE_FILE."
    echo "   Revisa que exista 'Back-End/docker-compose.dev.yml' o ajusta el script."
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
  
  # LIMPIAR TODOS los archivos de configuración previos
  echo "🧹 Limpiando archivos de configuración previos..."
  rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
  
  # Crear UN SOLO archivo .env para Back-End ATLAS
  echo "🔧 Configurando Back-End ATLAS..."
  cat > Back-End/.env << EOF
MONGODB_URL=mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/
DATABASE_NAME=lime_pathsys
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=your-production-secret-key-change-this
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  echo "✅ Back-End/.env creado para ATLAS"
  
  # Crear UN SOLO archivo .env para Front-End ATLAS
  echo "🔧 Configurando Front-End ATLAS..."
  cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Atlas)
VITE_APP_ENV=production
VITE_DEV_MODE=false
EOF
  echo "✅ Front-End/.env creado para ATLAS"
  
  echo "⚠️  Modo Docker + Atlas no está soportado actualmente porque no existe 'Back-End/docker-compose.atlas.yml'."
  echo "   Usa 'docker' (Mongo local) o 'local'. Si requieres Atlas, puedo habilitarlo ajustando el compose."
  return 1
}

function start_local() {
  echo "🚀 Iniciando sistema completo en LOCAL (Frontend + Back-End + MongoDB Local)..."
  
  # LIMPIAR TODOS los archivos de configuración previos
  echo "🧹 Limpiando archivos de configuración previos..."
  rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
  
  # Crear UN SOLO archivo .env para Back-End LOCAL
  echo "🔧 Configurando Back-End LOCAL..."
  cat > Back-End/.env << EOF
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=lime_pathsys
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-please-change-in-prod-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  echo "✅ Back-End/.env creado para LOCAL"
  
  # Crear UN SOLO archivo .env para Front-End LOCAL
  echo "🔧 Configurando Front-End LOCAL..."
  cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Local)
VITE_APP_ENV=development
VITE_DEV_MODE=true
EOF
  echo "✅ Front-End/.env creado para LOCAL"
  
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
  if [ ! -d "Back-End/venv" ]; then
    echo "🐍 Configurando entorno virtual para Back-End con Python 3.12..."
    cd Back-End
    /opt/homebrew/bin/python3.12 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    pip install -r requirements.txt
    cd ..
  fi
  
  
  # Iniciar MongoDB local
  echo "🗄️  Iniciando MongoDB local..."
  if ! pgrep -f mongod > /dev/null; then
    echo "  • Iniciando MongoDB..."
    brew services start mongodb/brew/mongodb-community
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 8
    
    # Verificar que MongoDB esté respondiendo
    echo "  • Verificando conexión a MongoDB..."
    for i in {1..10}; do
      if mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
        echo "✅ MongoDB iniciado y respondiendo en puerto 27017"
        break
      else
        echo "  ⏳ Intento $i/10: MongoDB aún no responde..."
        sleep 2
      fi
    done
    
    # Verificar una vez más
    if ! mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
      echo "❌ MongoDB no responde después de 10 intentos"
      echo "   Verifica que MongoDB esté instalado correctamente:"
      echo "   brew tap mongodb/brew && brew install mongodb-community"
      exit 1
    fi
  else
    echo "✅ MongoDB ya está corriendo"
    # Verificar que esté respondiendo
    if mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
      echo "✅ MongoDB respondiendo correctamente"
    else
      echo "⚠️  MongoDB está corriendo pero no responde. Reiniciando..."
      brew services restart mongodb/brew/mongodb-community
      sleep 5
    fi
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
  echo "🔧 Iniciando Backend (Back-End) en puerto 8000 con Python 3.12..."
  cd Back-End
  if [ ! -d "venv" ]; then
    echo "  • Creando entorno virtual con Python 3.12..."
    /opt/homebrew/bin/python3.12 -m venv venv
  fi
  if [ -f requirements.txt ]; then
    echo "  • Asegurando dependencias en venv..."
    ./venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1
    ./venv/bin/python -m pip install -r requirements.txt >/dev/null 2>&1 || ./venv/bin/python -m pip install -r requirements.txt
  fi
  ./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
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
  
  # Verificar que el frontend esté respondiendo
  echo "🔍 Verificando conexión frontend-backend..."
  if curl -s http://localhost:5174 >/dev/null 2>&1; then
    echo "✅ Frontend respondiendo en puerto 5174"
  else
    echo "⚠️  Frontend no responde en puerto 5174"
  fi
  
  if curl -s http://localhost:8000/docs >/dev/null 2>&1; then
    echo "✅ Backend respondiendo en puerto 8000"
  else
    echo "⚠️  Backend no responde en puerto 8000"
  fi
  
  
  # Verificar configuración CORS
  echo "🔍 Verificando configuración CORS..."
  if curl -s -H "Origin: http://localhost:5174" http://localhost:8000/health >/dev/null 2>&1; then
    echo "✅ CORS configurado correctamente para puerto 5174"
  else
    echo "⚠️  CORS no configurado correctamente para puerto 5174"
  fi
  
  echo ""
  echo "✅ Sistema completo iniciado en LOCAL."
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "📊 MongoDB:     mongodb://localhost:27017"
  echo "🔧 API:         http://localhost:8000"
  echo "📖 Docs API:    http://localhost:8000/docs"
  echo "🌐 Frontend:    http://localhost:5174"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo "💡 Usa './Run.sh stop' para detener todos los servicios"
}

function start_local_new() {
  echo "🚀 Iniciando sistema con BACKEND NUEVO (Frontend + Back-End + MongoDB Local)..."

  echo "🧹 Limpiando archivos de configuración previos..."
  rm -f Back-End/.env
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local

  echo "🔧 Configurando Back-End LOCAL..."
  cat > Back-End/.env << EOF
MONGODB_URL=mongodb://localhost:27017
DATABASE_NAME=lime_pathsys
ENVIRONMENT=development
DEBUG=True
SECRET_KEY=dev-secret-key-please-change-in-prod-32-chars-min
ACCESS_TOKEN_EXPIRE_MINUTES=30
EOF
  echo "✅ Back-End/.env creado para LOCAL"

  echo "🔧 Configurando Front-End LOCAL (apuntando a puerto 8001)..."
  cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8001
VITE_APP_TITLE=WEB-LIS PathSys (Local New)
VITE_APP_ENV=development
VITE_DEV_MODE=true
EOF
  echo "✅ Front-End/.env creado para LOCAL NEW"

  if ! command -v mongod &> /dev/null; then
    echo "❌ MongoDB no está instalado. Instalando..."
    brew tap mongodb/brew && brew install mongodb-community
  fi

  if [ ! -d "Front-End/node_modules" ]; then
    echo "📦 Instalando dependencias del Frontend..."
    cd Front-End && npm install && cd ..
  fi

  if [ ! -d "Back-End/venv" ]; then
    echo "🐍 Configurando entorno virtual para Back-End con Python 3.12..."
    cd Back-End
    /opt/homebrew/bin/python3.12 -m venv venv
    source venv/bin/activate
    pip install --upgrade pip
    if [ -f requirements.txt ]; then
      pip install -r requirements.txt
    else
      echo "⚠️  requirements.txt no encontrado en Back-End; omitiendo instalación"
    fi
    cd ..
  fi

  echo "🗄️  Asegurando MongoDB local..."
  if ! pgrep -f mongod > /dev/null; then
    echo "  • Iniciando MongoDB..."
    brew services start mongodb/brew/mongodb-community
    echo "⏳ Esperando que MongoDB esté listo..."
    sleep 8
    
    # Verificar que MongoDB esté respondiendo
    echo "  • Verificando conexión a MongoDB..."
    for i in {1..10}; do
      if mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
        echo "✅ MongoDB iniciado y respondiendo en puerto 27017"
        break
      else
        echo "  ⏳ Intento $i/10: MongoDB aún no responde..."
        sleep 2
      fi
    done
    
    # Verificar una vez más
    if ! mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
      echo "❌ MongoDB no responde después de 10 intentos"
      echo "   Verifica que MongoDB esté instalado correctamente:"
      echo "   brew tap mongodb/brew && brew install mongodb-community"
      exit 1
    fi
  else
    echo "✅ MongoDB ya está corriendo"
    # Verificar que esté respondiendo
    if mongosh --eval "db.runCommand('ping')" --quiet >/dev/null 2>&1; then
      echo "✅ MongoDB respondiendo correctamente"
    else
      echo "⚠️  MongoDB está corriendo pero no responde. Reiniciando..."
      brew services restart mongodb/brew/mongodb-community
      sleep 5
    fi
  fi

  if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  El puerto 8001 ya está en uso. Deteniendo proceso..."
    pkill -f "uvicorn.*8001" || true
    pkill -f "python3.*uvicorn" || true
    lsof -ti:8001 | xargs kill -9 2>/dev/null || true
    sleep 2
  fi

  echo "🔧 Iniciando Backend nuevo en puerto 8001 con Python 3.12..."
  cd Back-End
  if [ ! -d "venv" ]; then
    echo "  • Creando entorno virtual con Python 3.12..."
    /opt/homebrew/bin/python3.12 -m venv venv
  fi
  if [ -f requirements.txt ]; then
    echo "  • Asegurando dependencias en venv..."
    ./venv/bin/python -m pip install --upgrade pip >/dev/null 2>&1
    ./venv/bin/python -m pip install -r requirements.txt >/dev/null 2>&1 || ./venv/bin/python -m pip install -r requirements.txt
  fi
  if [ -f app/main.py ]; then
    ./venv/bin/python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8001 &
  else
    echo "❌ No se encontró app/main.py en Back-End"
  fi
  cd ..

  if lsof -Pi :5174 -sTCP:LISTEN -t >/dev/null ; then
    echo "⚠️  Puerto 5174 en uso. Deteniendo proceso..."
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    sleep 2
  fi

  echo "🌐 Iniciando Frontend local..."
  cd Front-End
  npm run dev &
  cd ..

  echo "⏳ Verificando servicios..."
  sleep 5
  if curl -s http://localhost:8001/docs >/dev/null 2>&1; then
    echo "✅ Backend nuevo respondiendo en puerto 8001"
  else
    echo "⚠️  Backend nuevo no responde en puerto 8001"
  fi
  if curl -s http://localhost:5174 >/dev/null 2>&1; then
    echo "✅ Frontend respondiendo en puerto 5174"
  else
    echo "⚠️  Frontend no responde en puerto 5174"
  fi
  echo "✅ Sistema iniciado con BACKEND NUEVO (8001)"
}

function status() {
  echo "📊 Estado del sistema WEB-LIS PathSys:"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  
  # Verificar Docker
  if docker info >/dev/null 2>&1; then
    echo "✅ Docker: Corriendo"
    
    # Verificar contenedores Docker
    if [ -f "$DOCKER_COMPOSE_FILE" ] && docker-compose -f "$DOCKER_COMPOSE_FILE" ps | grep -q "Up"; then
      echo "✅ Docker Compose: Contenedores activos"
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
  
  
  # Verificar configuración de base de datos
  if [ -f "Back-End/.env" ]; then
    echo "✅ Base de datos: Configurada (.env)"
    if grep -q "mongodb://localhost:27017" Back-End/.env; then
      echo "   └─ Tipo: LOCAL (MongoDB local)"
    elif grep -q "mongodb+srv://" Back-End/.env; then
      echo "   └─ Tipo: ATLAS (MongoDB cloud)"
    else
      echo "   └─ Tipo: DESCONOCIDO"
    fi
  else
    echo "❌ Base de datos: Sin configuración (.env)"
  fi
  
  # Verificar configuración del frontend
  if [ -f "Front-End/.env" ]; then
    echo "✅ Frontend: Configurado (.env)"
    if grep -q "VITE_API_BASE_URL=http://localhost:8000" Front-End/.env; then
      echo "   └─ API: http://localhost:8000"
    else
      echo "   └─ API: Configuración personalizada"
    fi
    if grep -q "VITE_APP_ENV=development" Front-End/.env; then
      echo "   └─ Modo: Development"
    elif grep -q "VITE_APP_ENV=production" Front-End/.env; then
      echo "   └─ Modo: Production"
    fi
  else
    echo "❌ Frontend: Sin configuración (.env)"
  fi
  
  # Verificar archivos de configuración adicionales
  if [ -f "Back-End/config.atlas.env" ]; then
    echo "✅ MongoDB Atlas: Archivo de referencia disponible"
  else
    echo "❌ MongoDB Atlas: Archivo de referencia no disponible"
  fi
  
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
}

function stop() {
  echo "🛑 Deteniendo procesos WEB-LIS PathSys..."
  
  # Detener contenedores Docker
  echo "  • Deteniendo contenedores Docker..."
  if [ -f "$DOCKER_COMPOSE_FILE" ]; then
    docker-compose -f "$DOCKER_COMPOSE_FILE" down 2>/dev/null || true
  fi
  
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
  
  # Limpiar archivos de configuración
  echo "  • Limpiando archivos de configuración..."
  rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
  rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
  
  echo "✅ Todos los procesos detenidos."
}

function help() {
  echo " WEB-LIS PathSys - Script de Control"
  echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
  echo " Comandos disponibles:"
  echo ""
  echo " Configuración:"
  echo "  setup        - Instala dependencias del sistema"
  echo "  setup-atlas  - Configura MongoDB Atlas"
  echo "  update-venv  - Actualiza entorno virtual a Python 3.12"
  echo ""
  echo " Inicio:"
  echo "  local        - Inicia servicios en LOCAL (MongoDB local)"
  echo "  docker       - Inicia servicios Docker (MongoDB local)"
  echo "  docker-atlas - Inicia servicios Docker con MongoDB Atlas"
  echo ""
  echo "  Utilidades:"
  echo "  status       - Muestra el estado del sistema"
  echo "  stop         - Detiene todos los procesos"
  echo "  clean        - Limpia archivos de configuración"
  echo "  restart-fe   - Reinicia solo el frontend"
  echo "  debug        - Muestra configuración de archivos .env"
  echo "  help         - Muestra esta ayuda"
  echo ""
  echo " URLs del sistema:"
  echo "  Frontend:     http://localhost:5174"
  echo "  API:          http://localhost:8000"
  echo "  API Docs:     http://localhost:8000/docs"
  echo "  MongoDB:      mongodb://localhost:27017 (local) / MongoDB Atlas (cloud)"
  echo "  Mongo Express: http://localhost:8081 (solo local)"
  echo ""
  echo " Ejemplos de uso:"
  echo "  ./Run.sh setup        # Primera vez - instalar todo"
  echo "  ./Run.sh setup-atlas  # Configurar MongoDB Atlas"
  echo "  ./Run.sh update-venv  # Actualizar a Python 3.12"
  echo "  ./Run.sh local        # Iniciar todo en LOCAL"
  echo "  ./Run.sh docker       # Iniciar con Docker (MongoDB local)"
  echo "  ./Run.sh docker-atlas # Iniciar con Docker + MongoDB Atlas"
  echo "  ./Run.sh status       # Ver estado actual"
  echo "  ./Run.sh stop         # Detener todo"
  echo "  ./Run.sh clean        # Limpiar configuración"
  echo "  ./Run.sh restart-fe   # Reiniciar solo frontend"
  echo "  ./Run.sh debug        # Debuggear configuración"
  echo ""
  echo " Sistema de configuración:"
  echo "  • LOCAL: MongoDB local (puerto 27017) + Frontend Development"
  echo "  • DOCKER: MongoDB local en Docker + Frontend Development"
  echo "  • ATLAS: MongoDB Atlas en la nube + Frontend Production"
  echo "  • Cada comando crea UN SOLO archivo .env por directorio"
  echo "  • Se eliminan automáticamente todos los archivos .env previos"
}

case "$1" in
  setup)
    setup
    ;;
  setup-atlas)
    setup_atlas
    ;;
  update-venv)
    update_venv
    ;;
  local)
    start_local
    ;;
  docker)
    start_docker
    ;;
  local-new)
    start_local_new
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
  clean)
    echo "🧹 Limpiando configuración..."
    rm -f Back-End/.env Back-End/.env.example Back-End/.env.development Back-End/.env.production
    rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
    echo "✅ Todos los archivos .env eliminados"
    ;;
  debug)
    echo "🔍 Debug: Mostrando configuración de archivos .env..."
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
    echo "🔍 Verificando variables de entorno del backend..."
    if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "✅ Backend corriendo en puerto 8000"
      echo "🔍 Probando endpoint de salud..."
      if curl -s http://localhost:8000/health >/dev/null 2>&1; then
        echo "✅ Endpoint /health responde"
        echo "🔍 Probando CORS desde puerto 5174..."
        if curl -s -H "Origin: http://localhost:5174" http://localhost:8000/health >/dev/null 2>&1; then
          echo "✅ CORS funciona correctamente"
        else
          echo "❌ CORS no funciona - Revisar configuración"
        fi
      else
        echo "❌ Endpoint /health no responde"
      fi
    else
      echo "❌ Backend no está corriendo"
    fi
    ;;
  restart-fe)
    echo "🔄 Reiniciando solo el frontend..."
    
    # Detener frontend actual
    echo "  • Deteniendo frontend actual..."
    pkill -f "npm run dev" || true
    pkill -f "vite" || true
    lsof -ti:5174 | xargs kill -9 2>/dev/null || true
    sleep 2
    
    # Verificar que el backend esté corriendo
    if ! lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1; then
      echo "❌ Backend no está corriendo. Ejecuta './Run.sh local' primero."
      return 1
    fi
    
    # LIMPIAR archivos de configuración previos del frontend
    echo "🧹 Limpiando archivos de configuración previos del frontend..."
    rm -f Front-End/.env Front-End/.env.development Front-End/.env.production Front-End/.env.local
    
    # Crear UN SOLO archivo .env para Front-End LOCAL
    echo "🔧 Configurando Front-End LOCAL..."
    cat > Front-End/.env << EOF
VITE_API_BASE_URL=http://localhost:8000
VITE_APP_TITLE=WEB-LIS PathSys (Local)
VITE_APP_ENV=development
VITE_DEV_MODE=true
EOF
    echo "✅ Front-End/.env creado para LOCAL"
    
    # Iniciar frontend
    echo "🌐 Iniciando frontend..."
    cd Front-End
    npm run dev &
    cd ..
    
    echo "⏳ Esperando que el frontend esté listo..."
    sleep 5
    
    if curl -s http://localhost:5174 >/dev/null 2>&1; then
      echo "✅ Frontend reiniciado exitosamente en puerto 5174"
      echo "🌐 URL: http://localhost:5174"
    else
      echo "❌ Error al reiniciar frontend"
    fi
    ;;
  help|*)
    help
    ;;
esac
