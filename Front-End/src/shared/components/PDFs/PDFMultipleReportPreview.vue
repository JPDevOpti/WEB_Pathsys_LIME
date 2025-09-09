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

    <!-- PDF Preview Content -->
    <div v-if="hasData && !isLoading" class="pdf-multiple-container">
      <!-- Elementos de medición ocultos -->
      <div class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
        <div ref="measureBodyRef" style="width:7.5in; font-size:12px; line-height:1.4; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>
        <div ref="measureHeaderRef" style="width:7.5in; box-sizing:border-box;">
          <div v-if="firstCaseItem">
            <PDFReportHeader :case-item="firstCaseItem" />
            <PDFReportPatientData :case-item="firstCaseItem" :recibido-numero="recibidoNumero(firstCaseItem?.caseDetails?.CasoCode || firstCaseItem?.sampleId)" />
          </div>
        </div>
        <div ref="measureFooterRef" style="width:7.5in; box-sizing:border-box;">
          <PDFReportFooter :current-page="1" :total-pages="1" />
        </div>
        <div ref="measureSignatureRef" style="width:7.5in; box-sizing:border-box;">
          <PDFReportSignature v-if="firstCaseItem" :case-item="firstCaseItem" />
        </div>
      </div>

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
              <!-- Header (en todas las páginas para modo múltiple) -->
              <div 
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
                  height: `${page.isFirstPage ? caseBundle.availableFirstPx : caseBundle.availableContPx}px`, 
                  maxHeight: `${page.isFirstPage ? caseBundle.availableFirstPx : caseBundle.availableContPx}px`, 
                  overflow: 'hidden', 
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
  firma?: string
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
interface PageInfo {
  content: string
  isFirstPage: boolean
  isLastPage: boolean
}

interface CaseBundle {
  item: Case
  caseItem: CaseItem  // Para compatibilidad con componentes PDF
  pages: PageInfo[]
  headerPx: number
  footerPx: number
  signaturePx: number
  availableFirstPx: number
  availableContPx: number
}

// Computed
const hasData = computed(() => props.cases && props.cases.length > 0)
const firstCase = computed(() => props.cases?.[0] || null)
const firstCaseItem = computed(() => firstCase.value ? convertCaseToCaseItem(firstCase.value) : null)

