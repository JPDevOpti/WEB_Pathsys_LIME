from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os
import logging
from app.config.settings import settings
from fastapi.encoders import jsonable_encoder

# Crear aplicación FastAPI
app = FastAPI(title="WEB-LIS PathSys - New Backend", version="1.0.0")

# CORS para el frontend local y producción
allowed_origins = [
    "http://localhost:5174", 
    "http://127.0.0.1:5174",
    "http://localhost:5175", 
    "http://127.0.0.1:5175",
    # URLs de producción específicas
    "https://pathsys-frontend.onrender.com",
    "https://web-lis-pathsys-frontend.onrender.com",
    # URL de Vercel (reemplaza con tu URL real)
    "https://tu-proyecto.vercel.app"
]

# Agregar dominios de producción si están configurados
if hasattr(settings, 'FRONTEND_URL') and settings.FRONTEND_URL:
    allowed_origins.append(settings.FRONTEND_URL)

app.add_middleware(
    CORSMiddleware,
    allow_origins=allowed_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Crear directorio de uploads si no existe
os.makedirs("uploads/signatures", exist_ok=True)

# Montar archivos estáticos para servir firmas
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

# Incluir router principal v1 si existe; si falla, montar al menos auth
try:
    from .api.v1.router import api_router as api_v1_router  # type: ignore
    app.include_router(api_v1_router, prefix="/api/v1")
except Exception:
    try:
        from app.modules.auth.routes.auth_routes import auth_router  # type: ignore
        fallback_router = APIRouter()
        fallback_router.include_router(auth_router, prefix="/auth")
        app.include_router(fallback_router, prefix="/api/v1")
    except Exception:
        pass


@app.get("/health")
async def health():
    return {"status": "ok"}

# Global exception handlers with normalized messages
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    # Asegurar que los errores sean JSON-serializables
    errors = jsonable_encoder(exc.errors())
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": errors})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Preserve status_code, unify message format
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(status_code=exc.status_code, content={"detail": message})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logger = logging.getLogger("app.main")
    logger.exception("[global] Unhandled exception en %s %s", request.method, request.url.path)
    detail = "Internal server error"
    if getattr(settings, "DEBUG", False):
        # En modo desarrollo, exponer el mensaje para facilitar el diagnóstico
        detail = f"Internal server error: {str(exc)}"
    return JSONResponse(status_code=500, content={"detail": detail})


