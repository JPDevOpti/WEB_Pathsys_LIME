from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.middleware import setup_middleware
from app.api.v1.router import api_router
from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.config.database_indexes import create_all_indexes
from contextlib import asynccontextmanager
import logging
from app.config.logging_config import setup_logging

# Configurar logging estructurado
setup_logging()
logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Iniciando aplicación...")
    try:
        await connect_to_mongo()
        logger.info("Conexión a MongoDB establecida exitosamente")
        # Crear índices en startup si está habilitado
        try:
            if settings.CREATE_INDEXES_ON_STARTUP:
                db = await get_database()
                await create_all_indexes(db)
                logger.info("Índices de base de datos verificados/creados")
        except Exception as idx_err:
            logger.error(f"Error creando índices en startup: {idx_err}")
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {e}")
        raise
    
    yield
    
    # Shutdown
    logger.info("Cerrando aplicación...")
    await close_mongo_connection()

def create_application() -> FastAPI:
    """Crear y configurar la aplicación FastAPI"""
    app = FastAPI(
        title="WEB-LIS PathSys API",
        description="Sistema de Información de Laboratorio - Patología",
        version="2.0.0",
        docs_url="/docs",
        redoc_url="/redoc",
        lifespan=lifespan
    )
    
    # Configurar CORS
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.BACKEND_CORS_ORIGINS,
        allow_credentials=True,
        allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS", "PATCH", "HEAD"],
        allow_headers=["*"],
        expose_headers=["*"],
        max_age=600,
    )
    
    # Configurar middlewares personalizados
    setup_middleware(app)
    
    # Incluir routers
    app.include_router(api_router, prefix="/api/v1")
    
    @app.get("/")
    async def root():
        return {"message": "WEB-LIS PathSys API v2.0.0"}
    
    @app.get("/health")
    async def health_check():
        return {"status": "healthy"}
    
    return app

app = create_application()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True
    )