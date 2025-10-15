<template>
  <AdminLayout>
    <PageBreadcrumb pageTitle="Técnicas Complementarias" />
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
        <ComplementaryTechniquesFilters
          v-model="filters"
          :total-filtered="filteredTechniques.length"
          :total-all="techniques.length"
          :is-loading="isLoading"
          :can-export="filteredTechniques.length > 0"
          @refresh="reload"
          @export="exportExcel"
          @search="applyFilters"
          @new-technique="openNewTechniqueDrawer"
        />

        <div class="bg-white rounded-xl border border-gray-200">
          <ComplementaryTechniquesTable
            :techniques="paginatedTechniques"
            :selected-ids="selectedTechniqueIds"
            :is-all-selected="isAllSelected"
            :columns="columns"
            :sort-key="sortKey"
            :sort-order="sortOrder"
            :current-page="currentPage"
            :total-pages="totalPages"
            :items-per-page="itemsPerPage"
            :total-items="filteredTechniques.length"
            :no-results-message="hasActiveFilters ? 'No se encontraron técnicas con los filtros aplicados' : 'No hay técnicas complementarias disponibles'"
            @toggle-select="toggleSelect"
            @toggle-select-all="toggleSelectAll"
            @clear-selection="selectedTechniqueIds = []"
            @sort="sortBy"
            @show-details="showDetails"
            @edit="editTechnique"
            @update-items-per-page="(v: number) => itemsPerPage = v"
            @prev-page="() => currentPage--"
            @next-page="() => currentPage++"
            @refresh="loadTechniques"
            @update-technique="handleUpdateTechniqueFromTable"
          />
        </div>

        <ComplementaryTechniqueDetailsModal
          :technique="selectedTechnique"
          @close="closeDetails"
          @edit="editTechnique"
        />

        <!-- New Technique Drawer -->
        <NewComplementaryTechniqueDrawer
          :is-open="isNewTechniqueDrawerOpen"
          @close="closeNewTechniqueDrawer"
          @save="handleSaveNewTechnique"
        />

        <!-- Edit Technique Drawer -->
        <EditComplementaryTechniqueDrawer
          :is-open="isEditTechniqueDrawerOpen"
          :technique="techniqueToEdit"
          @close="closeEditTechniqueDrawer"
          @save="handleUpdateTechnique"
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
  ComplementaryTechniquesTable,
  ComplementaryTechniquesFilters,
  ComplementaryTechniqueDetailsModal,
  NewComplementaryTechniqueDrawer,
  EditComplementaryTechniqueDrawer
} from '../components'
import type { ComplementaryTechnique, ComplementaryTechniqueFilters, Column } from '../types'

// State
const isLoading = ref(false)
const error = ref<string | null>(null)
const techniques = ref<ComplementaryTechnique[]>([])
const selectedTechniqueIds = ref<string[]>([])
const selectedTechnique = ref<ComplementaryTechnique | null>(null)
const isNewTechniqueDrawerOpen = ref(false)
const isEditTechniqueDrawerOpen = ref(false)
const techniqueToEdit = ref<ComplementaryTechnique | null>(null)

// Permisos
const { isPatologo } = usePermissions()

