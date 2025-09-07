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

from app.config.database import connect_to_mongo, close_mongo_connection
from bson import ObjectId
from app.modules.casos.repositories.caso_repository import CasoRepository
from app.modules.casos.schemas.caso import (
    CasoCreateRequest,
    PacienteInfo as CasoPacienteInfo,
    EntidadInfo as CasoEntidadInfo,
    MuestraInfo,
    PatologoInfo as CasoPatologoInfo,
    ResultadoInfo,
)
from app.modules.casos.models.caso import PrioridadCasoEnum
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository
from app.modules.pruebas.schemas.prueba import PruebasItem
from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
from app.modules.entidades.models.entidad import EntidadSearch
from app.shared.schemas.common import EstadoCasoEnum


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

def generar_observaciones_caso(region_cuerpo: str, tipo_atencion: str, estado: EstadoCasoEnum, es_reciente: bool) -> str:
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
        EstadoCasoEnum.EN_PROCESO: [
            "Caso en proceso de análisis",
            "Muestra recibida, iniciando procesamiento",
            "En espera de procesamiento histológico"
        ],
        EstadoCasoEnum.POR_FIRMAR: [
            "Resultado listo para revisión y firma",
            "Estudio completado, pendiente validación",
            "Análisis finalizado, esperando firma del patólogo"
        ],
        EstadoCasoEnum.POR_ENTREGAR: [
            "Resultado firmado, listo para entrega",
            "Caso finalizado, pendiente de entrega al paciente",
            "Informe completo y validado"
        ],
        EstadoCasoEnum.COMPLETADO: [
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


def format_caso_code(year: int, number: int) -> str:
    return f"{year}-{number:05d}"


async def load_entities(db) -> Dict[str, Dict]:
    repo = EntidadRepository(db)
    name_to_entity: Dict[str, Dict] = {}
    skip = 0
    limit = 100
    while True:
        page = await repo.get_all(search_params=EntidadSearch(activo=None, skip=skip, limit=limit))
        if not page:
            break
        for e in page:
            doc = e.model_dump() if hasattr(e, "model_dump") else e
            name_to_entity[doc.get("entidad_name") or doc.get("EntidadName")] = doc
        if len(page) < limit:
            break
        skip += limit
    return name_to_entity


async def load_patologos(db) -> List[Dict]:
    repo = PatologoRepository(db)
    patologos: List[Dict] = []
    skip = 0
    limit = 200
    while True:
        page = await repo.get_multi(skip=skip, limit=limit, filters={"is_active": True})
        if not page:
            break
        for p in page:
            doc = p.model_dump() if hasattr(p, "model_dump") else p
            patologos.append(doc)
        if len(page) < limit:
            break
        skip += limit
    return patologos


async def load_pruebas(db) -> List[Dict]:
    repo = PruebaRepository(db)
    pruebas: List[Dict] = []
    # Reusar get_all con búsqueda amplia
    from app.modules.pruebas.schemas.prueba import PruebaSearch
    search = PruebaSearch(query=None, activo=True, skip=0, limit=1000)
    page = await repo.get_all(search)
    for pr in page:
        doc = pr.model_dump() if hasattr(pr, "model_dump") else pr
        # id puede venir como ObjectId; asegurar string
        _id = str(doc.get("_id") or doc.get("id"))
        codigo = doc.get("prueba_code", _id)  # Usar código si existe, sino usar ID
        nombre = doc.get("prueba_name", "Prueba sin nombre")
        pruebas.append({"id": codigo, "nombre": nombre})  # Usar código como ID
    return pruebas


async def load_pacientes(db, batch_size: int = 1000) -> List[Dict]:
    # Cargar pacientes desde la colección directamente (estructura dict con entidad_info {nombre})
    pacientes: List[Dict] = []
    cursor = db.pacientes.find({}, {"_id": 1, "paciente_code": 1, "nombre": 1, "edad": 1, "sexo": 1, "entidad_info": 1, "tipo_atencion": 1})
    while True:
        chunk = await cursor.to_list(length=batch_size)
        if not chunk:
            break
        for doc in chunk:
            # Asegurar que entidad_info tenga la estructura correcta
            if "entidad_info" in doc and isinstance(doc["entidad_info"], dict):
                if "nombre" not in doc["entidad_info"]:
                    doc["entidad_info"]["nombre"] = "Entidad Desconocida"
            pacientes.append(doc)
        if len(chunk) < batch_size:
            break
    return pacientes


def build_pruebas_items(pruebas_catalog: List[Dict]) -> List[PruebasItem]:
    if not pruebas_catalog:
        return []
    count = random.randint(1, 4)
    selected = random.choices(pruebas_catalog, k=count)
    # Para simular múltiplos de una misma prueba, permitimos duplicados en selected
    return [PruebasItem(id=s["id"], nombre=s["nombre"]) for s in selected]


async def seed_cases(count: int, year: int, start_number: int, dry_run: bool) -> Tuple[int, int]:
    created = 0
    skipped = 0
    
    # Contadores para estadísticas
    stats = {
        "casos_recientes": 0,
        "casos_antiguos": 0,
        "estados": {
            EstadoCasoEnum.EN_PROCESO: 0,
            EstadoCasoEnum.POR_FIRMAR: 0,
            EstadoCasoEnum.POR_ENTREGAR: 0,
            EstadoCasoEnum.COMPLETADO: 0
        },
        "con_patologo": 0,
        "sin_patologo": 0,
        "con_medico": 0,
        "sin_medico": 0
    }

    db = await connect_to_mongo()
    try:
        caso_repo = CasoRepository(db)
        entidades_by_name = await load_entities(db)
        patologos = await load_patologos(db)
        pruebas_catalog = await load_pruebas(db)
        pacientes = await load_pacientes(db)

        if not pacientes:
            print("[WARN] No hay pacientes en la base de datos. Aborto.")
            return 0, count
        if not entidades_by_name:
            print("[WARN] No hay entidades en la base de datos. Aborto.")
            return 0, count
        if not patologos:
            print("[WARN] No hay patólogos activos. Continuaré creando casos sin patólogo_asignado.")

        current_num = start_number
        base_start_date = datetime(year, 1, 1)
        today = datetime.now()
        
        # Calcular cuántos casos serán recientes (10% del total)
        casos_recientes_count = max(1, int(count * 0.1))  # Al menos 1 caso reciente
        casos_antiguos_count = count - casos_recientes_count
        
        # Fechas para casos recientes (últimos 10 días: del 9 al 19 de agosto)
        fecha_inicio_recientes = today - timedelta(days=10)  # 9 de agosto
        fecha_fin_recientes = today  # 19 de agosto
        
        print(f"Generando {count} casos:")
        print(f"  - Casos recientes (últimos 10 días): {casos_recientes_count} ({casos_recientes_count/count*100:.1f}%)")
        print(f"  - Casos antiguos (completados): {casos_antiguos_count} ({casos_antiguos_count/count*100:.1f}%)")
        print(f"  - DEBUG: Fecha hoy = {today.strftime('%d/%m/%Y')}")
        print(f"  - DEBUG: Rango recientes = {fecha_inicio_recientes.strftime('%d/%m/%Y')} a {fecha_fin_recientes.strftime('%d/%m/%Y')}")
        print(f"  - DEBUG: Estados disponibles = {[e.value for e in EstadoCasoEnum]}")
        print()
        
        # Fechas para casos antiguos (desde enero hasta hace 11 días)
        max_fecha_antiguos = today - timedelta(days=11)  # 8 de agosto hacia atrás
        if base_start_date > max_fecha_antiguos:
            base_start_date = max_fecha_antiguos - timedelta(days=60)  # Si el año es muy reciente, usar 60 días atrás
        total_span_days_antiguos = max(1, (max_fecha_antiguos - base_start_date).days)

        for i in range(count):
            # Ya no necesitamos generar el código manualmente, 
            # el servicio lo hará automáticamente

            # Paciente
            p = random.choice(pacientes)
            entidad_nombre = ((p.get("entidad_info") or {}).get("nombre"))
            entidad_doc = entidades_by_name.get(entidad_nombre) if entidad_nombre else None
            if not entidad_doc:
                # Si no se encuentra por nombre, elegir una al azar
                entidad_doc = random.choice(list(entidades_by_name.values()))
            entidad_info = CasoEntidadInfo(
                id=entidad_doc.get("entidad_code") or entidad_doc.get("EntidadCode"),
                nombre=entidad_doc.get("entidad_name") or entidad_doc.get("EntidadName"),
            )
            # Asegurar que el tipo de atención sea válido (solo Ambulatorio o Hospitalizado)
            tipo_atencion_original = str(p.get("tipo_atencion", "Ambulatorio"))
            if tipo_atencion_original not in ["Ambulatorio", "Hospitalizado"]:
                tipo_atencion_valido = random.choice(["Ambulatorio", "Hospitalizado"])
            else:
                tipo_atencion_valido = tipo_atencion_original
            
            paciente_info = CasoPacienteInfo(
                paciente_code=str(p.get("paciente_code") or p.get("_id")),
                nombre=p.get("nombre", "Paciente Sin Nombre"),
                edad=max(1, int(p.get("edad", 30))),  # Asegurar edad válida
                sexo=str(p.get("sexo", "Masculino")),
                entidad_info=entidad_info,
                tipo_atencion=tipo_atencion_valido,
                observaciones=f"Paciente ingresado para estudio histopatológico - {tipo_atencion_valido}",
            )

            # Muestras (1-3), con pruebas (1-4, con duplicados posibles)
            muestras: List[MuestraInfo] = []
            num_muestras = random.randint(1, 3)
            for _m in range(num_muestras):
                region = random.choice(REGIONES_CUERPO)
                pruebas_items = build_pruebas_items(pruebas_catalog)
                muestras.append(MuestraInfo(region_cuerpo=region, pruebas=pruebas_items))

            # Médico solicitante (80% de probabilidad de tener uno)
            medico_solicitante: Optional[str] = None
            if random.random() < 0.8:  # 80% de casos tendrán médico solicitante
                nombre_medico = random.choice(NOMBRES_MEDICOS)
                medico_solicitante = nombre_medico

            # Determinar si este caso será reciente o antiguo
            # Los ÚLTIMOS N casos serán recientes (números más altos = fechas más recientes)
            es_caso_reciente = i >= (count - casos_recientes_count)
            
            if es_caso_reciente:
                # Caso reciente: fecha aleatoria en los últimos 10 días
                days_back = random.randint(0, 10)  # 0 = hoy, 10 = hace 10 días
                fecha_creacion = today - timedelta(days=days_back)
                days_since_creation = days_back
            else:
                # Caso antiguo: distribuir desde enero hasta hace 11 días
                # Como los casos antiguos son los primeros índices (0 a casos_antiguos_count-1)
                caso_antiguo_index = i
                if casos_antiguos_count <= 1:
                    ingreso_offset_days = total_span_days_antiguos
                else:
                    ingreso_offset_days = math.floor(caso_antiguo_index * (total_span_days_antiguos / (casos_antiguos_count - 1)))
                ingreso_offset_days = max(0, min(total_span_days_antiguos, ingreso_offset_days))
                fecha_creacion = base_start_date + timedelta(days=ingreso_offset_days)
                days_since_creation = (today - fecha_creacion).days
            
            if es_caso_reciente:
                # Casos recientes: estados más realistas y variados (SIN fecha de entrega para la mayoría)
                estados_posibles = [
                    EstadoCasoEnum.EN_PROCESO,
                    EstadoCasoEnum.POR_FIRMAR, 
                    EstadoCasoEnum.POR_ENTREGAR,
                    EstadoCasoEnum.COMPLETADO
                ]
                
                # Probabilidades más realistas para casos recientes - MENOS completados
                probabilidades = [0.5, 0.3, 0.15, 0.05]  # 50% en proceso, 30% por firmar, 15% por entregar, 5% completado
                estado_final = random.choices(estados_posibles, weights=probabilidades)[0]
                
                # Configurar fechas según el estado - IMPORTANTE: casos recientes NO deben tener fecha_entrega excepto los completados
                if estado_final == EstadoCasoEnum.EN_PROCESO:
                    # En proceso: sin fecha de firma ni entrega
                    fecha_firma_final = None
                    fecha_entrega = None
                    fecha_finalizacion = fecha_creacion
                    
                elif estado_final == EstadoCasoEnum.POR_FIRMAR:
                    # Por firmar: sin fecha de firma ni entrega, pero con resultado
                    fecha_firma_final = None
                    fecha_entrega = None
                    # Si es de hoy, usar la misma fecha; si no, agregar días aleatorios
                    if days_since_creation == 0:
                        fecha_finalizacion = fecha_creacion
                    else:
                        fecha_finalizacion = fecha_creacion + timedelta(days=random.randint(1, max(1, days_since_creation)))
                    
                elif estado_final == EstadoCasoEnum.POR_ENTREGAR:
                    # Por entregar: con fecha de firma pero SIN fecha de entrega
                    if days_since_creation == 0:
                        # Si es de hoy, firmar el mismo día
                        firma_offset_days = 0
                    else:
                        firma_offset_days = random.randint(1, min(3, max(1, days_since_creation)))
                    fecha_firma_final = fecha_creacion + timedelta(days=firma_offset_days)
                    fecha_entrega = None  # IMPORTANTE: Sin fecha de entrega
                    fecha_finalizacion = fecha_firma_final
                    
                else:  # COMPLETADO - Solo unos pocos casos recientes
                    # Completado: con todas las fechas
                    if days_since_creation == 0:
                        # Si es de hoy, completar el mismo día
                        days_to_delivery = 0
                        fecha_entrega = fecha_creacion
                        fecha_firma_final = fecha_creacion
                    else:
                        max_delivery_days = max(1, min(days_since_creation, 5))  # Máximo 5 días para casos recientes
                        days_to_delivery = random.randint(1, max_delivery_days)
                        fecha_entrega = fecha_creacion + timedelta(days=days_to_delivery)
                        
                        firma_offset_days = random.randint(1, min(2, days_to_delivery))
                        fecha_firma_final = fecha_creacion + timedelta(days=firma_offset_days)
                        
                        if fecha_firma_final > fecha_entrega:
                            fecha_firma_final = fecha_entrega
                    
                    fecha_finalizacion = fecha_entrega
            else:
                # Casos antiguos: TODOS completados con fecha de entrega
                max_delivery_days = max(1, min(10, days_since_creation))
                days_to_delivery = random.randint(1, max_delivery_days)
                fecha_entrega = fecha_creacion + timedelta(days=days_to_delivery)
                
                # Validación adicional para evitar errores
                max_firma_days = min(3, days_to_delivery)
                firma_offset_days = random.randint(1, max(1, max_firma_days))
                fecha_firma_final = fecha_creacion + timedelta(days=firma_offset_days)
                
                if fecha_firma_final > fecha_entrega:
                    fecha_firma_final = fecha_entrega
                
                estado_final = EstadoCasoEnum.COMPLETADO
                fecha_finalizacion = fecha_entrega

            # Patólogo asignado según el estado del caso (después de determinar el estado)
            patologo_info: Optional[CasoPatologoInfo] = None
            if patologos:
                # Probabilidad de asignación según el estado
                probabilidad_patologo = {
                    EstadoCasoEnum.EN_PROCESO: 0.7,      # 70% tienen patólogo asignado
                    EstadoCasoEnum.POR_FIRMAR: 0.95,     # 95% tienen patólogo asignado
                    EstadoCasoEnum.POR_ENTREGAR: 1.0,    # 100% tienen patólogo asignado
                    EstadoCasoEnum.COMPLETADO: 1.0       # 100% tienen patólogo asignado
                }
                
                if random.random() < probabilidad_patologo.get(estado_final, 0.8):
                    pat = random.choice(patologos)
                    pat_codigo = pat.get("patologo_code") or pat.get("patologoCode")
                    pat_nombre = pat.get("patologo_name") or pat.get("patologoName")
                    if pat_codigo and pat_nombre:
                        patologo_info = CasoPatologoInfo(codigo=pat_codigo, nombre=pat_nombre)

            # Validar que las fechas sean consistentes
            if fecha_firma_final and fecha_firma_final < fecha_creacion:
                fecha_firma_final = fecha_creacion + timedelta(hours=random.randint(1, 24))
            
            if fecha_entrega and fecha_entrega < fecha_creacion:
                fecha_entrega = fecha_creacion + timedelta(days=random.randint(1, 5))

            # Generar observaciones realistas
            region_principal = muestras[0].region_cuerpo if muestras else "región no especificada"
            observaciones_generadas = generar_observaciones_caso(region_principal, tipo_atencion_valido, estado_final, es_caso_reciente)
            
            # Determinar prioridad (Normal: 70%, Prioritario: 25%, Urgente: 5%)
            prioridad_rand = random.random()
            if prioridad_rand < 0.70:
                prioridad_caso = PrioridadCasoEnum.NORMAL
            elif prioridad_rand < 0.95:
                prioridad_caso = PrioridadCasoEnum.PRIORITARIO
            else:
                prioridad_caso = PrioridadCasoEnum.URGENTE
            
            # Usar CasoCreateRequest en lugar de CasoCreate (sin CasoCode)
            caso_create = CasoCreateRequest(
                paciente=paciente_info,
                medico_solicitante=medico_solicitante,
                servicio=random.choice(SERVICIOS_MEDICOS),  # Servicio aleatorio
                muestras=muestras,
                estado=estado_final,
                prioridad=prioridad_caso,
                fecha_creacion=fecha_creacion,
                fecha_firma=fecha_firma_final,
                fecha_entrega=fecha_entrega,
                fecha_actualizacion=fecha_finalizacion,
                observaciones_generales=observaciones_generadas,
            )

            # Actualizar estadísticas
            if es_caso_reciente:
                stats["casos_recientes"] += 1
            else:
                stats["casos_antiguos"] += 1
            
            stats["estados"][estado_final] += 1
            
            if patologo_info:
                stats["con_patologo"] += 1
            else:
                stats["sin_patologo"] += 1
                
            if medico_solicitante:
                stats["con_medico"] += 1
            else:
                stats["sin_medico"] += 1

            if dry_run:
                created += 1
                entrega_txt = fecha_entrega.strftime('%d/%m/%Y') if fecha_entrega else 'SIN ENTREGA'
                medico_txt = medico_solicitante if medico_solicitante else 'sin médico'
                reciente_txt = "RECIENTE" if es_caso_reciente else "ANTIGUO"
                dias_txt = f"({days_since_creation}d)"
                print(f"[DRY-RUN] Caso #{i+1} {reciente_txt} {dias_txt} | estado={estado_final.value}, entrega={entrega_txt}, médico={medico_txt}")
                continue

            try:
                # Generar código consecutivo manualmente
                from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository
                consecutivo_repo = ConsecutivoRepository(db)
                siguiente_numero = await consecutivo_repo.obtener_siguiente_numero(year)
                caso_code_generado = f"{year}-{siguiente_numero:05d}"
                
                # Crear el caso directamente con todos los datos correctos
                from app.modules.casos.models.caso import Caso
                
                # Preparar resultado SOLO si el caso está en estado que lo requiere
                resultado_data = None
                if estado_final in [EstadoCasoEnum.POR_FIRMAR, EstadoCasoEnum.POR_ENTREGAR, EstadoCasoEnum.COMPLETADO]:
                    from app.modules.casos.models.caso import ResultadoInfo as ModelResultadoInfo
                    resultado_data = ModelResultadoInfo(
                        metodo=["Histopatología"],
                        resultado_macro="Muestra procesada correctamente. Tejido de características normales.",
                        resultado_micro="Arquitectura conservada. Sin alteraciones significativas observadas.",
                        diagnostico=random.choice([
                            "Proceso inflamatorio crónico leve",
                            "Hiperplasia benigna",
                            "Cambios reactivos inespecíficos",
                            "Tejido normal sin alteraciones",
                            "Proceso inflamatorio agudo resuelto",
                            "Fibrosis leve",
                            "Hiperplasia epitelial benigna",
                            "Infiltrado linfocitario moderado",
                            "Cambios degenerativos leves",
                            "Proceso cicatricial maduro",
                            "Hiperqueratosis benigna",
                            "Metaplasia escamosa",
                            "Adenoma tubular",
                            "Lipoma benigno",
                            "Quiste sebáceo"
                        ])
                    )
                # Los casos EN_PROCESO no tienen resultado
                
                # Crear el caso completo - convertir objetos Pydantic a diccionarios
                caso_completo = Caso(
                    caso_code=caso_code_generado,
                    paciente=paciente_info.model_dump(),
                    medico_solicitante=medico_solicitante.model_dump() if medico_solicitante else None,
                    servicio=random.choice(SERVICIOS_MEDICOS),
                    muestras=[muestra.model_dump() for muestra in muestras],
                    estado=estado_final,  # ESTADO CORRECTO
                    fecha_creacion=fecha_creacion,
                    fecha_firma=fecha_firma_final,
                    fecha_entrega=fecha_entrega,
                    fecha_actualizacion=fecha_finalizacion,
                    patologo_asignado=patologo_info.model_dump() if patologo_info else None,
                    resultado=resultado_data.model_dump() if resultado_data else None,
                    observaciones_generales=observaciones_generadas,
                    ingresado_por="seed_script",
                    actualizado_por="seed_script",
                    # Campo activo eliminado
                )
                
                # Insertar directamente en MongoDB para evitar cualquier modificación del repositorio
                caso_dict = caso_completo.model_dump(by_alias=True)
                caso_dict["_id"] = ObjectId()  # Generar ID manualmente
                
                result = await db.casos.insert_one(caso_dict)
                created_caso = caso_completo
                
                created += 1
                medico_txt = medico_solicitante if medico_solicitante else 'sin médico'
                reciente_txt = "RECIENTE" if es_caso_reciente else "ANTIGUO"
                entrega_txt = fecha_entrega.strftime('%d/%m/%Y') if fecha_entrega else 'SIN ENTREGA'
                print(f"[OK] Caso {reciente_txt} creado: {caso_code_generado} - estado={estado_final.value}, entrega={entrega_txt}, médico={medico_txt}")
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
                print(f"  {estado.value}: {cantidad} ({porcentaje:.1f}%)")
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
    parser = argparse.ArgumentParser(description="Seed casos con muestras y pruebas reales")
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

    created, skipped = asyncio.run(
        seed_cases(count=count, year=args.year, start_number=args.start_number, dry_run=args.dry_run)
    )
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


