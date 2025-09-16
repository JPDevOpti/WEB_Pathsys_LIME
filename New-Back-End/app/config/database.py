from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from typing import Optional
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Gestor de conexión a MongoDB"""
    
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
    """Crear conexión a la base de datos"""
    try:
        if database_manager.client is None:
            database_manager.client = AsyncIOMotorClient(
                settings.MONGODB_URL, 
                **database_manager._connection_options
            )
            database_manager.database = database_manager.client[settings.DATABASE_NAME]
            
            # Verificar conexión
            await database_manager.client.admin.command('ping')
            logger.info(f"Conectado a MongoDB: {settings.DATABASE_NAME}")
            
        return database_manager.database
    except Exception as e:
        logger.error(f"Error al conectar con MongoDB: {str(e)}")
        database_manager.client = None
        database_manager.database = None
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
    
    try:
        await database_manager.client.admin.command('ping')
    except Exception:
        logger.warning("Conexión perdida, reconectando...")
        database_manager.client = None
        database_manager.database = None
        await connect_to_mongo()
        
    return database_manager.database

def get_database_sync() -> Optional[AsyncIOMotorDatabase]:
    """Obtener instancia de la base de datos de forma síncrona (para scripts)"""
    return database_manager.database

async def create_basic_indexes():
    """Crear índices básicos para las colecciones principales"""
    try:
        db = await get_database()
        
        # Índices para usuarios
        await db.usuarios.create_index("email", unique=True)
        await db.usuarios.create_index("username", unique=True)
        
        # Índices para entidades
        await db.entidades.create_index("entidad_code", unique=True)
        
        # Índices para patólogos
        await db.patologos.create_index("patologo_code", unique=True)
        await db.patologos.create_index("patologo_email", unique=True)
        await db.patologos.create_index("registro_medico", unique=True)
        
        # Índices para residentes
        await db.residentes.create_index("residente_code", unique=True)
        await db.residentes.create_index("residente_email", unique=True)
        
        # Índices para auxiliares
        await db.auxiliares.create_index("auxiliar_code", unique=True)
        await db.auxiliares.create_index("auxiliar_email", unique=True)
        
        # Índices para pruebas
        await db.pruebas.create_index("prueba_code", unique=True)
        
        # Índices para casos
        await db.casos.create_index("caso_code", unique=True)
        await db.casos.create_index("paciente.paciente_code")
        await db.casos.create_index("estado")
        await db.casos.create_index("fecha_creacion")
        
        # Índices para pacientes
        await db.pacientes.create_index("paciente_code", unique=True)
        
        logger.info("Índices básicos creados correctamente")
        
    except Exception as e:
        logger.error(f"Error al crear índices: {str(e)}")
        raise