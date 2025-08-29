<template>
  <div class="space-y-6">
    <div class="grid grid-cols-1 lg:grid-cols-3 gap-6 items-start">
      <ComponentCard class="lg:col-span-2 min-h-[640px] flex flex-col" :dense="false" :fullHeight="true">
        <div class="flex items-center justify-between mb-2">
          <h2 class="text-lg font-semibold">Firmar Resultados</h2>
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
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z" />
            </svg>
            Buscar Caso
          </h3>

          <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-stretch md:items-end">
            <div class="flex-1">
              <FormInputField id="codigo-caso" :model-value="codigoCaso" @update:model-value="handleCodigoChange"
                type="text" placeholder="Ej: 2025-00001" maxlength="10" autocomplete="off" :disabled="isLoadingSearch"
                @keydown.enter.prevent="buscarCaso" class="flex-1" />

              <div v-if="codigoCaso && !isValidCodigoFormat(codigoCaso)" class="mt-1 text-xs text-red-600">
                El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
              </div>
            </div>

            <div class="flex gap-2 md:gap-3">
              <SearchButton v-if="!casoEncontrado" text="Buscar" loading-text="Buscando..." :loading="isLoadingSearch"
                @click="buscarCaso" size="md" variant="primary" />

              <ClearButton v-if="casoEncontrado" text="Limpiar" @click="limpiarBusqueda" />
            </div>
          </div>

          <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                  d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z" />
              </svg>
              <p class="text-sm text-red-600">{{ searchError }}</p>
            </div>
          </div>
        </div>

        <div class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor class="flex-1 min-h-0" :model-value="sections[activeSection]"
            @update:model-value="updateSectionContent" :active-section="activeSection"
            @update:activeSection="activeSection = $event" :sections="sections" />

          <!-- Sección de Diagnóstico CIE-10 -->
          <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <DocsIcon class="w-4 h-4 mr-2 text-gray-500" />
              Diagnóstico
            </h3>

            <!-- Campo de Diagnóstico Principal -->
            <div class="mb-4">
              <DiseaseList :model-value="primaryDisease" @update:model-value="handlePrimaryDiseaseChange"
                @cieo-disease-selected="handlePrimaryDiseaseCIEOChange" label="Diagnóstico CIE-10"
                placeholder="Buscar enfermedad CIE-10..." :required="true" />
            </div>
          </div>

          <ValidationAlert :visible="!!validationMessage" class="mt-2"
            :errors="validationMessage ? [validationMessage] : []" />
          <ErrorMessage v-if="errorMessage" class="mt-2" :message="errorMessage" />

          <!-- Alerta de patólogo no asignado -->
          <div v-if="caseDetails?.caso_code && !caseDetails.patologo_asignado?.nombre"
            class="mt-3 p-3 bg-orange-50 border border-orange-200 rounded-lg">
            <div class="flex items-center">
              <WarningIcon class="w-5 h-5 text-orange-500 mr-2 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-orange-800">Patólogo no asignado</p>
                <p class="text-sm text-orange-700">Este caso aún no tiene un patólogo asignado. Contacta al auxiliar
                  administrativo para asignar un patólogo antes de firmar.</p>
              </div>
            </div>
          </div>

          <!-- Alerta de patólogo no autorizado -->
          <div v-if="caseDetails?.caso_code && caseDetails.patologo_asignado?.nombre && !isAssignedPathologist"
            class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <ErrorIcon class="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-red-800">No eres el patólogo asignado</p>
                <p class="text-sm text-red-700">Este caso está asignado a <strong>{{
                  caseDetails.patologo_asignado.nombre }}</strong>. Solo el patólogo asignado puede firmar este
                  resultado.</p>
              </div>
            </div>
          </div>

          <!-- Alerta de estado no válido para firmar -->
          <div v-if="caseDetails?.caso_code && !canSignByStatus && !hasBeenSigned"
            class="mt-3 p-3 bg-yellow-50 border border-yellow-200 rounded-lg">
            <div class="flex items-center">
              <WarningIcon class="w-5 h-5 text-yellow-500 mr-2 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-yellow-800">Estado no válido para firmar</p>
                <p class="text-sm text-yellow-700">{{ invalidStatusMessage }}</p>
              </div>
            </div>
          </div>

          <div class="mt-3 flex flex-wrap items-center gap-3 justify-end">
            <ClearButton :disabled="loading" @click="handleClearResults" />
            <PreviewButton :disabled="loading" @click="goToPreview" />
            <SaveButton
              :disabled="loading || !canSave || !hasDisease || !caseDetails?.patologo_asignado?.nombre || !isAssignedPathologist || (!canSignByStatus && !hasBeenSigned)"
              :loading="signing" :text="'Firmar'" :loading-text="'Firmando...'" @click="handleSign" />
          </div>

          <!-- Notificación de firma exitosa -->
          <Notification class="mt-3" :visible="notification.visible" :type="notification.type"
            :title="notification.title" :message="notification.message" :inline="true" :auto-close="false"
            data-notification="success"
            @close="closeNotification" />
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

    <PreviousCaseDetailsModal
      v-if="selectedPreviousCase"
      :case-item="selectedPreviousCase"
      @close="selectedPreviousCase = null"
    />
  </div>
