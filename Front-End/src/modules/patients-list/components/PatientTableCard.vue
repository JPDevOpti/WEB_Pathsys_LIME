<template>
  <ComponentCard
    title="Lista de Pacientes"
    :show-content="true"
  >
    <template #header-actions>
      <div class="flex items-center space-x-2">
        <!-- Batch actions -->
        <div v-if="hasSelectedPatients" class="flex items-center space-x-2">
          <span class="text-sm text-gray-600">
            {{ selectedIds.length }} paciente(s) seleccionado(s)
          </span>
          <button
            @click="handleBatchExport"
            class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
          >
            <svg class="w-4 h-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 10v6m0 0l-3-3m3 3l3-3m2 8H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
            </svg>
            Exportar Excel
          </button>
        </div>
        
        <!-- Select all toggle -->
        <button
          @click="handleToggleSelectAll"
          class="inline-flex items-center px-3 py-2 border border-gray-300 shadow-sm text-sm leading-4 font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 focus:outline-none focus:ring-2 focus:ring-offset-2 focus:ring-blue-500"
        >
          {{ isAllSelected ? 'Deseleccionar Todo' : 'Seleccionar Todo' }}
        </button>
      </div>
    </template>

    <template #content>
      <!-- Desktop table view -->
      <div class="hidden md:block">
        <div class="overflow-x-auto">
          <table class="min-w-full divide-y divide-gray-200">
            <thead class="bg-gray-50">
              <tr>
                <th scope="col" class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">
                  <input
                    type="checkbox"
                    :checked="isAllSelected"
                    @change="handleToggleSelectAll"
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </th>
                <th
                  v-for="column in visibleColumns"
                  :key="column.key"
                  scope="col"
                  class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider cursor-pointer hover:bg-gray-100"
                  @click="handleSort(column.key)"
                >
                  <div class="flex items-center space-x-1">
                    <span>{{ column.label }}</span>
                    <svg
                      v-if="sortKey === column.key"
                      class="w-4 h-4"
                      :class="sortOrder === 'asc' ? 'transform rotate-180' : ''"
                      fill="none"
                      stroke="currentColor"
                      viewBox="0 0 24 24"
                    >
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 9l-7 7-7-7" />
                    </svg>
                  </div>
                </th>
                <th scope="col" class="relative px-6 py-3">
                  <span class="sr-only">Acciones</span>
                </th>
              </tr>
            </thead>
            <tbody class="bg-white divide-y divide-gray-200">
              <tr
                v-for="patient in patients"
                :key="patient.id"
                class="hover:bg-gray-50 cursor-pointer"
                @click="handlePatientSelect(patient)"
              >
                <td class="px-6 py-4 whitespace-nowrap">
                  <input
                    type="checkbox"
                    :checked="selectedIds.includes(patient.id)"
                    @change="handlePatientToggle(patient.id)"
                    @click.stop
                    class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                  />
                </td>
                <td
                  v-for="column in visibleColumns"
                  :key="column.key"
                  class="px-6 py-4 whitespace-nowrap text-sm text-gray-900"
                >
                  <span v-if="column.key === 'createdAt' || column.key === 'updatedAt'">
                    {{ formatDate(patient[column.key as keyof PatientData] as string) }}
                  </span>
                  <span v-else>
                    {{ patient[column.key as keyof PatientData] }}
                  </span>
                </td>
                <td class="px-6 py-4 whitespace-nowrap text-right text-sm font-medium">
                  <div class="flex items-center space-x-2">
                    <button
                      @click.stop="handleViewDetails(patient)"
                      class="text-blue-600 hover:text-blue-900"
                      title="Ver detalles"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                      </svg>
                    </button>
                    <button
                      v-if="canEditPatient"
                      @click.stop="handleEdit(patient)"
                      class="text-green-600 hover:text-green-900"
                      title="Editar"
                    >
                      <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                      </svg>
                    </button>
                  </div>
                </td>
              </tr>
            </tbody>
          </table>
        </div>
      </div>

      <!-- Mobile card view -->
      <div class="md:hidden space-y-4">
        <div
          v-for="patient in patients"
          :key="patient.id"
          class="bg-white border border-gray-200 rounded-lg p-4 shadow-sm"
          @click="handlePatientSelect(patient)"
        >
          <div class="flex items-start justify-between mb-3">
            <div class="flex items-center space-x-3">
              <input
                type="checkbox"
                :checked="selectedIds.includes(patient.id)"
                @change="handlePatientToggle(patient.id)"
                @click.stop
                class="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
              />
              <div>
                <h3 class="text-sm font-medium text-gray-900">{{ patient.fullName }}</h3>
                <p class="text-xs text-gray-500">{{ patient.code }}</p>
              </div>
            </div>
            <div class="flex items-center space-x-2">
              <button
                @click.stop="handleViewDetails(patient)"
                class="text-blue-600 hover:text-blue-900"
                title="Ver detalles"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z" />
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z" />
                </svg>
              </button>
              <button
                v-if="canEditPatient"
                @click.stop="handleEdit(patient)"
                class="text-green-600 hover:text-green-900"
                title="Editar"
              >
                <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z" />
                </svg>
              </button>
            </div>
          </div>
          
          <div class="grid grid-cols-2 gap-2 text-xs">
            <div>
              <span class="text-gray-500">ID:</span>
              <span class="ml-1 text-gray-900">{{ patient.identification }}</span>
            </div>
            <div>
              <span class="text-gray-500">Sexo:</span>
              <span class="ml-1 text-gray-900">{{ patient.gender }}</span>
            </div>
            <div>
              <span class="text-gray-500">Edad:</span>
              <span class="ml-1 text-gray-900">{{ patient.age }} años</span>
            </div>
            <div>
              <span class="text-gray-500">Entidad:</span>
              <span class="ml-1 text-gray-900">{{ patient.entity }}</span>
            </div>
          </div>
        </div>
      </div>

      <!-- No results message -->
      <div v-if="patients.length === 0" class="text-center py-12">
        <svg class="mx-auto h-12 w-12 text-gray-400" fill="none" viewBox="0 0 24 24" stroke="currentColor">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
        </svg>
        <h3 class="mt-2 text-sm font-medium text-gray-900">{{ noResultsMessage }}</h3>
        <p class="mt-1 text-sm text-gray-500">Intenta ajustar los filtros de búsqueda.</p>
      </div>

      <!-- Pagination -->
      <div v-if="patients.length > 0" class="bg-white px-4 py-3 flex items-center justify-between border-t border-gray-200 sm:px-6">
        <div class="flex-1 flex justify-between sm:hidden">
          <button
            @click="handlePreviousPage"
            :disabled="currentPage === 1"
            class="relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Anterior
          </button>
          <button
            @click="handleNextPage"
            :disabled="currentPage === totalPages"
            class="ml-3 relative inline-flex items-center px-4 py-2 border border-gray-300 text-sm font-medium rounded-md text-gray-700 bg-white hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            Siguiente
          </button>
        </div>
        <div class="hidden sm:flex-1 sm:flex sm:items-center sm:justify-between">
          <div>
            <p class="text-sm text-gray-700">
              Mostrando
              <span class="font-medium">{{ startItem }}</span>
              a
              <span class="font-medium">{{ endItem }}</span>
              de
              <span class="font-medium">{{ totalItems }}</span>
              resultados
            </p>
          </div>
          <div>
            <nav class="relative z-0 inline-flex rounded-md shadow-sm -space-x-px" aria-label="Pagination">
              <button
                @click="handlePreviousPage"
                :disabled="currentPage === 1"
                class="relative inline-flex items-center px-2 py-2 rounded-l-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Anterior</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M12.707 5.293a1 1 0 010 1.414L9.414 10l3.293 3.293a1 1 0 01-1.414 1.414l-4-4a1 1 0 010-1.414l4-4a1 1 0 011.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
              
              <button
                v-for="page in visiblePages"
                :key="page"
                @click="handlePageChange(page)"
                :class="[
                  'relative inline-flex items-center px-4 py-2 border text-sm font-medium',
                  page === currentPage
                    ? 'z-10 bg-blue-50 border-blue-500 text-blue-600'
                    : 'bg-white border-gray-300 text-gray-500 hover:bg-gray-50'
                ]"
              >
                {{ page }}
              </button>
              
              <button
                @click="handleNextPage"
                :disabled="currentPage === totalPages"
                class="relative inline-flex items-center px-2 py-2 rounded-r-md border border-gray-300 bg-white text-sm font-medium text-gray-500 hover:bg-gray-50 disabled:opacity-50 disabled:cursor-not-allowed"
              >
                <span class="sr-only">Siguiente</span>
                <svg class="h-5 w-5" fill="currentColor" viewBox="0 0 20 20">
                  <path fill-rule="evenodd" d="M7.293 14.707a1 1 0 010-1.414L10.586 10 7.293 6.707a1 1 0 011.414-1.414l4 4a1 1 0 010 1.414l-4 4a1 1 0 01-1.414 0z" clip-rule="evenodd" />
                </svg>
              </button>
            </nav>
          </div>
        </div>
      </div>
    </template>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed } from 'vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import { ComponentCard } from '@/shared/components'

