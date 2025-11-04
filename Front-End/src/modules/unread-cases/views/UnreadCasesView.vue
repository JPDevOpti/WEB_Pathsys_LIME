<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Casos sin lectura" />
    <div class="space-y-4">
      <!-- Loading State -->
      <Card v-if="isLoading">
        <div class="p-8 text-center">
          <LoadingSpinner />
        </div>
      </Card>

      <!-- Error State -->
      <Card v-else-if="error">
        <div class="p-8 text-center">
          <p class="text-red-600 mb-4">{{ error }}</p>
          <BaseButton size="sm" variant="primary" @click="reload">Reintentar</BaseButton>
        </div>
      </Card>

      <!-- Main Content -->
      <template v-else>
        <UnreadCasesFilters
          v-model="filters"
          :total-filtered="totalItems"
          :total-all="totalItems"
          :is-loading="isLoading"
          :can-export="totalItems > 0"
          @refresh="reload"
          @export="exportExcel"
          @search="applyFilters"
          @new-unread-case="openNewUnreadCaseDrawer"
        />

        <div class="bg-white rounded-xl border border-gray-200">
          <UnreadCasesTable
            :unreadCases="paginatedUnreadCases"
            :selected-ids="selectedUnreadCaseIds"
            :is-all-selected="isAllSelected"
            :columns="columns"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            :current-page="currentPage"
            :total-pages="totalPages"
            :items-per-page="itemsPerPage"
            :total-items="totalItems"
          :no-results-message="hasActiveFilters ? 'No se encontraron casos sin lectura con los filtros aplicados' : 'No hay casos sin lectura disponibles'"
            @toggle-select="toggleSelect"
            @toggle-select-all="toggleSelectAll"
            @clear-selection="selectedUnreadCaseIds = []"
            @sort="sortBy"
            @show-details="showDetails"
            @edit="editUnreadCase"
            @update-items-per-page="handleItemsPerPageChange"
            @prev-page="handlePrevPage"
            @next-page="handleNextPage"
            @refresh="loadUnreadCases"
            @update-unread-case="handleUpdateUnreadCaseFromTable"
            @batch-delivered="handleBatchDelivered"
          />
        </div>

        <UnreadCaseDetailsModal
          :unreadCase="selectedUnreadCase"
          @close="closeDetails"
          @edit="editUnreadCase"
        />

        <!-- New UnreadCase Drawer -->
        <NewUnreadCaseDrawer
          :is-open="isNewUnreadCaseDrawerOpen"
          @close="closeNewUnreadCaseDrawer"
          @save="handleSaveNewUnreadCase"
        />

        <!-- Edit UnreadCase Drawer -->
        <EditUnreadCaseDrawer
          :is-open="isEditUnreadCaseDrawerOpen"
          :unreadCase="unreadCaseToEdit"
          @close="closeEditUnreadCaseDrawer"
          @save="handleUpdateUnreadCase"
        />
      </template>
    </div>
  </AdminLayout>
</template>

<script setup lang="ts">
import { ref, computed, onMounted } from 'vue'
import { AdminLayout } from '@/shared/components/layout'
import PageBreadcrumb from '@/shared/components/navigation/PageBreadcrumb.vue'
import Card from '@/shared/components/layout/Card.vue'
import { BaseButton } from '@/shared/components'
import LoadingSpinner from '@/shared/components/ui/feedback/LoadingSpinner.vue'
import { usePermissions } from '@/shared/composables/usePermissions'
import {
  UnreadCasesTable,
  UnreadCasesFilters,
  UnreadCaseDetailsModal,
  NewUnreadCaseDrawer,
  EditUnreadCaseDrawer
} from '../components'
import { unreadCasesService } from '../services'
import type {
  UnreadCase,
  UnreadCaseFilters,
  Column,
  UnreadCaseCreatePayload,
  UnreadCaseUpdatePayload,
  BulkMarkDeliveredPayload,
  TestGroup
} from '../types'

