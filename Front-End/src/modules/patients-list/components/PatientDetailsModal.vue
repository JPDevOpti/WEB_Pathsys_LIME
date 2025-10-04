<template>
  <div v-if="isVisible" class="fixed inset-0 z-50 overflow-y-auto" @click="handleBackdropClick">
    <div class="flex items-center justify-center min-h-screen pt-4 px-4 pb-20 text-center sm:block sm:p-0">
      <!-- Backdrop -->
      <div class="fixed inset-0 bg-gray-500 bg-opacity-75 transition-opacity"></div>

      <!-- Modal -->
      <div class="inline-block align-bottom bg-white rounded-lg text-left overflow-hidden shadow-xl transform transition-all sm:my-8 sm:align-middle sm:max-w-4xl sm:w-full">
        <!-- Header -->
        <div class="bg-white px-4 pt-5 pb-4 sm:p-6 sm:pb-4">
          <div class="flex items-center justify-between mb-4">
            <div class="flex items-center gap-3">
              <div class="p-2 bg-blue-100 rounded-lg">
                <PatientsIcon class="w-6 h-6 text-blue-600" />
              </div>
              <div>
                <h3 class="text-lg font-medium text-gray-900">
                  Detalles del Paciente
                </h3>
                <p class="text-sm text-gray-500">
                  {{ patient?.full_name }}
                </p>
              </div>
            </div>
            <button
              @click="$emit('close')"
              class="rounded-md text-gray-400 hover:text-gray-500 focus:outline-none focus:ring-2 focus:ring-blue-500"
            >
              <svg class="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12" />
              </svg>
            </button>
          </div>

          <!-- Patient Information -->
          <div class="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
            <!-- Basic Info -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Información Básica</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Código:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.patient_code }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Documento:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.identification_number }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Género:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.gender }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Edad:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.age }} años</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Fecha de Nacimiento:</span>
                  <span class="text-sm font-medium text-gray-900">{{ formatDate(patient?.birth_date || '') }}</span>
                </div>
              </div>
            </div>

            <!-- Contact Info -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Información de Contacto</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Municipio:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.location?.municipality_name || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Subregión:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.location?.subregion || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Dirección:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.location?.address || 'N/A' }}</span>
                </div>
              </div>
            </div>

            <!-- Medical Info -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Información Médica</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Entidad:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.entity_info?.name || 'N/A' }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Tipo de Atención:</span>
                  <span class="text-sm font-medium text-gray-900">{{ patient?.care_type }}</span>
                </div>
                <div v-if="patient?.observations" class="pt-2 border-t border-gray-200">
                  <p class="text-xs font-medium text-gray-700 mb-1">Observaciones:</p>
                  <p class="text-xs text-gray-600">{{ patient.observations }}</p>
                </div>
              </div>
            </div>

            <!-- System Info -->
            <div class="bg-gray-50 rounded-lg p-4">
              <h4 class="text-sm font-medium text-gray-900 mb-3">Información del Sistema</h4>
              <div class="space-y-2">
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Creado:</span>
                  <span class="text-sm font-medium text-gray-900">{{ formatDateTime(patient?.created_at || '') }}</span>
                </div>
                <div class="flex justify-between">
                  <span class="text-sm text-gray-600">Actualizado:</span>
                  <span class="text-sm font-medium text-gray-900">{{ formatDateTime(patient?.updated_at || '') }}</span>
                </div>
              </div>
            </div>
          </div>

          <!-- Patient Cases -->
          <div class="border-t border-gray-200 pt-6">
            <div class="flex items-center justify-between mb-4">
              <h4 class="text-lg font-medium text-gray-900">Casos del Paciente</h4>
              <div class="flex items-center gap-2">
                <button
                  @click="loadPatientCases"
                  :disabled="isLoadingCases"
                  class="inline-flex items-center gap-2 px-3 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
                >
                  <RefreshIcon class="w-4 h-4" :class="{ 'animate-spin': isLoadingCases }" />
                  {{ isLoadingCases ? 'Cargando...' : 'Actualizar' }}
                </button>
              </div>
            </div>

            <!-- Cases List -->
            <div v-if="isLoadingCases" class="flex items-center justify-center py-8">
              <div class="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600"></div>
            </div>

            <div v-else-if="patientCases.length === 0" class="text-center py-8 text-gray-500">
              <CaseIcon class="w-12 h-12 mx-auto mb-2 text-gray-300" />
              <p>No hay casos registrados para este paciente</p>
            </div>

            <div v-else class="space-y-3">
              <div
                v-for="case_ in patientCases"
                :key="case_.id"
                class="bg-white border border-gray-200 rounded-lg p-4 hover:shadow-sm transition-shadow"
              >
                <div class="flex items-center justify-between mb-2">
                  <div class="flex items-center gap-2">
                    <span class="text-sm font-medium text-gray-900">{{ case_.caseCode || case_.id }}</span>
                    <span class="inline-flex items-center px-2 py-1 rounded-full text-xs font-medium"
                          :class="getCaseStatusClass(case_.status)">
                      {{ case_.status }}
                    </span>
                  </div>
                  <span class="text-xs text-gray-500">{{ formatDate(case_.receivedAt) }}</span>
                </div>
                
                <div class="grid grid-cols-2 gap-4 text-sm">
                  <div>
                    <span class="text-gray-600">Tipo de Muestra:</span>
                    <span class="ml-1 font-medium text-gray-900">{{ case_.sampleType }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600">Solicitante:</span>
                    <span class="ml-1 font-medium text-gray-900">{{ case_.requester }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600">Patólogo:</span>
                    <span class="ml-1 font-medium text-gray-900">{{ case_.pathologist || 'No asignado' }}</span>
                  </div>
                  <div>
                    <span class="text-gray-600">Pruebas:</span>
                    <span class="ml-1 font-medium text-gray-900">{{ case_.tests.join(', ') }}</span>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer -->
        <div class="bg-gray-50 px-4 py-3 sm:px-6 sm:flex sm:flex-row-reverse">
          <button
            @click="$emit('close')"
            class="w-full inline-flex justify-center rounded-md border border-transparent shadow-sm px-4 py-2 bg-blue-600 text-base font-medium text-white hover:bg-blue-700 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500 sm:ml-3 sm:w-auto sm:text-sm"
          >
            Cerrar
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, watch } from 'vue'
import type { Patient, PatientCase } from '../types/patient.types'
import { PatientsIcon, RefreshIcon, CaseIcon } from '@/assets/icons'
import { formatDate, formatDateTime } from '../utils/dateUtils'
import { getPatientCases } from '../services/patientListApi'

interface Props {
  patient: Patient | null
  isVisible: boolean
}

const props = defineProps<Props>()
const emit = defineEmits<{
  'close': []
}>()

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
    patientCases.value = await getPatientCases(props.patient.id)
  } catch (error) {
    patientCases.value = []
  } finally {
    isLoadingCases.value = false
  }
}

const getCaseStatusClass = (status: string) => {
  const statusClasses = {
    'pendiente': 'bg-yellow-100 text-yellow-800',
    'en_proceso': 'bg-blue-100 text-blue-800',
    'completado': 'bg-green-100 text-green-800',
    'entregado': 'bg-gray-100 text-gray-800',
    'cancelado': 'bg-red-100 text-red-800'
  }
  return statusClasses[status as keyof typeof statusClasses] || 'bg-gray-100 text-gray-800'
}

const handleBackdropClick = (event: MouseEvent) => {
  if (event.target === event.currentTarget) {
    emit('close')
  }
}
</script>