<template>
  <ComponentCard title="Solicitudes de Pruebas Complementarias" description="Lista de solicitudes de pruebas complementarias que requieren aprobación para proceder.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </template>

    <div class="space-y-6">
      <!-- Filtros de búsqueda -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
        <div>
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar Solicitud</label>
          <div class="flex gap-2">
            <div class="flex-1">
              <FormInputField 
                v-model="searchTerm" 
                :label="undefined" 
                placeholder="Código del caso (ej: 2025-01009)" 
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
          <p class="text-lg font-medium">No hay solicitudes de pruebas complementarias</p>
          <p class="text-sm">Todas las solicitudes han sido procesadas o no hay solicitudes pendientes.</p>
        </div>

        <div v-else class="space-y-3">
          <div v-for="caseItem in filteredCases" :key="caseItem.id" class="border border-gray-200 rounded-lg p-4 bg-white hover:bg-gray-50 transition-colors">
            <div class="flex items-start justify-between">
              <div class="flex-1">
                <div class="flex items-center gap-3 mb-2">
                  <span class="text-sm font-medium text-gray-900">Solicitud para {{ caseItem.caseCode }}</span>
                  <span 
                    :class="[
                      'inline-flex items-center px-2.5 py-0.5 rounded-full text-xs font-medium',
                      caseItem.status === 'solicitud_hecha' ? 'bg-blue-100 text-blue-800' :
                      caseItem.status === 'pendiente_aprobacion' ? 'bg-yellow-100 text-yellow-800' :
                      caseItem.status === 'aprobado' ? 'bg-green-100 text-green-800' :
                      'bg-red-100 text-red-800'
                    ]"
                  >
                    {{ 
                      caseItem.status === 'solicitud_hecha' ? 'Solicitud Hecha' :
                      caseItem.status === 'pendiente_aprobacion' ? 'Pendiente de Aprobación' :
                      caseItem.status === 'aprobado' ? 'Aprobado' :
                      'Rechazado'
                    }}
                  </span>
                </div>
                
                <div class="grid grid-cols-1 md:grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-600">Caso Original</p>
                    <p class="font-medium">{{ caseItem.caseCode }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-600">Pruebas Solicitadas</p>
                    <p class="font-medium">{{ getCaseTestsCount(caseItem) }}</p>
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
                      :key="test.codigo"
                      class="inline-flex items-center px-2 py-1 rounded-md text-xs font-medium bg-blue-50 text-blue-800"
                    >
                      {{ test.codigo }} - {{ test.nombre }} ({{ test.cantidad }})
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
                
                <!-- Botón Revisar - Solo visible si es solicitud hecha -->
                <BaseButton
                  v-if="caseItem.status === 'solicitud_hecha'"
                  variant="outline"
                  size="sm"
                  text="Revisar"
                  loading-text="Revisando..."
                  :loading="caseItem.managing"
                  :disabled="caseItem.rejecting || caseItem.approving"
                  custom-class="bg-white border-orange-600 text-orange-600 hover:bg-orange-50 focus:ring-orange-500"
                  @click="manageCase(caseItem.id)"
                />
                
                <!-- Botón Aprobar - Solo visible si está pendiente de aprobación -->
                <BaseButton
                  v-if="caseItem.status === 'pendiente_aprobacion'"
                  variant="outline"
                  size="sm"
                  text="Aprobar"
                  loading-text="Aprobando..."
                  :loading="caseItem.approving"
                  :disabled="caseItem.rejecting"
                  custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50 focus:ring-green-500"
                  @click="approveCase(caseItem.id)"
                />
                
                <!-- Botón Rechazar - Visible para solicitud hecha y pendiente de aprobación -->
                <BaseButton
                  v-if="caseItem.status === 'solicitud_hecha' || caseItem.status === 'pendiente_aprobacion'"
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
    :approval-case="selectedApprovalCase"
    @close="closeModal"
    @approve="approveFromModal"
    @reject="rejectFromModal"
    @manage="manageFromModal"
    @tests-updated="handleTestsUpdated"
  />
  
  <!-- Dialog de confirmación para revisar -->
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

  <!-- Dialog de confirmación para aprobar -->
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
</template>

<script setup lang="ts">
import { computed, ref } from 'vue'
import { ComponentCard, FormInputField, BaseButton, PathologistList, SearchButton } from '@/shared/components'
import ConfirmDialog from '@/shared/components/feedback/ConfirmDialog.vue'
import CaseApprovalDetailsModal from './CaseApprovalDetailsModal.vue'
import casoAprobacionService from '@/modules/results/services/casoAprobacion.service'
import type { CasoAprobacionResponse, CasoAprobacionSearch } from '@/modules/results/services/casoAprobacion.service'
// Componente actualizado para trabajar con solicitudes de pruebas complementarias
// basado en la estructura real de la base de datos MongoDB

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
  status: 'solicitud_hecha' | 'pendiente_aprobacion' | 'aprobado' | 'rechazado'
  approving: boolean
  rejecting: boolean
  managing: boolean
  complementaryTests: Array<{ codigo: string; nombre: string; cantidad: number }>
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
  const backendId = (c as any).id || normalizeId((c as any)._id)
  return {
    id: backendId,
    caseCode: c.caso_original,
    patientName: `Caso ${c.caso_original}`, // No tenemos info del paciente directamente
    pathologistName: 'Patólogo Solicitante', // No tenemos info del patólogo directamente  
    pathologistId: c.aprobacion_info?.solicitado_por,
    description: c.aprobacion_info?.motivo || 'Sin motivo especificado',
    createdAt: c.fecha_creacion,
    updatedAt: c.fecha_actualizacion,
    status: c.estado_aprobacion,
    approving: false,
    rejecting: false,
    managing: false,
    complementaryTests: c.pruebas_complementarias || []
  }
}

