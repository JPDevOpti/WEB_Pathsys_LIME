<template>
  <transition name="fade-scale">
    <div
      v-if="visible"
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="emit('close')"
    >
      <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
        <button
          @click="emit('close')"
          class="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white/90 hover:bg-white transition-all duration-200 text-gray-600 hover:text-gray-800 ring-1 ring-transparent hover:ring-gray-200 hover:scale-105"
          title="Cerrar"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>

        <div class="relative flex h-full flex-col overflow-y-auto">
          <div class="px-6 py-6 pr-16 border-b border-gray-200 shrink-0 sticky top-0 bg-white z-10">
            <div class="flex items-center space-x-4">
              <div class="flex-shrink-0">
                <div class="w-14 h-14 bg-green-50 rounded-full flex items-center justify-center">
                  <CaseIcon class="w-7 h-7 text-green-600" />
                </div>
              </div>
              <div>
                <h3 class="text-xl font-bold text-gray-900">{{ successTitle }}</h3>
                <p class="text-gray-600 text-sm mt-1">{{ successMessage }}</p>
              </div>
            </div>
          </div>

          <div class="flex-1">
            <div class="p-6 space-y-6">
              <div class="bg-white rounded-lg p-5 border border-gray-200 space-y-4">
                <div class="flex flex-col md:flex-row md:items-center md:justify-between gap-3 pb-4 border-b border-gray-200">
                  <div>
                    <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Código del Caso</p>
                    <div class="flex items-center flex-wrap gap-2">
                      <h4 class="text-2xl font-semibold text-gray-900 font-mono break-all">{{ caseCode || 'Sin código' }}</h4>
                      <button
                        v-if="caseCode"
                        type="button"
                        @click="copyCaseCode"
                        class="inline-flex items-center px-3 py-1.5 rounded-md border border-gray-200 text-xs font-semibold text-gray-600 hover:bg-gray-100 hover:text-gray-800 transition-colors duration-150"
                      >
                        <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z" />
                        </svg>
                        <span>{{ copied ? 'Copiado' : 'Copiar ' }}</span>
                      </button>
                    </div>
                    <p class="text-sm text-gray-600 mt-2">
                      Paciente: <span class="font-semibold text-gray-900">{{ patientName }}</span>
                    </p>
                  </div>
                  <div class="flex flex-wrap gap-2">
                    <span
                      v-if="caseState"
                      class="inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold bg-blue-50 text-blue-700 border border-blue-100"
                    >
                      Estado: {{ caseState }}
                    </span>
                    <span
                      v-if="casePriority"
                      :class="['inline-flex items-center px-3 py-1 rounded-full text-xs font-semibold border', priorityBadgeClasses]"
                    >
                      Prioridad: {{ casePriority }}
                    </span>
                  </div>
                </div>

                <div class="grid grid-cols-1 sm:grid-cols-2 gap-4">
                  <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento del Paciente</p>
                        <p class="text-lg font-bold text-gray-900 font-mono">{{ patientDocument || '—' }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Edad</p>
                        <p class="text-lg font-bold text-gray-900">{{ patientAge ? `${patientAge} años` : '—' }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Sexo</p>
                        <p class="text-lg font-bold text-gray-900 capitalize">{{ patientGender || '—' }}</p>
                      </div>
                    </div>
                  </div>

                  <div class="bg-gray-50 rounded-lg p-4 border border-gray-200">
                    <div class="flex items-center space-x-3">
                      <div class="flex-shrink-0">
                        <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                          <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 21V5a2 2 0 00-2-2H7a2 2 0 00-2 2v16m14 0h2m-2 0h-5m-9 0H3m2 0h5M9 7h1m-1 4h1m4-4h1m-1 4h1m-5 10v-5a1 1 0 011-1h2a1 1 0 011 1v5m-4 0h4" />
                          </svg>
                        </div>
                      </div>
                      <div class="flex-1 min-w-0">
                        <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Tipo de Atención</p>
                        <p class="text-lg font-bold text-gray-900 capitalize">{{ patientCareType || '—' }}</p>
                      </div>
                    </div>
                  </div>
                </div>

                <div class="bg-gray-50 rounded-lg p-5 border border-gray-200">
                  <div class="flex items-start space-x-3">
                    <div class="flex-shrink-0">
                      <div class="w-12 h-12 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <EntityIcon class="w-6 h-6 text-gray-700" />
                      </div>
                    </div>
                    <div class="flex-1">
                      <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad Responsable</p>
                      <p class="text-lg font-semibold text-gray-900">{{ entityName || 'No especificada' }}</p>
                      <p v-if="entityCode" class="text-sm text-gray-600 font-mono mt-1">
                        Código: {{ entityCode }}
                      </p>
                    </div>
                  </div>
                </div>
              </div>

              <div v-if="normalizedSamples.length" class="bg-white rounded-lg border border-gray-200">
                <div class="px-5 py-4 border-b border-gray-200 flex items-center space-x-2">
                  <SampleIcon class="w-5 h-5 text-blue-600" />
                  <h4 class="text-sm font-semibold text-gray-800">Submuestras registradas</h4>
                  <span class="ml-auto inline-flex items-center px-3 py-0.5 rounded-full text-xs font-medium bg-blue-50 text-blue-700">
                    {{ normalizedSamples.length }} submuestra{{ normalizedSamples.length !== 1 ? 's' : '' }}
                  </span>
                </div>
                <div class="divide-y divide-gray-200">
                  <div v-for="sample in normalizedSamples" :key="sample.number" class="px-5 py-4">
                    <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                      <div>
                        <p class="text-sm font-semibold text-gray-900">{{ sample.label }}</p>
                        <p class="text-xs text-gray-500 mt-0.5 uppercase tracking-wide">Región: {{ sample.bodyRegion || 'Sin especificar' }}</p>
                      </div>
                      <div class="flex items-center space-x-2 text-xs text-gray-500">
                        <span class="inline-flex items-center px-2 py-0.5 rounded-full bg-gray-100 text-gray-700 border border-gray-200">
                          {{ sample.tests.length }} prueba{{ sample.tests.length !== 1 ? 's' : '' }}
                        </span>
                      </div>
                    </div>
                    <ul v-if="sample.tests.length" class="mt-3 space-y-1">
                      <li
                        v-for="(test, index) in sample.tests"
                        :key="index"
                        class="flex items-center text-sm text-gray-700"
                      >
                        <span class="w-1.5 h-1.5 bg-green-500 rounded-full mr-2"></span>
                        <span class="flex-1 truncate">
                          {{ (test.code || test.codigo || test.cod || test.id || '—') + ' - ' + (test.name || test.nombre || test.descripcion || 'Prueba sin nombre') }}
                        </span>
                        <span class="text-xs text-gray-500 ml-3">x{{ test.quantity || test.cantidad || 1 }}</span>
                      </li>
                    </ul>
                    <p v-else class="mt-3 text-sm text-gray-500">Sin pruebas registradas</p>
                  </div>
                </div>
              </div>

              <div v-if="observations" class="bg-gray-50 rounded-lg p-5 border border-gray-200">
                <div class="flex items-start space-x-3">
                  <div class="flex-shrink-0">
                    <div class="w-10 h-10 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                      <svg class="w-5 h-5 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                      </svg>
                    </div>
                  </div>
                  <div class="flex-1">
                    <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-2">Observaciones</p>
                    <p class="text-sm text-gray-700 leading-relaxed">{{ observations }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
          <div class="px-6 py-4 border-t border-gray-200 bg-white shrink-0 sticky bottom-0 z-10">
              <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-3">
                <div class="flex items-center space-x-2 text-sm text-gray-500">
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Creado el {{ formattedCreatedAt }}</span>
              </div>
                <div class="flex flex-col sm:flex-row sm:items-center gap-2">
                  <button
                    class="inline-flex items-center justify-center px-4 py-2 rounded-lg text-sm font-semibold border border-green-500 text-green-500 bg-white hover:bg-green-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
                    @click="handleGoToCases"
                  >
                    Listado de casos
                  </button>
                  <button
                    class="inline-flex items-center justify-center px-4 py-2 rounded-lg text-sm font-semibold border border-red-500 text-red-500 bg-white hover:bg-red-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-red-500 focus:ring-offset-2"
                    @click="emit('close')"
                  >
                    Cerrar
                  </button>
                </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, onMounted, onBeforeUnmount, ref, watch } from 'vue'
import { useRouter } from 'vue-router'
import { useSidebar } from '@/shared/composables/SidebarControl'
import CaseIcon from '@/assets/icons/CaseIcon.vue'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import SampleIcon from '@/assets/icons/SampleIcon.vue'

interface CasePatientData {
  name?: string
  nombre?: string
  patient_code?: string
  patientCode?: string
  age?: number | string
  edad?: number | string
  gender?: string
  genero?: string
  sexo?: string
  care_type?: string
  careType?: string
  tipoAtencion?: string
  entity?: string
  entityCode?: string
  entity_code?: string
  entity_info?: {
    id?: string
    name?: string
  }
}

interface CaseSampleData {
  number?: number
  numero?: number
  label?: string
  title?: string
  bodyRegion?: string
  region?: string
  regionCuerpo?: string
  body_region?: string
  tests?: any[]
  pruebas?: any[]
}

interface CaseData {
  code?: string
  case_code?: string
  caseCode?: string
  codigo?: string
  id?: string
  uuid?: string
  state?: string
  estado?: string
  priority?: string
  prioridad?: string
  created_at?: string | Date
  createdAt?: string | Date
  created?: string | Date
  fecha_creacion?: string | Date
  observations?: string
  observaciones?: string
  entity?: string
  entity_name?: string
  entityCode?: string
  entity_code?: string
  entity_info?: {
    id?: string
    name?: string
  }
  patient?: CasePatientData
  paciente?: CasePatientData
  patient_info?: CasePatientData
  samples?: CaseSampleData[]
  muestras?: CaseSampleData[]
}

interface Props {
  visible: boolean
  caseData: CaseData
  closeOnEsc?: boolean
  mode?: 'created' | 'updated'
}

const props = withDefaults(defineProps<Props>(), {
  closeOnEsc: true,
  mode: 'created'
})

const emit = defineEmits<{ (e: 'close'): void }>()

const router = useRouter()
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const successTitle = computed(() => {
  return props.mode === 'created' ? 'Caso creado exitosamente' : 'Caso actualizado exitosamente'
})

const successMessage = computed(() => {
  return props.mode === 'created' 
    ? 'El caso ha sido registrado en el sistema' 
    : 'Los cambios han sido guardados correctamente'
})

const activePatient = computed<CasePatientData>(() => props.caseData.patient || props.caseData.paciente || props.caseData.patient_info || {})

const caseCode = computed(() =>
  props.caseData.code ||
  props.caseData.case_code ||
  props.caseData.caseCode ||
  props.caseData.codigo ||
  props.caseData.id ||
  props.caseData.uuid ||
  ''
)

const copied = ref(false)
let copyResetTimeout: ReturnType<typeof setTimeout> | undefined

const copyCaseCode = async () => {
  const code = caseCode.value
  if (!code) return

  const fallbackCopy = () => {
    const textarea = document.createElement('textarea')
    textarea.value = code
    textarea.setAttribute('readonly', '')
    textarea.style.position = 'absolute'
    textarea.style.left = '-9999px'
    document.body.appendChild(textarea)
    textarea.select()
    try { document.execCommand('copy') } catch {}
    document.body.removeChild(textarea)
  }

  try {
    await navigator.clipboard.writeText(code)
  } catch {
    fallbackCopy()
  }

  copied.value = true
  if (copyResetTimeout) clearTimeout(copyResetTimeout)
  copyResetTimeout = setTimeout(() => { copied.value = false }, 2000)
}

watch(caseCode, () => {
  copied.value = false
  if (copyResetTimeout) {
    clearTimeout(copyResetTimeout)
    copyResetTimeout = undefined
  }
})

const caseState = computed(() => translateCaseState(props.caseData.state || props.caseData.estado))
const casePriority = computed(() => translateCasePriority(props.caseData.priority || props.caseData.prioridad))

const patientName = computed(() => activePatient.value.name || activePatient.value.nombre || 'No registrado')
const patientDocument = computed(() =>
  activePatient.value.patient_code ||
  activePatient.value.patientCode ||
  props.caseData.case_code ||
  props.caseData.caseCode ||
  ''
)
function computeAgeFrom(dateInput?: string | Date | null): number | '' {
  if (!dateInput) return ''
  const d = typeof dateInput === 'string' || dateInput instanceof Date ? new Date(dateInput) : null
  if (!d || Number.isNaN(d.getTime())) return ''
  const today = new Date()
  let age = today.getFullYear() - d.getFullYear()
  const m = today.getMonth() - d.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < d.getDate())) age--
  return age >= 0 ? age : ''
}