</template>

<script setup lang="ts">
import { onMounted, onUnmounted, ref, computed } from 'vue'
import { useRouter } from 'vue-router'
import { ComponentCard } from '@/shared/components'
import { ErrorMessage, ValidationAlert } from '@/shared/components/feedback'
import { FormInputField } from '@/shared/components/forms'
import { SearchButton, ClearButton, SaveButton, PreviewButton } from '@/shared/components/buttons'
import { DiseaseList } from '@/shared/components/List'
import { FormCheckbox, FormTextarea } from '@/shared/components/forms'
import DocsIcon from '@/assets/icons/DocsIcon.vue'
import WarningIcon from '@/assets/icons/WarningIcon.vue'
import ErrorIcon from '@/assets/icons/ErrorIcon.vue'
import ResultEditor from '../PerformResults/ResultEditor.vue'
import PatientInfoCard from '../PerformResults/PatientInfoCard.vue'
import CaseDetailsCard from '../PerformResults/CaseDetailsCard.vue'
import PreviousCaseDetailsModal from '../PerformResults/PreviousCaseDetailsModal.vue'
import { usePerformResults } from '../../composables/usePerformResults'
import casesApiService from '@/modules/cases/services/casesApi.service'
import { useDiseaseDiagnosis } from '@/shared/composables/useDiseaseDiagnosis'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import type { Disease } from '@/shared/services/disease.service'
import Notification from '@/shared/components/feedback/Notification.vue'
import resultsApiService from '../../services/resultsApiService'

interface Props {
  sampleId: string
  autoSearch?: boolean
}
const props = defineProps<Props>()

// Composable para resultados
const {
  loading,
  patient, caseDetails,
  activeSection, sectionContent,
  errorMessage, validationMessage,
  previewData, isPreviewOpen, isDirty,
  initialize, previousCases, sections,
  missingFields, canSave,
  onSaveDraft, closePreview, onClear, clearAfterSuccess,
  loadCaseByCode,
  // CIEO diagnosis
  primaryDiseaseCIEO,
  hasDiseaseCIEO,
  showCIEODiagnosis,
  setPrimaryDiseaseCIEO,
  clearPrimaryDiseaseCIEO,
  toggleCIEODiagnosis
} = usePerformResults(props.sampleId)

// Composable para permisos y autenticación
const { isPatologo } = usePermissions()
const authStore = useAuthStore()

// Composable para notificaciones
const { notification, showSuccess, showError, closeNotification } = useNotifications()

// Disease Diagnosis composable
const {
  primaryDisease,
  hasDisease,
  setPrimaryDisease,
  clearPrimaryDisease,
  clearDiagnosis,
  formatDiagnosisForReport,
  getDiagnosisData,
  validateDiagnosis
} = useDiseaseDiagnosis()

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

// Función para ejecutar búsqueda automática
const ejecutarBusquedaAutomatica = async () => {
  if (!props.sampleId) return

  // Simular que se escribió el código en el buscador
  codigoCaso.value = props.sampleId

  // Ejecutar la búsqueda automáticamente
  await buscarCaso()
}

// Estado local extra
const signing = ref(false)
const hasBeenSigned = ref(false)

// Computed para verificar si el usuario logueado es el patólogo asignado
const isAssignedPathologist = computed(() => {
  if (!caseDetails.value?.patologo_asignado?.nombre || !authStore.user) {
    return false
  }

  const assignedPathologist = caseDetails.value.patologo_asignado.nombre
  const currentUser = getCurrentUserName()

  return assignedPathologist === currentUser
})

// Función para normalizar estados (convertir a formato de BD)
const normalizeStatus = (status: string): string => {
  if (!status) return status

  // Convertir a mayúsculas y reemplazar espacios con guiones bajos
  return status.toUpperCase().replace(/\s+/g, '_')
}

