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
from app.modules.pacientes.repositories.repository import PacienteRepository
from app.modules.pacientes.models import PacienteCreate, Sexo, TipoAtencion


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
    today = datetime.now()
    start = datetime(today.year, 1, 1)
    delta_days = (today - start).days
    rand_days = random.randint(0, max(0, delta_days))
    rand_seconds = random.randint(0, 86399)
    return start + timedelta(days=rand_days, seconds=rand_seconds)


async def seed_patients(count: int, dry_run: bool) -> Tuple[int, int]:
    created = 0
    skipped = 0

    # Connect and fetch entities
    db = await connect_to_mongo()
    try:
        entidad_repo = EntidadRepository(db)
        paciente_repo = PacienteRepository(db)

        # Fetch all entities with pagination (limit <= 100 per schema)
        entidades: List[Dict] = []
        _skip = 0
        _limit = 100
        while True:
            page = await entidad_repo.get_all(
                search_params=EntidadSearch(activo=None, skip=_skip, limit=_limit)
            )
            if not page:
                break
            entidades.extend([p.model_dump() if hasattr(p, "model_dump") else p for p in page])
            if len(page) < _limit:
                break
            _skip += _limit
        if not entidades:
            print("[WARN] No entities found. Aborting.")
            return 0, count

        existing_cedulas: set = set()

        for _ in range(count):
            sexo = random.choice([Sexo.MASCULINO, Sexo.FEMENINO])
            nombre = random_name(sexo)
            edad = random.randint(0, 95)
            tipo = random.choice([TipoAtencion.AMBULATORIO, TipoAtencion.HOSPITALIZADO])
            entidad = random.choice(entidades)
            entidad_info = {"id": str(entidad.get("_id") or entidad.get("id")), "nombre": entidad["EntidadName"]}
            cedula = random_cedula(existing_cedulas)

            payload = PacienteCreate(
                nombre=nombre,
                edad=edad,
                sexo=sexo,
                entidad_info=entidad_info,
                tipo_atencion=tipo,
                observaciones=None,
                cedula=cedula,
            )

            if dry_run:
                created += 1
                print(f"[DRY-RUN] {cedula} -> {nombre}, {sexo.value}, {edad} años, entidad={entidad_info.nombre}, tipo={tipo.value}")
                continue

            try:
                created_doc = await paciente_repo.create(payload)
                # Update dates to a random date from Jan 1 to today
                rnd_date = random_date_from_january_to_today()
                await paciente_repo.collection.update_one(
                    {"_id": created_doc["id"]},
                    {"$set": {"fecha_creacion": rnd_date, "fecha_actualizacion": rnd_date}}
                )
                created += 1
                print(f"[OK] Paciente creado: {created_doc['id']} - {created_doc['nombre']}")
            except Exception as e:
                skipped += 1
                print(f"[SKIP] {cedula} -> {e}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Seed patients with realistic data from January to today")
    parser.add_argument("--count", type=int, help="How many patients to create")
    parser.add_argument("--dry-run", action="store_true", help="Preview without inserting")
    args = parser.parse_args()

    if args.count is None:
        try:
            user_input = input("¿Cuántos pacientes quieres generar? ").strip()
            count = int(user_input)
        except Exception:
            print("Entrada inválida. Usa --count N")
            sys.exit(1)
    else:
        count = args.count

    created, skipped = asyncio.run(seed_patients(count=count, dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


