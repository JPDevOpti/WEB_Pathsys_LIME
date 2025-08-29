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
    const localRaw = localStorage.getItem('results_preview_payload')
    const sessionRaw = !localRaw ? sessionStorage.getItem('results_preview_payload') : null
    const raw = localRaw || sessionRaw
    payload.value = raw ? JSON.parse(raw) : null
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
    
    // Esperar a que las firmas estén cargadas
    if (!signaturesReady.value) {
      console.log('⏳ Esperando a que las firmas se carguen...')
      await new Promise(resolve => setTimeout(resolve, 1000))
    }
    
    // Usar directamente el contenedor de preview sin clonar
    const targetElement = previewContainer.value?.querySelector('.print-content') as HTMLElement
    if (!targetElement) {
      throw new Error('No se encontró el contenido para exportar')
    }
    
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
    allPages.forEach((page, index) => {
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
      margin: [0, 0, 0, 0], // Sin márgenes para evitar hojas en blanco
      filename,
      image: { type: 'jpeg', quality: 0.98 },
      html2canvas: { 
        scale: 1.5, 
        useCORS: true, 
        allowTaint: true,
        backgroundColor: '#ffffff',
        logging: true,
        removeContainer: false,
        x: 0, // Posición X inicial
        y: 0, // Posición Y inicial
        scrollX: 0, // Sin scroll horizontal
        scrollY: 0, // Sin scroll vertical
        width: undefined, // Usar ancho natural
        height: undefined, // Usar altura natural
        windowWidth: 816, // Ancho Carta en píxeles (8.5in * 96dpi)
        windowHeight: 1056 // Alto Carta en píxeles (11in * 96dpi)
      },
      jsPDF: { 
        unit: 'in', 
        format: 'letter', 
        orientation: 'portrait',
        compress: true,
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


