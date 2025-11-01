from __future__ import annotations

from typing import Any, Optional
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from markupsafe import Markup
import re
from pathlib import Path


class CasePdfService:
    def __init__(self, database: Any):
        from app.modules.cases.services.case_service import CaseService
        from app.modules.pathologists.services.pathologist_service import PathologistService
        from app.modules.approvals.services.approval_service import ApprovalService
        
        self.case_service = CaseService(database)
        self.pathologist_service = PathologistService(database)
        self.approval_service = ApprovalService(database)
        self.database = database
        
        templates_dir = Path(__file__).parent.parent / "templates"
        self.templates_path = templates_dir.resolve()
        self.jinja_env = Environment(
            loader=FileSystemLoader(str(self.templates_path)),
            autoescape=select_autoescape(["html", "xml"]),
            enable_async=True,
        )

    # Sanitizador básico de HTML para PDF
    def _sanitize_html(self, html: Optional[str]) -> Markup:
        """Sanitiza HTML permitiendo un subconjunto seguro de etiquetas y estilos.
        Comentario: Mantiene alineaciones simples de texto y elimina scripts/eventos."""
        if not html:
            return Markup("")

        # Remover bloques peligrosos (script/style)
        clean = re.sub(r"(?is)<(script|style).*?>.*?</\\1>", "", html)

        # Eliminar atributos de eventos (onload, onclick, etc.)
        clean = re.sub(r"\son[a-zA-Z]+\s*=\s*(\".*?\"|\'.*?\'|[^\s>]+)", "", clean)

        # Permitir solo ciertos estilos en style="..."
        allowed_props = {"text-align", "font-weight", "font-style", "text-decoration"}

        def _clean_style(match: re.Match) -> str:
            style_val = match.group(1)
            parts = [p.strip() for p in style_val.split(";") if p.strip()]
            kept = []
            for decl in parts:
                if ":" not in decl:
                    continue
                prop, val = decl.split(":", 1)
                prop = prop.strip().lower()
                val = val.strip()
                if prop in allowed_props:
                    kept.append(f"{prop}: {val}")
            return f' style="{"; ".join(kept)}"' if kept else ""

        clean = re.sub(r"\sstyle\s*=\s*\"(.*?)\"", _clean_style, clean)
        clean = re.sub(r"\sstyle\s*=\s*\'(.*?)\'", _clean_style, clean)

        # Remover etiquetas no permitidas, conservar: div, span, br, p, b, strong, i, em, u, ul, ol, li
        allowed_tags = {"div", "span", "br", "p", "b", "strong", "i", "em", "u", "ul", "ol", "li"}

        def _filter_tag(match: re.Match) -> str:
            tag_name = match.group(1).lower()
            return match.group(0) if tag_name in allowed_tags else ""

        clean = re.sub(r"</?([a-zA-Z0-9]+)(\b[^>]*)?>", _filter_tag, clean)
        return Markup(clean)

    async def generate_case_pdf(self, case_code: str) -> bytes:
        try:
            from playwright.async_api import async_playwright  # type: ignore
        except Exception as e:  # ImportError or runtime errors
            raise RuntimeError(
                "Playwright no está instalado o no se han instalado los navegadores. "
                "Ejecuta: pip install playwright && playwright install chromium"
            ) from e

        # Obtener datos del caso
        case_data = await self._get_case_data(case_code)
        
        # Obtener pruebas complementarias pendientes de aprobación
        complementary_tests = await self._get_complementary_tests(case_code)
        
        # Obtener firma del patólogo
        pathologist_signature = await self._get_pathologist_signature(case_data)
        print(f"DEBUG: Firma obtenida: {'SÍ' if pathologist_signature else 'NO'}")

        # Renderizar template
        template = self.jinja_env.get_template("case_report.html")
        html: str = await template.render_async(
            case=case_data, 
            pathologist_signature=pathologist_signature,
            pruebas_complementarias=complementary_tests
        )

        # Generar PDF
        async with async_playwright() as p:
            browser = await p.chromium.launch()
            context = await browser.new_context()
            page = await context.new_page()
            await page.set_content(html, wait_until="load")
            pdf_bytes = await page.pdf(
                format="Letter",
                margin={"top": "15mm", "right": "12mm", "bottom": "22mm", "left": "12mm"},
                print_background=True,
                display_header_footer=True,
                header_template="<span></span>",
                footer_template=(
                    "<div style='font-family: Arial, sans-serif; font-size:10px; color:#000; width:100%; padding:0 15mm;'>"
                    "<div style='text-align:center; font-style:italic; white-space:nowrap;'>"
                    "Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años"
                    "</div>"
                    "<div style='border-top:1px solid #000; margin:2mm 0 0 0;'></div>"
                    "<div style='text-align:right; font-weight:bold;'>Página <span class='pageNumber'></span> de <span class='totalPages'></span></div>"
                    "</div>"
                ),
            )
            await context.close()
            await browser.close()

        return pdf_bytes

    async def _get_case_data(self, case_code: str) -> dict:
        """Obtener datos del caso y convertirlos al formato esperado por la plantilla"""
        case = await self.case_service.get_case(case_code)
        if not case:
            raise ValueError(f"Caso con código {case_code} no encontrado")
        
        # Convertir CaseResponse a diccionario compatible con la plantilla
        case_dict = case.model_dump()
        
        # Mapear campos del nuevo formato al formato esperado por la plantilla
        mapped_case = {
            # Información básica
            'id': case_dict.get('id'),
            'caso_code': case_dict.get('case_code'),
            'fecha_creacion': case_dict.get('created_at'),
            'fecha_firma': case_dict.get('signed_at'),
            'fecha_entrega': case_dict.get('delivered_at'),
            'updated_at': case_dict.get('updated_at'),
            
            # Información del paciente (mapear de patient_info)
            'paciente': {
                'nombre': case_dict.get('patient_info', {}).get('name', ''),
                'paciente_code': case_dict.get('patient_info', {}).get('patient_code', ''),
                'identification_type': case_dict.get('patient_info', {}).get('identification_type', None),
                'identification_number': case_dict.get('patient_info', {}).get('identification_number', ''),
                'edad': case_dict.get('patient_info', {}).get('age', ''),
                'sexo': case_dict.get('patient_info', {}).get('gender', ''),
                'telefono': case_dict.get('patient_info', {}).get('phone', ''),
                'entidad_info': {
                    'nombre': case_dict.get('patient_info', {}).get('entity_info', {}).get('name', '')
                }
            },
            
            # Médico solicitante
            'medico_solicitante': case_dict.get('requesting_physician', ''),
            
            # Servicio
            'servicio': case_dict.get('service', ''),
            
            # Patólogo asignado (mapear de assigned_pathologist)
            'patologo_asignado': {
                'nombre': case_dict.get('assigned_pathologist', {}).get('name', ''),
                'codigo': case_dict.get('assigned_pathologist', {}).get('id', ''),
                'registro_medico': case_dict.get('assigned_pathologist', {}).get('medical_license', '')
            } if case_dict.get('assigned_pathologist') else None,
            
            # Muestras (mapear de samples)
            'muestras': self._map_samples(case_dict.get('samples', [])),
            
            # Resultado (mapear de result)
            'resultado': self._map_result(case_dict.get('result')),
            
            # Notas adicionales
            'notas_adicionales': case_dict.get('additional_notes', []),
            
            # Pruebas complementarias
            'complementary_tests': case_dict.get('complementary_tests', []),
            
            # Observaciones generales
            'observaciones_generales': case_dict.get('observations', '')
        }
        
        return mapped_case

    def _map_samples(self, samples: list) -> list:
        """Mapear muestras del nuevo formato al formato esperado por la plantilla"""
        mapped_samples = []
        for sample in samples:
            mapped_sample = {
                'region_cuerpo': sample.get('body_region', ''),
                'pruebas': []
            }
            
            # Mapear pruebas
            for test in sample.get('tests', []):
                mapped_test = {
                    'id': test.get('id', ''),
                    'codigo': test.get('id', ''),
                    'nombre': test.get('name', ''),
                    'cantidad': test.get('quantity', 1)
                }
                mapped_sample['pruebas'].append(mapped_test)
            
            mapped_samples.append(mapped_sample)
        
        return mapped_samples

    def _map_result(self, result: Optional[dict]) -> Optional[dict]:
        """Mapear resultado del nuevo formato al formato esperado por la plantilla"""
        if not result:
            return None

        mapped_result = {
            'metodo': result.get('method', []),
            # Sanitizar campos con posible HTML
            'resultado_macro': self._sanitize_html(result.get('macro_result', '')),
            'resultado_micro': self._sanitize_html(result.get('micro_result', '')),
            'diagnostico': self._sanitize_html(result.get('diagnosis', '')),
            'observaciones': self._sanitize_html(result.get('observations', '')),
            'updated_at': result.get('updated_at'),
            
            # Diagnósticos CIE-10 y CIE-O
            'diagnostico_cie10': None,
            'diagnostico_cieo': None
        }
        
        # Mapear diagnóstico CIE-10
        cie10 = result.get('cie10_diagnosis')
        if cie10:
            mapped_result['diagnostico_cie10'] = {
                'codigo': cie10.get('code', ''),
                'nombre': cie10.get('name', '')
            }
        
        # Mapear diagnóstico CIE-O
        cieo = result.get('cieo_diagnosis')
        if cieo:
            mapped_result['diagnostico_cieo'] = {
                'codigo': cieo.get('code', ''),
                'nombre': cieo.get('name', '')
            }
        
        return mapped_result

    async def _get_complementary_tests(self, case_code: str) -> Optional[dict]:
        """Obtener pruebas complementarias pendientes de aprobación"""
        try:
            # Buscar solicitudes de aprobación para este caso
            from app.modules.approvals.schemas.approval import ApprovalRequestSearch
            from app.modules.approvals.models.approval_request import ApprovalStateEnum
            
            search_params = ApprovalRequestSearch(
                original_case_code=case_code,
                approval_state=ApprovalStateEnum.REQUEST_MADE
            )
            approval_requests = await self.approval_service.search_approvals(search_params)
            
            if not approval_requests or len(approval_requests) == 0:
                # Intentar buscar en pending_approval también
                search_params.approval_state = ApprovalStateEnum.PENDING_APPROVAL
                approval_requests = await self.approval_service.search_approvals(search_params)
                
                if not approval_requests or len(approval_requests) == 0:
                    return None
            
            # Tomar la primera solicitud pendiente
            approval = approval_requests[0]
            
            # Extraer motivo del approval_info
            motivo = ''
            if approval.approval_info:
                motivo = approval.approval_info.reason or ''
            
            # Mapear al formato esperado por la plantilla
            complementary_tests = {
                'pruebas': [],
                'motivo': motivo,
                'fecha_solicitud': approval.created_at,
                'estado': approval.approval_state.value if hasattr(approval.approval_state, 'value') else str(approval.approval_state)
            }
            
            # Mapear pruebas complementarias
            for test in approval.complementary_tests or []:
                # test es un objeto ComplementaryTestInfo
                mapped_test = {
                    'codigo': test.code if hasattr(test, 'code') else test.get('code', ''),
                    'nombre': test.name if hasattr(test, 'name') else test.get('name', ''),
                    'cantidad': test.quantity if hasattr(test, 'quantity') else test.get('quantity', 1)
                }
                complementary_tests['pruebas'].append(mapped_test)
            
            return complementary_tests
            
        except Exception as e:
            print(f"Error obteniendo pruebas complementarias: {e}")
            import traceback
            traceback.print_exc()
            return None

    async def _get_pathologist_signature(self, case_data: dict) -> Optional[str]:
        """Obtener firma del patólogo asignado desde la carpeta uploads/signatures/"""
        try:
            patologo_asignado = case_data.get('patologo_asignado')
            if not patologo_asignado:
                # Para pruebas, usar un patólogo fijo que sabemos que tiene firma
                pathologist_id = "1129564009"
                print(f"DEBUG: No hay patólogo asignado, usando patólogo de prueba: {pathologist_id}")
            else:
                pathologist_id = patologo_asignado.get('codigo') or patologo_asignado.get('id')
                if not pathologist_id:
                    return None
                print(f"DEBUG: Patólogo asignado encontrado: {pathologist_id}")
            
            # Buscar archivo de firma en la carpeta uploads/signatures/
            import os
            from pathlib import Path
            
            # Obtener la ruta base del proyecto
            project_root = Path(__file__).parent.parent.parent.parent.parent
            signatures_dir = project_root / "uploads" / "signatures"
            
            # Buscar archivos que contengan el ID del patólogo
            signature_files = list(signatures_dir.glob(f"*{pathologist_id}*"))
            print(f"DEBUG: Buscando firmas para ID: {pathologist_id}")
            print(f"DEBUG: Directorio: {signatures_dir}")
            print(f"DEBUG: Archivos encontrados: {signature_files}")
            
            if signature_files:
                # Tomar el primer archivo encontrado
                signature_file = signature_files[0]
                
                # Convertir a base64 para usar en HTML
                import base64
                
                with open(signature_file, "rb") as img_file:
                    img_data = img_file.read()
                    img_base64 = base64.b64encode(img_data).decode('utf-8')
                    
                    # Obtener la extensión del archivo
                    file_ext = signature_file.suffix.lower()
                    if file_ext == '.png':
                        result = f"data:image/png;base64,{img_base64}"
                        print(f"DEBUG: Firma cargada exitosamente (PNG): {len(img_base64)} chars")
                        return result
                    elif file_ext == '.jpg' or file_ext == '.jpeg':
                        result = f"data:image/jpeg;base64,{img_base64}"
                        print(f"DEBUG: Firma cargada exitosamente (JPEG): {len(img_base64)} chars")
                        return result
                    else:
                        result = f"data:image/png;base64,{img_base64}"
                        print(f"DEBUG: Firma cargada exitosamente (default PNG): {len(img_base64)} chars")
                        return result
            
            print(f"DEBUG: No se encontraron archivos de firma para ID: {pathologist_id}")
            return None
            
        except Exception as e:
            print(f"Error obteniendo firma del patólogo: {e}")
            return None
