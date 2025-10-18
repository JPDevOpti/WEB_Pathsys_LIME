# Guía de Despliegue en Render

## Configuración para Producción

### Frontend (Static Site)

1. **Crear un nuevo servicio Static Site en Render**
2. **Configuración:**
   - **Name:** `pathsys-frontend`
   - **Repository:** `https://github.com/JPDevOpti/WEB_Pathsys_LIME`
   - **Branch:** `production`
   - **Root Directory:** `Front-End` ⭐ **IMPORTANTE: Esto hace que Render ejecute comandos desde la carpeta Front-End**
   - **Build Command:** `npm install && npm run build`
   - **Publish Directory:** `dist`
   - **Environment Variables:**
     ```
     VITE_API_BASE_URL=https://web-lis-pathsys-backend.onrender.com
     VITE_APP_TITLE=WEB-LIS PathSys
     VITE_APP_ENV=production
     VITE_DEV_MODE=false
     ```

### Backend (Web Service)

1. **Crear un nuevo servicio Web Service en Render**
2. **Configuración:**
   - **Environment:** Python
   - **Build Command:** `cd Back-End && pip install -r requirements.txt`
   - **Start Command:** `cd Back-End && uvicorn app.main:app --host 0.0.0.0 --port $PORT`
   - **Environment Variables:**
     ```
     MONGODB_URL=mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/
     DATABASE_NAME=lime_pathsys
     ENVIRONMENT=production
     DEBUG=False
     SECRET_KEY=your-production-secret-key-change-this-in-production
     ACCESS_TOKEN_EXPIRE_MINUTES=240
     FRONTEND_URL=https://web-lis-pathsys-frontend.onrender.com
     ```

## Pasos para Desplegar

### 1. Preparar el Repositorio

```bash
# Asegurarse de estar en la rama main
git checkout main

# Hacer commit de los cambios de configuración
git add .
git commit -m "feat: configuración para despliegue en Render"
git push origin main
```

### 2. Desplegar Backend

1. Ir a [Render Dashboard](https://dashboard.render.com)
2. Crear nuevo **Web Service**
3. Conectar repositorio de GitHub
4. Usar configuración del archivo `Back-End/render.yaml`
5. Desplegar

### 3. Desplegar Frontend

1. Crear nuevo **Static Site**
2. Conectar el mismo repositorio
3. Usar configuración del archivo `Front-End/render.yaml`
4. Desplegar

### 4. Verificar Despliegue

- Backend: `https://web-lis-pathsys-backend.onrender.com/docs`
- Frontend: `https://web-lis-pathsys-frontend.onrender.com`

## Variables de Entorno Importantes

### Backend
- `SECRET_KEY`: Cambiar por una clave segura en producción
- `MONGODB_URL`: URL de conexión a MongoDB Atlas
- `FRONTEND_URL`: URL del frontend para CORS

### Frontend
- `VITE_API_BASE_URL`: URL del backend en producción

## Notas Importantes

1. **CORS**: El backend está configurado para permitir el frontend de Render
2. **Base de Datos**: Usa MongoDB Atlas en producción
3. **Archivos Estáticos**: Las firmas se sirven desde `/uploads`
4. **Logs**: Revisar logs en Render Dashboard para debugging

## Troubleshooting

### Error de CORS
- Verificar que `FRONTEND_URL` esté configurado correctamente
- Revisar que las URLs coincidan exactamente

### Error de Base de Datos
- Verificar conexión a MongoDB Atlas
- Revisar credenciales y permisos

### Error de Build
- Verificar que todas las dependencias estén en `requirements.txt`
- Revisar logs de build en Render

