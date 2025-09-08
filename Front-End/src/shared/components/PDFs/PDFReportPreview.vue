<template>
  <div>
    <div v-if="!hasData" class="p-4 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800 print-hidden">
      No hay datos para previsualizar.
    </div>

    <div class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
      <div ref="measureBodyRef" style="width:7.5in; font-size:12px; line-height:1.4; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>

      <div ref="measureHeaderRef" style="width:7.5in; box-sizing:border-box;">
        <div>
          <PDFReportHeader :case-item="singleCaseObject" />
          <PDFReportPatientData :case-item="singleCaseObject" :recibido-numero="recibidoNumero(singleCaseObject.caseDetails?.CasoCode || singleCaseObject.sampleId)" />
        </div>
      </div>

      <div ref="measureFooterRef" style="width:7.5in; box-sizing:border-box;">
        <PDFReportFooter :current-page="1" :total-pages="1" />
      </div>

      <div ref="measureSignatureRef" style="width:7.5in; box-sizing:border-box;">
        <PDFReportSignature :case-item="singleCaseObject" />
      </div>
    </div>

    <div v-if="hasData" class="pdf-preview-container" :class="{ 'multi': isMultiple }">
      <div v-if="isMultiple" class="print-content multi">
        <template v-for="(bundle, i) in casesPages" :key="`bundle-${i}`">
          <div v-if="i>0" class="case-separator"></div>
          <div
            v-for="(page, pageIndex) in bundle.pages"
            :key="`case-${i}-page-${pageIndex}`"
            class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
            :style="pageStyle"
          >
            <div class="page-header" :style="{ height: `${bundle.headerPx}px`, maxHeight: `${bundle.headerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
              <PDFReportHeader :case-item="bundle.item" />
              <PDFReportPatientData :case-item="bundle.item" :recibido-numero="recibidoNumero(bundle.item.caseDetails?.CasoCode || bundle.item.sampleId)" />
            </div>

            <div class="page-body" :style="{ height: `${page.isFirstPage ? bundle.availableFirstPx : bundle.availableContPx}px`, maxHeight: `${page.isFirstPage ? bundle.availableFirstPx : bundle.availableContPx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
              <div v-html="page.content" class="dynamic-content"></div>
            </div>

            <div v-if="page.isLastPage" class="page-signature" :style="{ height: `${bundle.signaturePx}px`, maxHeight: `${bundle.signaturePx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
              <PDFReportSignature :case-item="bundle.item" />
            </div>

            <div class="page-footer" :style="{ height: `${bundle.footerPx}px`, maxHeight: `${bundle.footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
              <PDFReportFooter :current-page="pageIndex + 1" :total-pages="bundle.pages.length" />
            </div>
          </div>
        </template>
      </div>

      <div v-else class="print-content">
        <!-- Renderizar páginas calculadas automáticamente -->
        <div
          v-if="!needsPagination"
          class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
          :style="pageStyle"
        >
          <div class="page-header" :style="{ height: `${headerPx}px`, maxHeight: `${headerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
            <PDFReportHeader :case-item="singleCaseObject" />
            <PDFReportPatientData :case-item="singleCaseObject" :recibido-numero="recibidoNumero(singleCaseObject.caseDetails?.CasoCode || singleCaseObject.sampleId)" />
          </div>

          <div class="page-body" :style="{ height: `${availableFirstPx}px`, maxHeight: `${availableFirstPx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
            <PDFReportPatientBlock :case-item="singleCaseObject" />
          </div>

          <div class="page-signature" :style="{ height: `${signaturePx}px`, maxHeight: `${signaturePx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
            <PDFReportSignature :case-item="singleCaseObject" />
          </div>

          <div class="page-footer" :style="{ height: `${footerPx}px`, maxHeight: `${footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
            <PDFReportFooter :current-page="1" :total-pages="1" />
          </div>
        </div>

        <!-- Páginas múltiples cuando hay overflow -->
        <template v-else>
          <div
            v-for="(page, pageIndex) in pages"
            :key="`page-${pageIndex}`"
            class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
            :style="pageStyle"
          >
            <!-- Primera página: Header + Datos + Contenido parcial (sin firma si hay múltiples páginas) -->
            <template v-if="page.isFirstPage">
              <div class="page-header" :style="{ height: `${headerPx}px`, maxHeight: `${headerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
                <PDFReportHeader :case-item="singleCaseObject" />
                <PDFReportPatientData :case-item="singleCaseObject" :recibido-numero="recibidoNumero(singleCaseObject.caseDetails?.CasoCode || singleCaseObject.sampleId)" />
              </div>

              <!-- Si es la ÚNICA página, incluir signature -->
              <template v-if="pages.length === 1">
                <div class="page-body constrained-height" :style="{ height: `${availableFirstPx}px`, maxHeight: `${availableFirstPx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
                  <div v-html="page.content" class="dynamic-content"></div>
                </div>

                <div class="page-signature" :style="{ height: `${signaturePx}px`, maxHeight: `${signaturePx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
                  <PDFReportSignature :case-item="singleCaseObject" />
                </div>
              </template>

              <!-- Si hay múltiples páginas, NO incluir signature en la primera -->
              <template v-else>
                <div class="page-body constrained-height" :style="{ height: `${availableFirstPx + signaturePx}px`, maxHeight: `${availableFirstPx + signaturePx}px`, overflow: 'hidden', position: 'relative', zIndex: 5 }">
                  <div v-html="page.content" class="dynamic-content"></div>
                </div>
              </template>

              <div class="page-footer" :style="{ height: `${footerPx}px`, maxHeight: `${footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
                <PDFReportFooter :current-page="pageIndex + 1" :total-pages="pages.length" />
              </div>
            </template>

            <!-- Páginas de continuación: Solo contenido + Footer -->
            <template v-else>
              <!-- Si es la ÚLTIMA página, incluir signature -->
              <template v-if="pageIndex === pages.length - 1">
                <div class="page-body continuation-page" :style="{ height: `${availableContPx - signaturePx}px`, maxHeight: `${availableContPx - signaturePx}px`, overflow: 'hidden' }">
                  <div v-html="page.content" class="dynamic-content"></div>
                </div>

                <div class="page-signature" :style="{ height: `${signaturePx}px`, maxHeight: `${signaturePx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
                  <PDFReportSignature :case-item="singleCaseObject" />
                </div>
              </template>

              <!-- Páginas intermedias: Sin signature -->
              <template v-else>
                <div class="page-body continuation-page" :style="{ height: `${availableContPx}px`, maxHeight: `${availableContPx}px`, overflow: 'hidden' }">
                  <div v-html="page.content" class="dynamic-content"></div>
                </div>
              </template>

              <div class="page-footer" :style="{ height: `${footerPx}px`, maxHeight: `${footerPx}px`, overflow: 'hidden', background: 'white', position: 'relative', zIndex: 10 }">
                <PDFReportFooter :current-page="pageIndex + 1" :total-pages="pages.length" />
              </div>
            </template>
          </div>
        </template>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick, watch } from 'vue'
