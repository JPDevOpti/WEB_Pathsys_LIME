<template>
  <ComponentCard title="Casos Pendientes de Aprobación" description="Lista de casos que requieren revisión y aprobación antes de proceder.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </template>

    <div class="space-y-6">
      <!-- Filtros de búsqueda -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar Caso</label>
          <div class="flex gap-2">
            <div class="flex-1">
              <FormInputField 
                v-model="searchTerm" 
                :label="undefined" 
                placeholder="Número del caso o nombre del paciente" 
                :max-length="100" 
                @keyup.enter="handleSearch"
              />
            </div>
            <SearchButton 
              text="Buscar" 
              size="md" 
              variant="primary" 
              @click="handleSearch" 
            />
          </div>
        </div>
        <PathologistList 
          v-model="selectedPathologist" 
          label="Filtrar por Patólogo" 
          placeholder="Seleccionar patólogo..." 
          :required="false" 
          @pathologist-selected="handlePathologistFilter"
        />
      </div>

      <!-- Lista de casos -->
      <div class="space-y-4">
        <div v-if="filteredCases.length === 0" class="text-center py-8 text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p class="text-lg font-medium">No hay casos pendientes de aprobación</p>
          <p class="text-sm">Todos los casos han sido revisados o no hay casos en el sistema.</p>
        </div>

        <div v-else class="space-y-3">
          <div v-for="caseItem in filteredCases" :key="caseItem.id" class="border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-sm font-medium text-gray-900">Caso #{{ caseItem.id }}</span>
                  <span 
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      caseItem.status === 'pendiente' ? 'bg-yellow-100 text-yellow-800' :
                      caseItem.status === 'gestionando' ? 'bg-blue-100 text-blue-800' :
                      caseItem.status === 'aprobado' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ 
                      caseItem.status === 'pendiente' ? 'Pendiente' :
                      caseItem.status === 'gestionando' ? 'En Gestión' :
                      caseItem.status === 'aprobado' ? 'Aprobado' :
                      'Rechazado'
                    }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-600">Paciente</p>
                    <p class="font-medium">{{ caseItem.patientName }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Patólogo</p>
                    <p class="font-medium">{{ caseItem.pathologistName }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Fecha de Creación</p>
                    <p class="font-medium">{{ formatDate(caseItem.createdAt) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Última Actualización</p>
                    <p class="font-medium">{{ formatDate(caseItem.updatedAt) }}</p>
                  </div>
                </div>

                <div class="mt-3">
                  <p class="text-sm text-gray-600">Descripción</p>
                  <p class="text-sm">{{ caseItem.description || 'Sin descripción disponible' }}</p>
                </div>
              </div>

              <div class="flex flex-col gap-2 ml-4 w-36">
                <BaseButton
                  variant="outline"
                  size="sm"
                  text="Ver Detalles"
                  :disabled="caseItem.approving || caseItem.rejecting || caseItem.managing"
                  custom-class="bg-white border-blue-600 text-blue-600 hover:bg-blue-50 focus:ring-blue-500"
                  @click="viewCase(caseItem.id)"
                />
                
                <!-- Botón Gestionar - Solo visible si está pendiente -->
                <BaseButton
                  v-if="caseItem.status === 'pendiente'"
                  variant="outline"
                  size="sm"
                  text="Gestionar"
                  loading-text="Gestionando..."
                  :loading="caseItem.managing"
                  :disabled="caseItem.rejecting || caseItem.approving"
                  custom-class="bg-white border-orange-600 text-orange-600 hover:bg-orange-50 focus:ring-orange-500"
                  @click="manageCase(caseItem.id)"
                />
                
                <!-- Botón Aprobar - Solo visible si está en gestión -->
                <BaseButton
                  v-if="caseItem.status === 'gestionando'"
                  variant="outline"
                  size="sm"
                  text="Aprobar"
                  loading-text="Aprobando..."
                  :loading="caseItem.approving"
                  :disabled="caseItem.rejecting"
                  custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500"
                  @click="approveCase(caseItem.id)"
                />
                
                <!-- Botón Rechazar - Siempre visible excepto cuando ya está rechazado -->
                <BaseButton
                  v-if="caseItem.status !== 'rechazado' && caseItem.status !== 'aprobado'"
                  variant="outline"
                  size="sm"
                  text="Rechazar"
                  loading-text="Rechazando..."
                  :loading="caseItem.rejecting"
                  :disabled="caseItem.approving || caseItem.managing"
                  custom-class="bg-white border-red-600 text-red-600 hover:bg-red-50 focus:ring-red-500"
                  @click="rejectCase(caseItem.id)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>
    </div>
  </ComponentCard>
  <CaseApprovalDetailsModal
    :case-item="selectedCaseDetails"
    :loading-approve="modalApproving"
    :loading-reject="modalRejecting"
    @close="closeModal"
    @approve="approveFromModal"
    @reject="rejectFromModal"
  @preview="previewPdf"
  />
</template>

<script setup lang="ts">
import { computed, ref, reactive } from 'vue'
import { ComponentCard, FormInputField, BaseButton, PathologistList, SearchButton } from '@/shared/components'
import CaseApprovalDetailsModal from '../../cases/components/CaseApprovalDetailsModal.vue'
import type { CaseApprovalDetails } from '../../cases/types/case-approval.types'

// ============================================================================
// INTERFACES Y TIPOS
// ============================================================================

interface CaseToApprove {
  id: string
  patientName: string
  pathologistName: string
  pathologistId: string
  description?: string
  createdAt: string
  updatedAt: string
  status?: 'pendiente' | 'gestionando' | 'aprobado' | 'rechazado'
  approving?: boolean
  rejecting?: boolean
  managing?: boolean
}

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const searchTerm = ref('')
const selectedPathologist = ref('')

// Datos de ejemplo (en producción vendrían del backend)
const cases = reactive<CaseToApprove[]>([
  {
    id: 'CASE-001',
    patientName: 'María González López',
    pathologistName: 'Dr. Carlos Rodríguez',
    pathologistId: 'path-001',
    description: 'Biopsia de mama derecha - evaluación de lesión sospechosa',
    createdAt: '2024-01-15T10:30:00Z',
    updatedAt: '2024-01-16T14:20:00Z',
    status: 'pendiente',
    approving: false,
    rejecting: false,
    managing: false
  },
  {
    id: 'CASE-002',
    patientName: 'Juan Pérez Martínez',
    pathologistName: 'Dra. Ana García',
    pathologistId: 'path-002',
    description: 'Citología de ganglio linfático - posible linfoma',
    createdAt: '2024-01-16T09:15:00Z',
    updatedAt: '2024-01-16T16:45:00Z',
    status: 'gestionando',
    approving: false,
    rejecting: false,
    managing: false
  },
  {
    id: 'CASE-003',
    patientName: 'Carmen Silva Ruiz',
    pathologistName: 'Dr. Miguel Torres',
    pathologistId: 'path-003',
    description: 'Análisis histopatológico de piel - lesión pigmentada',
    createdAt: '2024-01-17T08:00:00Z',
    updatedAt: '2024-01-17T10:15:00Z',
    status: 'pendiente',
    approving: false,
    rejecting: false,
    managing: false
  }
])

// ============================================================================
// FUNCIONES DE FILTRADO
// ============================================================================

const handlePathologistFilter = (pathologist: any) => {
  selectedPathologist.value = pathologist?.id || ''
}

const handleSearch = () => {
  // Punto de extensión: aquí podrías disparar una llamada al backend si el filtrado fuera server-side
  console.log('Ejecutar búsqueda con término:', searchTerm.value)
}

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

const filteredCases = computed(() => {
  let filtered = cases

  if (searchTerm.value) {
    const term = searchTerm.value.toLowerCase()
    filtered = filtered.filter(caseItem => 
      caseItem.id.toLowerCase().includes(term) ||
      caseItem.patientName.toLowerCase().includes(term) ||
      caseItem.pathologistName.toLowerCase().includes(term)
    )
  }

  if (selectedPathologist.value) {
    filtered = filtered.filter(caseItem => 
      caseItem.pathologistId === selectedPathologist.value
    )
  }

  return filtered
})

// ============================================================================
// FUNCIONES
// ============================================================================

const formatDate = (dateString: string): string => {
  return new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })
}

const viewCase = (caseId: string): void => {
  const c = cases.find(ca => ca.id === caseId)
  if (!c) return
  selectedCaseDetails.value = mapCaseToDetails(c)
}

const manageCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.find(c => c.id === caseId)
  if (!caseItem) return

  caseItem.managing = true
  try {
    // Aquí se implementaría la llamada al backend para poner en gestión
    console.log('Gestionando caso:', caseId)
    await new Promise(resolve => setTimeout(resolve, 1500)) // Simulación
    
    // Cambiar estado a gestionando
    caseItem.status = 'gestionando'
    caseItem.updatedAt = new Date().toISOString()
  } catch (error) {
    console.error('Error al gestionar caso:', error)
  } finally {
    caseItem.managing = false
  }
}

const approveCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.find(c => c.id === caseId)
  if (!caseItem) return

  caseItem.approving = true
  try {
    // Aquí se implementaría la llamada al backend para aprobar
    console.log('Aprobando caso:', caseId)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulación
    
    // Cambiar estado a aprobado
    caseItem.status = 'aprobado'
    caseItem.updatedAt = new Date().toISOString()
    
    // Remover el caso de la lista (en producción se actualizaría el estado)
    const index = cases.findIndex(c => c.id === caseId)
    if (index > -1) {
      cases.splice(index, 1)
    }
  } catch (error) {
    console.error('Error al aprobar caso:', error)
  } finally {
    caseItem.approving = false
  }
}

const rejectCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.find(c => c.id === caseId)
  if (!caseItem) return

  caseItem.rejecting = true
  try {
    // Aquí se implementaría la llamada al backend para rechazar
    console.log('Rechazando caso:', caseId)
    await new Promise(resolve => setTimeout(resolve, 1000)) // Simulación
    
    // Cambiar estado a rechazado
    caseItem.status = 'rechazado'
    caseItem.updatedAt = new Date().toISOString()
    
    // Remover el caso de la lista (en producción se actualizaría el estado)
    const index = cases.findIndex(c => c.id === caseId)
    if (index > -1) {
      cases.splice(index, 1)
    }
  } catch (error) {
    console.error('Error al rechazar caso:', error)
  } finally {
    caseItem.rejecting = false
  }
}

// ============================================================================
// MODAL STATE & HELPERS
// ============================================================================
const selectedCaseDetails = ref<CaseApprovalDetails | null>(null)
const modalApproving = ref(false)
const modalRejecting = ref(false)

const closeModal = () => {
  selectedCaseDetails.value = null
  modalApproving.value = false
  modalRejecting.value = false
}

const mapCaseToDetails = (c: CaseToApprove): CaseApprovalDetails => ({
  id: c.id,
  caseCode: c.id,
  status: c.status || 'pendiente',
  description: c.description,
  createdAt: c.createdAt,
  updatedAt: c.updatedAt,
  patient: { id: 'N/A', fullName: c.patientName },
  pathologist: c.pathologistName,
  newAssignedTests: [
    { id: 'TEST-NEW-01', name: 'Inmunohistoquímica Panel A', quantity: 1 },
    { id: 'TEST-NEW-02', name: 'PCR Especial', quantity: 2 }
  ]
})

const approveFromModal = async (c: CaseApprovalDetails) => {
  modalApproving.value = true
  await approveCase(c.id)
  modalApproving.value = false
  closeModal()
}

const rejectFromModal = async (c: CaseApprovalDetails) => {
  modalRejecting.value = true
  await rejectCase(c.id)
  modalRejecting.value = false
  closeModal()
}

const previewPdf = (c: CaseApprovalDetails) => {
  console.log('Previsualizar PDF del caso', c.id)
  // TODO: integrar generación/descarga de PDF
}


</script>
