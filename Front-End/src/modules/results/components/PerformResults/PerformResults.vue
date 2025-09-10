<template>
  <div class="space-y-6">
    <div class="grid gap-6 items-start grid-cols-1 lg:grid-cols-3">
      <ComponentCard 
        :class="[
          'flex flex-col',
          casoEncontrado ? 'lg:col-span-2 min-h-[600px]' : 'lg:col-span-2 min-h-[160px]'
        ]" 
        :dense="false"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <h2 class="text-lg font-semibold">
              {{ casoEncontrado ? 'Realizar Resultados' : 'Buscar caso para realizar resultados' }}
            </h2>
            <p v-if="!casoEncontrado" class="text-sm text-gray-500 mt-1">
              Ingresa el código del caso para acceder a los campos de método, cortes y diagnóstico
            </p>
          </div>
          <div v-if="caseDetails?.caso_code" class="text-sm text-gray-500">
            <span class="font-medium">Caso:</span> {{ caseDetails.caso_code }}
            <span class="mx-2">-</span>
            <span v-if="caseDetails.patologo_asignado?.nombre" class="text-blue-600">
              {{ caseDetails.patologo_asignado.nombre }}
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
                :model-value="codigoCaso"
                @update:model-value="handleCodigoChange"
                type="text"
                placeholder="Ejemplo: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isLoadingSearch"
                @keydown.enter.prevent="buscarCaso"
                @keydown="keydownHandler"
                class="flex-1"
              />

            </div>

            <div class="flex gap-2 md:gap-3 md:mt-0 mt-2">
              <SearchButton
                v-if="!casoEncontrado"
                text="Buscar"
                loading-text="Buscando..."
                :loading="isLoadingSearch"
                @click="buscarCaso"
                size="md"
                variant="primary"
              />

              <ClearButton
                v-if="casoEncontrado"
                text="Limpiar"
                @click="limpiarBusqueda"
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

          <!-- Se elimina el bloque de notificación de caso encontrado -->
        </div>

        <!-- Editor de resultados - Solo visible cuando se encuentra un caso -->
        <div v-if="casoEncontrado" class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor
            class="flex-1 min-h-0"
            :model-value="activeSection === 'method' ? (Array.isArray(sections[activeSection]) ? [...sections[activeSection]] : []) : sections[activeSection]"
            @update:model-value="updateSectionContent"
            :active-section="activeSection"
            @update:activeSection="activeSection = $event"
            :sections="sections"
          >
            <template #footer>
              <div class="flex flex-wrap items-center gap-3 justify-end">
                <ClearButton :disabled="loading" @click="handleClearResults" />
                <SaveButton 
                  :disabled="saving || loading || !canSaveProgress" 
                  :loading="saving" 
                  :text="canComplete ? 'Completar para Firma' : 'Guardar Progreso'" 
                  :loading-text="canComplete ? 'Completando...' : 'Guardando...'" 
                  @click="handleSaveAction"
                />
              </div>
            </template>
          </ResultEditor>

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
          :case-code="savedCaseCode || caseDetails?.caso_code || props.sampleId"
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
      :case-item="selectedPreviousCase"
      @close="selectedPreviousCase = null"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, nextTick } from 'vue'
import { useRouter } from 'vue-router'
import { ComponentCard } from '@/shared/components'
import { ErrorMessage, ValidationAlert } from '@/shared/components/feedback'
import { FormInputField } from '@/shared/components/forms'
import { SearchButton, ClearButton, SaveButton } from '@/shared/components/buttons'
import ResultEditor from '../Shared/ResultEditor.vue'
import PatientInfoCard from '../Shared/PatientInfoCard.vue'
import CaseDetailsCard from '../Shared/CaseDetailsCard.vue'
import PreviousCaseDetailsModal from '../Shared/PreviousCaseDetailsModal.vue'
// import AttachmentsPanel from './AttachmentsPanel.vue'
import Notification from '@/shared/components/feedback/Notification.vue'
import ResultsActionNotification from '../Shared/ResultsActionNotification.vue'
import { usePerformResults } from '../../composables/usePerformResults'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import casesApiService from '@/modules/cases/services/casesApi.service'
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
  previewData, isPreviewOpen, isDirty,
  initialize, previousCases, sections,
  canSaveProgress, canComplete,
  // addAttachment, removeAttachment,
  onSaveDraft, onCompleteForSigning, closePreview,
  loadCaseByCode,
  getDiagnosisData,
  hasDiseaseCIEO,
  primaryDiseaseCIEO,
  formatDiagnosisForReport
} = usePerformResults(props.sampleId)