import type { CSSProperties } from 'vue'
import PDFReportHeader from './parts/PDFReportHeader.vue'
import PDFReportPatientData from './parts/PDFReportPatientData.vue'
import PDFReportPatientBlock from './parts/PDFReportPatientBlock.vue'
import PDFReportSignature from './parts/PDFReportSignature.vue'
import PDFReportFooter from './parts/PDFReportFooter.vue'

export interface PreviewDiagnosis { cie10?: { primary?: any, codigo?: string, nombre?: string }; cieo?: { primary?: any, codigo?: string, nombre?: string }; formatted?: string }
export interface PreviewSections { method: string; macro: string; micro: string; diagnosis: string }
export interface PreviewCaseItem { sampleId?: string; patient?: any; caseDetails?: any; sections?: PreviewSections; diagnosis?: PreviewDiagnosis; generatedAt?: string }
export interface PreviewPayload { sampleId?: string; patient?: any; caseDetails?: any; sections?: PreviewSections | null; diagnosis?: PreviewDiagnosis | null; generatedAt?: string; multipleCases?: boolean; cases?: Array<PreviewCaseItem> }

const props = defineProps<{ payload: PreviewPayload | null | undefined }>()

const isMultiple = computed(() => Boolean(props.payload?.multipleCases && props.payload?.cases && props.payload?.cases.length))
const hasData = computed(() => {
  if (!props.payload) return false
  if (isMultiple.value) return Boolean(props.payload?.cases && props.payload?.cases.length)
  return Boolean(props.payload?.caseDetails || props.payload?.sections)
})

