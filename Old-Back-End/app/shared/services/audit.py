import logging
from datetime import datetime
from typing import Optional, Dict, Any, List
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.shared.schemas.common import AuditInfo
from enum import Enum

logger = logging.getLogger(__name__)

class AuditAction(str, Enum):
    """Acciones de auditoría"""
    CREATE = "create"
    READ = "read"
    UPDATE = "update"
    DELETE = "delete"
    LOGIN = "login"
    LOGOUT = "logout"
    EXPORT = "export"
    IMPORT = "import"
    APPROVE = "approve"
    REJECT = "reject"
    SIGN = "sign"
    SEND = "send"
    RECEIVE = "receive"
    CANCEL = "cancel"
    RESTORE = "restore"

class AuditLevel(str, Enum):
    """Niveles de auditoría"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    CRITICAL = "critical"

class AuditService:
    """Servicio de auditoría para registrar acciones del sistema"""
    
    def __init__(self):
        self.collection_name = "audit_logs"
    
    async def _get_collection(self):
        """Obtener colección de auditoría"""
        db = await get_database()
        return db[self.collection_name]
    
    async def log_action(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        user_email: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None,
        user_agent: Optional[str] = None,
        level: AuditLevel = AuditLevel.INFO,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Registrar una acción de auditoría"""
        try:
            collection = await self._get_collection()
            
            audit_record = {
                "timestamp": datetime.utcnow(),
                "action": action.value,
                "resource_type": resource_type,
                "resource_id": resource_id,
                "user_id": user_id,
                "user_email": user_email,
                "level": level.value,
                "ip_address": ip_address,
                "user_agent": user_agent,
                "details": details or {},
                "old_values": old_values,
                "new_values": new_values,
                "session_id": None  # Se puede agregar si se implementa manejo de sesiones
            }
            
            await collection.insert_one(audit_record)
            
            # Log también en el sistema de logging
            log_message = f"Audit: {action.value} on {resource_type}"
            if resource_id:
                log_message += f" (ID: {resource_id})"
            if user_email:
                log_message += f" by {user_email}"
            
            if level == AuditLevel.ERROR:
                logger.error(log_message)
            elif level == AuditLevel.WARNING:
                logger.warning(log_message)
            elif level == AuditLevel.CRITICAL:
                logger.critical(log_message)
            else:
                logger.info(log_message)
            
            return True
            
        except Exception as e:
            logger.error(f"Error al registrar auditoría: {str(e)}")
            return False
    
    async def log_user_action(
        self,
        action: AuditAction,
        user_id: str,
        user_email: str,
        resource_type: str,
        resource_id: Optional[str] = None,
        details: Optional[Dict[str, Any]] = None,
        ip_address: Optional[str] = None
    ) -> bool:
        """Registrar acción de usuario"""
        return await self.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            details=details,
            ip_address=ip_address
        )
    
    async def log_system_action(
        self,
        action: AuditAction,
        resource_type: str,
        details: Optional[Dict[str, Any]] = None,
        level: AuditLevel = AuditLevel.INFO
    ) -> bool:
        """Registrar acción del sistema"""
        return await self.log_action(
            action=action,
            resource_type=resource_type,
            user_email="system",
            details=details,
            level=level
        )
    
    async def log_data_change(
        self,
        action: AuditAction,
        resource_type: str,
        resource_id: str,
        user_id: str,
        user_email: str,
        old_values: Dict[str, Any],
        new_values: Dict[str, Any],
        ip_address: Optional[str] = None
    ) -> bool:
        """Registrar cambio de datos con valores anteriores y nuevos"""
        return await self.log_action(
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            user_id=user_id,
            user_email=user_email,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address
        )
    
    async def get_audit_logs(
        self,
        resource_type: Optional[str] = None,
        resource_id: Optional[str] = None,
        user_id: Optional[str] = None,
        action: Optional[AuditAction] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        level: Optional[AuditLevel] = None,
        skip: int = 0,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Obtener logs de auditoría con filtros"""
        try:
            collection = await self._get_collection()
            
            # Construir filtros
            filters = {}
            
            if resource_type:
                filters["resource_type"] = resource_type
            
            if resource_id:
                filters["resource_id"] = resource_id
            
            if user_id:
                filters["user_id"] = user_id
            
            if action:
                filters["action"] = action.value
            
            if level:
                filters["level"] = level.value
            
            if start_date or end_date:
                date_filter = {}
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
                filters["timestamp"] = date_filter
            
            # Ejecutar consulta
            cursor = collection.find(filters).sort("timestamp", -1).skip(skip).limit(limit)
            logs = await cursor.to_list(length=limit)
            
            # Convertir ObjectId a string
            for log in logs:
                if "_id" in log:
                    log["_id"] = str(log["_id"])
            
            return logs
            
        except Exception as e:
            logger.error(f"Error al obtener logs de auditoría: {str(e)}")
            return []
    
    async def get_user_activity(
        self,
        user_id: str,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtener actividad de un usuario específico"""
        return await self.get_audit_logs(
            user_id=user_id,
            start_date=start_date,
            end_date=end_date,
            limit=limit
        )
    
    async def get_resource_history(
        self,
        resource_type: str,
        resource_id: str,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtener historial de un recurso específico"""
        return await self.get_audit_logs(
            resource_type=resource_type,
            resource_id=resource_id,
            limit=limit
        )
    
    async def get_audit_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtener estadísticas de auditoría"""
        try:
            collection = await self._get_collection()
            
            # Filtro de fechas
            date_filter = {}
            if start_date or end_date:
                if start_date:
                    date_filter["$gte"] = start_date
                if end_date:
                    date_filter["$lte"] = end_date
            
            match_stage = {"timestamp": date_filter} if date_filter else {}
            
            # Pipeline de agregación
            pipeline = [
                {"$match": match_stage},
                {
                    "$group": {
                        "_id": {
                            "action": "$action",
                            "resource_type": "$resource_type",
                            "level": "$level"
                        },
                        "count": {"$sum": 1}
                    }
                }
            ]
            
            results = await collection.aggregate(pipeline).to_list(length=None)
            
            # Procesar resultados
            stats = {
                "total_actions": 0,
                "by_action": {},
                "by_resource_type": {},
                "by_level": {}
            }
            
            for result in results:
                count = result["count"]
                action = result["_id"]["action"]
                resource_type = result["_id"]["resource_type"]
                level = result["_id"]["level"]
                
                stats["total_actions"] += count
                
                if action not in stats["by_action"]:
                    stats["by_action"][action] = 0
                stats["by_action"][action] += count
                
                if resource_type not in stats["by_resource_type"]:
                    stats["by_resource_type"][resource_type] = 0
                stats["by_resource_type"][resource_type] += count
                
                if level not in stats["by_level"]:
                    stats["by_level"][level] = 0
                stats["by_level"][level] += count
            
            return stats
            
        except Exception as e:
            logger.error(f"Error al obtener estadísticas de auditoría: {str(e)}")
            return {}
    
    async def cleanup_old_logs(self, days: int = 90) -> int:
        """Limpiar logs antiguos (para mantenimiento)"""
        try:
            collection = await self._get_collection()
            
            cutoff_date = datetime.utcnow().replace(
                hour=0, minute=0, second=0, microsecond=0
            )
            cutoff_date = cutoff_date.replace(day=cutoff_date.day - days)
            
            result = await collection.delete_many({
                "timestamp": {"$lt": cutoff_date}
            })
            
            deleted_count = result.deleted_count
            logger.info(f"Limpieza de auditoría completada: {deleted_count} registros eliminados")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error en limpieza de logs de auditoría: {str(e)}")
            return 0

# Instancia global del servicio
audit_service = AuditService()