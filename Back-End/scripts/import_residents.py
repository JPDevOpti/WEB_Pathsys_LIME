#!/usr/bin/env python3
"""
Script para insertar residentes del sistema

Este script crea residentes en la base de datos con los códigos y nombres especificados.
Los residentes incluyen médicos residentes en patología con sus respectivos datos.

Uso:
    python3 scripts/import_residents.py [--dry-run]

Argumentos:
    --dry-run: Solo mostrar qué se haría sin ejecutar cambios reales
"""

import os
import sys
from pathlib import Path
import asyncio
import argparse
from typing import Optional, Tuple, List, Dict
from datetime import datetime

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
    """Importar lista de residentes embebida. Retorna (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0

    print(f"{'='*60}")
    print("IMPORTACIÓN DE RESIDENTES")
    print(f"{'='*60}")
    print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total residentes a procesar: {len(RESIDENTS_LIST)}")
    print(f"{'='*60}")

    # Dry run: do not connect to DB
    if dry_run:
        for i, row in enumerate(RESIDENTS_LIST, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")
            
            print(f"\n[{i}/{len(RESIDENTS_LIST)}] Procesando: {raw_name}")
            print(f"  Código: {raw_code}")
            print(f"  Siglas: {raw_siglas}")
            
            # Validaciones previas
            if not raw_code or not raw_name:
                print(f"  [SKIP] Código o nombre vacío")
                skipped += 1
                continue
                
            # Validar longitud del código según el esquema (1-20 caracteres)
            if len(raw_code) < 1 or len(raw_code) > 20:
                print(f"  [SKIP] Código debe tener entre 1 y 20 caracteres, actual: {len(raw_code)}")
                skipped += 1
                continue
                
            # Validar longitud del nombre (2-100 caracteres)
            if len(raw_name) < 2 or len(raw_name) > 100:
                print(f"  [SKIP] Nombre debe tener entre 2 y 100 caracteres, actual: {len(raw_name)}")
                skipped += 1
                continue
                
            initials = derive_initials(raw_siglas, raw_name)
            email = compose_email(raw_code, initials)
            registro_medico = f"PEND-{raw_code}"
            
            # Validar longitud de iniciales (2-10 caracteres)
            if len(initials) < 2 or len(initials) > 10:
                print(f"  [SKIP] Iniciales deben tener entre 2 y 10 caracteres, actual: {len(initials)}")
                skipped += 1
                continue
            
            print(f"  [DRY-RUN] Se crearía el residente: {raw_name}")
            print(f"    - Código: {raw_code}")
            print(f"    - Email: {email}")
            print(f"    - Iniciales: {initials}")
            print(f"    - Registro médico: {registro_medico}")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = ResidenteRepository(db)
        user_service = UserManagementService(db)
        service = ResidenteService(repo, user_service)

        for i, row in enumerate(RESIDENTS_LIST, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")

            print(f"\n[{i}/{len(RESIDENTS_LIST)}] Procesando: {raw_name}")
            print(f"  Código: {raw_code}")
            print(f"  Siglas: {raw_siglas}")

            try:
                # Validaciones previas
                if not raw_code or not raw_name:
                    print(f"  [SKIP] Código o nombre vacío")
                    skipped += 1
                    continue
                    
                # Validar longitud del código según el esquema (1-20 caracteres)
                if len(raw_code) < 1 or len(raw_code) > 20:
                    print(f"  [SKIP] Código debe tener entre 1 y 20 caracteres, actual: {len(raw_code)}")
                    skipped += 1
                    continue

                # Validar longitud del nombre (2-100 caracteres)
                if len(raw_name) < 2 or len(raw_name) > 100:
                    print(f"  [SKIP] Nombre debe tener entre 2 y 100 caracteres, actual: {len(raw_name)}")
                    skipped += 1
                    continue

                initials = derive_initials(raw_siglas, raw_name)
                email = compose_email(raw_code, initials)
                registro_medico = f"PEND-{raw_code}"

                # Validar longitud de iniciales (2-10 caracteres)
                if len(initials) < 2 or len(initials) > 10:
                    print(f"  [SKIP] Iniciales deben tener entre 2 y 10 caracteres, actual: {len(initials)}")
                    skipped += 1
                    continue

                # Crear payload usando el esquema de validación
                payload = ResidenteCreate(
                    residente_name=raw_name,
                    iniciales_residente=initials,
                    residente_code=raw_code,
                    residente_email=email,
                    registro_medico=registro_medico,
                    password=raw_code,  # Password equals document number
                    is_active=True,
                    observaciones=None,
                )

                await service.create_residente(payload)
                print(f"  [OK] Residente creado exitosamente")
                print(f"    - Código: {raw_code}")
                print(f"    - Email: {email}")
                print(f"    - Iniciales: {initials}")
                print(f"    - Registro médico: {registro_medico}")
                created += 1
                
            except ValueError as e:
                print(f"  [SKIP] Error de validación: {str(e)}")
                skipped += 1
            except Exception as e:
                print(f"  [ERROR] Error inesperado: {str(e)}")
                errors += 1

        # Resumen final
        print(f"\n{'='*60}")
        print("RESUMEN DE IMPORTACIÓN")
        print(f"{'='*60}")
        print(f"Total procesados: {len(RESIDENTS_LIST)}")
        print(f"Creados: {created}")
        print(f"Saltados: {skipped}")
        print(f"Errores: {errors}")
        
        if dry_run:
            print(f"\n⚠️  MODO DRY-RUN: No se realizaron cambios en la base de datos")
            print(f"Para ejecutar realmente, ejecuta el script sin --dry-run")
        else:
            print(f"\n✅ Importación completada")
            
        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Importar residentes del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/import_residents.py --dry-run    # Solo mostrar qué se haría
  python3 scripts/import_residents.py              # Ejecutar realmente
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    asyncio.run(import_residents(dry_run=args.dry_run))


if __name__ == "__main__":
    main()


