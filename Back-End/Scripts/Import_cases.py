import sys
import math
from pathlib import Path
import asyncio
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Dict, Tuple, Optional

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import get_database, close_mongo_connection
from bson import ObjectId
from app.modules.cases.schemas.case import (
    CaseCreate,
    PatientInfo,
    EntityInfo,
    SampleInfo,
    SampleTest,
    AssignedPathologist,
    CasePriority,
    CaseState
)
from app.modules.cases.services.case_service import CaseService
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.patients.services.patient_service import PatientService
from app.modules.entities.services.entity_service import EntityService
from app.modules.pathologists.services.pathologist_service import PathologistService
from app.modules.tests.services.test_service import TestService

REGIONES_CUERPO = [
    # Cabeza y Cuello
    "Cabeza", "Cuello", "Cara", "Cuero Cabelludo", "Oreja", "Nariz", "Boca", "Lengua", "Garganta", "Tiroides",
    # Tórax
    "Tórax", "Mama Derecha", "Mama Izquierda", "Pulmón Derecho", "Pulmón Izquierdo", "Corazón", "Mediastino",
    # Abdomen
    "Abdomen", "Estómago", "Intestino Delgado", "Intestino Grueso", "Colon", "Recto", "Hígado", "Vesícula Biliar",
    "Páncreas", "Bazo", "Riñón Derecho", "Riñón Izquierdo", "Vejiga", "Útero", "Ovario Derecho", "Ovario Izquierdo",
    "Próstata", "Testículo Derecho", "Testículo Izquierdo",
    # Extremidades Superiores
    "Brazo Derecho", "Brazo Izquierdo", "Antebrazo Derecho", "Antebrazo Izquierdo", "Mano Derecha", "Mano Izquierda",
    "Dedo",
    # Extremidades Inferiores
    "Muslo Derecho", "Muslo Izquierdo", "Pierna Derecha", "Pierna Izquierda", "Pie Derecho", "Pie Izquierdo",
    "Dedo del Pie",
    # Piel
    "Piel de Cabeza", "Piel de Tórax", "Piel de Abdomen", "Piel de Brazo", "Piel de Pierna", "Piel de Espalda",
    "Piel de Glúteo",
    # Ganglios Linfáticos
    "Ganglio Cervical", "Ganglio Axilar", "Ganglio Inguinal", "Ganglio Mediastínico", "Ganglio Abdominal",
    # Otros
    "Otro (Especificar)", "No Especificado",
]

# Nombres genéricos para médicos solicitantes
NOMBRES_MEDICOS = [
    "Dr. Carlos Rodríguez", "Dra. María González", "Dr. José Martínez", "Dra. Ana López",
    "Dr. Luis García", "Dra. Carmen Hernández", "Dr. Miguel Pérez", "Dra. Isabel Sánchez",
    "Dr. Antonio Ramírez", "Dra. Patricia Torres", "Dr. Francisco Flores", "Dra. Rosa Morales",
    "Dr. Manuel Jiménez", "Dra. Teresa Ruiz", "Dr. Rafael Castillo", "Dra. Silvia Ortega",
    "Dr. Alejandro Vargas", "Dra. Lucía Ramos", "Dr. Fernando Guerrero", "Dra. Mónica Herrera", 
    "Dr. Ricardo Mendoza", "Dra. Adriana Castro", "Dr. Sergio Romero", "Dra. Beatriz Aguilar",
    "Dr. Javier Medina", "Dra. Claudia Vega", "Dr. Andrés Moreno", "Dra. Gabriela Delgado",
    "Dr. Pablo Gutiérrez", "Dra. Verónica Reyes", "Dr. Eduardo Silva", "Dra. Natalia Cruz",
    "Dr. Rubén Díaz", "Dra. Alejandra Peña", "Dr. Óscar Valdez", "Dra. Mariana Campos",
    "Dr. Víctor Núñez", "Dra. Daniela Espinoza", "Dr. Arturo Cabrera", "Dra. Paola Contreras",
]

SERVICIOS_MEDICOS = [
    "Patología", "Cirugía General", "Medicina Interna", "Ginecología", 
    "Urología", "Dermatología", "Gastroenterología", "Oncología"
]

