<template>
  <div>
    <div v-if="!hasData" class="p-4 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800 print-hidden">
      No hay datos para previsualizar.
    </div>

    
    <!-- Contenedores de medición ocultos (renderizan tamaño real fuera de pantalla) -->
    <div class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
      <!-- Medidor de ancho real del cuerpo de página (8.5in completo) -->
      <div ref="measureBodyRef" style="width:8.5in; font-size:12px; line-height:1.35; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>

      <!-- Medir altura de encabezados+paciente (primera página) en ancho de cuerpo (8.5in) sin padding -->
      <div ref="measureHeaderRef" style="width:8.5in; box-sizing:border-box;">
        <div>
          <PDFReportHeader />
          <PDFReportDeptInfo :case-item="singleCaseObject" :format-date="formatDate" :recibido-numero="recibidoNumero" />
          <PDFReportPatientBlock :case-item="singleCaseObject" :recibido-numero="recibidoNumero" />
        </div>
      </div>

      <!-- Medir altura del footer en ancho de cuerpo (8.5in) sin padding -->
      <div ref="measureFooterRef" style="width:8.5in; box-sizing:border-box;">
        <PDFReportFooter :page="1" :total="1" />
      </div>

      <!-- Medir altura de la firma del patólogo en ancho de cuerpo (8.5in) sin padding -->
      <div ref="measureSignatureRef" style="width:8.5in; box-sizing:border-box;">
        <PDFReportSignature :case-item="singleCaseObject" />
      </div>
    </div>

    <div v-if="hasData" class="pdf-preview-container">
      <!-- Múltiples casos -->
      <div v-if="isMultiple" class="print-content">
        <div
          v-for="(item, index) in casesWithPagination"
          :key="`${item.originalIndex}-${item.pageIndex}`"
          class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
          :style="pageStyle"
        >
          <template v-if="item.pageIndex === 0">
            <PDFReportHeader />
            <PDFReportDeptInfo
              :case-item="item.case"
              :format-date="formatDate"
              :recibido-numero="recibidoNumero"
            />
            <PDFReportPatientBlock :case-item="item.case" :recibido-numero="recibidoNumero" />
          </template>

          <div class="content-area">
            <div class="wrap body-text" style="white-space: pre-wrap;" v-html="item.pageContent">
            </div>
          </div>

          <template v-if="item.isLastPage">
            <PDFReportSignature 
              :case-item="item.case" 
              @signature-loaded="handleSignatureLoaded"
            />
          </template>

          <div class="footer-container">
            <PDFReportFooter :page="item.pageNumber" :total="item.totalPagesForPatient" />
          </div>
        </div>
      </div>

      <!-- Caso único -->
      <div v-else class="print-content">
        <div
          v-for="(chunk, idx) in singleCaseChunks"
          :key="idx"
          class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
          :style="pageStyle"
        >
          <template v-if="idx === 0">
            <PDFReportHeader />
            <PDFReportDeptInfo
              :case-item="singleCaseObject"
              :format-date="formatDate"
              :recibido-numero="recibidoNumero"
            />
            <PDFReportPatientBlock :case-item="singleCaseObject" :recibido-numero="recibidoNumero" />
          </template>

          <div class="content-area">
            <div class="wrap body-text" style="white-space: pre-wrap;" v-html="chunk">
            </div>
          </div>

          <template v-if="idx === singleCaseChunks.length - 1">
            <PDFReportSignature 
              :case-item="singleCaseObject" 
              @signature-loaded="handleSignatureLoaded"
            />
          </template>

          <div class="footer-container">
            <PDFReportFooter :page="idx + 1" :total="singleCaseChunks.length" />
          </div>
        </div>
      </div>
    </div>
  </div>
  
</template>

