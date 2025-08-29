<template>
  <div>
    <div v-if="!hasData" class="p-4 bg-yellow-50 border border-yellow-200 rounded text-sm text-yellow-800 print-hidden">
      No hay datos para previsualizar.
    </div>

    <div class="print-hidden" style="position:absolute; left:-10000px; top:0; opacity:0; pointer-events:none; overflow:visible;">
      <div ref="measureBodyRef" style="width:8.5in; font-size:12px; line-height:1.35; white-space:pre-wrap; word-break:break-word; overflow-wrap:anywhere;"></div>

      <div ref="measureHeaderRef" style="width:8.5in; box-sizing:border-box;">
        <div>
          <PDFReportHeader :case-item="singleCaseObject" />
          <PDFReportDeptInfo :case-item="singleCaseObject" :recibido-numero="recibidoNumero(singleCaseObject.caseDetails?.CasoCode || singleCaseObject.sampleId)" />
        </div>
      </div>

      <div ref="measureFooterRef" style="width:8.5in; box-sizing:border-box;">
        <PDFReportFooter :current-page="1" :total-pages="1" />
      </div>

      <div ref="measureSignatureRef" style="width:8.5in; box-sizing:border-box;">
        <PDFReportSignature :case-item="singleCaseObject" />
      </div>
    </div>

    <div v-if="hasData" class="pdf-preview-container">
      <div v-if="isMultiple" class="print-content">
        <div
          v-for="(item, index) in props.payload?.cases || []"
          :key="`m-${index}`"
          class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
          :style="pageStyle"
        >
          <PDFReportHeader :case-item="item" />
          <PDFReportDeptInfo :case-item="item" :recibido-numero="recibidoNumero(item.caseDetails?.CasoCode || item.sampleId)" />

          <div class="content-area">
            <PDFReportPatientBlock :case-item="item" />
          </div>

          <div class="footer-container">
            <PDFReportFooter :current-page="1" :total-pages="1" />
          </div>
        </div>
      </div>

      <div v-else class="print-content">
        <div
          class="bg-white mx-auto shadow-sm border border-gray-200 report-page"
          :style="pageStyle"
        >
          <PDFReportHeader :case-item="singleCaseObject" />
          <PDFReportDeptInfo :case-item="singleCaseObject" :recibido-numero="recibidoNumero(singleCaseObject.caseDetails?.CasoCode || singleCaseObject.sampleId)" />

          <div class="content-area">
            <PDFReportPatientBlock :case-item="singleCaseObject" />
          </div>

          <div class="footer-container">
            <PDFReportFooter :current-page="1" :total-pages="1" />
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

export interface PreviewDiagnosis { cie10?: { primary?: any }; cieo?: { primary?: any }; formatted?: string }
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

const pageStyle: CSSProperties = { width: '8.5in', height: '11in', padding: '0.5in 0.5in 0.3in 0.5in', boxSizing: 'border-box', color: '#111827', overflow: 'hidden' }

const measureBodyRef = ref<HTMLDivElement | null>(null)
const measureHeaderRef = ref<HTMLDivElement | null>(null)
const measureFooterRef = ref<HTMLDivElement | null>(null)
const measureSignatureRef = ref<HTMLDivElement | null>(null)

const availableFirstPx = ref(0)
const availableContPx = ref(0)
const signaturePx = ref(0)

onMounted(async () => {
  await nextTick()
  const pagePx = 11 * 96
  const padTop = 0.5 * 96
  const padBottom = 0.3 * 96
  const headerH = measureHeaderRef.value?.scrollHeight || 0
  const footerH = measureFooterRef.value?.scrollHeight || 0
  const sigH = measureSignatureRef.value?.scrollHeight || 0
  const pageInnerPx = Math.max(0, pagePx - padTop - padBottom)
  availableFirstPx.value = Math.max(0, pageInnerPx - headerH - footerH)
  availableContPx.value = Math.max(0, pageInnerPx - footerH)
  signaturePx.value = sigH
})

function recibidoNumero(casoCode?: string): string {
  if (!casoCode) return '—'
  const parts = String(casoCode).split('-')
  if (parts.length < 2) return casoCode
  return parts.slice(1).join('-')
}
</script>

<style>
.pdf-preview-container { background-color: #f9fafb; border-radius: 0; border: 0; padding: 0; margin: 0; height: 11in; display: flex; justify-content: center; align-items: flex-start; }
.report-page { width: 8.5in; height: 11in; margin: 0; display: block; overflow: hidden; box-sizing: border-box; padding: 0.5in 0.5in 0.3in 0.5in; position: relative; }
.report-page:not(:last-child) { margin-bottom: 20px; }
.print-content { display: flex; flex-direction: column; gap: 0; margin: 0 auto; padding: 0; position: relative; height: 11in; width: 8.5in; }
.report-page .body-text { font-size: 12px; line-height: 1.35; }
.print-content .report-page { margin-bottom: 20px; min-height: 11in !important; padding: 0.5in 0.5in 0.3in 0.5in !important; box-sizing: border-box !important; overflow: visible !important; }
.print-content .report-page { position: relative; z-index: 1; }
.report-page table { table-layout: fixed; }
.report-page td, .report-page th { word-break: break-word; overflow-wrap: anywhere; }
.report-page .wrap { white-space: pre-wrap; word-break: break-word; overflow-wrap: anywhere; }
.content-area { display: block; margin-bottom: 20px; }
.footer-container { position: absolute; bottom: 0.3in; left: 0.5in; right: 0.5in; }
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


