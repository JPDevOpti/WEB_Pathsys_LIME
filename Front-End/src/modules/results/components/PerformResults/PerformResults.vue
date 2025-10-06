<template>
  <div class="space-y-6">
    <div class="grid gap-6 items-start grid-cols-1 lg:grid-cols-3">
      <ComponentCard 
        :class="[
          'flex flex-col',
          'lg:col-span-2'
        ]" 
        :style="{ minHeight: caseFound ? (activeSection === 'method' ? 'auto' : '600px') : '160px' }"
        :dense="false"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <h2 class="text-lg font-semibold">
              {{ caseFound ? 'Realizar Resultados' : 'Buscar caso para realizar resultados' }}
            </h2>
            <p v-if="!caseFound" class="text-sm text-gray-500 mt-1">
              Ingresa el código del caso para acceder a los campos de método, cortes y diagnóstico
            </p>
          </div>
          <div v-if="caseDetails?.case_code" class="text-sm text-gray-500">
            <span class="font-medium">Caso:</span> {{ caseDetails.case_code }}
            <span class="mx-2">-</span>
            <span v-if="caseDetails.assigned_pathologist?.name" class="text-blue-600">
              {{ caseDetails.assigned_pathologist.name }}
            </span>
            <span v-else class="text-orange-600 italic">
              Sin patólogo asignado
            </span>
          </div>
        </div>

        <!-- Buscador de caso -->
        <div class="bg-gray-50 rounded-lg p-3 md:p-4 border border-gray-200 mb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Buscar caso
          </h3>


          <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-start md:items-center">
            <div class="flex-1">
              <FormInputField
                id="codigo-caso"
                :model-value="caseCode"
                @update:model-value="handleCaseCodeChange"
                type="text"
                placeholder="Ejemplo: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isLoadingSearch"
                @keydown.enter.prevent="searchCase"
                @keydown="keydownHandler"
                @paste="handlePaste"
                class="flex-1"
              />

            </div>

            <div class="flex gap-2 md:gap-3 md:mt-0 mt-2">
              <SearchButton
                v-if="!caseFound"
                text="Buscar"
                loading-text="Buscando..."
                :loading="isLoadingSearch"
                @click="searchCase"
                size="md"
                variant="primary"
              />

              <ClearButton
                v-if="caseFound"
                text="Limpiar"
                @click="clearSearch"
              />
            </div>
          </div>

          <!-- Mensaje de error de búsqueda -->
          <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <p class="text-sm text-red-600">{{ searchError }}</p>
            </div>
          </div>

        </div>

        <!-- Editor de resultados - Solo visible cuando se encuentra un caso -->
        <div v-if="caseFound" class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor
            :model-value="activeSection === 'method' ? (Array.isArray(sections[activeSection]) ? [...sections[activeSection]] : []) : sections[activeSection]"
            @update:model-value="updateSectionContent"
            :active-section="activeSection"
            @update:activeSection="activeSection = $event"
            :sections="sections"
            :show-validation="showValidation"
          >
            <template #footer>
              <div class="flex flex-wrap items-center gap-3 justify-end">
                <ClearButton :disabled="loading" @click="() => { showValidation = false; handleClearResults() }" />
                <SaveButton 
                  :disabled="saving || loading || !canSaveProgress || !canTranscribeByStatus" 
                  :loading="saving" 
                  :text="!canTranscribeByStatus ? 'No se puede guardar' : (canComplete ? 'Completar para Firma' : 'Guardar Progreso')" 
                  :loading-text="canComplete ? 'Completando...' : 'Guardando...'" 
                  @click="() => { showValidation = true; handleSaveAction() }"
                />
              </div>
            </template>
          </ResultEditor>

          <!-- Advertencia para casos que no están en proceso -->
          <div v-if="caseInfo?.case_code && !canTranscribeByStatus"
            class="mt-3 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <div>
                <p class="text-sm font-bold text-red-800">Estado no válido para transcripción</p>
                <p class="text-sm text-red-700 mt-1">
                  Solo se pueden transcribir resultados en casos con estado "En proceso".
                </p>
                <p class="text-xs text-red-600 mt-2">
                  Estado actual: <span class="font-semibold">{{ caseInfo?.state }}</span>
                </p>
              </div>
            </div>
          </div>

          <ValidationAlert
            :visible="!!validationMessage"
            class="mt-2"
            :errors="validationMessage ? [validationMessage] : []"
          />
          <ErrorMessage v-if="errorMessage" class="mt-2" :message="errorMessage" />
        </div>
        
        <ResultsActionNotification
          class="mt-3"
          :visible="notification.visible"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          :case-code="savedCaseCode || caseDetails?.case_code || props.sampleId"
          :saved-content="savedContent"
          context="save"
          @close="closeAndClearNotification"
        />
      </ComponentCard>

      <!-- Paneles laterales - Siempre visibles -->
      <div class="space-y-6">
        <ComponentCard>
          <PatientInfoCard 
            :patient="patient" 
            :loading="loading" 
            :previous-cases="previousCases" 
            @case-click="handleCaseClick"
          />
        </ComponentCard>
        <ComponentCard>
          <CaseDetailsCard :details="caseDetails" :loading="loading" />
        </ComponentCard>
      </div>
    </div>

    

    <!-- Modal de previsualización temporalmente deshabilitado -->

    <PreviousCaseDetailsModal
      v-if="selectedPreviousCase"
      :case-item="selectedPreviousCase as any"
      @close="selectedPreviousCase = null"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed, watch } from 'vue'