def business_days(start: datetime, end: datetime) -> int:
    if not start or not end or end < start:
        return 0
    days = 0
    d = start.date()
    end_d = end.date()
    while d <= end_d:
        if d.weekday() < 5:
            days += 1
        d += timedelta(days=1)
    return max(0, days - 1)

def generar_observaciones_caso(region_cuerpo: str, tipo_atencion: str, estado: str, es_reciente: bool) -> str:
    """Genera observaciones realistas para un caso basado en la región del cuerpo, tipo de atención y estado."""
    observaciones_base = [
        f"Muestra de {region_cuerpo.lower()} para estudio histopatológico",
        f"Paciente {tipo_atencion.lower()} con lesión en {region_cuerpo.lower()}",
        f"Biopsia de {region_cuerpo.lower()} - descartar malignidad",
        f"Estudio anatomopatológico de {region_cuerpo.lower()}",
        f"Análisis histológico de muestra de {region_cuerpo.lower()}"
    ]
    
    observaciones_adicionales = [
        "Se requiere estudio urgente",
        "Control post-quirúrgico",
        "Seguimiento de lesión previa",
        "Primera consulta",
        "Paciente con antecedentes familiares",
        "Lesión de crecimiento reciente",
        "Cambios en características de la lesión"
    ]
    
    # Observaciones específicas según el estado
    observaciones_estado = {
        CaseState.EN_PROCESO: [
            "Caso en proceso de análisis",
            "Muestra recibida, iniciando procesamiento",
            "En espera de procesamiento histológico"
        ],
        CaseState.POR_FIRMAR: [
            "Resultado listo para revisión y firma",
            "Estudio completado, pendiente validación",
            "Análisis finalizado, esperando firma del patólogo"
        ],
        CaseState.POR_ENTREGAR: [
            "Resultado firmado, listo para entrega",
            "Caso finalizado, pendiente de entrega al paciente",
            "Informe completo y validado"
        ],
        CaseState.COMPLETADO: [
            "Caso completado y entregado",
            "Proceso finalizado exitosamente",
            "Resultado entregado al paciente"
        ]
    }
    
    obs_principal = random.choice(observaciones_base)
    
    # Agregar observación del estado si es caso reciente
    if es_reciente and estado in observaciones_estado:
        obs_estado = random.choice(observaciones_estado[estado])
        obs_principal = f"{obs_principal}. {obs_estado}"
    
    # Agregar observación adicional ocasionalmente
    if random.random() < 0.3:  # 30% de probabilidad
        obs_adicional = random.choice(observaciones_adicionales)
        obs_principal = f"{obs_principal}. {obs_adicional}"
    
    return f"{obs_principal}."

def random_date_from_year_to_today(year: int) -> datetime:
    today = datetime.now()
    # Excluir los últimos 8 días para casos normales
    end_date = today - timedelta(days=8)
    start = datetime(year, 1, 1)
    
    if start > end_date:
        start = datetime(today.year, 1, 1)
    
    delta_days = (end_date - start).days
    if delta_days <= 0:
        # Si no hay rango válido, usar una fecha hace 30 días
        return today - timedelta(days=random.randint(9, 30))
    
    rand_days = random.randint(0, delta_days)
    rand_seconds = random.randint(0, 86399)
    return start + timedelta(days=rand_days, seconds=rand_seconds)

async def load_entities(db) -> Dict[str, Dict]:
    entity_service = EntityService(db)
    from app.modules.entities.schemas.entity import EntitySearch
    search_params = EntitySearch()
    entities = await entity_service.list_all(search_params)
    
    name_to_entity: Dict[str, Dict] = {}
    for entity in entities:
        entity_dict = entity.model_dump() if hasattr(entity, "model_dump") else entity
        name_to_entity[entity_dict.get("name")] = entity_dict
    return name_to_entity

async def load_pathologists(db) -> List[Dict]:
    pathologist_service = PathologistService(db)
    pathologists = await pathologist_service.list_pathologists(skip=0, limit=1000)
    
    pathologist_list: List[Dict] = []
    for pathologist in pathologists:
        pathologist_dict = pathologist.model_dump() if hasattr(pathologist, "model_dump") else pathologist
        # Usar el código como ID, no el _id
        pathologist_code = pathologist_dict.get("pathologist_code") or pathologist_dict.get("code")
        pathologist_name = pathologist_dict.get("name") or pathologist_dict.get("pathologist_name")
        pathologist_list.append({
            "id": pathologist_code,
            "name": pathologist_name,
            "pathologist_code": pathologist_code,
            "pathologist_name": pathologist_name
        })
    return pathologist_list