<script setup lang="ts">
import { computed, ref, onMounted, nextTick } from 'vue'
import type { CSSProperties } from 'vue'
import PDFReportHeader from './parts/PDFReportHeader.vue'
import PDFReportDeptInfo from './parts/PDFReportDeptInfo.vue'
import PDFReportPatientBlock from './parts/PDFReportPatientBlock.vue'
import PDFReportSignature from './parts/PDFReportSignature.vue'
import PDFReportFooter from './parts/PDFReportFooter.vue'

export interface PreviewDiagnosis {
  cie10?: { primary?: any }
  cieo?: { primary?: any }
  formatted?: string
}

export interface PreviewSections { method: string; macro: string; micro: string; diagnosis: string }

export interface PreviewCaseItem {
  sampleId?: string
  patient?: any
  caseDetails?: any
  sections?: PreviewSections
  diagnosis?: PreviewDiagnosis
  generatedAt?: string
}

export interface PreviewPayload {
  sampleId?: string
  patient?: any
  caseDetails?: any
  sections?: PreviewSections | null
  diagnosis?: PreviewDiagnosis | null
  generatedAt?: string
  multipleCases?: boolean
  cases?: Array<PreviewCaseItem>
}

const props = defineProps<{ payload: PreviewPayload | null | undefined }>()

const emit = defineEmits<{
  'all-signatures-loaded': []
}>()

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

// utilidades locales para extracción de códigos/nombres
const pickCode = (o: any): string | undefined => (o?.codigo ?? o?.code ?? o?.cod ?? o?.id)
const pickName = (o: any): string | undefined => (o?.nombre ?? o?.name ?? o?.descripcion ?? o?.description)

const pageStyle: CSSProperties = { 
  width: '8.5in', 
  height: '11in', 
  padding: '0.5in 0.5in 0.3in 0.5in', 
  boxSizing: 'border-box', 
  color: '#111827', 
  overflow: 'hidden' 
}

