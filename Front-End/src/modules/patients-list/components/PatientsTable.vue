<template>
  <div class="overflow-hidden rounded-xl border border-gray-200 bg-white">
    <div v-if="selectedIds.length > 0" class="bg-blue-50 border-b border-blue-200 px-4 py-3">
      <div class="flex items-center justify-between">
        <div class="flex items-center gap-3">
          <span class="text-sm font-medium text-blue-800">
            {{ selectedIds.length }} paciente{{ selectedIds.length > 1 ? 's' : '' }} seleccionado{{ selectedIds.length > 1 ? 's' : '' }}
          </span>
          <button
            @click="clearSelection"
            class="text-sm text-blue-600 hover:text-blue-800 underline"
          >
            Deseleccionar todo
          </button>
        </div>
        
        <div class="flex items-center gap-2">
          <button
            @click="handleBatchDownloadExcel"
            :disabled="isDownloadingExcel"
            class="inline-flex items-center gap-2 px-3 py-2 bg-white text-gray-700 border border-gray-300 rounded-lg hover:bg-gray-50 transition-colors text-sm font-medium disabled:opacity-50 disabled:cursor-not-allowed"
          >
            <svg v-if="isDownloadingExcel" class="w-4 h-4 animate-spin" fill="none" viewBox="0 0 24 24">
              <circle class="opacity-25" cx="12" cy="12" r="10" stroke="currentColor" stroke-width="4"></circle>
              <path class="opacity-75" fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"></path>
            </svg>
            <DocsIcon v-else class="w-4 h-4" />
            {{ isDownloadingExcel ? 'Generando Excel...' : 'Exportar Excel Seleccionados' }}
          </button>
        </div>
      </div>
    </div>

    <div class="hidden lg:block max-w-full overflow-x-auto custom-scrollbar">
      <table class="min-w-full text-base">
        <thead>
          <tr class="border-b border-gray-200 bg-gray-50">
            <th class="px-2 py-2 text-center w-12">
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="props.isAllSelected"
                  :id="`select-all-${props.selectedIds.length}-${props.patients.length}`"
                  label=""
                  @update:model-value="toggleSelectAll"
                />
              </div>
            </th>
            <th v-for="column in props.columns" :key="column.key" class="px-2 py-2 text-center text-gray-700" :class="column.class">
              <button class="flex items-center gap-1 font-medium text-gray-600 text-sm hover:text-gray-700 justify-center w-full" @click="$emit('sort', column.key)">
                {{ column.label }}
                <span v-if="sortKey === column.key">{{ sortOrder === 'asc' ? '▲' : '▼' }}</span>
              </button>
            </th>
          </tr>
        </thead>
        <tbody class="divide-y divide-gray-200">
          <tr v-for="(patient, index) in props.patients" :key="`patient-${patient.patient_code}-${index}`" class="hover:bg-gray-50" @click="togglePatientSelection(patient.patient_code)">
            <td class="px-2 py-3 text-center">
              <div class="flex items-center justify-center">
                <FormCheckbox
                  :model-value="isPatientSelected(patient.patient_code)"
                  :id="`patient-${patient.patient_code}-${props.selectedIds.includes(patient.patient_code)}`"
                  label=""
                  @update:model-value="() => togglePatientSelection(patient.patient_code)"
                  @click.stop
                />
              </div>
            </td>
            <td class="px-1 py-3 text-center">
              <span class="font-medium text-gray-800">{{ getIdentificationTypeLabel(patient.identification_type) }}-{{ patient.identification_number }}</span>
            </td>
            <td class="px-2 py-3 text-center">
              <p class="text-gray-800 text-sm">{{ patient.full_name }}</p>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-sm">{{ patient.gender }}</p>
                <p class="text-gray-500 text-xs">{{ patient.age }} años</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-sm">{{ patient.entity_info?.name || 'N/A' }}</p>
                <p class="text-gray-500 text-xs">{{ patient.care_type }}</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex flex-col items-center gap-1">
                <p class="text-gray-800 text-sm">{{ patient.location?.municipality_name || 'N/A' }}</p>
                <p class="text-gray-500 text-xs">{{ patient.location?.subregion || 'N/A' }}</p>
              </div>
            </td>
            <td class="px-2 py-3 text-center">
              <p class="text-gray-800 text-sm">{{ formatDate(patient.created_at || '') }}</p>
            </td>
            <td class="px-2 py-3 text-center">
              <div class="flex items-center justify-center gap-1">
                <button
                  @click.stop="$emit('show-details', patient)"
                  class="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                  title="Ver detalles"
                >
                  <InfoCircleIcon class="w-4 h-4" />
                </button>
                <button
                  v-if="canEditPatient"
                  @click.stop="$emit('edit', patient)"
                  class="p-1 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                  title="Editar paciente"
                >
                  <EditPatientIcon class="w-4 h-4" />
                </button>
              </div>
            </td>
          </tr>
        </tbody>
      </table>
    </div>

    <!-- Vista móvil -->
    <div class="lg:hidden">
      <div v-if="props.patients.length === 0" class="p-8 text-center text-gray-500">
        {{ props.noResultsMessage || 'No hay pacientes disponibles' }}
      </div>
      <div v-else class="divide-y divide-gray-200">
        <div v-for="(patient, index) in props.patients" :key="`mobile-patient-${patient.patient_code}-${index}`" class="p-4 hover:bg-gray-50">
          <div class="flex items-start justify-between">
            <div class="flex items-start gap-3 flex-1">
              <FormCheckbox
                :model-value="isPatientSelected(patient.patient_code)"
                :id="`mobile-patient-${patient.patient_code}`"
                label=""
                @update:model-value="() => togglePatientSelection(patient.patient_code)"
              />
              <div class="flex-1 min-w-0">
                <div class="flex items-center gap-2 mb-1">
                  <h3 class="font-medium text-gray-900 truncate">{{ patient.full_name }}</h3>
                </div>
                <div class="space-y-1 text-sm text-gray-600">
                  <p><span class="font-medium">Documento:</span> {{ getIdentificationTypeLabel(patient.identification_type) }}-{{ patient.identification_number }}</p>
                  <p><span class="font-medium">Sexo/Edad:</span> {{ patient.gender }}, {{ patient.age }} años</p>
                  <p><span class="font-medium">Entidad:</span> {{ patient.entity_info?.name || 'N/A' }}</p>
                  <p><span class="font-medium">Tipo:</span> {{ patient.care_type }}</p>
                  <p v-if="patient.location?.municipality_name"><span class="font-medium">Municipio:</span> {{ patient.location.municipality_name }}</p>
                  <p><span class="font-medium">Creado:</span> {{ formatDate(patient.created_at || '') }}</p>
                </div>
              </div>
            </div>
            <div class="flex items-center gap-1 ml-2">
              <button
                @click="$emit('show-details', patient)"
                class="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                title="Ver detalles"
              >
                <InfoCircleIcon class="w-5 h-5" />
              </button>
              <button
                v-if="canEditPatient"
                @click="$emit('edit', patient)"
                class="p-2 text-gray-600 hover:text-gray-800 hover:bg-gray-100 rounded transition-colors"
                title="Editar paciente"
              >
                <EditPatientIcon class="w-5 h-5" />
              </button>
            </div>
          </div>
        </div>
      </div>
    </div>

    <!-- Paginación -->
    <div v-if="props.patients.length > 0" class="border-t border-gray-200 bg-white px-4 py-3 flex items-center justify-between">
      <div class="flex items-center gap-4">
        <div class="flex items-center gap-2">
          <label class="text-sm text-gray-700">Mostrar:</label>
          <select
            :value="props.itemsPerPage"
            @change="$emit('update-items-per-page', parseInt(($event.target as HTMLSelectElement).value))"
            class="border border-gray-300 rounded px-2 py-1 text-sm"
          >
            <option value="10">10</option>
            <option value="25">25</option>
            <option value="50">50</option>
            <option value="100">100</option>
          </select>
        </div>
        <div class="text-sm text-gray-700">
          Mostrando {{ ((props.currentPage - 1) * props.itemsPerPage) + 1 }} a 
          {{ Math.min(props.currentPage * props.itemsPerPage, props.totalItems) }} de 
          {{ props.totalItems }} pacientes
        </div>
      </div>
      
      <div class="flex items-center gap-2">
        <button
          @click="$emit('prev-page')"
          :disabled="props.currentPage <= 1"
          class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Anterior
        </button>
        <span class="text-sm text-gray-700">
          Página {{ props.currentPage }} de {{ props.totalPages }}
        </span>
        <button
          @click="$emit('next-page')"
          :disabled="props.currentPage >= props.totalPages"
          class="px-3 py-1 border border-gray-300 rounded text-sm hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
        >
          Siguiente
        </button>
      </div>
    </div>

    <!-- Mensaje cuando no hay resultados -->
    <div v-if="props.patients.length === 0" class="hidden lg:block p-8 text-center text-gray-500">
      {{ props.noResultsMessage || 'No hay pacientes disponibles' }}
    </div>
  </div>
