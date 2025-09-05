<template>
  <div class="case-report-container">
    <div class="report-page first-page">
      <!-- Encabezado -->
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
              <div><span class="font-semibold">Informe No:</span> {{ caseData.caseDetails?.CasoCode || caseData.sampleId
                || '—' }}</div>
              <div><span class="font-semibold">Fecha de Recibo:</span> {{
                formatDate(caseData.caseDetails?.fecha_creacion) || '—' }}</div>
              <div><span class="font-semibold">Fecha de Informe:</span> {{ formatDate(caseData.generatedAt || new
                Date().toISOString()) }}</div>
            </td>
          </tr>
        </table>
      </div>

      <!-- Información del paciente -->
      <div class="patient-info text-xs space-y-0.5 mb-4">
        <div><strong>Documento de identidad:</strong> {{ caseData.patient?.document ||
          caseData.caseDetails?.paciente?.cedula || '—' }}</div>
        <div><strong>Paciente:</strong> {{ caseData.patient?.fullName || caseData.caseDetails?.paciente?.nombre || '—'
        }}</div>
        <div>
          <strong>Edad:</strong> {{ caseData.caseDetails?.paciente?.edad ?? '—' }}
          <span class="ml-4"><strong>Sexo:</strong> {{ caseData.caseDetails?.paciente?.sexo || '—' }}</span>
        </div>
        <div>
          <strong>Institución:</strong> {{ caseData.caseDetails?.entidad_info?.nombre || caseData.patient?.entity || '—'
          }}
          <span class="ml-4"><strong>Servicio:</strong> {{ caseData.caseDetails?.servicio || '—' }}</span>
          <span class="ml-4"><strong>Recibido N°:</strong> {{ recibidoNumero(caseData.caseDetails?.CasoCode ||
            caseData.sampleId) || '—' }}</span>
        </div>
        <div><strong>Médico Solicitante:</strong> {{ caseData.caseDetails?.medico_solicitante?.nombre || '—' }}</div>
      </div>

      <!-- Contenido del informe -->
      <div class="report-content text-xs space-y-3">
        <div class="section-muestra">
          <h3 class="font-semibold mb-1 text-sm">MUESTRA:</h3>
          <div class="whitespace-pre-wrap">{{ buildSamplesDescription(caseData.caseDetails?.muestras) }}</div>
        </div>

        <div class="section-macro">
          <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MACROSCÓPICA</h3>
          <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseData.sections?.macro || '—' }}</div>
        </div>

        <div class="section-micro">
          <h3 class="font-semibold mb-1 text-sm">DESCRIPCIÓN MICROSCÓPICA</h3>
          <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseData.sections?.micro || '—' }}</div>
        </div>

        <div class="section-metodo">
          <h3 class="font-semibold mb-1 text-sm">MÉTODO UTILIZADO</h3>
          <div class="whitespace-pre-wrap break-words overflow-hidden">{{ caseData.sections?.method || '—' }}</div>
        </div>

        <div class="section-diagnostico">
          <h3 class="font-semibold mb-1 text-sm">DIAGNÓSTICO</h3>
          <div class="whitespace-pre-wrap mt-1 pt-1">
            <div>{{ getDiagnosisText(caseData.sections, caseData.diagnosis) || '—' }}</div>
            <div class="mt-2 text-xs text-gray-800">
              <div class="mb-1">
                <strong>CIE-10:</strong> {{ (caseData.diagnosis?.cie10?.primary?.codigo ||
                  caseData.diagnosis?.cie10?.codigo) ?? '—' }}
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

      <!-- Pie -->
      <div class="report-footer">
        <div class="signature-section">
          <div class="border-t border-gray-400 w-2/3 mx-auto mb-1"></div>
          <div class="text-center text-xs">Médico Patólogo: {{ caseData.caseDetails?.patologo_asignado?.nombre || '—' }}
          </div>
        </div>
        <div class="footer-section text-center text-xs text-gray-700 mt-2 pt-2">
          <div>Los informes de resultados, las placas y bloques de estudios anatomopatológicos se archivan por 15 años
          </div>
          <div class="my-1 leading-none">
            ___________________________________________________________________________________________</div>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
interface CaseData {
  sampleId: string
  patient: any
  caseDetails: any
  sections: { method: string; macro: string; micro: string; diagnosis: string }
  diagnosis?: { cie10?: { codigo?: string, nombre?: string, primary?: any }, cieo?: { codigo?: string, nombre?: string, primary?: any }, formatted?: string }
  generatedAt: string
}

defineProps<{ caseData: CaseData }>()

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
  const formatted = (diag?.formatted ?? '').toString().trim()
  if (formatted) return formatted
  const free = (sec?.diagnosis ?? '').toString().trim()
  return free
}
</script>

<style scoped>
/* Estilos para imágenes de firma */
.signature-section img {
  background: transparent !important;
  mix-blend-mode: multiply;
}

@media print {
  .signature-section img {
    background: transparent !important;
    mix-blend-mode: multiply !important;
    -webkit-print-color-adjust: exact !important;
    color-adjust: exact !important;
  }
}
</style>
