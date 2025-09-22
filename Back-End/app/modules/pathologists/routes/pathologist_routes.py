"""Rutas de la API para el módulo de Pathologists"""

from typing import List
from fastapi import APIRouter, Depends, Query, HTTPException, status, UploadFile, File
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.config.database import get_database
from app.modules.pathologists.services.pathologist_service import PathologistService
from app.modules.pathologists.schemas.pathologist import (
    PathologistCreate,
    PathologistUpdate,
    PathologistResponse,
    PathologistSearch,
    SignatureUpdate,
    SignatureResponse
)
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["pathologists"])

# Dependency para obtener el servicio de pathologists
async def get_pathologist_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> PathologistService:
    """Obtener instancia del servicio de pathologists"""
    return PathologistService(database)

@router.post("/", response_model=PathologistResponse, status_code=status.HTTP_201_CREATED)
async def create_pathologist(
    pathologist: PathologistCreate,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Crear un nuevo patólogo"""
    try:
        return await pathologist_service.create_pathologist(pathologist)
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/", response_model=List[PathologistResponse])
async def list_pathologists(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(10, ge=1, le=100, description="Número máximo de registros a devolver"),
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Listar patólogos activos"""
    try:
        return await pathologist_service.list_pathologists(skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/search", response_model=List[PathologistResponse])
async def search_pathologists(
    q: str = Query(None, description="Término de búsqueda general"),
    pathologist_name: str = Query(None, description="Filtrar por nombre"),
    pathologist_code: str = Query(None, description="Filtrar por código"),
    pathologist_email: str = Query(None, description="Filtrar por email"),
    medical_license: str = Query(None, description="Filtrar por licencia médica"),
    is_active: bool = Query(None, description="Filtrar por estado activo"),
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros a devolver"),
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Buscar patólogos"""
    try:
        search_params = PathologistSearch(
            q=q,
            pathologist_name=pathologist_name,
            pathologist_code=pathologist_code,
            pathologist_email=pathologist_email,
            medical_license=medical_license,
            is_active=is_active
        )
        return await pathologist_service.search_pathologists(search_params, skip=skip, limit=limit)
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{pathologist_code}", response_model=PathologistResponse)
async def get_pathologist(
    pathologist_code: str,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Obtener patólogo por código"""
    try:
        return await pathologist_service.get_pathologist(pathologist_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{pathologist_code}", response_model=PathologistResponse)
async def update_pathologist(
    pathologist_code: str,
    pathologist: PathologistUpdate,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Actualizar patólogo por código"""
    try:
        return await pathologist_service.update_pathologist(pathologist_code, pathologist)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.delete("/{pathologist_code}", status_code=status.HTTP_200_OK)
async def delete_pathologist(
    pathologist_code: str,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Eliminar patólogo por código"""
    try:
        result = await pathologist_service.delete_pathologist(pathologist_code)
        return {"message": f"Pathologist with code {pathologist_code} deleted successfully", **result}
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{pathologist_code}/signature", response_model=PathologistResponse)
async def update_signature(
    pathologist_code: str,
    signature_data: SignatureUpdate,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Actualizar solo la firma digital de un patólogo"""
    try:
        return await pathologist_service.update_signature(pathologist_code, signature_data.signature)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.get("/{pathologist_code}/signature", response_model=SignatureResponse)
async def get_signature(
    pathologist_code: str,
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Obtener solo la firma digital de un patólogo"""
    try:
        return await pathologist_service.get_signature(pathologist_code)
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")

@router.put("/{pathologist_code}/upload-signature", response_model=PathologistResponse)
async def upload_signature_file(
    pathologist_code: str,
    file: UploadFile = File(...),
    pathologist_service: PathologistService = Depends(get_pathologist_service)
):
    """Subir archivo de firma digital para un patólogo"""
    try:
        # Leer contenido del archivo
        file_content = await file.read()
        
        # Validar que el archivo no esté vacío
        if len(file_content) == 0:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="File is empty")
        
        return await pathologist_service.upload_signature_file(
            pathologist_code, 
            file_content, 
            file.filename or "signature"
        )
    except NotFoundError as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail="Internal server error")
