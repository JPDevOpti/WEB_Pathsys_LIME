from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        self._connection_options = {
            "serverSelectionTimeoutMS": 5000,
            "connectTimeoutMS": 10000,
            "socketTimeoutMS": 20000,
            "maxPoolSize": 10,
            "minPoolSize": 1,
            "maxIdleTimeMS": 30000,
            "retryWrites": True,
            "retryReads": True
        }

database_manager = DatabaseManager()

async def connect_to_mongo():
    try:
        if database_manager.client is None:
            database_manager.client = AsyncIOMotorClient(
                settings.MONGODB_URL, 
                **database_manager._connection_options
            )
            database_manager.database = database_manager.client[settings.DATABASE_NAME]
            
            await database_manager.client.admin.command('ping')
            logger.info(f"Conectado a MongoDB: {settings.DATABASE_NAME}")
            
        return database_manager.database
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {str(e)}")
        database_manager.client = None
        database_manager.database = None
        raise

async def close_mongo_connection():
    if database_manager.client:
        database_manager.client.close()
        database_manager.client = None
        database_manager.database = None
        logger.info("Conexión a MongoDB cerrada")

async def get_database() -> AsyncIOMotorDatabase:
    if database_manager.database is None:
        await connect_to_mongo()
    
    if database_manager.database is None:
        raise Exception("No se pudo establecer conexión con la base de datos")
    
    try:
        await database_manager.client.admin.command('ping')
    except Exception:
        database_manager.client = None
        database_manager.database = None
        await connect_to_mongo()
        
    return database_manager.database

def get_database_sync() -> Optional[AsyncIOMotorDatabase]:
    return database_manager.database