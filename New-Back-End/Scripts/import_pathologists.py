#!/usr/bin/env python3
"""
Script to insert system pathologists

This script creates pathologists in the database with the specified codes and names.
Pathologists include medical specialists in pathology.

Usage:
    python3 Scripts/import_pathologists_en.py [--dry-run]

Arguments:
    --dry-run: Only show what would be done without executing real changes
"""

import sys
import os
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict
from datetime import datetime

# Add project root directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app.config.database import get_database, close_mongo_connection
from app.modules.pathologists.schemas.pathologist import PathologistCreate
from app.modules.pathologists.services.pathologist_service import PathologistService
from app.shared.services.user_management import UserManagementService


def derive_initials(raw_initials: Optional[str], raw_name: str) -> str:
    if raw_initials and str(raw_initials).strip():
        return str(raw_initials).strip().upper()
    # Fallback: Take initials from name
    parts = [p for p in str(raw_name).strip().split() if p]
    return ("".join(p[0] for p in parts)[:4]).upper() if parts else "XX"


def compose_email(code: str, initials: str) -> str:
    # Required format: "numero.iniciales@udea.edu.co"
    return f"{code}.{(initials or '').lower()}@udea.edu.co"


def generate_default_password(code: str, initials: str) -> str:
    # Generate a default password using only the code
    return code


# Embedded list of pathologists (Teachers) provided
PATHOLOGISTS_DOCENTES: List[Dict[str, str]] = [
    {"raw_code": "32108690", "raw_name": "Leiby Alejandra Medina Zuluaica", "raw_siglas": "LAM", "registro_medico": "R-05-0816", "email": "leiby.medina@udea.edu.co"},
    {"raw_code": "71589374", "raw_name": "Juan Carlos Arango Viana", "raw_siglas": "JCA", "registro_medico": "R-9745-87", "email": "jcarlos.arango@udea.edu.co"},
    {"raw_code": "43617501", "raw_name": "Carolina López Urán", "raw_siglas": "CLU", "registro_medico": "R-1543901", "email": "carolina.lopezu@udea.edu.co"},
    {"raw_code": "1129564009", "raw_name": "Vanessa Santiago Pacheco", "raw_siglas": "VSP", "registro_medico": "R-5-6088-09", "email": "vanessa.santiago@udea.edu.co"},
    {"raw_code": "32259741", "raw_name": "Alejandra Taborda Murillo", "raw_siglas": "ATM", "registro_medico": "R-5-0967-09", "email": "alejandra.tabordam@udea.edu.co"},
    {"raw_code": "72257523", "raw_name": "Ariel Antonio Arteta Cueto", "raw_siglas": "AAA", "registro_medico": "R-13008141-5", "email": "ariel.arteta@udea.edu.co"},
    {"raw_code": "71666530", "raw_name": "Miguel Ignacio Roldán Pérez", "raw_siglas": "MRP", "registro_medico": "R-36793", "email": "mirope65@yahoo.com"},
    {"raw_code": "30582655", "raw_name": "Dilia Rosa Díaz Macea", "raw_siglas": "DRD", "registro_medico": "R-5-1161-10", "email": "diliadiazm@yahoo.com"},
    {"raw_code": "1144050050", "raw_name": "Luis Eduardo Muñoz Rayo", "raw_siglas": "LEM", "registro_medico": "R-1144050050", "email": "luis.munoz2@udea.edu.co"},
    {"raw_code": "1017233614", "raw_name": "Janine Orejuela Erazo", "raw_siglas": "JOE", "registro_medico": "R-1017233614", "email": "janine.orejuela@udea.edu.co"},
    {"raw_code": "10102849456", "raw_name": "Emil de Jesús Jiménez Berastegui", "raw_siglas": "EJB", "registro_medico": "R-1102849456", "email": "emil.jimenezb@udea.edu.co"},
    {"raw_code": "1036636079", "raw_name": "Julieth Alexandra Franco Mira", "raw_siglas": "JFM", "registro_medico": "R-1036636079", "email": "juliethfranco13@gmail.com"},
    {"raw_code": "1130613519", "raw_name": "Andrés Lozano Camayo", "raw_siglas": "ALC", "registro_medico": "R-1130613519", "email": "feloza@gmail.com"},
    {"raw_code": "70092000", "raw_name": "German de Jesus Osorio Sandoval", "raw_siglas": "GOS", "registro_medico": "R-2863", "email": "osoriosandoval2000@yahoo.es"},
    {"raw_code": "71749611", "raw_name": "Andres Felipe Covo Sandoval", "raw_siglas": "ABC", "registro_medico": "R-76-4975", "email": "afelipe.bernal@udea.edu.co"},
]


