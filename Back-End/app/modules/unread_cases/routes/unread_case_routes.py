"""API routes for unread cases."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query, status
from motor.motor_asyncio import AsyncIOMotorDatabase

from ..schemas.unread_case import (
    BulkMarkDeliveredRequest,
    BulkMarkDeliveredResponse,
    UnreadCaseCreate,
    UnreadCaseFilter,
    UnreadCaseListResponse,
    UnreadCaseResponse,
    UnreadCaseUpdate,
)
from ..services.unread_case_service import UnreadCaseService, get_unread_case_service
from app.config.database import get_database
from app.core.exceptions import ConflictError, NotFoundError


router = APIRouter(tags=["unread-cases"])


def get_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> UnreadCaseService:
    return get_unread_case_service(database)


@router.get("/", response_model=UnreadCaseListResponse)
async def list_unread_cases(
    page: int = Query(1, ge=1),
    limit: int = Query(25, ge=1, le=200),
    search_query: str | None = Query(None),
    selected_institution: str | None = Query(None),
    selected_test_type: str | None = Query(None),
    selected_status: str | None = Query(None),
    date_from: str | None = Query(None),
    date_to: str | None = Query(None),
    sort_key: str | None = Query(None),
    sort_order: str | None = Query(None),
    service: UnreadCaseService = Depends(get_service),
) -> UnreadCaseListResponse:
    filters = UnreadCaseFilter(
        page=page,
        limit=limit,
        search_query=search_query,
        selected_institution=selected_institution,
        selected_test_type=selected_test_type,
        selected_status=selected_status,
        date_from=date_from,
        date_to=date_to,
        sort_key=sort_key,
        sort_order=sort_order,
    )
    return await service.list_unread_cases(filters)


@router.get("/{case_code}", response_model=UnreadCaseResponse)
async def get_unread_case(case_code: str, service: UnreadCaseService = Depends(get_service)) -> UnreadCaseResponse:
    try:
        return await service.get_unread_case(case_code)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/", response_model=UnreadCaseResponse, status_code=status.HTTP_201_CREATED)
async def create_unread_case(
    payload: UnreadCaseCreate,
    service: UnreadCaseService = Depends(get_service),
) -> UnreadCaseResponse:
    try:
        return await service.create_unread_case(payload)
    except ConflictError as exc:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(exc))


@router.patch("/{case_code}", response_model=UnreadCaseResponse)
async def update_unread_case(
    case_code: str,
    payload: UnreadCaseUpdate,
    service: UnreadCaseService = Depends(get_service),
) -> UnreadCaseResponse:
    try:
        return await service.update_unread_case(case_code, payload)
    except NotFoundError as exc:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(exc))


@router.post("/batch/mark-delivered", response_model=BulkMarkDeliveredResponse)
async def mark_unread_cases_delivered(
    payload: BulkMarkDeliveredRequest,
    service: UnreadCaseService = Depends(get_service),
) -> BulkMarkDeliveredResponse:
    updated = await service.mark_delivered(payload)
    if not updated.updated:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="No se actualizaron casos")
    return updated

