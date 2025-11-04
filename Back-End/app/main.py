from fastapi import FastAPI, Request, APIRouter
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from starlette.exceptions import HTTPException as StarletteHTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.encoders import jsonable_encoder
import os, logging
from app.config.settings import settings
from app.config.database import connect_to_mongo, close_mongo_connection, get_database
from app.modules.cases.repositories.case_repository import CaseRepository
from app.modules.cases.repositories.consecutive_repository import CaseConsecutiveRepository
from app.modules.approvals.repositories.approval_repository import ApprovalRepository
from app.modules.approvals.repositories.consecutive_repository import ApprovalConsecutiveRepository
from app.modules.patients.repositories.patient_repository import PatientRepository
from app.modules.unread_cases.repositories.unread_case_repository import UnreadCaseRepository

app = FastAPI(title="WEB-LIS PathSys - New Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

os.makedirs("uploads/signatures", exist_ok=True)
app.mount("/uploads", StaticFiles(directory="uploads"), name="uploads")

try:
    from .api.v1.router import api_router as api_v1_router  # type: ignore
    app.include_router(api_v1_router, prefix="/api/v1")
except Exception:
    try:
        from app.modules.auth.routes.auth_routes import auth_router  # type: ignore
        r = APIRouter(); r.include_router(auth_router, prefix="/auth"); app.include_router(r, prefix="/api/v1")
    except Exception:
        pass

@app.on_event("startup")
async def on_startup():
    # Conectar a Mongo y preparar índices críticos del módulo de casos
    await connect_to_mongo()
    db = await get_database()
    # Casos
    await CaseRepository(db).ensure_indexes()
    await CaseConsecutiveRepository(db).ensure_indexes()
    # Aprobaciones
    await ApprovalRepository(db).ensure_indexes()
    await ApprovalConsecutiveRepository(db).ensure_indexes()
    # Pacientes
    await PatientRepository(db).ensure_indexes()
    # Casos sin lectura
    await UnreadCaseRepository(db).ensure_indexes()

@app.on_event("shutdown")
async def on_shutdown():
    # Cerrar conexión a Mongo limpiamente
    await close_mongo_connection()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(status_code=422, content={"detail": "Error de validación", "errors": jsonable_encoder(exc.errors())})

@app.exception_handler(StarletteHTTPException)
async def http_exception_handler(request: Request, exc: StarletteHTTPException):
    m = exc.detail if isinstance(exc.detail, str) else "Error HTTP"; return JSONResponse(status_code=exc.status_code, content={"detail": m})

@app.exception_handler(Exception)
async def unhandled_exception_handler(request: Request, exc: Exception):
    logging.getLogger("app.main").exception("[global] Excepción no controlada en %s %s", request.method, request.url.path)
    d = "Error interno del servidor"
    if getattr(settings, "DEBUG", False):
        d = f"Error interno del servidor: {str(exc)}"
    return JSONResponse(status_code=500, content={"detail": d})