import { ComponentCard } from '@/shared/components'
import { ErrorMessage, ValidationAlert } from '@/shared/components/ui/feedback'
import { FormInputField } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton, SaveButton } from '@/shared/components/ui/buttons'
import ResultEditor from '../Shared/ResultEditor.vue'
import PatientInfoCard from '../Shared/PatientInfoCard.vue'
import CaseDetailsCard from '../Shared/CaseDetailsCard.vue'
import PreviousCaseDetailsModal from '../Shared/PreviousCaseDetailsModal.vue'
// import AttachmentsPanel from './AttachmentsPanel.vue'
import ResultsActionNotification from '../Shared/ResultsActionNotification.vue'
import { usePerformResults } from '../../composables/usePerformResults'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import casesApiService from '@/modules/cases/services/casesApi.service'
import resultsApiService from '../../services/resultsApiService'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'

interface Props { 
  sampleId: string
  autoSearch?: boolean
}
const props = defineProps<Props>()

const {
  loading, saving,
  patient, caseDetails,
  activeSection,
  errorMessage, validationMessage,
  isDirty,
  initialize, previousCases, sections,
  canSaveProgress, canComplete,
  onSaveDraft, onCompleteForSigning,
  loadCaseByCode
} = usePerformResults(props.sampleId)

// Mostrar validación en Método solo al intentar guardar/completar
const showValidation = ref(false)

// Composable para permisos y autenticación
const { isPatologo } = usePermissions()
const authStore = useAuthStore()

// Types
interface CaseInfo {
  case_code: string
  state: string
  assigned_pathologist?: {
    name: string
  }
}

interface PathologistInfo {
  name: string
}

interface CaseData {
  case_code: string
  state: string
  assigned_pathologist?: PathologistInfo
}

// Constants
const CASE_CODE_MAX_LENGTH = 10
const CASE_CODE_FORMAT_POSITION = 4
const IN_PROGRESS_STATE = 'EN_PROCESO'

onMounted(() => {
  initialize()
  
  // Si autoSearch está activado, ejecutar búsqueda automática
  if (props.autoSearch && props.sampleId) {
    executeAutomaticSearch()
  }
  
  // Escuchar evento para limpiar el buscador
  const handleClearSearch = () => {
    clearSearch()
  }
  window.addEventListener('clear-search', handleClearSearch)
  
  // Limpiar el event listener al desmontar
  onUnmounted(() => {
    window.removeEventListener('clear-search', handleClearSearch)
  })
})