</template>

<script setup lang="ts">
import { ref, computed } from 'vue'
import type { Patient } from '../types/patient.types'
import { FormCheckbox } from '@/shared/components'
import { DocsIcon } from '@/assets/icons'
import InfoCircleIcon from '@/assets/icons/InfoCircleIcon.vue'
import EditPatientIcon from '@/assets/icons/EditPatientIcon.vue'
import { usePatientExcelExport } from '../composables/usePatientExcelExport'
import { formatDate } from '../utils/dateUtils'
import { usePermissions } from '@/shared/composables/usePermissions'

interface Column {
  key: string
  label: string
  class?: string
}

interface Props {
  patients: Patient[]
  selectedIds: string[]
  isAllSelected: boolean
  columns: Column[]
  sortKey: string
  sortOrder: 'asc' | 'desc'
  currentPage: number
  totalPages: number
  itemsPerPage: number
  totalItems: number
  noResultsMessage?: string
}

const props = defineProps<Props>()

const emit = defineEmits<{
  'toggle-select': [patientId: string]
  'toggle-select-all': []
  'clear-selection': []
  'sort': [key: string]
  'show-details': [patient: Patient]
  'edit': [patient: Patient]
  'update-items-per-page': [value: number]
  'prev-page': []
  'next-page': []
  'refresh': []
}>()

