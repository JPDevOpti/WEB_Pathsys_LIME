<template>
  <div class="case-report-container">
    <!-- Elementos de medición ocultos -->
    <div class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
      <div ref="measureBodyRef" style="width:7.5in; font-size:12px; line-height:1.4; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>
      <div ref="measureHeaderRef" style="width:7.5in; box-sizing:border-box;">
        <div class="report-header">
          <table class="w-full text-sm border border-gray-300 mb-4" style="border-collapse: collapse;">
            <tr>
              <td class="border border-gray-300 p-2" style="width: 75%; vertical-align: middle;">
                <div class="text-base font-semibold">Departamento de Patología</div>
                <div class="text-xs leading-tight">
                  <div>Hospital San Vicente Fundación</div>
                  <div>Calle 64 Carrera 51D. Bloque 13</div>
                  <div>Tel. 6042192400</div>
                </div>
              </td>
              <td class="border border-gray-300 p-2" style="width: 25%; vertical-align: middle;">
                <div><span class="font-semibold">Informe No:</span> {{ caseData.caseDetails?.CasoCode || caseData.sampleId || '—' }}</div>
                <div><span class="font-semibold">Fecha de Recibo:</span> {{ formatDate(caseData.caseDetails?.fecha_creacion) || '—' }}</div>
                <div><span class="font-semibold">Fecha de Informe:</span> {{ formatDate(caseData.generatedAt || new Date().toISOString()) }}</div>
              </td>
            </tr>
          </table>
        </div>
        <div class="patient-info text-xs space-y-0.5 mb-4">
          <div><strong class="inline-label">Documento de identidad:</strong><span class="label-value">{{ caseData.patient?.document || caseData.caseDetails?.paciente?.cedula || '—' }}</span></div>
          <div><strong class="inline-label">Paciente:</strong><span class="label-value">{{ caseData.patient?.fullName || caseData.caseDetails?.paciente?.nombre || '—' }}</span></div>
          <div>
            <strong class="inline-label">Edad:</strong><span class="label-value">{{ caseData.caseDetails?.paciente?.edad ?? '—' }}</span>
            <span class="ml-4"><strong class="inline-label">Sexo:</strong><span class="label-value">{{ caseData.caseDetails?.paciente?.sexo || '—' }}</span></span>
          </div>
          <div>
            <strong class="inline-label">Institución:</strong><span class="label-value">{{ caseData.caseDetails?.entidad_info?.nombre || caseData.patient?.entity || '—' }}</span>
            <span class="ml-4"><strong class="inline-label">Servicio:</strong><span class="label-value">{{ caseData.caseDetails?.servicio || '—' }}</span></span>
            <span class="ml-4"><strong class="inline-label">Recibido N°:</strong><span class="label-value">{{ recibidoNumero(caseData.caseDetails?.CasoCode || caseData.sampleId) || '—' }}</span></span>
          </div>
          <div><strong class="inline-label">Médico Solicitante:</strong><span class="label-value">{{ caseData.caseDetails?.medico_solicitante?.nombre || '—' }}</span></div>
        </div>
      </div>
      <div ref="measureFooterRef" style="width:7.5in; box-sizing:border-box;">
        <div class="report-footer">
          <div class="signature-section">
            <div class="border-t border-gray-400 w-2/3 mx-auto mb-1"></div>
            <div class="text-center text-xs">Médico Patólogo: {{ caseData.caseDetails?.patologo_asignado?.nombre || '—' }}</div>
          </div>
          <div class="footer-section text-center text-xs text-gray-700 mt-2 pt-2">
            <div>Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años</div>
            <div class="my-1 leading-none">___________________________________________________________________________________________</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Contenido principal con paginación -->
    <div v-if="!needsPagination" class="report-page" :style="pageStyle">
      <div class="page-header" :style="{ height: `${headerPx}px`, maxHeight: `${headerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
        <div class="report-header">
          <table class="w-full text-sm border border-gray-300 mb-4" style="border-collapse: collapse;">
            <tr>
              <td class="border border-gray-300 p-2" style="width: 75%; vertical-align: middle;">
                <div class="text-base font-semibold">Departamento de Patología</div>
                <div class="text-xs leading-tight">
                  <div>Hospital San Vicente Fundación</div>
                  <div>Calle 64 Carrera 51D. Bloque 13</div>
                  <div>Tel. 6042192400</div>
                </div>
              </td>
              <td class="border border-gray-300 p-2" style="width: 25%; vertical-align: middle;">
                <div><span class="font-semibold">Informe No:</span> {{ caseData.caseDetails?.CasoCode || caseData.sampleId || '—' }}</div>
                <div><span class="font-semibold">Fecha de Recibo:</span> {{ formatDate(caseData.caseDetails?.fecha_creacion) || '—' }}</div>
                <div><span class="font-semibold">Fecha de Informe:</span> {{ formatDate(caseData.generatedAt || new Date().toISOString()) }}</div>
              </td>
            </tr>
          </table>
        </div>
        <div class="patient-info text-xs space-y-0.5 mb-4">
          <div><strong>Documento de identidad:</strong> {{ caseData.patient?.document || caseData.caseDetails?.paciente?.cedula || '—' }}</div>
          <div><strong>Paciente:</strong> {{ caseData.patient?.fullName || caseData.caseDetails?.paciente?.nombre || '—' }}</div>
          <div>
            <strong>Edad:</strong> {{ caseData.caseDetails?.paciente?.edad ?? '—' }}
            <span class="ml-4"><strong>Sexo:</strong> {{ caseData.caseDetails?.paciente?.sexo || '—' }}</span>
          </div>
          <div>
            <strong>Institución:</strong> {{ caseData.caseDetails?.entidad_info?.nombre || caseData.patient?.entity || '—' }}
            <span class="ml-4"><strong>Servicio:</strong> {{ caseData.caseDetails?.servicio || '—' }}</span>
            <span class="ml-4"><strong>Recibido N°:</strong> {{ recibidoNumero(caseData.caseDetails?.CasoCode || caseData.sampleId) || '—' }}</span>
          </div>
          <div><strong>Médico Solicitante:</strong> {{ caseData.caseDetails?.medico_solicitante?.nombre || '—' }}</div>
        </div>
      </div>

      <div class="page-body" :style="{ height: `${availableFirstPx}px`, maxHeight: `${availableFirstPx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
        <div class="report-content text-xs space-y-3">
          <div class="section-muestra">
            <h3 class="font-semibold mb-1 text-sm">MUESTRA:</h3>
            <div class="whitespace-pre-wrap">{{ buildSamplesDescription(caseData.caseDetails?.muestras) }}</div>
          </div>

          <div class="section-metodo">
            <h3 class="font-semibold mb-1 text-sm">MÉTODO UTILIZADO</h3>
            <div class="whitespace-pre-wrap break-words overflow-hidden">{{ getMethodText(caseData.sections) || '—' }}</div>
          </div>

          <div class="section-macro">
            <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MACROSCÓPICA</h3>
            <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseData.sections?.macro || '—' }}</div>
          </div>

          <div class="section-micro">
            <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MICROSCÓPICA</h3>
            <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseData.sections?.micro || '—' }}</div>
          </div>

          <div class="section-diagnostico">
            <h3 class="font-semibold mb-1 text-sm">DIAGNÓSTICO</h3>
            <div class="whitespace-pre-wrap break-words overflow-hidden">{{ getDiagnosisText(caseData.sections, caseData.diagnosis) || '—' }}</div>
          </div>

          <div class="section-cie-codes">
            <div class="mt-2 text-xs text-gray-800">
              <div class="mb-1">
                <strong>CIE-10:</strong> {{ (caseData.diagnosis?.cie10?.primary?.codigo || caseData.diagnosis?.cie10?.codigo) ?? '—' }}
                <template v-if="(caseData.diagnosis?.cie10?.primary?.nombre || caseData.diagnosis?.cie10?.nombre)">
                  - {{ caseData.diagnosis?.cie10?.primary?.nombre || caseData.diagnosis?.cie10?.nombre }}
                </template>
              </div>
              <div class="mb-1">
                <strong>CIE-O:</strong> {{ caseData.diagnosis?.cieo?.codigo ?? '—' }}
                <template v-if="caseData.diagnosis?.cieo?.nombre"> - {{ caseData.diagnosis.cieo.nombre }}</template>
              </div>
            </div>
          </div>
        </div>
      </div>

      <div class="page-footer" :style="{ height: `${footerPx}px`, maxHeight: `${footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
        <div class="report-footer">
          <div class="signature-section">
            <div class="border-t border-gray-400 w-2/3 mx-auto mb-1"></div>
            <div class="text-center text-xs">Médico Patólogo: {{ caseData.caseDetails?.patologo_asignado?.nombre || '—' }}</div>
          </div>
          <div class="footer-section text-center text-xs text-gray-700 mt-2 pt-2">
            <div>Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años</div>
            <div class="my-1 leading-none">___________________________________________________________________________________________</div>
          </div>
        </div>
      </div>
    </div>

    <!-- Páginas múltiples cuando hay overflow -->
    <template v-else>
      <div
        v-for="(page, pageIndex) in pages"
        :key="`page-${pageIndex}`"
        class="report-page"
        :style="pageStyle"
      >
        <div class="page-header" :style="{ height: `${headerPx}px`, maxHeight: `${headerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
          <div class="report-header">
            <table class="w-full text-sm border border-gray-300 mb-4" style="border-collapse: collapse;">
              <tr>
                <td class="border border-gray-300 p-2" style="width: 75%; vertical-align: middle;">
                  <div class="text-base font-semibold">Departamento de Patología</div>
                  <div class="text-xs leading-tight">
                    <div>Hospital San Vicente Fundación</div>
                    <div>Calle 64 Carrera 51D. Bloque 13</div>
                    <div>Tel. 6042192400</div>
                  </div>
                </td>
                <td class="border border-gray-300 p-2" style="width: 25%; vertical-align: middle;">
                  <div><span class="font-semibold">Informe No:</span> {{ caseData.caseDetails?.CasoCode || caseData.sampleId || '—' }}</div>
                  <div><span class="font-semibold">Fecha de Recibo:</span> {{ formatDate(caseData.caseDetails?.fecha_creacion) || '—' }}</div>
                  <div><span class="font-semibold">Fecha de Informe:</span> {{ formatDate(caseData.generatedAt || new Date().toISOString()) }}</div>
                </td>
              </tr>
            </table>
          </div>
          <div class="patient-info text-xs space-y-0.5 mb-4">
            <div><strong class="inline-label">Documento de identidad:</strong><span class="label-value">{{ caseData.patient?.document || caseData.caseDetails?.paciente?.cedula || '—' }}</span></div>
            <div><strong class="inline-label">Paciente:</strong><span class="label-value">{{ caseData.patient?.fullName || caseData.caseDetails?.paciente?.nombre || '—' }}</span></div>
            <div>
              <strong class="inline-label">Edad:</strong><span class="label-value">{{ caseData.caseDetails?.paciente?.edad ?? '—' }}</span>
              <span class="ml-4"><strong class="inline-label">Sexo:</strong><span class="label-value">{{ caseData.caseDetails?.paciente?.sexo || '—' }}</span></span>
            </div>
            <div>
              <strong class="inline-label">Institución:</strong><span class="label-value">{{ caseData.caseDetails?.entidad_info?.nombre || caseData.patient?.entity || '—' }}</span>
              <span class="ml-4"><strong class="inline-label">Servicio:</strong><span class="label-value">{{ caseData.caseDetails?.servicio || '—' }}</span></span>
              <span class="ml-4"><strong class="inline-label">Recibido N°:</strong><span class="label-value">{{ recibidoNumero(caseData.caseDetails?.CasoCode || caseData.sampleId) || '—' }}</span></span>
            </div>
            <div><strong class="inline-label">Médico Solicitante:</strong><span class="label-value">{{ caseData.caseDetails?.medico_solicitante?.nombre || '—' }}</span></div>
          </div>
        </div>

        <div class="page-body" :style="{ height: `${page.isFirstPage ? availableFirstPx : availableContPx}px`, maxHeight: `${page.isFirstPage ? availableFirstPx : availableContPx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
          <div v-html="page.content" class="dynamic-content"></div>
        </div>

        <div v-if="page.isLastPage" class="page-footer" :style="{ height: `${footerPx}px`, maxHeight: `${footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
          <div class="report-footer">
            <div class="signature-section">
              <div class="border-t border-gray-400 w-2/3 mx-auto mb-1"></div>
              <div class="text-center text-xs">Médico Patólogo: {{ caseData.caseDetails?.patologo_asignado?.nombre || '—' }}</div>
            </div>
            <div class="footer-section text-center text-xs text-gray-700 mt-2 pt-2">
              <div>Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años</div>
              <div class="my-1 leading-none">___________________________________________________________________________________________</div>
            </div>
          </div>
        </div>
      </div>
    </template>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, onMounted, nextTick, watch } from 'vue'

