from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.modules.cases.services.pdf_service import CasePdfService
from app.core.exceptions import NotFoundError, BadRequestError

router = APIRouter()


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
        return StreamingResponse(
            iter([pdf_bytes]), 
            media_type="application/pdf", 
            headers={
                "Content-Disposition": f"inline; filename=caso-{case_code}.pdf"
            }
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except RuntimeError as e:
        raise HTTPException(status_code=500, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")