// Composable para permisos y autenticación
const { isPatologo } = usePermissions()
const authStore = useAuthStore()
const router = useRouter()

onMounted(() => {
  initialize()
  
  // Si autoSearch está activado, ejecutar búsqueda automática
  if (props.autoSearch && props.sampleId) {
    ejecutarBusquedaAutomatica()
  }
  
  // Escuchar evento para limpiar el buscador
  const handleClearSearch = () => {
    limpiarBusqueda()
  }
  window.addEventListener('clear-search', handleClearSearch)
  
  // Limpiar el event listener al desmontar
  onUnmounted(() => {
    window.removeEventListener('clear-search', handleClearSearch)
  })
})

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
// const router = useRouter()
const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')
const casoInfo = ref<any>(null)

// Estado para el modal de casos anteriores
const selectedPreviousCase = ref<any>(null)

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
  let userName = authStore.user.nombre || null

  // Si no hay nombre, usar email como fallback
  if (!userName) {
    userName = authStore.user.email
  }
  
  return userName
}

// Función helper para obtener el nombre del patólogo asignado
const getAssignedPathologistName = (caseData: any): string | null => {
  if (!caseData?.patologo_asignado) return null
  
  const pathologistName = caseData.patologo_asignado.nombre || null
  
  return pathologistName
}

const handleCodigoChange = (value: string) => {
  // Solo números y guión
  value = value.replace(/[^\d-]/g, '')
  // Máximo 10 chars
  value = value.slice(0, 10)
  // Insertar guión después de 4 dígitos
  if (value.length >= 4 && !value.includes('-')) {
    value = value.slice(0, 4) + '-' + value.slice(4)
  }
  // Evitar múltiples guiones
  const parts = value.split('-')
  if (parts.length > 2) {
    value = parts[0] + '-' + parts.slice(1).join('')
  }
  // Asegurar guión en posición 4
  if (value.includes('-') && value.indexOf('-') !== 4) {
    const digits = value.replace(/-/g, '')
    if (digits.length >= 4) {
      value = digits.slice(0, 4) + '-' + digits.slice(4, 9)
    } else {
      value = digits
    }
  }
  codigoCaso.value = value
}

/**
 * Maneja la entrada de solo números en el campo de código de caso
 */