const pageStyle = computed(() => ({
  width: '8.5in',
  height: '11in', 
  padding: '0.5in 0.5in 0.4in 0.5in',
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
        nombre: caseData.patologo_asignado?.nombre || caseData.pathologist || 'No asignado',
        firma: caseData.patologo_asignado?.firma || undefined
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

async function processAllCases() {
  if (!hasData.value) return

  isLoading.value = true
  error.value = null
  
  try {
    await nextTick()
    
    // Procesar cada caso individualmente
    const bundles: CaseBundle[] = []
    
    for (const caseItem of props.cases) {
      const bundle = await processSingleCase(caseItem)
      if (bundle) {
        bundles.push(bundle)
      }
    }
    
    processedCases.value = bundles
  } catch (err) {
    console.error('Error processing cases:', err)
    error.value = err instanceof Error ? err.message : 'Error desconocido'
  } finally {
    isLoading.value = false
  }
}

async function processSingleCase(caseItem: Case): Promise<CaseBundle | null> {
  try {
    await nextTick()
    
    // Convertir Case a CaseItem para compatibilidad
    const caseItemConverted = convertCaseToCaseItem(caseItem)
    
    // Obtener dimensiones de elementos fijos
    const dimensions = await getMeasurements()
    
    // Generar contenido del caso usando el CaseItem convertido
    const content = generateCaseContent(caseItemConverted)
    
    // Paginar el contenido
    const pages = await paginateContent(content, dimensions)
    
    return {
      item: caseItem,
      caseItem: caseItemConverted,
      pages,
      headerPx: dimensions.headerPx,
      footerPx: dimensions.footerPx,
      signaturePx: dimensions.signaturePx,
      availableFirstPx: dimensions.availableFirstPx,
      availableContPx: dimensions.availableContPx
    }
  } catch (err) {
    console.error(`Error processing case ${caseItem.id}:`, err)
    return null
  }
}

async function getMeasurements() {
  await nextTick()
  
  // TAMAÑO CARTA EXACTO: 8.5" x 11" (como en el componente original)
  const pageHeight = 11 * 96 // 11 pulgadas = 1056px
  const padding = 0.5 * 96 // 0.5 pulgadas = 48px arriba y abajo
  
  // Altura disponible para contenido = 11" - 1" padding = 10" = 960px
  const availableHeight = pageHeight - (padding * 2)
  
  // Medir componentes fijos
  const headerEl = measureHeaderRef.value
  const footerEl = measureFooterRef.value
  
  const headerPx = headerEl?.scrollHeight || Math.round(2.5 * 96 * 0.8)
  const footerPx = footerEl?.scrollHeight || Math.round(1.0 * 96 * 0.6)
  const signaturePx = 160 // Altura fija de 160px para la firma (siempre igual)
  
  // Espacio disponible para BODY en primera página
  // Para modo múltiple: 960px - header - footer - signature
  const availableFirstPx = Math.max(200, availableHeight - headerPx - footerPx - signaturePx)
  
  // Espacio disponible para BODY en páginas de continuación  
  // Para modo múltiple: 960px - header - footer (todas tienen header)
  const availableContPx = Math.max(400, availableHeight - headerPx - footerPx)
  
  return {
    headerPx,
    footerPx,
    signaturePx,
    availableFirstPx,
    availableContPx
  }
}

function generateCaseContent(caseItem: CaseItem): string {
  const sections = [
    { title: 'MUESTRA', content: buildSamplesText(caseItem.caseDetails?.muestras) },
    { title: 'MÉTODO UTILIZADO', content: getMethodText(caseItem.sections) || '—' },
    { title: 'DESCRIPCIÓN MACROSCÓPICA', content: caseItem.sections?.macro || '—' },
    { title: 'DESCRIPCIÓN MICROSCÓPICA', content: caseItem.sections?.micro || '—' },
    { title: 'DIAGNÓSTICO', content: getDiagnosisText(caseItem.sections, caseItem.diagnosis) || '—' },
    { title: 'CIE-10', content: `${(caseItem.diagnosis?.cie10?.primary?.codigo || caseItem.diagnosis?.cie10?.codigo) ?? '—'}${(caseItem.diagnosis?.cie10?.primary?.nombre || caseItem.diagnosis?.cie10?.nombre) ? ` - ${caseItem.diagnosis?.cie10?.primary?.nombre || caseItem.diagnosis?.cie10?.nombre}` : ''}` },
    { title: 'CIE-O', content: `${caseItem.diagnosis?.cieo?.codigo ?? '—'}${caseItem.diagnosis?.cieo?.nombre ? ` - ${caseItem.diagnosis.cieo.nombre}` : ''}` }
  ]
  return sections.map(s => `
    <div class="section-item" style="margin-bottom: 12px;">
      <h3 style="font-weight: 600; margin-bottom: 4px; font-size: 12px; color: #374151;">${s.title}</h3>
      <div style="white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; color: #111827;">${s.content}</div>
    </div>
  `).join('')
}

async function paginateContent(content: string, dimensions: any): Promise<PageInfo[]> {
  if (!measureBodyRef.value) {
    return [{
      content,
      isFirstPage: true,
      isLastPage: true
    }]
  }
  
  // Medir el contenido
  measureBodyRef.value.innerHTML = content
  const totalHeight = measureBodyRef.value.scrollHeight
  
  const maxFirstPageHeight = dimensions.availableFirstPx - 20 // Margen de seguridad
  const maxContinuationHeight = dimensions.availableContPx - 20
  
  if (totalHeight <= maxFirstPageHeight) {
    // Todo cabe en una página
    return [{
      content,
      isFirstPage: true,
      isLastPage: true
    }]
  }
  
  // Dividir el contenido por section-items (como en el componente original)
  const sections = content.split('<div class="section-item"').filter(s => s.trim()).map(s => `<div class="section-item"${s}`)
  let firstContent = ''
  
  // Simular cada sección para medir su altura en la primera página
  for (const sec of sections) {
    measureBodyRef.value.innerHTML = firstContent + sec
    const h = measureBodyRef.value.scrollHeight
    if (h <= maxFirstPageHeight) { 
      firstContent += sec
    } else { 
      break 
    }
  }
  
  const result: PageInfo[] = []
  
  // Primera página
  result.push({ 
    content: firstContent, 
    isFirstPage: true, 
    isLastPage: false 
  })
  
  // Contenido restante
  const remaining = sections.join('')?.replace(firstContent, '') || ''
  if (remaining.trim()) {
    const parts = remaining.split('<div class="section-item"').filter(s => s.trim()).map(s => `<div class="section-item"${s}`)
    let current = ''
    
    for (const part of parts) {
      measureBodyRef.value.innerHTML = current + part
      const h = measureBodyRef.value.scrollHeight
      if (h <= maxContinuationHeight) { 
        current += part
      } else {
        if (current) {
          result.push({ 
            content: current, 
            isFirstPage: false, 
            isLastPage: false 
          })
        }
        current = part
      }
    }
    
    if (current) {
      result.push({ 
        content: current, 
        isFirstPage: false, 
        isLastPage: true 
      })
    }
  }
  
  // Marcar la última página como isLastPage
  if (result.length > 0) {
    result[result.length - 1].isLastPage = true
  }
  
  return result.length > 0 ? result : [{
    content,
    isFirstPage: true,
    isLastPage: true
  }]
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
}

.page-header,
.page-footer,
.page-signature {
  flex-shrink: 0;
}

.page-body {
  flex-grow: 1;
  overflow: hidden;
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
  margin-bottom: 12px;
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
