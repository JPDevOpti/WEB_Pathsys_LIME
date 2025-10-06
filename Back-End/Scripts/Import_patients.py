#!/usr/bin/env python3
"""
Script to generate test patients for the system

This script creates patients with random but realistic data for testing.
Patients include complete identification, names, birth date, gender, location, health entity and care type.
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
from datetime import datetime, timedelta, date
from typing import List, Tuple, Dict, Optional

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database, close_mongo_connection
from app.modules.entities.services.entity_service import get_entity_service
from app.modules.patients.services.patient_service import get_patient_service
from app.modules.patients.schemas.patient import PatientCreate, Gender, CareType, EntityInfo, IdentificationType, Location


# ============================================================================
# DATOS BASE PARA GENERACIÓN
# ============================================================================

FIRST_NAMES_M = [
    "Juan", "Carlos", "Luis", "Andrés", "Miguel", "Jorge", "Felipe", "Santiago", "David", "Ricardo",
    "Alejandro", "Sebastián", "Fernando", "Héctor", "Mauricio", "Nicolás", "Pablo", "Raúl", "Iván", "Óscar",
    "Adrián", "Alfredo", "Benjamín", "Bruno", "César", "Cristian", "Diego", "Emilio", "Esteban", "Gabriel",
    "Gonzalo", "Guillermo", "Hernán", "Hugo", "Jaime", "Julián", "Leonardo", "Manuel", "Marco", "Mario",
    "Martín", "Matías", "Patricio", "Rafael", "Rubén", "Samuel", "Simón", "Tomás", "Vicente", "Xavier",
]

SECOND_NAMES_M = [
    "José", "Antonio", "Manuel", "Francisco", "Javier", "Enrique", "Alberto", "Eduardo", "Roberto", "Armando",
    "Augusto", "Camilo", "Daniel", "Ernesto", "Fabián", "Germán", "Ignacio", "León", "Orlando", "Pedro",
]

FIRST_NAMES_F = [
    "María", "Laura", "Ana", "Carolina", "Camila", "Luisa", "Daniela", "Valentina", "Juliana", "Sofía",
    "Isabella", "Gabriela", "Natalia", "Paula", "Sara", "Mariana", "Alejandra", "Elena", "Lucía", "Verónica",
    "Adriana", "Amalia", "Beatriz", "Catalina", "Claudia", "Diana", "Estefanía", "Eva", "Fernanda", "Florencia",
    "Inés", "Irene", "Josefina", "Karina", "Liliana", "Lorena", "Magdalena", "Noelia", "Patricia", "Raquel",
    "Rocío", "Romina", "Silvia", "Teresa", "Vanessa", "Violeta", "Ximena", "Yolanda", "Zulema", "Mónica",
]

SECOND_NAMES_F = [
    "Isabel", "Cristina", "Alejandra", "Andrea", "Fernanda", "Victoria", "Esperanza", "Mercedes", "Angélica", "Beatriz",
    "Cecilia", "Dolores", "Eugenia", "Gladys", "Helena", "Inés", "Jimena", "Leticia", "Mercedes", "Noemí",
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

# Municipios de Antioquia con códigos DIVIPOLA reales
MUNICIPALITIES_ANTIOQUIA = [
    {"code": "05001", "name": "Medellín", "subregion": "Valle de Aburrá"},
    {"code": "05002", "name": "Abejorral", "subregion": "Oriente"},
    {"code": "05004", "name": "Abriaquí", "subregion": "Occidente"},
    {"code": "05021", "name": "Alejandría", "subregion": "Oriente"},
    {"code": "05030", "name": "Amagá", "subregion": "Suroeste"},
    {"code": "05031", "name": "Amalfi", "subregion": "Nordeste"},
    {"code": "05034", "name": "Andes", "subregion": "Suroeste"},
    {"code": "05036", "name": "Angelópolis", "subregion": "Suroeste"},
    {"code": "05038", "name": "Angostura", "subregion": "Norte"},
    {"code": "05040", "name": "Anorí", "subregion": "Nordeste"},
    {"code": "05044", "name": "Anza", "subregion": "Norte"},
    {"code": "05045", "name": "Apartadó", "subregion": "Urabá"},
    {"code": "05051", "name": "Arboletes", "subregion": "Urabá"},
    {"code": "05055", "name": "Argelia", "subregion": "Suroeste"},
    {"code": "05059", "name": "Armenia", "subregion": "Suroeste"},
    {"code": "05079", "name": "Barbosa", "subregion": "Valle de Aburrá"},
    {"code": "05086", "name": "Bello", "subregion": "Valle de Aburrá"},
    {"code": "05088", "name": "Belmira", "subregion": "Norte"},
    {"code": "05091", "name": "Betania", "subregion": "Suroeste"},
    {"code": "05093", "name": "Betulia", "subregion": "Suroeste"},
    {"code": "05101", "name": "Ciudad Bolívar", "subregion": "Suroeste"},
    {"code": "05107", "name": "Briceño", "subregion": "Norte"},
    {"code": "05113", "name": "Buriticá", "subregion": "Occidente"},
    {"code": "05120", "name": "Cáceres", "subregion": "Bajo Cauca"},
    {"code": "05125", "name": "Caicedo", "subregion": "Suroeste"},
    {"code": "05129", "name": "Caldas", "subregion": "Valle de Aburrá"},
    {"code": "05134", "name": "Campamento", "subregion": "Norte"},
    {"code": "05138", "name": "Cañasgordas", "subregion": "Occidente"},
    {"code": "05142", "name": "Caracolí", "subregion": "Magdalena Medio"},
    {"code": "05145", "name": "Caramanta", "subregion": "Suroeste"},
    {"code": "05147", "name": "Carepa", "subregion": "Urabá"},
    {"code": "05148", "name": "Carmen de Viboral", "subregion": "Oriente"},
    {"code": "05150", "name": "Carolina", "subregion": "Nordeste"},
    {"code": "05154", "name": "Caucasia", "subregion": "Bajo Cauca"},
    {"code": "05172", "name": "Chigorodó", "subregion": "Urabá"},
    {"code": "05190", "name": "Cisneros", "subregion": "Nordeste"},
    {"code": "05197", "name": "Cocorná", "subregion": "Oriente"},
    {"code": "05206", "name": "Concepción", "subregion": "Oriente"},
    {"code": "05209", "name": "Concordia", "subregion": "Suroeste"},
    {"code": "05212", "name": "Copacabana", "subregion": "Valle de Aburrá"},
    {"code": "05234", "name": "Dabeiba", "subregion": "Occidente"},
    {"code": "05237", "name": "Don Matías", "subregion": "Norte"},
    {"code": "05240", "name": "Ebéjico", "subregion": "Occidente"},
    {"code": "05250", "name": "El Bagre", "subregion": "Bajo Cauca"},
    {"code": "05264", "name": "Entrerríos", "subregion": "Norte"},
    {"code": "05266", "name": "Envigado", "subregion": "Valle de Aburrá"},
    {"code": "05282", "name": "Fredonia", "subregion": "Suroeste"},
    {"code": "05284", "name": "Frontino", "subregion": "Occidente"},
    {"code": "05306", "name": "Giraldo", "subregion": "Occidente"},
    {"code": "05308", "name": "Girardota", "subregion": "Valle de Aburrá"},
    {"code": "05310", "name": "Gómez Plata", "subregion": "Norte"},
    {"code": "05313", "name": "Granada", "subregion": "Oriente"},
    {"code": "05315", "name": "Guadalupe", "subregion": "Norte"},
    {"code": "05318", "name": "Guarne", "subregion": "Oriente"},
    {"code": "05321", "name": "Guatapé", "subregion": "Oriente"},
    {"code": "05347", "name": "Heliconia", "subregion": "Occidente"},
    {"code": "05353", "name": "Hispania", "subregion": "Suroeste"},
    {"code": "05360", "name": "Itagüí", "subregion": "Valle de Aburrá"},
    {"code": "05361", "name": "Ituango", "subregion": "Norte"},
    {"code": "05364", "name": "Jardín", "subregion": "Suroeste"},
    {"code": "05368", "name": "Jericó", "subregion": "Suroeste"},
    {"code": "05376", "name": "La Ceja", "subregion": "Oriente"},
    {"code": "05380", "name": "La Estrella", "subregion": "Valle de Aburrá"},
    {"code": "05390", "name": "La Pintada", "subregion": "Suroeste"},
    {"code": "05400", "name": "La Unión", "subregion": "Oriente"},
    {"code": "05411", "name": "Liborina", "subregion": "Occidente"},
    {"code": "05425", "name": "Maceo", "subregion": "Magdalena Medio"},
    {"code": "05440", "name": "Marinilla", "subregion": "Oriente"},
    {"code": "05467", "name": "Montebello", "subregion": "Suroeste"},
    {"code": "05475", "name": "Murindó", "subregion": "Urabá"},
    {"code": "05480", "name": "Mutatá", "subregion": "Urabá"},
    {"code": "05483", "name": "Nariño", "subregion": "Oriente"},
    {"code": "05490", "name": "Necoclí", "subregion": "Urabá"},
    {"code": "05495", "name": "Nechí", "subregion": "Bajo Cauca"},
    {"code": "05501", "name": "Olaya", "subregion": "Occidente"},
    {"code": "05541", "name": "Peñol", "subregion": "Oriente"},
    {"code": "05543", "name": "Peque", "subregion": "Occidente"},
    {"code": "05576", "name": "Pueblorrico", "subregion": "Suroeste"},
    {"code": "05579", "name": "Puerto Berrío", "subregion": "Magdalena Medio"},
    {"code": "05585", "name": "Puerto Nare", "subregion": "Magdalena Medio"},
    {"code": "05591", "name": "Puerto Triunfo", "subregion": "Magdalena Medio"},
    {"code": "05604", "name": "Remedios", "subregion": "Nordeste"},
    {"code": "05607", "name": "Retiro", "subregion": "Oriente"},
    {"code": "05615", "name": "Rionegro", "subregion": "Oriente"},
    {"code": "05628", "name": "Sabanalarga", "subregion": "Norte"},
    {"code": "05631", "name": "Sabaneta", "subregion": "Valle de Aburrá"},
    {"code": "05642", "name": "Salgar", "subregion": "Suroeste"},
    {"code": "05647", "name": "San Andrés de Cuerquia", "subregion": "Norte"},
    {"code": "05649", "name": "San Carlos", "subregion": "Oriente"},
    {"code": "05652", "name": "San Francisco", "subregion": "Oriente"},
    {"code": "05656", "name": "San Jerónimo", "subregion": "Occidente"},
    {"code": "05658", "name": "San José de La Montaña", "subregion": "Norte"},
    {"code": "05659", "name": "San Juan de Urabá", "subregion": "Urabá"},
    {"code": "05660", "name": "San Luis", "subregion": "Oriente"},
    {"code": "05664", "name": "San Pedro de Urabá", "subregion": "Urabá"},
    {"code": "05665", "name": "San Pedro de los Milagros", "subregion": "Norte"},
    {"code": "05667", "name": "San Rafael", "subregion": "Oriente"},
    {"code": "05670", "name": "San Roque", "subregion": "Nordeste"},
    {"code": "05674", "name": "San Vicente", "subregion": "Oriente"},
    {"code": "05679", "name": "Santa Bárbara", "subregion": "Suroeste"},
    {"code": "05686", "name": "Santa Rosa de Osos", "subregion": "Norte"},
    {"code": "05690", "name": "Santo Domingo", "subregion": "Nordeste"},
    {"code": "05697", "name": "El Santuario", "subregion": "Oriente"},
    {"code": "05736", "name": "Segovia", "subregion": "Nordeste"},
    {"code": "05756", "name": "Sonsón", "subregion": "Oriente"},
    {"code": "05761", "name": "Sopetrán", "subregion": "Occidente"},
    {"code": "05789", "name": "Támesis", "subregion": "Suroeste"},
    {"code": "05790", "name": "Tarazá", "subregion": "Bajo Cauca"},
    {"code": "05792", "name": "Tarso", "subregion": "Suroeste"},
    {"code": "05809", "name": "Titiribí", "subregion": "Suroeste"},
    {"code": "05819", "name": "Toledo", "subregion": "Norte"},
    {"code": "05837", "name": "Turbo", "subregion": "Urabá"},
    {"code": "05842", "name": "Uramita", "subregion": "Occidente"},
    {"code": "05847", "name": "Urrao", "subregion": "Suroeste"},
    {"code": "05854", "name": "Valdivia", "subregion": "Norte"},
    {"code": "05856", "name": "Valparaíso", "subregion": "Suroeste"},
    {"code": "05858", "name": "Vegachí", "subregion": "Nordeste"},
    {"code": "05861", "name": "Venecia", "subregion": "Suroeste"},
    {"code": "05873", "name": "Vigía del Fuerte", "subregion": "Urabá"},
    {"code": "05885", "name": "Yalí", "subregion": "Nordeste"},
    {"code": "05887", "name": "Yarumal", "subregion": "Norte"},
    {"code": "05890", "name": "Yolombó", "subregion": "Nordeste"},
    {"code": "05893", "name": "Yondó", "subregion": "Magdalena Medio"},
    {"code": "05895", "name": "Zaragoza", "subregion": "Bajo Cauca"},
]

# Tipos de vías comunes en Colombia
STREET_TYPES = ["Calle", "Carrera", "Avenida", "Diagonal", "Transversal", "Circular"]


# ============================================================================
# FUNCIONES DE GENERACIÓN DE DATOS ALEATORIOS
# ============================================================================

def random_identification_type() -> IdentificationType:
    """Generate random identification type with realistic distribution"""
    # 85% Cédula de Ciudadanía, 5% Tarjeta de Identidad, 3% Registro Civil, resto otros
    weights = [85, 2, 5, 1, 3, 1, 1, 1, 1]  # Total = 100
    types = list(IdentificationType)
    return random.choices(types, weights=weights)[0]


def random_identification_number() -> str:
    """Generate random identification number (6-12 digits)"""
    length = random.choices([8, 9, 10], weights=[20, 60, 20])[0]  # Mayoría 9-10 dígitos
    # Evitar que empiece con 0
    first_digit = random.randint(1, 9)
    remaining_digits = ''.join([str(random.randint(0, 9)) for _ in range(length - 1)])
    return str(first_digit) + remaining_digits


def random_first_name(gender: Gender) -> str:
    """Generate random first name based on gender"""
    if gender == Gender.MASCULINO:
        return random.choice(FIRST_NAMES_M)
    else:
        return random.choice(FIRST_NAMES_F)


def random_second_name(gender: Gender) -> Optional[str]:
    """Generate random second name (50% probability)"""
    if random.random() < 0.5:  # 50% probabilidad de tener segundo nombre
        if gender == Gender.MASCULINO:
            return random.choice(SECOND_NAMES_M)
        else:
            return random.choice(SECOND_NAMES_F)
    return None


def random_lastname() -> str:
    """Generate random lastname"""
    return random.choice(LAST_NAMES)


def random_birth_date() -> date:
    """Generate random birth date (0-95 years old) with realistic age distribution"""
    # Distribución más realista de edades (campana gaussiana)
    # Media 40 años, desviación estándar 20
    age = int(random.gauss(40, 20))
    age = max(0, min(95, age))  # Limitar entre 0 y 95 años
    
    today = date.today()
    birth_year = today.year - age
    
    # Mes y día aleatorios
    birth_month = random.randint(1, 12)
    
    # Días válidos según el mes
    days_in_month = {
        1: 31, 2: 28, 3: 31, 4: 30, 5: 31, 6: 30,
        7: 31, 8: 31, 9: 30, 10: 31, 11: 30, 12: 31
    }
    
    # Ajustar febrero en años bisiestos
    if birth_month == 2 and (birth_year % 4 == 0 and (birth_year % 100 != 0 or birth_year % 400 == 0)):
        days_in_month[2] = 29
    
    birth_day = random.randint(1, days_in_month[birth_month])
    
    return date(birth_year, birth_month, birth_day)


def random_location() -> Location:
    """Generate random location from Antioquia municipalities"""
    municipality = random.choice(MUNICIPALITIES_ANTIOQUIA)
    
    # Generar dirección realista colombiana
    street_type = random.choice(STREET_TYPES)
    street_number = random.randint(10, 99)
    cross_number = random.randint(10, 99)
    house_number = random.randint(1, 199)
    
    address = f"{street_type} {street_number} # {cross_number}-{house_number}"
    
    # Agregar complemento opcional (30% probabilidad)
    if random.random() < 0.3:
        complements = ["Apto", "Casa", "Local", "Oficina", "Interior"]
        complement_number = random.randint(1, 50)
        address += f" {random.choice(complements)} {complement_number}"
    
    return Location(
        municipality_code=municipality["code"],
        municipality_name=municipality["name"],
        subregion=municipality["subregion"],
        address=address
    )


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


def calculate_age(birth_date: date) -> int:
    """Calculate age from birth date"""
    today = date.today()
    age = today.year - birth_date.year - ((today.month, today.day) < (birth_date.month, birth_date.day))
    return age


def format_full_name(first_name: str, second_name: Optional[str], first_lastname: str, second_lastname: Optional[str]) -> str:
    """Format full name from parts"""
    parts = [first_name]
    if second_name:
        parts.append(second_name)
    parts.append(first_lastname)
    if second_lastname:
        parts.append(second_lastname)
    return " ".join(parts)


# ============================================================================
# FUNCIÓN PRINCIPAL DE GENERACIÓN
# ============================================================================

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
        search_params = EntitySearch(skip=0, limit=100)
        entities = await entity_service.list_all(search_params)
        
        # Convert entities to use codes as IDs
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
        
        # Statistics tracking
        entity_stats = {entity["name"]: 0 for entity in entities_list}
        identification_type_stats: Dict[str, int] = {}
        gender_stats = {"Masculino": 0, "Femenino": 0}
        care_type_stats = {"Ambulatorio": 0, "Hospitalizado": 0}
        age_distribution = {"0-17": 0, "18-30": 0, "31-50": 0, "51-70": 0, "71+": 0}

        for i in range(count):
            print(f"\n[{i+1}/{count}] Generating patient...")
            
            try:
                # Generate random data
                gender = random.choice([Gender.MASCULINO, Gender.FEMENINO])
                identification_type = random_identification_type()
                identification_number = random_identification_number()
                
                # Generate names
                first_name = random_first_name(gender)
                second_name = random_second_name(gender)
                first_lastname = random_lastname()
                second_lastname = random_lastname() if random.random() < 0.7 else None  # 70% tienen segundo apellido
                
                # Generate birth date and calculate age
                birth_date = random_birth_date()
                age = calculate_age(birth_date)
                
                # Generate location
                location = random_location()
                
                # Select random entity
                entity = random.choice(entities_list)
                entity_info = EntityInfo(
                    id=entity["id"],
                    name=entity["name"]
                )
                
                # Generate care type
                care_type = random.choice([CareType.AMBULATORIO, CareType.HOSPITALIZADO])
                
                # Format full name for display
                full_name = format_full_name(first_name, second_name, first_lastname, second_lastname)

                # Create payload using validation schema
                payload = PatientCreate(
                    identification_type=identification_type,
                    identification_number=identification_number,
                    first_name=first_name,
                    second_name=second_name,
                    first_lastname=first_lastname,
                    second_lastname=second_lastname,
                    birth_date=birth_date,
                    gender=gender,
                    location=location,
                    entity_info=entity_info,
                    care_type=care_type,
                    observations="Test data generated automatically (uniform distribution)",
                )

                if dry_run:
                    print(f"  [DRY-RUN] Would create patient:")
                    print(f"    - Identification: {identification_type.name} {identification_number}")
                    print(f"    - Name: {full_name}")
                    print(f"    - Birth Date: {birth_date} (Age: {age} years)")
                    print(f"    - Gender: {gender.value}")
                    print(f"    - Location: {location.municipality_name}, {location.subregion}")
                    print(f"    - Address: {location.address}")
                    print(f"    - Entity: {entity_info.name}")
                    print(f"    - Care Type: {care_type.value}")
                    
                    # Update statistics
                    entity_stats[entity_info.name] += 1
                    id_type_name = identification_type.name
                    identification_type_stats[id_type_name] = identification_type_stats.get(id_type_name, 0) + 1
                    gender_stats[gender.value] += 1
                    care_type_stats[care_type.value] += 1
                    
                    # Age distribution
                    if age < 18:
                        age_distribution["0-17"] += 1
                    elif age < 31:
                        age_distribution["18-30"] += 1
                    elif age < 51:
                        age_distribution["31-50"] += 1
                    elif age < 71:
                        age_distribution["51-70"] += 1
                    else:
                        age_distribution["71+"] += 1
                    
                    created += 1
                    continue

                # Create real patient
                created_patient = await patient_service.create_patient(payload)
                
                # Generate random date from January to today
                rnd_date = random_date_from_january_to_today()
                
                # Update dates in the created document
                update_result = await db.patients.update_one(
                    {"_id": created_patient.id},
                    {"$set": {"created_at": rnd_date, "updated_at": rnd_date}}
                )
                
                if update_result.modified_count == 0:
                    print(f"  [WARNING] Could not update date for patient {created_patient.id}")
                
                # Update statistics
                entity_stats[entity_info.name] += 1
                id_type_name = identification_type.name
                identification_type_stats[id_type_name] = identification_type_stats.get(id_type_name, 0) + 1
                gender_stats[gender.value] += 1
                care_type_stats[care_type.value] += 1
                
                # Age distribution
                if age < 18:
                    age_distribution["0-17"] += 1
                elif age < 31:
                    age_distribution["18-30"] += 1
                elif age < 51:
                    age_distribution["31-50"] += 1
                elif age < 71:
                    age_distribution["51-70"] += 1
                else:
                    age_distribution["71+"] += 1
                
                print(f"  [OK] Patient created successfully:")
                print(f"    - ID: {created_patient.id}")
                print(f"    - Code: {created_patient.patient_code}")
                print(f"    - Name: {full_name}")
                print(f"    - Identification: {identification_type.name} {identification_number}")
                print(f"    - Birth Date: {birth_date} (Age: {age} years)")
                print(f"    - Location: {location.municipality_name}")
                print(f"    - Entity: {entity_info.name}")
                print(f"    - Date: {rnd_date.strftime('%Y-%m-%d')}")
                created += 1

            except ValueError as e:
                print(f"  [SKIP] Validation error: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Unexpected error: {str(e)}")
                errors += 1

        # Show statistics
        if created > 0:
            print(f"\n{'='*60}")
            print("GENERATION STATISTICS")
            print(f"{'='*60}")
            
            # Entity distribution
            print("\n📊 PATIENTS BY ENTITY:")
            for entity_name, count_val in sorted(entity_stats.items(), key=lambda x: x[1], reverse=True):
                if count_val > 0:
                    percentage = (count_val / created) * 100
                    print(f"  {entity_name:<50} : {count_val:>4} ({percentage:>5.1f}%)")
            
            # Identification type distribution
            print("\n📊 PATIENTS BY IDENTIFICATION TYPE:")
            for id_type, count_val in sorted(identification_type_stats.items(), key=lambda x: x[1], reverse=True):
                percentage = (count_val / created) * 100
                print(f"  {id_type:<30} : {count_val:>4} ({percentage:>5.1f}%)")
            
            # Gender distribution
            print("\n📊 PATIENTS BY GENDER:")
            for gender_key, count_val in gender_stats.items():
                percentage = (count_val / created) * 100
                print(f"  {gender_key:<30} : {count_val:>4} ({percentage:>5.1f}%)")
            
            # Care type distribution
            print("\n📊 PATIENTS BY CARE TYPE:")
            for care_key, count_val in care_type_stats.items():
                percentage = (count_val / created) * 100
                print(f"  {care_key:<30} : {count_val:>4} ({percentage:>5.1f}%)")
            
            # Age distribution
            print("\n📊 PATIENTS BY AGE GROUP:")
            for age_range, count_val in age_distribution.items():
                percentage = (count_val / created) * 100
                print(f"  {age_range:<30} : {count_val:>4} ({percentage:>5.1f}%)")
        
        # Show date distribution statistics (only for real execution)
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
                monthly_counts: Dict[str, int] = {}
                for patient in all_patients:
                    if patient.get("created_at"):
                        month_key = patient["created_at"].strftime("%Y-%m")
                        monthly_counts[month_key] = monthly_counts.get(month_key, 0) + 1
                
                print("Distribution by month:")
                for month in sorted(monthly_counts.keys()):
                    count_val = monthly_counts[month]
                    print(f"  {month}: {count_val} patients")
                
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
