#!/usr/bin/env python3
"""
Script para insertar patólogos del sistema

Este script crea patólogos en la base de datos con los códigos y nombres especificados.
Los patólogos incluyen médicos docentes especialistas en patología.

Uso:
    python3 scripts/import_pathologists.py [--dry-run]

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


async def import_pathologists(dry_run: bool) -> Tuple[int, int]:
    """Importar lista de patólogos embebida. Retorna (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0

    print(f"{'='*60}")
    print("IMPORTACIÓN DE PATÓLOGOS")
    print(f"{'='*60}")
    print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total patólogos a procesar: {len(PATHOLOGISTS_DOCENTES)}")
    print(f"{'='*60}")

    # Modo dry-run: no conectamos a la BD
    if dry_run:
        for i, row in enumerate(PATHOLOGISTS_DOCENTES, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")
            
            print(f"\n[{i}/{len(PATHOLOGISTS_DOCENTES)}] Procesando: {raw_name}")
            print(f"  Código: {raw_code}")
            print(f"  Siglas: {raw_siglas}")
            
            # Validaciones previas
            if not raw_code or not raw_name:
                print(f"  [SKIP] Código o nombre vacío")
                skipped += 1
                continue
                
            # Validar longitud del código según el esquema (6-10 caracteres)
            if len(raw_code) < 6 or len(raw_code) > 10:
                print(f"  [SKIP] Código debe tener entre 6 y 10 caracteres, actual: {len(raw_code)}")
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
            
            print(f"  [DRY-RUN] Se crearía el patólogo: {raw_name}")
            print(f"    - Código: {raw_code}")
            print(f"    - Email: {email}")
            print(f"    - Iniciales: {initials}")
            print(f"    - Registro médico: {registro_medico}")
            print(f"    - Se crearía en: patologos + usuarios (rol: patologo)")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = PatologoRepository(db)
        user_service = UserManagementService(db)
        service = PatologoService(repo, user_service)

        for i, row in enumerate(PATHOLOGISTS_DOCENTES, 1):
            raw_code = str(row.get("raw_code", "")).strip()
            raw_name = str(row.get("raw_name", "")).strip()
            raw_siglas = row.get("raw_siglas")

            print(f"\n[{i}/{len(PATHOLOGISTS_DOCENTES)}] Procesando: {raw_name}")
            print(f"  Código: {raw_code}")
            print(f"  Siglas: {raw_siglas}")

            try:
                # Validaciones previas
                if not raw_code or not raw_name:
                    print(f"  [SKIP] Código o nombre vacío")
                    skipped += 1
                    continue
                    
                # Validar longitud del código según el esquema (6-10 caracteres)
                if len(raw_code) < 6 or len(raw_code) > 10:
                    print(f"  [SKIP] Código debe tener entre 6 y 10 caracteres, actual: {len(raw_code)}")
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
                payload = PatologoCreate(
                    patologo_name=raw_name,
                    iniciales_patologo=initials,
                    patologo_code=raw_code,
                    patologo_email=email,
                    registro_medico=registro_medico,
                    password=raw_code,  # Contraseña igual al número de documento
                    is_active=True,
                    firma="",
                    observaciones=None,
                )

                await service.create_patologo(payload)
                print(f"  [OK] Patólogo creado exitosamente")
                print(f"    - Código: {raw_code}")
                print(f"    - Email: {email}")
                print(f"    - Iniciales: {initials}")
                print(f"    - Registro médico: {registro_medico}")
                print(f"    - Creado en: patologos + usuarios (rol: patologo)")
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
        print(f"Total procesados: {len(PATHOLOGISTS_DOCENTES)}")
        print(f"Creados: {created}")
        print(f"Saltados: {skipped}")
        print(f"Errores: {errors}")
        
        if dry_run:
            print(f"\n⚠️  MODO DRY-RUN: No se realizaron cambios en la base de datos")
            print(f"Para ejecutar realmente, ejecuta el script sin --dry-run")
        else:
            print(f"\n✅ Importación completada")
            print(f"📝 Nota: Los patólogos se crean en ambas colecciones:")
            print(f"   - patologos: Datos del patólogo")
            print(f"   - usuarios: Usuario con rol 'patologo'")
            
        print(f"{'='*60}")

        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    """Función principal"""
    parser = argparse.ArgumentParser(
        description="Importar patólogos del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/import_pathologists.py --dry-run    # Solo mostrar qué se haría
  python3 scripts/import_pathologists.py              # Ejecutar realmente
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    asyncio.run(import_pathologists(dry_run=args.dry_run))


if __name__ == "__main__":
    main()


