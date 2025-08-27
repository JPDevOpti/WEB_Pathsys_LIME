import sys
from pathlib import Path
import asyncio
import argparse
from typing import Dict, List, Tuple

# Ensure 'app' package is importable when running directly
CURRENT_DIR = Path(__file__).resolve().parent
BACKEND_ROOT = CURRENT_DIR.parent
if str(BACKEND_ROOT) not in sys.path:
    sys.path.insert(0, str(BACKEND_ROOT))

from app.config.database import connect_to_mongo, close_mongo_connection
from app.modules.pruebas.repositories.prueba_repository import PruebaRepository
from app.modules.pruebas.services.prueba_service import PruebaService
from app.modules.pruebas.models.prueba import PruebaCreate


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
    tiempo_hours = 6  # Valor solicitado

    merged = coalesce_rows(RAW_TEST_ROWS)

    if dry_run:
        for code, data in merged.items():
            print(f"[DRY-RUN] {code} -> name='{data['name']}', tiempo={tiempo_hours}h, desc_len={len(data.get('desc') or '')}")
            created += 1
        return created, skipped

    db = await connect_to_mongo()
    try:
        repo = PruebaRepository(db)
        service = PruebaService(repo)
        for code, data in merged.items():
            payload = PruebaCreate(
                pruebasName=data["name"],
                pruebaCode=code,
                pruebasDescription=data.get("desc"),
                tiempo=tiempo_hours,
                isActive=True,
            )
            try:
                await service.create_prueba(payload)
                print(f"[OK] Prueba creada: {code} - {data['name']}")
                created += 1
            except Exception as e:
                print(f"[SKIP] {code} - {data['name']} -> {e}")
                skipped += 1
        return created, skipped
    finally:
        await close_mongo_connection()


def main():
    parser = argparse.ArgumentParser(description="Import tests (pruebas) from embedded list with tiempo=6 hours")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB, just preview")
    args = parser.parse_args()

    created, skipped = asyncio.run(import_tests(dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


