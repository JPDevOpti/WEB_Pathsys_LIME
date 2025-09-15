#!/usr/bin/env python3
"""
Script para optimizar índices del módulo de casos.
Ejecutar después de cambios en el esquema de datos.
"""

import asyncio
import sys
import os
from pathlib import Path

# Agregar el directorio raíz del proyecto al path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from app.config.database import get_database
from app.modules.casos.services.index_optimizer import IndexOptimizer
import logging

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


async def main():
    """Función principal para optimizar índices."""
    try:
        logger.info("Iniciando optimización de índices del módulo de casos...")
        
        # Obtener conexión a la base de datos
        database = await get_database()
        
        # Crear optimizador de índices
        optimizer = IndexOptimizer(database)
        
        # Crear índices optimizados
        logger.info("Creando índices optimizados...")
        results = await optimizer.create_optimized_indexes()
        
        # Mostrar resultados
        logger.info("Resultados de la creación de índices:")
        for index_name, status in results.items():
            logger.info(f"  {index_name}: {status}")
        
        # Obtener estadísticas de índices
        logger.info("Obteniendo estadísticas de índices...")
        stats = await optimizer.get_index_stats()
        
        if "error" not in stats:
            logger.info(f"Total de índices: {stats['total_indexes']}")
            logger.info("Índices creados:")
            for idx in stats["indexes"]:
                logger.info(f"  - {idx['name']}: {idx['size']} bytes")
        else:
            logger.error(f"Error obteniendo estadísticas: {stats['error']}")
        
        # Identificar índices no utilizados
        logger.info("Identificando índices no utilizados...")
        unused = await optimizer.drop_unused_indexes()
        
        if unused:
            logger.info("Índices no utilizados eliminados:")
            for idx_name, status in unused.items():
                logger.info(f"  {idx_name}: {status}")
        else:
            logger.info("No se encontraron índices no utilizados")
        
        logger.info("Optimización de índices completada exitosamente")
        
    except Exception as e:
        logger.error(f"Error durante la optimización: {e}")
        sys.exit(1)
    finally:
        # Cerrar conexión a la base de datos
        if 'database' in locals():
            database.client.close()


if __name__ == "__main__":
    asyncio.run(main())
