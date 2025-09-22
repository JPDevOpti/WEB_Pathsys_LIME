<template>
  <ComponentCard title="Solicitudes de Pruebas Complementarias" description="Lista de solicitudes de pruebas complementarias que requieren aprobación para proceder.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
      </svg>
    </template>

    <div class="space-y-6">
      <!-- Filtros de búsqueda -->
      <div class="flex flex-col md:flex-row gap-3">
        <div class="flex-1">
          <label class="block text-sm font-medium text-gray-700 mb-1">Buscar Solicitud</label>
          <div class="flex gap-2">
            <div class="flex-1">
              <FormInputField 
                v-model="searchTerm" 
                :label="undefined" 
                placeholder="Código del caso (Ejemplo: 2025-00001)" 
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
        <div class="flex gap-3 items-end">
          <div class="w-64">
            <PathologistList v-model="selectedPathologist" label="Patólogo" placeholder="Buscar y seleccionar patólogo..." />
          </div>
          <div class="w-48">
            <label class="block text-sm font-medium text-gray-700 mb-1">Estado</label>
            <select 
              v-model="selectedStatus" 
              class="w-full px-3 py-2 border border-gray-300 rounded-lg focus:outline-none focus:ring-2 focus:ring-blue-400 focus:border-blue-400 transition-colors bg-white"
            >
              <option value="">Todos los estados</option>
              <option value="solicitud_hecha">Solicitud Hecha</option>
              <option value="pendiente_aprobacion">Pendiente de Aprobación</option>
              <option value="aprobado">Aprobado</option>
              <option value="rechazado">Rechazado</option>
            </select>
          </div>
          <div class="flex items-end">
            <BaseButton 
              size="sm" 
              variant="outline" 
              text="Limpiar" 
              @click="clearFilters"
            >
              <template #icon-left>
                <TrashIcon class="w-4 h-4 mr-1" />
              </template>
            </BaseButton>
          </div>
        </div>
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

      <!-- Paginación -->
      <div v-if="total > 0" class="px-4 sm:px-5 py-4 border-t border-gray-200 bg-gray-50 rounded-b-xl">
        <div class="flex flex-col sm:flex-row sm:items-center sm:justify-between gap-4">
          <!-- Información de resultados -->
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
          
          <!-- Navegación de páginas -->
          <div class="flex items-center justify-center gap-2">
            <button 
              @click="handlePageChange(currentPage - 1)" 
              :disabled="currentPage === 1" 
              class="px-3 py-1.5 border rounded-lg text-sm disabled:opacity-50 disabled:cursor-not-allowed hover:bg-gray-50 transition-colors"
            >
              <span class="hidden sm:inline">Anterior</span>
              <span class="sm:hidden">←</span>
            </button>
            
            <!-- Información de página -->
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
    :approval-case="selectedApprovalCase"
    @close="closeModal"
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

  <!-- Notificación de caso creado tras aprobar -->
  <CaseCreatedToast v-model="createdToastVisible" :case-data="createdCase" />

  <!-- Dialog de confirmación para rechazar -->
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
import { TrashIcon } from '@/assets/icons'
import ConfirmDialog from '@/shared/components/feedback/ConfirmDialog.vue'
import CaseApprovalDetailsModal from './CaseApprovalDetailsModal.vue'
import CaseCreatedToast from '../CurrentCases/CaseCreatedToast.vue'
import casoAprobacionService from '@/modules/results/services/casoAprobacion.service'
import type { CasoAprobacionResponse, CasoAprobacionSearch } from '@/modules/results/services/casoAprobacion.service'
import PathologistList from '@/shared/components/List/PathologistList.vue'

// Sin fechas; se filtra por patólogo
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
const loading = ref(false)
const errorMessage = ref('')
const cases = ref<CaseToApprove[]>([])
const total = ref(0)
const currentPage = ref(1)
const itemsPerPage = ref(20)

// Filtros
const selectedPathologist = ref<string>('')
const selectedStatus = ref<string>('')

// const authStore = useAuthStore()

const normalizeId = (raw: any): string => {
  if (!raw) return ''
  if (typeof raw === 'string') return raw
  if (typeof raw === 'object' && ('$oid' in raw)) return (raw as any).$oid as string
  return ''
}

const mapBackendCase = (c: CasoAprobacionResponse): CaseToApprove => {
  const backendId = (c as any).id || normalizeId((c as any)._id)
  
  // Obtener información del patólogo del caso original (ahora viene directamente en la respuesta)
  const patologoAsignado = (c.aprobacion_info as any)?.patologo_asignado
  let pathologistName = 'Pendiente'
  let pathologistId = ''
  
  if (patologoAsignado && patologoAsignado.nombre) {
    pathologistName = patologoAsignado.nombre
    pathologistId = patologoAsignado.codigo || ''
  }
  
  return {
    id: backendId,
    caseCode: c.caso_original,
    patientName: `Caso ${c.caso_original}`,
    pathologistName: pathologistName,
    pathologistId: pathologistId,
    description: c.aprobacion_info?.motivo || 'Sin motivo especificado',
    createdAt: c.fecha_creacion,
    updatedAt: c.fecha_creacion, // Usar fecha_creacion para ambos campos
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
      estado_aprobacion: selectedStatus.value || undefined,
      solicitado_por: selectedPathologist.value || undefined
    }
    
    // Debug: mostrar el payload que se envía
    console.log('🔍 Payload de búsqueda:', { 
      solicitado_por: searchPayload.solicitado_por, 
      estado_aprobacion: searchPayload.estado_aprobacion,
      fullPayload: searchPayload 
    })
    
    // Calcular skip basado en la página actual
    const calculatedSkip = (currentPage.value - 1) * itemsPerPage.value
    
    const respData = await casoAprobacionService.searchCasos(searchPayload, calculatedSkip, itemsPerPage.value)
    const dataList: CasoAprobacionResponse[] = respData?.data || []
    total.value = respData?.total || dataList.length
    cases.value = dataList.map(mapBackendCase)
    
    // Debug: mostrar resultados
    console.log('📊 Resultados encontrados:', {
      total: total.value,
      casos: cases.value.length,
      primerosCasos: cases.value.slice(0, 3).map(c => ({
        id: c.id,
        caseCode: c.caseCode,
        createdAt: c.createdAt,
        status: c.status
      }))
    })
  } catch (e: any) {
    console.error('❌ Error en fetchCases:', e)
    errorMessage.value = e.message || 'Error cargando casos'
  } finally {
    loading.value = false
  }
}

