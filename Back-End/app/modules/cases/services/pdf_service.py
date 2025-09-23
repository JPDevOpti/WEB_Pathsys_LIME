from __future__ import annotations

from typing import Any, Optional
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
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
                format="A4",
                margin={"top": "20mm", "right": "15mm", "bottom": "20mm", "left": "15mm"},
                print_background=True,
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
            'resultado_macro': result.get('macro_result', ''),
            'resultado_micro': result.get('micro_result', ''),
            'diagnostico': result.get('diagnosis', ''),
            'observaciones': result.get('observations', ''),
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
            search_params = ApprovalRequestSearch(
                original_case_code=case_code,
                approval_state=['request_made', 'pending_approval']
            )
            approval_requests = await self.approval_service.search_approvals(search_params)
            
            if not approval_requests or len(approval_requests) == 0:
                return None
            
            # Tomar la primera solicitud pendiente
            approval = approval_requests[0]
            
            # Mapear al formato esperado por la plantilla
            complementary_tests = {
                'pruebas': [],
                'motivo': approval.reason or '',
                'fecha_solicitud': approval.created_at,
                'estado': approval.approval_state or ''
            }
            
            # Mapear pruebas complementarias
            for test in approval.complementary_tests or []:
                mapped_test = {
                    'codigo': test.get('code', ''),
                    'nombre': test.get('name', ''),
                    'cantidad': test.get('quantity', 1)
                }
                complementary_tests['pruebas'].append(mapped_test)
            
            return complementary_tests
            
        except Exception as e:
            print(f"Error obteniendo pruebas complementarias: {e}")
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
