from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime
import asyncio

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.casos.models.caso import Caso, ResultadoInfo as ModelResultadoInfo
from app.modules.casos.schemas.caso import (
    CasoCreate, CasoCreateRequest, CasoCreateWithCode, CasoUpdate, CasoResponse,
    CasoSearch, CasoStats, MuestraStats, PatologoInfo, ResultadoInfo, AgregarNotaAdicionalRequest
)
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from app.shared.schemas.common import EstadoCasoEnum


class CasoService:
    def __init__(self, database: Any):
        # Importar repositorios aquí para evitar import circular
        from app.modules.casos.repositories.caso_repository import CasoRepository
        from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository
        self.repository = CasoRepository(database)
        self.consecutivo_repository = ConsecutivoRepository(database)
    
    async def crear_caso(self, caso_data: CasoCreateRequest, usuario_id: str) -> CasoResponse:
        caso_code = await self._generar_codigo_consecutivo()
        caso_dict = {**caso_data.model_dump(), "caso_code": caso_code, "ingresado_por": usuario_id, "actualizado_por": usuario_id}
        caso = await self.repository.create(CasoCreate.model_validate(caso_dict))
        return self._to_response(caso)
    
    async def crear_caso_con_codigo(self, caso_data: CasoCreateWithCode, usuario_id: str) -> CasoResponse:
        if await self.repository.get_by_caso_code(caso_data.caso_code):
            raise ConflictError(f"Ya existe un caso con el código {caso_data.caso_code}")
        caso_dict = {**caso_data.model_dump(), "ingresado_por": usuario_id, "actualizado_por": usuario_id}
        caso = await self.repository.create(CasoCreate.model_validate(caso_dict))
        return self._to_response(caso)
    
    async def obtener_siguiente_consecutivo(self) -> str:
        return await self._consultar_proximo_consecutivo()
    
    async def _consultar_proximo_consecutivo(self) -> str:
        current_year = datetime.now().year
        proximo_numero = await self.consecutivo_repository.consultar_proximo_numero(current_year)
        return f"{current_year}-{proximo_numero:05d}"
    
    async def _generar_codigo_consecutivo(self) -> str:
        current_year = datetime.now().year
        siguiente_numero = await self.consecutivo_repository.obtener_siguiente_numero(current_year)
        return f"{current_year}-{siguiente_numero:05d}"
    
    async def obtener_caso_por_caso_code(self, CasoCode: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        return self._to_response(caso)
    
    async def listar_casos(self, skip: int = 0, limit: int = 100, filtros: Optional[Dict[str, Any]] = None, sort_field: str = "caso_code", sort_direction: int = -1) -> List[CasoResponse]:
        casos = await self.repository.get_multi(skip=skip, limit=limit, filters=filtros, sort_field=sort_field, sort_direction=sort_direction)
        return [self._to_response(caso) for caso in casos]
    
    async def buscar_casos(self, search_params: CasoSearch, skip: int = 0, limit: int = 1000) -> List[CasoResponse]:
        casos = await self.repository.search_casos(search_params, skip=skip, limit=limit)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_paciente(self, paciente_code: str) -> List[CasoResponse]:
        casos = await self.repository.get_by_paciente_code(paciente_code)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_patologo(self, patologo_codigo: str) -> List[CasoResponse]:
        casos = await self.repository.get_casos_by_patologo(patologo_codigo)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_estado(self, estado: EstadoCasoEnum) -> List[CasoResponse]:
        casos = await self.repository.get_casos_by_estado(estado)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_sin_patologo(self) -> List[CasoResponse]:
        casos = await self.repository.get_casos_sin_patologo()
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_vencidos(self) -> List[CasoResponse]:
        casos = await self.repository.get_casos_vencidos()
        return [self._to_response(caso) for caso in casos]
    
    async def actualizar_caso_por_caso_code(self, CasoCode: str, caso_update: CasoUpdate, usuario_id: str) -> CasoResponse:
        caso_existente = await self.repository.get_by_caso_code(CasoCode)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        update_data = caso_update.model_dump(exclude_unset=True)
        
        if "patologo_asignado" in update_data and update_data["patologo_asignado"]:
            patologo_dict = update_data["patologo_asignado"]
            patologo_dict.pop("firma", None)
            try:
                from bson import ObjectId
                if (patologo_dict.get("codigo") and len(patologo_dict["codigo"]) == 24 and 
                    all(c in '0123456789abcdef' for c in patologo_dict["codigo"].lower())):
                    from app.modules.patologos.repositories.patologo_repository import PatologoRepository
                    from app.shared.services.user_management import UserManagementService
                    pat_repo = PatologoRepository(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                    user_mgmt = UserManagementService(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                    raw = await pat_repo.collection.find_one({"_id": ObjectId(patologo_dict["codigo"])})
                    if raw:
                        patologo_dict["codigo"] = raw.get("patologo_code", patologo_dict["codigo"])
                        patologo_dict["nombre"] = raw.get("patologo_name", patologo_dict.get("nombre"))
            except Exception:
                pass
            patologo_dict.pop("firma", None)
        
        if "paciente" in update_data and "fecha_actualizacion" not in update_data["paciente"]:
            update_data["paciente"]["fecha_actualizacion"] = datetime.utcnow()
        
        update_data.update({"actualizado_por": usuario_id, "fecha_actualizacion": datetime.utcnow()})
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise NotFoundError(f"Error al actualizar el caso {CasoCode}")
        
        return self._to_response(caso_actualizado)
    
    async def eliminar_caso_por_caso_code(self, CasoCode: str) -> bool:
        if not await self.repository.get_by_caso_code(CasoCode):
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not await self.repository.delete_by_caso_code(CasoCode):
            raise BadRequestError(f"Error al eliminar el caso {CasoCode}")
        return True
    
    async def asignar_patologo_por_caso_code(self, CasoCode: str, patologo_info: PatologoInfo, usuario_id: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if caso.patologo_asignado:
            raise ConflictError("El caso ya tiene un patólogo asignado")
        if caso.estado == EstadoCasoEnum.COMPLETADO:
            raise BadRequestError("No se pueden asignar patólogos a casos completados")
        
        patologo_dict = patologo_info.model_dump()
        patologo_dict.pop("firma", None)
        try:
            from bson import ObjectId
            if (patologo_dict.get("codigo") and len(patologo_dict["codigo"]) == 24 and 
                all(c in '0123456789abcdef' for c in patologo_dict["codigo"].lower())):
                from app.modules.patologos.repositories.patologo_repository import PatologoRepository
                from app.shared.services.user_management import UserManagementService
                pat_repo = PatologoRepository(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                user_mgmt = UserManagementService(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                raw = await pat_repo.collection.find_one({"_id": ObjectId(patologo_dict["codigo"])})
                if raw:
                    patologo_dict["codigo"] = raw.get("patologo_code", patologo_dict["codigo"])
                    patologo_dict["nombre"] = raw.get("patologo_name", patologo_dict.get("nombre"))
        except Exception:
            pass
        patologo_dict.pop("firma", None)
        
        caso_actualizado = await self.repository.asignar_patologo_por_caso_code(CasoCode, patologo_dict)
        if not caso_actualizado:
            raise BadRequestError("No se pudo asignar el patólogo")
        
        return self._to_response(caso_actualizado)
    
    async def asignar_patologo_por_codigo(self, CasoCode: str, patologo_codigo: str, usuario_id: str) -> CasoResponse:
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        try:
            patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(patologo_codigo)
            return await self.asignar_patologo_por_caso_code(CasoCode, PatologoInfo(**patologo_info_dict), usuario_id)
        except NotFoundError:
            raise NotFoundError(f"Patólogo con código {patologo_codigo} no encontrado")
    
    async def sincronizar_firma_patologo(self, CasoCode: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.patologo_asignado:
            raise BadRequestError("El caso no tiene un patólogo asignado")
        
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        try:
            patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(caso.patologo_asignado.codigo)
            patologo_info_dict.pop("firma", None)
            caso_actualizado = await self.repository.asignar_patologo_por_caso_code(CasoCode, patologo_info_dict)
            if not caso_actualizado:
                raise BadRequestError("No se pudo sincronizar la información del patólogo")
            return self._to_response(caso_actualizado)
        except NotFoundError:
            raise NotFoundError(f"Patólogo con código {caso.patologo_asignado.codigo} no encontrado")
    
    async def sincronizar_firmas_patologos_masivo(self) -> Dict[str, Any]:
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        casos_con_patologos = await self.repository.collection.find({
            "patologo_asignado": {"$exists": True, "$ne": None}
        }).to_list(length=None)
        
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        casos_actualizados = casos_con_error = 0
        errores = []
        
        for caso_doc in casos_con_patologos:
            try:
                if caso_doc.get("patologo_asignado") and caso_doc["patologo_asignado"].get("codigo"):
                    patologo_codigo = caso_doc["patologo_asignado"]["codigo"]
                    patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(patologo_codigo)
                    patologo_info_dict.pop("firma", None)
                    await self.repository.collection.update_one(
                        {"_id": caso_doc["_id"]},
                        {"$set": {
                            "patologo_asignado": patologo_info_dict,
                            "fecha_actualizacion": datetime.utcnow()
                        }}
                    )
                    casos_actualizados += 1
            except Exception as e:
                casos_con_error += 1
                errores.append({
                    "caso_id": str(caso_doc.get("_id", "unknown")),
                    "caso_code": caso_doc.get("caso_code", "unknown"),
                    "error": str(e)
                })
        
        return {
            "mensaje": "Sincronización masiva completada",
            "casos_actualizados": casos_actualizados,
            "casos_con_error": casos_con_error,
            "total_casos_procesados": len(casos_con_patologos),
            "errores": errores[:10]
        }
    
    async def desasignar_patologo_por_caso_code(self, CasoCode: str, usuario_id: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.patologo_asignado:
            raise BadRequestError("El caso no tiene patólogo asignado")
        
        caso_actualizado = await self.repository.desasignar_patologo_por_caso_code(CasoCode)
        if not caso_actualizado:
            raise BadRequestError("No se pudo desasignar el patólogo")
        
        return self._to_response(caso_actualizado)
    
    async def actualizar_resultado_por_caso_code(self, CasoCode: str, resultado_info: ResultadoInfo, usuario_id: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.patologo_asignado:
            raise BadRequestError("El caso debe tener un patólogo asignado para actualizar el resultado")
        
        resultado_dict = {**resultado_info.model_dump(exclude_unset=True), "fecha_resultado": datetime.utcnow()}
        update_data = {
            "resultado": resultado_dict,
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo actualizar el resultado")
        
        return self._to_response(caso_actualizado)
    
    async def agregar_o_actualizar_resultado_por_caso_code(self, CasoCode: str, resultado_data: ResultadoInfo, usuario_id: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")

        resultado_dict = resultado_data.model_dump(exclude_unset=True)
        update_data = {
            "resultado": resultado_dict, 
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        if caso.estado == EstadoCasoEnum.EN_PROCESO:
            update_data["estado"] = EstadoCasoEnum.POR_FIRMAR
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo actualizar el resultado del caso")

        return self._to_response(caso_actualizado)

    async def obtener_resultado_por_caso_code(self, CasoCode: str) -> ModelResultadoInfo:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.resultado:
            raise NotFoundError("El caso no tiene resultado registrado")
        return caso.resultado

    async def firmar_resultado_por_caso_code(self, CasoCode: str, patologo_codigo: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.resultado:
            raise BadRequestError("El caso no tiene resultado para firmar")
        if caso.estado not in [EstadoCasoEnum.POR_FIRMAR, EstadoCasoEnum.POR_ENTREGAR]:
            raise BadRequestError(f"El caso debe estar en estado 'Por firmar' o 'Por entregar' para poder firmarlo. Estado actual: {caso.estado}")
        
        resultado_actualizado = caso.resultado.model_copy()
        nuevo_estado = EstadoCasoEnum.POR_ENTREGAR if caso.estado == EstadoCasoEnum.POR_FIRMAR else caso.estado
        
        update_data = {
            "resultado": resultado_actualizado.model_dump(),
            "fecha_firma": datetime.utcnow(),
            "estado": nuevo_estado,
            "actualizado_por": patologo_codigo,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo firmar el resultado")
        
        return self._to_response(caso_actualizado)
    
    async def firmar_resultado_con_diagnosticos(self, CasoCode: str, patologo_codigo: str, diagnostico_cie10: Optional[Dict[str, Any]] = None, diagnostico_cieo: Optional[Dict[str, Any]] = None) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not caso.resultado:
            raise BadRequestError("El caso no tiene resultado para firmar")
        if caso.estado not in [EstadoCasoEnum.POR_FIRMAR, EstadoCasoEnum.POR_ENTREGAR]:
            raise BadRequestError(f"El caso debe estar en estado 'Por firmar' o 'Por entregar' para poder firmarlo. Estado actual: {caso.estado}")
        
        resultado_actualizado = caso.resultado.model_copy()
        if diagnostico_cie10:
            resultado_actualizado.diagnostico_cie10 = diagnostico_cie10
        if diagnostico_cieo:
            resultado_actualizado.diagnostico_cieo = diagnostico_cieo
        
        nuevo_estado = EstadoCasoEnum.POR_ENTREGAR if caso.estado == EstadoCasoEnum.POR_FIRMAR else caso.estado
        
        update_data = {
            "resultado": resultado_actualizado.model_dump(),
            "fecha_firma": datetime.utcnow(),
            "estado": nuevo_estado,
            "actualizado_por": patologo_codigo,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo firmar el resultado")
        
        return self._to_response(caso_actualizado)
    
    async def cambiar_estado_por_caso_code(self, CasoCode: str, nuevo_estado: EstadoCasoEnum, usuario_id: str) -> CasoResponse:
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        if not self._validar_transicion_estado(caso.estado, nuevo_estado):
            raise BadRequestError(f"Transición de estado inválida: {caso.estado} -> {nuevo_estado}")
        
        update_data = {
            "estado": nuevo_estado,
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo cambiar el estado del caso")
        
        return self._to_response(caso_actualizado)
    
    async def obtener_estadisticas(self) -> CasoStats:
        stats_data = await self.repository.get_estadisticas()
        casos_vencidos = await self.repository.get_casos_vencidos()
        casos_sin_patologo = await self.repository.get_casos_sin_patologo()
        stats_data.casos_vencidos = len(casos_vencidos)
        stats_data.casos_sin_patologo = len(casos_sin_patologo)
        return stats_data
    
    async def obtener_estadisticas_muestras(self) -> MuestraStats:
        return await self.repository.get_estadisticas_muestras()
    
    async def obtener_casos_por_año(self, año: int) -> List[CasoResponse]:
        casos = await self.repository.get_casos_por_año(año)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_mes(self, año: int) -> Dict[str, Any]:
        casos = await self.repository.get_casos_por_año(año)
        datos_mensuales = [0] * 12
        
        for caso in casos:
            if hasattr(caso, 'fecha_creacion') and caso.fecha_creacion:
                datos_mensuales[caso.fecha_creacion.month - 1] += 1
        
        return {
            "datos": datos_mensuales,
            "total": sum(datos_mensuales),
            "año": año
        }

    async def obtener_oportunidad_por_mes(self, año: int) -> Dict[str, Any]:
        datos = await self.repository.get_oportunidad_por_mes_agregado(año)
        return {"año": año, "porcentaje_por_mes": datos}
    
    async def obtener_estadisticas_oportunidad_mensual(self) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        ahora = datetime.utcnow()
        
        if ahora.month == 1:
            mes_anterior_inicio = datetime(ahora.year - 1, 12, 1)
            mes_anterior_fin = datetime(ahora.year, 1, 1) - timedelta(seconds=1)
        else:
            mes_anterior_inicio = datetime(ahora.year, ahora.month - 1, 1)
            mes_anterior_fin = datetime(ahora.year, ahora.month, 1) - timedelta(seconds=1)
        
        if mes_anterior_inicio.month == 1:
            mes_anterior_anterior_inicio = datetime(mes_anterior_inicio.year - 1, 12, 1)
            mes_anterior_anterior_fin = mes_anterior_inicio - timedelta(seconds=1)
        else:
            mes_anterior_anterior_inicio = datetime(mes_anterior_inicio.year, mes_anterior_inicio.month - 1, 1)
            mes_anterior_anterior_fin = mes_anterior_inicio - timedelta(seconds=1)
        
        pipeline = [
            {
                "$match": {
                    "fecha_creacion": {"$gte": mes_anterior_anterior_inicio, "$lt": mes_anterior_fin},
                    "estado": "Completado",
                    "fecha_entrega": {"$exists": True, "$ne": None}
                }
            },
            {
                "$project": {
                    "fecha_creacion": 1,
                    "fecha_entrega": 1,
                    "oportunidad": 1,
                    "mes": {
                        "$cond": {
                            "if": {"$gte": ["$fecha_creacion", mes_anterior_inicio]},
                            "then": "mes_anterior",
                            "else": "mes_anterior_anterior"
                        }
                    }
                }
            },
            {
                "$group": {
                    "_id": "$mes",
                    "total_casos": {"$sum": 1},
                    "casos_dentro_oportunidad": {
                        "$sum": {"$cond": [{"$lte": ["$oportunidad", 5]}, 1, 0]}
                    },
                    "tiempo_promedio": {"$avg": "$oportunidad"}
                }
            }
        ]
        
        resultados = await self.repository.collection.aggregate(pipeline, allowDiskUse=True, maxTimeMS=15000).to_list(length=None)
        
        stats_mes_anterior = stats_mes_anterior_anterior = None
        for resultado in resultados:
            if resultado["_id"] == "mes_anterior":
                stats_mes_anterior = resultado
            else:
                stats_mes_anterior_anterior = resultado
        
        if stats_mes_anterior:
            total_mes_anterior = stats_mes_anterior["total_casos"]
            casos_dentro_oportunidad_mes_anterior = stats_mes_anterior["casos_dentro_oportunidad"]
            casos_fuera_oportunidad_mes_anterior = total_mes_anterior - casos_dentro_oportunidad_mes_anterior
            porcentaje_oportunidad_mes_anterior = (casos_dentro_oportunidad_mes_anterior / total_mes_anterior * 100) if total_mes_anterior > 0 else 0
            tiempo_promedio = stats_mes_anterior["tiempo_promedio"] or 0
        else:
            total_mes_anterior = casos_dentro_oportunidad_mes_anterior = casos_fuera_oportunidad_mes_anterior = porcentaje_oportunidad_mes_anterior = tiempo_promedio = 0
        
        if stats_mes_anterior_anterior:
            total_mes_anterior_anterior = stats_mes_anterior_anterior["total_casos"]
            casos_dentro_oportunidad_mes_anterior_anterior = stats_mes_anterior_anterior["casos_dentro_oportunidad"]
            porcentaje_oportunidad_mes_anterior_anterior = (casos_dentro_oportunidad_mes_anterior_anterior / total_mes_anterior_anterior * 100) if total_mes_anterior_anterior > 0 else 0
        else:
            total_mes_anterior_anterior = casos_dentro_oportunidad_mes_anterior_anterior = porcentaje_oportunidad_mes_anterior_anterior = 0
        
        cambio_porcentual = porcentaje_oportunidad_mes_anterior - porcentaje_oportunidad_mes_anterior_anterior if porcentaje_oportunidad_mes_anterior_anterior > 0 else (100 if porcentaje_oportunidad_mes_anterior > 0 else 0)
        
        meses_es = {1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                   7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"}
        nombre_mes = f"{meses_es[mes_anterior_inicio.month]} {mes_anterior_inicio.year}"
        
        return {
            "porcentaje_oportunidad": round(porcentaje_oportunidad_mes_anterior, 2),
            "cambio_porcentual": round(cambio_porcentual, 2),
            "tiempo_promedio": round(tiempo_promedio, 1),
            "casos_dentro_oportunidad": casos_dentro_oportunidad_mes_anterior,
            "casos_fuera_oportunidad": casos_fuera_oportunidad_mes_anterior,
            "total_casos_mes_anterior": total_mes_anterior,
            "mes_anterior": {
                "nombre": nombre_mes,
                "inicio": mes_anterior_inicio.isoformat(),
                "fin": mes_anterior_fin.isoformat()
            }
        }

    async def obtener_estadisticas_oportunidad_mensual_detalle(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        ahora = datetime.utcnow()
        if year and month:
            if year < 2020 or year > 2030 or month < 1 or month > 12:
                raise BadRequestError("Parámetros de año o mes fuera de rango")
            inicio = datetime(year, month, 1)
            fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        else:
            if ahora.month == 1:
                inicio = datetime(ahora.year - 1, 12, 1)
                fin = datetime(ahora.year, 1, 1) - timedelta(seconds=1)
            else:
                inicio = datetime(ahora.year, ahora.month - 1, 1)
                fin = datetime(ahora.year, ahora.month, 1) - timedelta(seconds=1)

        detalle = await self.repository.get_oportunidad_detalle_por_mes_agregado(inicio, fin)
        return {
            "pruebas": detalle.get("pruebas", []),
            "patologos": detalle.get("patologos", []),
            "resumen": detalle.get("resumen", {"total": 0, "dentro": 0, "fuera": 0}),
            "periodo": {"inicio": inicio.isoformat(), "fin": fin.isoformat()}
        }
    
    def _es_caso_vencido(self, caso) -> bool:
        fecha_creacion = getattr(caso, 'fecha_creacion', None)
        if not fecha_creacion:
            return False
        fecha_entrega = getattr(caso, 'fecha_entrega', None)
        if fecha_entrega:
            return (fecha_entrega - fecha_creacion).days > 6
        if caso.estado != EstadoCasoEnum.COMPLETADO:
            return (datetime.utcnow() - fecha_creacion).days > 6
        return False
    
    def _calcular_tiempo_promedio_procesamiento(self, casos) -> float:
        if not casos:
            return 0.0
        
        tiempos_procesamiento = []
        for caso in casos:
            if caso.estado == EstadoCasoEnum.COMPLETADO and hasattr(caso, 'fecha_creacion') and caso.fecha_creacion:
                fecha_completado = caso.fecha_entrega if hasattr(caso, 'fecha_entrega') and caso.fecha_entrega else (caso.fecha_firma if hasattr(caso, 'fecha_firma') and caso.fecha_firma else None)
                if fecha_completado:
                    tiempo = (fecha_completado - caso.fecha_creacion).days
                    if tiempo >= 0:
                        tiempos_procesamiento.append(tiempo)
        
        return sum(tiempos_procesamiento) / len(tiempos_procesamiento) if tiempos_procesamiento else 0.0
    
    def _validar_transicion_estado(self, estado_actual: EstadoCasoEnum, nuevo_estado: EstadoCasoEnum) -> bool:
        transiciones_validas = {
            EstadoCasoEnum.EN_PROCESO: [EstadoCasoEnum.POR_FIRMAR],
            EstadoCasoEnum.POR_FIRMAR: [EstadoCasoEnum.POR_ENTREGAR],
            EstadoCasoEnum.POR_ENTREGAR: [EstadoCasoEnum.COMPLETADO],
            EstadoCasoEnum.COMPLETADO: []
        }
        return nuevo_estado in transiciones_validas.get(estado_actual, [])
    
    def _to_response(self, caso: Caso) -> CasoResponse:
        caso_dict = caso.model_dump(by_alias=True, mode='json')
        caso_dict["id"] = str(caso.id)
        return CasoResponse(**caso_dict)

    async def obtener_entidades_por_patologo(self, patologo: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        entidades = await self.repository.get_entidades_por_patologo(patologo, filtros_fecha)
        
        return {
            "patologo": patologo,
            "entidades": entidades,
            "total_entidades": len(entidades),
            "periodo": {
                "month": month,
                "year": year,
                "filtrado": bool(month and year)
            }
        }

    async def obtener_pruebas_por_patologo(self, patologo: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        pruebas = await self.repository.get_pruebas_por_patologo(patologo, filtros_fecha)
        
        return {
            "patologo": patologo,
            "pruebas": pruebas,
            "total_pruebas": len(pruebas),
            "periodo": {
                "month": month,
                "year": year,
                "filtrado": bool(month and year)
            }
        }

    async def obtener_estadisticas_entidades_mensual(self, month: Optional[int] = None, year: Optional[int] = None, entity: Optional[str] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        if not month or not year:
            now = datetime.now()
            month = 12 if now.month == 1 else now.month - 1
            year = now.year - 1 if now.month == 1 else now.year
        
        inicio = datetime(year, month, 1)
        fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        estadisticas = await self.repository.get_estadisticas_entidades_mensual(inicio, fin, entity)
        
        return {
            "entities": estadisticas["entities"],
            "summary": estadisticas["summary"],
            "periodo": {"month": month, "year": year, "entity": entity}
        }

    async def obtener_detalle_entidad(self, entidad: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        if not month or not year:
            now = datetime.now()
            month = 12 if now.month == 1 else now.month - 1
            year = now.year - 1 if now.month == 1 else now.year
        
        inicio = datetime(year, month, 1)
        fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
        
        detalles = await self.repository.get_detalle_entidad(entidad, inicio, fin)
        
        return {
            "entidad": entidad,
            "detalles": detalles,
            "periodo": {"month": month, "year": year}
        }

    async def obtener_patologos_por_entidad(self, entidad: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        from datetime import datetime, timedelta
        
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            fin = datetime(year + 1, 1, 1) - timedelta(seconds=1) if month == 12 else datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        patologos = await self.repository.get_patologos_por_entidad(entidad, filtros_fecha)
        
        return {
            "entidad": entidad,
            "patologos": patologos,
            "total_patologos": len(patologos),
            "periodo": {
                "month": month,
                "year": year,
                "filtrado": bool(month and year)
            }
        }

    async def obtener_estadisticas_pruebas_mensual(self, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        pruebas_stats = await self.repository.get_estadisticas_pruebas_mensual(month, year, entity)
        total_solicitadas = sum(p["total_solicitadas"] for p in pruebas_stats)
        total_completadas = sum(p["total_completadas"] for p in pruebas_stats)
        tiempo_promedio = sum(p["tiempo_promedio"] for p in pruebas_stats) / len(pruebas_stats) if pruebas_stats else 0.0
        
        return {
            "pruebas": pruebas_stats,
            "resumen": {
                "totalSolicitadas": total_solicitadas,
                "totalCompletadas": total_completadas,
                "tiempoPromedio": round(tiempo_promedio, 1)
            }
        }

    async def obtener_detalle_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        if not codigo_prueba:
            raise BadRequestError("El código de prueba es requerido")
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        return await self.repository.get_detalle_prueba(codigo_prueba, month, year, entity)

    async def obtener_patologos_por_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        if not codigo_prueba:
            raise BadRequestError("El código de prueba es requerido")
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        return await self.repository.get_patologos_por_prueba(codigo_prueba, month, year, entity)
    
    async def agregar_nota_adicional(self, caso_code: str, nota_data: Dict[str, Any], usuario_id: str) -> CasoResponse:
        caso_existente = await self.repository.get_by_caso_code(caso_code)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {caso_code} no encontrado")
        if caso_existente.estado != EstadoCasoEnum.COMPLETADO:
            raise BadRequestError(f"Solo se pueden agregar notas adicionales a casos completados. Estado actual: {caso_existente.estado}")
        
        nueva_nota = {
            "fecha": datetime.utcnow(),
            "nota": nota_data.get("nota", ""),
            "agregado_por": nota_data.get("agregado_por", usuario_id)
        }
        
        update_data = {
            "$push": {"notas_adicionales": nueva_nota},
            "$set": {
                "fecha_actualizacion": datetime.utcnow(),
                "actualizado_por": usuario_id
            }
        }
        
        caso_actualizado = await self.repository.update_by_caso_code_optimized(caso_code, update_data)
        if not caso_actualizado:
            raise NotFoundError(f"Error al actualizar el caso {caso_code}")
        
        return self._to_response(caso_actualizado)

    # ============================================================================
    # MÉTODOS OPTIMIZADOS CON CACHÉ Y PAGINACIÓN
    # ============================================================================

    async def obtener_caso_por_caso_code_cached(self, caso_code: str) -> CasoResponse:
        """Obtener caso por código con caché."""
        caso = await self.repository.get_caso_cached(caso_code)
        if not caso:
            raise NotFoundError(f"Caso con código {caso_code} no encontrado")
        return self._to_response(caso)

    async def listar_casos_optimized(
        self,
        cursor: Optional[str] = None,
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None,
        sort_field: str = "fecha_creacion",
        sort_direction: int = -1
    ) -> Dict[str, Any]:
        """Listar casos con paginación cursor-based optimizada."""
        pagination_result = await self.repository.get_multi_optimized(
            cursor=cursor,
            limit=limit,
            filters=filtros,
            sort_field=sort_field,
            sort_direction=sort_direction
        )
        
        # Convertir resultados a CasoResponse
        casos = [self._to_response(Caso(**doc)) for doc in pagination_result.get("results", [])]
        
        return {
            "casos": casos,
            "next_cursor": pagination_result.get("next_cursor"),
            "has_more": pagination_result.get("has_more", False),
            "count": pagination_result.get("count", 0)
        }

    async def obtener_estadisticas_cached(self) -> CasoStats:
        """Obtener estadísticas con caché."""
        return await self.repository.get_estadisticas_cached()

    async def obtener_estadisticas_muestras_cached(self) -> MuestraStats:
        """Obtener estadísticas de muestras con caché."""
        return await self.repository.get_estadisticas_muestras_cached()

    async def obtener_casos_por_mes_cached(self, año: int) -> Dict[str, Any]:
        """Obtener casos por mes con caché."""
        return await self.repository.get_casos_por_mes_cached(año)

    async def obtener_oportunidad_por_mes_cached(self, año: int) -> Dict[str, Any]:
        """Obtener oportunidad por mes con caché."""
        return await self.repository.get_oportunidad_por_mes_cached(año)

    async def buscar_casos_optimized(
        self,
        search_params: CasoSearch,
        cursor: Optional[str] = None,
        limit: int = 1000
    ) -> Dict[str, Any]:
        """Búsqueda optimizada con paginación cursor-based."""
        pagination_result = await self.repository.search_casos_optimized(
            search_params=search_params,
            cursor=cursor,
            limit=limit
        )
        
        # Convertir resultados a CasoResponse
        casos = [self._to_response(Caso(**doc)) for doc in pagination_result.get("results", [])]
        
        return {
            "casos": casos,
            "next_cursor": pagination_result.get("next_cursor"),
            "has_more": pagination_result.get("has_more", False),
            "count": pagination_result.get("count", 0)
        }

    async def obtener_casos_por_estado_optimized(
        self,
        estado: EstadoCasoEnum,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtener casos por estado con paginación optimizada."""
        pagination_result = await self.repository.get_casos_by_estado_optimized(
            estado=estado,
            cursor=cursor,
            limit=limit
        )
        
        # Convertir resultados a CasoResponse
        casos = [self._to_response(Caso(**doc)) for doc in pagination_result.get("results", [])]
        
        return {
            "casos": casos,
            "next_cursor": pagination_result.get("next_cursor"),
            "has_more": pagination_result.get("has_more", False),
            "count": pagination_result.get("count", 0)
        }

    async def obtener_casos_por_patologo_optimized(
        self,
        patologo_codigo: str,
        cursor: Optional[str] = None,
        limit: int = 100
    ) -> Dict[str, Any]:
        """Obtener casos por patólogo con paginación optimizada."""
        pagination_result = await self.repository.get_casos_by_patologo_optimized(
            patologo_codigo=patologo_codigo,
            cursor=cursor,
            limit=limit
        )
        
        # Convertir resultados a CasoResponse
        casos = [self._to_response(Caso(**doc)) for doc in pagination_result.get("results", [])]
        
        return {
            "casos": casos,
            "next_cursor": pagination_result.get("next_cursor"),
            "has_more": pagination_result.get("has_more", False),
            "count": pagination_result.get("count", 0)
        }

    async def actualizar_caso_por_caso_code_optimized(
        self,
        caso_code: str,
        caso_update: CasoUpdate,
        usuario_id: str
    ) -> CasoResponse:
        """Actualizar caso con invalidación de caché."""
        caso_existente = await self.repository.get_by_caso_code(caso_code)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {caso_code} no encontrado")
        
        update_data = caso_update.model_dump(exclude_unset=True)
        
        # Procesar patólogo si está presente
        if "patologo_asignado" in update_data and update_data["patologo_asignado"]:
            patologo_dict = update_data["patologo_asignado"]
            patologo_dict.pop("firma", None)
            try:
                from bson import ObjectId
                if (patologo_dict.get("codigo") and len(patologo_dict["codigo"]) == 24 and 
                    all(c in '0123456789abcdef' for c in patologo_dict["codigo"].lower())):
                    from app.modules.patologos.repositories.patologo_repository import PatologoRepository
                    pat_repo = PatologoRepository(self.repository.database)
                    raw = await pat_repo.collection.find_one({"_id": ObjectId(patologo_dict["codigo"])})
                    if raw:
                        patologo_dict["codigo"] = raw.get("patologo_code", patologo_dict["codigo"])
                        patologo_dict["nombre"] = raw.get("patologo_name", patologo_dict.get("nombre"))
            except Exception:
                pass
        
        # Actualizar fecha de actualización del paciente si es necesario
        if "paciente" in update_data and "fecha_actualizacion" not in update_data["paciente"]:
            update_data["paciente"]["fecha_actualizacion"] = datetime.utcnow()
        
        update_data.update({
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        })
        
        caso_actualizado = await self.repository.update_by_caso_code_optimized(caso_code, update_data)
        if not caso_actualizado:
            raise NotFoundError(f"Error al actualizar el caso {caso_code}")
        
        return self._to_response(caso_actualizado)

    async def eliminar_caso_por_caso_code_optimized(self, caso_code: str) -> bool:
        """Eliminar caso con invalidación de caché."""
        if not await self.repository.get_by_caso_code(caso_code):
            raise NotFoundError(f"Caso con código {caso_code} no encontrado")
        
        result = await self.repository.delete_by_caso_code_optimized(caso_code)
        if not result:
            raise BadRequestError(f"Error al eliminar el caso {caso_code}")
        
        return True

    # ============================================================================
    # MÉTODOS DE OPTIMIZACIÓN AVANZADA
    # ============================================================================

    async def bulk_update_casos(
        self,
        updates: List[Dict[str, Any]],
        usuario_id: str
    ) -> Dict[str, Any]:
        """Actualizar múltiples casos en una sola operación."""
        # Preparar datos para bulk update
        bulk_updates = []
        for update in updates:
            bulk_updates.append({
                "caso_code": update["caso_code"],
                "data": {
                    **update["data"],
                    "actualizado_por": usuario_id,
                    "fecha_actualizacion": datetime.utcnow()
                }
            })
        
        result = await self.repository.bulk_update_casos(bulk_updates)
        return result

    async def get_casos_with_projection(
        self,
        projection: Dict[str, int],
        filters: Optional[Dict[str, Any]] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener casos con proyección específica para optimizar transferencia de datos."""
        return await self.repository.get_casos_with_projection(
            projection=projection,
            filters=filters,
            limit=limit
        )

    async def get_estadisticas_optimized(self) -> CasoStats:
        """Obtener estadísticas usando agregaciones optimizadas."""
        return await self.repository.get_estadisticas_optimized()

    # ============================================================================
    # MÉTODOS DE INVALIDACIÓN DE CACHÉ
    # ============================================================================

    async def invalidate_caso_cache(self, caso_code: str):
        """Invalidar caché de un caso específico."""
        await self.repository.cache_service.invalidate_caso_cache(caso_code)

    async def invalidate_stats_cache(self):
        """Invalidar caché de estadísticas."""
        await self.repository.cache_service.invalidate_stats_cache()

    async def clear_all_cache(self):
        """Limpiar todo el caché del módulo de casos."""
        patterns = [
            "caso_detail:*",
            "caso_stats:*",
            "muestra_stats:*",
            "casos_por_mes:*",
            "oportunidad_stats:*",
            "entidades_stats:*",
            "pruebas_stats:*"
        ]
        
        for pattern in patterns:
            await self.repository.cache_service.delete_pattern(pattern)