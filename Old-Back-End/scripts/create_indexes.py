#!/usr/bin/env python3
"""
Script para crear índices optimizados en MongoDB para mejorar el rendimiento del dashboard
"""

import asyncio
import sys
from pathlib import Path

# Asegurar que el módulo 'app' sea importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection

async def create_indexes():
    """Crear índices optimizados para el dashboard"""
    db = await connect_to_mongo()
    
    try:
        print("🚀 Creando índices optimizados para el dashboard...")
        
        # Índices para la colección de casos
        casos_indexes = [
            # Índice compuesto para consultas por patólogo y fecha
            {
                "keys": [("patologo_asignado.codigo", 1), ("fecha_creacion", 1)],
                "name": "patologo_fecha_creacion",
                "background": True
            },
            # Índice para consultas por fecha de creación
            {
                "keys": [("fecha_creacion", 1)],
                "name": "fecha_creacion",
                "background": True
            },
            # Índice para consultas por estado y fecha de entrega
            {
                "keys": [("estado", 1), ("fecha_entrega", 1)],
                "name": "estado_fecha_entrega",
                "background": True
            },
            # Índice para consultas de oportunidad
            {
                "keys": [("fecha_creacion", 1), ("fecha_entrega", 1), ("estado", 1)],
                "name": "oportunidad_stats",
                "background": True
            },
            # Índice para consultas por mes
            {
                "keys": [("fecha_creacion", 1), ("patologo_asignado.codigo", 1)],
                "name": "mes_patologo",
                "background": True
            }
        ]
        
        # Crear índices para casos
        for index_spec in casos_indexes:
            try:
                await db.casos.create_index(
                    index_spec["keys"],
                    name=index_spec["name"],
                    background=index_spec["background"]
                )
                print(f"✅ Índice creado: {index_spec['name']}")
            except Exception as e:
                print(f"⚠️  Error creando índice {index_spec['name']}: {e}")
        
        # Índices para la colección de patólogos
        patologos_indexes = [
            {
                "keys": [("email", 1)],
                "name": "email_unique",
                "unique": True,
                "background": True
            },
            {
                "keys": [("patologo_code", 1)],
                "name": "patologo_code",
                "background": True
            }
        ]
        
        for index_spec in patologos_indexes:
            try:
                await db.patologos.create_index(
                    index_spec["keys"],
                    name=index_spec["name"],
                    unique=index_spec.get("unique", False),
                    background=index_spec["background"]
                )
                print(f"✅ Índice creado: {index_spec['name']}")
            except Exception as e:
                print(f"⚠️  Error creando índice {index_spec['name']}: {e}")
        
        # Índices para la colección de pacientes
        pacientes_indexes = [
            {
                "keys": [("paciente_code", 1)],
                "name": "paciente_code",
                "background": True
            },
            {
                "keys": [("entidad_info.nombre", 1)],
                "name": "entidad_nombre",
                "background": True
            }
        ]
        
        for index_spec in pacientes_indexes:
            try:
                await db.pacientes.create_index(
                    index_spec["keys"],
                    name=index_spec["name"],
                    background=index_spec["background"]
                )
                print(f"✅ Índice creado: {index_spec['name']}")
            except Exception as e:
                print(f"⚠️  Error creando índice {index_spec['name']}: {e}")
        
        print("\n🎉 ¡Índices creados exitosamente!")
        print("📊 El rendimiento del dashboard debería mejorar significativamente")
        
        # Mostrar estadísticas de índices
        print("\n📈 Estadísticas de índices:")
        casos_stats = await db.casos.index_information()
        print(f"   Casos: {len(casos_stats)} índices")
        
        patologos_stats = await db.patologos.index_information()
        print(f"   Patólogos: {len(patologos_stats)} índices")
        
        pacientes_stats = await db.pacientes.index_information()
        print(f"   Pacientes: {len(pacientes_stats)} índices")
        
    except Exception as e:
        print(f"❌ Error creando índices: {e}")
    finally:
        await close_mongo_connection()

if __name__ == "__main__":
    asyncio.run(create_indexes())
