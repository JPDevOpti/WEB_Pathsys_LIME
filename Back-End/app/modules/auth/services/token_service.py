"""Servicio de tokens"""

from typing import Optional, List, Dict, Any
from datetime import datetime, timedelta, timezone
from jose import JWTError, jwt
from app.modules.auth.schemas.token import TokenPayload
from app.config.settings import settings
from app.core.exceptions import UnauthorizedError


class TokenService:
    """Servicio para manejo de tokens JWT"""
    
    def __init__(self):
        self.secret_key = settings.SECRET_KEY
        self.algorithm = "HS256"
        # Extender la duración del token de acceso a 24 horas para evitar expiraciones frecuentes
        self.access_token_expire_minutes = 24 * 60  # 24 horas
        # Mantener/ajustar refresh token (opcional: ampliar si se requiere persistencia más larga)
        self.refresh_token_expire_days = 7  # 7 días
    
    async def create_access_token(
        self, 
        user_id: str, 
        email: str, 
        username: str, 
        roles: List[str]
    ) -> Dict[str, Any]:
        """Crear token de acceso"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(minutes=self.access_token_expire_minutes)
        
        payload = {
            "sub": user_id,
            "email": email,
            "username": username,
            "roles": roles,
            "exp": expire,
            "iat": now,
            "type": "access"
        }
        
        token = jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
        
        return {
            "access_token": token,
            "expires_in": self.access_token_expire_minutes * 60,
            "token_type": "bearer"
        }
    
    async def create_refresh_token(
        self, 
        user_id: str, 
        email: str, 
        username: str, 
        roles: List[str]
    ) -> str:
        """Crear token de actualización"""
        now = datetime.now(timezone.utc)
        expire = now + timedelta(days=self.refresh_token_expire_days)
        
        payload = {
            "sub": user_id,
            "email": email,
            "username": username,
            "roles": roles,
            "exp": expire,
            "iat": now,
            "type": "refresh"
        }
        
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    async def verify_token(self, token: str, expected_type: Optional[str] = None) -> Optional[TokenPayload]:
        """Verificar y decodificar token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            
            # Verificar expiración
            exp = payload.get("exp")
            if exp and datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc):
                return None
            
            # Validar campos requeridos
            sub = payload.get("sub")
            email = payload.get("email")
            username = payload.get("username")
            exp_timestamp = payload.get("exp")
            iat_timestamp = payload.get("iat")
            token_type = payload.get("type")
            
            if not all([sub, email, username, exp_timestamp, iat_timestamp, token_type]):
                return None
            
            # Validar tipo de token si se especifica
            if expected_type and token_type != expected_type:
                return None
            
            return TokenPayload(
                sub=str(sub),
                email=str(email),
                username=str(username),
                roles=payload.get("roles", []),
                exp=datetime.fromtimestamp(float(exp_timestamp), tz=timezone.utc),
                iat=datetime.fromtimestamp(float(iat_timestamp), tz=timezone.utc),
                type=token_type
            )
        except JWTError:
            return None
    
    async def decode_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Decodificar token sin verificar"""
        try:
            return jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
        except JWTError:
            return None
    
    async def is_token_expired(self, token: str) -> bool:
        """Verificar si el token está expirado"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if exp:
                return datetime.fromtimestamp(exp, tz=timezone.utc) < datetime.now(timezone.utc)
            return True
        except JWTError:
            return True
    
    async def get_token_remaining_time(self, token: str) -> Optional[int]:
        """Obtener tiempo restante del token en segundos"""
        try:
            payload = jwt.decode(
                token, 
                self.secret_key, 
                algorithms=[self.algorithm],
                options={"verify_exp": False}
            )
            exp = payload.get("exp")
            if exp:
                remaining = datetime.fromtimestamp(exp, tz=timezone.utc) - datetime.now(timezone.utc)
                return max(0, int(remaining.total_seconds()))
            return 0
        except JWTError:
            return None