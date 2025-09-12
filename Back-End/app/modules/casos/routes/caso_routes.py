"""Rutas de la API para el módulo de casos."""

from typing import List, Optional, Dict, Any
from functools import wraps
from datetime import datetime
from fastapi import APIRouter, Depends, HTTPException, Query, status, Body
from motor.motor_asyncio import AsyncIOMotorDatabase
import logging

from app.modules.casos.services.caso_service import CasoService
from app.modules.casos.schemas.caso import (
    CasoCreateRequest,
    CasoCreateWithCode,
    CasoUpdate,
    CasoResponse,
    CasoSearch,
    CasoStats,
    MuestraStats,
    CasoDeleteResponse,
    PatologoInfo,
    ResultadoInfo,
    AgregarNotaAdicionalRequest
)
from app.config.database import get_database
from app.shared.schemas.common import EstadoCasoEnum
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from fastapi.responses import StreamingResponse

# Configurar logger
logger = logging.getLogger(__name__)

router = APIRouter(tags=["casos"])


def get_caso_service(database: AsyncIOMotorDatabase = Depends(get_database)) -> CasoService:
    """Dependencia para el servicio de casos."""
    return CasoService(database)


def handle_exceptions(func):
    """Decorador para manejo centralizado de excepciones."""
    @wraps(func)
    async def wrapper(*args, **kwargs):
        try:
            return await func(*args, **kwargs)
        except ConflictError as e:
            raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail=str(e))
        except NotFoundError as e:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
        except BadRequestError as e:
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
        except Exception as e:
            raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=str(e))
    return wrapper


@router.get("/siguiente-consecutivo", response_model=dict)
@handle_exceptions
async def obtener_siguiente_consecutivo(caso_service: CasoService = Depends(get_caso_service)):
    """Consultar el siguiente código consecutivo disponible (NO lo consume)."""
    codigo = await caso_service.obtener_siguiente_consecutivo()
    return {
        "codigo_consecutivo": codigo,
        "mensaje": "Este es el próximo código disponible. No se ha consumido."
    }


@router.get("/test", response_model=dict)
@handle_exceptions
async def test_endpoint():
    """Endpoint de prueba simple."""
    return {"message": "Casos router funcionando correctamente"}


