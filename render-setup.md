# 🚀 DESPLIEGUE EN RENDER.COM - WEB-LIS PathSys

## 📋 REQUISITOS PREVIOS

1. **Cuenta en Render.com** (gratuita)
2. **Repositorio en GitHub** con este código
3. **MongoDB Atlas** configurado (ya tienes)

## 🔧 PASOS PARA DESPLIEGUE

### **PASO 1: Conectar GitHub a Render**

1. Ve a [render.com](https://render.com)
2. Crea una cuenta o inicia sesión
3. Haz clic en "New +" → "Blueprint"
4. Conecta tu repositorio de GitHub
5. Selecciona este repositorio

### **PASO 2: Configurar Blueprint**

1. Render detectará automáticamente el archivo `render.yaml`
2. Verifica que los servicios estén configurados:
   - **pathsys-backend** (Python)
   - **pathsys-frontend** (Static Site)

### **PASO 3: Variables de Entorno**

El backend se configurará automáticamente con:
- `MONGODB_URL`: Tu URL de MongoDB Atlas
- `SECRET_KEY`: Generada automáticamente por Render
- `ENVIRONMENT`: production
- `DEBUG`: false

### **PASO 4: Desplegar**

1. Haz clic en "Apply"
2. Render construirá y desplegará ambos servicios
3. Espera a que ambos estén "Live"

## 🌐 URLs DESPUÉS DEL DESPLIEGUE

- **Backend API**: `https://pathsys-backend.onrender.com`
- **Frontend**: `https://pathsys-frontend.onrender.com`
- **API Docs**: `https://pathsys-backend.onrender.com/docs`
- **Health Check**: `https://pathsys-backend.onrender.com/health`

## 🔍 VERIFICACIÓN DEL DESPLIEGUE

### **Backend:**
```bash
curl https://pathsys-backend.onrender.com/health
# Debe responder: {"status": "healthy"}
```

### **Frontend:**
- Abre `https://pathsys-frontend.onrender.com`
- Debe cargar la aplicación Vue.js
- Verifica que pueda conectarse al backend

## 🚨 SOLUCIÓN DE PROBLEMAS

### **Error de CORS:**
- Verifica que las URLs estén en `BACKEND_CORS_ORIGINS`
- Asegúrate de que el frontend use HTTPS

### **Error de MongoDB:**
- Verifica que la URL de Atlas sea correcta
- Confirma que la IP de Render esté en la whitelist de Atlas

### **Error de Build:**
- Revisa los logs de build en Render
- Verifica que `requirements.txt` esté en la raíz

## 💰 COSTOS

- **Plan Gratuito**: 750 horas/mes
- **Backend**: ~$7/mes después de las horas gratuitas
- **Frontend**: Siempre gratuito (sitio estático)
- **Base de datos**: MongoDB Atlas (ya tienes)

## 🔄 ACTUALIZACIONES AUTOMÁTICAS

- Cada push a `main` activará un nuevo despliegue
- Los cambios se reflejarán automáticamente
- Puedes configurar despliegues manuales si es necesario

## 📞 SOPORTE

Si tienes problemas:
1. Revisa los logs en Render
2. Verifica la configuración de MongoDB Atlas
3. Confirma que las variables de entorno estén correctas
