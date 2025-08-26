"""Configuración de la base de datos MongoDB"""

import os
from motor.motor_asyncio import AsyncIOMotorClient, AsyncIOMotorDatabase
from typing import Optional


class DatabaseManager:
    """Gestor de conexión a la base de datos"""
    
    def __init__(self):
        self.client: Optional[AsyncIOMotorClient] = None
        self.database: Optional[AsyncIOMotorDatabase] = None
        
    async def connect_to_database(self):
        """Conectar a MongoDB"""
        # Obtener configuración desde variables de entorno
        mongodb_url = os.getenv("MONGODB_URL", "mongodb://localhost:27017")
        database_name = os.getenv("DATABASE_NAME", "pathsys_db")
        
        # Crear cliente de MongoDB
        self.client = AsyncIOMotorClient(mongodb_url)
        self.database = self.client[database_name]
        
        # Verificar conexión
        try:
            await self.client.admin.command('ping')
            print(f"✅ Conectado a MongoDB: {database_name}")
        except Exception as e:
            print(f"❌ Error conectando a MongoDB: {e}")
            raise
    
    async def close_database_connection(self):
        """Cerrar conexión a la base de datos"""
        if self.client is not None:
            self.client.close()
            print("🔌 Conexión a MongoDB cerrada")
    
    def get_database(self) -> AsyncIOMotorDatabase:
        """Obtener instancia de la base de datos"""
        if self.database is None:
            raise RuntimeError("Base de datos no inicializada")
        return self.database


# Instancia global del gestor de base de datos
database_manager = DatabaseManager()


# Dependency para FastAPI
async def get_database() -> AsyncIOMotorDatabase:
    """Dependency para obtener la base de datos en los endpoints"""
    return database_manager.get_database()


# Funciones para el ciclo de vida de la aplicación
async def startup_database():
    """Inicializar conexión a la base de datos al iniciar la aplicación"""
    await database_manager.connect_to_database()


async def shutdown_database():
    """Cerrar conexión a la base de datos al cerrar la aplicación"""
    await database_manager.close_database_connection()