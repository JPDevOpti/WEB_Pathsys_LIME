<template>
  <ComponentCard title="Solicitudes de Pruebas Complementarias" description="Lista de solicitudes de pruebas complementarias que requieren aprobación para proceder.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </template>

    <div class="space-y-6">
      <div class="flex flex-col md:flex-row gap-3">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar Solicitud</label>
          <div class="flex gap-2">
            <div class="flex-1">
              <FormInputField 
                v-model="searchTerm" 
                placeholder="Código del caso (Ejemplo: 2025-00001)" 
                :max-length="100" 
                @keyup.enter="handleSearch"
              />
            </div>
            <SearchButton text="Buscar" size="md" variant="primary" @click="handleSearch" />
          </div>
        </div>
        <div class="flex gap-3 items-end">
          <div class="w-48">
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select v-model="selectedStatus" class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white">
              <option value="">Todos los estados</option>
              <option value="request_made">Solicitud Hecha</option>
              <option value="pending_approval">Pendiente de Aprobación</option>
              <option value="approved">Aprobado</option>
              <option value="rejected">Rechazado</option>
            </select>
          </div>
        </div>
      </div>

      <div class="space-y-4">
        <div v-if="filteredCases.length === 0" class="text-center py-8 text-gray-500">
          <svg class="w-12 h-12 mx-auto mb-4 text-gray-300" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
          </svg>
          <p class="text-lg font-medium">No hay solicitudes de pruebas complementarias</p>
          <p class="text-sm">Todas las solicitudes han sido procesadas o no hay solicitudes pendientes.</p>
        </div>

        <div v-else class="space-y-3">
          <div v-for="caseItem in filteredCases" :key="caseItem.id" class="border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-sm font-medium text-gray-900">Solicitud para {{ caseItem.caseCode }}</span>
                  <span :class="statusClasses(caseItem.status)">
                    {{ statusText(caseItem.status) }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-600">Caso Original</p>
                    <p class="font-medium">{{ caseItem.caseCode }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Patólogo Asignado</p>
                    <p class="font-medium">{{ getPathologistName(caseItem) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Fecha de Solicitud</p>
                    <p class="font-medium">{{ formatDate(caseItem.createdAt) }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Última Actualización</p>
                    <p class="font-medium">{{ formatDate(caseItem.updatedAt) }}</p>
                  </div>
                </div>

                <div class="mt-3">
                  <p class="text-sm text-gray-600">Motivo de la solicitud</p>
                  <p class="text-sm">{{ caseItem.description || 'Sin motivo especificado' }}</p>
                </div>
                
                <div class="mt-3" v-if="getCaseTests(caseItem).length">
                  <p class="text-sm text-gray-600">Pruebas Complementarias</p>
                  <div class="flex flex-wrap gap-1 mt-1">
                    <span
                      v-for="test in getCaseTests(caseItem)"
                      :key="test.code"
                      class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800"
                    >
                      {{ test.code }} - {{ test.name }} ({{ test.quantity }})
                    </span>
                  </div>
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
                
                <BaseButton
                  v-if="caseItem.status === 'request_made'"
                  variant="outline"
                  size="sm"
                  text="Revisar"
                  loading-text="Revisando..."
                  :loading="caseItem.managing"
                  :disabled="caseItem.rejecting || caseItem.approving"
                  custom-class="bg-white border-orange-600 text-orange-600 hover:bg-orange-50 focus:ring-orange-500"
                  @click="manageCase(caseItem.approvalCode)"
                />
                
                <BaseButton
                  v-if="caseItem.status === 'pending_approval'"
                  variant="outline"
                  size="sm"
                  text="Aprobar"
                  loading-text="Aprobando..."
                  :loading="caseItem.approving"
                  :disabled="caseItem.rejecting"
                  custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500"
                  @click="approveCase(caseItem.approvalCode)"
                />
                
                <BaseButton
                  v-if="caseItem.status === 'request_made' || caseItem.status === 'pending_approval'"
                  variant="outline"
                  size="sm"
                  text="Rechazar"
                  loading-text="Rechazando..."
                  :loading="caseItem.rejecting"
                  :disabled="caseItem.approving || caseItem.managing"
                  custom-class="bg-white border-red-600 text-red-600 hover:bg-red-50 focus:ring-red-500"
                  @click="rejectCase(caseItem.approvalCode)"
                />
              </div>
            </div>
          </div>
        </div>
      </div>

      <div v-if="total > 0" class="px-4 sm:px-5 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <div class="flex items-center gap-2 text-sm text-gray-500">
            <span>Mostrando</span>
            <select 
              :value="itemsPerPage" 
              @change="handleItemsPerPageChange(Number(($event.target as HTMLSelectElement)?.value))" 
              class="h-8 rounded-lg border border-gray-300 bg-white px-2 py-1 text-sm text-gray-700"
            >
              <option :value="5">5</option>
              <option :value="10">10</option>
              <option :value="20">20</option>
              <option :value="50">50</option>
              <option :value="100">100</option>
              <option :value="total">Todos</option>
            </select>
            <span>de {{ total }} resultados</span>
          </div>
          
          <div class="flex items-center justify-center gap-2">
            <button 
              @click="handlePageChange(currentPage - 1)" 
              :disabled="currentPage === 1" 
              class="px-3 py-1.5 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              <span class="hidden sm:inline">Anterior</span>
              <span class="sm:hidden">←</span>
            </button>
            
            <div class="flex items-center gap-1 text-sm text-gray-500">
              <span class="hidden sm:inline">Página</span>
              <span class="font-medium">{{ currentPage }}</span>
              <span class="hidden sm:inline">de</span>
              <span class="hidden sm:inline">{{ totalPages }}</span>
              <span class="sm:hidden">/ {{ totalPages }}</span>
            </div>
            
            <button 
              @click="handlePageChange(currentPage + 1)" 
              :disabled="currentPage === totalPages" 
              class="px-3 py-1.5 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              <span class="hidden sm:inline">Siguiente</span>
              <span class="sm:hidden">→</span>
            </button>
          </div>
        </div>
      </div>
    </div>
  </ComponentCard>
  <CaseApprovalDetailsModal
    :case-item="selectedApprovalCase"
    @close="closeModal"
    @tests-updated="handleTestsUpdated"
  />
  
  <ConfirmDialog
    v-model="showConfirmManage"
    title="Confirmar revisión"
    :message="`¿Desea marcar la solicitud del caso ${confirmData?.caseCode} como 'Pendiente de Aprobación'?`"
    confirm-text="Sí, revisar"
    cancel-text="Cancelar"
    :loading-confirm="confirmData?.loading || false"
    @confirm="confirmManageCase"
    @cancel="cancelConfirm"
  />

  <ConfirmDialog
    v-model="showConfirmApprove"
    title="Confirmar aprobación"
    :message="`¿Desea aprobar definitivamente la solicitud de pruebas complementarias para el caso ${confirmData?.caseCode}?`"
    confirm-text="Sí, aprobar"
    cancel-text="Cancelar"
    :loading-confirm="confirmData?.loading || false"
    @confirm="confirmApproveCase"
    @cancel="cancelConfirm"
  />

  <CaseCreatedToast v-model="createdToastVisible" :case-data="createdCase" />

  <ConfirmDialog
    v-model="showConfirmReject"
    title="Confirmar rechazo"
    :message="`¿Desea rechazar la solicitud de pruebas complementarias para el caso ${confirmData?.caseCode}?`"
    confirm-text="Sí, rechazar"
    cancel-text="Cancelar"
    :loading-confirm="confirmData?.loading || false"
    @confirm="confirmRejectCase"
    @cancel="cancelConfirm"
  />
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { ComponentCard, FormInputField, BaseButton, SearchButton } from '@/shared/components'
import ConfirmDialog from '@/shared/components/ui/feedback/ConfirmDialog.vue'
import CaseApprovalDetailsModal from './CaseApprovalDetailsModal.vue'
import { CaseCreatedToast } from '@/modules/case-list/components'
import approvalService from '@/shared/services/approval.service'
import type { 
  ApprovalRequestResponse, 
  ApprovalRequestSearch, 
  ApprovalState,
  ComplementaryTestInfo
} from '@/shared/services/approval.service'
import { useToasts } from '@/shared/composables/useToasts'

interface CaseToApprove {
  id: string
  approvalCode: string
  caseCode: string
  patientName: string
  pathologistName: string
  pathologistId?: string
  description?: string
  createdAt: string
  updatedAt: string
  status: ApprovalState
  approving: boolean
  rejecting: boolean
  managing: boolean
  complementaryTests: ComplementaryTestInfo[]
}

const searchTerm = ref('')
const loading = ref(false)
const errorMessage = ref('')
const cases = ref<CaseToApprove[]>([])
const total = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(20)
const selectedStatus = ref<string>('')

// Notificaciones
const { success, error: showError } = useToasts()

const mapBackendCase = (c: ApprovalRequestResponse): CaseToApprove => ({
  id: c.id,
  approvalCode: c.approval_code,
  caseCode: c.original_case_code,
  patientName: `Caso ${c.original_case_code}`,
  pathologistName: c.approval_info?.assigned_pathologist?.name || 'Sin asignar',
  pathologistId: c.approval_info?.assigned_pathologist?.id || '',
  description: c.approval_info?.reason || 'Sin motivo especificado',
  createdAt: c.created_at,
  updatedAt: c.updated_at,
  status: c.approval_state,
  approving: false,
  rejecting: false,
  managing: false,
  complementaryTests: c.complementary_tests || []
})

const statusClasses = (status: string) => {
  const base = 'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium'
  const colors = {
    request_made: 'bg-blue-100 text-blue-800',
    pending_approval: 'bg-yellow-100 text-yellow-800',
    approved: 'bg-green-100 text-green-800',
    rejected: 'bg-red-100 text-red-800'
  }
  return `${base} ${colors[status as keyof typeof colors] || 'bg-gray-100 text-gray-800'}`
}

const statusText = (status: string) => {
  const texts = {
    request_made: 'Solicitud Hecha',
    pending_approval: 'Pendiente de Aprobación',
    approved: 'Aprobado',
    rejected: 'Rechazado'
  }
  return texts[status as keyof typeof texts] || status
}

const fetchCases = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const searchPayload: ApprovalRequestSearch = {
      original_case_code: searchTerm.value.trim() || undefined,
      approval_state: selectedStatus.value as ApprovalState || undefined
    }
    const calculatedSkip = (currentPage.value - 1) * itemsPerPage.value
    const respData = await approvalService.searchApprovalRequests(searchPayload, calculatedSkip, itemsPerPage.value)
    const dataList: ApprovalRequestResponse[] = respData?.data || []
    total.value = respData?.total || dataList.length
    cases.value = dataList.map(mapBackendCase)
  } catch (e: any) {
    console.error('Error en fetchCases:', e)
    errorMessage.value = e.message || 'Error cargando casos'
  } finally {
    loading.value = false
  }
}

fetchCases()

let searchTimeout: NodeJS.Timeout | null = null

watch([selectedStatus], () => {
  currentPage.value = 1
  fetchCases()
})

watch(searchTerm, () => {
  currentPage.value = 1
  if (searchTimeout) clearTimeout(searchTimeout)
  searchTimeout = setTimeout(() => fetchCases(), 500)
})

const handleSearch = async () => {
  currentPage.value = 1
  await fetchCases()
}


const filteredCases = computed(() => cases.value)
const totalPages = computed(() => Math.ceil(total.value / itemsPerPage.value))

const handlePageChange = async (page: number) => {
  currentPage.value = page
  await fetchCases()
}

const handleItemsPerPageChange = async (newItemsPerPage: number) => {
  itemsPerPage.value = newItemsPerPage
  currentPage.value = 1
  await fetchCases()
}

const formatDate = (dateString: string): string => 
  new Date(dateString).toLocaleDateString('es-ES', {
    year: 'numeric',
    month: 'short',
    day: 'numeric',
    hour: '2-digit',
    minute: '2-digit'
  })

const getCaseTests = (caseItem: CaseToApprove) => caseItem.complementaryTests || []
const getPathologistName = (caseItem: CaseToApprove): string => 
  caseItem.pathologistName && caseItem.pathologistName !== 'Pendiente' 
    ? caseItem.pathologistName 
    : 'Pendiente'

const viewCase = async (caseId: string): Promise<void> => {
  const localCase = cases.value.find(ca => ca.id === caseId)
  if (!localCase) return

  try {
    selectedApprovalCase.value = await approvalService.getApprovalRequest(localCase.approvalCode)
  } catch (error) {
    console.error('Error al obtener detalles del caso:', error)
    selectedApprovalCase.value = {
      id: localCase.id,
      approval_code: localCase.approvalCode,
      original_case_code: localCase.caseCode,
      approval_state: localCase.status,
      complementary_tests: localCase.complementaryTests,
      approval_info: {
        reason: localCase.description || '',
        request_date: localCase.createdAt
      },
      created_at: localCase.createdAt,
      updated_at: localCase.updatedAt
    } as any as ApprovalRequestResponse
  }
}

const manageCase = async (approvalCode: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.approvalCode === approvalCode)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseItem.id,
    caseCode: caseItem.caseCode,
    approvalCode: approvalCode,
    loading: false
  }
  showConfirmManage.value = true
}

const approveCase = async (approvalCode: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.approvalCode === approvalCode)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseItem.id,
    caseCode: caseItem.caseCode,
    approvalCode: approvalCode,
    loading: false
  }
  showConfirmApprove.value = true
}

