import logging
from datetime import datetime, timedelta
from typing import Optional, Dict, Any, List
from enum import Enum
from motor.motor_asyncio import AsyncIOMotorDatabase
from app.config.database import get_database
from app.shared.services.email import EmailService
from app.shared.schemas.common import NotificationSettings

logger = logging.getLogger(__name__)

class NotificationType(str, Enum):
    """Tipos de notificación"""
    INFO = "info"
    WARNING = "warning"
    ERROR = "error"
    SUCCESS = "success"
    REMINDER = "reminder"
    ALERT = "alert"
    SYSTEM = "system"

class NotificationChannel(str, Enum):
    """Canales de notificación"""
    EMAIL = "email"
    IN_APP = "in_app"
    SMS = "sms"  # Para futuro
    PUSH = "push"  # Para futuro

class NotificationPriority(str, Enum):
    """Prioridad de notificación"""
    LOW = "low"
    NORMAL = "normal"
    HIGH = "high"
    URGENT = "urgent"

class NotificationService:
    """Servicio de notificaciones"""
    
    def __init__(self):
        self.collection_name = "notifications"
        self.email_service = EmailService()
    
    async def _get_collection(self):
        """Obtener colección de notificaciones"""
        db = await get_database()
        return db[self.collection_name]
    
    async def create_notification(
        self,
        user_id: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        priority: NotificationPriority = NotificationPriority.NORMAL,
        channels: Optional[List[NotificationChannel]] = None,
        data: Optional[Dict[str, Any]] = None,
        expires_at: Optional[datetime] = None,
        action_url: Optional[str] = None,
        send_immediately: bool = True
    ) -> str:
        """Crear una nueva notificación"""
        try:
            collection = await self._get_collection()
            
            if channels is None:
                channels = [NotificationChannel.IN_APP]
            
            notification = {
                "user_id": user_id,
                "title": title,
                "message": message,
                "type": notification_type.value,
                "priority": priority.value,
                "channels": [channel.value for channel in channels],
                "data": data or {},
                "action_url": action_url,
                "created_at": datetime.utcnow(),
                "expires_at": expires_at,
                "read": False,
                "sent_channels": [],
                "failed_channels": [],
                "retry_count": 0,
                "last_retry": None
            }
            
            result = await collection.insert_one(notification)
            notification_id = str(result.inserted_id)
            
            if send_immediately:
                await self._send_notification(notification_id, notification)
            
            return notification_id
            
        except Exception as e:
            logger.error(f"Error al crear notificación: {str(e)}")
            raise
    
    async def _send_notification(self, notification_id: str, notification: Dict[str, Any]):
        """Enviar notificación por los canales especificados"""
        collection = await self._get_collection()
        
        for channel in notification["channels"]:
            try:
                if channel == NotificationChannel.EMAIL.value:
                    await self._send_email_notification(notification)
                    notification["sent_channels"].append(channel)
                elif channel == NotificationChannel.IN_APP.value:
                    # Las notificaciones in-app se marcan como enviadas automáticamente
                    notification["sent_channels"].append(channel)
                # Agregar más canales aquí en el futuro
                
            except Exception as e:
                logger.error(f"Error enviando notificación por {channel}: {str(e)}")
                notification["failed_channels"].append(channel)
        
        # Actualizar estado en la base de datos
        await collection.update_one(
            {"_id": notification_id},
            {
                "$set": {
                    "sent_channels": notification["sent_channels"],
                    "failed_channels": notification["failed_channels"]
                }
            }
        )
    
    async def _send_email_notification(self, notification: Dict[str, Any]):
        """Enviar notificación por email"""
        # Obtener información del usuario
        db = await get_database()
        user = await db.usuarios.find_one({"_id": notification["user_id"]})
        
        if not user or not user.get("email"):
            raise Exception("Usuario no encontrado o sin email")
        
        # Preparar contenido del email
        subject = f"[PathSys] {notification['title']}"
        
        html_content = f"""
        <html>
        <body>
            <h2>{notification['title']}</h2>
            <p>{notification['message']}</p>
            
            {f'<p><a href="{notification["action_url"]}">Ver más</a></p>' if notification.get('action_url') else ''}
            
            <hr>
            <p><small>Este es un mensaje automático del sistema PathSys.</small></p>
        </body>
        </html>
        """
        
        await self.email_service.send_email(
            to_emails=[user["email"]],
            subject=subject,
            body=html_content
        )
    
    async def get_user_notifications(
        self,
        user_id: str,
        unread_only: bool = False,
        notification_type: Optional[NotificationType] = None,
        skip: int = 0,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Obtener notificaciones de un usuario"""
        try:
            collection = await self._get_collection()
            
            # Construir filtros
            filters: Dict[str, Any] = {"user_id": user_id}
            
            if unread_only:
                filters["read"] = False
            
            if notification_type:
                filters["type"] = notification_type.value
            
            # Filtrar notificaciones no expiradas
            filters["$or"] = [
                {"expires_at": None},
                {"expires_at": {"$gt": datetime.utcnow()}}
            ]
            
            cursor = collection.find(filters).sort("created_at", -1).skip(skip).limit(limit)
            notifications = await cursor.to_list(length=limit)
            
            # Convertir ObjectId a string
            for notification in notifications:
                if "_id" in notification:
                    notification["id"] = str(notification["_id"])
                    del notification["_id"]
            
            return notifications
            
        except Exception as e:
            logger.error(f"Error al obtener notificaciones: {str(e)}")
            return []
    
    async def mark_as_read(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Marcar notificación como leída"""
        try:
            collection = await self._get_collection()
            
            result = await collection.update_one(
                {"_id": notification_id, "user_id": user_id},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            
            return result.modified_count > 0
            
        except Exception as e:
            logger.error(f"Error al marcar notificación como leída: {str(e)}")
            return False
    
    async def mark_all_as_read(self, user_id: str) -> int:
        """Marcar todas las notificaciones como leídas"""
        try:
            collection = await self._get_collection()
            
            result = await collection.update_many(
                {"user_id": user_id, "read": False},
                {"$set": {"read": True, "read_at": datetime.utcnow()}}
            )
            
            return result.modified_count
            
        except Exception as e:
            logger.error(f"Error al marcar todas las notificaciones como leídas: {str(e)}")
            return 0
    
    async def delete_notification(
        self,
        notification_id: str,
        user_id: str
    ) -> bool:
        """Eliminar notificación"""
        try:
            collection = await self._get_collection()
            
            result = await collection.delete_one({
                "_id": notification_id,
                "user_id": user_id
            })
            
            return result.deleted_count > 0
            
        except Exception as e:
            logger.error(f"Error al eliminar notificación: {str(e)}")
            return False
    
    async def get_unread_count(self, user_id: str) -> int:
        """Obtener cantidad de notificaciones no leídas"""
        try:
            collection = await self._get_collection()
            
            count = await collection.count_documents({
                "user_id": user_id,
                "read": False,
                "$or": [
                    {"expires_at": None},
                    {"expires_at": {"$gt": datetime.utcnow()}}
                ]
            })
            
            return count
            
        except Exception as e:
            logger.error(f"Error al obtener conteo de notificaciones: {str(e)}")
            return 0
    
    async def send_bulk_notification(
        self,
        user_ids: List[str],
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """Enviar notificación a múltiples usuarios"""
        notification_ids = []
        
        for user_id in user_ids:
            try:
                notification_id = await self.create_notification(
                    user_id=user_id,
                    title=title,
                    message=message,
                    notification_type=notification_type,
                    channels=channels
                )
                notification_ids.append(notification_id)
            except Exception as e:
                logger.error(f"Error enviando notificación a usuario {user_id}: {str(e)}")
        
        return notification_ids
    
    async def send_role_notification(
        self,
        role: str,
        title: str,
        message: str,
        notification_type: NotificationType = NotificationType.INFO,
        channels: Optional[List[NotificationChannel]] = None
    ) -> List[str]:
        """Enviar notificación a todos los usuarios de un rol"""
        try:
            # Obtener usuarios del rol
            db = await get_database()
            users = await db.usuarios.find(
                {"rol": role, "is_active": True},
                {"_id": 1}
            ).to_list(length=None)
            
            user_ids = [str(user["_id"]) for user in users]
            
            return await self.send_bulk_notification(
                user_ids=user_ids,
                title=title,
                message=message,
                notification_type=notification_type,
                channels=channels
            )
            
        except Exception as e:
            logger.error(f"Error enviando notificación a rol {role}: {str(e)}")
            return []
    
    async def cleanup_expired_notifications(self) -> int:
        """Limpiar notificaciones expiradas"""
        try:
            collection = await self._get_collection()
            
            result = await collection.delete_many({
                "expires_at": {"$lt": datetime.utcnow()}
            })
            
            deleted_count = result.deleted_count
            if deleted_count > 0:
                logger.info(f"Limpieza de notificaciones: {deleted_count} notificaciones expiradas eliminadas")
            
            return deleted_count
            
        except Exception as e:
            logger.error(f"Error en limpieza de notificaciones: {str(e)}")
            return 0
    
    async def retry_failed_notifications(self, max_retries: int = 3) -> int:
        """Reintentar notificaciones fallidas"""
        try:
            collection = await self._get_collection()
            
            # Buscar notificaciones con canales fallidos y pocos reintentos
            failed_notifications = await collection.find({
                "failed_channels": {"$ne": []},
                "retry_count": {"$lt": max_retries},
                "$or": [
                    {"last_retry": None},
                    {"last_retry": {"$lt": datetime.utcnow() - timedelta(minutes=30)}}
                ]
            }).to_list(length=100)
            
            retry_count = 0
            
            for notification in failed_notifications:
                try:
                    # Reintentar solo los canales fallidos
                    notification["channels"] = notification["failed_channels"]
                    notification["failed_channels"] = []
                    
                    await self._send_notification(
                        str(notification["_id"]),
                        notification
                    )
                    
                    # Actualizar contadores
                    await collection.update_one(
                        {"_id": notification["_id"]},
                        {
                            "$inc": {"retry_count": 1},
                            "$set": {"last_retry": datetime.utcnow()}
                        }
                    )
                    
                    retry_count += 1
                    
                except Exception as e:
                    logger.error(f"Error reintentando notificación {notification['_id']}: {str(e)}")
            
            if retry_count > 0:
                logger.info(f"Reintento de notificaciones: {retry_count} notificaciones procesadas")
            
            return retry_count
            
        except Exception as e:
            logger.error(f"Error en reintento de notificaciones: {str(e)}")
            return 0

# Instancia global del servicio
notification_service = NotificationService()