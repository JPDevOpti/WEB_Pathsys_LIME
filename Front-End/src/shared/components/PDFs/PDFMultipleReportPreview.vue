<template>
  <div class="pdf-multiple-preview">
    <!-- Loading State -->
    <div v-if="isLoading" class="text-center py-8">
      <div class="inline-flex items-center gap-3">
        <svg class="w-6 h-6 animate-spin text-blue-600" fill="none" viewBox="0 0 24 24">
          <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
          <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
        </svg>
        <span class="text-gray-700">Preparando vista previa de {{ cases.length }} caso{{ cases.length > 1 ? 's' : '' }}...</span>
      </div>
    </div>

    <!-- Error State -->
    <div v-if="error" class="p-4 bg-red-50 border border-red-200 rounded text-sm text-red-800">
      Error al cargar la vista previa: {{ error }}
    </div>

    <!-- Empty State -->
    <div v-if="!hasData && !isLoading && !error" class="p-4 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800">
      No hay casos para previsualizar.
    </div>

    <!-- Elementos de medición ocultos (siempre montados cuando hay datos) -->
    <div v-if="hasData" class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
      <div ref="measureBodyRef" style="width:7.5in; font-size:12px; line-height:1.4; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>
      <div ref="measureHeaderRef" style="width:7.5in; box-sizing:border-box;">
        <div v-if="measureItem || firstCaseItem">
          <PDFReportHeader :case-item="(measureItem || firstCaseItem) as any" />
          <PDFReportPatientData 
            :case-item="(measureItem || firstCaseItem) as any" 
            :recibido-numero="recibidoNumero((measureItem || firstCaseItem)?.caseDetails?.CasoCode || (measureItem || firstCaseItem)?.sampleId)" 
          />
        </div>
      </div>
      <div ref="measureFooterRef" style="width:7.5in; box-sizing:border-box;">
        <PDFReportFooter :current-page="1" :total-pages="1" />
      </div>
      <div ref="measureSignatureRef" style="width:7.5in; box-sizing:border-box;">
        <PDFReportSignature v-if="measureItem || firstCaseItem" :case-item="(measureItem || firstCaseItem) as any" />
      </div>
    </div>

    <!-- PDF Preview Content -->
    <div v-if="hasData" class="pdf-multiple-container">
      <!-- Contenido principal con todos los casos -->
      <div class="print-content multiple-cases">
        <template v-for="(caseBundle, caseIndex) in processedCases" :key="`case-bundle-${caseIndex}`">
          <!-- Separador entre casos (excepto el primero) -->
          <div v-if="caseIndex > 0" class="case-separator print-break-before"></div>
          
          <!-- Páginas del caso actual -->
          <template v-for="(page, pageIndex) in caseBundle.pages" :key="`case-${caseIndex}-page-${pageIndex}`">
            <div
              class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
              :class="{ 'print-break-before': pageIndex > 0 }"
              :style="pageStyle"
            >
              <!-- Header solo en primera página del caso -->
              <div 
                v-if="page.isFirstPage"
                class="page-header" 
                :style="{ 
                  height: `${caseBundle.headerPx}px`, 
                  maxHeight: `${caseBundle.headerPx}px`, 
                  overflow: 'hidden', 
                  background: 'white', 
                  position: 'relative', 
                  zIndex: 10 
                }"
              >
                <PDFReportHeader :case-item="caseBundle.caseItem" />
                <PDFReportPatientData 
                  :case-item="caseBundle.caseItem" 
                  :recibido-numero="recibidoNumero(caseBundle.caseItem.caseDetails?.CasoCode || caseBundle.caseItem.sampleId)" 
                />
              </div>

              <!-- Body content -->
              <div 
                class="page-body" 
                :style="{ 
                  height: `${page.isFirstPage 
                    ? (page.isLastPage ? caseBundle.availableSinglePx : caseBundle.availableFirstPx) 
                    : (page.isLastPage ? (caseBundle.availableContPx - caseBundle.signaturePx) : caseBundle.availableContPx)}px`, 
                  maxHeight: `${page.isFirstPage 
                    ? (page.isLastPage ? caseBundle.availableSinglePx : caseBundle.availableFirstPx) 
                    : (page.isLastPage ? (caseBundle.availableContPx - caseBundle.signaturePx) : caseBundle.availableContPx)}px`, 
                  overflow: 'visible', 
                  position: 'relative', 
                  zIndex: 5 
                }"
              >
                <div v-html="page.content" class="dynamic-content"></div>
              </div>

              <!-- Signature (solo en última página de cada caso) -->
              <div 
                v-if="page.isLastPage"
                class="page-signature" 
                :style="{ 
                  height: `${caseBundle.signaturePx}px`, 
                  maxHeight: `${caseBundle.signaturePx}px`, 
                  overflow: 'hidden', 
                  background: 'white', 
                  position: 'relative', 
                  zIndex: 10 
                }"
              >
                <PDFReportSignature :case-item="caseBundle.caseItem" />
              </div>

              <!-- Footer -->
              <div 
                class="page-footer" 
                :style="{ 
                  height: `${caseBundle.footerPx}px`, 
                  maxHeight: `${caseBundle.footerPx}px`, 
                  overflow: 'hidden', 
                  background: 'white', 
                  position: 'relative', 
                  zIndex: 10 
                }"
              >
                <PDFReportFooter 
                  :current-page="pageIndex + 1" 
                  :total-pages="caseBundle.pages.length" 
                />
              </div>
            </div>
          </template>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick, onMounted } from 'vue'
