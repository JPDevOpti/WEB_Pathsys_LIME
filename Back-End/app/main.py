from fastapi import FastAPI, Request
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import os

# Crear aplicación FastAPI
app = FastAPI(title="WEB-LIS PathSys - New Backend", version="1.0.0")

# CORS para el frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5174", "http://127.0.0.1:5174"],
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
    return JSONResponse(status_code=422, content={"detail": "Validation error", "errors": exc.errors()})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    # Preserve status_code, unify message format
    message = exc.detail if isinstance(exc.detail, str) else "HTTP error"
    return JSONResponse(status_code=exc.status_code, content={"detail": message})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    return JSONResponse(status_code=500, content={"detail": "Internal server error"})


