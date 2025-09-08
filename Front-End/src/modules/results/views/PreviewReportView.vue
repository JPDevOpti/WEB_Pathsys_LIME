<template>
  <div class="preview-container">
    <!-- Controles de navegación - ocultos en impresión -->
    <div class="controls-section print-hidden">
      <div class="flex items-center justify-between mb-4">
        <h1 class="text-lg font-semibold">
          {{ payload?.multipleCases && payload?.cases?.length ? `Previsualización de ${payload.cases.length} Informes` : 'Previsualización de Informe' }}
        </h1>
        <div class="flex gap-2">
          <button class="px-3 py-2 text-sm rounded border border-gray-300 bg-white hover:bg-gray-100 disabled:opacity-60" :disabled="isDownloading" @click="downloadPdf">
            {{ isDownloading ? 'Generando PDF…' : 'Descargar PDF' }}
          </button>
          <button class="px-3 py-2 text-sm rounded border border-gray-300 bg-white hover:bg-gray-100" @click="goBack">Volver</button>
        </div>
      </div>
    </div>

    <!-- Contenedor del PDF sin padding para impresión correcta -->
    <div ref="previewContainer" class="pdf-container">
      <PDFReportPreview 
        :payload="payload" 
        ref="pdfPreviewRef"
        @all-signatures-loaded="handleAllSignaturesLoaded"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { onMounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import html2pdf from 'html2pdf.js'
import PDFReportPreview from '@/shared/components/PDFs/PDFReportPreview.vue'

const router = useRouter()
const payload = ref<any>(null)
const isDownloading = ref(false)
const pdfPreviewRef = ref<any>(null)
const previewContainer = ref<HTMLElement | null>(null)
const signaturesReady = ref(false)

onMounted(() => {
  try {
    const sessionRaw = sessionStorage.getItem('results_preview_payload')
    const localRaw = !sessionRaw ? localStorage.getItem('results_preview_payload') : null
    const raw = sessionRaw || localRaw
    payload.value = raw ? JSON.parse(raw) : null
    if (payload.value) normalizePayload(payload.value)
  } catch (error) {
    payload.value = null
  }
})

function goBack() { router.back() }

function handleAllSignaturesLoaded() {
  signaturesReady.value = true
}

async function downloadPdf() {
  if (isDownloading.value) return
  try {
    isDownloading.value = true
    await nextTick()
    // Esperar que fuentes estén listas (mejor soporte de caracteres acentuados)
    if (document?.fonts?.ready) {
      try { await document.fonts.ready } catch {}
    }
    // Pequeña espera para asegurar que el DOM interno se haya renderizado
    if (!signaturesReady.value) await new Promise(r => setTimeout(r, 300))
    // Selección robusta del contenido a exportar
    let targetElement = previewContainer.value?.querySelector('.print-content') as HTMLElement | null
    if (!targetElement) targetElement = (previewContainer.value?.firstElementChild as HTMLElement) || null
    if (!targetElement) targetElement = previewContainer.value as HTMLElement | null
    if (!targetElement) throw new Error('No se encontró el contenedor de previsualización para exportar')
    
    // Limpiar estilos que puedan causar problemas de alineación
    const originalStyles = {
      margin: targetElement.style.margin,
      padding: targetElement.style.padding,
      position: targetElement.style.position,
      left: targetElement.style.left,
      top: targetElement.style.top
    }
    
    // Aplicar estilos limpios para la generación del PDF
    targetElement.style.margin = '0'
    targetElement.style.padding = '0'
    targetElement.style.position = 'relative'
    targetElement.style.left = '0'
    targetElement.style.top = '0'
    
    // Limpiar estilos de todos los elementos hijos que puedan causar hojas en blanco
    const allPages = targetElement.querySelectorAll('.report-page')
    allPages.forEach((page) => {
      const pageElement = page as HTMLElement
      pageElement.style.margin = '0'
      pageElement.style.marginBottom = '0'
      pageElement.style.marginTop = '0'
      pageElement.style.padding = '0.5in 0.5in 0.3in 0.5in'
      pageElement.style.boxSizing = 'border-box'
      pageElement.style.width = '8.5in'
      pageElement.style.height = '11in'
      pageElement.style.pageBreakAfter = 'auto'
      pageElement.style.breakAfter = 'auto'
      pageElement.style.pageBreakBefore = 'auto'
      pageElement.style.breakBefore = 'auto'
      pageElement.style.pageBreakInside = 'avoid'
      pageElement.style.breakInside = 'avoid'
    })
    
    const filename = payload.value?.cases?.length
      ? `informes_${payload.value.cases.length}_casos.pdf`
      : `informe_${payload.value?.sampleId || 'caso'}.pdf`

    const options = {
      margin: [0, 0, 0, 0],
      filename,
      image: { type: 'png', quality: 1 },
      html2canvas: {
        scale: 2.2,        // Mayor resolución (≈ 210–220 DPI efectivos)
        useCORS: true,
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: false,
        letterRendering: true,
        removeContainer: true,
        x: 0,
        y: 0,
        scrollX: 0,
        scrollY: 0,
        windowWidth: 816,
        windowHeight: 1056
      },
      jsPDF: {
        unit: 'pt',        // Puntos para mejor precisión tipográfica
        format: 'letter',
        orientation: 'portrait',
        compress: false,   // Evita artefactos en textos/firma
        putOnlyUsedFonts: true
      }
    }

    await html2pdf().from(targetElement).set(options).save()
    
    // Restaurar estilos originales
    targetElement.style.margin = originalStyles.margin
    targetElement.style.padding = originalStyles.padding
    targetElement.style.position = originalStyles.position
    targetElement.style.left = originalStyles.left
    targetElement.style.top = originalStyles.top
    
    // Restaurar estilos de los elementos hijos
    const allPagesRestore = targetElement.querySelectorAll('.report-page')
    allPagesRestore.forEach((page) => {
      const pageElement = page as HTMLElement
      pageElement.style.margin = ''
      pageElement.style.marginBottom = ''
      pageElement.style.marginTop = ''
      pageElement.style.padding = ''
      pageElement.style.boxSizing = ''
      pageElement.style.width = ''
      pageElement.style.height = ''
      pageElement.style.pageBreakAfter = ''
      pageElement.style.breakAfter = ''
      pageElement.style.pageBreakBefore = ''
      pageElement.style.breakBefore = ''
      pageElement.style.pageBreakInside = ''
      pageElement.style.breakInside = ''
    })
    
  } catch (e) {
    console.error('Error generando PDF:', e)
    alert('Error al generar el PDF. Por favor, inténtalo de nuevo.')
  } finally {
    isDownloading.value = false
  }
}

// Normalizar payload: asegurar method como array y methodText para compatibilidad
function normalizePayload(p: any) {
  const normalizeOne = (obj: any) => {
    if (!obj) return
    if (obj.sections) {
      const m = obj.sections.method
      if (Array.isArray(m)) obj.sections.method = m
      else if (typeof m === 'string' && m.trim()) obj.sections.method = [m.trim()]
      else obj.sections.method = []
      ;(obj.sections as any).methodText = obj.sections.method.length ? obj.sections.method.join(', ') : ''
    }
    // Normalizar diagnósticos y completar desde backend si faltan
    obj.diagnosis = obj.diagnosis || {}
    // CIE-10: aceptar estructura {primary:{codigo,nombre}} o {codigo,nombre}
    if (obj.diagnosis.cie10 && typeof obj.diagnosis.cie10 === 'object') {
      const src = obj.diagnosis.cie10
      const codigo = src?.primary?.codigo || src?.codigo
      const nombre = src?.primary?.nombre || src?.nombre
      obj.diagnosis.cie10 = (codigo || nombre) ? { codigo, nombre } : undefined
    }
    if (!obj.diagnosis.cie10 && obj.caseDetails?.resultado?.diagnostico_cie10) {
      const d = obj.caseDetails.resultado.diagnostico_cie10
      if (d) obj.diagnosis.cie10 = { codigo: d.codigo, nombre: d.nombre }
    }
    if (obj.diagnosis.cieo && typeof obj.diagnosis.cieo === 'object') {
      const src = obj.diagnosis.cieo
      const codigo = src?.primary?.codigo || src?.codigo
      const nombre = src?.primary?.nombre || src?.nombre
      obj.diagnosis.cieo = (codigo || nombre) ? { codigo, nombre } : undefined
    }
    if (!obj.diagnosis.cieo && obj.caseDetails?.resultado?.diagnostico_cieo) {
      const d = obj.caseDetails.resultado.diagnostico_cieo
      obj.diagnosis.cieo = d ? { codigo: d.codigo, nombre: d.nombre } : undefined
    }
    // Si no hay diagnosis.formatted, no lo generamos desde CIE; priorizamos diagnóstico libre
    if (!obj.diagnosis.formatted) {
      const freeDx = obj.sections?.diagnosis || obj.caseDetails?.resultado?.diagnostico || ''
      if (freeDx) obj.diagnosis.formatted = '' // mantener libre separado y no sobreescribir
    }
  }
  if (p?.cases && Array.isArray(p.cases)) p.cases.forEach((c: any) => normalizeOne(c))
  else normalizeOne(p)
}
</script>

<style scoped>
/* Contenedor principal con padding solo para la vista previa */
.preview-container {
  padding: 1rem;
}

@media (min-width: 768px) {
  .preview-container {
    padding: 1.5rem;
  }
}

/* Contenedor del PDF sin padding para impresión correcta */
.pdf-container {
  margin: 0;
  padding: 0;
  position: relative;
  min-height: 11in; /* Altura de Carta */
}

/* Asegurar que el contenido del PDF tenga la altura correcta */
.pdf-container :deep(.print-content) {
  min-height: 11in; /* Altura de Carta */
}

.pdf-container :deep(.report-page) {
  min-height: 11in !important; /* Altura de Carta */
  padding: 0.5in 0.5in 0.3in 0.5in !important;
  box-sizing: border-box !important;
  overflow: visible !important;
}

/* Ocultar controles en impresión */
@media print {
  .preview-container {
    padding: 0 !important;
    margin: 0 !important;
  }
  
  .controls-section {
    display: none !important;
  }
  
  .pdf-container {
    margin: 0 !important;
    padding: 0 !important;
    position: static !important;
    height: auto !important;
  }
}
</style>


