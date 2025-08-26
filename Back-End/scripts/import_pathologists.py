import os
import sys
from pathlib import Path
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict

# Asegurar que el paquete 'app' sea importable al ejecutar el script directamente
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.patologos.repositories.patologo_repository import PatologoRepository
from app.modules.patologos.services.patologo_service import PatologoService
from app.modules.patologos.schemas.patologo import PatologoCreate
from app.shared.services.user_management import UserManagementService


def derive_initials(raw_initials: Optional[str], raw_name: str) -> str:
    if raw_initials and str(raw_initials).strip():
        return str(raw_initials).strip().upper()
    # Fallback: Tomar iniciales del nombre
    parts = [p for p in str(raw_name).strip().split() if p]
    return ("".join(p[0] for p in parts)[:4]).upper() if parts else "XX"


def compose_email(code: str, initials: str) -> str:
    # Formato requerido: "numero.iniciales@udea.edu.co"
    return f"{code}.{(initials or '').lower()}@udea.edu.co"


# Lista embebida de patólogos (Docentes) proporcionada
PATHOLOGISTS_DOCENTES: List[Dict[str, str]] = [
    {"raw_code": "32108690", "raw_name": "Leiby Alejandra Medina Zuluaica", "raw_siglas": "LAM"},
    {"raw_code": "71589374", "raw_name": "Juan Carlos Arango Viana", "raw_siglas": "JCA"},
    {"raw_code": "43617501", "raw_name": "Carolina López Urán", "raw_siglas": "CLU"},
    {"raw_code": "1129564009", "raw_name": "Vanessa Santiago Pacheco", "raw_siglas": "VSP"},
    {"raw_code": "32259741", "raw_name": "Alejandra Taborda Murillo", "raw_siglas": "ATM"},
    {"raw_code": "72257523", "raw_name": "Ariel Antonio Arteta Cueto", "raw_siglas": "AAA"},
    {"raw_code": "71666530", "raw_name": "Miguel Ignacio Roldán Pérez", "raw_siglas": "MRP"},
    {"raw_code": "30582655", "raw_name": "Dilia Rosa Díaz Macea", "raw_siglas": "DRD"},
    {"raw_code": "1144050050", "raw_name": "Luis Eduardo Muñoz Rayo", "raw_siglas": "LEM"},
    {"raw_code": "1017233614", "raw_name": "Janine Orejuela Erazo", "raw_siglas": "JOE"},
    {"raw_code": "10102849456", "raw_name": "Emil de Jesús Jiménez Berastegui", "raw_siglas": "EJB"},
    {"raw_code": "1036636079", "raw_name": "Julieth Alexandra Franco Mira", "raw_siglas": "JFM"},
    {"raw_code": "1130613519", "raw_name": "Andrés Lozano Camayo", "raw_siglas": "ALC"},
]


async def import_pathologists(
    dry_run: bool,
) -> Tuple[int, int]:
    """Importa la lista embebida de patólogos Docentes. Retorna (creados, saltados)."""
    created = 0
    skipped = 0

    # Modo dry-run: no conectamos a la BD
    if dry_run:
        for row in PATHOLOGISTS_DOCENTES:
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")
            if not raw_code or not raw_name:
                skipped += 1
                continue
            # Nota: el backend ahora permite hasta 11 caracteres para patologoCode
            initials = derive_initials(raw_siglas, raw_name)
            email = compose_email(raw_code, initials)
            registro_medico = f"PEND-{raw_code}"
            print(f"[DRY-RUN] {raw_name} ({raw_code}) -> email={email} password=<doc> registro_medico='{registro_medico}' observaciones=None")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = PatologoRepository(db)
        user_service = UserManagementService(db)
        service = PatologoService(repo, user_service)

        for row in PATHOLOGISTS_DOCENTES:
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")

            if not raw_code or not raw_name:
                skipped += 1
                continue
            # Nota: el backend ahora permite hasta 11 caracteres para patologoCode

            initials = derive_initials(raw_siglas, raw_name)
            email = compose_email(raw_code, initials)
            registro_medico = f"PEND-{raw_code}"  # Placeholder único para cumplir el esquema y evitar colisión

            payload = PatologoCreate(
                patologoName=raw_name,
                InicialesPatologo=initials,
                patologoCode=raw_code,
                PatologoEmail=email,
                registro_medico=registro_medico,
                password=raw_code,  # Contraseña igual al número de documento
                isActive=True,
                firma="",
                observaciones=None,
            )

            try:
                await service.create_patologo(payload)
                created += 1
                print(f"[OK] Patólogo creado: {raw_name} ({raw_code})")
            except Exception as e:
                skipped += 1
                print(f"[SKIP] {raw_name} ({raw_code}) -> {e}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Import pathologists (Docentes) from embedded list")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB, just preview")
    args = parser.parse_args()

    created, skipped = asyncio.run(import_pathologists(dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


