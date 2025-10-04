<template>
  <div class="border rounded-lg p-4 shadow-sm" :class="caseInfo ? 'bg-white border-gray-200' : 'bg-gray-50 border-gray-200'">
    <!-- Header -->
    <div class="flex items-center mb-3 pb-3" :class="caseInfo ? 'border-b border-gray-200' : 'border-b border-gray-200'">
      <svg class="w-5 h-5 mr-2 flex-shrink-0" :class="caseInfo ? 'text-blue-600' : 'text-gray-400'" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
      <h4 class="text-sm font-semibold" :class="caseInfo ? 'text-gray-800' : 'text-gray-600'">Detalles del Caso</h4>
    </div>
    
    <!-- Scrollable content -->
    <div v-if="caseInfo" class="overflow-y-auto space-y-4 custom-scrollbar" style="max-height: 600px;">
      <!-- Basic case info -->
      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
        <div>
          <span class="font-medium text-gray-600">Código:</span>
          <p class="text-gray-900 font-mono font-semibold">{{ caseCode }}</p>
        </div>
        <div>
          <span class="font-medium text-gray-600">Estado:</span>
          <p class="text-gray-900 font-semibold">{{ caseState }}</p>
        </div>
        <div class="sm:col-span-2">
          <span class="font-medium text-gray-600">Paciente:</span>
          <p class="text-gray-900 font-semibold break-words">{{ patientName }}</p>
        </div>
        <div>
          <span class="font-medium text-gray-600">Documento:</span>
          <p class="text-gray-900 font-mono">{{ patientDocument }}</p>
        </div>
        <div>
          <span class="font-medium text-gray-600">Entidad:</span>
          <p class="text-gray-900 break-words">{{ entityName }}</p>
        </div>
        <div class="sm:col-span-2">
          <span class="font-medium text-gray-600">Patólogo Actual:</span>
          <p class="text-gray-900 font-semibold break-words">{{ currentPathologist }}</p>
        </div>
      </div>

      <!-- Case metadata -->
      <div v-if="metaInfo.length" class="space-y-2">
        <h5 class="text-xs font-semibold uppercase tracking-wide text-gray-700 border-b border-gray-200 pb-1">Información Adicional</h5>
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-2">
          <div v-for="item in metaInfo" :key="item.label" class="bg-gray-50 border border-gray-200 rounded-md p-2 shadow-sm">
            <span class="block text-xs font-medium uppercase tracking-wide text-gray-600">{{ item.label }}</span>
            <p class="mt-0.5 text-sm text-gray-900 font-semibold break-words">{{ item.value }}</p>
          </div>
        </div>
      </div>

      <!-- Samples -->
      <div v-if="samples.length" class="space-y-2">
        <h5 class="text-xs font-semibold uppercase tracking-wide text-gray-700 border-b border-gray-200 pb-1">Muestras ({{ samples.length }})</h5>
        <div class="space-y-2">
          <div v-for="sample in samples" :key="sample.key" class="bg-blue-50 border border-blue-200 rounded-md p-3 shadow-sm">
            <div class="flex flex-wrap items-center justify-between gap-2 mb-2">
              <span class="text-sm font-semibold text-blue-700">{{ sample.region }}</span>
              <span v-if="sample.totalTests" class="inline-flex items-center px-2 py-0.5 rounded-full bg-blue-100 text-blue-700 text-xs font-medium">
                {{ sample.totalTests }} prueba{{ sample.totalTests === 1 ? '' : 's' }}
              </span>
            </div>
            <ul v-if="sample.tests.length" class="space-y-1">
              <li v-for="test in sample.tests" :key="test.key" class="flex items-center justify-between text-xs text-blue-900 bg-white border border-blue-100 rounded px-2 py-1">
                <span class="font-medium">{{ test.name }}</span>
                <span v-if="test.quantity" class="font-semibold">x{{ test.quantity }}</span>
              </li>
            </ul>
            <p v-else class="text-xs text-blue-700">Sin pruebas registradas</p>
          </div>
        </div>
      </div>

      <!-- Observations -->
      <div v-if="observations" class="space-y-1">
        <h5 class="text-xs font-semibold uppercase tracking-wide text-gray-700 border-b border-gray-200 pb-1">Observaciones</h5>
        <div class="bg-gray-50 border border-gray-200 rounded-md p-3">
          <p class="text-sm text-gray-900 whitespace-pre-line">{{ observations }}</p>
        </div>
      </div>
    </div>

    <!-- Empty state when no case -->
    <div v-else class="flex items-center justify-center py-12 text-gray-400">
      <div class="text-center">
        <svg class="w-16 h-16 mx-auto mb-3 opacity-40" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
        </svg>
        <p class="text-sm font-medium text-gray-500">No hay caso seleccionado</p>
        <p class="text-xs text-gray-400 mt-1">Busque un caso para ver sus detalles</p>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import type { CaseModel } from '../types'