const confirmManageCase = async (): Promise<void> => {
  if (!confirmData.value) return
  
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  
  confirmData.value.loading = true
  caseItem.managing = true
  
  try {
    await approvalService.manageApprovalRequest(confirmData.value.approvalCode!)
    await fetchCases()
    showConfirmManage.value = false
    
    if (selectedApprovalCase.value && (selectedApprovalCase.value as any).id === confirmData.value.caseId) {
      closeModal()
    }
  } catch (error) {
    console.error('Error al gestionar caso:', error)
  } finally {
    caseItem.managing = false
    confirmData.value.loading = false
  }
}

const confirmApproveCase = async (): Promise<void> => {
  if (!confirmData.value) return
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  confirmData.value.loading = true
  caseItem.approving = true
  try {
    const result = await approvalService.approveRequest(confirmData.value.approvalCode!)
    await fetchCases()
    showConfirmApprove.value = false
    
    if (result.data?.new_case) {
      showSuccessNotification(result.data.new_case)
    }
    
    if (selectedApprovalCase.value && (selectedApprovalCase.value as any).id === confirmData.value.caseId) {
      closeModal()
    }
  } catch (error) {
    console.error('Error al aprobar caso:', error)
  } finally {
    caseItem.approving = false
    confirmData.value.loading = false
  }
}

