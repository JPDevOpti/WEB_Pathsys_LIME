#!/usr/bin/env python3
"""
Script para insertar pruebas del sistema

Este script crea pruebas en la base de datos con los códigos y nombres especificados.
Las pruebas incluyen estudios anatomopatológicos, inmunohistoquímicos, citológicos, etc.

Uso:
    python3 scripts/import_tests.py [--dry-run]

Argumentos:
    --dry-run: Solo mostrar qué se haría sin ejecutar cambios reales
"""

import sys
import os
from pathlib import Path
import asyncio
import argparse
from typing import Dict, List, Tuple
from datetime import datetime

# Ensure 'app' package is importable when running directly
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository
from app.modules.pruebas.services.prueba_service import PruebaService
from app.modules.pruebas.schemas.prueba import PruebaCreate


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
    tiempo_dias = 6  # 6 días

    merged = coalesce_rows(RAW_TEST_ROWS)

    print(f"{'='*60}")
    print("IMPORTACIÓN DE PRUEBAS")
    print(f"{'='*60}")
    print(f"Modo: {'DRY-RUN (sin cambios)' if dry_run else 'EJECUCIÓN REAL'}")
    print(f"Total pruebas a procesar: {len(merged)}")
    print(f"Tiempo por defecto: {tiempo_dias} días")
    print(f"{'='*60}")

    if dry_run:
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Procesando: {code}")
            print(f"  Nombre: {data['name']}")
            print(f"  Tiempo: {tiempo_dias} días")
            print(f"  Descripción: {len(data.get('desc') or '')} caracteres")
            print(f"  [DRY-RUN] Se crearía la prueba: {code}")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = PruebaRepository(db)
        service = PruebaService(repo)
        
        for i, (code, data) in enumerate(merged.items(), 1):
            print(f"\n[{i}/{len(merged)}] Procesando: {code}")
            print(f"  Nombre: {data['name']}")
            print(f"  Tiempo: {tiempo_dias} días")
            
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
                
                # Validar longitud del código
                if len(code) < 2 or len(code) > 20:
                    print(f"  [SKIP] Código debe tener entre 2 y 20 caracteres, actual: {len(code)}")
                    skipped += 1
                    continue
                
                # Validar longitud del nombre
                if len(data['name']) < 2 or len(data['name']) > 200:
                    print(f"  [SKIP] Nombre debe tener entre 2 y 200 caracteres, actual: {len(data['name'])}")
                    skipped += 1
                    continue
                
                # Validar longitud de la descripción
                if data.get('desc') and len(data['desc']) > 500:
                    print(f"  [SKIP] Descripción no puede exceder 500 caracteres, actual: {len(data['desc'])}")
                    skipped += 1
                    continue
                
                # Crear payload usando el esquema de validación
                payload = PruebaCreate(
                    prueba_name=data["name"],
                    prueba_code=code,
                    prueba_description=data.get("desc"),
                    tiempo=tiempo_dias,
                    is_active=True,
                )
                
                await service.create_prueba(payload)
                print(f"  [OK] Prueba creada exitosamente")
                print(f"    - Código: {code}")
                print(f"    - Nombre: {data['name']}")
                print(f"    - Tiempo: {tiempo_dias} días")
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
        description="Importar pruebas del sistema",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos:
  python3 scripts/import_tests.py --dry-run    # Solo mostrar qué se haría
  python3 scripts/import_tests.py              # Ejecutar realmente
        """
    )
    
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Solo mostrar qué se haría sin ejecutar cambios reales"
    )
    
    args = parser.parse_args()
    
    # Ejecutar la importación
    asyncio.run(import_tests(dry_run=args.dry_run))


if __name__ == "__main__":
    main()


