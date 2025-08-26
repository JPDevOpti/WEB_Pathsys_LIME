# 🗄️ CONFIGURACIÓN MONGODB ATLAS PARA RENDER

## 📋 CONFIGURACIÓN ACTUAL

Tu cluster MongoDB Atlas ya está configurado:
- **URL**: `mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/`
- **Base de datos**: `lime_pathsys`

## 🔧 PASOS PARA RENDER

### **PASO 1: Configurar Network Access**

1. Ve a [MongoDB Atlas](https://cloud.mongodb.com)
2. Selecciona tu cluster
3. Ve a "Network Access" → "IP Addresses"
4. Haz clic en "Add IP Address"
5. **IMPORTANTE**: Agrega `0.0.0.0/0` para permitir acceso desde cualquier IP
   - Esto es necesario para Render.com
   - ⚠️ **Nota de seguridad**: En producción, considera restringir a IPs específicas

### **PASO 2: Verificar Usuario de Base de Datos**

1. Ve a "Database Access" → "Users"
2. Verifica que el usuario `practicantedoslime` tenga permisos:
   - **Built-in Role**: `Read and write to any database`
   - **Database**: `lime_pathsys`

### **PASO 3: Verificar Conexión**

```bash
# Test de conexión desde tu máquina local
mongosh "mongodb+srv://practicantedoslime:xC4Nmj3LDU3t89HJ@cluster0.dujsqez.mongodb.net/lime_pathsys"
```

## 🚨 CONSIDERACIONES DE SEGURIDAD

### **Para Desarrollo:**
- `0.0.0.0/0` está bien para pruebas

### **Para Producción:**
- Considera restringir a IPs específicas de Render
- Usa variables de entorno para credenciales
- Rota las credenciales regularmente

## 🔍 VERIFICACIÓN EN RENDER

### **Backend Logs:**
```bash
# En Render, ve a tu servicio backend
# Revisa los logs para ver si se conecta a MongoDB
```

### **Health Check:**
```bash
curl https://pathsys-backend.onrender.com/health
# Debe responder: {"status": "healthy"}
```

## 📊 MONITOREO

### **MongoDB Atlas:**
- Ve a "Metrics" para ver el uso
- Revisa "Logs" para conexiones
- Monitorea el uso de almacenamiento

### **Render:**
- Revisa logs del backend
- Monitorea el uso de recursos
- Verifica el estado del servicio

## 🆘 SOLUCIÓN DE PROBLEMAS

### **Error de Conexión:**
1. Verifica que la IP `0.0.0.0/0` esté en la whitelist
2. Confirma que las credenciales sean correctas
3. Verifica que el usuario tenga permisos

### **Error de Autenticación:**
1. Confirma el nombre de usuario y contraseña
2. Verifica que el usuario esté activo
3. Confirma que tenga acceso a la base de datos

### **Error de Timeout:**
1. Verifica la conectividad de red
2. Confirma que el cluster esté activo
3. Revisa si hay restricciones de firewall