interface CaseData {
  sampleId: string
  patient: any
  caseDetails: any
  sections: { method?: string | string[]; methodText?: string; macro: string; micro: string; diagnosis: string }
  diagnosis?: { cie10?: { codigo?: string, nombre?: string, primary?: any }, cieo?: { codigo?: string, nombre?: string, primary?: any }, formatted?: string }
  generatedAt: string
}

const props = defineProps<{ caseData: CaseData }>()

const measureBodyRef = ref<HTMLElement>()
const measureHeaderRef = ref<HTMLElement>()
const measureFooterRef = ref<HTMLElement>()

const needsPagination = ref(false)
const pages = ref<any[]>([])
const headerPx = ref(0)
const footerPx = ref(0)
const availableFirstPx = ref(0)
const availableContPx = ref(0)

// Página interna mide 10in de alto útil + 1in de padding total (0.5in arriba y abajo) = 11in exactos Carta
const pageStyle = computed(() => ({
  width: '7.5in',
  minHeight: '11in',
  maxHeight: '11in',
  margin: '0 auto',
  padding: '0.5in',
  boxSizing: 'border-box' as const,
  backgroundColor: 'white',
  position: 'relative' as const
}))

function buildSamplesDescription(list: any[] | undefined): string {
  if (!list || list.length === 0) return '—'
  const regiones = list
    .map(it => (it?.region_cuerpo || '').toString().trim())
    .filter(Boolean)
  return regiones.length ? Array.from(new Set(regiones)).join(' | ') : '—'
}

