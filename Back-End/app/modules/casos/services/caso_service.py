"""Servicio para la lógica de negocio de casos."""

from typing import List, Optional, Dict, Any, TYPE_CHECKING
from datetime import datetime

if TYPE_CHECKING:
    from motor.motor_asyncio import AsyncIOMotorDatabase

from app.modules.casos.repositories.caso_repository import CasoRepository
from app.modules.casos.repositories.consecutivo_repository import ConsecutivoRepository
from app.modules.casos.models.caso import Caso, ResultadoInfo as ModelResultadoInfo
from app.modules.casos.schemas.caso import (
    CasoCreate,
    CasoCreateRequest,
    CasoCreateWithCode,
    CasoUpdate,
    CasoResponse,
    CasoSearch,
    CasoStats,
    MuestraStats,
    PatologoInfo,
    ResultadoInfo,
    AgregarNotaAdicionalRequest
)
from app.core.exceptions import ConflictError, NotFoundError, BadRequestError
from app.shared.schemas.common import EstadoCasoEnum


class CasoService:
    """Servicio para la gestión de casos."""
    
    def __init__(self, database: Any):
        self.repository = CasoRepository(database)
        self.consecutivo_repository = ConsecutivoRepository(database)
    
    
    async def crear_caso(self, caso_data: CasoCreateRequest, usuario_id: str) -> CasoResponse:
        """Crear un nuevo caso con código consecutivo automático."""
        caso_code = await self._generar_codigo_consecutivo()
        
        caso_dict = caso_data.model_dump()
        caso_dict.update({
            "caso_code": caso_code,
            "ingresado_por": usuario_id,
            "actualizado_por": usuario_id
        })
        
        caso_create = CasoCreate.model_validate(caso_dict)
        caso = await self.repository.create(caso_create)
        return self._to_response(caso)
    
    async def crear_caso_con_codigo(self, caso_data: CasoCreateWithCode, usuario_id: str) -> CasoResponse:
        """Crear un nuevo caso con código específico proporcionado."""
        caso_existente = await self.repository.get_by_caso_code(caso_data.caso_code)
        if caso_existente:
            raise ConflictError(f"Ya existe un caso con el código {caso_data.caso_code}")
        
        caso_dict = caso_data.model_dump()
        caso_dict.update({
            "ingresado_por": usuario_id,
            "actualizado_por": usuario_id
        })
        
        caso_create = CasoCreate.model_validate(caso_dict)
        caso = await self.repository.create(caso_create)
        return self._to_response(caso)
    
    async def obtener_siguiente_consecutivo(self) -> str:
        """Obtener el siguiente código consecutivo disponible (solo consulta)."""
        return await self._consultar_proximo_consecutivo()
    
    async def _consultar_proximo_consecutivo(self) -> str:
        """Consulta el próximo código consecutivo sin incrementar el contador."""
        current_year = datetime.now().year
        proximo_numero = await self.consecutivo_repository.consultar_proximo_numero(current_year)
        return f"{current_year}-{proximo_numero:05d}"
    
    async def _generar_codigo_consecutivo(self) -> str:
        """Genera y consume el siguiente código consecutivo para el año actual."""
        current_year = datetime.now().year
        siguiente_numero = await self.consecutivo_repository.obtener_siguiente_numero(current_year)
        return f"{current_year}-{siguiente_numero:05d}"
    
    async def obtener_caso_por_caso_code(self, CasoCode: str) -> CasoResponse:
        """Obtener un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        return self._to_response(caso)
    
    async def listar_casos(
        self, 
        skip: int = 0, 
        limit: int = 100,
        filtros: Optional[Dict[str, Any]] = None
    ) -> List[CasoResponse]:
        """Listar casos con paginación y filtros."""
        casos = await self.repository.get_multi(skip=skip, limit=limit, filters=filtros)
        return [self._to_response(caso) for caso in casos]
    
    async def buscar_casos(self, search_params: CasoSearch, skip: int = 0, limit: int = 1000) -> List[CasoResponse]:
        """Búsqueda avanzada de casos con paginación."""
        casos = await self.repository.search_casos(search_params, skip=skip, limit=limit)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_paciente(self, paciente_code: str) -> List[CasoResponse]:
        """Obtener casos de un paciente por código."""
        casos = await self.repository.get_by_paciente_code(paciente_code)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_patologo(self, patologo_codigo: str) -> List[CasoResponse]:
        """Obtener casos asignados a un patólogo."""
        casos = await self.repository.get_casos_by_patologo(patologo_codigo)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_estado(self, estado: EstadoCasoEnum) -> List[CasoResponse]:
        """Obtener casos por estado."""
        casos = await self.repository.get_casos_by_estado(estado)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_sin_patologo(self) -> List[CasoResponse]:
        """Obtener casos sin patólogo asignado."""
        casos = await self.repository.get_casos_sin_patologo()
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_vencidos(self) -> List[CasoResponse]:
        """Obtener casos vencidos."""
        casos = await self.repository.get_casos_vencidos()
        return [self._to_response(caso) for caso in casos]
    
    async def actualizar_caso_por_caso_code(
        self, 
        CasoCode: str, 
        caso_update: CasoUpdate, 
        usuario_id: str
    ) -> CasoResponse:
        """Actualizar un caso por código de caso."""
        caso_existente = await self.repository.get_by_caso_code(CasoCode)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        update_data = caso_update.model_dump(exclude_unset=True)
        # Asegurar que el paciente tenga fecha_actualizacion
        if "paciente" in update_data and "fecha_actualizacion" not in update_data["paciente"]:
            update_data["paciente"]["fecha_actualizacion"] = datetime.utcnow()
        update_data["actualizado_por"] = usuario_id
        update_data["fecha_actualizacion"] = datetime.utcnow()

        # Log detallado del payload que se va a enviar al repositorio
        import logging, json
        logging.getLogger(__name__).info(
            "Payload update caso %s: %s", 
            CasoCode, 
            json.dumps(update_data, default=str)
        )
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise NotFoundError(f"Error al actualizar el caso {CasoCode}")
        
        return self._to_response(caso_actualizado)
    
    async def eliminar_caso_por_caso_code(self, CasoCode: str) -> bool:
        """Eliminar un caso por código de caso."""
        caso_existente = await self.repository.get_by_caso_code(CasoCode)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        resultado = await self.repository.delete_by_caso_code(CasoCode)
        if not resultado:
            raise BadRequestError(f"Error al eliminar el caso {CasoCode}")
        
        return True
    
    async def asignar_patologo_por_caso_code(
        self, 
        CasoCode: str, 
        patologo_info: PatologoInfo, 
        usuario_id: str
    ) -> CasoResponse:
        """Asignar patólogo a un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if caso.patologo_asignado:
            raise ConflictError("El caso ya tiene un patólogo asignado")
        
        if caso.estado == EstadoCasoEnum.COMPLETADO:
            raise BadRequestError("No se pueden asignar patólogos a casos completados")
        
        # Normalizar datos del patólogo: si el campo codigo parece ser un ObjectId (24 hex) buscar patólogo real
        patologo_dict = patologo_info.model_dump()
        try:
            from bson import ObjectId
            if patologo_dict.get("codigo") and len(patologo_dict["codigo"]) == 24 and all(c in '0123456789abcdef' for c in patologo_dict["codigo"].lower()):
                # Intentar buscar patólogo por _id
                from app.modules.patologos.repositories.patologo_repository import PatologoRepository
                from app.modules.patologos.services.patologo_service import PatologoService
                from app.shared.services.user_management import UserManagementService
                pat_repo = PatologoRepository(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                user_mgmt = UserManagementService(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                pat_service = PatologoService(pat_repo, user_mgmt)
                # Buscar manualmente en la colección por _id
                raw = await pat_repo.collection.find_one({"_id": ObjectId(patologo_dict["codigo"])})
                if raw:
                    # Reemplazar campos correctos
                    patologo_dict["codigo"] = raw.get("patologo_code", patologo_dict["codigo"])
                    patologo_dict["nombre"] = raw.get("patologo_name", patologo_dict.get("nombre"))
                    patologo_dict["firma"] = raw.get("firma") or patologo_dict.get("firma")
        except Exception:
            pass
        # Si falta firma pero tenemos codigo normalizado, intentar completarla
        if patologo_dict.get("codigo") and not patologo_dict.get("firma"):
            try:
                from app.modules.patologos.repositories.patologo_repository import PatologoRepository
                from app.modules.patologos.services.patologo_service import PatologoService
                from app.shared.services.user_management import UserManagementService
                pat_repo = PatologoRepository(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                user_mgmt = UserManagementService(self.repository.database if hasattr(self.repository, 'database') else self.repository.db)
                pat_service = PatologoService(pat_repo, user_mgmt)
                pat = await pat_service.get_by_code(patologo_dict["codigo"]) if hasattr(pat_service, 'get_by_code') else None
                if pat and getattr(pat, 'firma', None):
                    patologo_dict['firma'] = pat.firma
            except Exception:
                pass
        caso_actualizado = await self.repository.asignar_patologo_por_caso_code(CasoCode, patologo_dict)
        
        if not caso_actualizado:
            raise BadRequestError("No se pudo asignar el patólogo")
        
        return self._to_response(caso_actualizado)
    
    async def asignar_patologo_por_codigo(
        self, 
        CasoCode: str, 
        patologo_codigo: str, 
        usuario_id: str
    ) -> CasoResponse:
        """Asignar patólogo a un caso obteniendo automáticamente su información completa incluyendo firma."""
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        # Obtener la información completa del patólogo
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        try:
            patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(patologo_codigo)
            patologo_info = PatologoInfo(**patologo_info_dict)
            return await self.asignar_patologo_por_caso_code(CasoCode, patologo_info, usuario_id)
        except NotFoundError as e:
            raise NotFoundError(f"Patólogo con código {patologo_codigo} no encontrado")
    
    async def sincronizar_firma_patologo(self, CasoCode: str) -> CasoResponse:
        """Sincronizar la firma del patólogo asignado a un caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.patologo_asignado:
            raise BadRequestError("El caso no tiene un patólogo asignado")
        
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        # Obtener la información actualizada del patólogo
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        try:
            patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(caso.patologo_asignado.codigo)
            
            # Actualizar la información del patólogo en el caso
            caso_actualizado = await self.repository.asignar_patologo_por_caso_code(CasoCode, patologo_info_dict)
            
            if not caso_actualizado:
                raise BadRequestError("No se pudo sincronizar la información del patólogo")
            
            return self._to_response(caso_actualizado)
            
        except NotFoundError as e:
            raise NotFoundError(f"Patólogo con código {caso.patologo_asignado.codigo} no encontrado")
    
    async def sincronizar_firmas_patologos_masivo(self) -> Dict[str, Any]:
        """Sincronizar las firmas de todos los patólogos asignados en todos los casos."""
        from app.modules.patologos.services.patologo_service import PatologoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        from app.shared.services.user_management import UserManagementService
        
        # Obtener todos los casos con patólogos asignados
        casos_con_patologos = await self.repository.collection.find({
            "patologo_asignado": {"$exists": True, "$ne": None}
        }).to_list(length=None)
        
        patologo_repository = PatologoRepository(self.repository.db)
        user_management_service = UserManagementService(self.repository.db)
        patologo_service = PatologoService(patologo_repository, user_management_service)
        
        casos_actualizados = 0
        casos_con_error = 0
        errores = []
        
        for caso_doc in casos_con_patologos:
            try:
                if caso_doc.get("patologo_asignado") and caso_doc["patologo_asignado"].get("codigo"):
                    patologo_codigo = caso_doc["patologo_asignado"]["codigo"]
                    
                    # Verificar si ya tiene firma
                    current_firma = caso_doc["patologo_asignado"].get("firma")
                    if current_firma:
                        continue  # Ya tiene firma, saltar
                    
                    # Obtener información actualizada del patólogo
                    patologo_info_dict = await patologo_service.get_patologo_info_for_assignment(patologo_codigo)
                    
                    # Actualizar en la base de datos
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
            "errores": errores[:10]  # Solo los primeros 10 errores
        }
    
    
    
    async def desasignar_patologo_por_caso_code(
        self, 
        CasoCode: str, 
        usuario_id: str
    ) -> CasoResponse:
        """Desasignar patólogo de un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.patologo_asignado:
            raise BadRequestError("El caso no tiene patólogo asignado")
        
        # Desasignar patólogo
        caso_actualizado = await self.repository.desasignar_patologo_por_caso_code(CasoCode)
        
        if not caso_actualizado:
            raise BadRequestError("No se pudo desasignar el patólogo")
        
        return self._to_response(caso_actualizado)
    
    async def actualizar_resultado_por_caso_code(
        self, 
        CasoCode: str, 
        resultado_info: ResultadoInfo, 
        usuario_id: str
    ) -> CasoResponse:
        """Actualizar resultado de un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.patologo_asignado:
            raise BadRequestError("El caso debe tener un patólogo asignado para actualizar el resultado")
        
        resultado_dict = resultado_info.model_dump(exclude_unset=True)
        resultado_dict["fecha_resultado"] = datetime.utcnow()
        
        update_data = {
            "resultado": resultado_dict,
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        if not caso_actualizado:
            raise BadRequestError("No se pudo actualizar el resultado")
        
        return self._to_response(caso_actualizado)
    
    async def agregar_o_actualizar_resultado_por_caso_code(
        self, 
        CasoCode: str, 
        resultado_data: ResultadoInfo, 
        usuario_id: str
    ) -> CasoResponse:
        """Agrega o actualiza la información del resultado de un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")

        resultado_dict = resultado_data.model_dump(exclude_unset=True)
    # Se elimina control de fecha_resultado interno

        # Si el caso está en estado EN_PROCESO y se está guardando un resultado,
        # cambiar el estado a POR_FIRMAR
        update_data = {
            "resultado": resultado_dict, 
            "actualizado_por": usuario_id,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        # Cambiar estado a POR_FIRMAR si está en EN_PROCESO
        if caso.estado == EstadoCasoEnum.EN_PROCESO:
            update_data["estado"] = EstadoCasoEnum.POR_FIRMAR
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        
        if not caso_actualizado:
            raise BadRequestError("No se pudo actualizar el resultado del caso")

        return self._to_response(caso_actualizado)

    async def obtener_resultado_por_caso_code(self, CasoCode: str) -> ModelResultadoInfo:
        """Obtiene la información del resultado de un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.resultado:
            raise NotFoundError("El caso no tiene resultado registrado")
        
        return caso.resultado

    async def firmar_resultado_por_caso_code(
        self, 
        CasoCode: str, 
        patologo_codigo: str
    ) -> CasoResponse:
        """Firma el resultado de un caso por código de caso."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.resultado:
            raise BadRequestError("El caso no tiene resultado para firmar")
        
        # Validar que el caso esté en estado POR_FIRMAR o POR_ENTREGAR
        if caso.estado not in [EstadoCasoEnum.POR_FIRMAR, EstadoCasoEnum.POR_ENTREGAR]:
            raise BadRequestError(f"El caso debe estar en estado 'Por firmar' o 'Por entregar' para poder firmarlo. Estado actual: {caso.estado}")
        
        resultado_actualizado = caso.resultado.model_copy()
        
        # Solo cambiar a "Por entregar" si el caso actual está en "Por firmar"
        nuevo_estado = EstadoCasoEnum.POR_ENTREGAR if caso.estado == EstadoCasoEnum.POR_FIRMAR else caso.estado
        
        update_data = {
            "resultado": resultado_actualizado.model_dump(),
            "fecha_firma": datetime.utcnow(),  # sólo a nivel de caso
            "estado": nuevo_estado,
            "actualizado_por": patologo_codigo,
            "fecha_actualizacion": datetime.utcnow()
        }
        
        caso_actualizado = await self.repository.update_by_caso_code(CasoCode, update_data)
        
        if not caso_actualizado:
            raise BadRequestError("No se pudo firmar el resultado")
        
        return self._to_response(caso_actualizado)
    
    async def firmar_resultado_con_diagnosticos(
        self, 
        CasoCode: str, 
        patologo_codigo: str,
        diagnostico_cie10: Optional[Dict[str, Any]] = None,
        diagnostico_cieo: Optional[Dict[str, Any]] = None
    ) -> CasoResponse:
        """Firma el resultado de un caso incluyendo diagnósticos CIE-10 y CIEO."""
        caso = await self.repository.get_by_caso_code(CasoCode)
        if not caso:
            raise NotFoundError(f"Caso con código {CasoCode} no encontrado")
        
        if not caso.resultado:
            raise BadRequestError("El caso no tiene resultado para firmar")
        
        # Validar que el caso esté en estado POR_FIRMAR o POR_ENTREGAR
        if caso.estado not in [EstadoCasoEnum.POR_FIRMAR, EstadoCasoEnum.POR_ENTREGAR]:
            raise BadRequestError(f"El caso debe estar en estado 'Por firmar' o 'Por entregar' para poder firmarlo. Estado actual: {caso.estado}")
        
        resultado_actualizado = caso.resultado.model_copy()
        
        # Actualizar diagnósticos si se proporcionan
        if diagnostico_cie10:
            resultado_actualizado.diagnostico_cie10 = diagnostico_cie10
        
        if diagnostico_cieo:
            resultado_actualizado.diagnostico_cieo = diagnostico_cieo
        
        # Firma: únicamente se registra fecha_firma a nivel de caso
        
        # Solo cambiar a "Por entregar" si el caso actual está en "Por firmar"
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
    
    async def cambiar_estado_por_caso_code(
        self, 
        CasoCode: str, 
        nuevo_estado: EstadoCasoEnum, 
        usuario_id: str
    ) -> CasoResponse:
        """Cambiar estado de un caso por código de caso."""
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
        """Obtener estadísticas de casos."""
        stats_data = await self.repository.get_estadisticas()
        
        # El repository ya devuelve un CasoStats, solo necesitamos actualizarlo con datos adicionales
        casos_vencidos = await self.repository.get_casos_vencidos()
        casos_sin_patologo = await self.repository.get_casos_sin_patologo()
        
        # Actualizar los campos que se calculan dinámicamente
        stats_data.casos_vencidos = len(casos_vencidos)
        stats_data.casos_sin_patologo = len(casos_sin_patologo)
        
        return stats_data
    
    async def obtener_estadisticas_muestras(self) -> MuestraStats:
        """Obtener estadísticas de muestras."""
        return await self.repository.get_estadisticas_muestras()
    
    async def obtener_casos_por_año(self, año: int) -> List[CasoResponse]:
        """Obtener todos los casos de un año específico."""
        casos = await self.repository.get_casos_por_año(año)
        return [self._to_response(caso) for caso in casos]
    
    async def obtener_casos_por_mes(self, año: int) -> Dict[str, Any]:
        """Obtener estadísticas de casos por mes para un año específico."""
        casos = await self.repository.get_casos_por_año(año)
        
        # Inicializar array con 12 meses (0-11)
        datos_mensuales = [0] * 12
        
        # Contar casos por mes (por fecha_creacion)
        for caso in casos:
            if hasattr(caso, 'fecha_creacion') and caso.fecha_creacion:
                mes = caso.fecha_creacion.month - 1  # Convertir a índice 0-11
                datos_mensuales[mes] += 1
        
        # Calcular total
        total = sum(datos_mensuales)
        
        return {
            "datos": datos_mensuales,
            "total": total,
            "año": año
        }

    async def obtener_oportunidad_por_mes(self, año: int) -> Dict[str, Any]:
        """Porcentaje de oportunidad por cada mes del año vía agregación."""
        datos = await self.repository.get_oportunidad_por_mes_agregado(año)
        return {"año": año, "porcentaje_por_mes": datos}
    
    async def obtener_estadisticas_oportunidad_mensual(self) -> Dict[str, Any]:
        """Obtener estadísticas de oportunidad del mes anterior y comparación con el mes anterior a este."""
        from datetime import datetime, timedelta
        
        # Calcular fechas
        ahora = datetime.utcnow()
        
        # Mes anterior (mes inmediatamente anterior)
        if ahora.month == 1:
            mes_anterior_inicio = datetime(ahora.year - 1, 12, 1)
            mes_anterior_fin = datetime(ahora.year, 1, 1) - timedelta(seconds=1)
        else:
            mes_anterior_inicio = datetime(ahora.year, ahora.month - 1, 1)
            mes_anterior_fin = datetime(ahora.year, ahora.month, 1) - timedelta(seconds=1)
        
        # Mes anterior al anterior (mes anterior a este)
        if mes_anterior_inicio.month == 1:
            mes_anterior_anterior_inicio = datetime(mes_anterior_inicio.year - 1, 12, 1)
            mes_anterior_anterior_fin = mes_anterior_inicio - timedelta(seconds=1)
        else:
            mes_anterior_anterior_inicio = datetime(mes_anterior_inicio.year, mes_anterior_inicio.month - 1, 1)
            mes_anterior_anterior_fin = mes_anterior_inicio - timedelta(seconds=1)
        
        # Obtener casos del mes anterior
        casos_mes_anterior = await self.repository.get_casos_por_fecha_rango(
            mes_anterior_inicio, mes_anterior_fin
        )
        
        # Obtener casos del mes anterior al anterior
        casos_mes_anterior_anterior = await self.repository.get_casos_por_fecha_rango(
            mes_anterior_anterior_inicio, mes_anterior_anterior_fin
        )
        
        # Calcular estadísticas del mes anterior
        total_mes_anterior = len(casos_mes_anterior)
        casos_vencidos_mes_anterior = sum(1 for caso in casos_mes_anterior if self._es_caso_vencido(caso))
        casos_dentro_oportunidad_mes_anterior = total_mes_anterior - casos_vencidos_mes_anterior
        porcentaje_oportunidad_mes_anterior = (
            (casos_dentro_oportunidad_mes_anterior / total_mes_anterior * 100) 
            if total_mes_anterior > 0 else 0
        )
        
        # Calcular estadísticas del mes anterior al anterior
        total_mes_anterior_anterior = len(casos_mes_anterior_anterior)
        casos_vencidos_mes_anterior_anterior = sum(1 for caso in casos_mes_anterior_anterior if self._es_caso_vencido(caso))
        casos_dentro_oportunidad_mes_anterior_anterior = total_mes_anterior_anterior - casos_vencidos_mes_anterior_anterior
        porcentaje_oportunidad_mes_anterior_anterior = (
            (casos_dentro_oportunidad_mes_anterior_anterior / total_mes_anterior_anterior * 100) 
            if total_mes_anterior_anterior > 0 else 0
        )
        
        # Calcular cambio porcentual
        cambio_porcentual = 0
        if porcentaje_oportunidad_mes_anterior_anterior > 0:
            cambio_porcentual = porcentaje_oportunidad_mes_anterior - porcentaje_oportunidad_mes_anterior_anterior
        elif porcentaje_oportunidad_mes_anterior > 0:
            cambio_porcentual = 100  # Si no había casos antes pero ahora sí
        
        # Calcular tiempo promedio de procesamiento del mes anterior
        tiempo_promedio = self._calcular_tiempo_promedio_procesamiento(casos_mes_anterior)
        
        # Formatear nombre del mes en español
        import locale
        try:
            # Intentar configurar locale en español
            locale.setlocale(locale.LC_TIME, 'es_ES.UTF-8')
            nombre_mes = mes_anterior_inicio.strftime("%B %Y")
        except:
            # Si falla, usar un mapeo manual
            meses_es = {
                1: "enero", 2: "febrero", 3: "marzo", 4: "abril", 5: "mayo", 6: "junio",
                7: "julio", 8: "agosto", 9: "septiembre", 10: "octubre", 11: "noviembre", 12: "diciembre"
            }
            nombre_mes = f"{meses_es[mes_anterior_inicio.month]} {mes_anterior_inicio.year}"
        
        return {
            "porcentaje_oportunidad": round(porcentaje_oportunidad_mes_anterior, 2),
            "cambio_porcentual": round(cambio_porcentual, 2),
            "tiempo_promedio": round(tiempo_promedio, 1),
            "casos_dentro_oportunidad": casos_dentro_oportunidad_mes_anterior,
            "casos_fuera_oportunidad": casos_vencidos_mes_anterior,
            "total_casos_mes_anterior": total_mes_anterior,
            "mes_anterior": {
                "nombre": nombre_mes,
                "inicio": mes_anterior_inicio.isoformat(),
                "fin": mes_anterior_fin.isoformat()
            }
        }

    async def obtener_estadisticas_oportunidad_mensual_detalle(self, year: Optional[int] = None, month: Optional[int] = None) -> Dict[str, Any]:
        """Detalle por mes seleccionado (o mes anterior por defecto) agrupado por prueba y por patólogo.
        Se consideran casos con fecha_entrega dentro del rango del mes y se calcula oportunidad por (fecha_entrega - fecha_creacion) <= 6 días.
        """
        from datetime import datetime, timedelta
        ahora = datetime.utcnow()
        if year and month:
            # Validación de rango simple
            if year < 2020 or year > 2030 or month < 1 or month > 12:
                raise BadRequestError("Parámetros de año o mes fuera de rango")
            inicio = datetime(year, month, 1)
            # calcular fin del mes
            if month == 12:
                fin = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin = datetime(year, month + 1, 1) - timedelta(seconds=1)
        else:
            # Rango del mes inmediatamente anterior
            if ahora.month == 1:
                inicio = datetime(ahora.year - 1, 12, 1)
                fin = datetime(ahora.year, 1, 1) - timedelta(seconds=1)
            else:
                inicio = datetime(ahora.year, ahora.month - 1, 1)
                fin = datetime(ahora.year, ahora.month, 1) - timedelta(seconds=1)

        # Usar agregación en base de datos para eficiencia
        detalle = await self.repository.get_oportunidad_detalle_por_mes_agregado(inicio, fin)
        return {
            "pruebas": detalle.get("pruebas", []),
            "patologos": detalle.get("patologos", []),
            "resumen": detalle.get("resumen", {"total": 0, "dentro": 0, "fuera": 0}),
            "periodo": {"inicio": inicio.isoformat(), "fin": fin.isoformat()}
        }
    
    def _es_caso_vencido(self, caso) -> bool:
        """Fuera de oportunidad si (fecha_entrega - fecha_creacion) > 6 días.
        Si no hay fecha_entrega y han pasado > 6 días desde creación (y no está completado), también se considera fuera.
        """
        fecha_creacion = getattr(caso, 'fecha_creacion', None)
        if not fecha_creacion:
            return False
        # Si tiene entrega, usamos esa diferencia estrictamente
        fecha_entrega = getattr(caso, 'fecha_entrega', None)
        if fecha_entrega:
            dias = (fecha_entrega - fecha_creacion).days
            return dias > 6
        # Sin entrega aún: considerar fuera si ya excedió 6 días y no completado
        if caso.estado != EstadoCasoEnum.COMPLETADO:
            dias_en_sistema = (datetime.utcnow() - fecha_creacion).days
            return dias_en_sistema > 6
        return False
    
    def _calcular_tiempo_promedio_procesamiento(self, casos) -> float:
        """Calcular el tiempo promedio de procesamiento (fecha_entrega - fecha_creacion) en días."""
        if not casos:
            return 0.0
        
        tiempos_procesamiento = []
        for caso in casos:
            if caso.estado == EstadoCasoEnum.COMPLETADO and hasattr(caso, 'fecha_creacion') and caso.fecha_creacion:
                fecha_completado = None
                # Preferir fecha_entrega cuando exista; si no, usar fecha_firma como respaldo
                if hasattr(caso, 'fecha_entrega') and caso.fecha_entrega:
                    fecha_completado = caso.fecha_entrega
                elif hasattr(caso, 'fecha_firma') and caso.fecha_firma:
                    fecha_completado = caso.fecha_firma
                
                if fecha_completado:
                    tiempo = (fecha_completado - caso.fecha_creacion).days
                    if tiempo >= 0:
                        tiempos_procesamiento.append(tiempo)
        
        if not tiempos_procesamiento:
            return 0.0
        
        return sum(tiempos_procesamiento) / len(tiempos_procesamiento)
    
    def _validar_transicion_estado(self, estado_actual: EstadoCasoEnum, nuevo_estado: EstadoCasoEnum) -> bool:
        """Validar si una transición de estado es válida."""
        transiciones_validas = {
            EstadoCasoEnum.EN_PROCESO: [EstadoCasoEnum.POR_FIRMAR],
            EstadoCasoEnum.POR_FIRMAR: [EstadoCasoEnum.POR_ENTREGAR],
            EstadoCasoEnum.POR_ENTREGAR: [EstadoCasoEnum.COMPLETADO],
            EstadoCasoEnum.COMPLETADO: []
        }
        
        return nuevo_estado in transiciones_validas.get(estado_actual, [])
    
    def _to_response(self, caso: Caso) -> CasoResponse:
        """Convertir modelo de caso a respuesta (sin IO adicional)."""
        caso_dict = caso.model_dump(by_alias=True, mode='json')
        caso_dict["id"] = str(caso.id)
        return CasoResponse(**caso_dict)

    async def obtener_entidades_por_patologo(self, patologo: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtener entidades donde ha trabajado un patólogo específico."""
        from datetime import datetime, timedelta
        
        # Construir filtros de fecha si se proporcionan
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            if month == 12:
                fin = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin = datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        # Obtener entidades desde el repositorio
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
        """Obtener pruebas realizadas por un patólogo específico."""
        from datetime import datetime, timedelta
        
        # Construir filtros de fecha si se proporcionan
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            if month == 12:
                fin = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin = datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        # Obtener pruebas desde el repositorio
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
        """Obtener estadísticas de entidades por mes/año con distribución de ambulatorios y hospitalizados."""
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
        
        # Obtener estadísticas desde el repositorio
        estadisticas = await self.repository.get_estadisticas_entidades_mensual(inicio, fin, entity)
        
        return {
            "entities": estadisticas["entities"],
            "summary": estadisticas["summary"],
            "periodo": {
                "month": month,
                "year": year,
                "entity": entity
            }
        }

    async def obtener_detalle_entidad(self, entidad: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtener detalles completos de una entidad específica."""
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
        
        # Obtener detalles desde el repositorio
        detalles = await self.repository.get_detalle_entidad(entidad, inicio, fin)
        
        return {
            "entidad": entidad,
            "detalles": detalles,
            "periodo": {
                "month": month,
                "year": year
            }
        }

    async def obtener_patologos_por_entidad(self, entidad: str, month: Optional[int] = None, year: Optional[int] = None) -> Dict[str, Any]:
        """Obtener patólogos que han trabajado en una entidad específica."""
        from datetime import datetime, timedelta
        
        # Construir filtros de fecha si se proporcionan
        filtros_fecha = {}
        if month and year:
            inicio = datetime(year, month, 1)
            if month == 12:
                fin = datetime(year + 1, 1, 1) - timedelta(seconds=1)
            else:
                fin = datetime(year, month + 1, 1) - timedelta(seconds=1)
            filtros_fecha = {"fecha_entrega": {"$gte": inicio, "$lte": fin}}
        
        # Obtener patólogos desde el repositorio
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

    # ============================================================================
    # MÉTODOS PARA ESTADÍSTICAS DE PRUEBAS
    # ============================================================================

    async def obtener_estadisticas_pruebas_mensual(self, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        """Obtener estadísticas de pruebas por mes/año y opcionalmente por entidad."""
        # Validar parámetros
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        # Obtener estadísticas desde el repositorio
        pruebas_stats = await self.repository.get_estadisticas_pruebas_mensual(month, year, entity)
        
        # Calcular resumen
        total_solicitadas = sum(p["total_solicitadas"] for p in pruebas_stats)
        total_completadas = sum(p["total_completadas"] for p in pruebas_stats)
        tiempo_promedio = 0.0
        
        if pruebas_stats:
            tiempo_promedio = sum(p["tiempo_promedio"] for p in pruebas_stats) / len(pruebas_stats)
        
        return {
            "pruebas": pruebas_stats,
            "resumen": {
                "totalSolicitadas": total_solicitadas,
                "totalCompletadas": total_completadas,
                "tiempoPromedio": round(tiempo_promedio, 1)
            }
        }

    async def obtener_detalle_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> Dict[str, Any]:
        """Obtener detalles completos de una prueba específica."""
        # Validar parámetros
        if not codigo_prueba:
            raise BadRequestError("El código de prueba es requerido")
        
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        # Obtener detalles desde el repositorio
        detalle = await self.repository.get_detalle_prueba(codigo_prueba, month, year, entity)
        
        return detalle

    async def obtener_patologos_por_prueba(self, codigo_prueba: str, month: int, year: int, entity: str = None) -> List[Dict[str, Any]]:
        """Obtener patólogos que han trabajado en una prueba específica."""
        # Validar parámetros
        if not codigo_prueba:
            raise BadRequestError("El código de prueba es requerido")
        
        if month < 1 or month > 12:
            raise BadRequestError("El mes debe estar entre 1 y 12")
        
        if year < 2020 or year > 2030:
            raise BadRequestError("El año debe estar entre 2020 y 2030")
        
        # Obtener patólogos desde el repositorio
        patologos = await self.repository.get_patologos_por_prueba(codigo_prueba, month, year, entity)
        
        return patologos
    
    async def agregar_nota_adicional(
        self, 
        caso_code: str, 
        nota_data: Dict[str, Any], 
        usuario_id: str
    ) -> CasoResponse:
        """Agregar una nota adicional a un caso completado."""
        # Verificar que el caso existe
        caso_existente = await self.repository.get_by_caso_code(caso_code)
        if not caso_existente:
            raise NotFoundError(f"Caso con código {caso_code} no encontrado")
        
        # Verificar que el caso esté completado
        if caso_existente.estado != EstadoCasoEnum.COMPLETADO:
            raise BadRequestError(f"Solo se pueden agregar notas adicionales a casos completados. Estado actual: {caso_existente.estado}")
        
        # Crear la nueva nota
        nueva_nota = {
            "fecha": datetime.utcnow(),
            "nota": nota_data.get("nota", ""),
            "agregado_por": nota_data.get("agregado_por", usuario_id)
        }
        
        # Agregar la nota al array de notas_adicionales usando $push
        update_data = {
            "$push": {"notas_adicionales": nueva_nota},
            "$set": {
                "fecha_actualizacion": datetime.utcnow(),
                "actualizado_por": usuario_id
            }
        }
        
        # Actualizar el caso
        caso_actualizado = await self.repository.update_by_caso_code(caso_code, update_data)
        if not caso_actualizado:
            raise NotFoundError(f"Error al actualizar el caso {caso_code}")
        
        return self._to_response(caso_actualizado)