import logging
import time
from typing import Callable
from fastapi import Request, Response, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware, RequestResponseEndpoint
from app.core.exceptions import PathSysException, InternalServerError

# Configurar logger
logger = logging.getLogger(__name__)

class LoggingMiddleware(BaseHTTPMiddleware):
    """Middleware para logging de requests"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        start_time = time.time()
        
        # No loggear peticiones OPTIONS (CORS preflight)
        if request.method == "OPTIONS":
            return await call_next(request)
        
        # Log del request
        logger.info(
            f"Request: {request.method} {request.url.path} - "
            f"Client: {request.client.host if request.client else 'unknown'}"
        )
        
        try:
            response = await call_next(request)
            
            # Calcular tiempo de procesamiento
            process_time = time.time() - start_time
            
            # Log del response
            logger.info(
                f"Response: {response.status_code} - "
                f"Time: {process_time:.4f}s - "
                f"Path: {request.url.path}"
            )
            
            # Agregar header con tiempo de procesamiento
            response.headers["X-Process-Time"] = str(process_time)
            
            return response
            
        except Exception as e:
            process_time = time.time() - start_time
            logger.error(
                f"Error processing request: {request.method} {request.url.path} - "
                f"Time: {process_time:.4f}s - Error: {str(e)}"
            )
            raise

class ExceptionHandlerMiddleware(BaseHTTPMiddleware):
    """Middleware para manejo de excepciones"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        # No procesar excepciones para peticiones OPTIONS
        if request.method == "OPTIONS":
            return await call_next(request)
            
        try:
            return await call_next(request)
        except PathSysException as e:
            logger.error(f"PathSys Exception: {e.message} - Details: {e.details}")
            raise InternalServerError(detail=e.message)
        except HTTPException:
            # Re-raise HTTPExceptions to let FastAPI handle them
            raise
        except Exception as e:
            import traceback
            logger.error(f"Unhandled exception: {str(e)}")
            logger.error(f"Full traceback: {traceback.format_exc()}")
            raise InternalServerError(detail="Error interno del servidor")

class SecurityHeadersMiddleware(BaseHTTPMiddleware):
    """Middleware para agregar headers de seguridad"""
    
    async def dispatch(
        self, request: Request, call_next: RequestResponseEndpoint
    ) -> Response:
        response = await call_next(request)
        
        # Agregar headers de seguridad
        response.headers["X-Content-Type-Options"] = "nosniff"
        response.headers["X-Frame-Options"] = "DENY"
        response.headers["X-XSS-Protection"] = "1; mode=block"
        response.headers["Referrer-Policy"] = "strict-origin-when-cross-origin"
        
        return response

def setup_middleware(app):
    """Configurar todos los middlewares de la aplicación"""
    from fastapi import FastAPI
    
    # Agregar middlewares en orden de ejecución
    # NOTA: Los middlewares personalizados NO deben interferir con las solicitudes OPTIONS de CORS
    app.add_middleware(SecurityHeadersMiddleware)
    app.add_middleware(ExceptionHandlerMiddleware)
    app.add_middleware(LoggingMiddleware)
    
    logger.info("Middlewares configurados correctamente")