const { exportSelectedPatients } = usePatientExcelExport()
const isDownloadingExcel = ref(false)
const { isPatologo } = usePermissions()
const canEditPatient = computed(() => !isPatologo.value)

const isPatientSelected = (patientId: string) => {
  return props.selectedIds.includes(patientId)
}

const togglePatientSelection = (patientId: string) => {
  emit('toggle-select', patientId)
}

const toggleSelectAll = () => {
  emit('toggle-select-all')
}

const clearSelection = () => {
  emit('clear-selection')
}

const handleBatchDownloadExcel = async () => {
  if (props.selectedIds.length === 0) return
  
  isDownloadingExcel.value = true
  try {
    const selectedPatients = props.patients.filter(p => props.selectedIds.includes(p.patient_code))
    await exportSelectedPatients(selectedPatients)
  } catch (error) {
    // Error silenciado
  } finally {
    isDownloadingExcel.value = false
  }
}

const getIdentificationTypeLabel = (type: number): string => {
  const types: Record<number, string> = {
    1: 'CC',
    2: 'CE',
    3: 'TI',
    4: 'PA',
    5: 'RC',
    6: 'DE',
    7: 'NIT',
    8: 'CD',
    9: 'SC'
  }
  return types[type] || 'N/A'
}
</script>

<style scoped>
.custom-scrollbar {
  scrollbar-width: thin;
  scrollbar-color: #cbd5e0 #f7fafc;
}

.custom-scrollbar::-webkit-scrollbar {
  height: 8px;
}

.custom-scrollbar::-webkit-scrollbar-track {
  background: #f7fafc;
}

.custom-scrollbar::-webkit-scrollbar-thumb {
  background-color: #cbd5e0;
  border-radius: 4px;
}

.custom-scrollbar::-webkit-scrollbar-thumb:hover {
  background-color: #a0aec0;
}
</style>