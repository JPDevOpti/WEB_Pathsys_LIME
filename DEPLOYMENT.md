# 🚀 Guía de Despliegue - WEB-LIS PathSys

## 📋 Resumen del Sistema

- **Frontend**: Vue.js + Vite desplegado en Vercel
- **Backend**: FastAPI + Python desplegado en Railway/Render
- **Base de Datos**: MongoDB Atlas
- **Contenedores**: Docker optimizado para producción

## 🌐 Despliegue del Backend

### Opción 1: Railway (Recomendado)

#### 1. Instalar Railway CLI
```bash
npm install -g @railway/cli
```

#### 2. Iniciar sesión
```bash
railway login
```

#### 3. Desplegar automáticamente
```bash
./deploy.sh railway
```

### Opción 2: Render

#### 1. Ir a [Render.com](https://render.com)
#### 2. Crear cuenta o iniciar sesión
#### 3. Crear nuevo "Web Service"
#### 4. Conectar repositorio de GitHub
#### 5. Configurar variables de entorno:

```env
MONGODB_URL=mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/
DATABASE_NAME=lime_pathsys
ENVIRONMENT=production
DEBUG=false
SECRET_KEY=tu_clave_secreta_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=30
PORT=8000
```

#### 6. Build Command:
```bash
pip install -r requirements.txt
```

#### 7. Start Command:
```bash
uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

## 🔧 Configuración del Frontend (Vercel)

### 1. Variables de Entorno en Vercel

Configura estas variables en tu proyecto de Vercel:

```env
VITE_API_BASE_URL=https://tu-backend-url.railway.app
VITE_APP_NAME=WEB-LIS PathSys
VITE_APP_VERSION=2.0.0
VITE_APP_ENVIRONMENT=production
```

### 2. Actualizar configuración de API

El frontend ya está configurado para usar la URL del backend desde las variables de entorno.

## 📊 Verificación del Despliegue

### 1. Verificar Backend
```bash
# Health check
curl https://tu-backend-url.railway.app/health

# API info
curl https://tu-backend-url.railway.app/api/v1/info
```

### 2. Verificar Frontend
- Abrir tu aplicación en Vercel
- Verificar que se conecte al backend
- Probar funcionalidades principales

### 3. Verificar Base de Datos
- MongoDB Atlas debe estar accesible
- Las conexiones deben funcionar correctamente

## 🐳 Archivos de Docker

### Dockerfile.atlas
- Optimizado para producción
- Usa Python 3.11-slim
- Configurado para servicios en la nube
- Maneja variable PORT automáticamente

### docker-compose.atlas.yml
- Configuración para MongoDB Atlas
- Sin servicio de MongoDB local
- Variables de entorno desde archivo de configuración

## 🔒 Seguridad

### Variables Sensibles
- **NO** subir `.env` files al repositorio
- Usar variables de entorno en los servicios
- Cambiar `SECRET_KEY` en producción
- Configurar CORS correctamente

### CORS Configuration
```python
BACKEND_CORS_ORIGINS = [
    "https://tu-frontend.vercel.app",
    "http://localhost:5174"  # Para desarrollo local
]
```

## 📈 Monitoreo y Logs

### Railway
- Logs automáticos en el dashboard
- Métricas de rendimiento
- Escalado automático

### Render
- Logs en tiempo real
- Métricas de uso
- Alertas configurables

### MongoDB Atlas
- Monitoreo de conexiones
- Métricas de rendimiento
- Alertas de uso

## 🚨 Troubleshooting

### Problemas Comunes

#### 1. Backend no responde
- Verificar variables de entorno
- Revisar logs del servicio
- Verificar conexión a MongoDB Atlas

#### 2. CORS Errors
- Verificar configuración de CORS
- Asegurar que la URL del frontend esté incluida

#### 3. Conexión a Base de Datos
- Verificar URL de MongoDB Atlas
- Revisar credenciales
- Verificar reglas de firewall

### Comandos de Diagnóstico

```bash
# Ver estado del despliegue
./deploy.sh status

# Ver logs del backend
railway logs  # Si usas Railway

# Verificar conectividad
curl -v https://tu-backend-url.railway.app/health
```

## 🔄 Actualizaciones

### Backend
1. Hacer push a la rama principal
2. El servicio se actualiza automáticamente
3. Verificar que funcione correctamente

### Frontend
1. Hacer push a la rama principal
2. Vercel despliega automáticamente
3. Verificar integración con backend

## 📞 Soporte

- **Railway**: [docs.railway.app](https://docs.railway.app)
- **Render**: [render.com/docs](https://render.com/docs)
- **Vercel**: [vercel.com/docs](https://vercel.com/docs)
- **MongoDB Atlas**: [docs.atlas.mongodb.com](https://docs.atlas.mongodb.com)

---

**¡Tu sistema WEB-LIS PathSys está listo para producción! 🎉**
