"""Rutas de la API para el módulo de casos."""

from typing import List, Optional, Dict, Any
from functools import wraps
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from fastapi.responses import StreamingResponse
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.modules.casos.services.caso_service import CasoService
from app.modules.casos.schemas.caso import (
    CasoCreateRequest, CasoCreateWithCode, CasoUpdate, CasoResponse,
    CasoSearch, CasoStats, MuestraStats, CasoDeleteResponse,
    PatologoInfo, ResultadoInfo, AgregarNotaAdicionalRequest
)
from app.config.database import get_database
from app.shared.schemas.common import EstadoCasoEnum
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError

logger = logging.getLogger(__name__)
router = APIRouter(tags=["casos"])


def get_caso_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> CasoService:
    return CasoService(database)

def validate_year(year: int) -> None:
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=400, detail="El año debe estar entre 2020 y 2030")


def handle_exceptions(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConflictError as e:
            raise HTTPException(status_code=409, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=404, detail=str(e))
        except BadRequestError as e:
            raise HTTPException(status_code=400, detail=str(e))
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}")
            raise HTTPException(status_code=500, detail=str(e))
    return wrapper


@router.get("/siguiente-consecutivo", response_model=dict)
@handle_exceptions
async def obtener_siguiente_consecutivo(caso_service: CasoService = Depends(get_caso_service)):
    codigo = await caso_service.obtener_siguiente_consecutivo()
    return {"codigo_consecutivo": codigo, "mensaje": "Este es el próximo código disponible. No se ha consumido."}

@router.get("/test", response_model=dict)
@handle_exceptions
async def test_endpoint():
    return {"message": "Casos router funcionando correctamente"}


