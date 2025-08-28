#!/usr/bin/env python3
"""
Script para generar pacientes de prueba del sistema

Este script crea pacientes con datos aleatorios pero realistas para pruebas.
Los pacientes incluyen nombres, edades, sexo, entidad de salud y tipo de atención.
Los datos se marcan como de prueba para facilitar su identificación.

Uso:
    python3 scripts/seed_patients.py [--count N] [--dry-run]

Argumentos:
    --count N: Número de pacientes a generar
    --dry-run: Solo mostrar qué se haría sin ejecutar cambios reales
"""

import sys
from pathlib import Path
import asyncio
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
from app.modules.entidades.models.entidad import EntidadSearch
from app.modules.pacientes.repositories.paciente_repository import PacienteRepository
from app.modules.pacientes.schemas.paciente import PacienteCreate, Sexo, TipoAtencion


FIRST_NAMES_M = [
    "Juan", "Carlos", "Luis", "Andrés", "Miguel", "Jorge", "Felipe", "Santiago", "David", "Ricardo",
    "Alejandro", "Sebastián", "Fernando", "Héctor", "Mauricio", "Nicolás", "Pablo", "Raúl", "Iván", "Óscar",
    "Adrián", "Alfredo", "Benjamín", "Bruno", "César", "Cristian", "Diego", "Emilio", "Esteban", "Gabriel",
    "Gonzalo", "Guillermo", "Hernán", "Hugo", "Jaime", "Julián", "Leonardo", "Manuel", "Marco", "Mario",
    "Martín", "Matías", "Patricio", "Rafael", "Rubén", "Samuel", "Simón", "Tomás", "Vicente", "Xavier",
]
FIRST_NAMES_F = [
    "María", "Laura", "Ana", "Carolina", "Camila", "Luisa", "Daniela", "Valentina", "Juliana", "Sofía",
    "Isabella", "Gabriela", "Natalia", "Paula", "Sara", "Mariana", "Alejandra", "Elena", "Lucía", "Verónica",
    "Adriana", "Amalia", "Beatriz", "Catalina", "Claudia", "Diana", "Estefanía", "Eva", "Fernanda", "Florencia",
    "Inés", "Irene", "Josefina", "Karina", "Liliana", "Lorena", "Magdalena", "Noelia", "Patricia", "Raquel",
    "Rocío", "Romina", "Silvia", "Teresa", "Vanessa", "Violeta", "Ximena", "Yolanda", "Zulema", "Mónica",
]
LAST_NAMES = [
    "García", "López", "Martínez", "Gómez", "Rodríguez", "Hernández", "Pérez", "Sánchez", "Ramírez", "Torres",
    "Flores", "Acosta", "Aguilar", "Alvarez", "Arias", "Benítez", "Bermúdez", "Blanco", "Bravo", "Bustamante",
    "Cabrera", "Calderón", "Cano", "Cárdenas", "Castillo", "Castro", "Contreras", "Cortés", "Delgado", "Díaz",
    "Domínguez", "Escobar", "Espinosa", "Fajardo", "Figueroa", "Franco", "Fuentes", "Guerrero", "Guzmán", "Ibarra",
    "Jiménez", "León", "Luna", "Maldonado", "Medina", "Mejía", "Mendoza", "Molina", "Monroy", "Montoya",
    "Morales", "Navarro", "Navas", "Núñez", "Ortega", "Ortiz", "Osorio", "Palacios", "Patiño", "Peña",
    "Pineda", "Prieto", "Quintero", "Reyes", "Rincón", "Ríos", "Rivera", "Robles", "Rojas", "Salazar",
    "Salgado", "Serrano", "Suárez", "Tamayo", "Valencia", "Valenzuela", "Vargas", "Vega", "Vera", "Zamora",
]


def random_name(sexo: Sexo) -> str:
    first = random.choice(FIRST_NAMES_M if sexo == Sexo.MASCULINO else FIRST_NAMES_F)
    last = f"{random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"
    return f"{first} {last}"


def random_cedula(existing: set) -> str:
    while True:
        length = random.randint(6, 12)
        ced = "".join(random.choices("0123456789", k=length))
        if ced not in existing:
            existing.add(ced)
            return ced