const patientAge = computed(() => {
  const direct = activePatient.value.age || activePatient.value.edad
  if (direct !== undefined && direct !== null && direct !== '') return direct
  const dob =
    (activePatient.value as any).birthDate ||
    (activePatient.value as any).birth_date ||
    (activePatient.value as any).fecha_nacimiento ||
    (activePatient.value as any).fechaNacimiento ||
    (props.caseData as any).birthDate ||
    (props.caseData as any).birth_date ||
    (props.caseData as any).fecha_nacimiento ||
    (props.caseData as any).fechaNacimiento
  return computeAgeFrom(dob)
})
const patientGender = computed(() => normalizeGender(activePatient.value.gender || activePatient.value.genero || activePatient.value.sexo))
const patientCareType = computed(() => normalizeCareType(activePatient.value.care_type || activePatient.value.careType || activePatient.value.tipoAtencion))

const entityCode = computed(() =>
  props.caseData.entity_info?.id ||
  activePatient.value.entityCode ||
  activePatient.value.entity_code ||
  activePatient.value.entity_info?.id ||
  props.caseData.entityCode ||
  props.caseData.entity_code ||
  ''
)

const entityName = computed(() => {
  const nameCandidate =
    props.caseData.entity_info?.name ||
    activePatient.value.entity ||
    props.caseData.entity ||
    props.caseData.entity_name ||
    ''
  return nameCandidate || entityCode.value || 'No especificada'
})

