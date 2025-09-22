#!/usr/bin/env python3
"""
Script to insert system tests

This script creates tests in the database with the specified codes and names.
Tests include anatomical pathology studies, immunohistochemical, cytological, etc.

Usage:
    python3 Scripts/import_tests_en.py [--dry-run]

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
from app.modules.tests.schemas.test import TestCreate
from app.modules.tests.services.test_service import get_test_service


def normalize_text(text: str) -> str:
    if text is None:
        return None
    return " ".join(str(text).split()).strip()


# Embedded list from user (codes as strings)
RAW_TEST_ROWS: List[Dict[str, str]] = [
    {"code": "898101", "name": "Estudio de Coloración Básica en Biopsia", "desc": "Biopsia simple un (1) frasco con uno o varios fragmentos de tejido hasta 3 cm/cc. Ejemplos: endometrio, cuña de cérvix, cuña de piel, cureaje, tru-cut, biopsia renal, biopsia hepática, biopsias de colón o estómago."},
    {"code": "898201", "name": "Estudio de Coloración Básica en Espécimen de Reconocimiento", "desc": "Espécimen quirúrgico no tumoral\nEjemplo: apéndice cecal, vesícula biliar, útero sin anexos, ovario no tumoral, mama sin tumor, etc."},
    {"code": "898241", "name": "Estudio de Coloración Básica en Espécimen con Resección de Márgenes", "desc": "Espécimen quirúrgico por condición tumoral:\nEjemplo: mama, amputación, estómago, colon, útero por NIC/carcinoma o con anexos y cérvix conización."},
    {"code": "898102", "name": "Estudio Biopsia en Médula Ósea", "desc": "Sin coloraciones especiales ni inmunohistoquímica"},
    {"code": "898807-1", "name": "Estudio Anatomopatológico de Marcación Inmunohistoquímica", "desc": "Inmunohistoquímica básica (específico) sin lectura: cada marcador en bloque de parafina o placa cargada. Ejemplo: CD3, CKIT, actina de músculo liso, S100, HMB45, etc. (ver listado adjunto de anticuerpos disponibles)"},
    {"code": "898807", "name": "Estudio Anatomopatológico de Marcación Inmunohistoquímica", "desc": "Inmunohistoquímica básica (específico): cada marcador en bloque de parafina o placa cargada.\nEjemplo: CD3, CKIT, actina de músculo liso, S100, HMB45, etc. (ver listado adjunto de anticuerpos disponibles)"},
    {"code": "898812", "name": "Estudio Anatomopatológico de Marcación Inmunohistoquímica Especial", "desc": "Inmunohistoquímica de alta complejidad: cada marcador tumoral en placa cargada\nEjemplo: SOX-11, PAX5, C4D, SV40, C-ERB2, receptores de estrógenos y progesterona, etc. (ver listado adjunto de anticuerpos disponibles)."},
    {"code": "898813", "name": "Estudio Anatomopatológico de Marcación Inmunohistoquímica Especial", "desc": "Inmunohistoquímica especiales: cada marcador tumoral en placa cargada\nEjemplo: ATRX, IDH1, MUC1, PD1, PD-L1, perforina, PIT-1, TPIT, etc. (ver listado adjunto de anticuerpos disponibles)."},
    {"code": "898018", "name": "Estudio Anatomopatológico por Inmunohistoquímica", "desc": "Estudio anatomopatológico por inmunohistoquímica (marcador específico) en biopsia de médula ósea"},
    {"code": "898808", "name": "Estudio Anatomopatológico en Biopsia por Tinción Histoquímica", "desc": "Coloraciones especiales: tricrómico, retículo, hierro, plata metenamina, HPTA cerebro, rojo congo, cristal violeta, Wartin Starry, etc. 38 coloraciones disponibles (ver listado adjunto)"},
    {"code": "898809", "name": "Estudio Anatomopatológico en Biopsia por Tinción Histoquímica", "desc": "Coloraciones especiales: tricrómico, retículo, hierro, plata metenamina, HPTA cerebro, rojo congo, cristal violeta, Wartin Starry, etc. 38 coloraciones disponibles (ver listado adjunto)"},
    {"code": "898017", "name": "Estudio Anatomopatológico en Citología", "desc": "Estudio anatomopatológico en citología por tinción de histoquímica (específico)"},
    {"code": "898003", "name": "Estudio de Coloración Básica en Citología por Aspiración de Cualquier Tejido u Órgano - Aspirado (BACAF)", "desc": "Ejemplo: tiroides, ganglio linfático, mama, etc."},
    {"code": "898002", "name": "Estudio de Coloración Básica en Citología de Líquido Corporal o Secreción - Líquido Corporal", "desc": "Ejemplo: pleural, peritoneal, ascítico, LCR, orina, lavado, esputo, etc."},
    {"code": "898801", "name": "Estudio por Congelación o Consulta Intra-operatoria", "desc": "Incluye cortes rápidos por congelación, improntas y control de congelación posterior en hematoxilina-eosina. Informe preliminar y final."},
    {"code": "898805", "name": "Verificación Integral sin Preparación de Material de Rutina", "desc": "Revisión de placas por especialista en patología"},
    {"code": "898809", "name": "Estudio Anatomopatológico en Biopsia por Inmunofluorescencia", "desc": "Estudio anatomopatológico en biopsia por inmunofluorescencia (específico)."},
    {"code": "898304", "name": "Estudio Pos-mortem de Feto y Placenta (Hasta 38 Semanas de Gestación)", "desc": "Incluye disección del cadáver, estudio macroscópico, microscópico, correlación clínico-patológico y diagnóstico final. Se incluye además todas las coloraciones especiales e inmunohistoquímicas necesarias."},
    {"code": "898301", "name": "Autopsia Completa - Necropsia (Neonatos en Adelante)", "desc": "Incluye disección del cadáver, estudio macroscópico, microscópico, correlación clínico-patológico y diagnóstico final. Se incluye además, todas las coloraciones especiales e inmunohistoquímicas requeridas."},
]


def coalesce_rows(rows: List[Dict[str, str]]) -> Dict[str, Dict[str, str]]:
    merged: Dict[str, Dict[str, str]] = {}
    for row in rows:
        code = str(row.get("code", "")).strip()
        name = normalize_text(row.get("name"))
        desc = row.get("desc")
        if not code or not name:
            continue
        desc = desc if desc is None else desc.strip()
        if code not in merged:
            merged[code] = {"name": name, "desc": desc or None}
        else:
            # Keep first name; merge descriptions if different
            existing_desc = merged[code].get("desc")
            if desc and desc != existing_desc:
                if existing_desc:
                    merged[code]["desc"] = f"{existing_desc}\n{desc}"
                else:
                    merged[code]["desc"] = desc
    return merged


async def import_tests(dry_run: bool) -> Tuple[int, int]:
    created = 0
    skipped = 0
    errors = 0
    tiempo_dias = 6  # 6 days

    merged = coalesce_rows(RAW_TEST_ROWS)

    print(f"{'='*60}")
    print("TEST IMPORT")
    print(f"{'='*60}")
    print(f"Mode: {'DRY-RUN (no changes)' if dry_run else 'REAL EXECUTION'}")
    print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print(f"Total tests to process: {len(merged)}")
    print(f"Default time: {tiempo_dias} days")
    print(f"{'='*60}")

    if dry_run:
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Processing: {code}")
            print(f"  Name: {data['name']}")
            print(f"  Time: {tiempo_dias} days")
            print(f"  Description: {len(data.get('desc') or '')} characters")
            print(f"  [DRY-RUN] Would create test: {code}")
            created += 1
        return created, skipped

    db = await get_database()
    try:
        service = get_test_service(db)
        
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Processing: {code}")
            print(f"  Name: {data['name']}")
            print(f"  Time: {tiempo_dias} days")
            
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
                
                # Validate description length (max 500 characters)
                if data.get('desc') and len(data['desc']) > 500:
                    print(f"  [SKIP] Description cannot exceed 500 characters, current: {len(data['desc'])}")
                    skipped += 1
                    continue
                
                # Create payload using validation schema
                payload = TestCreate(
                    name=data["name"],
                    test_code=code,
                    description=data.get("desc"),
                    time=tiempo_dias,
                    price=0.0,
                    is_active=True,
                )
                
                await service.create_test(payload)
                print(f"  [OK] Test created successfully")
                print(f"    - Code: {code}")
                print(f"    - Name: {data['name']}")
                print(f"    - Time: {tiempo_dias} days")
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
        description="Import system tests",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python3 Scripts/import_tests_en.py --dry-run    # Only show what would be done
  python3 Scripts/import_tests_en.py              # Execute for real
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Only show what would be done without executing real changes"
    )
    
    args = parser.parse_args()
    
    # Execute import
    asyncio.run(import_tests(dry_run=args.dry_run))


if __name__ == "__main__":
    main()