def random_date_from_january_to_today() -> datetime:
    """Genera una fecha aleatoria desde el 1 de enero del año actual hasta hoy"""
    today = datetime.now()
    start = datetime(today.year, 1, 1)
    
    # Calcular días desde enero hasta hoy
    delta_days = (today - start).days
    
    # Generar días aleatorios (incluyendo 0 para el primer día)
    rand_days = random.randint(0, max(0, delta_days))
    
    # Generar hora, minuto y segundo aleatorios
    rand_hours = random.randint(0, 23)
    rand_minutes = random.randint(0, 59)
    rand_seconds = random.randint(0, 59)
    
    # Crear fecha aleatoria
    random_date = start + timedelta(
        days=rand_days,
        hours=rand_hours,
        minutes=rand_minutes,
        seconds=rand_seconds
    )
    
    return random_date


async def seed_patients(count: int, dry_run: bool) -> Tuple[int, int]:
    """Generar pacientes de prueba con datos aleatorios. Retorna (creados, saltados)."""
    created = 0
    skipped = 0
    errors = 0

    print(f"{'='*60}")
    print("GENERACIÓN DE PACIENTES DE PRUEBA")
    print(f"{'='*60}")
    print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
    print(f"Total pacientes a generar: {count}")
    print(f"{'='*60}")

    # Conectar y obtener entidades
    db = await connect_to_mongo()
    try:
        entidad_repo = EntidadRepository(db)
        paciente_repo = PacienteRepository(db)

        # Obtener todas las entidades directamente de la base de datos
        print("Obteniendo entidades disponibles...")
        entidades_cursor = db.entidades.find({}, {"_id": 1, "entidad_name": 1, "entidad_code": 1, "is_active": 1})
        entidades = await entidades_cursor.to_list(length=None)
        
        if not entidades:
            print("[ERROR] No se encontraron entidades. Abortando.")
            return 0, count

        print(f"Entidades disponibles: {len(entidades)}")
        print(f"{'='*60}")

        existing_cedulas: set = set()

        for i in range(count):
            print(f"\n[{i+1}/{count}] Generando paciente...")
            
            try:
                # Generar datos aleatorios
                sexo = random.choice([Sexo.MASCULINO, Sexo.FEMENINO])
                nombre = random_name(sexo)
                edad = random.randint(0, 95)
                tipo = random.choice([TipoAtencion.AMBULATORIO, TipoAtencion.HOSPITALIZADO])
                entidad = random.choice(entidades)
                
                # Validar estructura de entidad
                entidad_id = entidad.get("_id") or entidad.get("id")
                entidad_nombre = entidad.get("entidad_name") or entidad.get("EntidadName")
                
                if not entidad_id or not entidad_nombre:
                    print(f"  [SKIP] Entidad inválida: {entidad}")
                    skipped += 1
                    continue
                
                # Crear estructura de entidad_info según el esquema
                entidad_info = {
                    "id": str(entidad_id),
                    "nombre": entidad_nombre
                }
                
                # Generar código único
                paciente_code = random_cedula(existing_cedulas)

                # Crear payload usando el esquema de validación
                payload = PacienteCreate(
                    nombre=nombre,
                    edad=edad,
                    sexo=sexo,
                    entidad_info=entidad_info,
                    tipo_atencion=tipo,
                    observaciones="Datos de prueba generados automáticamente",
                    paciente_code=paciente_code,
                )

                if dry_run:
                    print(f"  [DRY-RUN] Se crearía paciente:")
                    print(f"    - Código: {paciente_code}")
                    print(f"    - Nombre: {nombre}")
                    print(f"    - Sexo: {sexo.value}")
                    print(f"    - Edad: {edad} años")
                    print(f"    - Entidad: {entidad_info['nombre']}")
                    print(f"    - Tipo: {tipo.value}")
                    created += 1
                    continue

                # Crear paciente real
                created_doc = await paciente_repo.create(payload)
                
                # Generar fecha aleatoria desde enero hasta hoy
                rnd_date = random_date_from_january_to_today()
                
                # Actualizar fechas en el documento creado
                # Usar _id en lugar de id para MongoDB
                update_result = await paciente_repo.collection.update_one(
                    {"_id": created_doc["_id"]},
                    {"$set": {"fecha_creacion": rnd_date, "fecha_actualizacion": rnd_date}}
                )
                
                if update_result.modified_count == 0:
                    print(f"  [WARNING] No se pudo actualizar la fecha del paciente {created_doc['_id']}")
                
                # Verificar que la fecha se actualizó correctamente
                updated_doc = await paciente_repo.collection.find_one({"_id": created_doc["_id"]})
                if updated_doc and updated_doc.get("fecha_creacion"):
                    actual_date = updated_doc["fecha_creacion"]
                    print(f"  [OK] Fecha verificada: {actual_date.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  [WARNING] No se pudo verificar la fecha del paciente")
                
                print(f"  [OK] Paciente creado exitosamente:")
                print(f"    - ID: {created_doc['_id']}")
                print(f"    - Código: {paciente_code}")
                print(f"    - Nombre: {nombre}")
                print(f"    - Fecha: {rnd_date.strftime('%Y-%m-%d')}")
                created += 1

            except ValueError as e:
                print(f"  [SKIP] Error de validación: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Error inesperado: {str(e)}")
                errors += 1

        # Mostrar estadísticas de distribución de fechas
        if not dry_run and created > 0:
            print(f"\n{'='*60}")
            print("ESTADÍSTICAS DE DISTRIBUCIÓN DE FECHAS")
            print(f"{'='*60}")
            
            # Obtener todos los pacientes creados en esta sesión
            all_patients = await paciente_repo.collection.find({
                "observaciones": "Datos de prueba generados automáticamente"
            }).to_list(length=None)
            
            if all_patients:
                # Contar por mes
                monthly_counts = {}
                for patient in all_patients:
                    if patient.get("fecha_creacion"):
                        month_key = patient["fecha_creacion"].strftime("%Y-%m")
                        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                print("Distribución por mes:")
                for month in sorted(monthly_counts.keys()):
                    count = monthly_counts[month]
                    print(f"  {month}: {count} pacientes")
                
                # Mostrar rango de fechas
                dates = [p.get("fecha_creacion") for p in all_patients if p.get("fecha_creacion")]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    print(f"\nRango de fechas:")
                    print(f"  Desde: {min_date.strftime('%Y-%m-%d')}")
                    print(f"  Hasta: {max_date.strftime('%Y-%m-%d')}")
        
        # Resumen final
        print(f"\n{'='*60}")
        print("RESUMEN DE GENERACIÓN")
        print(f"{'='*60}")
        print(f"Total procesados: {count}")
        print(f"Creados: {created}")
        print(f"Saltados: {skipped}")
        print(f"Errores: {errors}")

        if dry_run:
            print(f"\n⚠️  MODO DRY-RUN: No se realizaron cambios en la base de datos")
            print(f"Para ejecutar realmente, ejecuta el script sin --dry-run")
        else:
            print(f"\n✅ Generación completada")

        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Generar pacientes de prueba con datos aleatorios",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/seed_patients.py --count 10 --dry-run    # Solo mostrar qué se haría
  python3 scripts/seed_patients.py --count 10              # Generar 10 pacientes
  python3 scripts/seed_patients.py                         # Preguntar cantidad
        """
    )
    
    parser.add_argument(
        "--count",
        type=int,
        help="Número de pacientes a generar"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()

    # Obtener cantidad de pacientes
    if args.count is None:
        try:
            user_input = input("¿Cuántos pacientes quieres generar? ").strip()
            count = int(user_input)
            if count <= 0:
                print("La cantidad debe ser mayor a 0")
                sys.exit(1)
        except ValueError:
            print("Entrada inválida. Debe ser un número entero.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperación cancelada por el usuario")
            sys.exit(0)
    else:
        count = args.count

    # Ejecutar generación
    try:
        created, skipped = asyncio.run(seed_patients(count=count, dry_run=args.dry_run))
        print(f"\n✅ Completado. Creados: {created}, Saltados: {skipped}")
    except KeyboardInterrupt:
        print("\n⚠️  Operación cancelada por el usuario")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Error inesperado: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()