import type { Case } from '@/modules/case-list/types/case.types'
import PDFReportHeader from './parts/PDFReportHeader.vue'
import PDFReportPatientData from './parts/PDFReportPatientData.vue'
import PDFReportFooter from './parts/PDFReportFooter.vue'
import PDFReportSignature from './parts/PDFReportSignature.vue'

// Interface para compatibilidad con componentes PDF existentes
interface CaseItem {
  caseDetails?: {
    caso_code?: string
    CasoCode?: string
    fecha_ingreso?: string
    fecha_creacion?: string
    fecha_firma?: string
    muestras?: any[]
    metodos?: any[]
    resultados?: any[]
    diagnostico?: any
    paciente?: {
      cedula?: string
      nombre?: string
      edad?: number
      sexo?: string
    }
    entidad_info?: {
      nombre?: string
    }
    servicio?: string
    medico_solicitante?: {
      nombre?: string
    }
    patologo_asignado?: {
      nombre?: string
    }
  }
  sections?: {
    method?: string | string[]
    methodText?: string
    macro?: string
    micro?: string
    diagnosis?: string
  }
  diagnosis?: {
    formatted?: string
    cie10?: {
      codigo?: string
      nombre?: string
      primary?: any
    }
    cieo?: {
      codigo?: string
      nombre?: string
    }
  }
  sampleId?: string
  patient?: {
    document?: string
    fullName?: string
    entity?: string
  }
  generatedAt?: string
}

// Props
const props = defineProps<{
  cases: Case[]
  showOnMount?: boolean
}>()

// State
const isLoading = ref(false)
const error = ref<string | null>(null)
const processedCases = ref<CaseBundle[]>([])

// Refs para medición
const measureBodyRef = ref<HTMLElement>()
const measureHeaderRef = ref<HTMLElement>()
const measureFooterRef = ref<HTMLElement>()
const measureSignatureRef = ref<HTMLElement>()

// Interfaces
interface PageInfo { content: string; isFirstPage: boolean; isLastPage: boolean }
interface CaseBundle { item: Case; caseItem: CaseItem; pages: PageInfo[]; headerPx: number; footerPx: number; signaturePx: number; availableFirstPx: number; availableContPx: number; availableSinglePx: number }

// Computed
const hasData = computed(() => props.cases && props.cases.length > 0)
const firstCase = computed(() => props.cases?.[0] || null)
const firstCaseItem = computed(() => firstCase.value ? convertCaseToCaseItem(firstCase.value) : null)

const pageStyle = computed(() => ({
  width: '8.5in',
  height: '11in', 
  padding: '0.5in 0.5in 0.5in 0.5in',
  boxSizing: 'border-box' as const,
  color: '#111827',
  overflow: 'hidden' as const,
  fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial'
}))