// Función para convertir estados de BD a formato legible
const getReadableStatus = (status: string): string => {
  const normalizedStatus = normalizeStatus(status)
  const statusMap: Record<string, string> = {
    'EN_PROCESO': 'En Proceso',
    'POR_ENTREGAR': 'Por Entregar',
    'POR_FIRMAR': 'Por Firmar',
    'COMPLETADO': 'Completado',
    'PENDIENTE': 'Pendiente',
    'CANCELADO': 'Cancelado'
  }
  return statusMap[normalizedStatus] || status
}

// Computed para verificar si el caso está en un estado válido para firmar
const canSignByStatus = computed(() => {
  if (!caseDetails.value?.estado) return false

  const normalizedStatus = normalizeStatus(caseDetails.value.estado)
  // Solo NO se puede firmar si está COMPLETADO
  return normalizedStatus !== 'COMPLETADO'
})

// Computed para obtener el mensaje de estado no válido
const invalidStatusMessage = computed(() => {
  if (!caseDetails.value?.estado) return ''

  const estado = caseDetails.value.estado
  const normalizedStatus = normalizeStatus(estado)

  if (normalizedStatus === 'COMPLETADO') {
    return 'Este caso ya ha sido completado y firmado.'
  }

  return ''
})

// Buscador (clonado)
const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')

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
  let userName = (authStore.user as any).username || // username tiene el nombre completo
    authStore.user.nombre ||
    (authStore.user as any).nombres ||
    (authStore.user as any).nombre_completo ||
    (authStore.user as any).full_name ||
    null

  // Si no hay nombre completo, intentar construir desde nombres + apellidos
  if (!userName && ((authStore.user as any).nombres || (authStore.user as any).apellidos)) {
    const nombres = (authStore.user as any).nombres || ''
    const apellidos = (authStore.user as any).apellidos || ''
    userName = `${nombres} ${apellidos}`.trim()
  }

  // Si no hay nombre completo, intentar construir desde first_name + last_name
  if (!userName && ((authStore.user as any).first_name || (authStore.user as any).last_name)) {
    const firstName = (authStore.user as any).first_name || ''
    const lastName = (authStore.user as any).last_name || ''
    userName = `${firstName} ${lastName}`.trim()
  }

  return userName
}

// Función helper para obtener el nombre del patólogo asignado
const getAssignedPathologistName = (caseData: any): string | null => {
  if (!caseData?.patologo_asignado) return null

  const pathologistName = caseData.patologo_asignado.nombre ||
    caseData.patologo_asignado.nombres ||
    caseData.patologo_asignado.nombre_completo ||
    null

  return pathologistName
}

const handleCodigoChange = (value: string) => {
  value = value.replace(/[^\d-]/g, '')
  value = value.slice(0, 10)
  if (value.length >= 4 && !value.includes('-')) {
    value = value.slice(0, 4) + '-' + value.slice(4)
  }
  const parts = value.split('-')
  if (parts.length > 2) {
    value = parts[0] + '-' + parts.slice(1).join('')
  }
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
    searchError.value = 'Por favor, ingrese un código de caso';
    return
  }
  if (!isValidCodigoFormat(codigoCaso.value)) {
    searchError.value = 'El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)';
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

    casoEncontrado.value = true
    await loadCaseByCode(codigoCaso.value.trim())

    // Cargar diagnósticos existentes solo en Firmar Resultados
    await loadExistingDiagnosis(data)
  } catch (error: any) {
    casoEncontrado.value = false
    searchError.value = error.message || 'Error al buscar el caso'
  } finally {
    isLoadingSearch.value = false
  }
}

// Función para cargar diagnósticos existentes (solo en Firmar Resultados)
const loadExistingDiagnosis = async (caseData: any) => {
  try {
    if (caseData.resultado) {
      const resultado = caseData.resultado as any

      // Cargar diagnóstico CIE-10 existente
      if (resultado.diagnostico_cie10) {
        const diseaseData = {
          id: resultado.diagnostico_cie10.id,
          codigo: resultado.diagnostico_cie10.codigo,
          nombre: resultado.diagnostico_cie10.nombre,
          tabla: 'CIE-10',
          isActive: true
        }
        setPrimaryDisease(diseaseData)
      }

      // Cargar diagnóstico CIE-O existente
      if (resultado.diagnostico_cieo) {
        const diseaseDataCIEO = {
          id: resultado.diagnostico_cieo.id,
          codigo: resultado.diagnostico_cieo.codigo,
          nombre: resultado.diagnostico_cieo.nombre,
          tabla: 'CIE-O',
          isActive: true
        }
        setPrimaryDiseaseCIEO(diseaseDataCIEO)
        showCIEODiagnosis.value = true // Mostrar la sección CIE-O si existe
      }
    }
  } catch (error) {
    console.warn('Error al cargar diagnósticos existentes:', error)
  }
}