// Types
interface PatientData {
  id: string
  code: string
  fullName: string
  identification: string
  gender: string
  age: number
  entity: string
  careType: string
  location: string
  createdAt: string
  updatedAt?: string
}

interface TableColumn {
  key: string
  label: string
  sortable?: boolean
}

// Props
interface Props {
  patients: PatientData[]
  selectedIds: string[]
  isAllSelected: boolean
  columns: TableColumn[]
  sortKey: string
  sortOrder: 'asc' | 'desc'
  currentPage: number
  totalPages: number
  itemsPerPage: number
  totalItems: number
  noResultsMessage?: string
}

const props = withDefaults(defineProps<Props>(), {
  noResultsMessage: 'No se encontraron pacientes'
})

// Emits
const emit = defineEmits<{
  patientSelect: [patient: PatientData]
  patientToggle: [patientId: string]
  toggleSelectAll: []
  batchExport: []
  sort: [key: string]
  viewDetails: [patient: PatientData]
  edit: [patient: PatientData]
  pageChange: [page: number]
  previousPage: []
  nextPage: []
}>()

// Computed
const hasSelectedPatients = computed(() => props.selectedIds.length > 0)

const visibleColumns = computed(() => 
  props.columns.filter(column => column.key !== 'actions')
)

const startItem = computed(() => 
  (props.currentPage - 1) * props.itemsPerPage + 1
)