interface Props {
  caseInfo: CaseModel | null
  caseState?: string
  currentPathologist?: string
}

const props = defineProps<Props>()

// Computed properties for case info
const caseCode = computed(() => {
  if (!props.caseInfo) return 'N/A'
  return (props.caseInfo as any).case_code || (props.caseInfo as any).caso_code || 'N/A'
})

const patientName = computed(() => {
  if (!props.caseInfo) return 'N/A'
  return props.caseInfo.patient_info?.name || 'N/A'
})

const patientDocument = computed(() => {
  if (!props.caseInfo) return 'N/A'
  return props.caseInfo.patient_info?.patient_code || 'N/A'
})

const entityName = computed(() => {
  if (!props.caseInfo) return 'N/A'
  return (props.caseInfo as any).patient_info?.entity_info?.name || 
         (props.caseInfo as any).patient_info?.entity_info?.nombre || 'N/A'
})

const metaInfo = computed(() => {
  if (!props.caseInfo) return []
  const info = props.caseInfo as any
  const meta = [
    { label: 'Prioridad', value: info.priority || info.prioridad },
    { label: 'Servicio', value: info.service || info.servicio },
    { label: 'Médico Solicitante', value: info.requesting_physician || info.medico_solicitante },
    { label: 'Tipo de Atención', value: info.care_type || info.tipo_atencion || info.patient_info?.care_type },
    { label: 'Fecha de Creación', value: formatDateDisplay(info.created_at || info.fecha_creacion) },
    { label: 'Última Actualización', value: formatDateDisplay(info.updated_at || info.fecha_actualizacion) }
  ]

  return meta
    .filter(item => item.value)
    .map(item => ({ label: item.label, value: String(item.value) }))
})

const samples = computed(() => {
  if (!props.caseInfo) return []
  const samplesData = (props.caseInfo as any).samples || []
  if (!Array.isArray(samplesData)) return []

  return samplesData.map((sample: any, sampleIndex: number) => {
    const testsRaw = Array.isArray(sample.tests) ? sample.tests : Array.isArray(sample.pruebas) ? sample.pruebas : []
    const tests = testsRaw.map((test: any, testIndex: number) => ({
      key: test.id || test._id || `${sampleIndex}-${testIndex}`,
      name: test.name || test.nombre || test.test || 'Prueba sin nombre',
      quantity: typeof test.quantity === 'number' ? test.quantity : typeof test.cantidad === 'number' ? test.cantidad : null
    }))

    return {
      key: sample.id || sample._id || `${sample.body_region || sample.region_cuerpo || 'sample'}-${sampleIndex}`,
      region: sample.body_region || sample.region_cuerpo || `Muestra ${sampleIndex + 1}`,
      tests,
      totalTests: tests.length
    }
  })
})

const observations = computed(() => {
  if (!props.caseInfo) return ''
  const info = props.caseInfo as any
  return info.observations || info.observaciones || info.additional_notes || ''
})

function formatDateDisplay(value: string | undefined) {
  if (!value) return ''
  const date = new Date(value)
  if (Number.isNaN(date.getTime())) return value
  return date.toLocaleDateString('es-CO', { year: 'numeric', month: 'short', day: 'numeric' })
}
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: rgba(59, 130, 246, 0.3) transparent;
}

.custom-scrollbar::-webkit-scrollbar {
  width: 6px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: transparent;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: rgba(59, 130, 246, 0.3);
  border-radius: 3px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: rgba(59, 130, 246, 0.5);
}
</style>