function getMethodText(sec?: { method?: string | string[], methodText?: string } | null): string {
  if (!sec) return ''
  const mt = (sec as any).methodText
  if (typeof mt === 'string' && mt.trim()) return mt
  const m = (sec as any).method
  if (Array.isArray(m)) return m.filter((x)=>typeof x==='string' && x.trim()).join(', ')
  if (typeof m === 'string') return m
  return ''
}

function formatDate(iso?: string): string | null {
  if (!iso) return null
  try {
    const d = new Date(iso)
    const dd = d.toLocaleDateString('es-CO', { year: 'numeric', month: '2-digit', day: '2-digit' })
    const tt = d.toLocaleTimeString('es-CO', { hour: '2-digit', minute: '2-digit' })
    return `${dd} ${tt}`
  } catch {
    return null
  }
}

function recibidoNumero(casoCode?: string): string | null {
  if (!casoCode) return null
  const parts = String(casoCode).split('-')
  if (parts.length < 2) return casoCode
  return parts.slice(1).join('-')
}

function getDiagnosisText(
  sec?: { diagnosis?: string } | null,
  diag?: { formatted?: string } | null
): string {
  const free = (sec?.diagnosis ?? '').toString().trim()
  if (free) return free
  const formatted = (diag?.formatted ?? '').toString().trim()
  if (formatted) return formatted
  return ''
}

