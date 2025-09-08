<template>
  <div class="report-body">
    <div class="body-grid">
      <template v-if="!onlyDiagnosis">
        <div class="section-item">
          <h3 class="section-heading">MUESTRA</h3>
          <div class="section-content wrap">{{ buildSamplesDescription(caseItem?.caseDetails?.muestras) }}</div>
        </div>
        <div class="section-item">
          <h3 class="section-heading">MÉTODO UTILIZADO</h3>
          <div class="section-content wrap">{{ getMethodText(caseItem?.sections) || '—' }}</div>
        </div>
        <div class="section-item">
          <h3 class="section-heading">DESCRIPCIÓN MACROSCÓPICA</h3>
          <div class="section-content wrap">{{ caseItem?.sections?.macro || '—' }}</div>
        </div>
        <div class="section-item">
          <h3 class="section-heading">DESCRIPCIÓN MICROSCÓPICA</h3>
          <div class="section-content wrap">{{ caseItem?.sections?.micro || '—' }}</div>
        </div>
      </template>
      <div class="section-item diagnosis-section">
        <h3 class="section-heading">DIAGNÓSTICO</h3>
        <div class="section-content">
          <div class="wrap diagnosis-text">{{ getDiagnosisText(caseItem?.sections, caseItem?.diagnosis, diagnosisOverride) || '—' }}</div>
          <div v-if="!onlyDiagnosis" class="cie-codes">
            <div class="cie-item">
              <strong>CIE-10:</strong> {{ (caseItem?.diagnosis?.cie10?.primary?.codigo || caseItem?.diagnosis?.cie10?.codigo) ?? '—' }}
              <template v-if="(caseItem?.diagnosis?.cie10?.primary?.nombre || caseItem?.diagnosis?.cie10?.nombre)"> - {{ caseItem?.diagnosis?.cie10?.primary?.nombre || caseItem?.diagnosis?.cie10?.nombre }}</template>
            </div>
            <div class="cie-item">
              <strong>CIE-O:</strong> {{ caseItem?.diagnosis?.cieo?.codigo ?? '—' }}
              <template v-if="caseItem?.diagnosis?.cieo?.nombre"> - {{ caseItem.diagnosis.cieo.nombre }}</template>
            </div>
          </div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CaseItem {
  caseDetails?: {
    muestras?: any[]
  }
  sections?: {
    macro?: string
    micro?: string
    method?: string | string[]
    methodText?: string
    diagnosis?: string
  }
  diagnosis?: {
    cie10?: {
      codigo?: string
      nombre?: string
      primary?: any
    }
    cieo?: {
      codigo?: string
      nombre?: string
    }
    formatted?: string
  }
}

defineProps<{
  caseItem?: CaseItem
  recibidoNumero?: string
  diagnosisOverride?: string
  onlyDiagnosis?: boolean
}>()

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

function getDiagnosisText(
  sec?: { diagnosis?: string } | null,
  diag?: { formatted?: string } | null,
  override?: string
): string {
  const ov = (override ?? '').toString().trim()
  if (ov) return ov
  const free = (sec?.diagnosis ?? '').toString().trim()
  if (free) return free
  const formatted = (diag?.formatted ?? '').toString().trim()
  if (formatted) return formatted
  return ''
}
</script>

<style scoped>
.report-body {
  margin-bottom: 1rem;
  font-size: 12px;
  line-height: 1.4;
  flex-grow: 1;
}

.body-grid {
  display: grid;
  grid-template-rows: auto auto auto auto 1fr;
  grid-row-gap: 0.5rem;
  height: 100%;
}

.section-item {
  min-height: 0;
  display: flex;
  flex-direction: column;
}

.diagnosis-section {
  flex-grow: 1;
}

.section-heading {
  margin-bottom: 0.25rem;
  font-weight: 600;
  font-size: 12px;
  letter-spacing: 0.02em;
  color: #374151;
  flex-shrink: 0;
}

.section-content {
  flex-grow: 1;
  color: #111827;
}

.wrap {
  white-space: pre-wrap;
  word-break: break-word;
  overflow-wrap: anywhere;
}

.diagnosis-text {
  margin-bottom: 0.75rem;
}

.cie-codes {
  font-size: 11px;
  color: #6b7280;
  line-height: 1.3;
}

.cie-item {
  margin-bottom: 0.25rem;
}

.cie-item strong {
  font-weight: 600;
  color: #374151;
}
</style>
