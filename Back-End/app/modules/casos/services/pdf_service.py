from __future__ import annotations

from typing import Any
import asyncio
from jinja2 import Environment, FileSystemLoader, select_autoescape
from pathlib import Path


class CasePdfService:
    def __init__(self, database: Any):
        from app.modules.casos.services.caso_service import CasoService
        self.caso_service = CasoService(database)
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

        template = self.jinja_env.get_template("case_report.html")
        html: str = await template.render_async(case=case)

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



