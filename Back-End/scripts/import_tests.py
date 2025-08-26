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
    {"code": "898101", "name": "ESTUDIO DE COLORACIÓN BÁSICA EN BIOPSIA", "desc": "BIOPSIA SIMPLE UN (1) FRASCO CON UNO O VARIOS FRAGMENTOS DE TEJIDO HASTA 3 CM/CC. EJEMPLOS: ENDOMETRIO, CUÑA DE CÉRVIX, CUÑA DE PIEL, CUREAJE, TRU-CUT., BIOPSIA RENAL, BIOPSIA HEPÁTICA, BIOPSIAS DE COLÓN O ESTOMAGO."},
    {"code": "898201", "name": "ESTUDIO DE COLORACIÓN BÁSICA EN ESPÉCIMEN DE RECONOCIMIENTO", "desc": "ESPÉCIMEN QUIRÚRGICO NO TUMORAL\nEJEMPLO: APÉNDICE CECAL, VESÍCULA BILIAR, ÚTERO SIN ANEXOS, OVARIO NO TUMORAL, MAMA SIN TUMOR, E.T.C."},
    {"code": "898241", "name": "ESTUDIO DE COLORACIÓN BÁSICA EN ESPÉCIMEN CON RESECCIÓN DE MÁRGENES", "desc": "ESPÉCIMEN QUIRÚRGICO POR CONDICIÓN TUMORAL:\nEJEMPLO: MAMA, AMPUTACIÓN, ESTÓMAGO, COLON, ÚTERO POR NIC/CARCINOMA O CON ANEXOS Y CÉRVIX CONIZACIÓN*."},
    {"code": "898101", "name": "ESTUDIO BIOPSIA EN MÉDULA ÓSEA:", "desc": "SIN COLORACIONES ESPECIALES NI INMUNOHISTOQUÍMICA*"},
    {"code": "898807-1", "name": "ESTUDIO ANATOMOPATOLÓGICO DE MARCACIÓN INMUNOHISTOQUÍMICA", "desc": "INMUNOHISTOQUÍMICA BÁSICA (ESPECÍFICO) SIN LECTURA: CADA MARCADOR EN BLOQUE DE PARAFINA O PLACA CARGADA. EJEMPLO: CD3, CKIT, ACTINA DE MÚSCULO LISO, S100, HMB45, ETC. (VER LISTADO ADJUNTO DE ANTICUERPOS DISPONIBLES)*"},
    {"code": "898807", "name": "ESTUDIO ANATOMOPATOLÓGICO DE MARCACIÓN INMUNOHISTOQUÍMICA", "desc": "INMUNOHISTOQUÍMICA BÁSICA (ESPECÍFICO): CADA MARCADOR EN BLOQUE DE PARAFINA O PLACA CARGADA.\nEJEMPLO: CD3, CKIT, ACTINA DE MÚSCULO LISO, S100, HMB45, ETC. (VER LISTADO ADJUNTO DE ANTICUERPOS DISPONIBLES)*"},
    {"code": "898812", "name": "ESTUDIO ANATOMOPATOLÓGICO DE MARCACIÓN INMUNOHISTOQUÍMICA ESPECIAL", "desc": "INMUNOHISTOQUÍMICA DE ALTA COMPLEJIDAD: CADA MARCADOR TUMORAL EN PLACA CARGADA\nEJEMPLO: SOX-11, PAX5, C4D, SV40, C-ERB2, RECEPTORES DE ESTRÓGENOS Y PROGESTERONA, ETC. (VER LISTADO ADJUNTO DE ANTICUERPOS DISPONIBLES)*."},
    {"code": "898812", "name": "ESTUDIO ANATOMOPATOLÓGICO DE MARCACIÓN INMUNOHISTOQUÍMICA ESPECIAL", "desc": "INMUNOHISTOQUÍMICA ESPECIALES: CADA MARCADOR TUMORAL EN PLACA CARGADA\nEJEMPLO: ATRX, IDH1, MUC1, PD1, PD-L1, PERFORINA, PIT-1, TPIT), ETC. (VER LISTADO ADJUNTO DE ANTICUERPOS DISPONIBLES)*."},
    {"code": "898018", "name": "ESTUDIO ANATOMOPATOLÓGICO POR INMUNOHISTOQUÍMICA", "desc": "ESTUDIO ANATOMOPATOLÓGICO POR INMUNOHISTOQUÍMICA (MARCADOR ESPECÍFICO) EN BIOPSIA DE MÉDULA ÓSEA"},
    {"code": "898808", "name": "ESTUDIO ANATOMOPATOLÓGICO EN BIOPSIA POR TINCIÓN HISTOQUÍMICA", "desc": "COLORACIONES ESPECIALES: TRICRÓMICO, RETÍCULO, HIERRO, PLATA METENAMINA, HPTA CEREBRO, ROJO CONGO, CRISTAL VIOLETA, WARTIN STARRY, ETC. 38 COLORACIONES DISPONIBLES (VER LISTADO ADJUNTO)"},
    {"code": "898808", "name": "ESTUDIO ANATOMOPATOLÓGICO EN BIOPSIA POR TINCIÓN HISTOQUÍMICA", "desc": "COLORACIONES ESPECIALES: TRICRÓMICO, RETÍCULO, HIERRO, PLATA METENAMINA,  HPTA CEREBRO, ROJO CONGO, CRISTAL VIOLETA, WARTIN STARRY, ETC. 38 COLORACIONES DISPONIBLES (VER LISTADO ADJUNTO)*"},
    {"code": "898017", "name": "ESTUDIO ANATOMOPATOLÓGICO EN CITOLOGÍA", "desc": "ESTUDIO ANATOMOPATOLÓGICO EN CITOLOGÍA POR TINCIÓN DE HISTOQUIMICA (ESPECÍFICO)"},
    {"code": "898003", "name": "ESTUDIO DE COLORACIÓN BÁSICA EN CITOLOGÍA POR ASPIRACIÓN DE CUALQUIER TEJIDO U ORGANO -ASPIRADO (BACAF)", "desc": "EJEMPLO: TIROIDES, GANGLIO LINFÁTICO, MAMA, E.T.C."},
    {"code": "898002", "name": "ESTUDIO DE COLORACIÓN BÁSICA EN CITOLOGÍA DE LÍQUIDO CORPORAL O - SECRECION -LÍQUIDO CORPORAL", "desc": "EJEMPLO: PLEURAL, PERITONEAL, ASCÍTICO, LCR, ORINA, LAVADO, ESPUTO E.T.C."},
    {"code": "898801", "name": "ESTUDIO POR CONGELACIÓN O CONSULTA INTRA-OPERATORIA.", "desc": "INCLUYE CORTES RÁPIDOS POR CONGELACIÓN, IMPRONTAS Y CONTROL DE CONGELACIÓN POSTERIOR EN HEMATOXILINA- EOSINA. INFORME PRELIMINAR Y FINAL."},
    {"code": "898805", "name": "VERIFICACIÓN INTEGRAL SIN PREPARACIÓN DE MATERIAL DE RUTINA.", "desc": "REVISIÓN DE PLACAS POR ESPECIALISTA EN PATOLOGÍA"},
    {"code": "8988809", "name": "ESTUDIO ANATOMOPATOLÓGICO EN BIOPSIA POR INMUNOFLUORESCENCIA", "desc": "ESTUDIO ANATOMOPATOLÓGICO EN BIOPSIA POR INMUNOFLUORESCENCIA (ESPECÍFICO)."},
    {"code": "898304", "name": "ESTUDIO POS-MORTEM DE FETO Y PLACENTA: (HASTA 38 SEMANAS DE GESTACIÓN).", "desc": "INCLUYE DISECCIÓN DEL CADÁVER, ESTUDIO MACROSCÓPICO, MICROSCÓPICO, CORRELACIÓN CLÍNICO-PATOLÓGICO Y DIAGNÓSTICO FINAL. SE INCLUYE ADEMÁS TODAS LAS COLORACIONES ESPECIALES E INMUNOHISTOQUÍMICAS NECESARIAS."},
    {"code": "898301", "name": "AUTOPSIA COMPLETA -NECROPSIA: (NEONATOS EN ADELANTE):", "desc": "INCLUYE DISECCIÓN DEL CADÁVER, ESTUDIO MACROSCÓPICO, MICROSCÓPICO, CORRELACIÓN CLÍNICO-PATOLÓGICO Y DIAGNÓSTICO FINAL.  SE INCLUYE ADEMÁS, TODAS LAS COLORACIONES ESPECIALES E INMUNOHISTOQUÍMICAS REQUERIDAS."},
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
    parser = argparse.ArgumentParser(description="Import tests (pruebas) from embedded list with tiempo=5 days")
    parser.add_argument("--dry-run", action="store_true", help="Do not write to DB, just preview")
    args = parser.parse_args()

    created, skipped = asyncio.run(import_tests(dry_run=args.dry_run))
    print(f"Done. Created: {created}, Skipped: {skipped}")


if __name__ == "__main__":
    main()