// State
const isLoading = ref(false)
const error = ref<string | null>(null)
const unreadCases = ref<UnreadCase[]>([])
const totalItems = ref(0)
const selectedUnreadCaseIds = ref<string[]>([])
const selectedUnreadCase = ref<UnreadCase | null>(null)
const isNewUnreadCaseDrawerOpen = ref(false)
const isEditUnreadCaseDrawerOpen = ref(false)
const unreadCaseToEdit = ref<UnreadCase | null>(null)

// Permisos
const { isPatologo } = usePermissions()

// Filters
const filters = ref<UnreadCaseFilters>({
  searchQuery: '',
  dateFrom: '',
  dateTo: '',
  selectedInstitution: '',
  selectedTestType: '',
  selectedStatus: ''
})

// Pagination
const currentPage = ref(1)
const itemsPerPage = ref(25)
const sortKey = ref('entryDate')
const sortOrder = ref<'asc' | 'desc'>('desc')

// Columns definition
const columns: Column[] = [
  { key: 'caseCode', label: 'Código Caso', class: 'min-w-[120px]' },
  { key: 'patientName', label: 'Paciente / Documento', class: 'min-w-[200px]' },
  { key: 'institution', label: 'Institución', class: 'min-w-[150px]' },
  { key: 'tests', label: 'Pruebas', class: 'min-w-[200px]' },
  { key: 'numberOfPlates', label: 'N° Placas', class: 'min-w-[80px]' },
  { key: 'deliveredTo', label: 'Ingreso / Entrega', class: 'min-w-[150px]' },
  { key: 'status', label: 'Estado', class: 'min-w-[120px]' },
  { key: 'actions', label: 'Acciones', class: 'min-w-[100px]' }
]

// Computed
const hasActiveFilters = computed(() => {
  return !!(
    filters.value.searchQuery ||
    filters.value.selectedInstitution ||
    filters.value.selectedTestType ||
    filters.value.selectedStatus
  )
})

const paginatedUnreadCases = computed(() => unreadCases.value)

const totalPages = computed(() => {
  if (itemsPerPage.value <= 0) return 1
  return Math.max(1, Math.ceil(totalItems.value / itemsPerPage.value))
})

const isAllSelected = computed(() => {
  return paginatedUnreadCases.value.length > 0 &&
    paginatedUnreadCases.value.every(t => selectedUnreadCaseIds.value.includes(t.id))
})

// Methods
const loadUnreadCases = async () => {
  isLoading.value = true
  error.value = null
  try {
    const response = await unreadCasesService.list({
      page: currentPage.value,
      limit: itemsPerPage.value,
      searchQuery: filters.value.searchQuery || undefined,
      selectedInstitution: filters.value.selectedInstitution || undefined,
      selectedTestType: filters.value.selectedTestType || undefined,
      selectedStatus: filters.value.selectedStatus || undefined,
      dateFrom: filters.value.dateFrom || undefined,
      dateTo: filters.value.dateTo || undefined,
      sortKey: sortKey.value,
      sortOrder: sortOrder.value
    })

    unreadCases.value = response.items || []
    totalItems.value = response.total || 0
    const lastPage = Math.max(1, Math.ceil(totalItems.value / itemsPerPage.value))
    if (currentPage.value > lastPage) {
      currentPage.value = lastPage
      return await loadUnreadCases()
    }
    selectedUnreadCaseIds.value = []
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'Error al cargar los casos sin lectura'
  } finally {
    isLoading.value = false
  }
}

const reload = () => {
  loadUnreadCases()
}

const applyFilters = () => {
  currentPage.value = 1
  loadUnreadCases()
}

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
  currentPage.value = 1
  loadUnreadCases()
}

const handleItemsPerPageChange = (value: number) => {
  itemsPerPage.value = value
  currentPage.value = 1
  loadUnreadCases()
}