// Watch para cambios en el sampleId
watch(() => props.sampleId, (newSampleId) => {
  if (newSampleId && props.autoSearch) {
    executeAutomaticSearch()
  }
}, { immediate: false })

// Confirmación al abandonar si hay cambios sin guardar
if (typeof window !== 'undefined') {
  window.addEventListener('beforeunload', (e) => {
    if (isDirty.value) {
      e.preventDefault()
      e.returnValue = ''
    }
  })
}

// ------------------------
// Buscador de casos (UI)
// ------------------------
const caseCode = ref('')
const isLoadingSearch = ref(false)
const caseFound = ref(false)
const searchError = ref('')
const caseInfo = ref<CaseInfo | null>(null)

// Estado para el modal de casos anteriores
const selectedPreviousCase = ref<CaseData | null>(null)

// Normaliza estados a formato de BD (mayúsculas y guiones bajos)
const normalizeStatus = (status: string): string => {
  if (!status) return status
  return status.toUpperCase().replace(/\s+/g, '_')
}

// Solo se puede transcribir si el caso está en estado "En proceso"
const canTranscribeByStatus = computed(() => {
  const estado = caseInfo.value?.state
  if (!estado) return false
  const normalizedStatus = normalizeStatus(estado)
  return normalizedStatus === IN_PROGRESS_STATE
})

const invalidStatusMessage = computed(() => {
  const estado = caseInfo.value?.state
  if (!estado) return ''
  const normalizedStatus = normalizeStatus(estado)
  if (normalizedStatus !== IN_PROGRESS_STATE) {
    return `Este caso está en estado "${estado}". Solo se pueden transcribir resultados en casos con estado "En proceso".`
  }
  return ''
})


// Estado para almacenar el contenido guardado para mostrar en la notificación
const savedContent = ref({
  method: [] as string[],
  macro: '',
  micro: '',
  diagnosis: ''
})
// Guardar el código del caso que se acaba de guardar para mostrar en la notificación
const savedCaseCode = ref('')


// Función helper para obtener el nombre del usuario actual
const getCurrentUserName = (): string | null => {
  if (!authStore.user) return null
  
  // Para patólogos, comparamos por NOMBRE
  const userName = authStore.user.name || authStore.user.email || null
  
  return userName
}

// Función helper para obtener el nombre del patólogo asignado
const getAssignedPathologistName = (caseData: CaseData): string | null => {
  return caseData?.assigned_pathologist?.name || null
}

const handleCaseCodeChange = (value: string) => {
  // Solo números y guión
  let cleanValue = value.replace(/[^\d-]/g, '')
  
  // Máximo chars
  cleanValue = cleanValue.slice(0, CASE_CODE_MAX_LENGTH)
  
  // Insertar guión después de 4 dígitos
  if (cleanValue.length >= CASE_CODE_FORMAT_POSITION && !cleanValue.includes('-')) {
    cleanValue = cleanValue.slice(0, CASE_CODE_FORMAT_POSITION) + '-' + cleanValue.slice(CASE_CODE_FORMAT_POSITION)
  }
  
  // Evitar múltiples guiones
  const parts = cleanValue.split('-')
  if (parts.length > 2) {
    cleanValue = parts[0] + '-' + parts.slice(1).join('')
  }
  
  // Asegurar guión en posición correcta
  if (cleanValue.includes('-') && cleanValue.indexOf('-') !== CASE_CODE_FORMAT_POSITION) {
    const digits = cleanValue.replace(/-/g, '')
    if (digits.length >= CASE_CODE_FORMAT_POSITION) {
      cleanValue = digits.slice(0, CASE_CODE_FORMAT_POSITION) + '-' + digits.slice(CASE_CODE_FORMAT_POSITION, 9)
    } else {
      cleanValue = digits
    }
  }
  
  caseCode.value = cleanValue
}

