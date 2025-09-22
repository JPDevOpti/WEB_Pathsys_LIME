#!/usr/bin/env python3
"""
Script to insert system entities

This script creates entities in the database with the specified codes and names.
Entities include hospitals, clinics, laboratories and other health institutions.

Usage:
    python3 Scripts/import_entities_en.py [--dry-run]

Arguments:
    --dry-run: Only show what would be done without executing real changes
"""

import sys
import os
import asyncio
import argparse
from typing import Dict, List, Tuple
from datetime import datetime

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database, close_mongo_connection
from app.modules.entities.schemas.entity import EntityCreate
from app.modules.entities.services.entity_service import get_entity_service


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
    """Import embedded entities list. Returns (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0

    merged = dedupe_rows(RAW_ENTITIES)

    print(f"{'='*60}")
    print("ENTITY IMPORT")
    print(f"{'='*60}")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total entities to process: {len(merged)}")
    print(f"{'='*60}")

    # Dry run: do not connect to DB
    if dry_run:
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Processing: {code}")
            print(f"  Name: {data['name']}")
            
            # Previous validations
            if not code or not code.strip():
                print(f"  [SKIP] Empty or invalid code")
                skipped += 1
                continue
                
            if not data['name'] or not data['name'].strip():
                print(f"  [SKIP] Empty or invalid name")
                skipped += 1
                continue

            # Validate code length (1-20 characters)
            if len(code) < 1 or len(code) > 20:
                print(f"  [SKIP] Code must be between 1 and 20 characters, current: {len(code)}")
                skipped += 1
                continue

            # Validate name length (1-200 characters)
            if len(data['name']) < 1 or len(data['name']) > 200:
                print(f"  [SKIP] Name must be between 1 and 200 characters, current: {len(data['name'])}")
                skipped += 1
                continue
            
            print(f"  [DRY-RUN] Would create entity: {code}")
            print(f"    - Code: {code}")
            print(f"    - Name: {data['name']}")
            created += 1
        return created, skipped

    db = await get_database()
    try:
        service = get_entity_service(db)

        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Processing: {code}")
            print(f"  Name: {data['name']}")

            try:
                # Previous validations
                if not code or not code.strip():
                    print(f"  [SKIP] Empty or invalid code")
                    skipped += 1
                    continue
                    
                if not data['name'] or not data['name'].strip():
                    print(f"  [SKIP] Empty or invalid name")
                    skipped += 1
                    continue

                # Validate code length (1-20 characters)
                if len(code) < 1 or len(code) > 20:
                    print(f"  [SKIP] Code must be between 1 and 20 characters, current: {len(code)}")
                    skipped += 1
                    continue

                # Validate name length (1-200 characters)
                if len(data['name']) < 1 or len(data['name']) > 200:
                    print(f"  [SKIP] Name must be between 1 and 200 characters, current: {len(data['name'])}")
                    skipped += 1
                    continue

                # Create payload using validation schema
                payload = EntityCreate(
                    name=data["name"],
                    entity_code=code,
                    notes=None,
                    is_active=True,
                )

                await service.create_entity(payload)
                print(f"  [OK] Entity created successfully")
                print(f"    - Code: {code}")
                print(f"    - Name: {data['name']}")
                created += 1
                
            except ValueError as e:
                print(f"  [SKIP] Validation error: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Unexpected error: {str(e)}")
                errors += 1

        # Final summary
        print(f"\n{'='*60}")
        print("IMPORT SUMMARY")
        print(f"{'='*60}")
        print(f"Total processed: {len(merged)}")
        print(f"Created: {created}")
        print(f"Skipped: {skipped}")
        print(f"Errors: {errors}")
        
        if dry_run:
            print(f"\n⚠️  DRY-RUN MODE: No changes were made to the database")
            print(f"To execute for real, run the script without --dry-run")
        else:
            print(f"\n✅ Import completed")
            
        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Main function"""
    parser = argparse.ArgumentParser(
        description="Import system entities",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/import_entities_en.py --dry-run    # Only show what would be done
  python3 Scripts/import_entities_en.py              # Execute for real
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()
    
    # Execute import
    asyncio.run(import_entities(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
