import sys
import asyncio
from pathlib import Path
from collections import defaultdict
from datetime import datetime

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import get_database, close_mongo_connection
from app.modules.entities.services.entity_service import EntityService
from app.modules.entities.schemas.entity import EntitySearch

async def analyze_entity_distribution():
    """Analiza la distribución de casos por entidades"""
    
    print("="*80)
    print("ANÁLISIS DE DISTRIBUCIÓN DE CASOS POR ENTIDADES")
    print("="*80)
    
    db = await get_database()
    
    try:
        # 1. Obtener todas las entidades disponibles
        entity_service = EntityService(db)
        search_params = EntitySearch(skip=0, limit=100)
        entities = await entity_service.list_all(search_params)
        
        print(f"\n📋 ENTIDADES REGISTRADAS EN EL SISTEMA:")
        print(f"Total de entidades: {len(entities)}")
        
        entity_info = {}
        for entity in entities:
            entity_dict = entity.model_dump() if hasattr(entity, "model_dump") else entity
            entity_code = entity_dict.get("entity_code") or entity_dict.get("code")
            entity_name = entity_dict.get("name")
            entity_info[entity_code] = {
                "name": entity_name,
                "code": entity_code,
                "is_active": entity_dict.get("is_active", True)
            }
        
        # 2. Analizar casos por entidad
        print(f"\n🔍 ANALIZANDO CASOS POR ENTIDAD...")
        
        # Pipeline para obtener estadísticas por entidad
        pipeline = [
            {
                "$group": {
                    "_id": "$patient_info.entity_info.id",
                    "entity_name": {"$first": "$patient_info.entity_info.name"},
                    "total_casos": {"$sum": 1},
                    "casos_completados": {
                        "$sum": {"$cond": [{"$eq": ["$state", "Completado"]}, 1, 0]}
                    },
                    "casos_en_proceso": {
                        "$sum": {"$cond": [{"$eq": ["$state", "En proceso"]}, 1, 0]}
                    },
                    "casos_por_firmar": {
                        "$sum": {"$cond": [{"$eq": ["$state", "Por firmar"]}, 1, 0]}
                    },
                    "casos_por_entregar": {
                        "$sum": {"$cond": [{"$eq": ["$state", "Por entregar"]}, 1, 0]}
                    },
                    "fecha_mas_antigua": {"$min": "$created_at"},
                    "fecha_mas_reciente": {"$max": "$created_at"}
                }
            },
            {"$sort": {"total_casos": -1}}
        ]
        
        results = await db.cases.aggregate(pipeline).to_list(length=1000)
        
        # 3. Procesar resultados
        casos_por_entidad = {}
        total_casos = 0
        
        for result in results:
            entity_id = result["_id"]
            entity_name = result["entity_name"]
            casos_por_entidad[entity_id] = {
                "name": entity_name,
                "total_casos": result["total_casos"],
                "completados": result["casos_completados"],
                "en_proceso": result["casos_en_proceso"],
                "por_firmar": result["casos_por_firmar"],
                "por_entregar": result["casos_por_entregar"],
                "fecha_antigua": result["fecha_mas_antigua"],
                "fecha_reciente": result["fecha_mas_reciente"]
            }
            total_casos += result["total_casos"]
        
        # 4. Identificar entidades sin casos
        entidades_sin_casos = []
        for entity_code, entity_data in entity_info.items():
            if entity_code not in casos_por_entidad:
                entidades_sin_casos.append({
                    "code": entity_code,
                    "name": entity_data["name"],
                    "is_active": entity_data["is_active"]
                })
        
        # 5. Mostrar resultados
        print(f"\n📊 RESUMEN GENERAL:")
        print(f"Total de casos en el sistema: {total_casos}")
        print(f"Entidades con casos: {len(casos_por_entidad)}")
        print(f"Entidades sin casos: {len(entidades_sin_casos)}")
        
        # 6. Mostrar distribución de casos por entidad
        print(f"\n📈 DISTRIBUCIÓN DE CASOS POR ENTIDAD:")
        print(f"{'Entidad':<50} {'Casos':<8} {'Compl.':<8} {'Proc.':<8} {'Firm.':<8} {'Entr.':<8} {'%':<6}")
        print("-" * 100)
        
        for entity_id, data in sorted(casos_por_entidad.items(), key=lambda x: x[1]["total_casos"], reverse=True):
            porcentaje = (data["total_casos"] / total_casos * 100) if total_casos > 0 else 0
            print(f"{data['name']:<50} {data['total_casos']:<8} {data['completados']:<8} {data['en_proceso']:<8} {data['por_firmar']:<8} {data['por_entregar']:<8} {porcentaje:<6.1f}%")
        
        # 7. Mostrar entidades sin casos
        if entidades_sin_casos:
            print(f"\n⚠️  ENTIDADES SIN CASOS ASOCIADOS:")
            print(f"{'Código':<15} {'Nombre':<50} {'Activa':<8}")
            print("-" * 80)
            for entity in entidades_sin_casos:
                status = "✅ Sí" if entity["is_active"] else "❌ No"
                print(f"{entity['code']:<15} {entity['name']:<50} {status:<8}")
        else:
            print(f"\n✅ TODAS LAS ENTIDADES TIENEN CASOS ASOCIADOS")
        
        # 8. Análisis de distribución
        print(f"\n📊 ANÁLISIS DE DISTRIBUCIÓN:")
        
        if casos_por_entidad:
            casos_values = [data["total_casos"] for data in casos_por_entidad.values()]
            min_casos = min(casos_values)
            max_casos = max(casos_values)
            avg_casos = sum(casos_values) / len(casos_values)
            
            print(f"Casos por entidad - Mínimo: {min_casos}, Máximo: {max_casos}, Promedio: {avg_casos:.1f}")
            
            # Identificar entidades con muy pocos casos
            entidades_pocos_casos = []
            for entity_id, data in casos_por_entidad.items():
                if data["total_casos"] < 5:  # Menos de 5 casos
                    entidades_pocos_casos.append({
                        "name": data["name"],
                        "casos": data["total_casos"]
                    })
            
            if entidades_pocos_casos:
                print(f"\n⚠️  ENTIDADES CON POCOS CASOS (< 5):")
                for entity in entidades_pocos_casos:
                    print(f"  - {entity['name']}: {entity['casos']} casos")
        
        # 9. Análisis temporal
        print(f"\n📅 ANÁLISIS TEMPORAL:")
        if casos_por_entidad:
            fechas_antiguas = [data["fecha_antigua"] for data in casos_por_entidad.values() if data["fecha_antigua"]]
            fechas_recientes = [data["fecha_reciente"] for data in casos_por_entidad.values() if data["fecha_reciente"]]
            
            if fechas_antiguas:
                fecha_mas_antigua = min(fechas_antiguas)
                print(f"Fecha del caso más antiguo: {fecha_mas_antigua.strftime('%d/%m/%Y')}")
            
            if fechas_recientes:
                fecha_mas_reciente = max(fechas_recientes)
                print(f"Fecha del caso más reciente: {fecha_mas_reciente.strftime('%d/%m/%Y')}")
        
        # 10. Recomendaciones
        print(f"\n💡 RECOMENDACIONES:")
        
        if entidades_sin_casos:
            print(f"  - Hay {len(entidades_sin_casos)} entidades sin casos. Considera:")
            print(f"    * Verificar si estas entidades están activas")
            print(f"    * Generar casos de prueba para estas entidades")
            print(f"    * Revisar si hay errores en la asignación de entidades")
        
        if len(casos_por_entidad) > 0:
            # Calcular coeficiente de variación
            casos_values = [data["total_casos"] for data in casos_por_entidad.values()]
            if len(casos_values) > 1:
                import statistics
                cv = statistics.stdev(casos_values) / statistics.mean(casos_values) * 100
                print(f"  - Coeficiente de variación: {cv:.1f}%")
                if cv > 50:
                    print(f"    * La distribución es muy desigual (CV > 50%)")
                    print(f"    * Considera generar más casos para entidades con pocos casos")
                else:
                    print(f"    * La distribución es relativamente equilibrada")
        
        print(f"\n✅ Análisis completado")
        
    except Exception as e:
        print(f"❌ Error durante el análisis: {e}")
        import traceback
        traceback.print_exc()
    
    finally:
        await close_mongo_connection()

def main():
    """Función principal"""
    print("Iniciando análisis de distribución de casos por entidades...")
    asyncio.run(analyze_entity_distribution())

if __name__ == "__main__":
    main()