const handlePrevPage = () => {
  if (currentPage.value <= 1) return
  currentPage.value -= 1
  loadUnreadCases()
}

const handleNextPage = () => {
  if (currentPage.value >= totalPages.value) return
  currentPage.value += 1
  loadUnreadCases()
}

const toggleSelect = (id: string) => {
  const index = selectedUnreadCaseIds.value.indexOf(id)
  if (index > -1) {
    selectedUnreadCaseIds.value.splice(index, 1)
  } else {
    selectedUnreadCaseIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedUnreadCaseIds.value = selectedUnreadCaseIds.value.filter(
      id => !paginatedUnreadCases.value.some(t => t.id === id)
    )
  } else {
    const newIds = paginatedUnreadCases.value.map(t => t.id)
    selectedUnreadCaseIds.value = [...new Set([...selectedUnreadCaseIds.value, ...newIds])]
  }
}

const showDetails = (unreadCase: UnreadCase) => {
  selectedUnreadCase.value = unreadCase
}

const closeDetails = () => {
  selectedUnreadCase.value = null
}

const editUnreadCase = (unreadCase: UnreadCase) => {
  unreadCaseToEdit.value = unreadCase
  isEditUnreadCaseDrawerOpen.value = true
  // Cerrar el modal de detalles si está abierto
  selectedUnreadCase.value = null
}

// New UnreadCase Drawer functions
const openNewUnreadCaseDrawer = () => {
  if (isPatologo.value) return
  isNewUnreadCaseDrawerOpen.value = true
}

const closeNewUnreadCaseDrawer = () => {
  isNewUnreadCaseDrawerOpen.value = false
}

// Edit UnreadCase Drawer functions
const closeEditUnreadCaseDrawer = () => {
  isEditUnreadCaseDrawerOpen.value = false
  unreadCaseToEdit.value = null
}

const normalizeTestGroupsPayload = (groups: any[]): TestGroup[] => {
  if (!Array.isArray(groups)) return []
  return groups
    .filter(group => group && group.type)
    .map(group => ({
      type: group.type,
      tests: Array.isArray(group.tests)
        ? group.tests
            .filter((test: any) => test && test.code)
            .map((test: any) => ({
              code: test.code,
              quantity: Number(test.quantity) > 0 ? Number(test.quantity) : 1,
              name: test.name || undefined
            }))
        : []
    }))
}

const buildCreatePayload = (formData: any): UnreadCaseCreatePayload => {
  const normalizedGroups = normalizeTestGroupsPayload(formData.testGroups)
  const computedPlates = normalizedGroups.reduce((acc, group) => {
    return acc + group.tests.reduce((sum, test) => sum + test.quantity, 0)
  }, 0)

  const fullName = formData.isSpecialCase
    ? 'Caso Especial'
    : [formData.firstLastName, formData.secondLastName, formData.firstName, formData.secondName]
        .filter(Boolean)
        .join(' ')

  return {
    caseCode: formData.caseCode,
    isSpecialCase: !!formData.isSpecialCase,
    documentType: formData.isSpecialCase ? undefined : formData.documentType || undefined,
    patientDocument: formData.isSpecialCase ? undefined : formData.patientDocument || undefined,
    firstName: formData.isSpecialCase ? undefined : formData.firstName || undefined,
    secondName: formData.isSpecialCase ? undefined : formData.secondName || undefined,
    firstLastName: formData.isSpecialCase ? undefined : formData.firstLastName || undefined,
    secondLastName: formData.isSpecialCase ? undefined : formData.secondLastName || undefined,
    patientName: fullName || undefined,
    entityCode: formData.entityCode || undefined,
    entityName: formData.entityName || undefined,
    institution: formData.entityName || undefined,
    notes: formData.notes || undefined,
    testGroups: normalizedGroups.length ? normalizedGroups : undefined,
    numberOfPlates: formData.numberOfPlates || computedPlates,
    deliveredTo: formData.deliveredTo || undefined,
    deliveryDate: formData.deliveryDate || undefined,
    entryDate: formData.entryDate,
    receivedBy: formData.receivedBy || undefined,
    status: formData.status || 'En proceso',
    elaboratedBy: formData.elaboratedBy || undefined,
    receipt: formData.receipt || undefined
  }
}