const fetchCases = async () => {
  loading.value = true
  errorMessage.value = ''
  try {
    const term = (searchTerm.value || '').trim()
    const searchPayload: CasoAprobacionSearch = {
      caso_original: term || undefined,
      estado_aprobacion: undefined, // Obtener todos los estados
      solicitado_por: selectedPathologist.value || undefined
    }
    
    const respData = await casoAprobacionService.searchCasos(searchPayload, skip.value, limit.value)
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

const getCaseTestsCount = (caseItem: CaseToApprove): string => {
  if (!caseItem.complementaryTests || caseItem.complementaryTests.length === 0) {
    return 'Sin pruebas'
  }
  const totalTests = caseItem.complementaryTests.reduce((sum, test) => sum + (test.cantidad || 1), 0)
  return `${caseItem.complementaryTests.length} tipos (${totalTests} total)`
}

const getCaseTests = (caseItem: CaseToApprove) => {
  return caseItem.complementaryTests || []
}

const viewCase = async (caseId: string): Promise<void> => {
  // Buscar el caso en la lista local primero
  const localCase = cases.value.find(ca => ca.id === caseId)
  if (!localCase) return

  try {
    // Obtener los datos completos del caso de aprobación desde el backend
    const fullApprovalCase = await casoAprobacionService.getCasoAprobacion(caseId)
    selectedApprovalCase.value = fullApprovalCase
  } catch (error) {
    console.error('Error al obtener detalles del caso:', error)
    // Fallback: usar datos locales si falla la carga
    selectedApprovalCase.value = {
      caso_original: localCase.caseCode,
      estado_aprobacion: localCase.status as any,
      pruebas_complementarias: localCase.complementaryTests,
      aprobacion_info: {
        solicitado_por: localCase.pathologistId || '',
        fecha_solicitud: localCase.createdAt,
        motivo: localCase.description || '',
        gestionado_por: null,
        fecha_gestion: null,
        aprobado_por: null,
        fecha_aprobacion: null,
        comentarios_aprobacion: null,
        comentarios_gestion: null
      },
      fecha_creacion: localCase.createdAt,
      fecha_actualizacion: localCase.updatedAt
    } as any as CasoAprobacionResponse
  }
}

// Mostrar dialog de confirmación para revisar
const manageCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseId,
    caseCode: caseItem.caseCode,
    loading: false
  }
  showConfirmManage.value = true
}