/**
 * Maneja la entrada de solo números en el campo de código de caso
 */
const keydownHandler = (event: KeyboardEvent) => {
  // Permitir teclas de control
  const controlKeys = ['Backspace', 'Delete', 'Tab', 'Escape', 'Enter', 'ArrowLeft', 'ArrowRight', 'Home', 'End']
  if (controlKeys.includes(event.key)) {
    return true
  }
  
  // Permitir combinaciones de teclas para copiar y pegar
  if ((event.ctrlKey || event.metaKey) && ['c', 'v', 'a'].includes(event.key)) {
    return true
  }
  
  // Permitir números y guión
  if (/[0-9-]/.test(event.key)) {
    return true
  }
  
  // Bloquear todas las demás teclas
  event.preventDefault()
  return false
}

/**
 * Maneja el evento de pegar desde el portapapeles
 */
const handlePaste = (event: ClipboardEvent) => {
  event.preventDefault()
  const pastedText = event.clipboardData?.getData('text') || ''
  
  if (pastedText) {
    // Usar la misma lógica que handleCaseCodeChange
    handleCaseCodeChange(pastedText)
  }
}

const searchCase = async () => {
  if (!caseCode.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso'
    return
  }
  
  isLoadingSearch.value = true
  searchError.value = ''
  caseFound.value = false
  
  try {
    const data = await casesApiService.getCaseByCode(caseCode.value.trim()) as CaseData
    
    // Validar permisos para patólogos
    if (isPatologo.value && authStore.user) {
      const assignedPathologist = getAssignedPathologistName(data)
      const currentUser = getCurrentUserName()
      
      if (!assignedPathologist) {
        throw new Error('Este caso no tiene un patólogo asignado.')
      }
      
      if (!currentUser) {
        throw new Error('No se pudo identificar tu nombre de usuario. Contacta al administrador.')
      }
      
      if (assignedPathologist !== currentUser) {
        throw new Error('No tienes permisos para acceder a este caso. Solo puedes acceder a casos donde estés asignado como patólogo.')
      }
    }
    
    // Validar que el caso se puede editar usando el nuevo endpoint
    try {
      const validationResult = await resultsApiService.validateCaseForEditing(caseCode.value.trim())
      if (validationResult && !validationResult.can_edit) {
        throw new Error(validationResult.message || 'Este caso no puede ser editado debido a su estado actual.')
      }
    } catch (validationError: unknown) {
      // Si el endpoint de validación falla, usar validación local como fallback
      const errorMessage = validationError instanceof Error ? validationError.message : 'Error de validación'
      console.warn('Validación remota falló, usando validación local:', errorMessage)
    }
    
    caseInfo.value = data
    caseFound.value = true
    // Poblar paneles desde el composable
    await loadCaseByCode(caseCode.value.trim())
  } catch (error: unknown) {
    caseFound.value = false
    caseInfo.value = null
    const errorMessage = error instanceof Error ? error.message : 'Error al buscar el caso'
    searchError.value = errorMessage
  } finally {
    isLoadingSearch.value = false
  }
}

const clearSearch = () => {
  caseCode.value = ''
  caseFound.value = false  // Siempre establecer a false
  searchError.value = ''
  caseInfo.value = null
  
  // Limpiar solo los datos del caso, pero mantener la notificación
  // Limpiar datos del composable manualmente sin usar onClear()
  patient.value = null
  caseDetails.value = null
  previousCases.value = []
  
  // Limpiar secciones del editor
  sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
  activeSection.value = 'method'
  
  // NO cerrar la notificación - se mantiene visible
}

// ------------------------
// Notificaciones de guardado
// ------------------------
const { notification, showSuccess, showError, closeNotification } = useNotifications()

const handleClearResults = () => {
  // Limpiar solo las secciones del editor, pero mantener la notificación
  sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
  activeSection.value = 'method'
  
  // NO cerrar la notificación - se mantiene visible
}


