# Guía de Despliegue del Backend en Render

## 📋 Configuración Paso a Paso para Render

### 1. Crear Nuevo Servicio Web Service

1. **Ve a [Render Dashboard](https://dashboard.render.com)**
2. **Haz clic en "New +" → "Web Service"**
3. **Conecta tu repositorio GitHub:** `https://github.com/JPDevOpti/WEB_Pathsys_LIME`

### 2. Configuración del Servicio

**Configuración Básica:**
- **Name:** `web-lis-pathsys-backend`
- **Region:** `Oregon (US West)` (o la más cercana a ti)
- **Branch:** `production`
- **Root Directory:** `Back-End` ⭐ **CRÍTICO: Esto hace que Render ejecute desde la carpeta Back-End**

**Configuración de Build:**
- **Environment:** `Python`
- **Build Command:** `pip install -r requirements.txt`
- **Start Command:** `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### 3. Variables de Entorno

Ve a la sección **"Environment"** y agrega estas variables:

```
MONGODB_URL=mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/
DATABASE_NAME=lime_pathsys
ENVIRONMENT=production
DEBUG=False
SECRET_KEY=Pm-cEMixcQnyVp-5eaXYFxVfEoiwo2KTef4XaujP0Qk
ACCESS_TOKEN_EXPIRE_MINUTES=240
FRONTEND_URL=https://web-lis-pathsys-frontend.onrender.com
```

### 4. Configuración Avanzada (Opcional)

**Auto-Deploy:** ✅ Habilitado (para deploys automáticos)
**Health Check Path:** `/health`

### 5. Desplegar

1. **Haz clic en "Create Web Service"**
2. **Espera a que termine el build** (puede tomar 5-10 minutos)
3. **Verifica que el servicio esté "Live"**

## 🔍 Verificación del Despliegue

### URLs de Verificación:
- **API Principal:** `https://web-lis-pathsys-backend.onrender.com`
- **Health Check:** `https://web-lis-pathsys-backend.onrender.com/health`
- **API Docs:** `https://web-lis-pathsys-backend.onrender.com/docs`

### Respuestas Esperadas:
- **Health Check:** `{"status": "ok"}`
- **API Docs:** Documentación interactiva de FastAPI

## 🛠️ Troubleshooting

### Error: "Module not found"
- Verificar que `Root Directory` esté configurado como `Back-End`
- Verificar que `requirements.txt` esté en la carpeta `Back-End`

### Error: "Port binding failed"
- Verificar que `Start Command` use `$PORT`
- Verificar que el comando sea: `uvicorn app.main:app --host 0.0.0.0 --port $PORT`

### Error: "MongoDB connection failed"
- Verificar que `MONGODB_URL` esté configurado correctamente
- Verificar que la URL de MongoDB Atlas sea válida

### Error: "CORS error"
- Verificar que `FRONTEND_URL` esté configurado
- Verificar que la URL del frontend sea correcta

## 📝 Notas Importantes

1. **SECRET_KEY:** Cambiar por una clave segura de al menos 32 caracteres en producción
2. **MongoDB Atlas:** Asegurar que la IP de Render esté en la whitelist
3. **CORS:** Configurado para permitir el frontend de Render
4. **Logs:** Revisar logs en Render Dashboard para debugging

## 🚀 Próximos Pasos

Una vez que el backend esté desplegado:
1. Anotar la URL del backend (ej: `https://web-lis-pathsys-backend.onrender.com`)
2. Actualizar la variable `VITE_API_BASE_URL` en el frontend
3. Redesplegar el frontend con la nueva configuración
