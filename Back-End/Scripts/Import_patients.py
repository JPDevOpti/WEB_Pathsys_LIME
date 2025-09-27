#!/usr/bin/env python3
"""
Script to generate test patients for the system

This script creates patients with random but realistic data for testing.
Patients include names, ages, gender, health entity and care type.
Data is marked as test data for easy identification.

Usage:
    python3 Scripts/Import_patients.py [--count N] [--dry-run]

Arguments:
    --count N: Number of patients to generate
    --dry-run: Only show what would be done without executing real changes
"""

import sys
import os
import asyncio
import argparse
import random
from datetime import datetime, timedelta
from typing import List, Tuple, Dict

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database, close_mongo_connection
from app.modules.entities.services.entity_service import get_entity_service
from app.modules.patients.services.patient_service import get_patient_service
from app.modules.patients.schemas.patient import PatientCreate, Gender, CareType, EntityInfo


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


def random_name(gender: Gender) -> str:
    first = random.choice(FIRST_NAMES_M if gender == Gender.MASCULINO else FIRST_NAMES_F)
    last = f"{random.choice(LAST_NAMES)} {random.choice(LAST_NAMES)}"
    return f"{first} {last}"


def random_patient_code(existing: set) -> str:
    while True:
        length = random.randint(6, 12)
        code = "".join(random.choices("0123456789", k=length))
        if code not in existing:
            existing.add(code)
            return code


def random_date_from_january_to_today() -> datetime:
    """Generate a random date from January 1st of current year to today"""
    today = datetime.now()
    start = datetime(today.year, 1, 1)
    
    # Calculate days from January to today
    delta_days = (today - start).days
    
    # Generate random days (including 0 for the first day)
    rand_days = random.randint(0, max(0, delta_days))
    
    # Generate random hour, minute and second
    rand_hours = random.randint(0, 23)
    rand_minutes = random.randint(0, 59)
    rand_seconds = random.randint(0, 59)
    
    # Create random date
    random_date = start + timedelta(
        days=rand_days,
        hours=rand_hours,
        minutes=rand_minutes,
        seconds=rand_seconds
    )
    
    return random_date