const handleSaveAction = async () => {
  // Evitar múltiples ejecuciones
  if (saving.value) return
  
  // Validar que el caso no esté completado
  if (!canTranscribeByStatus.value) {
    showError('Estado no válido', invalidStatusMessage.value, 0)
    return
  }
  
  // Capturar todo el estado INMEDIATAMENTE para evitar cambios durante la ejecución
  const currentState = {
    method: Array.isArray(sections.value?.method) ? [...sections.value.method] : [],
    macro: sections.value?.macro || '',
    micro: sections.value?.micro || '',
    diagnosis: sections.value?.diagnosis || '',
    isComplete: canComplete.value,
    caseCode: caseDetails?.value?.case_code || ''
  }
  
  try {
    // Ejecutar la operación de guardado
    const success = currentState.isComplete ? await onCompleteForSigning() : await onSaveDraft()
    
    if (success) {
      // Actualizar savedContent una sola vez
      savedContent.value = {
        method: currentState.method,
        macro: currentState.macro,
        micro: currentState.micro,
        diagnosis: currentState.diagnosis
      }
      // Guardar el código del caso para que la notificación lo muestre incluso si limpiamos el caso
      savedCaseCode.value = currentState.caseCode || ''
      
      // Mostrar notificación apropiada
      if (currentState.isComplete) {
        showSuccess('Caso listo para firmar', `El caso ${currentState.caseCode} ha sido completado y está listo para firma.`, 0)
      } else {
        // Mostrar solo título de éxito al guardar el progreso (sin mensaje detallado)
        showSuccess('¡Progreso guardado!', '', 0)
      }
      
      // Mantener los datos visibles tras guardar/completar
    } else {
      const action = currentState.isComplete ? 'completar el caso para firma' : 'guardar el progreso'
      showError('Error al procesar', errorMessage?.value || `No se pudo ${action}.`, 0)
    }
  } catch (error: unknown) {
    console.error('Error en handleSaveAction:', error)
    showError('Error inesperado', 'Ocurrió un error inesperado al procesar la solicitud.', 0)
  }
}

// Cerrar notificación y limpiar código de caso guardado
const closeAndClearNotification = () => {
  closeNotification()
  savedCaseCode.value = ''
}


// Función para ejecutar búsqueda automática
const executeAutomaticSearch = async () => {
  if (!props.sampleId) return
  
  try {
    // Simular que se escribió el código en el buscador
    caseCode.value = props.sampleId
    
    // Ejecutar la búsqueda automáticamente
    await searchCase()
  } catch (error: unknown) {
    console.error('Error en búsqueda automática:', error)
    searchError.value = 'Error al ejecutar búsqueda automática'
  }
}

// Función para actualizar el contenido de la sección activa
const updateSectionContent = (value: string | string[]) => {
  if (!sections.value) return
  
  // Crear una nueva copia del objeto para evitar mutaciones directas
  const newSections = { ...sections.value }
  
  if (activeSection.value === 'method') {
    // Para la sección method, esperamos un array
    newSections[activeSection.value] = Array.isArray(value) ? [...value] : []
  } else {
    // Para otras secciones, esperamos string
    newSections[activeSection.value] = Array.isArray(value) ? '' : value
  }
  
  // Asignar la nueva referencia
  sections.value = newSections
}

// Función para manejar el clic en casos anteriores
const handleCaseClick = async (caseItem: any) => {
  try {
    // Obtener el código del caso correctamente
    const caseCodeValue = caseItem.case_code
    if (!caseCodeValue) {
      console.error('No se encontró código de caso en:', caseItem)
      return
    }
    
    // Cargar el caso completo desde la base de datos
    const fullCase = await casesApiService.getCaseByCode(caseCodeValue) as CaseData
    selectedPreviousCase.value = fullCase
  } catch (error: unknown) {
    console.error('Error al cargar caso completo:', error)
    // Si falla, usar el caso básico
    selectedPreviousCase.value = caseItem
  }
}
</script>