const buildUpdatePayload = (data: any): UnreadCaseUpdatePayload => {
  const groupsPayload = Array.isArray(data.testGroups) ? normalizeTestGroupsPayload(data.testGroups) : undefined

  const payload: UnreadCaseUpdatePayload = {
    isSpecialCase: data.isSpecialCase,
    documentType: data.isSpecialCase ? undefined : data.documentType || undefined,
    patientDocument: data.isSpecialCase ? undefined : data.patientDocument || undefined,
    firstName: data.isSpecialCase ? undefined : data.firstName || undefined,
    secondName: data.isSpecialCase ? undefined : data.secondName || undefined,
    firstLastName: data.isSpecialCase ? undefined : data.firstLastName || undefined,
    secondLastName: data.isSpecialCase ? undefined : data.secondLastName || undefined,
    patientName: data.patientName || undefined,
    entityCode: data.entityCode || undefined,
    entityName: data.entityName || undefined,
    institution: data.institution || data.entityName || undefined,
    notes: data.notes || undefined,
    testGroups: groupsPayload,
    numberOfPlates: data.numberOfPlates,
    deliveredTo: data.deliveredTo || undefined,
    deliveryDate: data.deliveryDate || undefined,
    entryDate: data.entryDate,
    receivedBy: data.receivedBy || undefined,
    status: data.status || undefined,
    elaboratedBy: data.elaboratedBy || undefined,
    receipt: data.receipt || undefined
  }

  if ((payload.numberOfPlates === undefined || payload.numberOfPlates <= 0) && groupsPayload) {
    payload.numberOfPlates = groupsPayload.reduce((acc, group) => acc + group.tests.reduce((sum, test) => sum + test.quantity, 0), 0)
  }

  return payload
}

const handleSaveNewUnreadCase = async (formData: any) => {
  try {
    const payload = buildCreatePayload(formData)
    await unreadCasesService.create(payload)
    currentPage.value = 1
    await loadUnreadCases()
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'Error al crear el caso sin lectura'
  }
}

const handleUpdateUnreadCase = async (updatedUnreadCase: UnreadCase) => {
  try {
    const caseCode = updatedUnreadCase.caseCode
    if (!caseCode) {
      throw new Error('Código del caso sin lectura inválido')
    }

    const payload = buildUpdatePayload(updatedUnreadCase)
    const saved = await unreadCasesService.update(caseCode, payload)
    unreadCases.value = unreadCases.value.map(item => (item.id === saved.id ? saved : item))
    closeEditUnreadCaseDrawer()
    await loadUnreadCases()
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'Error al actualizar el caso sin lectura'
  }
}

const handleUpdateUnreadCaseFromTable = (unreadCaseId: string, updatedUnreadCase: UnreadCase) => {
  const index = unreadCases.value.findIndex(t => t.id === unreadCaseId)
  if (index !== -1) {
    unreadCases.value[index] = updatedUnreadCase
  }
}

const handleBatchDelivered = async (payload: BulkMarkDeliveredPayload) => {
  try {
    const updatedCases = await unreadCasesService.markDelivered(payload)
    if (updatedCases && updatedCases.length) {
      const updatedMap = new Map(updatedCases.map(item => [item.id, item]))
      unreadCases.value = unreadCases.value.map(item => updatedMap.get(item.id) || item)
    }
    await loadUnreadCases()
  } catch (err: any) {
    console.error(err)
    error.value = err?.message || 'Error al marcar los casos como completados'
  }
}

const exportExcel = () => {
  // TODO: Implement Excel export
  console.log('Export to Excel')
}

// Lifecycle
onMounted(() => {
  loadUnreadCases()
})
</script>

