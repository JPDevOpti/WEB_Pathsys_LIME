<template>
  <div class="space-y-6">
    <!-- Search Card -->
    <PatientSearchCard
      :is-searching="isSearching"
      :gender-options="genderOptions"
      :entity-options="entityOptions"
      :care-type-options="careTypeOptions"
      @search="handleSearch"
      @clear-filters="handleClearFilters"
    />

    <!-- Patient Info Card (only show when a patient is selected) -->
    <PatientInfoCard
      v-if="selectedPatient"
      :selected-patient="selectedPatient"
      :allow-selection="false"
      @view-details="handleViewDetails"
      @edit="handleEdit"
    />

    <!-- Patients Table Card -->
    <PatientTableCard
      :patients="patients"
      :selected-ids="selectedIds"
      :is-all-selected="isAllSelected"
      :columns="columns"
      :sort-key="sortKey"
      :sort-order="sortOrder"
      :current-page="currentPage"
      :total-pages="totalPages"
      :items-per-page="itemsPerPage"
      :total-items="totalItems"
      :no-results-message="noResultsMessage"
      @patient-select="handlePatientSelect"
      @patient-toggle="handlePatientToggle"
      @toggle-select-all="handleToggleSelectAll"
      @batch-export="handleBatchExport"
      @sort="handleSort"
      @view-details="handleViewDetails"
      @edit="handleEdit"
      @page-change="handlePageChange"
      @previous-page="handlePreviousPage"
      @next-page="handleNextPage"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, reactive, computed, onMounted } from 'vue'
import PatientSearchCard from './PatientSearchCard.vue'
import PatientInfoCard from './PatientInfoCard.vue'
import PatientTableCard from './PatientTableCard.vue'

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
  additionalInfo?: {
    phone?: string
    email?: string
    address?: string
  }
}

interface TableColumn {
  key: string
  label: string
  sortable?: boolean
  class?: string
}

interface SearchFilters {
  searchText: string
  gender: string
  entityId: string
  careType: string
  ageFrom: string
  ageTo: string
  createdFrom: string
  createdTo: string
}

interface SelectOption {
  value: string
  label: string
}

// Props
interface Props {
  patients?: PatientData[]
  selectedIds?: string[]
  isAllSelected?: boolean
  columns?: TableColumn[]
  sortKey?: string
  sortOrder?: 'asc' | 'desc'
  currentPage?: number
  totalPages?: number
  itemsPerPage?: number
  totalItems?: number
  noResultsMessage?: string
  genderOptions?: SelectOption[]
  entityOptions?: SelectOption[]
  careTypeOptions?: SelectOption[]
  isSearching?: boolean
}

const props = withDefaults(defineProps<Props>(), {
  patients: () => [],
  selectedIds: () => [],
  isAllSelected: false,
  columns: () => [
    { key: 'code', label: 'Código', sortable: true },
    { key: 'fullName', label: 'Nombre Completo', sortable: true },
    { key: 'identification', label: 'Identificación', sortable: true },
    { key: 'gender', label: 'Sexo', sortable: true },
    { key: 'age', label: 'Edad', sortable: true },
    { key: 'entity', label: 'Entidad', sortable: true },
    { key: 'careType', label: 'Tipo de Atención', sortable: true },
    { key: 'location', label: 'Ubicación', sortable: true },
    { key: 'createdAt', label: 'Fecha de Creación', sortable: true }
  ],
  sortKey: 'createdAt',
  sortOrder: 'desc',
  currentPage: 1,
  totalPages: 1,
  itemsPerPage: 10,
  totalItems: 0,
  noResultsMessage: 'No se encontraron pacientes',
  genderOptions: () => [
    { value: '', label: 'Todos' },
    { value: 'M', label: 'Masculino' },
    { value: 'F', label: 'Femenino' }
  ],
  entityOptions: () => [
    { value: '', label: 'Todas las entidades' }
  ],
  careTypeOptions: () => [
    { value: '', label: 'Todos los tipos' },
    { value: 'ambulatory', label: 'Ambulatorio' },
    { value: 'hospitalization', label: 'Hospitalización' },
    { value: 'emergency', label: 'Urgencias' }
  ],
  isSearching: false
})

// Emits
const emit = defineEmits<{
  search: [filters: SearchFilters]
  clearFilters: []
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

// State
const selectedPatient = ref<PatientData | null>(null)

const searchFilters = reactive<SearchFilters>({
  searchText: '',
  gender: '',
  entityId: '',
  careType: '',
  ageFrom: '',
  ageTo: '',
  createdFrom: '',
  createdTo: ''
})

// Methods
const handleSearch = (filters: SearchFilters) => {
  Object.assign(searchFilters, filters)
  emit('search', filters)
}

const handleClearFilters = () => {
  Object.assign(searchFilters, {
    searchText: '',
    gender: '',
    entityId: '',
    careType: '',
    ageFrom: '',
    ageTo: '',
    createdFrom: '',
    createdTo: ''
  })
  emit('clearFilters')
}

const handlePatientSelect = (patient: PatientData) => {
  selectedPatient.value = patient
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

// Lifecycle
onMounted(() => {
  // Initialize with default search if needed
  if (props.patients.length === 0) {
    handleSearch(searchFilters)
  }
})
</script>