function escapeHtml(value: unknown): string {
  const s = String(value ?? '')
  return s
    .replace(/&/g, '&amp;')
    .replace(/</g, '&lt;')
    .replace(/>/g, '&gt;')
    .replace(/\"/g, '&quot;')
    .replace(/'/g, '&#39;')
}

// Construir el HTML del informe a paginar (sin encabezados)
function buildCaseFullText(ci: PreviewCaseItem): string {
  const parts: string[] = []
  const samples = escapeHtml(buildSamplesDescription((ci.caseDetails as any)?.muestras))
  const macro = escapeHtml(ci.sections?.macro || '—')
  const micro = escapeHtml(ci.sections?.micro || '—')
  const method = escapeHtml(ci.sections?.method || '—')

  // Helpers para extraer código/nombre con diferentes llaves
  const pickCode = (o: any): string | undefined => (o?.codigo ?? o?.code ?? o?.cod ?? o?.id)
  const pickName = (o: any): string | undefined => (o?.nombre ?? o?.name ?? o?.descripcion ?? o?.description)

  // CIE-10
  const cie10Any: any = (ci.diagnosis as any)?.cie10 || {}
  const cie10Primary: any = cie10Any?.primary || cie10Any
  const cie10CodeRaw = pickCode(cie10Primary)
  const cie10NameRaw = pickName(cie10Primary)
  const cie10Code = escapeHtml(cie10CodeRaw ?? '—')
  const cie10Name = cie10NameRaw ? ` - ${escapeHtml(cie10NameRaw)}` : ''

  // CIE-O
  const cieoAny: any = (ci.diagnosis as any)?.cieo || {}
  const cieoPrimary: any = cieoAny?.primary || cieoAny
  const cieoCodeRaw = pickCode(cieoPrimary)
  const cieoNameRaw = pickName(cieoPrimary)
  const cieoCode = escapeHtml(cieoCodeRaw ?? '—')
  const cieoName = cieoNameRaw ? ` - ${escapeHtml(cieoNameRaw)}` : ''

  // Priorizar siempre el texto libre del diagnóstico; si no existe, usar el formateado
  const dxRawFree = (ci.sections?.diagnosis ?? '').toString().trim()
  const dxRawFormatted = ((ci.diagnosis as any)?.formatted ?? '').toString().trim()
  const dxText = escapeHtml(dxRawFree || dxRawFormatted || '—')

  parts.push(`<strong>MUESTRA:</strong><br/>${samples}`)
  parts.push(`<br/><strong>DESCRIPCIÓN MACROSCÓPICA</strong><br/>${macro}`)
  parts.push(`<br/><strong>DESCRIPCIÓN MICROSCÓPICA</strong><br/>${micro}`)
  parts.push(`<br/><strong>MÉTODO UTILIZADO</strong><br/>${method}`)
  // Bloque compacto de diagnóstico + CIEs (un solo fragmento para evitar <br/> extra del join)
  const diagBlock = [
    `<br/><strong>DIAGNÓSTICO</strong>`,
    dxText,
    `<div style="margin-top:14px"><strong>CIE-10:</strong> ${cie10Code}${cie10Name}</div>`,
    `<div style="margin-top:0px"><strong>CIE-O:</strong> ${cieoCode}${cieoName}</div>`
  ].join('<br/>')
  parts.push(diagBlock)

  return parts.join('<br/>')
}

// Refs y mediciones para paginación por altura
const measureBodyRef = ref<HTMLDivElement | null>(null)
const measureHeaderRef = ref<HTMLDivElement | null>(null)
const measureFooterRef = ref<HTMLDivElement | null>(null)
const measureSignatureRef = ref<HTMLDivElement | null>(null)

const availableFirstPx = ref(0)
const availableContPx = ref(0)
const signaturePx = ref(0)

// Estado para manejar la carga de firmas
const signaturesLoaded = ref(0)
const totalSignatures = ref(0)
const allSignaturesLoaded = ref(false)

onMounted(async () => {
  await nextTick()
  // 96px por pulgada en CSS - Formato Carta (8.5in × 11in)
  const pagePx = 11 * 96 // 11 pulgadas de altura
  const padTop = 0.5 * 96
  const padBottom = 0.3 * 96
  const headerH = measureHeaderRef.value?.scrollHeight || 0
  const footerH = measureFooterRef.value?.scrollHeight || 0
  const sigH = measureSignatureRef.value?.scrollHeight || 0
  const pageInnerPx = Math.max(0, pagePx - padTop - padBottom)
  availableFirstPx.value = Math.max(0, pageInnerPx - headerH - footerH)
  availableContPx.value = Math.max(0, pageInnerPx - footerH)
  signaturePx.value = sigH
  
  // Calcular el total de firmas que se van a cargar
  if (isMultiple.value && props.payload?.cases) {
    totalSignatures.value = props.payload.cases.length
  } else {
    totalSignatures.value = 1
  }
})

// Función para manejar cuando se carga una firma
const handleSignatureLoaded = (hasSignature: boolean) => {
  signaturesLoaded.value++
  console.log(`📝 Firma ${signaturesLoaded.value}/${totalSignatures.value} cargada`)
  
  if (signaturesLoaded.value >= totalSignatures.value) {
    allSignaturesLoaded.value = true
    console.log('✅ Todas las firmas han sido cargadas')
    emit('all-signatures-loaded')
  }
}

function paginateByHeight(html: string, firstMaxPx: number, contMaxPx: number): string[] {
  if (!html) return ['']
  const paras = html.split(/<br\/>/)
  const chunks: string[] = []
  let buffer: string[] = []
  let isFirst = true

  const measure = (content: string): number => {
    if (!measureBodyRef.value) return 0
    measureBodyRef.value.innerHTML = content
    return measureBodyRef.value.scrollHeight
  }

  const flush = () => {
    const content = buffer.join('<br/>')
    chunks.push(content)
    buffer = []
  }

  let currentMax = firstMaxPx || 0
  for (let i = 0; i < paras.length; i += 1) {
    const nextCandidate = buffer.length ? buffer.join('<br/>') + '<br/>' + paras[i] : paras[i]
    const height = measure(nextCandidate)
    if (height <= (currentMax || Number.MAX_SAFE_INTEGER)) {
      buffer.push(paras[i])
    } else {
      // Intentar encajar parte del párrafo actual en el espacio restante
      if (buffer.length > 0) {
        const prefix = buffer.join('<br/>')
        const split = hardSplitAppend(prefix, paras[i], currentMax)
        if (split.fit) {
          buffer.push(split.fit)
          flush()
          isFirst = false
          currentMax = contMaxPx || 0
          if (split.rest) {
            // continuar el resto en la nueva página
            buffer.push(split.rest)
          }
          continue
        }
      }
      // Si no hay buffer o no se pudo encajar nada, forzar corte por caracteres desde el inicio del párrafo
      const hardSplit = hardSplitByHeight(paras[i], currentMax)
      buffer.push(hardSplit.fit)
      flush()
      isFirst = false
      currentMax = contMaxPx || 0
      if (hardSplit.rest) {
        buffer.push(hardSplit.rest)
      }
    }
  }
  if (buffer.length) flush()
  return chunks
}

function hardSplitByHeight(textFrag: string, maxPx: number): { fit: string; rest: string } {
  if (!measureBodyRef.value || !maxPx) return { fit: textFrag, rest: '' }
  let lo = 0, hi = textFrag.length, ans = 0
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    measureBodyRef.value.innerHTML = textFrag.slice(0, mid)
    const h = measureBodyRef.value.scrollHeight
    if (h <= maxPx) {
      ans = mid
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  const fit = textFrag.slice(0, ans)
  const rest = textFrag.slice(ans)
  return { fit, rest }
}

// Divide un párrafo teniendo en cuenta el contenido previo ya en la página
function hardSplitAppend(prefixHtml: string, paragraphHtml: string, maxPx: number): { fit: string; rest: string } {
  if (!measureBodyRef.value || !maxPx) return { fit: '', rest: paragraphHtml }
  let lo = 0, hi = paragraphHtml.length, ans = 0
  while (lo <= hi) {
    const mid = Math.floor((lo + hi) / 2)
    const content = (prefixHtml ? prefixHtml + '<br/>' : '') + paragraphHtml.slice(0, mid)
    measureBodyRef.value.innerHTML = content
    const h = measureBodyRef.value.scrollHeight
    if (h <= maxPx) {
      ans = mid
      lo = mid + 1
    } else {
      hi = mid - 1
    }
  }
  const fit = paragraphHtml.slice(0, ans)
  const rest = paragraphHtml.slice(ans)
  return { fit, rest }
}

function paginateCaseText(text: string): string[] {
  // Si ya tenemos medidas, usar paginación por altura; si no, fallback a una sola página y el navegador cortará
  if (availableFirstPx.value > 0 && availableContPx.value > 0) {
    return paginateByHeight(text, availableFirstPx.value, availableContPx.value)
  }
  return [text]
}

// Ajusta el último chunk para reservar espacio de firma en la última página del caso
function adjustLastChunkForSignature(chunks: string[], contMaxPx: number, signaturePxNeeded: number): string[] {
  if (!chunks.length || !measureBodyRef.value || !contMaxPx || !signaturePxNeeded) return chunks
  let last = chunks[chunks.length - 1]
  const allowed = Math.max(0, contMaxPx - signaturePxNeeded)
  const measure = (html: string) => {
    measureBodyRef.value!.innerHTML = html
    return measureBodyRef.value!.scrollHeight
  }
  while (measure(last) > allowed) {
    const split = hardSplitByHeight(last, allowed)
    chunks[chunks.length - 1] = split.fit
    if (split.rest) {
      chunks.push(split.rest)
      // Para páginas nuevas que no sean la última, no reservamos firma
      last = chunks[chunks.length - 1]
    } else {
      break
    }
  }
  return chunks
}

const casesWithPagination = computed(() => {
  if (!isMultiple.value || !props.payload?.cases) return [] as Array<{
    case: PreviewCaseItem; pageNumber: number; totalPagesForPatient: number; originalIndex: number; pageIndex: number; pageContent: string; isLastPage: boolean
  }>

  // Agrupar por paciente
  const patientGroups: Record<string, Array<{ case: PreviewCaseItem; originalIndex: number }>> = {}
  props.payload.cases.forEach((caseItem, index) => {
    const patientId = (caseItem.patient as any)?.document || (caseItem.caseDetails as any)?.paciente?.cedula || `unknown_${index}`
    if (!patientGroups[patientId]) patientGroups[patientId] = []
    patientGroups[patientId].push({ case: caseItem, originalIndex: index })
  })

  // Por cada paciente, expandir páginas y asignar numeración acumulada
  const expanded: Array<{
    case: PreviewCaseItem; pageNumber: number; totalPagesForPatient: number; originalIndex: number; pageIndex: number; pageContent: string; isLastPage: boolean
  }> = []

  Object.values(patientGroups).forEach(patientCases => {
    // Expandir a páginas
    const pagesPerCase: Array<{ originalIndex: number; case: PreviewCaseItem; chunks: string[] }> = patientCases.map(item => {
      const raw = paginateCaseText(buildCaseFullText(item.case))
      // Reservar espacio para firma en la última página del caso
      const isSinglePage = raw.length === 1
      const lastPageMax = isSinglePage ? availableFirstPx.value : availableContPx.value
      const adjusted = adjustLastChunkForSignature([...raw], lastPageMax, signaturePx.value)
      return { originalIndex: item.originalIndex, case: item.case, chunks: adjusted }
    })

    const totalPagesForPatient = pagesPerCase.reduce((sum, it) => sum + it.chunks.length, 0)

    // Asignar números consecutivos por paciente
    let runningPage = 1
    pagesPerCase.forEach(item => {
      item.chunks.forEach((content, idx) => {
        expanded.push({
          case: item.case,
          pageNumber: runningPage,
          totalPagesForPatient,
          originalIndex: item.originalIndex,
          pageIndex: idx,
          pageContent: content,
          isLastPage: idx === item.chunks.length - 1,
        })
        runningPage += 1
      })
    })
  })

  // Mantener orden original por caso
  return expanded.sort((a, b) => a.originalIndex - b.originalIndex || a.pageIndex - b.pageIndex)
})

const singleCaseChunks = computed(() => {
  const text = buildCaseFullText(singleCaseObject.value)
  const chunks = paginateCaseText(text)
  const lastPageMax = chunks.length === 1 ? availableFirstPx.value : availableContPx.value
  return adjustLastChunkForSignature(chunks, lastPageMax, signaturePx.value)
})

function recibidoNumero(casoCode?: string): string | null {
  if (!casoCode) return null
  const parts = String(casoCode).split('-')
  if (parts.length < 2) return casoCode
  return parts.slice(1).join('-')
}

function buildSamplesDescription(list: any[] | undefined): string {
  if (!list || list.length === 0) return '—'
  return list.map(it => `${it.region_cuerpo}: ${it.pruebas?.map((p: any) => {
    // Si el nombre es igual al id, solo mostrar el código
    if (p.id === p.nombre) {
      return p.id
    }
    // Si son diferentes, mostrar código - nombre
    return `${p.id} - ${p.nombre}`
  }).join(', ')}`).join(' | ')
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
</script>

<style>
/* Contenedor principal del PDF */
.pdf-preview-container {
  background-color: #f9fafb;
  border-radius: 0;
  border: 0;
  padding: 0;
  margin: 0;
  height: 11in; /* Altura fija de Carta (8.5in × 11in) */
  display: flex;
  justify-content: center;
  align-items: flex-start;
}

.report-page {
  width: 8.5in; /* Ancho completo de Carta */
  height: 11in; /* Altura fija de Carta */
  margin: 0;
  display: block;
  overflow: hidden;
  box-sizing: border-box;
  padding: 0.5in 0.5in 0.3in 0.5in;
  position: relative;
}

/* Evitar hojas en blanco en vista previa */
.report-page:not(:last-child) {
  margin-bottom: 20px;
}

.print-content {
  display: flex;
  flex-direction: column;
  gap: 0;
  margin: 0 auto;
  padding: 0;
  position: relative;
  height: 11in; /* Altura fija de Carta (8.5in × 11in) */
  width: 8.5in; /* Ancho completo de Carta para centrado */
}

/* Reducir tamaño solo del cuerpo */
.report-page .body-text { font-size: 12px; line-height: 1.35; }

.print-content .report-page { 
  margin-bottom: 20px; /* Margen entre páginas solo en vista previa */
  min-height: 11in !important; /* Altura de Carta */
  padding: 0.5in 0.5in 0.3in 0.5in !important;
  box-sizing: border-box !important;
  overflow: visible !important;
}

.print-content .report-page { position: relative; z-index: 1; }

/* Evitar desborde de texto hacia la derecha */
.report-page table { table-layout: fixed; }
.report-page td, .report-page th { word-break: break-word; overflow-wrap: anywhere; }
.report-page .wrap { white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; }

/* Estilos para el área de contenido */
.content-area {
  display: block;
  margin-bottom: 20px;
}

.footer-container {
  position: absolute;
  bottom: 0.3in;
  left: 0.5in;
  right: 0.5in;
}

@media print {
  @page { 
    size: letter; 
    margin: 0 !important;
  }
  
  * { 
    -webkit-print-color-adjust: exact !important; 
    color-adjust: exact !important; 
  }
  
  html, body { 
    margin: 0 !important; 
    padding: 0 !important; 
    height: auto !important;
  }
  
  .print-hidden { 
    display: none !important; 
  }
  
  .pdf-preview-container { 
    background: transparent !important; 
    border: none !important; 
    padding: 0 !important; 
    margin: 0 !important; 
    height: auto !important; 
    min-height: auto !important;
    display: block !important;
    width: 100% !important;
  }
  
  .print-content { 
    margin: 0 !important; 
    padding: 0 !important; 
    height: auto !important; 
    min-height: auto !important;
    width: 100% !important;
    display: block !important;
  }
  
  .report-page {
    width: 8.5in !important;
    height: 11in !important;
    min-height: 11in !important;
    max-height: 11in !important;
    padding: 0.5in 0.5in 0.3in 0.5in !important;
    margin: 0 !important;
    box-sizing: border-box !important;
    box-shadow: none !important;
    border: none !important;
    background: white !important;
    display: block !important;
    color: #111827 !important;
    page-break-inside: avoid !important;
    break-inside: avoid !important;
    overflow: hidden !important;
    position: relative !important;
    /* Formato Carta: 8.5in × 11in completo */
    max-width: 8.5in !important;
    max-height: 11in !important;
  }
  
  /* Forzar salto de página entre report-page */
  .report-page:not(:first-child) {
    page-break-before: always !important;
    break-before: page !important;
  }
  
  /* Evitar salto después de la última página */
  .report-page:last-child {
    page-break-after: avoid !important;
    break-after: avoid !important;
  }
  
  .content-area {
    display: block !important;
    height: auto !important;
    flex: none !important;
  }
  
  .report-page table { 
    border-collapse: collapse !important; 
    width: 100% !important; 
  }
  
  .report-page table td { 
    border: 1px solid #d1d5db !important; 
    vertical-align: top !important; 
  }
  
  .report-page img { 
    box-shadow: none !important; 
    display: block !important; 
  }
  
  /* Estilos específicos para imágenes de firma en PDF */
  .report-page img[alt*="firma"], .report-page img[alt*="Firma"] {
    background: transparent !important;
    mix-blend-mode: multiply !important;
    -webkit-print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
}
</style>


