<template>
  <transition name="fade-scale">
    <div 
      v-if="isVisible" 
      :class="['fixed right-0 bottom-0 z-[10000] flex items-center justify-center p-4 bg-black/40 top-16', overlayLeftClass]"
      @click.self="$emit('close')"
    >
      <div class="relative w-full max-w-3xl bg-white rounded-2xl shadow-2xl overflow-hidden max-h-[90vh] flex flex-col">
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
        
        <!-- Header fijo -->
        <div class="flex-shrink-0 px-4 py-4 pr-12 border-b border-gray-200 bg-white rounded-t-2xl">
          <div class="flex items-center space-x-3">
            <div class="flex-shrink-0">
              <div class="w-10 h-10 bg-blue-50 rounded-full flex items-center justify-center">
                <PatientsIcon class="w-5 h-5 text-blue-600" />
              </div>
            </div>
            <div>
              <h3 class="text-lg font-bold text-gray-900">Detalles del Paciente</h3>
              <p class="text-gray-600 text-xs mt-1">Información completa del paciente</p>
            </div>
          </div>
        </div>

        <!-- Contenido scrolleable -->
        <div class="flex-1 overflow-y-auto p-4 space-y-4">
            <!-- Información Principal -->
            <div class="bg-white rounded-lg p-3 border border-gray-200">
              <div class="mb-3 pb-3 border-b border-gray-200">
                <div class="flex items-center justify-between">
                  <div>
                    <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Nombre del Paciente</p>
                    <h4 class="text-lg font-semibold text-gray-900">{{ patient?.full_name }}</h4>
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
                      <p class="text-sm font-bold text-gray-900 font-mono">{{ patient?.identification_number }}</p>
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
                      <p class="text-sm font-bold text-gray-900">{{ patient?.age }} años</p>
                    </div>
                  </div>
                </div>
              </div>

              <!-- Género y Tipo de Atención -->
              <div class="grid grid-cols-2 gap-3 mt-3">
                <div v-if="patient?.gender" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <GerdenIcon size="16" color="#374151" />
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Género</p>
                      <p class="text-sm font-bold text-gray-900">{{ patient?.gender }}</p>
                    </div>
                  </div>
                </div>

                <div v-if="patient?.care_type" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
                  <div class="flex items-center space-x-2">
                    <div class="flex-shrink-0">
                      <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                        <AtentionTypeIcon size="16" color="#374151" />
                      </div>
                    </div>
                    <div class="flex-1 min-w-0">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide">Atención</p>
                      <p class="text-sm font-bold text-gray-900">{{ patient?.care_type }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Entidad -->
            <div v-if="patient?.entity_info?.name" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <EntityIcon class="w-4 h-4 text-gray-700" />
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-1">Entidad de Salud</p>
                  <p class="text-sm font-semibold text-gray-900">{{ patient?.entity_info?.name }}</p>
                  <p v-if="patient?.entity_info?.id" class="text-xs text-gray-600 font-mono mt-1">
                    Código: {{ patient?.entity_info?.id }}
                  </p>
                </div>
              </div>
            </div>

            <!-- Información de Ubicación -->
            <div v-if="patient?.location?.municipality_name || patient?.location?.subregion || patient?.location?.address" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
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
                    <div v-if="patient?.location?.municipality_name" class="space-y-1 flex flex-col justify-center">
                      <p class="text-xs text-gray-500 font-medium">Municipio</p>
                      <p class="text-sm font-semibold text-gray-900">{{ patient?.location?.municipality_name }}</p>
                    </div>
                    
                    <!-- Subregión y Dirección (Derecha) -->
                    <div class="space-y-2">
                      <!-- Subregión (Arriba) -->
                      <div v-if="patient?.location?.subregion">
                        <p class="text-xs text-gray-500 font-medium">Subregión</p>
                        <p class="text-sm font-semibold text-gray-900">{{ patient?.location?.subregion }}</p>
                      </div>
                      
                      <!-- Dirección (Abajo) -->
                      <div v-if="patient?.location?.address">
                        <p class="text-xs text-gray-500 font-medium">Dirección</p>
                        <p class="text-sm font-semibold text-gray-900">{{ patient?.location?.address }}</p>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Observaciones (si existen) -->
            <div v-if="patient?.observations" class="bg-gray-50 rounded-lg p-3 border border-gray-200">
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
                  <p class="text-xs text-gray-700 leading-relaxed">{{ patient?.observations }}</p>
                </div>
              </div>
            </div>

            <!-- Información del Sistema -->
            <div class="bg-gray-50 rounded-lg p-3 border border-gray-200">
              <div class="flex items-start space-x-2">
                <div class="flex-shrink-0">
                  <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                    <svg class="w-4 h-4 text-gray-700" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                    </svg>
                  </div>
                </div>
                <div class="flex-1">
                  <p class="text-xs uppercase tracking-wide text-gray-500 font-medium mb-2">Información del Sistema</p>
                  <div class="space-y-1">
                    <div class="flex items-center space-x-2">
                      <span class="text-xs text-gray-500">Creado:</span>
                      <span class="text-xs font-medium text-gray-900">{{ formatDateTime(patient?.created_at || '') }}</span>
                    </div>
                    <div class="flex items-center space-x-2">
                      <span class="text-xs text-gray-500">Actualizado:</span>
                      <span class="text-xs font-medium text-gray-900">{{ formatDateTime(patient?.updated_at || '') }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>

            <!-- Patient Cases -->
            <div class="border-t border-gray-200 pt-4">
              <div class="flex items-center space-x-2 mb-4">
                <div class="w-8 h-8 bg-white rounded-lg flex items-center justify-center border border-gray-200">
                  <CaseIcon class="w-4 h-4 text-gray-700" />
                </div>
                <h4 class="text-lg font-semibold text-gray-900">Casos del Paciente</h4>
              </div>

              <!-- Cases List -->
              <div v-if="isLoadingCases" class="flex items-center justify-center py-8">
                <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
              </div>

              <div v-else-if="patientCases.length === 0" class="text-center py-8 text-gray-500 bg-gray-50 rounded-lg border border-gray-200">
                <CaseIcon class="w-12 h-12 mx-auto mb-2 text-gray-300" />
                <p class="text-sm">No hay casos registrados para este paciente</p>
              </div>

              <div v-else class="space-y-3">
                <div
                  v-for="case_ in patientCases"
                  :key="case_._id || case_.id"
                  class="bg-gray-50 border border-gray-200 rounded-lg p-3 hover:shadow-sm transition-shadow"
                >
                  <div class="flex items-center justify-between mb-3">
                    <div class="flex items-center gap-2">
                      <span class="text-sm font-semibold text-gray-900">{{ case_.case_code || 'Sin código' }}</span>
                      <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                            :class="getCaseStatusClass(case_.state || 'pendiente')">
                        {{ case_.state || 'Pendiente' }}
                      </span>
                    </div>
                    <span class="text-xs text-gray-500 font-medium">{{ case_.created_at ? formatDate(case_.created_at) : 'Fecha no disponible' }}</span>
                  </div>
                  
                  <div class="grid grid-cols-2 gap-3">
                    <div class="bg-white rounded-lg p-2 border border-gray-200">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">Prioridad</p>
                      <p class="text-sm font-semibold text-gray-900">{{ case_.priority || 'Normal' }}</p>
                    </div>
                    <div class="bg-white rounded-lg p-2 border border-gray-200">
                      <p class="text-xs text-gray-500 font-medium uppercase tracking-wide mb-1">Patólogo Asignado</p>
                      <p class="text-sm font-semibold text-gray-900">{{ case_.assigned_pathologist?.name || 'No asignado' }}</p>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Footer fijo -->
          <div class="flex-shrink-0 flex items-center justify-between pt-3 border-t border-gray-200 px-4 pb-4 bg-white rounded-b-2xl">
            <div class="flex flex-col space-y-1 text-xs text-gray-500">
              <div class="flex items-center space-x-2">
                <svg class="w-3 h-3" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 8v4l3 3m6-3a9 9 0 11-18 0 9 9 0 0118 0z" />
                </svg>
                <span>Información actualizada</span>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="inline-flex items-center px-3 py-1.5 rounded-lg text-xs font-semibold border border-blue-500 text-blue-500 bg-white hover:bg-blue-50 transition-colors duration-200 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-offset-2"
            >
              Cerrar
            </button>
          </div>
        </div>
      </div>
  </transition>
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import type { Patient, PatientCase } from '../types/patient.types'
import { PatientsIcon, CaseIcon, EntityIcon } from '@/assets/icons'
import GerdenIcon from '@/assets/icons/GerdenIcon.vue'
import AtentionTypeIcon from '@/assets/icons/AtentionTypeIcon.vue'
import { formatDate, formatDateTime } from '../utils/dateUtils'
import { getPatientCases } from '../services/patientListApi'
import { useSidebar } from '@/shared/composables/SidebarControl'

interface Props {
  patient: Patient | null
  isVisible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
}>()

// Sidebar integration
const { isExpanded, isMobileOpen, isHovered } = useSidebar()
const overlayLeftClass = computed(() => {
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})

const patientCases = ref<PatientCase[]>([])
const isLoadingCases = ref(false)

// Watch for patient changes to load cases
watch(() => props.patient, (newPatient) => {
  if (newPatient && props.isVisible) {
    loadPatientCases()
  }
}, { immediate: true })

watch(() => props.isVisible, (isVisible) => {
  if (isVisible && props.patient) {
    loadPatientCases()
  }
})

const loadPatientCases = async () => {
  if (!props.patient) return
  
  isLoadingCases.value = true
  try {
    // Use patient_code or identification_number as the identifier for fetching cases
    const patientId = props.patient.patient_code || props.patient.identification_number || props.patient.id
    patientCases.value = await getPatientCases(patientId)
  } catch (error) {
    console.error('Error loading patient cases:', error)
    patientCases.value = []
  } finally {
    isLoadingCases.value = false
  }
}

const getCaseStatusClass = (status: string) => {
  const statusClasses = {
    // Database states (Spanish with spaces)
    'En proceso': 'bg-blue-100 text-blue-800',
    'Pendiente': 'bg-yellow-100 text-yellow-800',
    'Completado': 'bg-green-100 text-green-800',
    'Entregado': 'bg-gray-100 text-gray-800',
    'Cancelado': 'bg-red-100 text-red-800',
    // Legacy states (for backward compatibility)
    'pendiente': 'bg-yellow-100 text-yellow-800',
    'en_proceso': 'bg-blue-100 text-blue-800',
    'completado': 'bg-green-100 text-green-800',
    'entregado': 'bg-gray-100 text-gray-800',
    'cancelado': 'bg-red-100 text-red-800'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800'
}

</script>

<style scoped>
.fade-scale-enter-active { transition: all 0.18s ease-out; }
.fade-scale-leave-active { transition: all 0.12s ease-in; }
.fade-scale-enter-from, .fade-scale-leave-to { opacity: 0; transform: scale(.95); }
</style>