from typing import Any, Dict, Optional
from fastapi import HTTPException, status

class PathSysException(Exception):
    """Excepción base para el sistema PathSys"""
    def __init__(self, message: str, details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.details = details or {}
        super().__init__(self.message)

class DatabaseException(PathSysException):
    """Excepción para errores de base de datos"""
    pass

class ValidationException(PathSysException):
    """Excepción para errores de validación"""
    pass

class AuthenticationException(PathSysException):
    """Excepción para errores de autenticación"""
    pass

class AuthorizationException(PathSysException):
    """Excepción para errores de autorización"""
    pass

class NotFoundError(HTTPException):
    """Error 404 - Recurso no encontrado"""
    def __init__(self, detail: str = "Recurso no encontrado"):
        super().__init__(status_code=status.HTTP_404_NOT_FOUND, detail=detail)

class ConflictError(HTTPException):
    """Error 409 - Conflicto"""
    def __init__(self, detail: str = "Conflicto en la operación"):
        super().__init__(status_code=status.HTTP_409_CONFLICT, detail=detail)

class BadRequestError(HTTPException):
    """Error 400 - Solicitud incorrecta"""
    def __init__(self, detail: str = "Solicitud incorrecta"):
        super().__init__(status_code=status.HTTP_400_BAD_REQUEST, detail=detail)

class UnauthorizedError(HTTPException):
    """Error 401 - No autorizado"""
    def __init__(self, detail: str = "No autorizado"):
        super().__init__(status_code=status.HTTP_401_UNAUTHORIZED, detail=detail)

class ForbiddenError(HTTPException):
    """Error 403 - Prohibido"""
    def __init__(self, detail: str = "Acceso prohibido"):
        super().__init__(status_code=status.HTTP_403_FORBIDDEN, detail=detail)

class InternalServerError(HTTPException):
    """Error 500 - Error interno del servidor"""
    def __init__(self, detail: str = "Error interno del servidor"):
        super().__init__(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=detail)