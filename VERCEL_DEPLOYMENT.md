# Guía de Despliegue en Vercel

## 🚀 Configuración para Vercel

### 1. Configuración del Proyecto

El proyecto está configurado para desplegarse en Vercel con las siguientes características:

- **Framework**: Vite + Vue 3
- **Directorio de Build**: `Front-End/dist`
- **Comando de Build**: `cd Front-End && npm install && npm run build`
- **Variables de Entorno**: Configuradas en `vercel.json`

### 2. Archivos de Configuración

#### `vercel.json` (Raíz del proyecto)
```json
{
  "buildCommand": "cd Front-End && npm install && npm run build",
  "outputDirectory": "Front-End/dist",
  "installCommand": "cd Front-End && npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ],
  "env": {
    "VITE_API_BASE_URL": "https://web-lis-pathsys-backend.onrender.com",
    "VITE_APP_TITLE": "WEB-LIS PathSys",
    "VITE_APP_ENV": "production",
    "VITE_DEV_MODE": "false"
  }
}
```

#### `Front-End/vercel.json` (Directorio Front-End)
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "installCommand": "npm install",
  "framework": "vite",
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

### 3. Pasos para Desplegar

1. **Conectar Repositorio a Vercel**
   - Ir a [Vercel Dashboard](https://vercel.com/dashboard)
   - Hacer clic en "New Project"
   - Conectar el repositorio `JPDevOpti/WEB_Pathsys_LIME`
   - Seleccionar la rama `production`

2. **Configuración del Proyecto**
   - **Framework Preset**: Vite
   - **Root Directory**: `Front-End` (IMPORTANTE)
   - **Build Command**: `npm run build`
   - **Output Directory**: `dist`
   - **Install Command**: `npm install`

3. **Variables de Entorno**
   ```
   VITE_API_BASE_URL=https://web-lis-pathsys-backend.onrender.com
   VITE_APP_TITLE=WEB-LIS PathSys
   VITE_APP_ENV=production
   VITE_DEV_MODE=false
   ```

4. **Desplegar**
   - Hacer clic en "Deploy"
   - Esperar a que termine el build
   - Verificar que la aplicación funcione correctamente

### 4. Verificación del Despliegue

Una vez desplegado, verificar:

- ✅ La aplicación carga correctamente
- ✅ Las rutas funcionan (SPA routing)
- ✅ La conexión con el backend funciona
- ✅ Las variables de entorno están configuradas

### 5. URLs de Verificación

- **Frontend**: `https://tu-proyecto.vercel.app`
- **Backend**: `https://web-lis-pathsys-backend.onrender.com`
- **API Docs**: `https://web-lis-pathsys-backend.onrender.com/docs`

### 6. Troubleshooting

#### Error: "cd: Front-End: No such file or directory"
- **Solución**: Configurar el Root Directory como `Front-End` en Vercel
- **Alternativa**: Usar el archivo `vercel.json` en la raíz

#### Error: "Module not found"
- **Solución**: Verificar que todas las dependencias estén en `package.json`
- **Verificar**: Que el comando `npm install` se ejecute correctamente

#### Error: "Build failed"
- **Solución**: Revisar los logs de build en Vercel
- **Verificar**: Que el comando `npm run build` funcione localmente

### 7. Configuración Avanzada

#### Custom Domain
- Configurar dominio personalizado en Vercel Dashboard
- Configurar DNS según las instrucciones de Vercel

#### Environment Variables
- Configurar variables específicas por entorno
- Usar Vercel CLI para gestión de variables

#### Performance
- Habilitar Vercel Analytics
- Configurar Edge Functions si es necesario

## 📝 Notas Importantes

1. **Root Directory**: Debe estar configurado como `Front-End`
2. **Build Command**: Debe ejecutarse desde el directorio correcto
3. **Variables de Entorno**: Deben estar configuradas antes del build
4. **CORS**: El backend debe permitir el dominio de Vercel
5. **SPA Routing**: Configurado con rewrites para Vue Router

## 🔧 Comandos Útiles

```bash
# Instalar Vercel CLI
npm i -g vercel

# Login en Vercel
vercel login

# Desplegar desde el directorio Front-End
cd Front-End
vercel

# Ver logs de deployment
vercel logs
```
