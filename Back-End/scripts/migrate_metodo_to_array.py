#!/usr/bin/env python3
"""
Script de migración para convertir el campo 'metodo' de string a array en los casos existentes.
Este script convierte el campo 'resultado.metodo' de string a array de strings.
"""

import asyncio
import os
import sys
from pathlib import Path

# Agregar el directorio raíz al path
sys.path.append(str(Path(__file__).parent.parent))

from motor.motor_asyncio import AsyncIOMotorClient
from app.config.settings import get_settings


async def migrate_metodo_field():
    """Migrar campo metodo de string a array en todos los casos."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.database_url)
    db = client[settings.database_name]
    collection = db.casos
    
    print("🔄 Iniciando migración del campo 'metodo' de string a array...")
    
    # Buscar todos los casos que tienen resultado.metodo como string
    filter_query = {
        "resultado.metodo": {"$type": "string", "$ne": None}
    }
    
    casos_to_update = await collection.find(filter_query).to_list(None)
    total_casos = len(casos_to_update)
    
    if total_casos == 0:
        print("✅ No se encontraron casos con campo 'metodo' tipo string para migrar.")
        return
    
    print(f"📊 Se encontraron {total_casos} casos para migrar...")
    
    updated_count = 0
    error_count = 0
    
    for caso in casos_to_update:
        try:
            metodo_actual = caso.get("resultado", {}).get("metodo")
            
            if isinstance(metodo_actual, str) and metodo_actual.strip():
                # Convertir string a array
                metodo_array = [metodo_actual.strip()]
                
                # Actualizar el documento
                update_result = await collection.update_one(
                    {"_id": caso["_id"]},
                    {"$set": {"resultado.metodo": metodo_array}}
                )
                
                if update_result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Migrado caso {caso.get('caso_code', 'N/A')}: '{metodo_actual}' -> {metodo_array}")
                else:
                    print(f"⚠️  No se pudo actualizar caso {caso.get('caso_code', 'N/A')}")
                    error_count += 1
            else:
                # Campo vacío o None, convertir a array vacío
                update_result = await collection.update_one(
                    {"_id": caso["_id"]},
                    {"$set": {"resultado.metodo": []}}
                )
                
                if update_result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Migrado caso {caso.get('caso_code', 'N/A')}: campo vacío -> []")
                else:
                    print(f"⚠️  No se pudo actualizar caso {caso.get('caso_code', 'N/A')}")
                    error_count += 1
                    
        except Exception as e:
            error_count += 1
            print(f"❌ Error migrando caso {caso.get('caso_code', 'N/A')}: {str(e)}")
    
    print(f"\n🎯 Migración completada:")
    print(f"   ✅ Casos migrados exitosamente: {updated_count}")
    print(f"   ❌ Casos con errores: {error_count}")
    print(f"   📊 Total procesados: {total_casos}")
    
    # Verificar la migración
    print("\n🔍 Verificando migración...")
    casos_string = await collection.count_documents({"resultado.metodo": {"$type": "string"}})
    casos_array = await collection.count_documents({"resultado.metodo": {"$type": "array"}})
    
    print(f"   📝 Casos con metodo tipo string: {casos_string}")
    print(f"   📋 Casos con metodo tipo array: {casos_array}")
    
    if casos_string == 0:
        print("✅ ¡Migración completada exitosamente! Todos los casos tienen 'metodo' como array.")
    else:
        print("⚠️  Aún quedan casos con 'metodo' tipo string. Revisa los errores.")
    
    await client.close()


async def rollback_metodo_field():
    """Rollback: convertir campo metodo de array a string."""
    settings = get_settings()
    client = AsyncIOMotorClient(settings.database_url)
    db = client[settings.database_name]
    collection = db.casos
    
    print("🔄 Iniciando rollback del campo 'metodo' de array a string...")
    
    # Buscar todos los casos que tienen resultado.metodo como array
    filter_query = {
        "resultado.metodo": {"$type": "array"}
    }
    
    casos_to_rollback = await collection.find(filter_query).to_list(None)
    total_casos = len(casos_to_rollback)
    
    if total_casos == 0:
        print("✅ No se encontraron casos con campo 'metodo' tipo array para rollback.")
        return
    
    print(f"📊 Se encontraron {total_casos} casos para rollback...")
    
    updated_count = 0
    error_count = 0
    
    for caso in casos_to_rollback:
        try:
            metodo_array = caso.get("resultado", {}).get("metodo", [])
            
            if isinstance(metodo_array, list):
                if metodo_array and len(metodo_array) > 0:
                    # Convertir array a string (tomar el primer elemento)
                    metodo_string = metodo_array[0] if metodo_array[0] else ""
                else:
                    # Array vacío, convertir a string vacío
                    metodo_string = ""
                
                # Actualizar el documento
                update_result = await collection.update_one(
                    {"_id": caso["_id"]},
                    {"$set": {"resultado.metodo": metodo_string}}
                )
                
                if update_result.modified_count > 0:
                    updated_count += 1
                    print(f"✅ Rollback caso {caso.get('caso_code', 'N/A')}: {metodo_array} -> '{metodo_string}'")
                else:
                    print(f"⚠️  No se pudo hacer rollback caso {caso.get('caso_code', 'N/A')}")
                    error_count += 1
                    
        except Exception as e:
            error_count += 1
            print(f"❌ Error en rollback caso {caso.get('caso_code', 'N/A')}: {str(e)}")
    
    print(f"\n🎯 Rollback completado:")
    print(f"   ✅ Casos con rollback exitoso: {updated_count}")
    print(f"   ❌ Casos con errores: {error_count}")
    print(f"   📊 Total procesados: {total_casos}")
    
    await client.close()


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Migrar campo metodo de string a array")
    parser.add_argument("--rollback", action="store_true", help="Hacer rollback de la migración")
    args = parser.parse_args()
    
    if args.rollback:
        asyncio.run(rollback_metodo_field())
    else:
        asyncio.run(migrate_metodo_field())
