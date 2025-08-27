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
    {"code": "HSV001", "name": "Hospital Universitario San Vicente de Paul"},
    {"code": "HPTU", "name": "Hospital Pablo Tobón Uribe"},
    {"code": "HSCV003", "name": "Clínica Cardiovascular Santa María"},
    {"code": "PARTICULAR", "name": "Particular"},
    {"code": "AMB", "name": "Hospitales Ambulatorios"},
    {"code": "INV", "name": "Investigación"},
    {"code": "IPSA", "name": "IPS Universitaria Ambulatoria"},
    {"code": "VID", "name": "Clínica VID - Fundación Santa María"},
    {"code": "PROLAB", "name": "PROLAB S.A.S"},
    {"code": "SURA", "name": "SURA"},
    {"code": "DST", "name": "Patología Suescún S.A.S"},
    {"code": "PINTEGRAL", "name": "Patología Integral S.A"},
    {"code": "HSVR", "name": "Centros Especializados HSVF Rionegro"},
    {"code": "NEUROC", "name": "Neurocentro - Pereira"},
    {"code": "LEON XIII", "name": "Renales IPS Clínica León XIII"},
    {"code": "MICRO", "name": "Microbiología"},
    {"code": "SOMER", "name": "Clínica Somer"},
    {"code": "HGM", "name": "Hospital General de Medellín Luz Castro G."},
    {"code": "CES", "name": "Clínica CES"},
    {"code": "LIME", "name": "LIME"},
    {"code": "TEM", "name": "TEM - SIU"},
    {"code": "HAMA", "name": "Hospital Alma Máter de Antioquia"},
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