// Filters
const filters = ref<ComplementaryTechniqueFilters>({
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
  { key: 'deliveredTo', label: 'Entrega / Fecha', class: 'min-w-[150px]' },
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

const filteredTechniques = computed(() => {
  let result = [...techniques.value]

  // Filter by search query (case code, patient document or patient name)
  if (filters.value.searchQuery) {
    const query = filters.value.searchQuery.toLowerCase()
    result = result.filter(t =>
      t.caseCode.toLowerCase().includes(query) ||
      (t.patientDocument?.toLowerCase().includes(query) ?? false) ||
      (t.patientName?.toLowerCase().includes(query) ?? false)
    )
  }

  // Filter by institution
  if (filters.value.selectedInstitution) {
    const inst = filters.value.selectedInstitution.toLowerCase()
    result = result.filter(t => t.institution.toLowerCase().includes(inst))
  }

  // Filter by test type
  if (filters.value.selectedTestType) {
    const testType = filters.value.selectedTestType
    result = result.filter(t => {
      // Nuevo formato con testGroups
      if (t.testGroups && t.testGroups.length > 0) {
        return t.testGroups.some(group => {
          switch (testType) {
            case 'low_complexity':
              return group.type === 'LOW_COMPLEXITY_IHQ'
            case 'high_complexity':
              return group.type === 'HIGH_COMPLEXITY_IHQ'
            case 'special':
              return group.type === 'SPECIAL_IHQ'
            case 'histochemistry':
              return group.type === 'HISTOCHEMISTRY'
            default:
              return true
          }
        })
      }
      // Formato antiguo (retrocompatibilidad)
      switch (testType) {
        case 'low_complexity':
          return !!t.lowComplexityIHQ
        case 'high_complexity':
          return !!t.highComplexityIHQ
        case 'special':
          return !!t.specialIHQ
        case 'histochemistry':
          return !!t.histochemistry
        default:
          return true
      }
    })
  }

  // Filter by status
  if (filters.value.selectedStatus) {
    result = result.filter(t => t.status === filters.value.selectedStatus)
  }

  // Filter by date range (entry date)
  if (filters.value.dateFrom || filters.value.dateTo) {
    result = result.filter(t => {
      const techDate = new Date(t.entryDate)
      const fromDate = filters.value.dateFrom ? parseDate(filters.value.dateFrom) : null
      const toDate = filters.value.dateTo ? parseDate(filters.value.dateTo) : null

      if (fromDate && techDate < fromDate) return false
      if (toDate && techDate > toDate) return false
      return true
    })
  }

  return result
})

const sortedTechniques = computed(() => {
  const sorted = [...filteredTechniques.value]
  sorted.sort((a, b) => {
    const aVal = a[sortKey.value as keyof ComplementaryTechnique] as string
    const bVal = b[sortKey.value as keyof ComplementaryTechnique] as string
    
    if (!aVal || !bVal) return 0
    if (aVal === bVal) return 0
    const comparison = aVal > bVal ? 1 : -1
    return sortOrder.value === 'asc' ? comparison : -comparison
  })
  return sorted
})

const totalPages = computed(() => Math.ceil(filteredTechniques.value.length / itemsPerPage.value))

const paginatedTechniques = computed(() => {
  const start = (currentPage.value - 1) * itemsPerPage.value
  const end = start + itemsPerPage.value
  return sortedTechniques.value.slice(start, end)
})

const isAllSelected = computed(() => {
  return paginatedTechniques.value.length > 0 &&
    paginatedTechniques.value.every(t => selectedTechniqueIds.value.includes(t.id))
})

// Methods
const loadTechniques = async () => {
  isLoading.value = true
  error.value = null
  try {
    // TODO: Replace with actual API call
    await new Promise(resolve => setTimeout(resolve, 500))
    
    // Mock data based on CSV structure with new format
    techniques.value = [
      {
        id: '1',
        caseCode: 'TC2025-00001',
        isSpecialCase: false,
        patientDocument: '2582768',
        patientName: 'RANGEL YUS INGRID PAOLA',
        documentType: 'CC',
        firstName: 'INGRID',
        secondName: 'PAOLA',
        firstLastName: 'RANGEL',
        secondLastName: 'YUS',
        institution: 'SURA',
        entityCode: 'SURA001',
        entityName: 'SURA EPS',
        numberOfPlates: 1,
        deliveredTo: 'AMPR',
        deliveryDate: new Date('2025-07-02').toISOString(),
        entryDate: new Date('2025-07-01').toISOString(),
        receivedBy: 'JUAN BETANCUR',
        testGroups: [
          {
            type: 'HISTOCHEMISTRY',
            tests: [
              { code: 'ROJO_CONGO', quantity: 1, name: 'Rojo Congo' }
            ],
            observations: 'Muestra fijada en formol al 10%'
          }
        ],
        status: 'Completado',
        elaboratedBy: 'IMQ',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-07-01').toISOString(),
        updatedAt: new Date('2025-07-02').toISOString()
      },
      {
        id: '2',
        caseCode: 'TC2025-00002',
        isSpecialCase: false,
        patientDocument: '2582852',
        patientName: 'RUIZ URIBE SARA',
        documentType: 'CC',
        firstName: 'SARA',
        firstLastName: 'RUIZ',
        secondLastName: 'URIBE',
        institution: 'SURA',
        entityCode: 'SURA001',
        entityName: 'SURA EPS',
        numberOfPlates: 1,
        deliveredTo: 'IMQ',
        deliveryDate: new Date('2025-07-03').toISOString(),
        entryDate: new Date('2025-07-01').toISOString(),
        receivedBy: 'JULIO CARVAJAL',
        testGroups: [
          {
            type: 'LOW_COMPLEXITY_IHQ',
            tests: [
              { code: 'CMV', quantity: 1, name: 'Citomegalovirus' }
            ]
          }
        ],
        status: 'Completado',
        elaboratedBy: 'IMQ',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-07-01').toISOString(),
        updatedAt: new Date('2025-07-03').toISOString()
      },
      {
        id: '3',
        caseCode: 'TC2025-00003',
        isSpecialCase: false,
        patientDocument: '1073987364',
        patientName: 'ALNER DAVID ACOSTA OVIEDO',
        documentType: 'CC',
        firstName: 'ALNER',
        secondName: 'DAVID',
        firstLastName: 'ACOSTA',
        secondLastName: 'OVIEDO',
        institution: 'CES',
        entityCode: 'CES001',
        entityName: 'CES Universidad',
        numberOfPlates: 3,
        deliveredTo: 'IMQ',
        deliveryDate: new Date('2025-07-02').toISOString(),
        entryDate: new Date('2025-07-01').toISOString(),
        receivedBy: 'CESAR ORTIZ',
        testGroups: [
          {
            type: 'HISTOCHEMISTRY',
            tests: [
              { code: 'ZN', quantity: 1, name: 'Ziehl Neelsen' },
              { code: 'ZNMOD', quantity: 1, name: 'ZN Modificado' },
              { code: 'PM', quantity: 1, name: 'PAS Mucicarmín' }
            ],
            observations: 'Requiere control de calidad adicional'
          }
        ],
        status: 'Completado',
        elaboratedBy: 'IMQ',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-07-01').toISOString(),
        updatedAt: new Date('2025-07-02').toISOString()
      },
      {
        id: '4',
        caseCode: 'TC2025-00004',
        isSpecialCase: true,
        patientName: 'Caso Especial',
        institution: 'HPTU',
        entityCode: 'HPTU001',
        entityName: 'Hospital Pablo Tobón Uribe',
        notes: 'Laboratorio externo - Caso especial',
        numberOfPlates: 1,
        deliveredTo: 'IMQ',
        deliveryDate: new Date('2025-07-09').toISOString(),
        entryDate: new Date('2025-07-03').toISOString(),
        receivedBy: 'JORGE CALDERON',
        testGroups: [
          {
            type: 'SPECIAL_IHQ',
            tests: [
              { code: 'IDH-1', quantity: 1, name: 'IDH-1' }
            ],
            observations: 'Urgente - Caso oncológico prioritario'
          }
        ],
        status: 'En proceso',
        elaboratedBy: 'IMQ',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-07-03').toISOString(),
        updatedAt: new Date('2025-07-03').toISOString()
      },
      {
        id: '5',
        caseCode: 'TC2025-00005',
        isSpecialCase: false,
        patientDocument: '15328764',
        patientName: 'JHON JAIRO ORREGO',
        documentType: 'CC',
        firstName: 'JHON',
        secondName: 'JAIRO',
        firstLastName: 'ORREGO',
        institution: 'AMERICAS',
        entityCode: 'AMER001',
        entityName: 'Clínica Las Américas',
        numberOfPlates: 1,
        deliveredTo: 'IMQ',
        deliveryDate: new Date('2025-07-09').toISOString(),
        entryDate: new Date('2025-07-04').toISOString(),
        receivedBy: 'WILSON CASTAÑO',
        testGroups: [
          {
            type: 'HISTOCHEMISTRY',
            tests: [
              { code: 'PAS_DIASTASA', quantity: 1, name: 'PAS Diastasa' }
            ]
          }
        ],
        status: 'Completado',
        elaboratedBy: 'APA',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-07-04').toISOString(),
        updatedAt: new Date('2025-07-09').toISOString()
      },
      {
        id: '6',
        caseCode: 'TC2025-00006',
        isSpecialCase: true,
        patientName: 'Caso Especial',
        institution: 'DST',
        entityCode: 'DST001',
        entityName: 'Laboratorio DST',
        notes: 'Laboratorio externo - Sin datos de paciente',
        numberOfPlates: 3,
        deliveredTo: 'IMQ',
        deliveryDate: new Date('2025-09-06').toISOString(),
        entryDate: new Date('2025-08-01').toISOString(),
        receivedBy: 'JHONATAN',
        testGroups: [
          {
            type: 'LOW_COMPLEXITY_IHQ',
            tests: [
              { code: 'MAP2', quantity: 3, name: 'MAP2' }
            ]
          }
        ],
        status: 'Completado',
        elaboratedBy: 'IMQ',
        receipt: 'FACTURAR',
        createdAt: new Date('2025-08-01').toISOString(),
        updatedAt: new Date('2025-09-06').toISOString()
      }
    ]
  } catch (e) {
    error.value = 'Error al cargar las técnicas complementarias'
    console.error(e)
  } finally {
    isLoading.value = false
  }
}

const reload = () => {
  loadTechniques()
}

const applyFilters = () => {
  currentPage.value = 1
}

const sortBy = (key: string) => {
  if (sortKey.value === key) {
    sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
  } else {
    sortKey.value = key
    sortOrder.value = 'asc'
  }
}

const toggleSelect = (id: string) => {
  const index = selectedTechniqueIds.value.indexOf(id)
  if (index > -1) {
    selectedTechniqueIds.value.splice(index, 1)
  } else {
    selectedTechniqueIds.value.push(id)
  }
}

const toggleSelectAll = () => {
  if (isAllSelected.value) {
    selectedTechniqueIds.value = selectedTechniqueIds.value.filter(
      id => !paginatedTechniques.value.some(t => t.id === id)
    )
  } else {
    const newIds = paginatedTechniques.value.map(t => t.id)
    selectedTechniqueIds.value = [...new Set([...selectedTechniqueIds.value, ...newIds])]
  }
}

const showDetails = (technique: ComplementaryTechnique) => {
  selectedTechnique.value = technique
}

const closeDetails = () => {
  selectedTechnique.value = null
}

const editTechnique = (technique: ComplementaryTechnique) => {
  techniqueToEdit.value = technique
  isEditTechniqueDrawerOpen.value = true
  // Cerrar el modal de detalles si está abierto
  selectedTechnique.value = null
}

// New Technique Drawer functions
const openNewTechniqueDrawer = () => {
  if (isPatologo.value) return
  isNewTechniqueDrawerOpen.value = true
}

const closeNewTechniqueDrawer = () => {
  isNewTechniqueDrawerOpen.value = false
}

// Edit Technique Drawer functions
const closeEditTechniqueDrawer = () => {
  isEditTechniqueDrawerOpen.value = false
  techniqueToEdit.value = null
}

const handleUpdateTechnique = (updatedTechnique: ComplementaryTechnique) => {
  // Encontrar el índice de la técnica a actualizar
  const index = techniques.value.findIndex(t => t.id === updatedTechnique.id)
  if (index !== -1) {
    techniques.value[index] = updatedTechnique
    console.log('Técnica actualizada:', updatedTechnique)
  }
  closeEditTechniqueDrawer()
}

const handleUpdateTechniqueFromTable = (techniqueId: string, updatedTechnique: ComplementaryTechnique) => {
  const index = techniques.value.findIndex(t => t.id === techniqueId)
  if (index !== -1) {
    techniques.value[index] = updatedTechnique
  }
}

const handleSaveNewTechnique = (formData: any) => {
  // Calculate total plates from testGroups
  let totalPlates = 0
  if (formData.testGroups) {
    formData.testGroups.forEach((group: any) => {
      if (group.tests) {
        group.tests.forEach((test: any) => {
          totalPlates += test.quantity || 0
        })
      }
    })
  }

  // Build patient name from name fields if not special case
  let fullPatientName = undefined
  if (!formData.isSpecialCase) {
    const nameParts = [
      formData.firstName,
      formData.secondName,
      formData.firstLastName,
      formData.secondLastName
    ].filter(Boolean)
    fullPatientName = nameParts.join(' ')
  }

  // Create new technique object
  const newTechnique: ComplementaryTechnique = {
    id: String(techniques.value.length + 1),
    caseCode: formData.caseCode,
    isSpecialCase: formData.isSpecialCase,
    documentType: formData.isSpecialCase ? undefined : formData.documentType,
    patientDocument: formData.isSpecialCase ? undefined : formData.patientDocument,
    firstName: formData.isSpecialCase ? undefined : formData.firstName,
    secondName: formData.isSpecialCase ? undefined : formData.secondName,
    firstLastName: formData.isSpecialCase ? undefined : formData.firstLastName,
    secondLastName: formData.isSpecialCase ? undefined : formData.secondLastName,
    patientName: formData.isSpecialCase ? 'Caso Especial' : fullPatientName,
    entityCode: formData.entityCode,
    entityName: formData.entityName,
    institution: formData.entityName,
    notes: formData.isSpecialCase ? formData.notes : undefined,
    testGroups: formData.testGroups,
    numberOfPlates: totalPlates,
    deliveredTo: formData.deliveredTo || 'Pendiente',
    deliveryDate: formData.deliveryDate ? new Date(formData.deliveryDate).toISOString() : new Date().toISOString(),
    entryDate: new Date(formData.entryDate).toISOString(),
    receivedBy: formData.receivedBy,
    status: formData.deliveryDate ? 'Completado' : 'En proceso',
    elaboratedBy: 'IMQ',
    receipt: 'FACTURAR',
    createdAt: new Date().toISOString(),
    updatedAt: new Date().toISOString()
  }

  // Add to techniques list (mock - replace with API call)
  techniques.value.unshift(newTechnique)
  
  console.log('New technique created:', newTechnique)
  
  // TODO: Replace with API call
  // await createTechniqueAPI(newTechnique)
}

const exportExcel = () => {
  // TODO: Implement Excel export
  console.log('Export to Excel')
}

const parseDate = (dateStr: string): Date => {
  const parts = dateStr.split('/')
  if (parts.length === 3) {
    return new Date(parseInt(parts[2]), parseInt(parts[1]) - 1, parseInt(parts[0]))
  }
  return new Date(dateStr)
}

// Lifecycle
onMounted(() => {
  loadTechniques()
})
</script>