async def import_pathologists(dry_run: bool) -> Tuple[int, int]:
    """Import embedded pathologists list. Returns (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0
    users_created = 0
    users_skipped = 0

    print(f"{'='*60}")
    print("PATHOLOGIST IMPORT")
    print(f"{'='*60}")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total pathologists to process: {len(PATHOLOGISTS_DOCENTES)}")
    print(f"{'='*60}")

    # Dry run: do not connect to DB
    if dry_run:
        for i, row in enumerate(PATHOLOGISTS_DOCENTES, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")
            
            print(f"\n[{i}/{len(PATHOLOGISTS_DOCENTES)}] Processing: {raw_name}")
            print(f"  Code: {raw_code}")
            print(f"  Initials: {raw_siglas}")
            
            # Previous validations
            if not raw_code or not raw_name:
                print(f"  [SKIP] Empty code or name")
                skipped += 1
                continue
                
            # Validate code length according to schema (max 11 characters)
            if len(raw_code) > 11:
                print(f"  [SKIP] Code must have maximum 11 characters, current: {len(raw_code)}")
                skipped += 1
                continue
                
            # Validate name length (max 100 characters)
            if len(raw_name) > 100:
                print(f"  [SKIP] Name must have maximum 100 characters, current: {len(raw_name)}")
                skipped += 1
                continue
                
            initials = derive_initials(raw_siglas, raw_name)
            email = str(row.get("email") or "").strip() or compose_email(raw_code, initials)
            registro_medico = str(row.get("registro_medico") or "").strip() or f"PEND-{raw_code}"
            
            # Validate initials length (max 10 characters)
            if len(initials) > 10:
                print(f"  [SKIP] Initials must have maximum 10 characters, current: {len(initials)}")
                skipped += 1
                continue
            
            # Generate default password for user creation
            default_password = generate_default_password(raw_code, initials)
            
            print(f"  [DRY-RUN] Would create pathologist: {raw_name}")
            print(f"    - Code: {raw_code}")
            print(f"    - Email: {email}")
            print(f"    - Initials: {initials}")
            print(f"    - Medical License: {registro_medico}")
            print(f"    - Password: {default_password}")
            print(f"  [DRY-RUN] Would create user account: {raw_name}")
            print(f"    - Email: {email}")
            print(f"    - Role: pathologist")
            print(f"    - Password: {default_password} (will be encrypted)")
            print(f"    - Pathologist Code: {raw_code}")
            
            created += 1
            users_created += 1
        return created, skipped

    db = await get_database()
    try:
        service = PathologistService(db)
        user_service = UserManagementService(db)

        for i, row in enumerate(PATHOLOGISTS_DOCENTES, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")

            print(f"\n[{i}/{len(PATHOLOGISTS_DOCENTES)}] Processing: {raw_name}")
            print(f"  Code: {raw_code}")
            print(f"  Initials: {raw_siglas}")

            try:
                # Previous validations
                if not raw_code or not raw_name:
                    print(f"  [SKIP] Empty code or name")
                    skipped += 1
                    continue
                    
                # Validate code length according to schema (max 11 characters)
                if len(raw_code) > 11:
                    print(f"  [SKIP] Code must have maximum 11 characters, current: {len(raw_code)}")
                    skipped += 1
                    continue

                # Validate name length (max 100 characters)
                if len(raw_name) > 100:
                    print(f"  [SKIP] Name must have maximum 100 characters, current: {len(raw_name)}")
                    skipped += 1
                    continue

                initials = derive_initials(raw_siglas, raw_name)
                email = str(row.get("email") or "").strip() or compose_email(raw_code, initials)
                registro_medico = str(row.get("registro_medico") or "").strip() or f"PEND-{raw_code}"

                # Validate initials length (max 10 characters)
                if len(initials) > 10:
                    print(f"  [SKIP] Initials must have maximum 10 characters, current: {len(initials)}")
                    skipped += 1
                    continue

                # Create payload using validation schema
                default_password = generate_default_password(raw_code, initials)
                payload = PathologistCreate(
                    pathologist_code=raw_code,
                    pathologist_name=raw_name,
                    initials=initials,
                    pathologist_email=email,
                    medical_license=registro_medico,
                    is_active=True,
                    signature="",
                    observations=None,
                    password=default_password
                )

                # Create pathologist
                await service.create_pathologist(payload)
                print(f"  [OK] Pathologist created successfully")
                print(f"    - Code: {raw_code}")
                print(f"    - Email: {email}")
                print(f"    - Initials: {initials}")
                print(f"    - Medical License: {registro_medico}")
                created += 1
                
                # Create user account
                default_password = generate_default_password(raw_code, initials)
                user = await user_service.create_user_for_pathologist(
                    name=raw_name,
                    email=email,
                    password=default_password,
                    pathologist_code=raw_code,
                    is_active=True
                )
                
                if user:
                    print(f"  [OK] User account created successfully")
                    print(f"    - User ID: {user.get('id', 'N/A')}")
                    print(f"    - Email: {user.get('email', 'N/A')}")
                    print(f"    - Role: {user.get('role', 'N/A')}")
                    print(f"    - Password: {default_password} (encrypted in database)")
                    users_created += 1
                else:
                    print(f"  [WARNING] User account already exists or could not be created")
                    users_skipped += 1
                
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
        print(f"Total processed: {len(PATHOLOGISTS_DOCENTES)}")
        print(f"Pathologists created: {created}")
        print(f"Pathologists skipped: {skipped}")
        print(f"Users created: {users_created}")
        print(f"Users skipped: {users_skipped}")
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
        description="Import system pathologists",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/import_pathologists_en.py --dry-run    # Only show what would be done
  python3 Scripts/import_pathologists_en.py              # Execute for real
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()
    
    # Execute import
    asyncio.run(import_pathologists(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
