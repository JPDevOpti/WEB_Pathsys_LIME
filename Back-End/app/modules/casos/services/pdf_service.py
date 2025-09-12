from __future__ import annotations

from typing import Any
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


class CasePdfService:
    def __init__(self, database: Any):
        from app.modules.casos.services.caso_service import CasoService
        from app.modules.patologos.repositories.patologo_repository import PatologoRepository
        self.caso_service = CasoService(database)
        self.patologo_repository = PatologoRepository(database)
        templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_path = templates_dir.resolve()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )

    async def generate_case_pdf(self, caso_code: str) -> bytes:
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception as e:  # ImportError or runtime errors
            raise RuntimeError(
                "Playwright no está instalado o no se han instalado los navegadores. "
                "Ejecuta: pip install playwright && playwright install chromium"
            ) from e

        case = await self.caso_service.obtener_caso_por_caso_code(caso_code)
        
        # Obtener pruebas complementarias pendientes de aprobación
        pruebas_complementarias = None
        try:
            from app.modules.aprobacion.repositories.caso_aprobacion_repository import CasoAprobacionRepository
            from app.modules.aprobacion.models.caso_aprobacion import EstadoAprobacionEnum
            
            aprobacion_repo = CasoAprobacionRepository(self.database)
            caso_aprobacion = await aprobacion_repo.find_by_caso_original(caso_code)
            
            # Solo mostrar si el caso tiene pruebas pendientes de aprobación
            if (caso_aprobacion and 
                caso_aprobacion.estado_aprobacion in [EstadoAprobacionEnum.SOLICITUD_HECHA, EstadoAprobacionEnum.PENDIENTE_APROBACION]):
                pruebas_complementarias = {
                    'pruebas': caso_aprobacion.pruebas_complementarias,
                    'motivo': caso_aprobacion.aprobacion_info.motivo if caso_aprobacion.aprobacion_info else '',
                    'fecha_solicitud': caso_aprobacion.fecha_creacion,
                    'estado': caso_aprobacion.estado_aprobacion.value
                }
        except Exception as e:
            print(f"Error obteniendo pruebas complementarias: {e}")
            pruebas_complementarias = None

        # Obtener firma del patólogo desde la colección de patólogos
        pathologist_signature = None
        try:
            asignado = getattr(case, 'patologo_asignado', None) or case.get('patologo_asignado')
            if asignado:
                code = None
                if isinstance(asignado, dict):
                    code = asignado.get('codigo') or asignado.get('patologo_code')
                    registro = asignado.get('registro_medico')
                else:
                    code = getattr(asignado, 'codigo', None) or getattr(asignado, 'patologo_code', None)
                    registro = getattr(asignado, 'registro_medico', None)
                
                # 1) Intentar por código de patólogo (patologo_code) - PRIORIDAD
                if code:
                    patologo = await self.patologo_repository.get_by_codigo(code)
                    if patologo and getattr(patologo, 'firma', None):
                        pathologist_signature = patologo.firma
                
                # 2) Si no se logró, intentar por ObjectId directo si luce como tal
                if not pathologist_signature and code and len(code) == 24 and all(c in '0123456789abcdef' for c in code.lower()):
                    patologo = await self.patologo_repository.get(code)
                    if patologo and getattr(patologo, 'firma', None):
                        pathologist_signature = patologo.firma
                
                # 3) Si no se logró, intentar por registro médico
                if not pathologist_signature and registro:
                    patologo = await self.patologo_repository.get_by_registro_medico(registro)
                    if patologo and getattr(patologo, 'firma', None):
                        pathologist_signature = patologo.firma
                
                # 4) Si tampoco, probar el mismo 'code' como registro médico
                if not pathologist_signature and code:
                    patologo = await self.patologo_repository.get_by_registro_medico(code)
                    if patologo and getattr(patologo, 'firma', None):
                        pathologist_signature = patologo.firma
                
                # 5) Fallback: usar la firma que venga en el caso si existe
                if not pathologist_signature:
                    if isinstance(asignado, dict):
                        pathologist_signature = asignado.get('firma')
                    else:
                        pathologist_signature = getattr(asignado, 'firma', None)
        except Exception as e:
            print(f"Error obteniendo firma del patólogo: {e}")
            pathologist_signature = None

        template = self.jinja_env.get_template("case_report.html")
        html: str = await template.render_async(
            case=case, 
            pathologist_signature=pathologist_signature,
            pruebas_complementarias=pruebas_complementarias
        )

        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.set_content(html, wait_until="load")
            pdf_bytes = await page.pdf(
                format="A4",
                margin={"top": "20mm", "right": "15mm", "bottom": "20mm", "left": "15mm"},
                print_background=True,
            )
            await context.close()
            await browser.close()

        return pdf_bytes