function calculatePageMetrics() {
  if (!measureHeaderRef.value || !measureFooterRef.value) return

  // Altura interna disponible (11in total - 1in padding = 10in de contenido bruto)
  const totalPagePx = 11 * 96
  const paddingPx = 0.5 * 96 * 2 // 1in
  const contentAreaPx = totalPagePx - paddingPx // 10in

  headerPx.value = measureHeaderRef.value.scrollHeight
  footerPx.value = measureFooterRef.value.scrollHeight

  // Dejar un margen de seguridad de 4px para evitar corte inferior por rounding de html2canvas
  const safety = 4
  availableFirstPx.value = contentAreaPx - headerPx.value - footerPx.value - safety
  availableContPx.value = contentAreaPx - headerPx.value - safety
}

function formatBodyContent(): string {
  const sections = [
    {
      title: 'MUESTRA:',
      content: buildSamplesDescription(props.caseData.caseDetails?.muestras)
    },
    {
      title: 'MÉTODO UTILIZADO',
      content: getMethodText(props.caseData.sections) || '—'
    },
    {
      title: 'DESCRIPCIÓN MACROSCÓPICA',
      content: props.caseData.sections?.macro || '—'
    },
    {
      title: 'DESCRIPCIÓN MICROSCÓPICA',
      content: props.caseData.sections?.micro || '—'
    },
    {
      title: 'DIAGNÓSTICO',
      content: getDiagnosisText(props.caseData.sections, props.caseData.diagnosis) || '—'
    },
    {
      title: 'CIE-10',
      content: `${(props.caseData.diagnosis?.cie10?.primary?.codigo || props.caseData.diagnosis?.cie10?.codigo) ?? '—'}${(props.caseData.diagnosis?.cie10?.primary?.nombre || props.caseData.diagnosis?.cie10?.nombre) ? ` - ${props.caseData.diagnosis?.cie10?.primary?.nombre || props.caseData.diagnosis?.cie10?.nombre}` : ''}`
    },
    {
      title: 'CIE-O',
      content: `${props.caseData.diagnosis?.cieo?.codigo ?? '—'}${props.caseData.diagnosis?.cieo?.nombre ? ` - ${props.caseData.diagnosis.cieo.nombre}` : ''}`
    }
  ]

  return sections.map(section => `
    <div class="section-item" style="margin-bottom: 12px;">
      <h3 style="font-weight: 600; margin-bottom: 4px; font-size: 12px; color: #374151;">${section.title}</h3>
      <div style="white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; color: #111827;">${section.content}</div>
    </div>
  `).join('')
}