const samples = computed<CaseSampleData[]>(() => props.caseData.samples || props.caseData.muestras || [])

const normalizedSamples = computed(() =>
  samples.value.map((sample, index) => {
    const tests = Array.isArray(sample.tests) ? sample.tests : Array.isArray(sample.pruebas) ? sample.pruebas : []
    return {
      number: sample.number || sample.numero || index + 1,
      label: sample.label || sample.title || `Submuestra ${sample.number || sample.numero || index + 1}`,
      bodyRegion: sample.bodyRegion || sample.region || sample.regionCuerpo || sample.body_region || '',
      tests
    }
  })
)

const priorityBadgeClasses = computed(() => {
  const base = 'border-1'
  const key = (props.caseData.priority || props.caseData.prioridad || '').toString().trim().toLowerCase()
  if (key === 'normal') return `${base} bg-green-50 text-green-700 border-green-100`
  if (key === 'prioritario' || key === 'priority' || key === 'urgente' || key === 'urgent') return `${base} bg-red-50 text-red-700 border-red-100`
  return `${base} bg-gray-50 text-gray-700 border-gray-200`
})

const observations = computed(() => props.caseData.observations || props.caseData.observaciones || '')

const createdAt = computed(() => props.caseData.created_at || props.caseData.createdAt || props.caseData.created || props.caseData.fecha_creacion)

