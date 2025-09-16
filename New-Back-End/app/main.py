from fastapi import FastAPI
from fastapi import APIRouter
from fastapi.middleware.cors import CORSMiddleware

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

# Incluir router principal v1 si existe; si falla, montar al menos auth
try:
    from app.api.v1.router import api_router as api_v1_router  # type: ignore
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


