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
            :columns="columns"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            :current-page="currentPage"
            :total-pages="totalPages"
            :items-per-page="itemsPerPage"
            :total-items="filteredCases.length"
            :no-results-message="hasActiveFilters ? 'No se encontraron casos anteriores con los filtros aplicados' : 'No hay casos anteriores disponibles'"
            @sort="(k: any) => sortBy(k)"
            @show-details="showDetails"
            @edit="editCase"
            @validate="validateCase"
            @perform="performCase"
            @update-items-per-page="(v: number) => itemsPerPage = v"
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
import { AdminLayout } from '@/shared/components/layout'
import { useRouter } from 'vue-router'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import Card from '@/shared/components/layout/Card.vue'
import { BaseButton } from '@/shared/components'
import { RefreshIcon } from '@/shared/icons'
import LoadingSpinner from '@/shared/components/feedback/LoadingSpinner.vue'

import FiltersBar from '../components/FiltersBar.vue'
import CasesTable from '../components/CasesTable.vue'
import CaseDetailsModal from '../components/CaseDetailsModal.vue'

import { useCaseList } from '../composables/useCaseList'
import { useExcelExport } from '../composables/useExcelExport'

const pageTitle = 'Casos Anteriores'

const {
  // state
  cases,
  isLoading,
  error,
  filters,
  sortKey,
  sortOrder,
  currentPage,
  itemsPerPage,
  selectedCase,
  // derived
  filteredCases,
  paginatedCases,
  totalPages,
  // actions
  loadCases,
  sortBy,
  showDetails,
  closeDetails,
  validateCase,
  markAsCompleted,
} = useCaseList()

const { exportExcel } = useExcelExport()

// Listener para detectar cuando se crea un nuevo caso
const handleCaseCreated = (event: CustomEvent) => {
  loadCases()
}

onMounted(() => {
  // Agregar listener para eventos de creación de casos
  window.addEventListener('case-created', handleCaseCreated as EventListener)
})

onUnmounted(() => {
  // Limpiar listener al desmontar el componente
  window.removeEventListener('case-created', handleCaseCreated as EventListener)
})

// Configuración de columnas para la tabla
const columns = [
  { key: 'select', label: '', sortable: false, width: 'w-12' },
  { key: 'caseCode', label: 'Código', sortable: true, width: 'w-32' },
  { key: 'patient.dni', label: 'Cédula', sortable: true, width: 'w-32' },
  { key: 'patient.fullName', label: 'Paciente', sortable: true, width: 'w-48' },
  { key: 'pathologist', label: 'Patólogo', sortable: true, width: 'w-40' },
  { key: 'status', label: 'Estado', sortable: true, width: 'w-32' },
  { key: 'receivedAt', label: 'Recibido', sortable: true, width: 'w-32' },
  { key: 'deliveredAt', label: 'Entregado', sortable: true, width: 'w-32' },
  { key: 'actions', label: 'Acciones', sortable: false, width: 'w-32' }
]
</script>

<style scoped>
/* Estilos específicos para casos anteriores si es necesario */
</style>
