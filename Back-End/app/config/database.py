from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from app.config.settings import settings
from typing import Optional
import logging
import certifi
import os
import ssl

logger = logging.getLogger(__name__)

class DatabaseManager:
    """Database connection manager for MongoDB"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        
        # SSL configuration specific for different environments
        ssl_options = self._get_ssl_options()
        
        self._connection_options = {
            "serverSelectionTimeoutMS": 30000,  # Increased timeout for Render
            "connectTimeoutMS": 30000,          # Increased timeout for Render
            "socketTimeoutMS": 30000,           # Increased timeout for Render
            "maxPoolSize": 5,                   # Reduced pool size for Render
            "minPoolSize": 1,
            "maxIdleTimeMS": 60000,
            "retryWrites": True,
            "retryReads": True,
            "heartbeatFrequencyMS": 30000,      # Added for better connection monitoring
            **ssl_options
        }
    
    def _get_ssl_options(self):
        """Get SSL options based on environment"""
        env = os.getenv("ENVIRONMENT", "development")
        
        if env == "production":
            # Specific configuration for Render and production environments
            ssl_context = ssl.create_default_context()
            ssl_context.check_hostname = False
            ssl_context.verify_mode = ssl.CERT_NONE
            
            return {
                "tls": True,
                "tlsAllowInvalidCertificates": True,
                "tlsAllowInvalidHostnames": True,
                "ssl_context": ssl_context
            }
        else:
            # For local development
            return {
                "tls": True,
                "tlsCAFile": certifi.where()
            }

database_manager = DatabaseManager()

async def connect_to_mongo():
    """Create connection to database with enhanced error handling for Render"""
    try:
        if database_manager.client is None:
            mongodb_url = _get_mongodb_url()
            env = os.getenv("ENVIRONMENT", "development")
            
            if env == "production":
                # For Render deployment - try multiple connection strategies
                connection_strategies = [
                    # Strategy 1: Full SSL configuration
                    {
                        **database_manager._connection_options,
                        "serverSelectionTimeoutMS": 60000,
                        "connectTimeoutMS": 60000,
                        "socketTimeoutMS": 60000,
                    },
                    # Strategy 2: Minimal SSL configuration
                    {
                        "serverSelectionTimeoutMS": 60000,
                        "connectTimeoutMS": 60000,
                        "socketTimeoutMS": 60000,
                        "maxPoolSize": 3,
                        "minPoolSize": 1,
                        "retryWrites": True,
                        "retryReads": True,
                        "tls": True,
                        "tlsAllowInvalidCertificates": True,
                        "tlsAllowInvalidHostnames": True,
                    },
                    # Strategy 3: Basic configuration
                    {
                        "serverSelectionTimeoutMS": 60000,
                        "connectTimeoutMS": 60000,
                        "socketTimeoutMS": 60000,
                        "maxPoolSize": 1,
                        "retryWrites": True,
                        "tls": True,
                    }
                ]
                
                last_error = None
                for i, strategy in enumerate(connection_strategies, 1):
                    try:
                        logger.info(f"Attempting connection strategy {i} for Render deployment...")
                        database_manager.client = AsyncIOMotorClient(mongodb_url, **strategy)
                        database_manager.database = database_manager.client[settings.DATABASE_NAME]
                        
                        # Test connection with longer timeout
                        await database_manager.client.admin.command('ping')
                        logger.info(f"Successfully connected to MongoDB using strategy {i}: {settings.DATABASE_NAME}")
                        break
                        
                    except Exception as strategy_error:
                        logger.warning(f"Strategy {i} failed: {str(strategy_error)}")
                        last_error = strategy_error
                        if database_manager.client:
                            database_manager.client.close()
                            database_manager.client = None
                            database_manager.database = None
                        continue
                
                if database_manager.client is None:
                    raise last_error or Exception("All connection strategies failed")
                    
            else:
                # For development environment
                database_manager.client = AsyncIOMotorClient(
                    mongodb_url, 
                    **database_manager._connection_options
                )
                database_manager.database = database_manager.client[settings.DATABASE_NAME]
                
                # Test connection
                await database_manager.client.admin.command('ping')
                logger.info(f"Connected to MongoDB: {settings.DATABASE_NAME}")
            
        return database_manager.database
    except Exception as e:
        logger.error(f"Error connecting to MongoDB: {str(e)}")
        database_manager.client = None
        database_manager.database = None
        raise

def _get_mongodb_url():
    """Get MongoDB URL based on environment with proper SSL parameters"""
    env = os.getenv("ENVIRONMENT", "development")
    base_url = settings.MONGODB_URL
    
    if env == "production":
        # For production (Render), ensure SSL parameters are present
        required_params = [
            "retryWrites=true",
            "w=majority",
            "tlsAllowInvalidCertificates=true",
            "tlsAllowInvalidHostnames=true",
            "ssl=true",
            "authSource=admin"
        ]
        
        # Check if URL already has parameters
        if "?" in base_url:
            # Add missing parameters
            existing_params = base_url.split("?")[1] if "?" in base_url else ""
            for param in required_params:
                param_name = param.split("=")[0]
                if param_name not in existing_params:
                    base_url += f"&{param}"
        else:
            # Add all parameters
            base_url += "?" + "&".join(required_params)
    
    return base_url

async def close_mongo_connection():
    """Close database connection safely"""
    try:
        if database_manager.client:
            database_manager.client.close()
            logger.info("MongoDB connection closed successfully")
    except Exception as e:
        logger.warning(f"Error closing MongoDB connection: {str(e)}")
    finally:
        database_manager.client = None
        database_manager.database = None

async def get_database() -> AsyncIOMotorDatabase:
    """Get database instance with enhanced reconnection logic"""
    max_retries = 3
    retry_count = 0
    
    while retry_count < max_retries:
        try:
            if database_manager.database is None:
                logger.info("Database not initialized, connecting...")
                await connect_to_mongo()
            
            if database_manager.database is None:
                raise Exception("Could not establish database connection")
            
            # Test connection with timeout
            await database_manager.client.admin.command('ping')
            return database_manager.database
            
        except Exception as e:
            retry_count += 1
            logger.warning(f"Connection attempt {retry_count} failed: {str(e)}")
            
            # Clean up failed connection
            if database_manager.client:
                database_manager.client.close()
            database_manager.client = None
            database_manager.database = None
            
            if retry_count >= max_retries:
                logger.error(f"Failed to connect to database after {max_retries} attempts")
                raise Exception(f"Could not establish database connection after {max_retries} attempts: {str(e)}")
            
            # Wait before retry (exponential backoff)
            import asyncio
            wait_time = 2 ** retry_count
            logger.info(f"Waiting {wait_time} seconds before retry...")
            await asyncio.sleep(wait_time)
    
    raise Exception("Unexpected error in database connection")

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
        
        # Índices para pruebas (nuevo backend en inglés)
        await db.tests.create_index("test_code", unique=True)
        
        # Índices para casos (nuevo backend en inglés)
        await db.cases.create_index("case_code", unique=True)
        await db.cases.create_index("patient_info.patient_code")
        await db.cases.create_index("patient_info.identification_number")
        await db.cases.create_index("patient_info.identification_type")
        await db.cases.create_index("state")
        await db.cases.create_index("created_at")
        # Índice de counters de casos
        await db.case_counters.create_index("year", unique=True)
        
        # Índices para pacientes (nuevo backend en inglés)
        await db.patients.create_index("patient_code", unique=True)
        
        # Índices para pathologists (nuevo backend en inglés)
        await db.pathologists.create_index("pathologist_code", unique=True)
        await db.pathologists.create_index("pathologist_email", unique=True)
        await db.pathologists.create_index("medical_license", unique=True)
        await db.pathologists.create_index("is_active")
        
        logger.info("Índices básicos creados correctamente")
        
    except Exception as e:
        logger.error(f"Error al crear índices: {str(e)}")
        raise