// Methods
function convertCaseToCaseItem(caseData: Case): CaseItem {
  return {
    caseDetails: {
      caso_code: caseData.caseCode,
      CasoCode: caseData.caseCode,
      fecha_creacion: caseData.receivedAt,
      fecha_firma: caseData.signedAt,
      muestras: caseData.result ? [{
        region_cuerpo: caseData.sampleType || 'No especificado',
        pruebas: [{
          id: caseData.result.method || 'No especificado',
          nombre: caseData.result.method || 'No especificado'
        }]
      }] : [{
        region_cuerpo: caseData.sampleType || 'No especificado',
        pruebas: [{
          id: 'Pendiente',
          nombre: 'Método pendiente'
        }]
      }],
      paciente: {
        cedula: caseData.patient.dni,
        nombre: caseData.patient.fullName,
        edad: caseData.patient.age,
        sexo: caseData.patient.sex
      },
      entidad_info: {
        nombre: caseData.entity
      },
      servicio: caseData.servicio,
      medico_solicitante: {
        nombre: caseData.requester
      },
      patologo_asignado: {
        nombre: caseData.pathologist || 'No asignado'
      }
    },
    sections: {
      method: caseData.result?.method || '',
      methodText: caseData.result?.method || '',
      macro: caseData.result?.macro || '',
      micro: caseData.result?.micro || '',
      diagnosis: caseData.result?.diagnosis || ''
    },
    diagnosis: {
      formatted: caseData.result?.diagnosis || '',
      cie10: {
        codigo: caseData.result?.diagnostico_cie10?.codigo || '',
        nombre: caseData.result?.diagnostico_cie10?.nombre || ''
      },
      cieo: {
        codigo: caseData.result?.diagnostico_cieo?.codigo || '',
        nombre: caseData.result?.diagnostico_cieo?.nombre || ''
      }
    },
    sampleId: caseData.id,
    patient: {
      document: caseData.patient.dni,
      fullName: caseData.patient.fullName,
      entity: caseData.patient.entity
    },
    generatedAt: new Date().toISOString()
  }
}
// Utility functions (copied from PDFReportPreview.vue)
function buildSamplesText(samples: any[] | undefined): string {
  if (!samples || samples.length === 0) return '—'
  return samples.map(s => `${s.region_cuerpo}: ${s.pruebas?.map((p: any) => 
    p.id === p.nombre ? p.id : `${p.id} - ${p.nombre}`
  ).join(', ')}`).join(' | ')
}

function getMethodText(sections: any): string {
  if (!sections) return '—'
  const mt = sections.methodText
  if (typeof mt === 'string' && mt.trim()) return mt
  const m = sections.method
  if (Array.isArray(m)) return m.filter((x: any) => typeof x === 'string' && x.trim()).join(', ')
  if (typeof m === 'string') return m
  return '—'
}

function getDiagnosisText(sections: any, diagnosis: any): string {
  const formatted = diagnosis?.formatted?.toString().trim()
  if (formatted) return formatted
  const free = sections?.diagnosis?.toString().trim()
  return free || '—'
}

function recibidoNumero(caseCode: string | undefined): string {
  if (!caseCode) return '—'
  const parts = String(caseCode).split('-')
  if (parts.length < 2) return caseCode
  return parts.slice(1).join('-')
}

// --- Nueva lógica precisa de paginado multi (no solapamientos) ---
const measureItem = ref<any>(null)

interface MetricBundle {
  innerHeight: number
  headerPx: number
  footerPx: number
  signaturePx: number
  singleBody: number
  firstMultiBody: number
  contBody: number
  lastBody: number
}

function calculateAccurateMetrics(): MetricBundle {
  const DPI = 96
  const pageHeight = 11 * DPI
  const padding = 0.5 * DPI
  const innerHeight = pageHeight - (padding * 2)
  const headerPx = measureHeaderRef.value?.scrollHeight || Math.round(2.5 * DPI * 0.8)
  const footerPx = measureFooterRef.value?.scrollHeight || Math.round(1.0 * DPI * 0.6)
  const signaturePx = 160
  const singleBody = Math.max(0, innerHeight - headerPx - footerPx - signaturePx)
  const firstMultiBody = Math.max(0, innerHeight - headerPx - footerPx)
  const contBody = Math.max(0, innerHeight - footerPx)
  const lastBody = Math.max(0, innerHeight - footerPx - signaturePx)
  return { innerHeight, headerPx, footerPx, signaturePx, singleBody, firstMultiBody, contBody, lastBody }
}