async def load_tests(db) -> List[Dict]:
    test_service = TestService(db)
    from app.modules.tests.schemas.test import TestSearch
    search_params = TestSearch()
    tests = await test_service.list_all(search_params)
    
    test_list: List[Dict] = []
    for test in tests:
        test_dict = test.model_dump() if hasattr(test, "model_dump") else test
        # Usar el código como ID, no el _id
        test_code = test_dict.get("test_code") or test_dict.get("code")
        test_name = test_dict.get("name") or test_dict.get("test_name")
        test_list.append({
            "id": test_code,
            "name": test_name,
            "test_code": test_code,
            "test_name": test_name
        })
    return test_list

async def load_patients(db, batch_size: int = 1000) -> List[Dict]:
    # Cargar pacientes directamente desde la colección para mejor rendimiento
    patients: List[Dict] = []
    cursor = db.patients.find({}, {
        "_id": 1, 
        "patient_code": 1, 
        "name": 1, 
        "age": 1, 
        "gender": 1, 
        "entity_info": 1, 
        "care_type": 1
    })
    while True:
        chunk = await cursor.to_list(length=batch_size)
        if not chunk:
            break
        for doc in chunk:
            # Asegurar que entity_info tenga la estructura correcta
            if "entity_info" in doc and isinstance(doc["entity_info"], dict):
                if "name" not in doc["entity_info"]:
                    doc["entity_info"]["name"] = "Entidad Desconocida"
            patients.append(doc)
        if len(chunk) < batch_size:
            break
    return patients

def build_sample_tests(tests_catalog: List[Dict]) -> List[SampleTest]:
    if not tests_catalog:
        return []
    count = random.randint(1, 4)
    selected = random.choices(tests_catalog, k=count)
    # Usar el código como ID, no el _id
    return [SampleTest(id=s["id"], name=s["name"], quantity=random.randint(1, 3)) for s in selected]