const confirmRejectCase = async (): Promise<void> => {
  if (!confirmData.value) return
  
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  
  confirmData.value.loading = true
  caseItem.rejecting = true
  
  try {
    await approvalService.rejectRequest(confirmData.value.approvalCode!)
    await fetchCases()
    showConfirmReject.value = false
    
    if (selectedApprovalCase.value && (selectedApprovalCase.value as any).id === confirmData.value.caseId) {
      closeModal()
    }
  } catch (error) {
    console.error('Error al rechazar caso:', error)
    alert('Error al rechazar el caso. Por favor intente nuevamente.')
  } finally {
    caseItem.rejecting = false
    confirmData.value.loading = false
  }
}

const cancelConfirm = (): void => {
  showConfirmManage.value = false
  showConfirmApprove.value = false
  showConfirmReject.value = false
  confirmData.value = null
}

const rejectCase = async (approvalCode: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.approvalCode === approvalCode)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseItem.id,
    caseCode: caseItem.caseCode,
    approvalCode: approvalCode,
    loading: false
  }
  showConfirmReject.value = true
}

const selectedApprovalCase = ref<ApprovalRequestResponse | null>(null)
const showConfirmManage = ref(false)
const showConfirmApprove = ref(false)
const showConfirmReject = ref(false)
const confirmData = ref<{ caseId: string; caseCode: string; approvalCode: string; loading: boolean } | null>(null)