function checkContentOverflow() {
  if (!measureBodyRef.value) return false
  
  measureBodyRef.value.innerHTML = formatBodyContent()
  const contentHeight = measureBodyRef.value.scrollHeight
  
  return contentHeight > availableFirstPx.value
}

function splitContentIntoPages() {
  const sections = [
    { title: 'MUESTRA:', content: buildSamplesDescription(props.caseData.caseDetails?.muestras) },
    { title: 'MÉTODO UTILIZADO', content: getMethodText(props.caseData.sections) || '—' },
    { title: 'DESCRIPCIÓN MACROSCÓPICA', content: props.caseData.sections?.macro || '—' },
    { title: 'DESCRIPCIÓN MICROSCÓPICA', content: props.caseData.sections?.micro || '—' },
    { title: 'DIAGNÓSTICO', content: getDiagnosisText(props.caseData.sections, props.caseData.diagnosis) || '—' },
    { title: 'CIE-10', content: `${(props.caseData.diagnosis?.cie10?.primary?.codigo || props.caseData.diagnosis?.cie10?.codigo) ?? '—'}${(props.caseData.diagnosis?.cie10?.primary?.nombre || props.caseData.diagnosis?.cie10?.nombre) ? ` - ${props.caseData.diagnosis?.cie10?.primary?.nombre || props.caseData.diagnosis?.cie10?.nombre}` : ''}` },
    { title: 'CIE-O', content: `${props.caseData.diagnosis?.cieo?.codigo ?? '—'}${props.caseData.diagnosis?.cieo?.nombre ? ` - ${props.caseData.diagnosis.cieo.nombre}` : ''}` }
  ]

  const resultPages: any[] = []
  let currentPageContent = ''
  let isFirstPage = true

  for (const section of sections) {
    const sectionHtml = `
      <div class="section-item" style="margin-bottom: 12px;">
        <h3 style="font-weight: 600; margin-bottom: 4px; font-size: 12px; color: #374151;">${section.title}</h3>
        <div style="white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; color: #111827;">${section.content}</div>
      </div>
    `
    
    if (measureBodyRef.value) {
      measureBodyRef.value.innerHTML = currentPageContent + sectionHtml
      const newHeight = measureBodyRef.value.scrollHeight
      
      const availableHeight = isFirstPage ? availableFirstPx.value : availableContPx.value
      
      if (newHeight > availableHeight && currentPageContent) {
        resultPages.push({
          content: currentPageContent,
          isFirstPage,
          isLastPage: false
        })
        currentPageContent = sectionHtml
        isFirstPage = false
      } else {
        currentPageContent += sectionHtml
      }
    }
  }

  if (currentPageContent) {
    resultPages.push({
      content: currentPageContent,
      isFirstPage,
      isLastPage: true
    })
  }

  return resultPages
}