function formatBodyContentForItem(item: any): string {
  const sections = [
    { title: 'MUESTRA:', content: buildSamplesText(item.caseDetails?.muestras) },
    { title: 'MÉTODO UTILIZADO', content: getMethodText(item.sections) || '—' },
    { title: 'DESCRIPCIÓN MACROSCÓPICA', content: item.sections?.macro || '—' },
    { title: 'DESCRIPCIÓN MICROSCÓPICA', content: item.sections?.micro || '—' },
    { title: 'DIAGNÓSTICO', content: getDiagnosisText(item.sections, item.diagnosis) || '—' },
    { title: 'CIE-10', content: `${(item.diagnosis?.cie10?.primary?.codigo || item.diagnosis?.cie10?.codigo) ?? '—'}${(item.diagnosis?.cie10?.primary?.nombre || item.diagnosis?.cie10?.nombre) ? ` - ${item.diagnosis?.cie10?.primary?.nombre || item.diagnosis?.cie10?.nombre}` : ''}` },
    { title: 'CIE-O', content: `${item.diagnosis?.cieo?.codigo ?? '—'}${item.diagnosis?.cieo?.nombre ? ` - ${item.diagnosis.cieo.nombre}` : ''}` }
  ]
  return sections.map(s => `
    <div class="section-item">
      <h3>${s.title}</h3>
      <div>${s.content}</div>
    </div>
  `).join('')
}

async function computePagesForItem(item: any) {
  measureItem.value = item
  await nextTick()
  const metrics = calculateAccurateMetrics()
  const content = formatBodyContentForItem(item)
  if (!measureBodyRef.value) return { item, caseItem: item, pages: [], headerPx: metrics.headerPx, footerPx: metrics.footerPx, signaturePx: metrics.signaturePx, availableFirstPx: metrics.firstMultiBody, availableContPx: metrics.contBody, availableSinglePx: metrics.singleBody } as CaseBundle
  measureBodyRef.value.innerHTML = content
  const totalHeight = measureBodyRef.value.scrollHeight
  const pages: Array<{content:any,isFirstPage:boolean,isLastPage:boolean}> = []
  const safety = 20
  // SINGLE PAGE
  if (totalHeight <= (metrics.singleBody - safety)) {
    pages.push({ content, isFirstPage: true, isLastPage: true })
    return { item, caseItem: item, pages, headerPx: metrics.headerPx, footerPx: metrics.footerPx, signaturePx: metrics.signaturePx, availableFirstPx: metrics.firstMultiBody, availableContPx: metrics.contBody, availableSinglePx: metrics.singleBody } as CaseBundle
  }
  // MULTI: dividir por secciones como en el componente de uno solo
  const sections = content.split('<div class="section-item"').filter(s => s.trim()).map(s => `<div class="section-item"${s}`)
  let idx = 0
  // Primera página: capacidad sin firma
  let firstPageContent = ''
  while (idx < sections.length) {
    const candidate = firstPageContent + sections[idx]
    measureBodyRef.value.innerHTML = candidate
    if (measureBodyRef.value.scrollHeight <= (metrics.firstMultiBody - safety)) { firstPageContent = candidate; idx++ } else break
  }
  pages.push({ content: firstPageContent, isFirstPage: true, isLastPage: false })
  // Continuaciones
  while (idx < sections.length) {
    // decidir si esta página será la última según el alto de lo restante
    const remainingJoin = sections.slice(idx).join('')
    measureBodyRef.value.innerHTML = remainingJoin
    const remainingTotal = measureBodyRef.value.scrollHeight
    const isLastPageNow = remainingTotal <= (metrics.lastBody - safety)
    const capacity = (isLastPageNow ? (metrics.lastBody - safety) : (metrics.contBody - safety))
    let pageContent = ''
    let started = idx
    while (idx < sections.length) {
      const candidate = pageContent + sections[idx]
      measureBodyRef.value.innerHTML = candidate
      if (measureBodyRef.value.scrollHeight <= capacity) { pageContent = candidate; idx++ } else break
    }
    // seccion gigante, fragmentar
    if (!pageContent && idx < sections.length) {
      const part = sections[idx]
      const temp = document.createElement('div')
      temp.innerHTML = part
      const inner = temp.querySelector('.section-item') as HTMLElement
      const blocks = Array.from(inner?.childNodes || [])
      for (const block of blocks) {
        const html = (block as HTMLElement).outerHTML || (block as HTMLElement).textContent || ''
        const candidate = pageContent + html
        measureBodyRef.value.innerHTML = candidate
        if (measureBodyRef.value.scrollHeight <= capacity) pageContent = candidate
        else break
      }
      if (!pageContent) pageContent = part
      else idx++
    }
    pages.push({ content: pageContent, isFirstPage: false, isLastPage: isLastPageNow && (idx >= sections.length) })
  }
  if (pages.length) pages[pages.length - 1].isLastPage = true
  return { item, caseItem: item, pages, headerPx: metrics.headerPx, footerPx: metrics.footerPx, signaturePx: metrics.signaturePx, availableFirstPx: metrics.firstMultiBody, availableContPx: metrics.contBody, availableSinglePx: metrics.singleBody } as CaseBundle
}

