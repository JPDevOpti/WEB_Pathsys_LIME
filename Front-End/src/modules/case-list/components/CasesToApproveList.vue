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
                  <span class="text-sm font-medium text-gray-900">Caso {{ caseItem.caseCode }}</span>
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
import { computed, ref } from 'vue'
import { ComponentCard, FormInputField, BaseButton, PathologistList, SearchButton } from '@/shared/components'
import CaseApprovalDetailsModal from '../../cases/components/CaseApprovalDetailsModal.vue'
import type { CaseApprovalDetails } from '../../cases/types/case-approval.types'
import casoAprobacionService, { CasoAprobacionResponse, CasoAprobacionSearch } from '@/modules/cases/services/casoAprobacionApi.service'
// Nota: Los campos solicitado_por, costo y observaciones se han eliminado del modelo
// - solicitado_por: Se obtiene automáticamente del usuario autenticado
// - costo y observaciones: Eliminados de PruebaComplementaria por requerimiento

// ============================================================================
// INTERFACES Y TIPOS
// ============================================================================

interface CaseToApprove {
  id: string
  caseCode: string
  patientName: string
  pathologistName: string
  pathologistId?: string
  description?: string
  createdAt: string
  updatedAt: string
  status: 'pendiente' | 'gestionando' | 'aprobado' | 'rechazado'
  approving: boolean
  rejecting: boolean
  managing: boolean
}

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

const searchTerm = ref('')
const selectedPathologist = ref('')
const loading = ref(false)
const errorMessage = ref('')
const cases = ref<CaseToApprove[]>([])
const total = ref(0)
const skip = ref(0)
const limit = ref(20)

// const authStore = useAuthStore()

const normalizeId = (raw: any): string => {
  if (!raw) return ''
  if (typeof raw === 'string') return raw
  if (typeof raw === 'object' && ('$oid' in raw)) return (raw as any).$oid as string
  return ''
}

const mapBackendCase = (c: CasoAprobacionResponse): CaseToApprove => {
  const backendId = c.id || normalizeId((c as any)._id)
  return {
    id: backendId,
    caseCode: c.caso_aprobacion,
    patientName: c.paciente?.nombre || 'Sin paciente',
    pathologistName: c.patologo_asignado?.nombre || 'Sin patólogo',
    pathologistId: c.patologo_asignado?.codigo,
    description: c.aprobacion_info?.motivo,
    createdAt: c.fecha_creacion,
    updatedAt: c.fecha_actualizacion,
    status: c.estado_aprobacion,
    approving: false,
    rejecting: false,
    managing: false
  }
}

const fetchCases = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const term = (searchTerm.value || '').trim()
    const isAprobCode = term.startsWith('A-')
    const searchPayload: CasoAprobacionSearch = {
      query: term || undefined,
      paciente_nombre: term || undefined,
      caso_aprobacion: isAprobCode ? term : undefined,
      caso_code: !isAprobCode && term ? term : undefined,
      estado_aprobacion: undefined
    }
  const respData = await casoAprobacionService.searchCasosActive(searchPayload, skip.value, limit.value)
  const dataList: CasoAprobacionResponse[] = respData?.data || []
  total.value = respData?.total || dataList.length
    cases.value = dataList.map(mapBackendCase)
  } catch (e: any) {
    errorMessage.value = e.message || 'Error cargando casos'
  } finally {
    loading.value = false
  }
}

fetchCases()

// ============================================================================
// FUNCIONES DE FILTRADO
// ============================================================================

const handlePathologistFilter = async (pathologist: any) => {
  selectedPathologist.value = pathologist?.id || ''
  skip.value = 0
  await fetchCases()
}

const handleSearch = async () => {
  skip.value = 0
  await fetchCases()
}

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

const filteredCases = computed(() => cases.value)

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
  const c = cases.value.find(ca => ca.id === caseId)
  if (!c) return
  selectedCaseDetails.value = mapCaseToDetails(c)
}

const manageCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  caseItem.managing = true
  try {
    await casoAprobacionService.gestionarCaso(caseId)
    await fetchCases()
  } catch (error) {
    console.error('Error al gestionar caso:', error)
  } finally {
    caseItem.managing = false
  }
}

const approveCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  caseItem.approving = true
  try {
    await casoAprobacionService.aprobarCaso(caseId)
    await fetchCases()
  } catch (error) {
    console.error('Error al aprobar caso:', error)
  } finally {
    caseItem.approving = false
  }
}

const rejectCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  caseItem.rejecting = true
  try {
    await casoAprobacionService.rechazarCaso(caseId)
    await fetchCases()
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
  caseCode: c.caseCode,
  status: c.status,
  description: c.description,
  createdAt: c.createdAt,
  updatedAt: c.updatedAt,
  patient: { id: c.patientName, fullName: c.patientName },
  pathologist: c.pathologistName,
  newAssignedTests: [] // Se puede poblar con c.pruebas complementarias si se necesita
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