// Mostrar dialog de confirmación para aprobar
const approveCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseId,
    caseCode: caseItem.caseCode,
    loading: false
  }
  showConfirmApprove.value = true
}

// Ejecutar revisión después de confirmación
const confirmManageCase = async (): Promise<void> => {
  if (!confirmData.value) return
  
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  
  confirmData.value.loading = true
  caseItem.managing = true
  
  try {
    await casoAprobacionService.gestionarCaso(confirmData.value.caseId, 'Solicitud revisada y pasada a pendiente de aprobación')
    await fetchCases()
    showConfirmManage.value = false
  } catch (error) {
    console.error('Error al gestionar caso:', error)
  } finally {
    caseItem.managing = false
    confirmData.value.loading = false
  }
}

// Ejecutar aprobación después de confirmación
const confirmApproveCase = async (): Promise<void> => {
  if (!confirmData.value) return
  
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  
  confirmData.value.loading = true
  caseItem.approving = true
  
  try {
    await casoAprobacionService.aprobarCaso(confirmData.value.caseId, 'Pruebas complementarias aprobadas')
    await fetchCases()
    showConfirmApprove.value = false
  } catch (error) {
    console.error('Error al aprobar caso:', error)
  } finally {
    caseItem.approving = false
    confirmData.value.loading = false
  }
}

// Cancelar confirmación
const cancelConfirm = (): void => {
  showConfirmManage.value = false
  showConfirmApprove.value = false
  confirmData.value = null
}

const rejectCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  caseItem.rejecting = true
  try {
    await casoAprobacionService.rechazarCaso(caseId, 'Caso rechazado')
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
const selectedApprovalCase = ref<CasoAprobacionResponse | null>(null)

// Estado para diálogos de confirmación
const showConfirmManage = ref(false)
const showConfirmApprove = ref(false)
const confirmData = ref<{ caseId: string; caseCode: string; loading: boolean } | null>(null)

const closeModal = () => {
  selectedApprovalCase.value = null
}

const approveFromModal = async (caseId: string) => {
  // El modal ya manejó la confirmación, ejecutar directamente
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  
  caseItem.approving = true
  try {
    await casoAprobacionService.aprobarCaso(caseId, 'Pruebas complementarias aprobadas')
    await fetchCases()
    closeModal()
  } catch (error) {
    console.error('Error al aprobar caso desde modal:', error)
  } finally {
    caseItem.approving = false
  }
}

const rejectFromModal = async (caseId: string) => {
  await rejectCase(caseId)
  closeModal()
  await fetchCases()
}

const manageFromModal = async (caseId: string) => {
  // El modal ya manejó la confirmación, ejecutar directamente
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  
  caseItem.managing = true
  try {
    await casoAprobacionService.gestionarCaso(caseId, 'Solicitud revisada y pasada a pendiente de aprobación')
    await fetchCases()
    closeModal()
  } catch (error) {
    console.error('Error al gestionar caso desde modal:', error)
  } finally {
    caseItem.managing = false
  }
}

const handleTestsUpdated = async (updatedTests: Array<{ codigo: string; nombre: string; cantidad: number }>) => {
  // Actualizar la lista local con las pruebas modificadas
  if (selectedApprovalCase.value) {
    selectedApprovalCase.value.pruebas_complementarias = updatedTests
  }
  
  // Actualizar también en la lista principal
  const caseItem = cases.value.find(c => c.id === (selectedApprovalCase.value as any)?.id)
  if (caseItem) {
    caseItem.complementaryTests = updatedTests
  }
  
  // Refrescar la lista completa para asegurar consistencia
  await fetchCases()
}


</script>
