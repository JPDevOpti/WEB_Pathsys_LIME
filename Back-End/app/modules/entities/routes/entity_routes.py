from typing import List
from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase
from ..schemas import EntityCreate, EntityUpdate, EntityResponse, EntitySearch
from ..services import get_entity_service, EntityService
from app.config.database import get_database
from app.core.exceptions import NotFoundError, ConflictError, BadRequestError

router = APIRouter(tags=["entities"])

def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> EntityService:
    return get_entity_service(database)

@router.post("/", response_model=EntityResponse, status_code=status.HTTP_201_CREATED)
async def create_entity(entity: EntityCreate, service: EntityService = Depends(get_service)):
    try:
        return await service.create_entity(entity)
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")

@router.get("/", response_model=List[EntityResponse])
async def list_active_entities(
    query: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: EntityService = Depends(get_service)
):
    try:
        return await service.list_active(EntitySearch(query=query, skip=skip, limit=limit))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/inactive", response_model=List[EntityResponse])
async def list_all_entities(
    query: str = Query(None),
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    service: EntityService = Depends(get_service)
):
    try:
        return await service.list_all(EntitySearch(query=query, skip=skip, limit=limit))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.get("/{entity_code}", response_model=EntityResponse)
async def get_entity(entity_code: str, service: EntityService = Depends(get_service)):
    try:
        return await service.get_by_code(entity_code)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.put("/{entity_code}", response_model=EntityResponse)
async def update_entity(entity_code: str, entity_update: EntityUpdate, service: EntityService = Depends(get_service)):
    try:
        return await service.update_by_code(entity_code, entity_update)
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except ConflictError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error interno del servidor: {str(e)}")

@router.delete("/{entity_code}", response_model=dict)
async def delete_entity(entity_code: str, service: EntityService = Depends(get_service)):
    try:
        success = await service.delete_by_code(entity_code)
        if success:
            return {"message": f"Entidad {entity_code} eliminada exitosamente"}
        raise HTTPException(status_code=404, detail="Entidad no encontrada")
    except NotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        raise HTTPException(status_code=500, detail="Error interno del servidor")
