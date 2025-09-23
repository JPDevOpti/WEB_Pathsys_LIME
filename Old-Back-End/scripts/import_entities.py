#!/usr/bin/env python3
"""
Script para insertar entidades del sistema

Este script crea entidades en la base de datos con los códigos y nombres especificados.
Las entidades incluyen hospitales, clínicas, laboratorios y otras instituciones de salud.

Uso:
    python3 scripts/import_entities.py [--dry-run]

Argumentos:
    --dry-run: Solo mostrar qué se haría sin ejecutar cambios reales
"""

import sys
from pathlib import Path
import asyncio
import argparse
from typing import Dict, List, Tuple
from datetime import datetime

# Ensure 'app' package importable
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.entidades.repositories.entidad_repository import EntidadRepository
from app.modules.entidades.services.entidad_service import EntidadService
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
    """Importar lista de entidades embebida. Retorna (created, skipped)."""
    created = 0
    skipped = 0
    errors = 0

    merged = dedupe_rows(RAW_ENTITIES)

    print(f"{'='*60}")
    print("IMPORTACIÓN DE ENTIDADES")
    print(f"{'='*60}")
    print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
    print(f"Fecha: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total entidades a procesar: {len(merged)}")
    print(f"{'='*60}")

    # Dry run: do not connect to DB
    if dry_run:
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Procesando: {code}")
            print(f"  Nombre: {data['name']}")
            
            # Validaciones previas
            if not code or not code.strip():
                print(f"  [SKIP] Código vacío o inválido")
                skipped += 1
                continue
                
            if not data['name'] or not data['name'].strip():
                print(f"  [SKIP] Nombre vacío o inválido")
                skipped += 1
                continue

            # Validar longitud del código (2-20 caracteres)
            if len(code) < 2 or len(code) > 20:
                print(f"  [SKIP] Código debe tener entre 2 y 20 caracteres, actual: {len(code)}")
                skipped += 1
                continue

            # Validar longitud del nombre (2-200 caracteres)
            if len(data['name']) < 2 or len(data['name']) > 200:
                print(f"  [SKIP] Nombre debe tener entre 2 y 200 caracteres, actual: {len(data['name'])}")
                skipped += 1
                continue
            
            print(f"  [DRY-RUN] Se crearía la entidad: {code}")
            print(f"    - Código: {code}")
            print(f"    - Nombre: {data['name']}")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = EntidadRepository(db)
        service = EntidadService(repo)

        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Procesando: {code}")
            print(f"  Nombre: {data['name']}")

            try:
                # Validaciones previas
                if not code or not code.strip():
                    print(f"  [SKIP] Código vacío o inválido")
                    skipped += 1
                    continue
                    
                if not data['name'] or not data['name'].strip():
                    print(f"  [SKIP] Nombre vacío o inválido")
                    skipped += 1
                    continue

                # Validar longitud del código (2-20 caracteres)
                if len(code) < 2 or len(code) > 20:
                    print(f"  [SKIP] Código debe tener entre 2 y 20 caracteres, actual: {len(code)}")
                    skipped += 1
                    continue

                # Validar longitud del nombre (2-200 caracteres)
                if len(data['name']) < 2 or len(data['name']) > 200:
                    print(f"  [SKIP] Nombre debe tener entre 2 y 200 caracteres, actual: {len(data['name'])}")
                    skipped += 1
                    continue

                # Crear payload usando el esquema de validación
                payload = EntidadCreate(
                    entidad_name=data["name"],
                    entidad_code=code,
                    observaciones=None,
                    is_active=True,
                )

                await service.create_entidad(payload)
                print(f"  [OK] Entidad creada exitosamente")
                print(f"    - Código: {code}")
                print(f"    - Nombre: {data['name']}")
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
        print(f"Total procesados: {len(merged)}")
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
        description="Importar entidades del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/import_entities.py --dry-run    # Solo mostrar qué se haría
  python3 scripts/import_entities.py              # Ejecutar realmente
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    asyncio.run(import_entities(dry_run=args.dry_run))


if __name__ == "__main__":
    main()