async function processAllCases() {
  if (!hasData.value) return
  isLoading.value = true
  error.value = null
  try {
    await nextTick()
    const bundles: CaseBundle[] = []
    for (const c of props.cases) {
      const converted = convertCaseToCaseItem(c)
      const bundle = await computePagesForItem(converted)
      bundles.push({ ...bundle, item: c, caseItem: converted })
    }
    processedCases.value = bundles
  } catch (e) {
    error.value = e instanceof Error ? e.message : 'Error desconocido'
  } finally { isLoading.value = false }
}

// Watchers
watch(() => props.cases, () => {
  if (hasData.value) {
    processAllCases()
  }
}, { immediate: true })

// Lifecycle
onMounted(() => {
  if (props.showOnMount && hasData.value) {
    processAllCases()
  }
})
</script>

<style scoped>
/* Estilos específicos para vista previa múltiple */
.pdf-multiple-preview {
  width: 100%;
  height: 100%;
}

.pdf-multiple-container {
  width: 100%;
}

.multiple-cases {
  display: flex;
  flex-direction: column;
  gap: 1.5rem;
}

.case-separator {
  height: 1px;
  background-color: #d1d5db;
  margin: 2rem 0;
  page-break-before: always;
}

.report-page {
  margin-bottom: 1.5rem;
  box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1);
  display: flex;
  flex-direction: column;
  padding: 0.5in 0.5in 0.4in 0.5in;
  box-sizing: border-box;
}

.page-header,
.page-footer,
.page-signature {
  flex-shrink: 0;
}

.page-body {
  flex-shrink: 0;
  overflow: hidden;
  position: relative;
}

.dynamic-content {
  width: 100%;
  height: 100%;
  overflow: hidden;
  font-size: 12px;
  line-height: 1.4;
  box-sizing: border-box;
}

.dynamic-content .section-item {
  margin: 0 0 10px 0;
  padding: 0;
}

.dynamic-content .section-item h3 {
  font-weight: 600;
  margin-bottom: 4px;
  font-size: 12px;
  color: #374151;
}

.dynamic-content .section-item div {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
  color: #111827;
}

/* Estilos de impresión */
@media print {
  .print-hidden {
    display: none !important;
  }
  
  .report-page {
    box-shadow: none !important;
    border: none !important;
    margin: 0 !important;
    break-inside: avoid;
  padding: 0.5in 0.5in 0.4in 0.5in !important;
  }
  
  .print-break-before {
    page-break-before: always;
  }
  
  .case-separator {
    page-break-before: always;
    visibility: hidden;
    height: 0;
    margin: 0;
  }
}
</style>