@router.get("/debug-entidades", response_model=dict)
@handle_exceptions
async def debug_entidades(
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Endpoint de depuración para ver los datos reales de entidades."""
    from datetime import datetime, timedelta
    
    # Si no se proporcionan parámetros, usar el mes anterior
    if not month or not year:
        now = datetime.now()
        if now.month == 1:
            month = 12
            year = now.year - 1
        else:
            month = now.month - 1
            year = now.year
    
    # Construir filtros de fecha
    inicio = datetime(year, month, 1)
    if month == 12:
        fin = datetime(year + 1, 1, 1) - timedelta(seconds=1)
    else:
        fin = datetime(year, month + 1, 1) - timedelta(seconds=1)
    
    # Obtener datos de depuración desde el repositorio
    debug_data = await caso_service.repository.get_debug_entidades(inicio, fin, entity)
    
    return {
        "periodo": {"month": month, "year": year, "entity": entity},
        "filtros": {"inicio": inicio.isoformat(), "fin": fin.isoformat()},
        "datos_raw": debug_data
    }


# -------------------------------
# Endpoints de gestión de casos
# -------------------------------

@router.post("/", response_model=CasoResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def crear_caso(
    caso_data: CasoCreateRequest,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Crear un nuevo caso."""
    return await caso_service.crear_caso(caso_data, "sistema")


@router.post("/con-codigo", response_model=CasoResponse, status_code=status.HTTP_201_CREATED)
@handle_exceptions
async def crear_caso_con_codigo(
    caso_data: CasoCreateWithCode,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Crear un nuevo caso con código específico."""
    return await caso_service.crear_caso_con_codigo(caso_data, "sistema")


@router.get("/", response_model=List[CasoResponse])
@handle_exceptions
async def listar_casos(
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(100, ge=1, le=1000, description="Número máximo de registros"),
    estado: Optional[EstadoCasoEnum] = Query(None, description="Filtrar por estado"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Listar casos con paginación y filtros básicos."""
    filtros = {"estado": estado.value} if estado else {}
    return await caso_service.listar_casos(skip=skip, limit=limit, filtros=filtros)


@router.post("/buscar", response_model=List[CasoResponse])
@handle_exceptions
async def buscar_casos(
    search_params: CasoSearch,
    skip: int = Query(0, ge=0, description="Número de registros a omitir"),
    limit: int = Query(1000, ge=1, le=5000, description="Número máximo de registros"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Búsqueda avanzada de casos con paginación."""
    return await caso_service.buscar_casos(search_params, skip=skip, limit=limit)


@router.get("/estadisticas", response_model=CasoStats)
@handle_exceptions
async def obtener_estadisticas(caso_service: CasoService = Depends(get_caso_service)):
    """Obtener estadísticas de casos."""
    return await caso_service.obtener_estadisticas()


@router.get("/estadisticas-muestras", response_model=MuestraStats)
@handle_exceptions
async def obtener_estadisticas_muestras(caso_service: CasoService = Depends(get_caso_service)):
    """Obtener estadísticas de muestras."""
    return await caso_service.obtener_estadisticas_muestras()


@router.get("/casos-por-mes/{year}", response_model=dict)
@handle_exceptions
async def obtener_casos_por_mes(
    year: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas de casos por mes para un año específico."""
    # Validar que el año sea razonable
    if year < 2020 or year > 2030:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST, 
            detail="El año debe estar entre 2020 y 2030"
        )
    
    return await caso_service.obtener_casos_por_mes(year)


@router.get("/oportunidad-por-mes/{year}", response_model=dict)
@handle_exceptions
async def obtener_oportunidad_por_mes(
    year: int,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Porcentaje de oportunidad por cada mes del año: (entregados <=6 días) / entregados."""
    if year < 2020 or year > 2030:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="El año debe estar entre 2020 y 2030")
    return await caso_service.obtener_oportunidad_por_mes(year)




@router.get("/estadisticas/test", response_model=dict)
@handle_exceptions
async def test_estadisticas():
    """Endpoint de prueba para verificar que las rutas funcionan."""
    return {"message": "Endpoint de estadísticas funcionando correctamente"}


@router.get("/estadisticas-oportunidad-mensual", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_oportunidad_mensual(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas de oportunidad del mes anterior y comparación con el mes anterior a este."""
    return await caso_service.obtener_estadisticas_oportunidad_mensual()


@router.get("/estadisticas-oportunidad-mensual-detalle", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_oportunidad_mensual_detalle(
    year: Optional[int] = Query(None, description="Año (YYYY)"),
    month: Optional[int] = Query(None, description="Mes (1-12)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener detalle de oportunidad por prueba y por patólogo para el mes/año indicado.
    Si no se envían parámetros, usa el mes inmediatamente anterior.
    """
    return await caso_service.obtener_estadisticas_oportunidad_mensual_detalle(year, month)


# -------------------------------
# Endpoints de consulta por código
# -------------------------------

@router.get("/caso-code/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def obtener_caso_por_codigo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener un caso por código de caso."""
    return await caso_service.obtener_caso_por_caso_code(caso_code)


# -------------------------------
# Endpoints de consulta por criterios
# -------------------------------

@router.get("/paciente/{numero_documento}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_paciente(
    numero_documento: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos de un paciente por documento."""
    return await caso_service.obtener_casos_por_paciente(numero_documento)


@router.get("/patologo/{patologo_codigo}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_patologo(
    patologo_codigo: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos asignados a un patólogo."""
    return await caso_service.obtener_casos_por_patologo(patologo_codigo)


@router.get("/estado/{estado}", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_por_estado(
    estado: EstadoCasoEnum,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener casos por estado."""
    return await caso_service.obtener_casos_por_estado(estado)


# -------------------------------
# Endpoints de filtros especiales
# -------------------------------

@router.get("/sin-patologo", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_sin_patologo(caso_service: CasoService = Depends(get_caso_service)):
    """Obtener casos sin patólogo asignado."""
    return await caso_service.obtener_casos_sin_patologo()


@router.get("/vencidos", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_vencidos(caso_service: CasoService = Depends(get_caso_service)):
    """Obtener casos vencidos."""
    return await caso_service.obtener_casos_vencidos()


@router.get("/firmados", response_model=List[CasoResponse])
@handle_exceptions
async def obtener_casos_firmados(caso_service: CasoService = Depends(get_caso_service)):
    """Obtener casos con resultados firmados."""
    return await caso_service.obtener_casos_firmados()


# -------------------------------
# Endpoints de gestión de patólogos
# -------------------------------

@router.put("/caso-code/{caso_code}/asignar-patologo", response_model=CasoResponse)
@handle_exceptions
async def asignar_patologo(
    caso_code: str,
    patologo_info: PatologoInfo,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Asignar patólogo a un caso por código de caso."""
    return await caso_service.asignar_patologo_por_caso_code(caso_code, patologo_info, "sistema")

@router.put("/caso-code/{caso_code}/asignar-patologo-por-codigo", response_model=CasoResponse)
@handle_exceptions
async def asignar_patologo_por_codigo(
    caso_code: str,
    patologo_codigo: str = Query(..., description="Código del patólogo a asignar"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Asignar patólogo a un caso usando solo el código del patólogo (obtiene información completa automáticamente)."""
    return await caso_service.asignar_patologo_por_codigo(caso_code, patologo_codigo, "sistema")

@router.put("/caso-code/{caso_code}/sincronizar-firma-patologo", response_model=CasoResponse)
@handle_exceptions
async def sincronizar_firma_patologo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Sincronizar la firma del patólogo asignado a un caso."""
    return await caso_service.sincronizar_firma_patologo(caso_code)

@router.put("/sincronizar-firmas-patologos")
@handle_exceptions
async def sincronizar_firmas_patologos_masivo(
    caso_service: CasoService = Depends(get_caso_service)
):
    """Sincronizar las firmas de todos los patólogos asignados en todos los casos."""
    return await caso_service.sincronizar_firmas_patologos_masivo()


@router.delete("/caso-code/{caso_code}/desasignar-patologo", response_model=CasoResponse)
@handle_exceptions
async def desasignar_patologo(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Desasignar patólogo de un caso por código de caso."""
    return await caso_service.desasignar_patologo_por_caso_code(caso_code, "sistema")


# -------------------------------
# Endpoints de gestión de casos
# -------------------------------

@router.put("/caso-code/{caso_code}", response_model=CasoResponse)
@handle_exceptions
async def actualizar_caso(
    caso_code: str,
    caso_update: CasoUpdate,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Actualizar un caso por código de caso."""
    return await caso_service.actualizar_caso_por_caso_code(caso_code, caso_update, "sistema")


@router.delete("/caso-code/{caso_code}", response_model=CasoDeleteResponse)
@handle_exceptions
async def eliminar_caso(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Eliminar un caso por código de caso (eliminación permanente)."""
    await caso_service.eliminar_caso_por_caso_code(caso_code)
    return CasoDeleteResponse(
        message=f"El caso {caso_code} ha sido eliminado exitosamente",
        caso_code=caso_code
    )

# -------------------------------
# Endpoints de resultados del caso
# -------------------------------

@router.get("/caso-code/{caso_code}/resultado", response_model=ResultadoInfo)
@handle_exceptions
async def obtener_resultado(
    caso_code: str,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener resultado del caso por código de caso."""
    return await caso_service.obtener_resultado_por_caso_code(caso_code)


@router.put("/caso-code/{caso_code}/resultado", response_model=CasoResponse)
@handle_exceptions
async def upsert_resultado(
    caso_code: str,
    resultado: ResultadoInfo,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Crear o actualizar resultado del caso por código de caso."""
    return await caso_service.agregar_o_actualizar_resultado_por_caso_code(caso_code, resultado, "sistema")


@router.get("/caso-code/{caso_code}/pdf")
@handle_exceptions
async def generar_pdf_caso(
    caso_code: str,
    database: AsyncIOMotorDatabase = Depends(get_database)
):
    """Generar PDF del caso usando Playwright y plantilla HTML."""
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
    """Firmar el resultado del caso por código de caso."""
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
    """Firmar el resultado del caso incluyendo diagnósticos CIE-10 y CIEO."""
    return await caso_service.firmar_resultado_con_diagnosticos(
        caso_code, 
        patologo_codigo, 
        diagnostico_cie10, 
        diagnostico_cieo
    )


# -------------------------------
# Endpoints de estadísticas
# -------------------------------

@router.get("/entidades-por-patologo", response_model=dict)
@handle_exceptions
async def obtener_entidades_por_patologo(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener entidades donde ha trabajado un patólogo específico."""
    return await caso_service.obtener_entidades_por_patologo(patologo, month, year)


@router.get("/pruebas-por-patologo", response_model=dict)
@handle_exceptions
async def obtener_pruebas_por_patologo(
    patologo: str = Query(..., description="Nombre del patólogo"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener pruebas realizadas por un patólogo específico."""
    return await caso_service.obtener_pruebas_por_patologo(patologo, month, year)


# -------------------------------
# Endpoints de estadísticas de entidades
# -------------------------------

@router.get("/estadisticas-entidades-mensual", response_model=dict)
@handle_exceptions
async def obtener_estadisticas_entidades_mensual(
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas de entidades por mes/año con distribución de ambulatorios y hospitalizados.

    Nota: Se revirtió parámetro experimental 'all_states' para mantener la firma original.
    """
    return await caso_service.obtener_estadisticas_entidades_mensual(month, year, entity)


@router.get("/detalle-entidad", response_model=dict)
@handle_exceptions
async def obtener_detalle_entidad(
    entidad: str = Query(..., description="Nombre de la entidad"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener detalles completos de una entidad específica."""
    return await caso_service.obtener_detalle_entidad(entidad, month, year)


@router.get("/patologos-por-entidad", response_model=dict)
@handle_exceptions
async def obtener_patologos_por_entidad(
    entidad: str = Query(..., description="Nombre de la entidad"),
    month: Optional[int] = Query(None, ge=1, le=12, description="Mes (1-12)"),
    year: Optional[int] = Query(None, description="Año"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener patólogos que han trabajado en una entidad específica."""
    return await caso_service.obtener_patologos_por_entidad(entidad, month, year)

# ============================================================================
# ENDPOINTS PARA ESTADÍSTICAS DE PRUEBAS
# ============================================================================

@router.get("/estadisticas-pruebas-mensual")
async def obtener_estadisticas_pruebas_mensual(
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener estadísticas de pruebas por mes/año y opcionalmente por entidad."""
    try:
        result = await caso_service.obtener_estadisticas_pruebas_mensual(month, year, entity)
        return {
            "success": True,
            "data": result,
            "message": f"Estadísticas de pruebas obtenidas exitosamente para {month}/{year}"
        }
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener estadísticas de pruebas: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/detalle-prueba/{codigo_prueba}")
async def obtener_detalle_prueba(
    codigo_prueba: str,
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener detalles completos de una prueba específica."""
    try:
        result = await caso_service.obtener_detalle_prueba(codigo_prueba, month, year, entity)
        return {
            "success": True,
            "data": result,
            "message": f"Detalles de la prueba {codigo_prueba} obtenidos exitosamente"
        }
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener detalle de prueba: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )


@router.get("/patologos-por-prueba/{codigo_prueba}")
async def obtener_patologos_por_prueba(
    codigo_prueba: str,
    month: int = Query(..., description="Mes (1-12)", ge=1, le=12),
    year: int = Query(..., description="Año (2020-2030)", ge=2020, le=2030),
    entity: Optional[str] = Query(None, description="Nombre de la entidad (opcional)"),
    caso_service: CasoService = Depends(get_caso_service)
):
    """Obtener patólogos que han trabajado en una prueba específica."""
    try:
        result = await caso_service.obtener_patologos_por_prueba(codigo_prueba, month, year, entity)
        return {
            "success": True,
            "data": result,
            "message": f"Patólogos de la prueba {codigo_prueba} obtenidos exitosamente"
        }
    except BadRequestError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error(f"Error al obtener patólogos por prueba: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Error interno del servidor: {str(e)}"
        )

@router.post("/caso-code/{caso_code}/notas-adicionales", response_model=CasoResponse)
@handle_exceptions
async def agregar_nota_adicional(
    caso_code: str,
    nota_data: AgregarNotaAdicionalRequest,
    caso_service: CasoService = Depends(get_caso_service)
):
    """Agregar una nota adicional a un caso completado."""
    return await caso_service.agregar_nota_adicional(caso_code, nota_data.model_dump(), "sistema")