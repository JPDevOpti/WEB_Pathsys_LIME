from typing import Dict, List, Any
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

logger = logging.getLogger(__name__)

# Definición de índices por colección
COLLECTION_INDEXES: Dict[str, List[Dict[str, Any]]] = {
    "usuarios": [
        {"keys": [("email", 1)], "unique": True, "name": "email_unique"},
        {"keys": [("username", 1)], "unique": True, "name": "username_unique"},
        {"keys": [("is_active", 1)], "name": "is_active_idx"},
        {"keys": [("roles", 1)], "name": "roles_idx"}
    ],
    "entidades": [
        {"keys": [("EntidadCode", 1)], "unique": True, "name": "entidad_code_unique"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("EntidadName", "text")], "name": "entidad_name_text"}
    ],
    "patologos": [
        {"keys": [("patologoCode", 1)], "unique": True, "name": "patologo_code_unique"},
        {"keys": [("PatologoEmail", 1)], "unique": True, "name": "patologo_email_unique"},
        {"keys": [("registro_medico", 1)], "unique": True, "name": "registro_medico_unique"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("patologoName", "text")], "name": "patologo_name_text"}
    ],
    "residentes": [
        {"keys": [("residenteCode", 1)], "unique": True, "name": "residente_code_unique"},
        {"keys": [("ResidenteEmail", 1)], "unique": True, "name": "residente_email_unique"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("residenteName", "text")], "name": "residente_name_text"}
    ],
    "auxiliares": [
        {"keys": [("auxiliarCode", 1)], "unique": True, "name": "auxiliar_code_unique"},
        {"keys": [("AuxiliarEmail", 1)], "unique": True, "name": "auxiliar_email_unique"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("auxiliarName", "text")], "name": "auxiliar_name_text"}
    ],
    "pruebas": [
        {"keys": [("pruebaCode", 1)], "unique": True, "name": "prueba_code_unique"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("pruebasName", "text")], "name": "pruebas_name_text"}
    ],
    "casos": [
        {"keys": [("caso_code", 1)], "unique": True, "name": "caso_code_unique"},
        {"keys": [("paciente.cedula", 1)], "name": "paciente_cedula_idx"},
        {"keys": [("estado", 1)], "name": "estado_idx"},
        {"keys": [("fecha_creacion", -1)], "name": "fecha_creacion_idx"},
        {"keys": [("patologo_asignado.codigo", 1)], "name": "patologo_asignado_idx"},
        {"keys": [("fecha_firma", -1)], "name": "fecha_firma_idx"},
        {"keys": [("fecha_entrega", -1)], "name": "fecha_entrega_idx"}
    ],
    "pacientes": [
        {"keys": [("cedula", 1)], "unique": True, "name": "cedula_unique"},
        {"keys": [("nombre", "text")], "name": "nombre_text"},
        {"keys": [("entidad_info.nombre", 1)], "name": "entidad_idx"},
        {"keys": [("fecha_creacion", -1)], "name": "fecha_creacion_idx"}
    ],
    "enfermedades": [
        {"keys": [("codigo", 1)], "unique": True, "name": "codigo_unique"},
        {"keys": [("tabla", 1)], "name": "tabla_idx"},
        {"keys": [("isActive", 1)], "name": "is_active_idx"},
        {"keys": [("nombre", "text")], "name": "nombre_text"}
    ]
}

async def create_collection_indexes(db: AsyncIOMotorDatabase, collection_name: str) -> None:
    """Crear índices para una colección específica"""
    try:
        if collection_name not in COLLECTION_INDEXES:
            logger.warning(f"No hay índices definidos para la colección: {collection_name}")
            return
        
        collection = db[collection_name]
        existing_indexes = await collection.list_indexes()
        existing_index_names = [idx["name"] for idx in existing_indexes]
        
        for index_config in COLLECTION_INDEXES[collection_name]:
            index_name = index_config["name"]
            
            if index_name not in existing_index_names:
                try:
                    await collection.create_index(
                        index_config["keys"],
                        unique=index_config.get("unique", False),
                        name=index_name
                    )
                    logger.info(f"Índice '{index_name}' creado en colección '{collection_name}'")
                except Exception as e:
                    logger.error(f"Error al crear índice '{index_name}' en '{collection_name}': {e}")
            else:
                logger.debug(f"Índice '{index_name}' ya existe en colección '{collection_name}'")
                
    except Exception as e:
        logger.error(f"Error al crear índices para colección '{collection_name}': {e}")

async def create_all_indexes(db: AsyncIOMotorDatabase) -> None:
    """Crear todos los índices definidos"""
    logger.info("Iniciando creación de índices de base de datos...")
    
    for collection_name in COLLECTION_INDEXES.keys():
        await create_collection_indexes(db, collection_name)
    
    logger.info("Creación de índices completada")

async def drop_collection_indexes(db: AsyncIOMotorDatabase, collection_name: str) -> None:
    """Eliminar todos los índices de una colección (excepto _id)"""
    try:
        collection = db[collection_name]
        indexes = await collection.list_indexes()
        
        for index in indexes:
            if index["name"] != "_id_":
                await collection.drop_index(index["name"])
                logger.info(f"Índice '{index['name']}' eliminado de '{collection_name}'")
                
    except Exception as e:
        logger.error(f"Error al eliminar índices de '{collection_name}': {e}")

async def recreate_collection_indexes(db: AsyncIOMotorDatabase, collection_name: str) -> None:
    """Recrear índices de una colección específica"""
    logger.info(f"Recreando índices para colección: {collection_name}")
    await drop_collection_indexes(db, collection_name)
    await create_collection_indexes(db, collection_name)