const closeModal = () => {
  selectedApprovalCase.value = null
}

const handleTestsUpdated = async (updatedTests: ComplementaryTestInfo[]) => {
  if (!selectedApprovalCase.value?.approval_code) {
    console.error('No hay código de aprobación para actualizar')
    return
  }
  
  try {
    await approvalService.updateApprovalRequest(selectedApprovalCase.value.approval_code, {
      complementary_tests: updatedTests
    })
    
    if (selectedApprovalCase.value) {
      selectedApprovalCase.value.complementary_tests = updatedTests
    }
    
    const caseItem = cases.value.find(c => c.approvalCode === selectedApprovalCase.value?.approval_code)
    if (caseItem) {
      caseItem.complementaryTests = updatedTests
    }
    
    await fetchCases()
    success('generic', 'Pruebas actualizadas', 'Las pruebas complementarias se han actualizado exitosamente')
  } catch (error: any) {
    console.error('Error al actualizar pruebas:', error)
    showError('generic', 'Error al actualizar', error.message || 'No se pudieron actualizar las pruebas complementarias')
  }
}

const createdCase = ref<any | null>(null)
const createdToastVisible = ref(false)

const showSuccessNotification = (caseData: any) => {
  createdCase.value = caseData
  createdToastVisible.value = true
}
</script>
