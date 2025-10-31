from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
import re
from urllib.parse import quote
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.services.pdf_service import CasePdfService
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter(tags=["pdf"])


def get_pdf_service(db: AsyncIOMotorDatabase = Depends(get_database)) -> CasePdfService:
    return CasePdfService(db)


@router.get("/{case_code}/pdf")
async def generate_case_pdf(
    case_code: str,
    pdf_service: CasePdfService = Depends(get_pdf_service)
):
    """
    Generar PDF del informe de resultados de un caso
    
    - **case_code**: Código del caso (ej: 2025-00001)
    
    Retorna un archivo PDF con el informe completo del caso
    """
    try:
        pdf_bytes = await pdf_service.generate_case_pdf(case_code)

        # Intentar obtener el nombre del paciente para el filename
        patient_name = ""
        try:
            case_obj = await pdf_service.case_service.get_case(case_code)
            case_data = case_obj.model_dump() if hasattr(case_obj, "model_dump") else {}
            patient_name = (case_data.get("patient_info") or {}).get("name", "")
        except Exception:
            patient_name = ""

        base_name = f"{case_code}-{patient_name}".strip(" -") or f"{case_code}"
        # Sanitizar para filename seguro (mantener letras, números, guiones, espacios, puntos y guion bajo)
        safe_name = re.sub(r"[^\w\-. ]+", "", base_name).replace(" ", "_")
        utf8_name = quote(f"{base_name}.pdf")

        return StreamingResponse(
            iter([pdf_bytes]),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"inline; filename=\"{safe_name}.pdf\"; filename*=UTF-8''{utf8_name}"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
