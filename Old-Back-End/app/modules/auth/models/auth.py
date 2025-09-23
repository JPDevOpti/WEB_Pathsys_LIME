"""Modelos de autenticación"""

from typing import Optional, List, Union
from pydantic import BaseModel, Field, EmailStr
from datetime import datetime
from app.shared.schemas.common import RolEnum
class AuthUser(BaseModel):
    """Modelo de usuario para autenticación - Coincide con la estructura de la BD"""
    id: str = Field(..., description="ID del usuario")
    email: EmailStr = Field(..., description="Email del usuario")
    nombre: Optional[str] = Field(None, description="Nombre completo del usuario")
    rol: Optional[Union[RolEnum, str]] = Field(None, description="Rol del usuario")
    patologo_code: Optional[str] = Field(None, description="Código del patólogo si aplica")
    auxiliar_code: Optional[str] = Field(None, description="Código del auxiliar si aplica")
    residente_code: Optional[str] = Field(None, description="Código del residente si aplica")
    administrador_code: Optional[str] = Field(None, description="Código del administrador si aplica")
    facturacion_code: Optional[str] = Field(None, description="Código de facturación si aplica")
    is_active: Optional[bool] = Field(None, description="Estado activo del usuario")
    fecha_creacion: Optional[datetime] = Field(None, description="Fecha de creación")
    fecha_actualizacion: Optional[datetime] = Field(None, description="Fecha de actualización")
    ultimo_acceso: Optional[datetime] = Field(None, description="Último acceso")
    class Config:
        from_attributes = True
    
    def get_primary_role(self) -> str:
        """Obtener el rol principal del usuario"""
        if self.rol:
            return self.rol.value if hasattr(self.rol, 'value') else str(self.rol)
        return "user"
    
    def get_all_roles(self) -> List[str]:
        """Obtener todos los roles como strings (compatibilidad con sistema de múltiples roles)"""
        if self.rol:
            role_str = self.rol.value if hasattr(self.rol, 'value') else str(self.rol)
            return [role_str]
        return ["user"]
    
    def is_user_active(self) -> bool:
        """Verificar si el usuario está activo"""
        return self.is_active if self.is_active is not None else True
    
    def get_display_name(self) -> str:
        """Obtener nombre para mostrar (nombre completo o email)"""
        return self.nombre or self.email