const singleCaseObject = computed<PreviewCaseItem>(() => ({
  sampleId: props.payload?.sampleId,
  patient: props.payload?.patient,
  caseDetails: props.payload?.caseDetails,
  sections: props.payload?.sections || undefined,
  diagnosis: props.payload?.diagnosis || undefined,
  generatedAt: props.payload?.generatedAt,
}))

const pageStyle: CSSProperties = { width: '8.5in', height: '11in', padding: '0.5in 0.5in 0.4in 0.5in', boxSizing: 'border-box', color: '#111827', overflow: 'hidden', fontFamily: 'Inter, ui-sans-serif, system-ui, -apple-system, Segoe UI, Roboto, Helvetica, Arial' }

const measureBodyRef = ref<HTMLDivElement | null>(null)
const measureHeaderRef = ref<HTMLDivElement | null>(null)
const measureFooterRef = ref<HTMLDivElement | null>(null)
const measureSignatureRef = ref<HTMLDivElement | null>(null)
const measureItem = ref<any>(null)

const availableFirstPx = ref(0)
const availableContPx = ref(0)
const signaturePx = ref(0)
const headerPx = ref(0)
const footerPx = ref(0)
const pages = ref<Array<{ content: any, isFirstPage: boolean }>>([])
const needsPagination = ref(false)
const casesPages = ref<Array<{ item: any, pages: Array<{content:any,isFirstPage:boolean,isLastPage:boolean}>, headerPx:number, footerPx:number, signaturePx:number, availableFirstPx:number, availableContPx:number }>>([])

onMounted(async () => {
  await nextTick()
  calculatePageMetrics()
  checkContentOverflow()
  if (isMultiple.value) await computeAllCases()
})

// Recalcular cuando cambien los datos
watch(() => props.payload, async () => {
  await nextTick()
  calculatePageMetrics()
  checkContentOverflow()
  if (isMultiple.value) await computeAllCases()
}, { deep: true })

function calculatePageMetrics() {
  // TAMAÑO CARTA EXACTO: 8.5" x 11"
  const pageHeight = 11 * 96 // 11 pulgadas = 1056px
  const padding = 0.5 * 96 // 0.5 pulgadas = 48px arriba y abajo
  
  // Altura disponible para contenido = 11" - 1" padding = 10" = 960px
  const availableHeight = pageHeight - (padding * 2)
  
  // Medir componentes fijos
  const headerH = measureHeaderRef.value?.scrollHeight || Math.round(2.5 * 96 * 0.8)
  const footerH = measureFooterRef.value?.scrollHeight || Math.round(1.0 * 96 * 0.6)
  const sigH = 160 // Altura fija de 160px para la firma (siempre igual)
  
  // Espacio disponible para BODY en primera página
  // Si hay múltiples páginas: 960px - header - footer (sin signature)
  // Si hay una sola página: 960px - header - footer - signature
  headerPx.value = headerH
  footerPx.value = footerH
  signaturePx.value = sigH
  
  availableFirstPx.value = Math.max(200, availableHeight - headerPx.value - footerPx.value - signaturePx.value)
  
  // Espacio disponible para BODY en páginas de continuación
  // 960px - footer = espacio para body (sin header)
  // La última página reserva espacio para signature
  availableContPx.value = Math.max(400, availableHeight - footerPx.value)
  
  // Métricas calculadas para tamaño carta exacto
}

function checkContentOverflow() {
  if (!measureBodyRef.value) return
  
  // Simular el contenido del cuerpo para medir su altura
  const bodyContent = formatBodyContent()
  measureBodyRef.value.innerHTML = bodyContent
  
  const bodyHeight = measureBodyRef.value.scrollHeight
  
  if (bodyHeight > availableFirstPx.value) {
    needsPagination.value = true
    splitContentIntoPages(bodyContent, bodyHeight)
  } else {
    needsPagination.value = false
    pages.value = [{ content: bodyContent, isFirstPage: true }]
  }
}

