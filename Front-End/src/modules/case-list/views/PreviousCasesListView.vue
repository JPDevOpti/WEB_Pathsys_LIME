<template>
  <AdminLayout>
    <PageBreadcrumb :pageTitle="pageTitle" />
    <div class="space-y-4">
      <Card v-if="isLoading">
        <div class="p-8 text-center">
          <LoadingSpinner />
          <p class="text-gray-600 mt-2">Cargando casos anteriores...</p>
        </div>
      </Card>

      <Card v-else-if="error">
        <div class="p-8 text-center">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <BaseButton size="sm" variant="primary" @click="reload">Reintentar</BaseButton>
        </div>
      </Card>

      <template v-else>
        <FiltersBar
          v-model="filters"
          :totalFiltered="filteredCases.length"
          :totalAll="cases.length"
          :isLoading="isLoading"
          :canExport="filteredCases.length > 0"
          @refresh="reload"
          @export="exportExcel"
        />

        <div class="bg-white rounded-xl border border-gray-200">
          <CasesTable
            :cases="paginatedCases"
            :selected-ids="selectedCaseIds"
            :is-all-selected="isAllSelected"
            :columns="columns"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            :current-page="currentPage"
            :total-pages="totalPages"
            :items-per-page="itemsPerPage"
            :total-items="filteredCases.length"
            :no-results-message="hasActiveFilters ? 'No se encontraron casos anteriores con los filtros aplicados' : 'No hay casos anteriores disponibles'"
            @toggle-select="toggleSelect"
            @toggle-select-all="toggleSelectAll"
            @clear-selection="selectedCaseIds = []"
            @sort="(k: any) => sortBy(k)"
            @show-details="showDetails"
            @edit="editCase"
            @validate="validateCase"
            @perform="performCase"
            @update-items-per-page="(v: number) => (itemsPerPage = v)"
            @prev-page="() => currentPage--"
            @next-page="() => currentPage++"
          />
        </div>

        <CaseDetailsModal :case-item="selectedCase" @close="closeDetails" @edit="editCase" @preview="previewCase" />
      </template>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { computed, onMounted, onUnmounted } from 'vue'
import { useRouter } from 'vue-router'
import { AdminLayout } from '@/shared/components/layout'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import Card from '@/shared/components/layout/Card.vue'
import { BaseButton } from '@/shared/components'
import LoadingSpinner from '@/shared/components/feedback/LoadingSpinner.vue'
import { FiltersBar, CasesTable, CaseDetailsModal } from '../components'
import { useCaseList } from '../composables/useCaseList'
import { useExcelExport } from '../composables/useExcelExport'

const pageTitle = 'Casos Anteriores'

const {
  cases,
  isLoading,
  error,
  filters,
  sortKey,
  sortOrder,
  currentPage,
  itemsPerPage,
  selectedCaseIds,
  selectedCase,
  filteredCases,
  paginatedCases,
  totalPages,
  isAllSelected,
  loadCases,
  toggleSelectAll,
  toggleSelect,
  sortBy,
  showDetails,
  closeDetails,
  validateCase,
} = useCaseList()

const { exportCasesToExcel } = useExcelExport()
const router = useRouter()

const hasActiveFilters = computed(() => {
  return !!(
    filters.value.searchQuery ||
    filters.value.searchPathologist ||
    filters.value.dateFrom ||
    filters.value.dateTo ||
    filters.value.selectedEntity ||
    filters.value.selectedStatus ||
    filters.value.selectedTest
  )
})

function reload() {
  loadCases(false)
}
function exportExcel() {
  exportCasesToExcel(filteredCases.value)
}
function performCase(_c: any) {}
function editCase(c: any) {
  const code = c?.caseCode || c?.id || ''
  if (!code) return
  router.push({ name: 'cases-edit', params: { code }, query: { auto: '1' } })
}
function previewCase(_c: any) {}

const handleCaseCreated = (_event: CustomEvent) => {
  loadCases()
}

onMounted(() => {
  window.addEventListener('case-created', handleCaseCreated as EventListener)
})

onUnmounted(() => {
  window.removeEventListener('case-created', handleCaseCreated as EventListener)
})

const columns = [
  { key: 'select', label: '', sortable: false, width: 'w-12' },
  { key: 'caseCode', label: 'Código', sortable: true, width: 'w-32' },
  { key: 'patient.dni', label: 'Cédula', sortable: true, width: 'w-32' },
  { key: 'patient.fullName', label: 'Paciente', sortable: true, width: 'w-48' },
  { key: 'pathologist', label: 'Patólogo', sortable: true, width: 'w-40' },
  { key: 'status', label: 'Estado', sortable: true, width: 'w-32' },
  { key: 'receivedAt', label: 'Recibido', sortable: true, width: 'w-32' },
  { key: 'deliveredAt', label: 'Entregado', sortable: true, width: 'w-32' },
  { key: 'actions', label: 'Acciones', sortable: false, width: 'w-32' },
]
</script>

<style scoped>
/* Estilos específicos para casos anteriores si es necesario */
</style>
