<template>
  <div class="report-content text-xs space-y-3">
    <div class="section-muestra">
      <h3 class="font-semibold mb-1 text-sm">MUESTRA:</h3>
      <div class="whitespace-pre-wrap">{{ buildSamplesDescription(caseItem?.caseDetails?.muestras) }}</div>
    </div>

    <div class="section-macro">
      <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MACROSCÓPICA</h3>
      <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseItem?.sections?.macro || '—' }}</div>
    </div>

    <div class="section-micro">
      <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MICROSCÓPICA</h3>
      <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseItem?.sections?.micro || '—' }}</div>
    </div>

    <div class="section-metodo">
      <h3 class="font-semibold mb-1 text-sm">MÉTODO UTILIZADO</h3>
      <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseItem?.sections?.method || '—' }}</div>
    </div>

    <div class="section-diagnostico">
      <h3 class="font-semibold mb-1 text-sm">DIAGNÓSTICO</h3>
      <div class="whitespace-pre-wrap mt-1 pt-1">
        <div>{{ getDiagnosisText(caseItem?.sections, caseItem?.diagnosis) || '—' }}</div>
        <div class="mt-2 text-xs text-gray-800">
          <div class="mb-1">
            <strong>CIE-10:</strong> {{ (caseItem?.diagnosis?.cie10?.primary?.codigo || caseItem?.diagnosis?.cie10?.codigo) ?? '—' }}
            <template v-if="(caseItem?.diagnosis?.cie10?.primary?.nombre || caseItem?.diagnosis?.cie10?.nombre)">
              - {{ caseItem?.diagnosis?.cie10?.primary?.nombre || caseItem?.diagnosis?.cie10?.nombre }}
            </template>
          </div>
          <div class="mb-1">
            <strong>CIE-O:</strong> {{ caseItem?.diagnosis?.cieo?.codigo ?? '—' }}
            <template v-if="caseItem?.diagnosis?.cieo?.nombre"> - {{ caseItem.diagnosis.cieo.nombre }}</template>
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
    method?: string
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
}>()

function buildSamplesDescription(list: any[] | undefined): string {
  if (!list || list.length === 0) return '—'
  return list.map(it => `${it.region_cuerpo}: ${it.pruebas?.map((p: any) => {
    if (p.id === p.nombre) {
      return p.id
    }
    return `${p.id} - ${p.nombre}`
  }).join(', ')}`).join(' | ')
}

function getDiagnosisText(
  sec?: { diagnosis?: string } | null,
  diag?: { formatted?: string } | null
): string {
  const formatted = (diag?.formatted ?? '').toString().trim()
  if (formatted) return formatted
  const free = (sec?.diagnosis ?? '').toString().trim()
  return free
}
</script>

<style scoped>
.report-content {
  margin-bottom: 1rem;
}

.report-content > div {
  margin-bottom: 0.75rem;
}

.report-content h3 {
  margin-bottom: 0.25rem;
  font-weight: 600;
  font-size: 0.875rem;
}
</style>
