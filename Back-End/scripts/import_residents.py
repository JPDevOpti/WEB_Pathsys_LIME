import os
import sys
from pathlib import Path
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict

# Ensure 'app' package is importable when running this script directly
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.residentes.repositories.residente_repository import ResidenteRepository
from app.modules.residentes.services.residente_service import ResidenteService
from app.modules.residentes.schemas.residente import ResidenteCreate
from app.shared.services.user_management import UserManagementService


def derive_initials(raw_initials: Optional[str], raw_name: str) -> str:
    if raw_initials and str(raw_initials).strip():
        return str(raw_initials).strip().upper()
    parts = [p for p in str(raw_name).strip().split() if p]
    return ("".join(p[0] for p in parts)[:4]).upper() if parts else "XX"


def compose_email(code: str, initials: str) -> str:
    # Format: numero.iniciales@udea.edu.co
    return f"{code}.{(initials or '').lower()}@udea.edu.co"


# Embedded list of Residents provided (sheet: Residentes)
RESIDENTS_LIST: List[Dict[str, str]] = [
    {"raw_code": "1152202153", "raw_name": "María Carolina Aguilar Arango", "raw_siglas": "MCA"},
    {"raw_code": "1128457685", "raw_name": "Oscar Mauricio Yepes Grajales", "raw_siglas": "OMY"},
    {"raw_code": "1040747654", "raw_name": "Santiago Alzate Giraldo", "raw_siglas": "SAG"},
    {"raw_code": "1052970426", "raw_name": "Juan Armando Guzmán Mendoza", "raw_siglas": "JAM"},
    {"raw_code": "1037575729", "raw_name": "Juan Ricardo Cadavid Castrillón", "raw_siglas": "RCC"},
    {"raw_code": "1037655805", "raw_name": "Juan Camilo López Bedoya", "raw_siglas": "CLB"},
    {"raw_code": "1152200744", "raw_name": "José Fernando Rojas Agudelo", "raw_siglas": "FRA"},
    {"raw_code": "8164627", "raw_name": "Juan David Cuartas Ramírez", "raw_siglas": "JDC"},
    {"raw_code": "1152683958", "raw_name": "John Camilo Ochoa Hernández", "raw_siglas": "COH"},
    {"raw_code": "98644128", "raw_name": "Juan Diego Baena Morales", "raw_siglas": "DBM"},
    {"raw_code": "10782378", "raw_name": "Miguel Ángel Guevara Casadiego", "raw_siglas": "AGC"},
    {"raw_code": "1144089415", "raw_name": "Laura Lucía Gallego Gallón", "raw_siglas": "LLG"},
    {"raw_code": "1085325220", "raw_name": "Germán Dario Zamudio Burbano", "raw_siglas": "GDZ"},
    {"raw_code": "1090441696", "raw_name": "Jesús David Díaz Mosquera", "raw_siglas": "JDM"},
    {"raw_code": "1148205818", "raw_name": "Manuela Ocampo Medina", "raw_siglas": "MOM"},
    {"raw_code": "71276707", "raw_name": "Carlos Hernán Posada Rendón", "raw_siglas": "CPR"},
]


async def import_residents(dry_run: bool) -> Tuple[int, int]:
    """Import embedded residents list. Returns (created, skipped)."""
    created = 0
    skipped = 0

    # Dry run: do not connect to DB
    if dry_run:
        for row in RESIDENTS_LIST:
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")
            if not raw_code or not raw_name:
                skipped += 1
                continue
            initials = derive_initials(raw_siglas, raw_name)
            email = compose_email(raw_code, initials)
            registro_medico = f"PEND-{raw_code}"
            print(f"[DRY-RUN] {raw_name} ({raw_code}) -> email={email} password=<doc> registro_medico='{registro_medico}' observaciones=None")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = ResidenteRepository(db)
        user_service = UserManagementService(db)
        service = ResidenteService(repo, user_service)

        for row in RESIDENTS_LIST:
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")

            if not raw_code or not raw_name:
                skipped += 1
                continue

            initials = derive_initials(raw_siglas, raw_name)
            email = compose_email(raw_code, initials)
            registro_medico = f"PEND-{raw_code}"  # Respect min_length and uniqueness intent

            payload = ResidenteCreate(
                residenteName=raw_name,
                InicialesResidente=initials,
                residenteCode=raw_code,
                ResidenteEmail=email,
                registro_medico=registro_medico,
                password=raw_code,  # Password equals document number
                isActive=True,
                observaciones=None,
            )

            try:
                await service.create_residente(payload)
                created += 1
                print(f"[OK] Residente creado: {raw_name} ({raw_code})")
            except Exception as e:
                skipped += 1
                print(f"[SKIP] {raw_name} ({raw_code}) -> {e}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Import residents from embedded list")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB, just preview")
    args = parser.parse_args()

    created, skipped = asyncio.run(import_residents(dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