async def seed_patients(count: int, dry_run: bool) -> Tuple[int, int]:
    """Generate test patients with random data. Returns (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0

    print(f"{'='*60}")
    print("TEST PATIENTS GENERATION")
    print(f"{'='*60}")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
    print(f"Total patients to generate: {count}")
    print(f"{'='*60}")

    # Connect and get entities
    db = await get_database()
    try:
        entity_service = get_entity_service(db)
        patient_service = get_patient_service(db)

        # Get all entities from the database
        print("Getting available entities...")
        from app.modules.entities.schemas.entity import EntitySearch
        search_params = EntitySearch(skip=0, limit=100)  # Cargar hasta 100 entidades
        entities = await entity_service.list_all(search_params)
        
        # Convertir entidades para usar códigos como IDs
        entities_list = []
        for entity in entities:
            entity_dict = entity.model_dump() if hasattr(entity, "model_dump") else entity
            entity_code = entity_dict.get("entity_code") or entity_dict.get("code")
            entity_name = entity_dict.get("name") or entity_dict.get("entity_name")
            entities_list.append({
                "id": entity_code,
                "name": entity_name,
                "entity_code": entity_code,
                "entity_name": entity_name
            })
        
        if not entities_list:
            print("[ERROR] No entities found. Aborting.")
            return 0, count

        print(f"Available entities: {len(entities_list)}")
        print("All entities will be used for patient generation")
        print(f"{'='*60}")

        existing_codes: set = set()
        
        # Estadísticas de distribución por entidad
        entity_stats = {entity["name"]: 0 for entity in entities_list}

        for i in range(count):
            print(f"\n[{i+1}/{count}] Generating patient...")
            
            try:
                # Generate random data
                gender = random.choice([Gender.MASCULINO, Gender.FEMENINO])
                name = random_name(gender)
                age = random.randint(0, 95)
                care_type = random.choice([CareType.AMBULATORIO, CareType.HOSPITALIZADO])
                entity = random.choice(entities_list)
                
                # Create entity_info structure according to the schema
                entity_info = EntityInfo(
                    id=entity["id"],  # Usar el código
                    name=entity["name"]  # Usar el nombre
                )
                
                # Generate unique code
                patient_code = random_patient_code(existing_codes)

                # Create payload using validation schema
                payload = PatientCreate(
                    name=name,
                    age=age,
                    gender=gender,
                    entity_info=entity_info,
                    care_type=care_type,
                    observations="Test data generated automatically (uniform distribution)",
                    patient_code=patient_code,
                )

                if dry_run:
                    print(f"  [DRY-RUN] Would create patient:")
                    print(f"    - Code: {patient_code}")
                    print(f"    - Name: {name}")
                    print(f"    - Gender: {gender.value}")
                    print(f"    - Age: {age} years")
                    print(f"    - Entity: {entity_info.name}")
                    print(f"    - Care Type: {care_type.value}")
                    entity_stats[entity_info.name] += 1
                    created += 1
                    continue

                # Create real patient
                created_patient = await patient_service.create_patient(payload)
                
                # Generate random date from January to today
                rnd_date = random_date_from_january_to_today()
                
                # Update dates in the created document
                # Use the patient collection directly to update dates
                update_result = await db.patients.update_one(
                    {"_id": created_patient.id},
                    {"$set": {"created_at": rnd_date, "updated_at": rnd_date}}
                )
                
                if update_result.modified_count == 0:
                    print(f"  [WARNING] Could not update date for patient {created_patient.id}")
                
                # Verify that the date was updated correctly
                updated_doc = await db.patients.find_one({"_id": created_patient.id})
                if updated_doc and updated_doc.get("created_at"):
                    actual_date = updated_doc["created_at"]
                    print(f"  [OK] Date verified: {actual_date.strftime('%Y-%m-%d %H:%M:%S')}")
                else:
                    print(f"  [WARNING] Could not verify patient date")
                
                # Update statistics
                entity_stats[entity_info.name] += 1
                
                print(f"  [OK] Patient created successfully:")
                print(f"    - ID: {created_patient.id}")
                print(f"    - Code: {patient_code}")
                print(f"    - Name: {name}")
                print(f"    - Entity: {entity_info.name}")
                print(f"    - Date: {rnd_date.strftime('%Y-%m-%d')}")
                created += 1

            except ValueError as e:
                print(f"  [SKIP] Validation error: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Unexpected error: {str(e)}")
                errors += 1

        # Show entity distribution statistics
        if created > 0:
            print(f"\n{'='*60}")
            print("ENTITY DISTRIBUTION STATISTICS")
            print(f"{'='*60}")
            
            print("Patients created per entity:")
            for entity_name, count in sorted(entity_stats.items(), key=lambda x: x[1], reverse=True):
                if count > 0:
                    percentage = (count / created) * 100
                    print(f"  {entity_name:<50} : {count:>4} patients ({percentage:>5.1f}%)")
        
        # Show date distribution statistics
        if not dry_run and created > 0:
            print(f"\n{'='*60}")
            print("DATE DISTRIBUTION STATISTICS")
            print(f"{'='*60}")
            
            # Get all patients created in this session
            all_patients = await db.patients.find({
                "observations": "Test data generated automatically (uniform distribution)"
            }).to_list(length=None)
            
            if all_patients:
                # Count by month
                monthly_counts = {}
                for patient in all_patients:
                    if patient.get("created_at"):
                        month_key = patient["created_at"].strftime("%Y-%m")
                        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                print("Distribution by month:")
                for month in sorted(monthly_counts.keys()):
                    count = monthly_counts[month]
                    print(f"  {month}: {count} patients")
                
                # Show date range
                dates = [p.get("created_at") for p in all_patients if p.get("created_at")]
                if dates:
                    min_date = min(dates)
                    max_date = max(dates)
                    print(f"\nDate range:")
                    print(f"  From: {min_date.strftime('%Y-%m-%d')}")
                    print(f"  To: {max_date.strftime('%Y-%m-%d')}")
        
        # Final summary
        print(f"\n{'='*60}")
        print("GENERATION SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {count}")
        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")

        if dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made to the database")
            print(f"To execute for real, run the script without --dry-run")
        else:
            print(f"\n✅ Generation completed with UNIFORM distribution across ALL entities")

        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Generate test patients with random data",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/Import_patients.py --count 10 --dry-run    # Only show what would be done
  python3 Scripts/Import_patients.py --count 10              # Generate 10 patients
  python3 Scripts/Import_patients.py                         # Ask for quantity
        """
    )
    
    parser.add_argument(
        "--count",
        type=int,
        help="Number of patients to generate"
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()

    # Get patient quantity
    if args.count is None:
        try:
            user_input = input("How many patients do you want to generate? ").strip()
            count = int(user_input)
            if count <= 0:
                print("Quantity must be greater than 0")
                sys.exit(1)
        except ValueError:
            print("Invalid input. Must be an integer.")
            sys.exit(1)
        except KeyboardInterrupt:
            print("\nOperation cancelled by user")
            sys.exit(0)
    else:
        count = args.count

    # Execute generation
    try:
        created, skipped = asyncio.run(seed_patients(count=count, dry_run=args.dry_run))
        print(f"\n✅ Completed. Created: {created}, Skipped: {skipped}")
    except KeyboardInterrupt:
        print("\n⚠️  Operation cancelled by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n❌ Unexpected error: {str(e)}")
        sys.exit(1)


if __name__ == "__main__":
    main()
