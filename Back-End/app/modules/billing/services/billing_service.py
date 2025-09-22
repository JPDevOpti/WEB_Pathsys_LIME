"""Servicio para la lógica de negocio de Billing"""

from typing import List, Optional, Dict, Any
from motor.motor_asyncio import AsyncIOMotorDatabase

from app.core.exceptions import NotFoundError, ConflictError, BadRequestError
from app.modules.billing.schemas.billing import BillingCreate, BillingUpdate, BillingResponse, BillingSearch
from app.modules.billing.repositories.billing_repository import BillingRepository
from app.shared.services.user_management import UserManagementService

class BillingService:
    """Servicio para la lógica de negocio de Billing"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.repo = BillingRepository(db)
        self.user_service = UserManagementService(db)
    
    async def create_billing(self, payload: BillingCreate) -> BillingResponse:
        """Crear un nuevo usuario de facturación"""
        # Verificar que el código no esté en uso
        existing_code = await self.repo.get_by_billing_code(payload.billing_code)
        if existing_code:
            raise ConflictError("Billing code already exists")
        
        # Verificar que el email no esté en uso
        existing_email = await self.repo.get_by_email(payload.billing_email)
        if existing_email:
            raise ConflictError("Email already exists")
        
        # Crear el usuario de facturación en la colección billing
        doc = await self.repo.create(payload)
        
        # Crear el usuario en la colección users
        user_data = await self.user_service.create_user_for_billing(
            name=payload.billing_name,
            email=payload.billing_email,
            password=payload.password,
            billing_code=payload.billing_code,
            is_active=payload.is_active
        )
        
        if not user_data:
            # Si falla la creación del usuario, eliminar el billing creado
            await self.repo.delete_by_billing_code(payload.billing_code)
            raise ConflictError("Failed to create user account")
        
        return self._to_response(doc)
    
    async def get_billing(self, billing_code: str) -> BillingResponse:
        """Obtener usuario de facturación por código"""
        doc = await self.repo.get_by_billing_code(billing_code)
        if not doc:
            raise NotFoundError(f"Billing user with code {billing_code} not found")
        return self._to_response(doc)
    
    async def list_billing(self, skip: int = 0, limit: int = 100) -> List[BillingResponse]:
        """Listar usuarios de facturación activos"""
        billing_users = await self.repo.list_active(skip=skip, limit=limit)
        return [self._to_response(billing) for billing in billing_users]
    
    async def search_billing(self, search_params: BillingSearch, skip: int = 0, limit: int = 100) -> List[BillingResponse]:
        """Buscar usuarios de facturación"""
        billing_users = await self.repo.search(search_params, skip=skip, limit=limit)
        return [self._to_response(billing) for billing in billing_users]
    
    async def update_billing(self, billing_code: str, payload: BillingUpdate) -> BillingResponse:
        """Actualizar usuario de facturación por código"""
        # Verificar que el usuario de facturación existe
        existing = await self.repo.get_by_billing_code(billing_code)
        if not existing:
            raise NotFoundError(f"Billing user with code {billing_code} not found")
        
        # Verificar unicidad de email si se está actualizando
        if payload.billing_email and payload.billing_email != existing["billing_email"]:
            existing_email = await self.repo.get_by_email(payload.billing_email)
            if existing_email:
                raise ConflictError("Email already exists")
        
        # Actualizar el usuario de facturación
        update_data = payload.dict(exclude_unset=True)
        updated = await self.repo.update_by_billing_code(billing_code, update_data)
        if not updated:
            raise BadRequestError("Failed to update billing user")
        
        # Actualizar el usuario correspondiente en la colección users
        if payload.billing_name or payload.billing_email or payload.is_active is not None or payload.password:
            user_data = await self.user_service.update_user_for_billing(
                billing_code=billing_code,
                name=payload.billing_name,
                email=payload.billing_email,
                password=payload.password,
                is_active=payload.is_active
            )
            if not user_data:
                # Si falla la actualización del usuario, revertir cambios en billing
                # (opcional: implementar rollback si es crítico)
                pass
        
        return self._to_response(updated)
    
    async def delete_billing(self, billing_code: str) -> Dict[str, Any]:
        """Eliminar usuario de facturación por código"""
        doc = await self.repo.get_by_billing_code(billing_code)
        if not doc:
            raise NotFoundError(f"Billing user with code {billing_code} not found")
        
        ok = await self.repo.delete_by_billing_code(billing_code)
        return {"deleted": ok, "billing_code": billing_code}
    
    def _to_response(self, doc: dict) -> BillingResponse:
        """Convertir documento a respuesta"""
        return BillingResponse(
            id=doc["id"],
            billing_code=doc["billing_code"],
            billing_name=doc["billing_name"],
            billing_email=doc["billing_email"],
            is_active=doc["is_active"],
            observations=doc.get("observations"),
            created_at=doc["created_at"],
            updated_at=doc["updated_at"]
        )