function formatBodyContent(): string {
  const case_item = isMultiple.value ? 
    (props.payload?.cases?.[0] || singleCaseObject.value) : 
    singleCaseObject.value
    
  let content = ''
  
  // Muestra
  content += `<div class="section"><h3>MUESTRA</h3><div>${buildSamplesText(case_item.caseDetails?.muestras)}</div></div>`
  
  // Método
  content += `<div class="section"><h3>MÉTODO UTILIZADO</h3><div>${getMethodText(case_item.sections)}</div></div>`
  
  // Macroscópica
  content += `<div class="section"><h3>DESCRIPCIÓN MACROSCÓPICA</h3><div>${case_item.sections?.macro || '—'}</div></div>`
  
  // Microscópica  
  content += `<div class="section"><h3>DESCRIPCIÓN MICROSCÓPICA</h3><div>${case_item.sections?.micro || '—'}</div></div>`
  
  // Diagnóstico
  content += `<div class="section"><h3>DIAGNÓSTICO</h3><div>${getDiagnosisText(case_item.sections, case_item.diagnosis)}</div>`
  
  // CIE codes
  const cie10 = case_item.diagnosis?.cie10?.primary?.codigo || case_item.diagnosis?.cie10?.codigo || '—'
  const cie10Name = case_item.diagnosis?.cie10?.primary?.nombre || case_item.diagnosis?.cie10?.nombre || ''
  const cieo = case_item.diagnosis?.cieo?.codigo || '—'
  const cieoName = case_item.diagnosis?.cieo?.nombre || ''
  
  content += `<div class="cie-codes">`
  content += `<div><strong>CIE-10:</strong> ${cie10}${cie10Name ? ` - ${cie10Name}` : ''}</div>`
  content += `<div><strong>CIE-O:</strong> ${cieo}${cieoName ? ` - ${cieoName}` : ''}</div>`
  content += `</div></div>`
  
  return content
}

function splitContentIntoPages(content: string, totalHeight: number) {
  const maxFirstPageHeight = availableFirstPx.value - 20 // Margen de seguridad
  const maxContinuationHeight = availableContPx.value - 20
  
  if (totalHeight <= maxFirstPageHeight) {
    pages.value = [{ content, isFirstPage: true }]
    return
  }
  
  // Dividir el contenido por secciones
  const sections = content.split('<div class="section">').filter(s => s.trim())
  let accumulatedHeight = 0
  let firstPageContent = ''
  let remainingContent = ''
  
  // Simular cada sección para medir su altura
  for (let i = 0; i < sections.length; i++) {
    const sectionHtml = `<div class="section">${sections[i]}`
    measureBodyRef.value!.innerHTML = sectionHtml
    const sectionHeight = measureBodyRef.value!.scrollHeight
    
    if (accumulatedHeight + sectionHeight <= maxFirstPageHeight) {
      // Cabe en la primera página
      firstPageContent += sectionHtml
      accumulatedHeight += sectionHeight
    } else {
      // No cabe, va a página de continuación
      remainingContent += sectionHtml
    }
  }
  
  const result: Array<{ content: string, isFirstPage: boolean }> = []
  
  // Primera página
  if (firstPageContent) {
    result.push({ content: firstPageContent, isFirstPage: true })
  }
  
  // Páginas de continuación
  if (remainingContent) {
    // Dividir el contenido restante en páginas adicionales si es necesario
    const remainingSections = remainingContent.split('<div class="section">').filter(s => s.trim())
    let currentPageContent = ''
    let currentPageHeight = 0
    
    for (const section of remainingSections) {
      const sectionHtml = `<div class="section">${section}`
      measureBodyRef.value!.innerHTML = sectionHtml
      const sectionHeight = measureBodyRef.value!.scrollHeight
      
      if (currentPageHeight + sectionHeight <= maxContinuationHeight) {
        currentPageContent += sectionHtml
        currentPageHeight += sectionHeight
      } else {
        // Crear nueva página
        if (currentPageContent) {
          result.push({ content: currentPageContent, isFirstPage: false })
        }
        currentPageContent = sectionHtml
        currentPageHeight = sectionHeight
      }
    }
    
    // Agregar la última página si tiene contenido
    if (currentPageContent) {
      result.push({ content: currentPageContent, isFirstPage: false })
    }
  }
  
  pages.value = result.length > 0 ? result : [{ content, isFirstPage: true }]
}

