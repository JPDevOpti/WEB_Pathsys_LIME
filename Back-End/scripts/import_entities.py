import sys
from pathlib import Path
import asyncio
import argparse
from typing import Dict, List, Tuple

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
from app.modules.entidades.models.entidad import EntidadCreate


def normalize_text(text: str) -> str:
    if text is None:
        return None
    return " ".join(str(text).split()).strip()


RAW_ENTITIES: List[Dict[str, str]] = [
    {"code": "HSV001", "name": "HOSPITAL UNIVERSITARIO SAN VICENTE DE PAUL"},
    {"code": "HPTU", "name": "HOSPITAL PABLO TOBON URIBE"},
    {"code": "HSCV003", "name": "CLINICA CARDIOVASCULAR SANTA MARIA"},
    {"code": "pARTICULAR", "name": "PARTICULAR"},
    {"code": "Amb", "name": "HOSPITALES AMBULATORIOS"},
    {"code": "INV", "name": "INVESTIGACION"},
    {"code": "IPSA", "name": "IPS UNIVERSITARIA AMBULATORIA"},
    {"code": "VID", "name": "CLINICA VID - FUNDACIÓN SANTA MARIA"},
    {"code": "PROLAB", "name": "PROLAB S.A.S"},
    {"code": "SURA", "name": "SURA"},
    {"code": "DST", "name": "PATOLOGIA SUESCUN S.A.S"},
    {"code": "PINTEGRAL", "name": "PATOLOGIA INTEGRAL S.A"},
    {"code": "HSVR", "name": "CENTROS ESPECIALIZADOS HSVF RIONEGRO"},
    {"code": "NEUROC", "name": "NEUROCENTRO - PEREIRA"},
    {"code": "LEÓN XIII", "name": "RENALES IPS CLINICA LEON XIII"},
    {"code": "MICRO", "name": "MICROBIOLOGIA"},
    {"code": "SOMER", "name": "CLÍNICA SOMER"},
    {"code": "HGM", "name": "HOSPITAL GENERAL DE MEDELLÍN LUZ CASTRO G."},
    {"code": "CES", "name": "CLÍNICA CES"},
    {"code": "LIME", "name": "LIME"},
    {"code": "TEM", "name": "TEM - SIU"},
    {"code": "HAMA", "name": "HOSPITAL ALMA MÁTER DE ANTIOQUIA"},
]


def dedupe_rows(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = normalize_text(row.get("code") or "")
        name = normalize_text(row.get("name") or "")
        if not name:
            continue
        if not code:
            # Skip rows without code due to schema requirement
            continue
        merged[code] = {"name": name}
    return merged


async def import_entities(dry_run: bool) -> Tuple[int, int]:
    created = 0
    skipped = 0
    merged = dedupe_rows(RAW_ENTITIES)

    if dry_run:
        for code, data in merged.items():
            print(f"[DRY-RUN] {code} -> name='{data['name']}', observaciones=None")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = EntidadRepository(db)
        for code, data in merged.items():
            payload = EntidadCreate(
                EntidadName=data["name"],
                EntidadCode=code,
                observaciones=None,
                isActive=True,
            )
            try:
                await repo.create(payload)
                print(f"[OK] Entidad creada: {code} - {data['name']}")
                created += 1
            except Exception as e:
                print(f"[SKIP] {code} - {data['name']} -> {e}")
                skipped += 1
        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Import entities from embedded list (observaciones empty)")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB, just preview")
    args = parser.parse_args()

    created, skipped = asyncio.run(import_entities(dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


