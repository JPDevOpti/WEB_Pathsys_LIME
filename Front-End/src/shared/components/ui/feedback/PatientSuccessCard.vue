<template>
  <transition name="fade-scale">
    <div 
      v-if="visible" 
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="$emit('close')"
    >
  <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] overflow-y-auto">
        <!-- Close button absolute -->
        <button
          @click="$emit('close')"
          class="absolute top-4 right-4 z-10 p-2 rounded-lg bg-white/90 hover:bg-white transition-all duration-200 text-gray-600 hover:text-gray-800 ring-1 ring-transparent hover:ring-gray-200 hover:scale-105"
          title="Cerrar"
        >
          <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
          </svg>
        </button>
        
        <div class="relative">
          <!-- Header -->
          <div class="px-4 py-4 pr-12 border-b border-gray-200">
            <div class="flex items-center space-x-3">
              <div class="flex-shrink-0">
                <div class="w-10 h-10 bg-green-50 rounded-full flex items-center justify-center">
                  <svg class="w-5 h-5 text-green-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                </div>
              </div>
              <div>
                <h3 class="text-lg font-bold text-gray-900">Paciente Registrado Exitosamente</h3>
                <p class="text-gray-600 text-xs mt-1">El paciente ha sido ingresado al sistema</p>
              </div>
            </div>
          </div>

          <!-- Contenido -->
          <div class="p-4 space-y-4">
            <!-- Información Principal -->
            <div class="bg-white rounded-lg p-3 border border-gray-200">
              <div class="mb-3 pb-3 border-b border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Nombre del Paciente</p>
                    <h4 class="text-lg font-semibold text-gray-900">{{ displayName }}</h4>
                  </div>
                  <div class="flex items-center space-x-2 bg-gray-100 px-2 py-1 rounded-full">
                    <div class="w-1.5 h-1.5 bg-green-500 rounded-full"></div>
                    <span class="text-xs font-medium text-gray-700">Activo</span>
                  </div>
                </div>
              </div>

              <div class="grid grid-cols-2 gap-3">
                <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V8a2 2 0 00-2-2h-5m-4 0V5a2 2 0 114 0v1m-4 0a2 2 0 104 0m-5 8a2 2 0 100-4 2 2 0 000 4zm0 0c1.306 0 2.417.835 2.83 2M9 14a3.001 3.001 0 00-2.83 2M15 11h3m-3 4h2" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Documento</p>
                      <p class="text-sm font-bold text-gray-900 font-mono">{{ documentDisplay }}</p>
                    </div>
                  </div>
                </div>

                <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7V3m8 4V3m-9 8h10M5 21h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v12a2 2 0 002 2z" />
                        </svg>
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Edad</p>
                      <p class="text-sm font-bold text-gray-900">{{ computedAge }} años</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Género y Tipo de Atención -->
              <div class="grid grid-cols-2 gap-3 mt-3">
                <div v-if="patientGender" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <GerdenIcon size="16" color="#374151" />
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Género</p>
                      <p class="text-sm font-bold text-gray-900">{{ patientGender }}</p>
                    </div>
                  </div>
                </div>

                <div v-if="patientCareType" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <AtentionTypeIcon size="16" color="#374151" />
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Atención</p>
                      <p class="text-sm font-bold text-gray-900">{{ patientCareType }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Entidad -->
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <EntityIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad de Salud</p>
                  <p class="text-sm font-semibold text-gray-900">{{ patientData.entity_info?.name || patientData.entity }}</p>
                  <p v-if="patientData.entity_info?.id || patientData.entityCode" class="text-xs text-gray-600 font-mono mt-1">
                    Código: {{ patientData.entity_info?.id || patientData.entityCode }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Información de Ubicación -->
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-start space-x-2 mb-3">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z" />
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-2">Información de Ubicación</p>
                  
                  <div class="grid grid-cols-2 gap-1">
                    <!-- Municipio (Izquierda) -->
                    <div v-if="locationMunicipality" class="space-y-1 flex flex-col justify-center">
                      <p class="text-xs text-gray-500 font-medium">Municipio</p>
                      <p class="text-sm font-semibold text-gray-900">{{ locationMunicipality }}</p>
                      <p v-if="locationMunicipalityCode" class="text-xs text-gray-600 font-mono">
                        Código: {{ locationMunicipalityCode }}
                      </p>
                    </div>
                    
                    <!-- Subregión y Dirección (Derecha) -->
                    <div class="space-y-2">
                      <!-- Subregión (Arriba) -->
                      <div v-if="locationSubregion">
                        <p class="text-xs text-gray-500 font-medium">Subregión</p>
                        <p class="text-sm font-semibold text-gray-900">{{ locationSubregion }}</p>
                      </div>
                      
                      <!-- Dirección (Abajo) -->
                      <div v-if="locationAddress">
                        <p class="text-xs text-gray-500 font-medium">Dirección</p>
                        <p class="text-sm font-semibold text-gray-900">{{ locationAddress }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Observaciones (si existen) -->
            <div v-if="patientData.observations" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M7 8h10M7 12h4m1 8l-4-4H5a2 2 0 01-2-2V6a2 2 0 012-2h14a2 2 0 012 2v8a2 2 0 01-2 2h-3l-4 4z" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Observaciones</p>
                  <p class="text-xs text-gray-700 leading-relaxed">{{ patientData.observations }}</p>
                </div>
              </div>
            </div>

            <!-- Footer con timestamp y acciones -->
            <div class="flex items-center justify-between pt-3 border-t border-gray-200">
              <div class="flex flex-col space-y-1 text-xs text-gray-500">
                <div class="flex items-center space-x-2">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                  </svg>
                  <span>Registrado el {{ createdAtFormatted }}</span>
                </div>
                <div v-if="updatedAtFormatted" class="flex items-center space-x-2">
                  <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M4 4v5h.582m15.356 2A8.001 8.001 0 004.582 9m0 0H9m11 11v-5h-.581m0 0a8.003 8.003 0 01-15.357-2m15.357 2H15" />
                  </svg>
                  <span>Actualizado el {{ updatedAtFormatted }}</span>
                </div>
              </div>
              <button
                @click="handleCreateCase"
                class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-green-500 text-green-500 bg-white hover:bg-green-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-offset-2"
              >
                Crear Caso
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>
</template>

<script setup lang="ts">
import { computed, onMounted } from 'vue'
import { useRouter } from 'vue-router'
import { useSidebar } from '@/shared/composables/SidebarControl'
import { IDENTIFICATION_TYPE_NAMES, IdentificationType } from '@/modules/patients/types'
import EntityIcon from '@/assets/icons/EntityIcon.vue'
import GerdenIcon from '@/assets/icons/GerdenIcon.vue'
import AtentionTypeIcon from '@/assets/icons/AtentionTypeIcon.vue'

interface PatientData {
  name?: string
  patient_code?: string
  patientCode?: string
  identification_type?: number | string
  identification_number?: string
  first_name?: string
  second_name?: string
  first_lastname?: string
  second_lastname?: string
  birth_date?: string
  age?: number | string
  gender?: string
  location?: {
    municipality_code?: string
    municipality_name?: string
    subregion?: string
    address?: string
  }
  municipality_code?: string
  municipality_name?: string
  subregion?: string
  address?: string
  entity_info?: {
    id?: string
    name?: string
  }
  entity?: string
  entityCode?: string
  care_type?: string
  careType?: string
  observations?: string
  created_at?: string
  fecha_creacion?: string
}

interface Props {
  visible: boolean
  patientData: PatientData
  closeOnEsc?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  closeOnEsc: true
})

const emit = defineEmits<{ (e: 'close'): void }>()

const router = useRouter()
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const formatDateTime = (date: Date) => {
  return date.toLocaleString('es-ES', {
    day: '2-digit',
    month: 'long',
    year: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

// Mapeo seguro para códigos string (compatibilidad con listas)
const IDENTIFICATION_CODE_LABELS: Record<string, string> = {
  CC: 'Cédula de Ciudadanía',
  CE: 'Cédula de Extranjería',
  TI: 'Tarjeta de Identidad',
  PA: 'Pasaporte',
  RC: 'Registro Civil',
  NIT: 'NIT'
}

const getIdentificationTypeLabel = (value: unknown): string => {
  if (typeof value === 'number') {
    return IDENTIFICATION_TYPE_NAMES[value as IdentificationType] ?? String(value)
  }
  if (typeof value === 'string') {
    return IDENTIFICATION_CODE_LABELS[value] ?? value
  }
  return ''
}

// Display helpers
const displayName = computed(() => {
  const p: any = props.patientData || {}
  if (p.name) return p.name
  const parts = [p.first_name, p.second_name, p.first_lastname, p.second_lastname].filter(Boolean)
  return parts.join(' ').trim() || 'Sin nombre'
})

const documentDisplay = computed(() => {
  const p: any = props.patientData || {}
  const typeLabel = getIdentificationTypeLabel(p.identification_type)
  const number = p.identification_number || ''
  return [typeLabel, number].filter(Boolean).join(' - ')
})

const computedAge = computed(() => {
  const p: any = props.patientData || {}
  if (typeof p.age === 'number') return p.age
  const birth: string | undefined = p.birth_date
  if (!birth) return ''
  const dob = new Date(birth)
  if (isNaN(dob.getTime())) return ''
  const today = new Date()
  let age = today.getFullYear() - dob.getFullYear()
  const m = today.getMonth() - dob.getMonth()
  if (m < 0 || (m === 0 && today.getDate() < dob.getDate())) age--
  return age
})

const createdAtFormatted = computed(() => {
  const p: any = props.patientData || {}
  const dt = p.created_at || p.fecha_creacion || new Date().toISOString()
  const d = new Date(dt)
  return formatDateTime(isNaN(d.getTime()) ? new Date() : d)
})

// Location computed properties
const locationAddress = computed(() => {
  const p: any = props.patientData || {}
  return p.location?.address || p.address || ''
})

const locationMunicipality = computed(() => {
  const p: any = props.patientData || {}
  return p.location?.municipality_name || p.municipality_name || ''
})

const locationMunicipalityCode = computed(() => {
  const p: any = props.patientData || {}
  return p.location?.municipality_code || p.municipality_code || ''
})

const locationSubregion = computed(() => {
  const p: any = props.patientData || {}
  return p.location?.subregion || p.subregion || ''
})

const patientGender = computed(() => {
  const p: any = props.patientData || {}
  return p.gender || p.genero || ''
})

const patientCareType = computed(() => {
  const p: any = props.patientData || {}
  return p.care_type || p.tipo_atencion || ''
})

const updatedAtFormatted = computed(() => {
  const p: any = props.patientData || {}
  const dt = p.updated_at || p.fecha_actualizacion
  if (!dt) return ''
  const d = new Date(dt)
  return formatDateTime(isNaN(d.getTime()) ? new Date() : d)
})

const handleCreateCase = () => {
  emit('close')
  router.push('/cases/new')
}

function onKey(e: KeyboardEvent) {
  if (!props.visible) return
  if (e.key === 'Escape' && props.closeOnEsc) {
    emit('close')
  }
}

onMounted(() => {
  window.addEventListener('keydown', onKey)
})
</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>
