<template>
  <transition 
    enter-active-class="transition ease-out duration-300" 
    enter-from-class="opacity-0 transform scale-95" 
    enter-to-class="opacity-100 transform scale-100" 
    leave-active-class="transition ease-in duration-200" 
    leave-from-class="opacity-100 transform scale-100" 
    leave-to-class="opacity-0 transform scale-95"
  >
    <div
      v-if="approvalCase"
      :class="[
        'fixed right-0 bottom-0 z-[9999] flex items-end sm:items-center justify-center p-2 sm:p-4 bg-black/40',
        // Offset por header
        'top-16', // ~64px
        // Offset por sidebar en desktop
        overlayLeftClass
      ]"
      @click.self="$emit('close')"
    >
      <div class="relative bg-white w-full max-w-4xl rounded-t-2xl sm:rounded-2xl shadow-2xl h-[85vh] sm:h-auto sm:max-h-[90vh] overflow-y-auto overflow-x-hidden">
        <!-- Header -->
        <div class="sticky top-0 z-10 bg-white border-b border-gray-200 px-6 py-4 rounded-t-2xl flex items-center justify-between">
          <h3 class="text-xl font-semibold text-gray-900 flex items-center gap-2">
            <svg class="w-5 h-5 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z"/>
            </svg>
            Detalles de Solicitud de Pruebas Complementarias
          </h3>
          <button @click="$emit('close')" class="text-gray-400 hover:text-gray-600 p-2">
            <svg class="w-5 h-5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"/>
            </svg>
          </button>
        </div>

        <div class="p-6 space-y-6">
          <!-- Estado de la solicitud -->
          <div class="bg-gray-50 rounded-xl p-4">
            <div class="flex items-center justify-between">
              <h4 class="text-lg font-medium text-gray-900">Estado de la Solicitud</h4>
              <span 
                :class="[
                  'inline-flex items-center px-3 py-1 rounded-full text-sm font-medium',
                  approvalCase.estado_aprobacion === 'solicitud_hecha' ? 'bg-blue-100 text-blue-800' :
                  approvalCase.estado_aprobacion === 'pendiente_aprobacion' ? 'bg-yellow-100 text-yellow-800' :
                  approvalCase.estado_aprobacion === 'aprobado' ? 'bg-green-100 text-green-800' :
                  'bg-red-100 text-red-800'
                ]"
              >
                {{ getStatusLabel(approvalCase.estado_aprobacion) }}
              </span>
            </div>
            <div class="grid grid-cols-2 gap-4 mt-3">
              <div>
                <p class="text-sm text-gray-500">Fecha de solicitud</p>
                <p class="font-medium text-gray-900">{{ formatDate(approvalCase.fecha_creacion) }}</p>
              </div>
              <div>
                <p class="text-sm text-gray-500">Última actualización</p>
                <p class="font-medium text-gray-900">{{ formatDate(approvalCase.fecha_actualizacion) }}</p>
              </div>
            </div>
          </div>

          <!-- Información del caso original -->
          <div class="bg-gray-50 rounded-xl p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Información del Caso Original</h4>
            <div v-if="loadingOriginalCase" class="text-center py-4">
              <div class="animate-spin rounded-full h-6 w-6 border-b-2 border-blue-600 mx-auto"></div>
              <p class="text-sm text-gray-500 mt-2">Cargando información del caso...</p>
            </div>
            <div v-else-if="originalCaseError" class="text-center py-4">
              <p class="text-sm text-red-600">{{ originalCaseError }}</p>
            </div>
            <div v-else-if="originalCase" class="space-y-4">
              <!-- Información básica del caso -->
              <div class="grid grid-cols-2 md:grid-cols-3 gap-4">
                <div>
                  <p class="text-sm text-gray-500">Código del caso</p>
                  <p class="font-medium text-gray-900">{{ originalCase.caso_code }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Estado</p>
                  <p class="font-medium text-gray-900 capitalize">{{ originalCase.estado }}</p>
                </div>
                <div>
                  <p class="text-sm text-gray-500">Fecha de ingreso</p>
                  <p class="font-medium text-gray-900">{{ formatDate(originalCase.fecha_ingreso) }}</p>
                </div>
              </div>

              <!-- Información del paciente -->
              <div>
                <h5 class="text-sm font-medium text-gray-700 mb-2">Información del Paciente</h5>
                <div class="grid grid-cols-2 md:grid-cols-4 gap-4 bg-white border border-gray-200 rounded-lg p-3">
                  <div>
                    <p class="text-sm text-gray-500">Nombre</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.nombre || 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Código</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.paciente_code || 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Edad</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.edad ? `${originalCase.paciente.edad} años` : 'N/A' }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Sexo</p>
                    <p class="font-medium text-gray-900">{{ originalCase.paciente?.sexo || 'N/A' }}</p>
                  </div>
                </div>
              </div>

              <!-- Patólogo asignado -->
              <div v-if="originalCase.patologo_asignado">
                <h5 class="text-sm font-medium text-gray-700 mb-2">Patólogo Asignado</h5>
                <div class="bg-white border border-gray-200 rounded-lg p-3">
                  <p class="font-medium text-gray-900">{{ originalCase.patologo_asignado.nombre }}</p>
                  <p class="text-sm text-gray-500">Código: {{ originalCase.patologo_asignado.codigo }}</p>
                </div>
              </div>

              <!-- Muestras y pruebas del caso original -->
              <div v-if="originalCase.muestras && originalCase.muestras.length">
                <h5 class="text-sm font-medium text-gray-700 mb-2">Muestras del Caso Original</h5>
                <div class="space-y-2">
                  <div v-for="(muestra, index) in originalCase.muestras" :key="index" class="bg-white border border-gray-200 rounded-lg p-3">
                    <div class="mb-2">
                      <p class="text-sm text-gray-500">Región del cuerpo</p>
                      <p class="font-medium text-gray-900">{{ muestra.region_cuerpo || 'No especificada' }}</p>
                    </div>
                    <div v-if="muestra.pruebas && muestra.pruebas.length">
                      <p class="text-sm text-gray-500 mb-1">Pruebas realizadas</p>
                      <div class="flex flex-wrap gap-1">
                        <span
                          v-for="prueba in muestra.pruebas"
                          :key="prueba.id"
                          class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-gray-100 text-gray-700"
                        >
                          {{ prueba.id }} - {{ prueba.nombre }}
                        </span>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>

          <!-- Pruebas complementarias solicitadas -->
          <div class="bg-orange-50 border border-orange-200 rounded-xl p-4">
            <div class="flex items-center justify-between mb-3">
              <h4 class="text-lg font-medium text-gray-900 flex items-center gap-2">
                <svg class="w-5 h-5 text-orange-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
                </svg>
                Pruebas Complementarias Solicitadas
              </h4>
              <button
                v-if="canEditTests && !isEditingTests"
                @click="startEditingTests"
                class="inline-flex items-center px-3 py-1.5 text-sm font-medium text-orange-600 bg-orange-100 rounded-lg hover:bg-orange-200 transition-colors"
              >
                <svg class="w-4 h-4 mr-1" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M11 5H6a2 2 0 00-2 2v11a2 2 0 002 2h11a2 2 0 002-2v-5m-1.414-9.414a2 2 0 112.828 2.828L11.828 15H9v-2.828l8.586-8.586z"/>
                </svg>
                Editar
              </button>
            </div>
            
            <!-- Lista de pruebas -->
            <div class="space-y-2 mb-4">
              <div
                v-for="(test, index) in editedTests"
                :key="index"
                class="flex justify-between items-center bg-white border border-orange-200 rounded-lg p-3"
              >
                <div class="flex items-center gap-3">
                  <span class="inline-flex items-center px-2 py-1 rounded text-xs font-medium bg-orange-100 text-orange-800">
                    {{ test.codigo }}
                  </span>
                  <span class="font-medium text-gray-900">{{ test.nombre }}</span>
                </div>
                <div class="flex items-center gap-3">
                  <div v-if="isEditingTests" class="flex items-center gap-2">
                    <label class="text-sm text-gray-600">Cantidad:</label>
                    <input
                      v-model.number="test.cantidad"
                      type="number"
                      min="1"
                      max="20"
                      class="w-16 px-2 py-1 text-sm border border-gray-300 rounded focus:ring-2 focus:ring-orange-500 focus:border-orange-500"
                    />
                  </div>
                  <div v-else class="text-sm text-gray-600">
                    <span class="font-medium">Cantidad:</span> {{ test.cantidad }}
                  </div>
                  <button
                    v-if="isEditingTests"
                    @click="removeTest(index)"
                    class="text-red-500 hover:text-red-700 p-1"
                    title="Eliminar prueba"
                  >
                    <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                      <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 7l-.867 12.142A2 2 0 0116.138 21H7.862a2 2 0 01-1.995-1.858L5 7m5 4v6m4-6v6m1-10V4a1 1 0 00-1-1h-4a1 1 0 00-1 1v3M4 7h16"/>
                    </svg>
                  </button>
                </div>
              </div>
            </div>

            <!-- Botones de edición -->
            <div v-if="isEditingTests" class="flex gap-2 mb-4">
              <BaseButton
                variant="outline"
                size="sm"
                text="Guardar Cambios"
                @click="saveTestChanges"
                custom-class="bg-white border-green-600 text-green-600 hover:bg-green-50"
              />
              <BaseButton
                variant="outline"
                size="sm"
                text="Cancelar"
                @click="cancelTestEditing"
                custom-class="bg-white border-gray-600 text-gray-600 hover:bg-gray-50"
              />
            </div>

            <!-- Motivo de la solicitud -->
            <div>
              <h5 class="text-sm font-medium text-gray-700 mb-2">Motivo de la Solicitud</h5>
              <div class="bg-white border border-orange-200 rounded-lg p-3">
                <p class="text-gray-900">{{ approvalCase.aprobacion_info?.motivo || 'Sin motivo especificado' }}</p>
              </div>
            </div>
          </div>

          <!-- Información de gestión (si existe) -->
          <div v-if="approvalCase.aprobacion_info && (approvalCase.aprobacion_info.gestionado_por || approvalCase.aprobacion_info.aprobado_por)" class="bg-gray-50 rounded-xl p-4">
            <h4 class="text-lg font-medium text-gray-900 mb-3">Información de Gestión</h4>
            <div class="space-y-3">
              <div v-if="approvalCase.aprobacion_info.gestionado_por">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-500">Gestionado por</p>
                    <p class="font-medium text-gray-900">{{ approvalCase.aprobacion_info.gestionado_por }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Fecha de gestión</p>
                    <p class="font-medium text-gray-900">{{ approvalCase.aprobacion_info.fecha_gestion ? formatDate(approvalCase.aprobacion_info.fecha_gestion) : 'N/A' }}</p>
                  </div>
                </div>
                <div v-if="approvalCase.aprobacion_info.comentarios_gestion" class="mt-2">
                  <p class="text-sm text-gray-500">Comentarios de gestión</p>
                  <div class="bg-white border border-gray-200 rounded-lg p-2 mt-1">
                    <p class="text-sm text-gray-900">{{ approvalCase.aprobacion_info.comentarios_gestion }}</p>
                  </div>
                </div>
              </div>

              <div v-if="approvalCase.aprobacion_info.aprobado_por">
                <div class="grid grid-cols-2 gap-4">
                  <div>
                    <p class="text-sm text-gray-500">Aprobado por</p>
                    <p class="font-medium text-gray-900">{{ approvalCase.aprobacion_info.aprobado_por }}</p>
                  </div>
                  <div>
                    <p class="text-sm text-gray-500">Fecha de aprobación</p>
                    <p class="font-medium text-gray-900">{{ approvalCase.aprobacion_info.fecha_aprobacion ? formatDate(approvalCase.aprobacion_info.fecha_aprobacion) : 'N/A' }}</p>
                  </div>
                </div>
                <div v-if="approvalCase.aprobacion_info.comentarios_aprobacion" class="mt-2">
                  <p class="text-sm text-gray-500">Comentarios de aprobación</p>
                  <div class="bg-white border border-gray-200 rounded-lg p-2 mt-1">
                    <p class="text-sm text-gray-900">{{ approvalCase.aprobacion_info.comentarios_aprobacion }}</p>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Footer con botones -->
        <div class="sticky bottom-0 bg-white border-t border-gray-200 px-4 sm:px-6 py-3 sm:py-4 rounded-b-2xl">
          <div class="flex flex-col sm:flex-row justify-between items-stretch sm:items-center gap-3">
            <div class="flex justify-center sm:justify-start">
              <div class="text-sm text-gray-500">
                <span class="font-medium">Total de pruebas:</span>
                {{ approvalCase.pruebas_complementarias.reduce((sum, test) => sum + test.cantidad, 0) }}
              </div>
            </div>
            <div class="flex gap-2 justify-center sm:justify-end">
            <BaseButton
              variant="outline"
              size="md"
              text="Cerrar"
              @click="$emit('close')"
            />
            <BaseButton
              v-if="approvalCase.estado_aprobacion === 'solicitud_hecha'"
              variant="outline"
              size="md"
              text="Revisar"
              :loading="loadingManage"
              :disabled="loadingApprove || loadingReject || isEditingTests"
              custom-class="border-orange-600 text-orange-600 hover:bg-orange-50"
              @click="handleManage"
            />
            <BaseButton
              v-if="approvalCase.estado_aprobacion === 'pendiente_aprobacion'"
              variant="primary"
              size="md"
              text="Aprobar"
              :loading="loadingApprove"
              :disabled="loadingReject"
              custom-class="bg-green-600 hover:bg-green-700 border-green-600"
              @click="handleApprove"
            />
            <BaseButton
              v-if="approvalCase.estado_aprobacion === 'solicitud_hecha' || approvalCase.estado_aprobacion === 'pendiente_aprobacion'"
              variant="outline"
              size="md"
              text="Rechazar"
              :loading="loadingReject"
              :disabled="loadingApprove || loadingManage"
              custom-class="border-red-600 text-red-600 hover:bg-red-50"
              @click="handleReject"
            />
            </div>
          </div>
        </div>
      </div>
    </div>
  </transition>

  <!-- Dialog de confirmación para revisar -->
  <ConfirmDialog
    v-model="showConfirmManage"
    title="Confirmar revisión"
    :message="`¿Desea marcar la solicitud del caso ${approvalCase?.caso_original} como 'Pendiente de Aprobación'?`"
    confirm-text="Sí, revisar"
    cancel-text="Cancelar"
    :loading-confirm="loadingManage"
    @confirm="confirmManageAction"
    @cancel="cancelConfirmAction"
  />

  <!-- Dialog de confirmación para aprobar -->
  <ConfirmDialog
    v-model="showConfirmApprove"
    title="Confirmar aprobación"
    :message="`¿Desea aprobar definitivamente la solicitud de pruebas complementarias para el caso ${approvalCase?.caso_original}?`"
    confirm-text="Sí, aprobar"
    cancel-text="Cancelar"
    :loading-confirm="loadingApprove"
    @confirm="confirmApproveAction"
    @cancel="cancelConfirmAction"
  />
</template>

<script setup lang="ts">
import { ref, watch, computed } from 'vue'
import { BaseButton } from '@/shared/components'
import ConfirmDialog from '@/shared/components/feedback/ConfirmDialog.vue'
import casesApiService from '@/modules/cases/services/casesApi.service'
import casoAprobacionService from '@/modules/results/services/casoAprobacion.service'
import type { CasoAprobacionResponse } from '@/modules/results/services/casoAprobacion.service'
import { useSidebar } from '@/shared/composables/SidebarControl'

// Props
interface Props {
  approvalCase: CasoAprobacionResponse | null
}

const props = defineProps<Props>()

// Emits
const emit = defineEmits<{
  (e: 'close'): void
  (e: 'approve', caseId: string): void
  (e: 'reject', caseId: string): void
  (e: 'manage', caseId: string): void
  (e: 'tests-updated', tests: Array<{ codigo: string; nombre: string; cantidad: number }>): void
}>()

// Estado del componente
const originalCase = ref<any>(null)
const loadingOriginalCase = ref(false)
const originalCaseError = ref('')
const loadingApprove = ref(false)
const loadingReject = ref(false)
const loadingManage = ref(false)

// Estado para diálogos de confirmación
const showConfirmManage = ref(false)
const showConfirmApprove = ref(false)

// Estado para edición de pruebas
const isEditingTests = ref(false)
const editedTests = ref<Array<{ codigo: string; nombre: string; cantidad: number }>>([])
const originalTests = ref<Array<{ codigo: string; nombre: string; cantidad: number }>>([])

// Cargar información del caso original
const loadOriginalCase = async () => {
  if (!props.approvalCase?.caso_original) return
  
  loadingOriginalCase.value = true
  originalCaseError.value = ''
  
  try {
    originalCase.value = await casesApiService.getCaseByCode(props.approvalCase.caso_original)
  } catch (error: any) {
    originalCaseError.value = error.message || 'Error al cargar información del caso original'
  } finally {
    loadingOriginalCase.value = false
  }
}

// Computed properties
const canEditTests = computed(() => {
  return props.approvalCase?.estado_aprobacion === 'solicitud_hecha'
})


// Watchers
watch(() => props.approvalCase, (newCase) => {
  if (newCase) {
    loadOriginalCase()
    // Inicializar pruebas para edición
    editedTests.value = [...(newCase.pruebas_complementarias || [])]
    originalTests.value = [...(newCase.pruebas_complementarias || [])]
    isEditingTests.value = false
  }
}, { immediate: true })


// Funciones utilitarias
const formatDate = (dateString: string | null | undefined): string => {
  if (!dateString) return 'N/A'
  try {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return dateString
  }
}

const getStatusLabel = (status: string): string => {
  switch (status) {
    case 'solicitud_hecha': return 'Solicitud Hecha'
    case 'pendiente_aprobacion': return 'Pendiente de Aprobación'
    case 'aprobado': return 'Aprobado'
    case 'rechazado': return 'Rechazado'
    default: return status
  }
}

// Handlers para mostrar diálogos de confirmación
const handleManage = async () => {
  if (!props.approvalCase) return
  showConfirmManage.value = true
}

const handleApprove = async () => {
  if (!props.approvalCase) return
  showConfirmApprove.value = true
}

// Acciones confirmadas
const confirmManageAction = async () => {
  if (!props.approvalCase) return
  
  loadingManage.value = true
  try {
    emit('manage', (props.approvalCase as any).id || '')
  } finally {
    loadingManage.value = false
    showConfirmManage.value = false
  }
}

const confirmApproveAction = async () => {
  if (!props.approvalCase) return
  
  loadingApprove.value = true
  try {
    emit('approve', (props.approvalCase as any).id || '')
  } finally {
    loadingApprove.value = false
    showConfirmApprove.value = false
  }
}

// Cancelar confirmaciones
const cancelConfirmAction = () => {
  showConfirmManage.value = false
  showConfirmApprove.value = false
}

// Funciones para edición de pruebas
const startEditingTests = () => {
  isEditingTests.value = true
}

const removeTest = (index: number) => {
  editedTests.value.splice(index, 1)
}

const saveTestChanges = async () => {
  if (!props.approvalCase) return
  
  try {
    // Validar que al menos quede una prueba
    if (editedTests.value.length === 0) {
      alert('Debe mantener al menos una prueba complementaria')
      return
    }
    
    // Validar cantidades
    const invalidTest = editedTests.value.find(test => test.cantidad < 1 || test.cantidad > 20)
    if (invalidTest) {
      alert('Las cantidades deben estar entre 1 y 20')
      return
    }
    
    // Obtener el caso_original
    const casoOriginal = props.approvalCase?.caso_original || ''
    console.log('🔧 Updating case with caso_original:', casoOriginal)
    
    if (!casoOriginal) {
      alert('Error: No se pudo obtener el código del caso original')
      return
    }
    
    // Actualizar las pruebas en el backend
    await casoAprobacionService.updatePruebasComplementarias(
      casoOriginal, 
      editedTests.value
    )
    
    // Actualizar el estado local
    originalTests.value = [...editedTests.value]
    isEditingTests.value = false
    
    // Emitir evento para que el componente padre actualice
    emit('tests-updated', editedTests.value)
    
  } catch (error) {
    console.error('Error al guardar cambios en las pruebas:', error)
    alert('Error al guardar los cambios. Intente nuevamente.')
  }
}

const cancelTestEditing = () => {
  editedTests.value = [...originalTests.value]
  isEditingTests.value = false
}

const handleReject = async () => {
  if (!props.approvalCase) return
  loadingReject.value = true
  try {
    emit('reject', (props.approvalCase as any).id || '')
  } finally {
    loadingReject.value = false
  }
}

// Ajuste responsivo: respetar ancho del sidebar (colapsado/expandido) y su hover
const { isExpanded, isMobileOpen, isHovered } = useSidebar()

// En desktop (>= lg), cuando el sidebar está expandido u hovered, dejamos margen izquierdo ~18rem (w-72)
// Cuando está colapsado, dejamos ~5rem (w-20)
// En móvil, sidebar es overlay, así que sin margen (left: 0)
const overlayLeftClass = computed(() => {
  // Tailwind usa breakpoints; aquí usamos clases utilitarias fijas para left dinámico vía clases condicionales
  const hasWideSidebar = (isExpanded.value && !isMobileOpen.value) || (!isExpanded.value && isHovered.value)
  return hasWideSidebar ? 'left-0 lg:left-72' : 'left-0 lg:left-20'
})
</script>