@router.get("/debug-entidades", response_model=dict)
@handle_exceptions
async def debug_entidades(
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    from datetime import datetime, timedelta
    
    if not month or not year:
        now = datetime.now()
        month = 12 if now.month == 1 else now.month - 1
        year = now.year - 1 if now.month == 1 else now.year
    
    inicio = datetime(year, month, 1)
    fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    debug_data = await caso_service.repository.get_debug_entidades(inicio, fin, entity)
    
    return {
        "periodo": {"month": month, "year": year, "entity": entity},
        "filtros": {"inicio": inicio.isoformat(), "fin": fin.isoformat()},
        "datos_raw": debug_data
    }


# Gestión de casos
@router.post("/", response_model=CasoResponse, status_code=201)
@handle_exceptions
async def crear_caso(
    caso_data: CasoCreateRequest,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.crear_caso(caso_data, "sistema")

@router.post("/con-codigo", response_model=CasoResponse, status_code=201)
@handle_exceptions
async def crear_caso_con_codigo(
    caso_data: CasoCreateWithCode,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.crear_caso_con_codigo(caso_data, "sistema")


@router.get("/", response_model=List[CasoResponse])
@handle_exceptions
async def listar_casos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    sort_field: str = Query("caso_code", description="Campo de ordenamiento"),
    sort_direction: int = Query(-1, description="Dirección del ordenamiento (-1 desc, 1 asc)"),
    estado: Optional[EstadoCasoEnum] = Query(None, description="Filtrar por estado"),
    caso_service: CasoService = Depends(get_caso_service)
):
    filtros = {"estado": estado.value} if estado else {}
    return await caso_service.listar_casos(skip=skip, limit=limit, filtros=filtros, sort_field=sort_field, sort_direction=sort_direction)

@router.post("/buscar", response_model=List[CasoResponse])
@handle_exceptions
async def buscar_casos(
    search_params: CasoSearch,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(1000000, ge=1, le=2000000, description="Número máximo de registros"),
    sort_field: str = Query("caso_code", description="Campo de ordenamiento"),
    sort_direction: int = Query(-1, description="Dirección del ordenamiento (-1 desc, 1 asc)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    resultados = await caso_service.buscar_casos(search_params, skip=skip, limit=limit)
    try:
        reverse = sort_direction == -1
        resultados.sort(key=lambda c: getattr(c, sort_field, None) or "", reverse=reverse)
    except Exception:
        pass
    return resultados


@router.get("/estadisticas", response_model=CasoStats)
@handle_exceptions
async def obtener_estadisticas(caso_service: CasoService = Depends(get_caso_service)):
    return await caso_service.obtener_estadisticas()

@router.get("/estadisticas-muestras", response_model=MuestraStats)
@handle_exceptions
async def obtener_estadisticas_muestras(caso_service: CasoService = Depends(get_caso_service)):
    return await caso_service.obtener_estadisticas_muestras()


@router.get("/casos-por-mes/{year}", response_model=dict)
@handle_exceptions
async def obtener_casos_por_mes(
    year: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    validate_year(year)
    return await caso_service.obtener_casos_por_mes(year)

@router.get("/oportunidad-por-mes/{year}", response_model=dict)
@handle_exceptions
async def obtener_oportunidad_por_mes(
    year: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    validate_year(year)
    return await caso_service.obtener_oportunidad_por_mes(year)




@router.get("/estadisticas/test", response_model=dict)
@handle_exceptions
async def test_estadisticas():
    return {"message": "Endpoint de estadísticas funcionando correctamente"}

@router.get("/estadisticas-oportunidad-mensual", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_oportunidad_mensual(
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_estadisticas_oportunidad_mensual()

@router.get("/estadisticas-oportunidad-mensual-detalle", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_oportunidad_mensual_detalle(
    year: Optional[int] = Query(None, description="Año (YYYY)"),
    month: Optional[int] = Query(None, description="Mes (1-12)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_estadisticas_oportunidad_mensual_detalle(year, month)


# Consulta por código
@router.get("/caso-code/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def obtener_caso_por_codigo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_caso_por_caso_code(caso_code)


# Consulta por criterios
@router.get("/paciente/{numero_documento}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_paciente(
    numero_documento: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_casos_por_paciente(numero_documento)

@router.get("/patologo/{patologo_codigo}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_patologo(
    patologo_codigo: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_casos_por_patologo(patologo_codigo)

@router.get("/estado/{estado}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_estado(
    estado: EstadoCasoEnum,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_casos_por_estado(estado)


# Filtros especiales
@router.get("/sin-patologo", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_sin_patologo(caso_service: CasoService = Depends(get_caso_service)):
    return await caso_service.obtener_casos_sin_patologo()

@router.get("/vencidos", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_vencidos(caso_service: CasoService = Depends(get_caso_service)):
    return await caso_service.obtener_casos_vencidos()

@router.get("/firmados", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_firmados(caso_service: CasoService = Depends(get_caso_service)):
    return await caso_service.obtener_casos_firmados()


# Gestión de patólogos
@router.put("/caso-code/{caso_code}/asignar-patologo", response_model=CasoResponse)
@handle_exceptions
async def asignar_patologo(
    caso_code: str,
    patologo_info: PatologoInfo,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.asignar_patologo_por_caso_code(caso_code, patologo_info, "sistema")

@router.put("/caso-code/{caso_code}/asignar-patologo-por-codigo", response_model=CasoResponse)
@handle_exceptions
async def asignar_patologo_por_codigo(
    caso_code: str,
    patologo_codigo: str = Query(..., description="Código del patólogo a asignar"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.asignar_patologo_por_codigo(caso_code, patologo_codigo, "sistema")

@router.put("/caso-code/{caso_code}/sincronizar-firma-patologo", response_model=CasoResponse)
@handle_exceptions
async def sincronizar_firma_patologo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.sincronizar_firma_patologo(caso_code)

@router.put("/sincronizar-firmas-patologos")
@handle_exceptions
async def sincronizar_firmas_patologos_masivo(
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.sincronizar_firmas_patologos_masivo()

@router.delete("/caso-code/{caso_code}/desasignar-patologo", response_model=CasoResponse)
@handle_exceptions
async def desasignar_patologo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.desasignar_patologo_por_caso_code(caso_code, "sistema")


# Gestión de casos
@router.put("/caso-code/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def actualizar_caso(
    caso_code: str,
    caso_update: CasoUpdate,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.actualizar_caso_por_caso_code(caso_code, caso_update, "sistema")

@router.delete("/caso-code/{caso_code}", response_model=CasoDeleteResponse)
@handle_exceptions
async def eliminar_caso(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    await caso_service.eliminar_caso_por_caso_code(caso_code)
    return CasoDeleteResponse(
        message=f"El caso {caso_code} ha sido eliminado exitosamente",
        caso_code=caso_code
    )

# Resultados del caso
@router.get("/caso-code/{caso_code}/resultado", response_model=ResultadoInfo)
@handle_exceptions
async def obtener_resultado(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_resultado_por_caso_code(caso_code)

@router.put("/caso-code/{caso_code}/resultado", response_model=CasoResponse)
@handle_exceptions
async def upsert_resultado(
    caso_code: str,
    resultado: ResultadoInfo,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.agregar_o_actualizar_resultado_por_caso_code(caso_code, resultado, "sistema")


@router.get("/caso-code/{caso_code}/pdf")
@handle_exceptions
async def generar_pdf_caso(
    caso_code: str,
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    from app.modules.casos.services.pdf_service import CasePdfService
    service = CasePdfService(database)
    pdf_bytes = await service.generate_case_pdf(caso_code)
    return StreamingResponse(iter([pdf_bytes]), media_type="application/pdf", headers={
        "Content-Disposition": f"inline; filename=caso-{caso_code}.pdf"
    })


@router.post("/caso-code/{caso_code}/resultado/firmar", response_model=CasoResponse)
@handle_exceptions
async def firmar_resultado(
    caso_code: str,
    patologo_codigo: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.firmar_resultado_por_caso_code(caso_code, patologo_codigo)

@router.post("/caso-code/{caso_code}/resultado/firmar-con-diagnosticos", response_model=CasoResponse)
@handle_exceptions
async def firmar_resultado_con_diagnosticos(
    caso_code: str,
    patologo_codigo: str,
    diagnostico_cie10: Optional[Dict[str, Any]] = Body(None, description="Diagnóstico CIE-10"),
    diagnostico_cieo: Optional[Dict[str, Any]] = Body(None, description="Diagnóstico CIEO"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.firmar_resultado_con_diagnosticos(
        caso_code, patologo_codigo, diagnostico_cie10, diagnostico_cieo
    )


# Estadísticas
@router.get("/entidades-por-patologo", response_model=dict)
@handle_exceptions
async def obtener_entidades_por_patologo(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_entidades_por_patologo(patologo, month, year)

@router.get("/pruebas-por-patologo", response_model=dict)
@handle_exceptions
async def obtener_pruebas_por_patologo(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_pruebas_por_patologo(patologo, month, year)


# Estadísticas de entidades
@router.get("/estadisticas-entidades-mensual", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_entidades_mensual(
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_estadisticas_entidades_mensual(month, year, entity)

@router.get("/detalle-entidad", response_model=dict)
@handle_exceptions
async def obtener_detalle_entidad(
    entidad: str = Query(..., description="Nombre de la entidad"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_detalle_entidad(entidad, month, year)

@router.get("/patologos-por-entidad", response_model=dict)
@handle_exceptions
async def obtener_patologos_por_entidad(
    entidad: str = Query(..., description="Nombre de la entidad"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.obtener_patologos_por_entidad(entidad, month, year)

# Estadísticas de pruebas
@router.get("/estadisticas-pruebas-mensual")
@handle_exceptions
async def obtener_estadisticas_pruebas_mensual(
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    result = await caso_service.obtener_estadisticas_pruebas_mensual(month, year, entity)
    return {
        "success": True,
        "data": result,
        "message": f"Estadísticas de pruebas obtenidas exitosamente para {month}/{year}"
    }


@router.get("/detalle-prueba/{codigo_prueba}")
@handle_exceptions
async def obtener_detalle_prueba(
    codigo_prueba: str,
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    result = await caso_service.obtener_detalle_prueba(codigo_prueba, month, year, entity)
    return {
        "success": True,
        "data": result,
        "message": f"Detalles de la prueba {codigo_prueba} obtenidos exitosamente"
    }

@router.get("/patologos-por-prueba/{codigo_prueba}")
@handle_exceptions
async def obtener_patologos_por_prueba(
    codigo_prueba: str,
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    result = await caso_service.obtener_patologos_por_prueba(codigo_prueba, month, year, entity)
    return {
        "success": True,
        "data": result,
        "message": f"Patólogos de la prueba {codigo_prueba} obtenidos exitosamente"
    }

@router.post("/caso-code/{caso_code}/notas-adicionales", response_model=CasoResponse)
@handle_exceptions
async def agregar_nota_adicional(
    caso_code: str,
    nota_data: AgregarNotaAdicionalRequest,
    caso_service: CasoService = Depends(get_caso_service)
):
    return await caso_service.agregar_nota_adicional(caso_code, nota_data.model_dump(), "sistema")

# ============================================================================
# ENDPOINTS OPTIMIZADOS CON CACHÉ Y PAGINACIÓN
# ============================================================================

@router.get("/optimized/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def obtener_caso_optimized(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener caso por código con caché optimizado."""
    return await caso_service.obtener_caso_por_caso_code_cached(caso_code)

@router.get("/optimized/list", response_model=Dict[str, Any])
@handle_exceptions
async def listar_casos_optimized(
    cursor: Optional[str] = Query(None, description="Cursor para paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    estado: Optional[EstadoCasoEnum] = Query(None, description="Filtrar por estado"),
    patologo_codigo: Optional[str] = Query(None, description="Filtrar por patólogo"),
    entidad_id: Optional[str] = Query(None, description="Filtrar por entidad"),
    sort_field: str = Query("fecha_creacion", description="Campo de ordenamiento"),
    sort_direction: int = Query(-1, description="Dirección del ordenamiento (-1: desc, 1: asc)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Listar casos con paginación cursor-based optimizada."""
    # Construir filtros
    filtros = {}
    if estado:
        filtros["estado"] = estado.value
    if patologo_codigo:
        filtros["patologo_asignado.codigo"] = patologo_codigo
    if entidad_id:
        filtros["paciente.entidad_info.id"] = entidad_id
    
    return await caso_service.listar_casos_optimized(
        cursor=cursor,
        limit=limit,
        filtros=filtros,
        sort_field=sort_field,
        sort_direction=sort_direction
    )

@router.get("/optimized/stats", response_model=CasoStats)
@handle_exceptions
async def obtener_estadisticas_optimized(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas con caché optimizado."""
    return await caso_service.obtener_estadisticas_cached()

@router.get("/optimized/muestras/stats", response_model=MuestraStats)
@handle_exceptions
async def obtener_estadisticas_muestras_optimized(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas de muestras con caché optimizado."""
    return await caso_service.obtener_estadisticas_muestras_cached()

@router.get("/optimized/por-mes/{año}", response_model=Dict[str, Any])
@handle_exceptions
async def obtener_casos_por_mes_optimized(
    año: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos por mes con caché optimizado."""
    validate_year(año)
    return await caso_service.obtener_casos_por_mes_cached(año)

@router.get("/optimized/oportunidad/{año}", response_model=Dict[str, Any])
@handle_exceptions
async def obtener_oportunidad_por_mes_optimized(
    año: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener oportunidad por mes con caché optimizado."""
    validate_year(año)
    return await caso_service.obtener_oportunidad_por_mes_cached(año)

@router.post("/optimized/search", response_model=Dict[str, Any])
@handle_exceptions
async def buscar_casos_optimized(
    search_params: CasoSearch = Body(..., description="Parámetros de búsqueda"),
    cursor: Optional[str] = Query(None, description="Cursor para paginación"),
    limit: int = Query(1000, ge=1, le=5000, description="Número máximo de resultados"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Búsqueda optimizada con paginación cursor-based."""
    return await caso_service.buscar_casos_optimized(
        search_params=search_params,
        cursor=cursor,
        limit=limit
    )

@router.get("/optimized/por-estado/{estado}", response_model=Dict[str, Any])
@handle_exceptions
async def obtener_casos_por_estado_optimized(
    estado: EstadoCasoEnum,
    cursor: Optional[str] = Query(None, description="Cursor para paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos por estado con paginación optimizada."""
    return await caso_service.obtener_casos_por_estado_optimized(
        estado=estado,
        cursor=cursor,
        limit=limit
    )

@router.get("/optimized/por-patologo/{patologo_codigo}", response_model=Dict[str, Any])
@handle_exceptions
async def obtener_casos_por_patologo_optimized(
    patologo_codigo: str,
    cursor: Optional[str] = Query(None, description="Cursor para paginación"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos por patólogo con paginación optimizada."""
    return await caso_service.obtener_casos_por_patologo_optimized(
        patologo_codigo=patologo_codigo,
        cursor=cursor,
        limit=limit
    )

@router.put("/optimized/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def actualizar_caso_optimized(
    caso_code: str,
    caso_update: CasoUpdate,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Actualizar caso con invalidación de caché optimizada."""
    return await caso_service.actualizar_caso_por_caso_code_optimized(
        caso_code=caso_code,
        caso_update=caso_update,
        usuario_id="sistema"
    )

@router.delete("/optimized/{caso_code}")
@handle_exceptions
async def eliminar_caso_optimized(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Eliminar caso con invalidación de caché optimizada."""
    result = await caso_service.eliminar_caso_por_caso_code_optimized(caso_code)
    return {"message": "Caso eliminado exitosamente", "success": result}

# ============================================================================
# ENDPOINTS DE OPTIMIZACIÓN AVANZADA
# ============================================================================

@router.post("/bulk-update")
@handle_exceptions
async def bulk_update_casos(
    updates: List[Dict[str, Any]] = Body(..., description="Lista de actualizaciones"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Actualizar múltiples casos en una sola operación."""
    return await caso_service.bulk_update_casos(
        updates=updates,
        usuario_id="sistema"
    )

@router.get("/projection")
@handle_exceptions
async def get_casos_with_projection(
    projection: str = Query(..., description="Campos a incluir (JSON string)"),
    estado: Optional[EstadoCasoEnum] = Query(None, description="Filtrar por estado"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de resultados"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos con proyección específica para optimizar transferencia de datos."""
    import json
    projection_dict = json.loads(projection)
    
    filtros = {}
    if estado:
        filtros["estado"] = estado.value
    
    return await caso_service.get_casos_with_projection(
        projection=projection_dict,
        filters=filtros,
        limit=limit
    )

@router.get("/stats/optimized", response_model=CasoStats)
@handle_exceptions
async def get_estadisticas_optimized(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas usando agregaciones optimizadas."""
    return await caso_service.get_estadisticas_optimized()

# ============================================================================
# ENDPOINTS DE GESTIÓN DE CACHÉ
# ============================================================================

@router.post("/cache/invalidate/{caso_code}")
@handle_exceptions
async def invalidate_caso_cache(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Invalidar caché de un caso específico."""
    await caso_service.invalidate_caso_cache(caso_code)
    return {"message": f"Caché del caso {caso_code} invalidado exitosamente"}

@router.post("/cache/invalidate-stats")
@handle_exceptions
async def invalidate_stats_cache(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Invalidar caché de estadísticas."""
    await caso_service.invalidate_stats_cache()
    return {"message": "Caché de estadísticas invalidado exitosamente"}

@router.post("/cache/clear")
@handle_exceptions
async def clear_all_cache(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Limpiar todo el caché del módulo de casos."""
    await caso_service.clear_all_cache()
    return {"message": "Todo el caché del módulo de casos ha sido limpiado"}