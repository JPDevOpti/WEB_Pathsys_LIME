from fastapi import APIRouter


router = APIRouter(prefix="", tags=["casos-consulta"])

# Nota: Router registrado sin endpoints. Se agregarán GET /casos, POST /casos/buscar, etc.


