<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <ComponentCard class="lg:col-span-2 min-h-[640px] flex flex-col" :dense="false" :fullHeight="true">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-lg font-semibold">Realizar Resultados</h2>
          <div v-if="caseDetails?.CasoCode" class="text-sm text-gray-500">
            <span class="font-medium">Caso:</span> {{ caseDetails.CasoCode }}
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
            Buscar Caso
          </h3>
          


          <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-stretch md:items-end">
            <div class="flex-1">
              <FormInputField
                id="codigo-caso"
                :model-value="codigoCaso"
                @update:model-value="handleCodigoChange"
                type="text"
                placeholder="Ej: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isLoadingSearch"
                @keydown.enter.prevent="buscarCaso"
                class="flex-1"
              />

              <!-- Validación de formato del código -->
              <div v-if="codigoCaso && !isValidCodigoFormat(codigoCaso)" class="mt-1 text-xs text-red-600">
                El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
              </div>
            </div>

            <div class="flex gap-2 md:gap-3">
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

        <div class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor
            class="flex-1 min-h-0"
            :model-value="sections[activeSection]"
            @update:model-value="updateSectionContent"
            :active-section="activeSection"
            @update:activeSection="activeSection = $event"
            :sections="sections"
          />

          <ValidationAlert
            :visible="!!validationMessage"
            class="mt-2"
            :errors="validationMessage ? [validationMessage] : []"
          />
          <ErrorMessage v-if="errorMessage" class="mt-2" :message="errorMessage" />
          <div class="mt-3 flex flex-wrap items-center gap-3 justify-end">
            <ClearButton :disabled="loading" @click="handleClearResults" />
            <PreviewButton :disabled="loading" @click="goToPreview" />
            <SaveButton :disabled="saving || loading || !canSave" :loading="saving" :text="'Guardar'" :loading-text="'Guardando...'" @click="handleSaveDraft" />
          </div>
          <Notification
            class="mt-3"
            :visible="notification.visible"
            :type="notification.type"
            :title="notification.title"
            :message="notification.message"
            :inline="true"
            :auto-close="false"
            data-notification="success"
            @close="closeNotification"
          >
            <template v-if="notification.type === 'success'" #content>
              <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
                <div class="space-y-4">
                  <div class="text-center pb-3 border-b border-gray-200">
                    <div class="inline-block">
                      <p class="font-semibold text-gray-900 text-base">Resumen de cortes guardados</p>
                      <p class="text-gray-500 text-sm">Caso {{ caseDetails?.CasoCode || sampleId }}</p>
                    </div>
                  </div>
                  <div class="grid grid-cols-1 md:grid-cols-2 gap-4 text-sm">
                    <div>
                      <h5 class="font-medium text-gray-700 mb-1">Método</h5>
                      <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ sections.method || '—' }}</div>
                    </div>
                    <div>
                      <h5 class="font-medium text-gray-700 mb-1">Corte Macro</h5>
                      <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ sections.macro || '—' }}</div>
                    </div>
                    <div>
                      <h5 class="font-medium text-gray-700 mb-1">Corte Micro</h5>
                      <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ sections.micro || '—' }}</div>
                    </div>
                    <div>
                      <h5 class="font-medium text-gray-700 mb-1">Diagnóstico</h5>
                      <div class="text-gray-900 whitespace-pre-wrap break-words overflow-hidden bg-gray-50 border border-gray-200 rounded p-3 min-h-[60px] max-w-full">{{ sections.diagnosis || '—' }}</div>
                    </div>
                  </div>
                </div>
              </div>
            </template>
          </Notification>
        </div>
      </ComponentCard>

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

    

    <PreviewModal
      v-if="isPreviewOpen && previewData"
      :html="previewData.html"
      @close="closePreview"
    />

    <PreviousCaseDetailsModal
      v-if="selectedPreviousCase"
      :case-item="selectedPreviousCase"
      @close="selectedPreviousCase = null"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref } from 'vue'
import { useRouter } from 'vue-router'
import { ComponentCard } from '@/shared/components/ui'
import { ErrorMessage, ValidationAlert } from '@/shared/components/ui/feedback'
import { FormInputField } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton, SaveButton, PreviewButton } from '@/shared/components/ui/buttons'
import ResultEditor from './ResultEditor.vue'
import PatientInfoCard from './PatientInfoCard.vue'
import CaseDetailsCard from './CaseDetailsCard.vue'
import PreviousCaseDetailsModal from './PreviousCaseDetailsModal.vue'
// import AttachmentsPanel from './AttachmentsPanel.vue'
import Notification from '@/shared/components/ui/feedback/Notification.vue'
import PreviewModal from './PreviewModal.vue'
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
  activeSection, sectionContent,
  errorMessage, validationMessage,
  previewData, isPreviewOpen, isDirty,
  initialize, previousCases, sections,
  missingFields, canSave,
  // addAttachment, removeAttachment,
  onSaveDraft, closePreview, onClear,
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

const isValidCodigoFormat = (codigo: string | undefined | null): boolean => {
  if (!codigo || typeof codigo !== 'string' || codigo.trim() === '') return false
  const regex = /^\d{4}-\d{5}$/
  return regex.test(codigo.trim())
}

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

const buscarCaso = async () => {
  if (!codigoCaso.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso'
    return
  }
  if (!isValidCodigoFormat(codigoCaso.value)) {
    searchError.value = 'El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)'
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
  casoEncontrado.value = false
  searchError.value = ''
  casoInfo.value = null
  // NO cerrar la notificación - se mantiene visible
}

// Eliminado abrirCaso, navegación ya no es necesaria

// ------------------------
// Notificaciones de guardado
// ------------------------
const { notification, showSuccess, showError, closeNotification } = useNotifications()

  function handleClearResults() {
    onClear()
    // NO cerrar la notificación - se mantiene visible
  }

  function goToPreview() {
    // Guardar payload en sessionStorage para que la vista de previsualización lo consuma
    const payload = {
      sampleId: caseDetails?.value?.CasoCode || props.sampleId,
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
    try {
      sessionStorage.setItem('results_preview_payload', JSON.stringify(payload))
    } catch {}
    router.push({ name: 'results-preview' })
  }

async function handleSaveDraft() {
  const ok = await onSaveDraft()
  if (ok) {
    const code = caseDetails?.value?.CasoCode || ''
    showSuccess('¡Resultado guardado!', code ? `Se guardó el resultado del caso ${code}.` : 'Se guardó el resultado correctamente.', 0)
    // NO cerrar la notificación - se mantiene visible
  } else {
    showError('Error al guardar', errorMessage?.value || 'No se pudo guardar el resultado.', 0)
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
const updateSectionContent = (value: string) => {
  if (sections.value) {
    sections.value[activeSection.value] = value
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


