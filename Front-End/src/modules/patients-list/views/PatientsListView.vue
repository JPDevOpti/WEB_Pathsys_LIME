<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="pageTitle" />
    <div class="space-y-4">
      <!-- Mantener filtros siempre montados para conservar selección de municipio/entidad -->
      <FiltersBar 
        v-model="filters" 
        :totalFiltered="sortedPatients.length" 
        :totalAll="totalCount"
        :isLoading="isLoading" 
        :canExport="sortedPatients.length > 0" 
        @refresh="reload" 
        @export="exportExcel" 
        @search="handleSearch" 
      />
      <Card v-if="isLoading">
        <div class="p-8 text-center">
          <LoadingSpinner />
        </div>
      </Card>

      <Card v-else-if="error">
        <div class="p-8 text-center">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <BaseButton size="sm" variant="primary" @click="reload">Reintentar</BaseButton>
        </div>
      </Card>

      <template v-else>
        <div class="bg-white rounded-xl border border-gray-200">
          <PatientsTable 
            :patients="paginatedPatients" 
            :selected-ids="selectedPatientIds" 
            :is-all-selected="isAllSelected"
            :columns="columns" 
            :sort-key="sortKey" 
            :sort-order="sortOrder" 
            :current-page="currentPage"
            :total-pages="totalPages" 
            :items-per-page="itemsPerPage" 
            :total-items="sortedPatients.length"
            :no-results-message="hasActiveFilters ? 'No se encontraron pacientes con los filtros aplicados' : 'No hay pacientes disponibles'"
            @toggle-select="toggleSelect" 
            @toggle-select-all="toggleSelectAll" 
            @clear-selection="selectedPatientIds = []"
            @sort="sortBy" 
            @show-details="showDetails" 
            @edit="editPatient"
            @update-items-per-page="(v: number) => itemsPerPage = v"
            @prev-page="() => currentPage--" 
            @next-page="() => currentPage++" 
            @refresh="reload"
          />
        </div>

        <PatientDetailsModal 
          :patient="selectedPatient" 
          :is-visible="!!selectedPatient"
          @close="closeDetails" 
        />
      </template>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { AdminLayout } from '@/shared/components/layout'
import { useRouter } from 'vue-router'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import Card from '@/shared/components/layout/Card.vue'
import { BaseButton } from '@/shared/components'
import LoadingSpinner from '@/shared/components/ui/feedback/LoadingSpinner.vue'

import FiltersBar from '../components/FiltersBar.vue'
import PatientsTable from '../components/PatientsTable.vue'
import PatientDetailsModal from '../components/PatientDetailsModal.vue'

import { usePatientList } from '../composables/usePatientList'
import { usePatientExcelExport } from '../composables/usePatientExcelExport'

const pageTitle = 'Lista de Pacientes'

const {
  isLoading,
  error,
  totalCount,
  filters,
  sortKey,
  sortOrder,
  currentPage,
  itemsPerPage,
  selectedPatientIds,
  selectedPatient,
  sortedPatients,
  paginatedPatients,
  totalPages,
  isAllSelected,
  loadPatients,
  toggleSelectAll,
  toggleSelect,
  sortBy,
  showDetails,
  closeDetails,
} = usePatientList()

const { exportPatientsToExcel } = usePatientExcelExport()
const router = useRouter()

const columns = [
  { key: 'identification', label: 'Documento', class: 'w-[10%]' },
  { key: 'full_name', label: 'Nombre', class: 'w-[20%]' },
  { key: 'gender', label: 'Género / Edad', class: 'w-[12%]' },
  { key: 'entity_info', label: 'Entidad / Tipo', class: 'w-[18%]' },
  { key: 'location', label: 'Municipio / Subregión', class: 'w-[18%]' },
  { key: 'created_at', label: 'Fecha Creación', class: 'w-[12%]' },
  { key: 'actions', label: 'Acciones', class: 'w-[15%]' },
]

const hasActiveFilters = computed(() => {
  return !!(
    filters.value.search ||
    filters.value.entity ||
    filters.value.gender ||
    filters.value.care_type ||
    filters.value.municipality_code ||
    filters.value.municipality_name ||
    filters.value.subregion ||
    filters.value.date_from ||
    filters.value.date_to
  )
})

function reload() { 
  loadPatients() 
}

function handleSearch() {
  currentPage.value = 1
  loadPatients()
}

function exportExcel() { 
  exportPatientsToExcel(sortedPatients.value) 
}

function editPatient(patient: any) {
  const patientCode = patient?.patient_code || ''
  if (!patientCode) return
  
  router.push({ 
    name: 'patients-edit', 
    params: { code: patientCode }, 
    query: { auto: '1' } 
  })
}

const handlePatientCreated = (_event: CustomEvent) => {
  loadPatients()
}

const handlePatientUpdated = (_event: CustomEvent) => {
  loadPatients()
}

onMounted(() => {
  window.addEventListener('patient-created', handlePatientCreated as EventListener)
  window.addEventListener('patient-updated', handlePatientUpdated as EventListener)
  loadPatients()
})

onUnmounted(() => {
  window.removeEventListener('patient-created', handlePatientCreated as EventListener)
  window.removeEventListener('patient-updated', handlePatientUpdated as EventListener)
})
</script>