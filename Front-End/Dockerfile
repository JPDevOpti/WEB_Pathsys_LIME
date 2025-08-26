# Etapa de construcción
FROM node:18-alpine as build

WORKDIR /app

# Copiar archivos de dependencias
COPY package*.json ./

# Instalar todas las dependencias (incluyendo devDependencies para el build)
RUN npm ci

# Copiar código fuente
COPY . .

# Configurar variable de entorno para Docker
ENV VITE_API_BASE_URL=http://localhost:8000

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