// ===== MODO MULTIPLE =====
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
    <div class="section-item" style="margin-bottom: 12px;">
      <h3 style="font-weight: 600; margin-bottom: 4px; font-size: 12px; color: #374151;">${s.title}</h3>
      <div style="white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; color: #111827;">${s.content}</div>
    </div>
  `).join('')
}

async function computePagesForItem(item: any) {
  measureItem.value = item
  await nextTick()
  // calcular métricas para este item
  calculatePageMetrics()
  const content = formatBodyContentForItem(item)
  if (!measureBodyRef.value) return {
    item,
    pages: [],
    headerPx: headerPx.value,
    footerPx: footerPx.value,
    signaturePx: signaturePx.value,
    availableFirstPx: availableFirstPx.value,
    availableContPx: availableContPx.value
  } as { item: any; pages: Array<{content:any,isFirstPage:boolean,isLastPage:boolean}>; headerPx:number; footerPx:number; signaturePx:number; availableFirstPx:number; availableContPx:number }
  measureBodyRef.value.innerHTML = content
  const totalHeight = measureBodyRef.value.scrollHeight
  const bundlePages: Array<{content:any,isFirstPage:boolean,isLastPage:boolean}> = []
  if (totalHeight <= availableFirstPx.value) {
    bundlePages.push({ content, isFirstPage: true, isLastPage: true })
  } else {
    // dividir similar a splitContentIntoPages
    const sections = content.split('<div class="section-item"').filter(s => s.trim()).map(s => `<div class="section-item"${s}`)
    let firstContent = ''
    let acc = 0
    for (const sec of sections) {
      measureBodyRef.value.innerHTML = firstContent + sec
      const h = measureBodyRef.value.scrollHeight
      if (h <= availableFirstPx.value) { firstContent += sec; acc = h } else { break }
    }
    bundlePages.push({ content: firstContent, isFirstPage: true, isLastPage: false })
    const remaining = sections.join('')?.replace(firstContent, '') || ''
    const parts = remaining.split('<div class="section-item"').filter(s => s.trim()).map(s => `<div class="section-item"${s}`)
    let current = ''
    let currentH = 0
    for (const part of parts) {
      measureBodyRef.value.innerHTML = current + part
      const h = measureBodyRef.value.scrollHeight
      if (h <= availableContPx.value) { current += part; currentH = h } else {
        if (current) bundlePages.push({ content: current, isFirstPage: false, isLastPage: false })
        current = part
        currentH = h
      }
    }
    if (current) bundlePages.push({ content: current, isFirstPage: false, isLastPage: true })
  }
  return {
    item,
    pages: bundlePages,
    headerPx: headerPx.value,
    footerPx: footerPx.value,
    signaturePx: signaturePx.value,
    availableFirstPx: availableFirstPx.value,
    availableContPx: availableContPx.value
  } as { item: any; pages: Array<{content:any,isFirstPage:boolean,isLastPage:boolean}>; headerPx:number; footerPx:number; signaturePx:number; availableFirstPx:number; availableContPx:number }
}

async function computeAllCases() {
  casesPages.value = []
  const list = props.payload?.cases || []
  for (const item of list) {
    const bundle = await computePagesForItem(item)
    casesPages.value.push(bundle)
  }
}

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
  if (Array.isArray(m)) return m.filter(x => typeof x === 'string' && x.trim()).join(', ')
  if (typeof m === 'string') return m
  return '—'
}

function getDiagnosisText(sections: any, diagnosis: any): string {
  const formatted = diagnosis?.formatted?.toString().trim()
  if (formatted) return formatted
  const free = sections?.diagnosis?.toString().trim()
  return free || '—'
}

function recibidoNumero(casoCode?: string): string {
  if (!casoCode) return '—'
  const parts = String(casoCode).split('-')
  if (parts.length < 2) return casoCode
  return parts.slice(1).join('-')
}
</script>

<style>
.case-separator { page-break-before: always; break-before: page; height: 0; margin: 0; }
.pdf-preview-container { background-color: #f9fafb; border-radius: 0; border: 0; padding: 0; margin: 0; height: 11in; display: flex; justify-content: center; align-items: flex-start; }
.report-page { 
  width: 8.5in !important; 
  height: 11in !important; 
  max-width: 8.5in !important;
  max-height: 11in !important;
  min-height: 11in !important;
  margin: 0; 
  display: flex; 
  flex-direction: column; 
  overflow: hidden !important; 
  box-sizing: border-box; 
  padding: 0.5in 0.5in 0.5in 0.5in; 
  position: relative; 
}
.report-page:not(:last-child) { margin-bottom: 20px; }
.print-content { display: flex; flex-direction: column; gap: 0; margin: 0 auto; padding: 0; position: relative; height: 11in; width: 8.5in; }
.report-page .body-text { font-size: 12px; line-height: 1.4; }
.print-content .report-page { margin-bottom: 20px; min-height: 11in !important; padding: 0.5in 0.5in 0.3in 0.5in !important; box-sizing: border-box !important; overflow: visible !important; }
.print-content .report-page { position: relative; z-index: 1; }
.report-page table { table-layout: fixed; }
.report-page td, .report-page th { word-break: break-word; overflow-wrap: anywhere; }
.report-page .wrap { white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; }
.page-header {
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  background: white;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.page-body {
  flex-shrink: 0;
  position: relative;
  z-index: 5;
  overflow: hidden;
  display: flex;
  flex-direction: column;
}

.page-signature {
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  background: white;
  margin-top: 0.5rem;
  margin-bottom: 0.5rem;
  overflow: hidden;
}

.page-footer {
  flex-shrink: 0;
  position: relative;
  z-index: 10;
  background: white;
  overflow: hidden;
}

.constrained-height {
  overflow: hidden !important;
  box-sizing: border-box !important;
}

.continuation-page {
  padding-top: 0.5rem;
  box-sizing: border-box !important;
  overflow: hidden !important;
}

.dynamic-content {
  font-size: 12px;
  line-height: 1.4;
  height: 100%;
  overflow: hidden !important;
  box-sizing: border-box;
}

.dynamic-content .section {
  margin-bottom: 0.5rem;
}

.dynamic-content .section h3 {
  margin-bottom: 0.25rem;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.02em;
  color: #374151;
}

.dynamic-content .section div {
  color: #111827;
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.dynamic-content .cie-codes {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.3;
  margin-top: 0.75rem;
}

.dynamic-content .cie-codes div {
  margin-bottom: 0.25rem;
}

.dynamic-content .cie-codes strong {
  font-weight: 600;
  color: #374151;
}
@media print {
  @page { size: letter; margin: 0 !important; }
  * { -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
  html, body { margin: 0 !important; padding: 0 !important; height: auto !important; }
  .print-hidden { display: none !important; }
  .pdf-preview-container { background: transparent !important; border: none !important; padding: 0 !important; margin: 0 !important; height: auto !important; min-height: auto !important; display: block !important; width: 100% !important; }
  .print-content { margin: 0 !important; padding: 0 !important; height: auto !important; min-height: auto !important; width: 100% !important; display: block !important; }
  .report-page { width: 8.5in !important; height: 11in !important; min-height: 11in !important; max-height: 11in !important; padding: 0.5in 0.5in 0.3in 0.5in !important; margin: 0 !important; box-sizing: border-box !important; box-shadow: none !important; border: none !important; background: white !important; display: block !important; color: #111827 !important; page-break-inside: avoid !important; break-inside: avoid !important; overflow: hidden !important; position: relative !important; max-width: 8.5in !important; max-height: 11in !important; }
  .report-page:not(:first-child) { page-break-before: always !important; break-before: page !important; }
  .report-page:last-child { page-break-after: avoid !important; break-after: avoid !important; }
  .content-area { display: block !important; height: auto !important; flex: none !important; }
  .report-page table { border-collapse: collapse !important; width: 100% !important; }
  .report-page table td { border: 1px solid #d1d5db !important; vertical-align: top !important; }
  .report-page img { box-shadow: none !important; display: block !important; }
  .report-page img[alt*="firma"], .report-page img[alt*="Firma"] { background: transparent !important; mix-blend-mode: multiply !important; -webkit-print-color-adjust: exact !important; color-adjust: exact !important; }
}
</style>


