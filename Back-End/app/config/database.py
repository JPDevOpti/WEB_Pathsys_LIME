from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from typing import Optional
import logging
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexión a MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None

database_manager = DatabaseManager()

async def connect_to_mongo():
    """Crear conexión a la base de datos"""
    try:
        if database_manager.client is None:
            database_manager.client = AsyncIOMotorClient(settings.MONGODB_URL)
            database_manager.database = database_manager.client[settings.DATABASE_NAME]
            logger.info(f"Conectado a MongoDB: {settings.DATABASE_NAME}")
        return database_manager.database
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {str(e)}")
        raise

async def close_mongo_connection():
    """Cerrar conexión a la base de datos"""
    if database_manager.client:
        database_manager.client.close()
        database_manager.client = None
        database_manager.database = None
        logger.info("Conexión a MongoDB cerrada")

async def get_database() -> AsyncIOMotorDatabase:
    """Obtener instancia de la base de datos"""
    if database_manager.database is None:
        logger.info("Base de datos no inicializada, conectando...")
        await connect_to_mongo()
    
    if database_manager.database is None:
        logger.error("No se pudo establecer conexión con la base de datos")
        raise Exception("No se pudo establecer conexión con la base de datos")
        
    return database_manager.database

# Función síncrona para compatibilidad con scripts
def get_database_sync() -> Optional[AsyncIOMotorDatabase]:
    """Obtener instancia de la base de datos de forma síncrona (para scripts)"""
    return database_manager.database