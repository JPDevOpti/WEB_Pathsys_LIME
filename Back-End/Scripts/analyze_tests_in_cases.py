#!/usr/bin/env python3
"""
Script para analizar los tipos de pruebas almacenadas en los casos de la base de datos.
Evalúa cuántos tipos diferentes de pruebas hay y su distribución.
"""

import sys
import asyncio
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Any, Set
from collections import Counter

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import get_database, close_mongo_connection


async def analyze_tests_in_cases():
    """Analiza los tipos de pruebas almacenadas en los casos"""
    
    print("🔍 Analizando tipos de pruebas en los casos de la base de datos...")
    print("=" * 60)
    
    try:
        # Conectar a la base de datos
        database = await get_database()
        cases_collection = database.cases
        tests_collection = database.tests
        
        # 1. Contar casos totales
        total_cases = await cases_collection.count_documents({})
        print(f"📊 Total de casos en la base de datos: {total_cases:,}")
        
        # 2. Analizar estructura de casos
        print("\n🔍 Analizando estructura de casos...")
        
        # Casos con formato nuevo (samples)
        cases_with_samples = await cases_collection.count_documents({
            "samples": {"$exists": True, "$ne": []}
        })
        
        # Casos con formato legacy (muestras)
        cases_with_muestras = await cases_collection.count_documents({
            "muestras": {"$exists": True, "$ne": []}
        })
        
        print(f"   📋 Casos con formato nuevo (samples): {cases_with_samples:,}")
        print(f"   📋 Casos con formato legacy (muestras): {cases_with_muestras:,}")
        
        # 3. Extraer todas las pruebas de los casos
        print("\n🧪 Extrayendo pruebas de los casos...")
        
        # Pipeline para extraer pruebas del formato nuevo
        new_format_pipeline = [
            {"$match": {"samples": {"$exists": True, "$ne": []}}},
            {"$unwind": "$samples"},
            {"$unwind": "$samples.tests"},
            {
                "$project": {
                    "_id": 0,
                    "test_id": "$samples.tests.id",
                    "test_name": "$samples.tests.name",
                    "quantity": "$samples.tests.quantity",
                    "case_code": "$case_code",
                    "created_at": "$created_at",
                    "format": "new"
                }
            }
        ]
        
        # Pipeline para extraer pruebas del formato legacy
        legacy_format_pipeline = [
            {"$match": {"muestras": {"$exists": True, "$ne": []}}},
            {"$unwind": "$muestras"},
            {"$unwind": "$muestras.pruebas"},
            {
                "$project": {
                    "_id": 0,
                    "test_id": "$muestras.pruebas.id",
                    "test_name": "$muestras.pruebas.nombre",
                    "quantity": "$muestras.pruebas.cantidad",
                    "case_code": "$caso_code",
                    "created_at": "$fecha_creacion",
                    "format": "legacy"
                }
            }
        ]
        
        # Ejecutar ambos pipelines
        new_format_tests = await cases_collection.aggregate(new_format_pipeline).to_list(length=None)
        legacy_format_tests = await cases_collection.aggregate(legacy_format_pipeline).to_list(length=None)
        
        all_tests = new_format_tests + legacy_format_tests
        
        print(f"   🧪 Total de pruebas extraídas: {len(all_tests):,}")
        print(f"   📋 Formato nuevo: {len(new_format_tests):,}")
        print(f"   📋 Formato legacy: {len(legacy_format_tests):,}")
        
        # 4. Analizar tipos únicos de pruebas
        print("\n🔬 Analizando tipos únicos de pruebas...")
        
        # Contar por ID de prueba
        test_ids = [test["test_id"] for test in all_tests if test["test_id"]]
        unique_test_ids = set(test_ids)
        
        # Contar por nombre de prueba
        test_names = [test["test_name"] for test in all_tests if test["test_name"]]
        unique_test_names = set(test_names)
        
        print(f"   🆔 IDs únicos de pruebas: {len(unique_test_ids)}")
        print(f"   📝 Nombres únicos de pruebas: {len(unique_test_names)}")
        
        # 5. Top 10 pruebas más utilizadas
        print("\n🏆 Top 10 pruebas más utilizadas:")
        test_id_counter = Counter(test_ids)
        for i, (test_id, count) in enumerate(test_id_counter.most_common(10), 1):
            # Buscar el nombre de la prueba
            test_name = next((test["test_name"] for test in all_tests if test["test_id"] == test_id), "Sin nombre")
            print(f"   {i:2d}. {test_id} - {test_name} ({count:,} veces)")
        
        # 6. Análisis por año
        print("\n📅 Análisis por año:")
        years_counter = Counter()
        for test in all_tests:
            if test.get("created_at"):
                year = test["created_at"].year
                years_counter[year] += 1
        
        for year in sorted(years_counter.keys()):
            print(f"   {year}: {years_counter[year]:,} pruebas")
        
        # 7. Verificar coincidencias con la colección tests
        print("\n🔗 Verificando coincidencias con la colección 'tests':")
        
        # Obtener todos los test_codes de la colección tests
        tests_in_catalog = await tests_collection.find({}, {"test_code": 1, "name": 1, "is_active": 1}).to_list(length=None)
        catalog_test_codes = {test["test_code"] for test in tests_in_catalog}
        
        # Encontrar pruebas que están en casos pero no en el catálogo
        missing_in_catalog = unique_test_ids - catalog_test_codes
        
        # Encontrar pruebas que están en el catálogo pero no en casos
        unused_in_catalog = catalog_test_codes - unique_test_ids
        
        print(f"   📚 Pruebas en catálogo: {len(catalog_test_codes)}")
        print(f"   🚫 Pruebas en casos pero no en catálogo: {len(missing_in_catalog)}")
        print(f"   📦 Pruebas en catálogo pero no usadas: {len(unused_in_catalog)}")
        
        if missing_in_catalog:
            print("\n   ⚠️  Pruebas en casos pero no en catálogo:")
            for test_id in list(missing_in_catalog)[:10]:  # Mostrar solo las primeras 10
                test_name = next((test["test_name"] for test in all_tests if test["test_id"] == test_id), "Sin nombre")
                print(f"      - {test_id}: {test_name}")
        
        if unused_in_catalog:
            print(f"\n   📦 Pruebas en catálogo pero no usadas: {len(unused_in_catalog)}")
            unused_tests = [test for test in tests_in_catalog if test["test_code"] in unused_in_catalog]
            for test in unused_tests[:10]:  # Mostrar solo las primeras 10
                status = "✅ Activa" if test.get("is_active", True) else "❌ Inactiva"
                print(f"      - {test['test_code']}: {test['name']} ({status})")
        
        # 8. Análisis de formatos
        print("\n📊 Análisis de formatos:")
        format_counter = Counter(test["format"] for test in all_tests)
        for format_type, count in format_counter.items():
            print(f"   {format_type}: {count:,} pruebas")
        
        # 9. Resumen final
        print("\n" + "=" * 60)
        print("📋 RESUMEN FINAL:")
        print(f"   📊 Total de casos: {total_cases:,}")
        print(f"   🧪 Total de pruebas en casos: {len(all_tests):,}")
        print(f"   🆔 Tipos únicos de pruebas: {len(unique_test_ids)}")
        print(f"   📚 Pruebas en catálogo: {len(catalog_test_codes)}")
        print(f"   🔗 Coincidencias: {len(unique_test_ids & catalog_test_codes)}")
        print(f"   ⚠️  Desincronizaciones: {len(missing_in_catalog) + len(unused_in_catalog)}")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()


async def main():
    """Función principal"""
    print("🚀 Iniciando análisis de pruebas en casos...")
    await analyze_tests_in_cases()
    print("\n✅ Análisis completado!")


if __name__ == "__main__":
    asyncio.run(main())