const limpiarBusqueda = () => {
  codigoCaso.value = ''
  casoEncontrado.value = false
  searchError.value = ''
  hasBeenSigned.value = false // Resetear el estado de firma
  // NO cerrar la notificación - se mantiene visible

  // Limpiar diagnósticos cuando se limpia la búsqueda
  clearDiagnosis()
  clearPrimaryDiseaseCIEO()
  showCIEODiagnosis.value = false
}

// Acciones
function handleClearResults() {
  onClear()
  clearDiagnosis()
  clearPrimaryDiseaseCIEO()
  // NO cerrar la notificación - se mantiene visible
}

function goToPreview() {
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
  try { sessionStorage.setItem('results_preview_payload', JSON.stringify(payload)) } catch { }
  router.push({ name: 'results-preview' })
}

async function handleSign() {
  try {
    signing.value = true

    // Validar que haya un diagnóstico CIE-10
    const validation = validateDiagnosis()
    if (!validation.isValid) {
      validationMessage.value = validation.errors.join(', ')
      return
    }

    // Validar que el usuario sea el patólogo asignado
    if (!isAssignedPathologist.value) {
      showError(
        'No autorizado',
        'Solo el patólogo asignado al caso puede firmar este resultado.',
        0
      )
      return
    }

    // Validar que el caso esté en un estado válido para firmar
    if (!canSignByStatus.value && !hasBeenSigned.value) {
      showError(
        'Estado no válido',
        invalidStatusMessage.value,
        0
      )
      return
    }

    // Obtener el código del patólogo asignado
    const patologoCodigo = caseDetails?.value?.patologo_asignado?.codigo
    if (!patologoCodigo) {
      showError(
        'Error al firmar',
        'No se pudo identificar el patólogo asignado al caso.',
        0
      )
      return
    }

    // Preparar datos para la firma
    const casoCode = caseDetails?.value?.caso_code || props.sampleId
    const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
      id: primaryDisease.value.id,
      codigo: primaryDisease.value.codigo,
      nombre: primaryDisease.value.nombre
    } : undefined

    const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      id: primaryDiseaseCIEO.value.id,
      codigo: primaryDiseaseCIEO.value.codigo,
      nombre: primaryDiseaseCIEO.value.nombre
    } : undefined

    const requestData = {
      metodo: sections.value?.method || '',
      resultado_macro: sections.value?.macro || '',
      resultado_micro: sections.value?.micro || '',
      diagnostico: sections.value?.diagnosis || '',
      observaciones: '',
      diagnostico_cie10: diagnosticoCie10,
      diagnostico_cieo: diagnosticoCIEO
    }

    // Llamar al endpoint de firma que cambia el estado
    const response = await resultsApiService.firmarResultado(casoCode, requestData, patologoCodigo)

    if (response) {
      // Mostrar notificación de éxito
      showSuccess(
        '¡Resultado firmado exitosamente!',
        `El resultado del caso ${casoCode} ha sido firmado y está listo para entrega.`,
        0
      )

      // Limpiar mensajes de validación
      validationMessage.value = ''

      // Actualizar los datos del caso localmente
      if (caseDetails.value) {
        caseDetails.value.estado = 'COMPLETADO'
      }

      // Marcar que el caso ha sido firmado para ocultar alertas
      hasBeenSigned.value = true

      // Limpiar el formulario después de firmar exitosamente
      clearAfterSuccess()

      // NO redirigir automáticamente al PDF
      // El usuario puede hacer clic en "Previsualizar" si desea ver el PDF
    } else {
      showError(
        'Error al firmar',
        'El servidor no devolvió una respuesta válida.',
        0
      )
    }
  } catch (error: any) {
    showError(
      'Error al firmar',
      error.response?.data?.message || error.message || 'No se pudo firmar el resultado.',
      0
    )
  } finally {
    signing.value = false
  }
}

// Función para manejar cambio de diagnóstico principal
const handlePrimaryDiseaseChange = (disease: Disease | null) => {
  setPrimaryDisease(disease)
  if (disease) {
    validationMessage.value = '' // Limpiar mensaje de validación
  }
}

// Función para manejar cambio de diagnóstico CIEO
const handlePrimaryDiseaseCIEOChange = (disease: Disease | null) => {
  setPrimaryDiseaseCIEO(disease)
  if (disease) {
    validationMessage.value = '' // Limpiar mensaje de validación
  }
}

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
    const fullCase = await casesApiService.getCaseByCode(caseItem.caso_code)
    selectedPreviousCase.value = fullCase
  } catch (error) {
    // Si falla, usar el caso básico
    selectedPreviousCase.value = caseItem
  }
}


</script>
