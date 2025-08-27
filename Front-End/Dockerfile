# Etapa de construcción
FROM node:18-alpine as build

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar todas las dependencias (incluyendo devDependencies para el build)
RUN npm ci

# Copiar código fuente
COPY . .

# Configurar variable de entorno para Docker (honrar valor provisto por Render)
# Si no se define en el entorno de build, usar el backend de Render por defecto
ARG VITE_API_BASE_URL
ENV VITE_API_BASE_URL=${VITE_API_BASE_URL:-https://pathsys-backend.onrender.com}

# Construir la aplicación (solo vite build, sin type checking)
RUN npx vite build

# Etapa de producción
FROM nginx:alpine

# Copiar archivos construidos
COPY --from=build /app/dist /usr/share/nginx/html

# Copiar configuración de nginx
COPY nginx.conf /etc/nginx/nginx.conf

# Exponer puerto
EXPOSE 5174

# Iniciar nginx
CMD ["nginx", "-g", "daemon off;"]