const formattedCreatedAt = computed(() => {
  if (!createdAt.value) {
    return formatDateTime(new Date())
  }
  const parsed = new Date(createdAt.value)
  if (Number.isNaN(parsed.getTime())) {
    return String(createdAt.value)
  }
  return formatDateTime(parsed)
})

function normalizeGender(value: string | undefined | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('masc') || text === 'm') return 'masculino'
  if (text.startsWith('fem') || text === 'f') return 'femenino'
  return value
}

function normalizeCareType(value: string | undefined | null) {
  if (!value) return ''
  const text = value.toString().trim().toLowerCase()
  if (text.startsWith('ambu')) return 'ambulatorio'
  if (text.startsWith('hosp')) return 'hospitalizado'
  return value
}

function translateCaseState(value: string | undefined | null) {
  if (!value) return ''
  const map: Record<string, string> = {
    pending: 'Pendiente',
    'in process': 'En proceso',
    in_process: 'En proceso',
    processing: 'En proceso',
    completed: 'Completado',
    finished: 'Completado',
    delivered: 'Entregado',
    to_deliver: 'Para entregar',
    to_sign: 'Para firma',
    signed: 'Firmado',
    cancelled: 'Cancelado',
    canceled: 'Cancelado'
  }
  const key = value.toString().trim().toLowerCase()
  return map[key] || value
}

function translateCasePriority(value: string | undefined | null) {
  if (!value) return ''
  const map: Record<string, string> = {
    normal: 'Normal',
    priority: 'Prioritario',
    prioritario: 'Prioritario',
    urgente: 'Urgente'
  }
  const key = value.toString().trim().toLowerCase()
  return map[key] || value
}

function formatDateTime(date: Date) {
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// (El botón de ver caso se removió)

const handleGoToCases = () => {
  emit('close')
  router.push('/cases')
}

function onKey(event: KeyboardEvent) {
  if (!props.visible) return
  if (event.key === 'Escape' && props.closeOnEsc) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})

onBeforeUnmount(() => {
  if (copyResetTimeout) {
    clearTimeout(copyResetTimeout)
  }
  window.removeEventListener('keydown', onKey)
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>
