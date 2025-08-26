# Etapa de construcción
FROM python:3.11-slim as builder

# Instalar dependencias del sistema necesarias para compilación
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    libffi-dev \
    libssl-dev \
    && rm -rf /var/lib/apt/lists/*

# Crear directorio de trabajo
WORKDIR /app

# Copiar archivos de dependencias
COPY requirements.txt .

# Instalar dependencias de Python en un directorio separado
RUN pip install --no-cache-dir --user -r requirements.txt

# Etapa de producción
FROM python:3.11-slim

# Instalar dependencias del sistema mínimas para runtime
# Usar nombres de paquetes genéricos para mayor compatibilidad
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/* \
    && apt-get clean

# Crear usuario no-root para seguridad
RUN useradd --create-home --shell /bin/bash --uid 1000 app

# Establecer directorio de trabajo
WORKDIR /app

# Copiar dependencias instaladas desde la etapa de construcción
COPY --from=builder /root/.local /home/app/.local

# Copiar código de la aplicación
COPY --chown=app:app . .

# Crear directorios necesarios y establecer permisos
RUN mkdir -p uploads logs \
    && chown -R app:app /app \
    && chmod +x /app/scripts/*.py 2>/dev/null || true

# Cambiar al usuario no-root
USER app

# Exponer puerto
EXPOSE 8000

# Variables de entorno
ENV PYTHONPATH=/app
ENV PYTHONUNBUFFERED=1
ENV PATH=/home/app/.local/bin:$PATH

# Health check para verificar que la aplicación esté funcionando
HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/health || exit 1

# Comando para ejecutar la aplicación en producción
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]