const keydownHandler = (event: KeyboardEvent) => {
  // Permitir teclas de control (backspace, delete, tab, escape, enter, etc.)
  if (event.key === 'Backspace' || event.key === 'Delete' || event.key === 'Tab' || 
      event.key === 'Escape' || event.key === 'Enter' || event.key === 'ArrowLeft' || 
      event.key === 'ArrowRight' || event.key === 'Home' || event.key === 'End') {
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

const buscarCaso = async () => {
  if (!codigoCaso.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso'
    return
  }
  
  isLoadingSearch.value = true
  searchError.value = ''
  casoEncontrado.value = false
  
  try {
    const data = await casesApiService.getCaseByCode(codigoCaso.value.trim())
    
    // Validar permisos para patólogos
    if (isPatologo.value && authStore.user) {
      const nombrePatologoAsignado = getAssignedPathologistName(data)
      const nombreUsuario = getCurrentUserName()
      
      if (!nombrePatologoAsignado) {
        throw new Error('Este caso no tiene un patólogo asignado.')
      }
      
      if (!nombreUsuario) {
        throw new Error('No se pudo identificar tu nombre de usuario. Contacta al administrador.')
      }
      
      if (nombrePatologoAsignado !== nombreUsuario) {
        throw new Error('No tienes permisos para acceder a este caso. Solo puedes acceder a casos donde estés asignado como patólogo.')
      }
    }
    
    casoInfo.value = data
    casoEncontrado.value = true
    // Poblar paneles desde el composable
    await loadCaseByCode(codigoCaso.value.trim())
  } catch (error: any) {
    casoEncontrado.value = false
    casoInfo.value = null
    searchError.value = error.message || 'Error al buscar el caso'
  } finally {
    isLoadingSearch.value = false
  }
}

const limpiarBusqueda = () => {
  codigoCaso.value = ''
  casoEncontrado.value = false  // Siempre establecer a false
  searchError.value = ''
  casoInfo.value = null
  
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

// Eliminado abrirCaso, navegación ya no es necesaria

// ------------------------
// Notificaciones de guardado
// ------------------------
const { notification, showSuccess, showError, closeNotification } = useNotifications()

  function handleClearResults() {
    // Limpiar solo las secciones del editor, pero mantener la notificación
    sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
    activeSection.value = 'method'
    
    // NO cerrar la notificación - se mantiene visible
  }

  function goToPreview() {
    // Guardar payload en sessionStorage para que la vista de previsualización lo consuma
    const payload = {
      sampleId: caseDetails?.value?.caso_code || props.sampleId,
      patient: patient?.value || null,
      caseDetails: caseDetails?.value || null,
      sections: sections?.value || null,
      diagnosis: {
        cie10: getDiagnosisData(),
        cieo: hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
          id: primaryDiseaseCIEO.value.id,
          codigo: primaryDiseaseCIEO.value.codigo,
          nombre: primaryDiseaseCIEO.value.nombre
        } : undefined,
        formatted: formatDiagnosisForReport()
      },
      generatedAt: new Date().toISOString()
    }
    // Función de previsualización temporalmente deshabilitada
    console.log('Previsualización temporalmente deshabilitada')
  }

async function handleSaveAction() {
  // Evitar múltiples ejecuciones
  if (saving.value) return
  
  // Capturar todo el estado INMEDIATAMENTE para evitar cambios durante la ejecución
  const currentState = {
    method: Array.isArray(sections.value?.method) ? [...sections.value.method] : [],
    macro: sections.value?.macro || '',
    micro: sections.value?.micro || '',
    diagnosis: sections.value?.diagnosis || '',
    isComplete: canComplete.value,
    caseCode: caseDetails?.value?.caso_code || ''
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
  } catch (error) {
    console.error('Error en handleSaveAction:', error)
    showError('Error inesperado', 'Ocurrió un error inesperado al procesar la solicitud.', 0)
  }
}

// (Removed detailed content summary - not needed when saving simple notification)

// Cerrar notificación y limpiar código de caso guardado
function closeAndClearNotification() {
  closeNotification()
  savedCaseCode.value = ''
}

// Función separada para limpiar el formulario
function clearFormAfterSave() {
  // Limpiar en orden específico para evitar dependencias circulares
  sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
  activeSection.value = 'method'
  validationMessage.value = null
  errorMessage.value = null
  
  // Limpiar datos del buscador
  codigoCaso.value = ''
  searchError.value = ''
  casoInfo.value = null
  patient.value = null
  caseDetails.value = null
  previousCases.value = []
  
  // Emitir evento para limpiar el buscador en otros componentes
  if (typeof window !== 'undefined') {
    window.dispatchEvent(new CustomEvent('clear-search'))
  }
}

// Función para ejecutar búsqueda automática
const ejecutarBusquedaAutomatica = async () => {
  if (!props.sampleId) return
  
  // Simular que se escribió el código en el buscador
  codigoCaso.value = props.sampleId
  
  // Ejecutar la búsqueda automáticamente
  await buscarCaso()
}

// ------------------------
// Diagnóstico CIE-10
// ------------------------
// Estas funciones ya no se usan en Transcribir Resultados

// Función para actualizar el contenido de la sección activa
const updateSectionContent = (value: string | string[]) => {
  if (sections.value) {
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
}

// Función para manejar el clic en casos anteriores
const handleCaseClick = async (caseItem: any) => {
  try {
    // Cargar el caso completo desde la base de datos
    const fullCase = await casesApiService.getCaseByCode(caseItem.CasoCode)
    selectedPreviousCase.value = fullCase
  } catch (error) {
    // Si falla, usar el caso básico
    selectedPreviousCase.value = caseItem
  }
}
</script>