const endItem = computed(() => 
  Math.min(props.currentPage * props.itemsPerPage, props.totalItems)
)

const visiblePages = computed(() => {
  const pages = []
  const maxVisible = 5
  let start = Math.max(1, props.currentPage - Math.floor(maxVisible / 2))
  let end = Math.min(props.totalPages, start + maxVisible - 1)
  
  if (end - start + 1 < maxVisible) {
    start = Math.max(1, end - maxVisible + 1)
  }
  
  for (let i = start; i <= end; i++) {
    pages.push(i)
  }
  
  return pages
})

// Permisos: ocultar edición para patólogos
const { isPatologo } = usePermissions()
const canEditPatient = computed(() => !isPatologo.value)

// Methods
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: '2-digit',
      day: '2-digit'
    })
  } catch (error) {
    return dateString
  }
}

const handlePatientSelect = (patient: PatientData) => {
  emit('patientSelect', patient)
}

const handlePatientToggle = (patientId: string) => {
  emit('patientToggle', patientId)
}

const handleToggleSelectAll = () => {
  emit('toggleSelectAll')
}

const handleBatchExport = () => {
  emit('batchExport')
}

const handleSort = (key: string) => {
  emit('sort', key)
}

const handleViewDetails = (patient: PatientData) => {
  emit('viewDetails', patient)
}

const handleEdit = (patient: PatientData) => {
  emit('edit', patient)
}

const handlePageChange = (page: number) => {
  emit('pageChange', page)
}

const handlePreviousPage = () => {
  emit('previousPage')
}

const handleNextPage = () => {
  emit('nextPage')
}
</script>