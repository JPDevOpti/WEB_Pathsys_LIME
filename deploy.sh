#!/bin/zsh
# Script de Despliegue para WEB-LIS PathSys

set -e

echo "🚀 Script de Despliegue WEB-LIS PathSys"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

function deploy_railway() {
    echo "🌊 Desplegando en Railway..."
    
    # Verificar que Railway CLI esté instalado
    if ! command -v railway &> /dev/null; then
        echo "❌ Railway CLI no está instalado."
        echo "   Instala con: npm install -g @railway/cli"
        echo "   Luego ejecuta: railway login"
        return 1
    fi
    
    echo "✅ Railway CLI encontrado"
    echo "🔧 Iniciando despliegue..."
    
    cd Back-End
    railway up
    cd ..
    
    echo "✅ Despliegue en Railway completado"
}



function setup_frontend_config() {
    echo "🌐 Configurando Frontend para producción..."
    
    # Crear archivo de configuración del frontend
    cat > Front-End/src/core/config/production.config.ts << EOF
// Configuración de Producción
export const PRODUCTION_CONFIG = {
  // URL del backend desplegado
  API_BASE_URL: process.env.VITE_API_BASE_URL || 'https://your-backend-url.railway.app',
  
  // Configuración de la API
  API_VERSION: '/api/v1',
  
  // Timeout para las peticiones (en ms)
  TIMEOUT: 30000,
  
  // Headers por defecto
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Configuración de reintentos
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000, // ms
  },
  
  // Configuración de caché
  CACHE: {
    ENABLED: true,
    TTL: 5 * 60 * 1000, // 5 minutos
  }
}

// Función para construir URLs completas
export function buildProductionApiUrl(endpoint: string): string {
  return \`\${PRODUCTION_CONFIG.API_BASE_URL}\${PRODUCTION_CONFIG.API_VERSION}\${endpoint}\`
}

// Función para obtener headers con autenticación
export function getProductionAuthHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = { ...PRODUCTION_CONFIG.DEFAULT_HEADERS }
  
  if (token) {
    headers['Authorization'] = \`Bearer \${token}\`
  }
  
  return headers
}
EOF
    
    echo "✅ Configuración de producción del frontend creada"
    echo "📁 Archivo: Front-End/src/core/config/production.config.ts"
}

function show_deployment_status() {
    echo ""
    echo "📊 Estado del Despliegue:"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "✅ Backend: Listo para desplegar en Railway"
    echo "✅ MongoDB Atlas: Configurado"
    echo "✅ Frontend: Desplegado en Vercel"
    echo "✅ Archivos de configuración: Creados"
    echo ""
    echo "🚀 Próximos pasos:"
    echo "   1. Ejecuta: ./deploy.sh railway    # Para Railway"
    echo "   2. Obtén la URL del backend desde Railway"
    echo "   3. Actualiza la URL del backend en Vercel"
    echo "   4. Prueba la conexión completa"
}

function help() {
    echo "🔧 Script de Despliegue WEB-LIS PathSys"
    echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
    echo "📋 Comandos disponibles:"
    echo "  railway        - Desplegar en Railway"
    echo "  frontend       - Configurar frontend para producción"
    echo "  status         - Mostrar estado del despliegue"
    echo "  help           - Mostrar esta ayuda"
    echo ""
    echo "💡 Ejemplos de uso:"
    echo "  ./deploy.sh railway    # Desplegar en Railway"
    echo "  ./deploy.sh frontend   # Configurar frontend"
    echo "  ./deploy.sh status     # Ver estado del despliegue"
}

case "$1" in
    railway)
        deploy_railway
        ;;
    render)
        deploy_render
        ;;
    frontend)
        setup_frontend_config
        ;;
    status)
        show_deployment_status
        ;;
    help|*)
        help
        ;;
esac
