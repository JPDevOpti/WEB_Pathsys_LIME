from datetime import datetime, timedelta, timezone
from typing import Any, Union, Optional
from jose import jwt, JWTError
from passlib.context import CryptContext
from app.config.settings import settings

# Configuración de encriptación de contraseñas
pwd_context = CryptContext(schemes=["argon2", "bcrypt"], deprecated="auto")

def create_access_token(
    subject: Union[str, Any], expires_delta: Optional[timedelta] = None
) -> str:
    """Crear token de acceso JWT"""
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(
            minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES
        )
    
    to_encode = {"exp": expire, "sub": str(subject)}
    encoded_jwt = jwt.encode(
        to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM
    )
    return encoded_jwt

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verificar contraseña"""
    try:
        scheme = pwd_context.identify(hashed_password) or ""
    except Exception:
        scheme = ""
    if (scheme.startswith('bcrypt') or hashed_password.startswith('$2')) and len(plain_password.encode('utf-8')) > 72:
        plain_password = plain_password.encode('utf-8')[:72].decode('utf-8', errors='ignore')
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    """Obtener hash de contraseña"""
    # Usar argon2 por defecto (sin límite de longitud)
    return pwd_context.hash(password)

def decode_token(token: str) -> Optional[dict]:
    """Decodificar token JWT"""
    try:
        payload = jwt.decode(
            token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM]
        )
        return payload
    except JWTError:
        return None

def verify_token(token: str) -> Optional[str]:
    """Verificar token y obtener subject"""
    payload = decode_token(token)
    if payload is None:
        return None
    
    # Verificar expiración
    exp = payload.get("exp")
    if exp is None:
        return None
    
    # Convertir timestamp a datetime para comparación
    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
    if datetime.now(timezone.utc) > exp_datetime:
        return None
    
    return payload.get("sub")

def is_token_expired(token: str) -> bool:
    """Verificar si un token ha expirado"""
    payload = decode_token(token)
    if payload is None:
        return True
    
    exp = payload.get("exp")
    if exp is None:
        return True
    
    exp_datetime = datetime.fromtimestamp(exp, tz=timezone.utc)
    return datetime.now(timezone.utc) > exp_datetime