fetchCases()

// ============================================================================
// WATCHERS
// ============================================================================

// Watcher para ejecutar búsqueda automáticamente cuando cambien los filtros
watch([selectedPathologist, selectedStatus], () => {
  currentPage.value = 1
  fetchCases()
})

// Debounce para el término de búsqueda
let searchTimeout: NodeJS.Timeout | null = null

// Watcher para ejecutar búsqueda cuando cambie el término de búsqueda
watch(searchTerm, () => {
  currentPage.value = 1
  
  // Limpiar timeout anterior
  if (searchTimeout) {
    clearTimeout(searchTimeout)
  }
  
  // Debounce de 500ms
  searchTimeout = setTimeout(() => {
    fetchCases()
  }, 500)
})

// ============================================================================
// FUNCIONES DE FILTRADO
// ============================================================================

const handleSearch = async () => {
  currentPage.value = 1
  await fetchCases()
}

// Función para limpiar filtros
const clearFilters = () => {
  searchTerm.value = ''
  selectedPathologist.value = ''
  selectedStatus.value = ''
  currentPage.value = 1
}

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

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

const getCaseTests = (caseItem: CaseToApprove) => {
  return caseItem.complementaryTests || []
}

const getPathologistName = (caseItem: CaseToApprove): string => {
  // Retornar el nombre del patólogo si está disponible, sino "Pendiente"
  return caseItem.pathologistName && caseItem.pathologistName !== 'Pendiente' 
    ? caseItem.pathologistName 
    : 'Pendiente'
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
        motivo: localCase.description || '',
        patologo_asignado: localCase.pathologistName !== 'Pendiente' ? {
          codigo: '',
          nombre: localCase.pathologistName,
          firma: null
        } : null,
        fecha_aprobacion: null
      },
      fecha_creacion: localCase.createdAt
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
    await casoAprobacionService.gestionarCaso(confirmData.value.caseId)
    await fetchCases()
    showConfirmManage.value = false
    
    // Si el modal está abierto para este caso, cerrarlo
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

// Ejecutar aprobación después de confirmación
const confirmApproveCase = async (): Promise<void> => {
  if (!confirmData.value) return
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  confirmData.value.loading = true
  caseItem.approving = true
  try {
    const { nuevo_caso } = await casoAprobacionService.aprobarCaso(confirmData.value.caseId)
    await fetchCases()
    showConfirmApprove.value = false
    if (nuevo_caso) showSuccessNotification(nuevo_caso)
    
    // Si el modal está abierto para este caso, cerrarlo
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

// Ejecutar rechazo después de confirmación
const confirmRejectCase = async (): Promise<void> => {
  if (!confirmData.value) return
  
  const caseItem = cases.value.find(c => c.id === confirmData.value!.caseId)
  if (!caseItem) return
  
  confirmData.value.loading = true
  caseItem.rejecting = true
  
  try {
    await casoAprobacionService.rechazarCaso(confirmData.value.caseId)
    await fetchCases()
    showConfirmReject.value = false
    
    // Si el modal está abierto para este caso, cerrarlo
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

// Cancelar confirmación
const cancelConfirm = (): void => {
  showConfirmManage.value = false
  showConfirmApprove.value = false
  showConfirmReject.value = false
  confirmData.value = null
}

// Mostrar dialog de confirmación para rechazar
const rejectCase = async (caseId: string): Promise<void> => {
  const caseItem = cases.value.find(c => c.id === caseId)
  if (!caseItem) return
  
  confirmData.value = {
    caseId: caseId,
    caseCode: caseItem.caseCode,
    loading: false
  }
  showConfirmReject.value = true
}

// ============================================================================
// MODAL STATE & HELPERS
// ============================================================================
const selectedApprovalCase = ref<CasoAprobacionResponse | null>(null)

// Estado para diálogos de confirmación
const showConfirmManage = ref(false)
const showConfirmApprove = ref(false)
const showConfirmReject = ref(false)
const confirmData = ref<{ caseId: string; caseCode: string; loading: boolean } | null>(null)

const closeModal = () => {
  selectedApprovalCase.value = null
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

const createdCase = ref<any | null>(null)
const createdToastVisible = ref(false)

const showSuccessNotification = (caseData: any) => {
  createdCase.value = caseData
  createdToastVisible.value = true
}


</script>