async def seed_cases(count: int, year: int, start_number: int, dry_run: bool) -> Tuple[int, int]:
    created = 0
    skipped = 0
    
    # Contadores para estadísticas
    stats = {
        "casos_recientes": 0,
        "casos_antiguos": 0,
        "estados": {
            CaseState.EN_PROCESO: 0,
            CaseState.POR_FIRMAR: 0,
            CaseState.POR_ENTREGAR: 0,
            CaseState.COMPLETADO: 0
        },
        "con_patologo": 0,
        "sin_patologo": 0,
        "con_medico": 0,
        "sin_medico": 0
    }

    db = await get_database()
    try:
        case_service = CaseService(db)
        entity_service = EntityService(db)
        pathologist_service = PathologistService(db)
        test_service = TestService(db)
        patient_service = PatientService(db)

        # Cargar datos necesarios
        print("Cargando datos necesarios...")
        entidades_by_name = await load_entities(db)
        pathologists = await load_pathologists(db)
        tests_catalog = await load_tests(db)
        patients = await load_patients(db)

        if not patients:
            print("[ERROR] No hay pacientes en la base de datos. Abortando.")
            return 0, count
        if not entidades_by_name:
            print("[ERROR] No hay entidades en la base de datos. Abortando.")
            return 0, count
        if not pathologists:
            print("[WARN] No hay patólogos activos. Continuaré creando casos sin patólogo asignado.")

        current_num = start_number
        base_start_date = datetime(year, 1, 1)
        today = datetime.now()
        
        # Calcular cuántos casos serán recientes (10% del total)
        casos_recientes_count = max(1, int(count * 0.1))  # Al menos 1 caso reciente
        casos_antiguos_count = count - casos_recientes_count
        
        # Fechas para casos recientes (últimos 10 días)
        fecha_inicio_recientes = today - timedelta(days=10)
        fecha_fin_recientes = today
        
        print(f"Generando {count} casos (recientes: {casos_recientes_count}, antiguos: {casos_antiguos_count})")
        
        # Fechas para casos antiguos (desde enero hasta hace 11 días)
        max_fecha_antiguos = today - timedelta(days=11)
        if base_start_date > max_fecha_antiguos:
            base_start_date = max_fecha_antiguos - timedelta(days=60)
        total_span_days_antiguos = max(1, (max_fecha_antiguos - base_start_date).days)

        for i in range(count):
            # Paciente
            p = random.choice(patients)
            entidad_nombre = p.get("entity_info", {}).get("name")
            entidad_doc = entidades_by_name.get(entidad_nombre) if entidad_nombre else None
            if not entidad_doc:
                entidad_doc = random.choice(list(entidades_by_name.values()))
            
            entity_info = EntityInfo(
                id=entidad_doc.get("entity_code") or entidad_doc.get("code"),
                name=entidad_doc.get("name"),
            )
            
            # Asegurar que el tipo de atención sea válido
            tipo_atencion_original = str(p.get("care_type", "Ambulatorio"))
            if tipo_atencion_original not in ["Ambulatorio", "Hospitalizado"]:
                tipo_atencion_valido = random.choice(["Ambulatorio", "Hospitalizado"])
            else:
                tipo_atencion_valido = tipo_atencion_original
            
            # Asegurar que el género sea válido
            genero_original = str(p.get("gender", "Masculino"))
            if genero_original not in ["Masculino", "Femenino"]:
                genero_valido = random.choice(["Masculino", "Femenino"])
            else:
                genero_valido = genero_original
            
            patient_info = PatientInfo(
                patient_code=str(p.get("patient_code")),
                name=p.get("name", "Paciente Sin Nombre"),
                age=max(1, int(p.get("age", 30))),
                gender=genero_valido,
                entity_info=entity_info,
                care_type=tipo_atencion_valido,
                observations=f"Paciente ingresado para estudio histopatológico - {tipo_atencion_valido}",
            )

            # Muestras (1-3), con pruebas (1-4, con duplicados posibles)
            samples: List[SampleInfo] = []
            num_muestras = random.randint(1, 3)
            for _m in range(num_muestras):
                region = random.choice(REGIONES_CUERPO)
                tests_items = build_sample_tests(tests_catalog)
                samples.append(SampleInfo(body_region=region, tests=tests_items))

            # Médico solicitante (80% de probabilidad de tener uno)
            requesting_physician: Optional[str] = None
            if random.random() < 0.8:  # 80% de casos tendrán médico solicitante
                requesting_physician = random.choice(NOMBRES_MEDICOS)

            # Un solo servicio por caso
            service = random.choice(SERVICIOS_MEDICOS)

            # Determinar si este caso será reciente o antiguo
            es_caso_reciente = i >= (count - casos_recientes_count)
            
            if es_caso_reciente:
                # Caso reciente: fecha aleatoria en los últimos 10 días
                days_back = random.randint(0, 10)
                fecha_creacion = today - timedelta(days=days_back)
                days_since_creation = days_back
            else:
                # Caso antiguo: distribuir desde enero hasta hace 11 días
                caso_antiguo_index = i
                if casos_antiguos_count <= 1:
                    ingreso_offset_days = total_span_days_antiguos
                else:
                    ingreso_offset_days = math.floor(caso_antiguo_index * (total_span_days_antiguos / (casos_antiguos_count - 1)))
                ingreso_offset_days = max(0, min(total_span_days_antiguos, ingreso_offset_days))
                fecha_creacion = base_start_date + timedelta(days=ingreso_offset_days)
                days_since_creation = (today - fecha_creacion).days
            
            if es_caso_reciente:
                # Casos recientes: estados más realistas y variados
                estados_posibles = [
                    CaseState.EN_PROCESO,
                    CaseState.POR_FIRMAR, 
                    CaseState.POR_ENTREGAR,
                    CaseState.COMPLETADO
                ]
                
                # Probabilidades más realistas para casos recientes
                probabilidades = [0.5, 0.3, 0.15, 0.05]  # 50% en proceso, 30% por firmar, 15% por entregar, 5% completado
                estado_final = random.choices(estados_posibles, weights=probabilidades)[0]
            else:
                # Casos antiguos: TODOS completados
                estado_final = CaseState.COMPLETADO

            # Patólogo asignado según el estado del caso
            assigned_pathologist: Optional[AssignedPathologist] = None
            if pathologists:
                # Probabilidad de asignación según el estado
                probabilidad_patologo = {
                    CaseState.EN_PROCESO: 0.7,      # 70% tienen patólogo asignado
                    CaseState.POR_FIRMAR: 0.95,     # 95% tienen patólogo asignado
                    CaseState.POR_ENTREGAR: 1.0,    # 100% tienen patólogo asignado
                    CaseState.COMPLETADO: 1.0       # 100% tienen patólogo asignado
                }
                
                if random.random() < probabilidad_patologo.get(estado_final, 0.8):
                    pat = random.choice(pathologists)
                    assigned_pathologist = AssignedPathologist(
                        id=pat.get("id"),  # Ya es el código
                        name=pat.get("name")  # Ya es el nombre correcto
                    )

            # Generar observaciones realistas
            region_principal = samples[0].body_region if samples else "región no especificada"
            observaciones_generadas = generar_observaciones_caso(region_principal, tipo_atencion_valido, estado_final, es_caso_reciente)
            
            # Determinar prioridad (Normal: 75%, Prioritario: 25%)
            prioridad_rand = random.random()
            if prioridad_rand < 0.75:
                priority = CasePriority.NORMAL
            else:
                priority = CasePriority.PRIORITARIO
            
            # Crear el caso
            case_create = CaseCreate(
                patient_info=patient_info,
                requesting_physician=requesting_physician,
                service=service,
                samples=samples,
                state=estado_final,
                priority=priority,
                observations=observaciones_generadas,
            )

            # Actualizar estadísticas
            if es_caso_reciente:
                stats["casos_recientes"] += 1
            else:
                stats["casos_antiguos"] += 1
            
            stats["estados"][estado_final] += 1
            
            if assigned_pathologist:
                stats["con_patologo"] += 1
            else:
                stats["sin_patologo"] += 1
                
            if requesting_physician:
                stats["con_medico"] += 1
            else:
                stats["sin_medico"] += 1

            if dry_run:
                created += 1
                medico_txt = requesting_physician if requesting_physician else 'sin médico'
                reciente_txt = "RECIENTE" if es_caso_reciente else "ANTIGUO"
                dias_txt = f"({days_since_creation}d)"
                print(f"[DRY-RUN] Caso #{i+1} {reciente_txt} {dias_txt} | estado={estado_final}, médico={medico_txt}")
                continue

            try:
                # Crear el caso usando el servicio
                created_case = await case_service.create_case(case_create)

                # Ajustar la fecha de creación para distribuir los casos a lo largo del año
                # Nota: El repositorio permite actualizar 'created_at' directamente
                repo = CaseRepository(db)
                await repo.update_by_case_code(created_case.case_code, {"created_at": fecha_creacion})

                # Si el caso tiene patólogo asignado, actualizarlo
                if assigned_pathologist:
                    from app.modules.cases.schemas.case import CaseUpdate
                    case_update = CaseUpdate(assigned_pathologist=assigned_pathologist)
                    await case_service.update_case(created_case.case_code, case_update)

                # Asignar fecha de firma para casos Por entregar o Completados
                if estado_final in [CaseState.POR_FIRMAR, CaseState.POR_ENTREGAR, CaseState.COMPLETADO]:
                    # Asignar oportunidad entre 1 y 11 días hábiles (sesgo hacia 3-7)
                    pesos = [1, 2, 4, 6, 6, 6, 6, 4, 2, 1, 1]  # 1..11
                    objetivo_habiles = random.choices(list(range(1, 12)), weights=pesos, k=1)[0]
                    dias_corridos = 0
                    fecha_firma = fecha_creacion
                    while business_days(fecha_creacion, fecha_firma) < objetivo_habiles:
                        dias_corridos += 1
                        fecha_firma = fecha_creacion + timedelta(days=dias_corridos)
                    if fecha_firma > today:
                        fecha_firma = today
                    
                    update_data = {
                        "signed_at": fecha_firma,
                        "business_days": objetivo_habiles
                    }
                    
                    # Para casos completados, agregar campos adicionales
                    if estado_final == CaseState.COMPLETADO:
                        # Generar resultado del caso
                        region_principal = samples[0].body_region if samples else "región no especificada"
                        metodo = random.choice([
                            "tincion-he-eosina",
                            "inmunohistoquimica-polimero-peroxidasa", 
                            "tincion-tricromica-masson",
                            "tincion-pas",
                            "tincion-plata-metenamina"
                        ])
                        
                        macro_result = f"Lesión en {region_principal.lower()} de aspecto nodular, bien delimitada, de coloración variable."
                        micro_result = f"Microscópicamente se observa proliferación celular en {region_principal.lower()} con características histológicas sugestivas de proceso benigno."
                        diagnosis = f"Proceso proliferativo benigno en {region_principal.lower()}"
                        
                        # Fecha de entrega (1-3 días después de la firma)
                        dias_entrega = random.randint(1, 3)
                        fecha_entrega = fecha_firma + timedelta(days=dias_entrega)
                        if fecha_entrega > today:
                            fecha_entrega = today
                        
                        # A quién se entregó
                        entregado_a = random.choice([
                            "Dr. Carlos Rodríguez", "Dra. María González", "Dr. José Martínez", 
                            "Dra. Ana López", "Dr. Luis García", "Dra. Carmen Hernández",
                            "Paciente directamente", "Familiar del paciente", "Servicio de Medicina Interna"
                        ])
                        
                        update_data.update({
                            "result": {
                                "method": [metodo],
                                "macro_result": macro_result,
                                "micro_result": micro_result,
                                "diagnosis": diagnosis,
                                "updated_at": fecha_firma
                            },
                            "delivered_at": fecha_entrega,
                            "delivered_to": entregado_a
                        })
                    
                    await repo.update_by_case_code(created_case.case_code, update_data)

                created += 1
                medico_txt = requesting_physician if requesting_physician else 'sin médico'
                reciente_txt = "RECIENTE" if es_caso_reciente else "ANTIGUO"
                print(f"[OK] Caso {reciente_txt} creado: {created_case.case_code} - estado={estado_final}, médico={medico_txt}")
            except Exception as e:
                skipped += 1
                print(f"[SKIP] Error creando caso -> {e}")

        # Mostrar estadísticas finales
        if dry_run or created > 0:
            print("\n" + "="*60)
            print("RESUMEN DE CASOS GENERADOS")
            print("="*60)
            print(f"Total casos: {created}")
            print(f"Casos recientes (≤10 días): {stats['casos_recientes']}")
            print(f"Casos antiguos (>10 días): {stats['casos_antiguos']}")
            print("\nDistribución por estado:")
            for estado, cantidad in stats["estados"].items():
                porcentaje = (cantidad / created * 100) if created > 0 else 0
                print(f"  {estado}: {cantidad} ({porcentaje:.1f}%)")
            print(f"\nCon patólogo asignado: {stats['con_patologo']}")
            print(f"Sin patólogo asignado: {stats['sin_patologo']}")
            print(f"Con médico solicitante: {stats['con_medico']}")
            print(f"Sin médico solicitante: {stats['sin_medico']}")
            
            # Información adicional sobre casos recientes
            if stats['casos_recientes'] > 0:
                print(f"\nCasos recientes generados entre:")
                print(f"  Desde: {fecha_inicio_recientes.strftime('%d/%m/%Y')} (hace 10 días)")
                print(f"  Hasta: {fecha_fin_recientes.strftime('%d/%m/%Y')} (hoy)")
            
            print("="*60)

        return created, skipped
    finally:
        await close_mongo_connection()

def main():
    parser = argparse.ArgumentParser(description="Importar casos con muestras y pruebas reales")
    parser.add_argument("--count", type=int, help="Cantidad de casos a crear")
    parser.add_argument("--year", type=int, default=datetime.now().year, help="Año para el consecutivo (YYYY)")
    parser.add_argument("--start-number", type=int, default=1, help="Número inicial para el consecutivo (1 => 00001)")
    parser.add_argument("--dry-run", action="store_true", help="Previsualizar sin insertar")
    args = parser.parse_args()

    if args.count is None:
        try:
            user_input = input("¿Cuántos casos quieres generar? ").strip()
            count = int(user_input)
        except Exception:
            print("Entrada inválida. Usa --count N")
            sys.exit(1)
    else:
        count = args.count

    print("="*60)
    print("TEST CASES GENERATION")
    print("="*60)
    print(f"Mode: {'DRY RUN' if args.dry_run else 'REAL EXECUTION'}")
    print(f"Total cases to generate: {count}")
    print("="*60)

    created, skipped = asyncio.run(
        seed_cases(count=count, year=args.year, start_number=args.start_number, dry_run=args.dry_run)
    )
    print(f"✅ Completed. Created: {created}, Skipped: {skipped}")

if __name__ == "__main__":
    main()