function recalculatePagination() {
  calculatePageMetrics()
  needsPagination.value = checkContentOverflow()
  
  if (needsPagination.value) {
    pages.value = splitContentIntoPages()
  }
}

onMounted(() => {
  nextTick(() => {
    recalculatePagination()
  })
})

watch(() => props.caseData, () => {
  nextTick(() => {
    recalculatePagination()
  })
}, { deep: true })
</script>

<style scoped>
.case-report-container {
  font-family: Arial, sans-serif;
}

.report-page {
  width: 7.5in;
  min-height: 11in;
  max-height: 11in;
  margin: 0 auto;
  padding: 0.5in;
  box-sizing: border-box;
  background-color: white;
  position: relative;
  page-break-after: always;
}

.report-page:last-child {
  page-break-after: avoid;
}

.page-header {
  position: relative;
  z-index: 10;
  background: white;
}

.page-body {
  position: relative;
  z-index: 5;
}

.page-footer {
  position: relative;
  z-index: 10;
  background: white;
}

.dynamic-content {
  font-size: 12px;
  line-height: 1.4;
}

.inline-label {
  display: inline-block;
  margin-right: 2px; /* asegura espacio tras los dos puntos */
}

.label-value {
  display: inline;
  padding-left: 1px; /* micro separación visual */
}

.print-hidden {
  display: none;
}

@media print {
  .print-hidden {
    display: none !important;
  }
  
  .report-page {
    margin: 0;
    box-shadow: none;
    border: none;
  }
  
  .signature-section img {
    background: transparent !important;
    mix-blend-mode: multiply !important;
    -webkit-print-color-adjust: exact !important;
    print-color-adjust: exact !important;
  }
}

.signature-section img {
  background: transparent !important;
  mix-blend-mode: multiply;
}
</style>
