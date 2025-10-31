<template>
  <div class="space-y-6">
    <div class="grid gap-6 items-start grid-cols-1 lg:grid-cols-3">
      <ComponentCard 
        :class="[
          'flex flex-col',
          'lg:col-span-2'
        ]" 
        :style="{ minHeight: caseFound ? (activeSection === 'method' ? 'auto' : '640px') : '160px' }"
        :dense="false"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <h2 class="text-lg font-semibold">
              {{ caseFound ? 'Firmar Resultados' : 'Buscar caso para firmar resultados' }}
            </h2>
            <p v-if="!caseFound" class="text-sm text-gray-500 mt-1">
              Ingresa el código del caso para acceder a la firma de resultados
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

        <!-- Advertencia de falta de firma -->
        <div v-if="isPathologistWithoutSignature" class="mb-4 p-4 bg-yellow-50 border-l-4 border-yellow-400 text-yellow-800 rounded-r-lg">
          <div class="flex">
            <div class="flex-shrink-0">
              <WarningIcon class="h-5 w-5 text-yellow-500" />
            </div>
            <div class="ml-3">
              <p class="text-sm font-bold">Firma digital no configurada</p>
              <p class="text-sm mt-1">
                No puedes firmar resultados porque no has subido tu firma digital. Por favor, ve a 
                <router-link to="/profile" class="font-medium underline hover:text-yellow-900">tu perfil</router-link> 
                para configurarla.
              </p>
            </div>
          </div>
        </div>

        <div class="bg-gray-50 rounded-lg p-3 md:p-4 border border-gray-200 mb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Buscar caso
          </h3>

          <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-start md:items-center">
            <div class="flex-1">
              <FormInputField id="codigo-caso" :model-value="caseCode" @update:model-value="handleCaseCodeChange"
                type="text" placeholder="Ejemplo: 2025-00001" maxlength="10" autocomplete="off" :disabled="isLoadingSearch"
                @keydown.enter.prevent="searchCase" @keydown="keydownHandler" @paste="handlePaste" class="flex-1" />

            </div>

            <div class="flex gap-2 md:gap-3 md:mt-0 mt-2">
              <SearchButton v-if="!caseFound" text="Buscar" loading-text="Buscando..." :loading="isLoadingSearch"
                @click="searchCase" size="md" variant="primary" />

              <ClearButton v-if="caseFound" text="Limpiar" @click="clearSearch" />
            </div>
          </div>

          <!-- Mensaje de error de búsqueda -->
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

        <div v-if="caseFound" class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor :model-value="sections[activeSection]"
            @update:model-value="updateSectionContent" :active-section="activeSection"
            @update:activeSection="activeSection = $event" :sections="sections" />

          <div class="mt-4 p-4 bg-gray-50 rounded-lg border border-gray-200">
            <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
              <DocsIcon class="w-4 h-4 mr-2 text-gray-500" />
              Diagnóstico
            </h3>

            <div class="mb-4">
              <DiseaseList 
                :model-value="primaryDisease" 
                :cieo-value="primaryDiseaseCIEO"
                @update:model-value="handlePrimaryDiseaseChange"
                @cieo-disease-selected="handlePrimaryDiseaseCIEOChange" 
                label="Diagnóstico CIE-10"
                placeholder="Buscar enfermedad CIE-10..." 
                :required="true" 
              />
            </div>
          </div>

          <ComplementaryTestsSection
            :initial-needs-tests="needsComplementaryTests"
            :initial-details="complementaryTestsDetails"
            :caso-original="caseDetails?.case_code || caseCode"
            @needs-tests-change="handleNeedsTestsChange"
            @details-change="handleDetailsChange"
            @create-approval-request="handleCreateApprovalRequest"
            @sign-with-changes="handleSignWithChanges"
            @update-original-case="handleUpdateOriginalCase"
          />

          <ValidationAlert :visible="!!validationMessage" class="mt-2"
            :errors="validationMessage ? [validationMessage] : []" />
          <ErrorMessage v-if="errorMessage" class="mt-2" :message="errorMessage" />

          <div v-if="needsAssignedPathologist"
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

          <div v-if="caseDetails?.case_code && !caseDetails.assigned_pathologist?.name && authStore.user?.role === 'administrator'"
            class="mt-3 p-3 bg-blue-50 border border-blue-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-blue-500 mr-2 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div>
                <p class="text-sm font-medium text-blue-800">Firmando como administrador</p>
                <p class="text-sm text-blue-700">Este caso no tiene patólogo asignado. Como administrador, puedes firmarlo directamente.</p>
              </div>
            </div>
          </div>

          <div v-if="caseDetails?.case_code && caseDetails.assigned_pathologist?.name && !canUserSign"
            class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <ErrorIcon class="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-red-800">No autorizado para firmar</p>
                <p class="text-sm text-red-700">
                  <template v-if="authStore.user?.role === 'pathologist'">
                    Este caso está asignado a <strong>{{ caseDetails.assigned_pathologist.name }}</strong>. 
                    Solo el patólogo asignado o un administrador pueden firmar este resultado.
                  </template>
                  <template v-else>
                    Solo patólogos y administradores pueden firmar resultados.
                  </template>
                </p>
              </div>
            </div>
          </div>

          <!-- Advertencia para casos completados -->
          <div v-if="caseDetails?.case_code && !canSignByStatus && !hasBeenSigned"
            class="mt-3 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <div>
                <p class="text-sm font-bold text-red-800">Caso completado</p>
                <p class="text-sm text-red-700 mt-1">
                  Este caso ya ha sido completado. No se puede firmar un caso completado.
                </p>
                <p class="text-xs text-red-600 mt-2">
                  Estado actual: <span class="font-semibold">{{ caseDetails?.state }}</span>
                </p>
              </div>
            </div>
          </div>

          <div class="mt-3 flex flex-wrap items-center gap-3 justify-end">
            <ClearButton :disabled="loading" @click="clearSearch" />
            <PrintPdfButton 
              :disabled="loading || !(caseDetails?.case_code || props.sampleId || caseCode)"
              :case-code="caseDetails?.case_code || props.sampleId || caseCode"
              size="md"
              variant="secondary"
              text="Imprimir PDF"
            />
            <!-- Botón de previsualización temporalmente deshabilitado -->
            <button
              :disabled="loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature"
              :class="['px-4 py-2 text-sm font-medium rounded-md flex items-center gap-2', (loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature) ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700']"
              @click="handleSign"
            >
              <EditCaseIcon class="w-4 h-4" />
              {{ signing ? 'Firmando...' : 'Firmar' }}
            </button>
          </div>
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
          :diagnoses="{
            cie10: (hasDisease && primaryDisease) ? { codigo: primaryDisease.code, nombre: primaryDisease.name } : undefined,
            cieo: (hasDiseaseCIEO && primaryDiseaseCIEO) ? { codigo: primaryDiseaseCIEO.code, nombre: primaryDiseaseCIEO.name } : undefined
          }"
          :complementary-tests="requestedComplementaryTests"
          :complementary-tests-reason="requestedComplementaryTestsReason"
          context="sign"
          @close="handleNotificationClose"
        />
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
import { ComponentCard } from '@/shared/components'
import { ErrorMessage, ValidationAlert } from '@/shared/components/ui/feedback'
import { FormInputField } from '@/shared/components/ui/forms'
import { SearchButton, ClearButton, PrintPdfButton } from '@/shared/components/ui/buttons'
import { DiseaseList } from '@/shared/components/ui/lists'
import DocsIcon from '@/assets/icons/DocsIcon.vue'
import WarningIcon from '@/assets/icons/WarningIcon.vue'
import ErrorIcon from '@/assets/icons/ErrorIcon.vue'
import EditCaseIcon from '@/assets/icons/EditCaseIcon.vue'
import ResultEditor from '../Shared/ResultEditor.vue'
import PatientInfoCard from '../Shared/PatientInfoCard.vue'
import CaseDetailsCard from '../Shared/CaseDetailsCard.vue'
import PreviousCaseDetailsModal from '../Shared/PreviousCaseDetailsModal.vue'
import ComplementaryTestsSection from './ComplementaryTestsSection.vue'
import { usePerformResults } from '../../composables/usePerformResults'
import casesApiService from '@/modules/cases/services/casesApi.service'
import { useDiseaseDiagnosis } from '@/shared/composables/useDiseaseDiagnosis'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import { profileApiService } from '@/modules/profile/services/profileApiService'
import type { Disease } from '@/shared/services/disease.service'
import ResultsActionNotification from '../Shared/ResultsActionNotification.vue'
import signApiService from '../../services/signApiService'
import approvalService from '@/shared/services/approval.service'
import type { ComplementaryTestInfo } from '@/shared/services/approval.service'

interface Props {
  sampleId: string
  autoSearch?: boolean
}
const props = defineProps<Props>()

const { loading, patient, caseDetails, activeSection, errorMessage, validationMessage, initialize, previousCases, sections, loadCaseByCode, primaryDiseaseCIEO, hasDiseaseCIEO, showCIEODiagnosis, setPrimaryDiseaseCIEO, clearPrimaryDiseaseCIEO } = usePerformResults(props.sampleId)
const { isPatologo } = usePermissions()
const authStore = useAuthStore()
const { notification, showSuccess, showError, closeNotification } = useNotifications()
const { primaryDisease, hasDisease, setPrimaryDisease, clearDiagnosis, validateDiagnosis } = useDiseaseDiagnosis()

const handleClearSearch = () => clearSearch()
onMounted(() => {
  initialize()
  if (props.autoSearch && props.sampleId) executeAutomaticSearch()
  window.addEventListener('clear-search', handleClearSearch)
  // Refrescar firma del patólogo desde backend si no está en memoria
  try {
    const email = authStore.user?.email
    if (authStore.user?.role === 'pathologist' && email) {
      const current = (authStore.user as any).firma || (authStore.user as any).firma_url || (authStore.user as any).signatureUrl || (authStore.user as any).firmaDigital
      if (!current) {
        profileApiService.getByRoleAndEmail('patologo', email).then((pb: any) => {
          const firma = pb?.firma || ''
          if (firma) {
            ;(authStore.user as any).firma = firma
            ;(authStore.user as any).firma_url = firma
            ;(authStore.user as any).signatureUrl = firma
            ;(authStore.user as any).firmaDigital = firma
            try { localStorage.setItem('signature_url', firma) } catch {}
            try { sessionStorage.setItem('signature_url', firma) } catch {}
          }
        }).catch(() => {})
      }
    }
  } catch {}
})
onUnmounted(() => window.removeEventListener('clear-search', handleClearSearch))

const executeAutomaticSearch = async () => {
  if (!props.sampleId) return
  caseCode.value = props.sampleId
  await searchCase()
}

const signing = ref(false)
const hasBeenSigned = ref(false)
const needsComplementaryTests = ref(false)
const complementaryTestsDetails = ref('')
const savedContent = ref({
  method: [] as string[],
  macro: '',
  micro: '',
  diagnosis: ''
})
const savedCaseCode = ref('')

// Guarda el contenido actual del formulario para mostrar en notificaciones
const setSavedFromSections = () => {
  savedContent.value = {
    method: sections.value?.method || [],
    macro: sections.value?.macro || '',
    micro: sections.value?.micro || '',
    diagnosis: sections.value?.diagnosis || ''
  }
}

// Verifica si el usuario actual es el patólogo asignado al caso
const isAssignedPathologist = computed(() => {
  if (!caseDetails.value?.assigned_pathologist?.name || !authStore.user) return false
  const assignedPathologist = caseDetails.value.assigned_pathologist.name
  const currentUser = getCurrentUserName()
  return assignedPathologist === currentUser
})

// Reglas de autorización: administradores pueden firmar cualquier caso, patólogos solo sus casos asignados
const canUserSign = computed(() => {
  if (!authStore.user) return false
  // Los administradores pueden firmar cualquier caso
  if (authStore.user.role === 'administrator') return true
  // Los patólogos solo pueden firmar sus casos asignados
  if (authStore.user.role === 'pathologist') return isAssignedPathologist.value
  return false
})

// Patólogo sin firma digital configurada
const isPathologistWithoutSignature = computed(() => {
  if (!authStore.user) return false
  if (authStore.user.role !== 'pathologist') return false
  let firma = (authStore.user as any).firma || (authStore.user as any).firma_url || (authStore.user as any).signatureUrl || (authStore.user as any).firmaDigital
  if (!firma) {
    try { firma = localStorage.getItem('signature_url') || firma } catch {}
    try { firma = sessionStorage.getItem('signature_url') || firma } catch {}
  }
  return !firma || (typeof firma === 'string' && firma.trim() === '')
})

// Todos los casos requieren que tengan un patólogo asignado para poder firmarse (excepto administradores)
const needsAssignedPathologist = computed(() => {
  if (!authStore.user || !caseDetails.value?.case_code) return false
  // Los administradores pueden firmar casos sin patólogo asignado
  if (authStore.user.role === 'administrator') return false
  // Todos los demás usuarios requieren que el caso tenga un patólogo asignado
  return !caseDetails.value.assigned_pathologist?.name
})

// Normaliza estados a formato de BD (mayúsculas y guiones bajos)
const normalizeStatus = (status: string): string => {
  if (!status) return status
  return status.toUpperCase().replace(/\s+/g, '_')
}

// Solo se puede firmar si el caso NO está en estado COMPLETADO
const canSignByStatus = computed(() => {
  if (!caseDetails.value?.state) return false
  const normalizedStatus = normalizeStatus(caseDetails.value.state)
  return normalizedStatus !== 'COMPLETADO'
})

const invalidStatusMessage = computed(() => {
  if (!caseDetails.value?.state) return ''
  const estado = caseDetails.value.state
  const normalizedStatus = normalizeStatus(estado)
  if (normalizedStatus === 'COMPLETADO') {
    return 'Este caso ya ha sido completado. No se puede firmar un caso completado.'
  }
  return ''
})

const caseCode = ref('')
const isLoadingSearch = ref(false)
const caseFound = ref(false)
const searchError = ref('')
const selectedPreviousCase = ref<any>(null)


// Extrae el nombre completo del usuario desde diferentes formatos posibles
const getCurrentUserName = (): string | null => {
  if (!authStore.user) return null
  let userName = (authStore.user as any).username ||
    authStore.user.name ||
    (authStore.user as any).nombres ||
    (authStore.user as any).nombre_completo ||
    (authStore.user as any).full_name ||
    null
  if (!userName && ((authStore.user as any).nombres || (authStore.user as any).apellidos)) {
    const nombres = (authStore.user as any).nombres || ''
    const apellidos = (authStore.user as any).apellidos || ''
    userName = `${nombres} ${apellidos}`.trim()
  }
  if (!userName && ((authStore.user as any).first_name || (authStore.user as any).last_name)) {
    const firstName = (authStore.user as any).first_name || ''
    const lastName = (authStore.user as any).last_name || ''
    userName = `${firstName} ${lastName}`.trim()
  }
  return userName
}

const getAssignedPathologistName = (caseData: any): string | null => {
  if (!caseData?.assigned_pathologist) return null
  const pathologistName = caseData.assigned_pathologist.name ||
    caseData.assigned_pathologist.nombre ||
    caseData.assigned_pathologist.nombres ||
    caseData.assigned_pathologist.nombre_completo ||
    null
  return pathologistName
}

const handleCaseCodeChange = (value: string) => {
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
  caseCode.value = value
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
  
  // Permitir combinaciones de teclas para copiar y pegar
  if ((event.ctrlKey || event.metaKey) && (event.key === 'c' || event.key === 'v' || event.key === 'a')) {
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
  
  // Filtrar solo números y guiones del texto pegado
  const filteredText = pastedText.replace(/[^\d-]/g, '')
  
  if (filteredText) {
    // Aplicar el mismo formato que handleCodigoChange
    let formattedText = filteredText.slice(0, 10)
    
    // Insertar guión después de 4 dígitos si no existe
    if (formattedText.length >= 4 && !formattedText.includes('-')) {
      formattedText = formattedText.slice(0, 4) + '-' + formattedText.slice(4)
    }
    
    // Evitar múltiples guiones
    const parts = formattedText.split('-')
    if (parts.length > 2) {
      formattedText = parts[0] + '-' + parts.slice(1).join('')
    }
    
    // Asegurar guión en posición 4
    if (formattedText.includes('-') && formattedText.indexOf('-') !== 4) {
      const digits = formattedText.replace(/-/g, '')
      if (digits.length >= 4) {
        formattedText = digits.slice(0, 4) + '-' + digits.slice(4, 9)
      } else {
        formattedText = digits
      }
    }
    
    caseCode.value = formattedText
  }
}

const searchCase = async () => {
  if (!caseCode.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso';
    return
  }

  isLoadingSearch.value = true
  searchError.value = ''
  caseFound.value = false

  try {
    const data = await casesApiService.getCaseByCode(caseCode.value.trim())
    
    // Validar si el caso puede ser firmado usando el nuevo endpoint
    try {
      const validation = await signApiService.validateCaseForSigning(caseCode.value.trim())
      if (!validation.can_sign) {
        throw new Error(validation.message)
      }
    } catch (validationError: any) {
      // Si la validación falla, mostrar el mensaje específico
      throw new Error(validationError.message || 'El caso no puede ser firmado')
    }
    
    // Validación de permisos específica para patólogos
    if (isPatologo.value && authStore.user) {
      const nombrePatologoAsignado = getAssignedPathologistName(data)
      const nombreUsuario = getCurrentUserName()
      if (!nombrePatologoAsignado) {
        // No lanzar error, permitir cargar el caso pero mostrar alerta
        console.warn('Caso sin patólogo asignado')
      } else if (!nombreUsuario) {
        throw new Error('No se pudo identificar tu nombre de usuario. Contacta al administrador.')
      } else if (nombrePatologoAsignado !== nombreUsuario) {
        throw new Error('No tienes permisos para acceder a este caso. Solo puedes acceder a casos donde estés asignado como patólogo.')
      }
    }
    
    caseFound.value = true
    await loadCaseByCode(caseCode.value.trim())
    await loadExistingDiagnosis(data)
    await hydrateAssignedSignature(data)
  } catch (error: any) {
    caseFound.value = false
    searchError.value = error.message || 'Error al buscar el caso'
  } finally {
    isLoadingSearch.value = false
  }
}
// Hidratar firma del patólogo asignado - usar la que ya viene del backend
const hydrateAssignedSignature = async (caseData: any) => {
  try {
    // La firma ya debería estar en el caso que viene del backend
    const assigned: any = caseData?.assigned_pathologist as any
    if (assigned?.firma) {
      // Asegurar que la firma se propague a caseDetails
      if (caseDetails.value?.assigned_pathologist) {
        (caseDetails.value.assigned_pathologist as any).firma = assigned.firma
      }
    }
  } catch (error) {
    console.warn('SignResults - error en hydrateAssignedSignature:', error)
  }
}

// Carga diagnósticos existentes del caso (CIE-10 y CIE-O) si ya están firmados
const loadExistingDiagnosis = async (caseData: any) => {
  if (caseData.result) {
    const resultado = caseData.result as any
    
    // Cargar diagnóstico CIE-10 (formato nuevo)
    if (resultado.cie10_diagnosis) {
      const diseaseData = { 
        code: resultado.cie10_diagnosis.code, 
        name: resultado.cie10_diagnosis.name, 
        table: 'CIE-10', 
        is_active: true 
      }
      setPrimaryDisease(diseaseData)
    }
    // Compatibilidad con formato legacy
    else if (resultado.diagnostico_cie10) {
      const diseaseData = { 
        code: resultado.diagnostico_cie10.codigo, 
        name: resultado.diagnostico_cie10.nombre, 
        table: 'CIE-10', 
        is_active: true 
      }
      setPrimaryDisease(diseaseData)
    }
    
    // Cargar diagnóstico CIE-O (formato nuevo)
    if (resultado.cieo_diagnosis) {
      const diseaseDataCIEO = { 
        code: resultado.cieo_diagnosis.code, 
        name: resultado.cieo_diagnosis.name, 
        table: 'CIE-O', 
        is_active: true 
      }
      setPrimaryDiseaseCIEO(diseaseDataCIEO)
      showCIEODiagnosis.value = true
    }
    // Compatibilidad con formato legacy
    else if (resultado.diagnostico_cieo) {
      const diseaseDataCIEO = { 
        code: resultado.diagnostico_cieo.codigo, 
        name: resultado.diagnostico_cieo.nombre, 
        table: 'CIE-O', 
        is_active: true 
      }
      setPrimaryDiseaseCIEO(diseaseDataCIEO)
      showCIEODiagnosis.value = true
    }
  }
}

const clearSearch = () => {
  caseCode.value = ''
  caseFound.value = false
  searchError.value = ''
  hasBeenSigned.value = false
  resetEditorAndDiagnosis()
  patient.value = null
  caseDetails.value = null
  previousCases.value = []
}

// Resetea el editor de resultados y diagnósticos a estado inicial
const resetEditorAndDiagnosis = () => {
  sections.value = { method: [], macro: '', micro: '', diagnosis: '' }
  activeSection.value = 'method'
  clearDiagnosis()
  clearPrimaryDiseaseCIEO()
  showCIEODiagnosis.value = false
}



async function handleSign() {
  try {
    signing.value = true
    const validation = validateDiagnosis()
    if (!validation.isValid) {
      validationMessage.value = validation.errors.join(', ')
      return
    }
    if (!canUserSign.value) {
      showError('No autorizado', 'Solo el patólogo asignado al caso o un administrador pueden firmar este resultado.', 0)
      return
    }
    if (!canSignByStatus.value && !hasBeenSigned.value) {
      showError('Estado no válido', invalidStatusMessage.value, 0)
      return
    }
    
    const casoCode = caseDetails?.value?.case_code || props.sampleId
    if (!casoCode) {
      showError('Error al firmar', 'No se pudo obtener el código del caso.', 0)
      return
    }
    
    // Preparar diagnósticos CIE-10 y CIE-O
    const cie10Diagnosis = hasDisease.value && primaryDisease.value ? {
      code: primaryDisease.value.code,
      name: primaryDisease.value.name
    } : undefined
    
    const cieoDiagnosis = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      code: primaryDiseaseCIEO.value.code,
      name: primaryDiseaseCIEO.value.name
    } : undefined
    
    // Preparar datos para el nuevo endpoint
    const requestData = {
      method: sections.value?.method || [],
      macro_result: sections.value?.macro || '',
      micro_result: sections.value?.micro || '',
      diagnosis: sections.value?.diagnosis || '',
      observations: '',
      cie10_diagnosis: cie10Diagnosis,
      cieo_diagnosis: cieoDiagnosis
    }
    
    // Usar el nuevo endpoint de firma
    const response = await signApiService.signCase(casoCode, requestData)
    
    if (response) {
      // Actualizar el caso completo con la respuesta del backend
      caseDetails.value = response
      
      setSavedFromSections()
      savedCaseCode.value = casoCode
      showSuccess('¡Resultado firmado!', `El caso ${casoCode} ha sido firmado y está listo para entregar.`, 0)
      validationMessage.value = ''
      hasBeenSigned.value = true
      clearFormAfterSign()
    } else {
      showError('Error al firmar', 'El servidor no devolvió una respuesta válida.', 0)
    }
  } catch (error: any) {
    showError('Error al firmar', error.message || 'No se pudo firmar el resultado.', 0)
  } finally {
    signing.value = false
  }
}

const handlePrimaryDiseaseChange = (disease: Disease | null) => {
  setPrimaryDisease(disease)
  if (disease) validationMessage.value = ''
}

const handlePrimaryDiseaseCIEOChange = (disease: Disease | null) => {
  setPrimaryDiseaseCIEO(disease)
  if (disease) validationMessage.value = ''
}

const updateSectionContent = (value: string | string[]) => {
  if (sections.value) {
    if (activeSection.value === 'method') {
      sections.value[activeSection.value] = Array.isArray(value) ? value : []
    } else {
      sections.value[activeSection.value] = Array.isArray(value) ? '' : value
    }
  }
}

function clearFormAfterSign() {
  validationMessage.value = ''
  errorMessage.value = ''
}

const handleCaseClick = async (caseItem: any) => {
  try {
    // Obtener el código del caso correctamente
    const caseCodeValue = caseItem.case_code || caseItem.caso_code || caseItem.CasoCode || caseItem.id
    if (!caseCodeValue) {
      console.error('No se encontró código de caso en:', caseItem)
      return
    }
    
    // Cargar el caso completo desde la base de datos
    const fullCase = await casesApiService.getCaseByCode(caseCodeValue)
    selectedPreviousCase.value = fullCase
  } catch (error) {
    console.error('Error al cargar caso completo:', error)
    // Si falla, usar el caso básico
    selectedPreviousCase.value = caseItem
  }
}

const handleNeedsTestsChange = (value: boolean) => {
  needsComplementaryTests.value = value
  if (!value) complementaryTestsDetails.value = ''
}

const handleDetailsChange = (value: string) => {
  complementaryTestsDetails.value = value
}

// Estado para almacenar las pruebas complementarias solicitadas para la notificación
const requestedComplementaryTests = ref<ComplementaryTestInfo[]>([])
const requestedComplementaryTestsReason = ref('')

// Crear solicitud de aprobación (sin lógica de firma ni CIE-10 aquí)
const handleCreateApprovalRequest = async (payload: { case_code: string; reason: string; complementary_tests: ComplementaryTestInfo[] }) => {
  try {
    // Verificar token antes de operación crítica
    const token = localStorage.getItem('auth_token') || sessionStorage.getItem('auth_token')
    if (!token) {
      showError('Sesión expirada', 'Por favor, inicia sesión nuevamente para continuar.', 0)
      return
    }
    
    if (!payload?.case_code || !/^[0-9]{4}-[0-9]{5}$/.test(payload.case_code)) throw new Error('Código de caso inválido')
    if (!payload?.reason?.trim()) throw new Error('Motivo requerido')
    if (!payload?.complementary_tests?.length) throw new Error('Debe seleccionar al menos una prueba')
    
    // Validar que el caso tenga diagnóstico CIE-10 completo
    const validation = validateDiagnosis()
    if (!validation.isValid) {
      throw new Error(`El caso debe tener un diagnóstico CIE-10 completo antes de solicitar pruebas complementarias. Errores: ${validation.errors.join(', ')}`)
    }
    
    // Validar que el caso tenga método, corte macro, micro y diagnósticos completos
    // Verificar en el editor local (sections) en lugar del estado guardado
    if (!sections.value?.macro?.trim()) {
      throw new Error('El caso debe tener un resultado macroscópico antes de solicitar pruebas complementarias')
    }
    if (!sections.value?.micro?.trim()) {
      throw new Error('El caso debe tener un resultado microscópico antes de solicitar pruebas complementarias')
    }
    if (!sections.value?.diagnosis?.trim()) {
      throw new Error('El caso debe tener un diagnóstico antes de solicitar pruebas complementarias')
    }
    
    const response = await approvalService.createApprovalRequest({
      original_case_code: payload.case_code,
      complementary_tests: payload.complementary_tests.map(p => ({ 
        code: p.code, 
        name: p.name || p.code, 
        quantity: p.quantity || 1 
      })),
      reason: payload.reason.trim()
    })
    
    if (response) {
      setSavedFromSections()
      savedCaseCode.value = payload.case_code
      requestedComplementaryTests.value = payload.complementary_tests
      requestedComplementaryTestsReason.value = payload.reason.trim()
      
      // Cambiar estado del caso original a "Por entregar"
      try {
        await casesApiService.updateCaseState(payload.case_code, 'Por entregar')
      } catch (updateError) {
        console.error('Error al actualizar estado del caso:', updateError)
        // No bloquear la operación si falla la actualización del estado
      }
      
      showSuccess('Solicitud de aprobación creada', `Se creó la solicitud de pruebas complementarias para ${payload.case_code}.`, 0)
      needsComplementaryTests.value = false
      complementaryTestsDetails.value = ''
    }
  } catch (error: any) {
    showError('Error al crear solicitud', error.message || 'No se pudo crear la solicitud de aprobación.', 0)
  }
}

// Actualizar el caso original con complementary_tests
const handleUpdateOriginalCase = async (payload: { complementary_tests: Array<ComplementaryTestInfo | { reason: string }> }) => {
  try {
    if (!caseDetails.value?.case_code) {
      throw new Error('No hay código de caso disponible')
    }
    
    console.log('Actualizando caso original con complementary_tests:', payload.complementary_tests)
    
    await casesApiService.updateCase(caseDetails.value.case_code, {
      complementary_tests: payload.complementary_tests
    })
    
    console.log('Caso original actualizado exitosamente con complementary_tests')
    
    // Actualizar el estado local del caso
    if (caseDetails.value) {
      (caseDetails.value as any).complementary_tests = payload.complementary_tests
    }
    
  } catch (error: any) {
    console.error('Error al actualizar caso original:', error)
    showError('Error al actualizar caso', error.message || 'Error desconocido')
  }
}

// Firmar caso con pruebas complementarias
const handleSignWithChanges = async (data: { details: string; tests: ComplementaryTestInfo[] }) => {
  try {
    signing.value = true
    
    // Validar diagnósticos (igual que en handleSign normal)
    const validation = validateDiagnosis()
    if (!validation.isValid) {
      validationMessage.value = validation.errors.join(', ')
      return
    }
    
    // Validar que se pueda firmar
    if (!canUserSign.value) {
      showError('No autorizado', 'Solo el patólogo asignado al caso o un administrador pueden firmar este resultado.', 0)
      return
    }
    
    if (!canSignByStatus.value && !hasBeenSigned.value) {
      showError('Estado no válido', invalidStatusMessage.value, 0)
      return
    }
    
    const casoCode = caseDetails?.value?.case_code || props.sampleId
    if (!casoCode) {
      showError('Error al firmar', 'No se pudo obtener el código del caso.', 0)
      return
    }
    
    // Preparar diagnósticos CIE-10 y CIE-O
    const cie10Diagnosis = hasDisease.value && primaryDisease.value ? {
      code: primaryDisease.value.code,
      name: primaryDisease.value.name
    } : undefined
    
    const cieoDiagnosis = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      code: primaryDiseaseCIEO.value.code,
      name: primaryDiseaseCIEO.value.name
    } : undefined
    
    // Preparar datos para el nuevo endpoint (incluyendo observaciones de pruebas complementarias)
    const requestData = {
      method: sections.value?.method || [],
      macro_result: sections.value?.macro || '',
      micro_result: sections.value?.micro || '',
      diagnosis: sections.value?.diagnosis || '',
      observations: data.details, // Usar el motivo de las pruebas complementarias
      cie10_diagnosis: cie10Diagnosis,
      cieo_diagnosis: cieoDiagnosis
    }
    
    // Usar el nuevo endpoint de firma
    const response = await signApiService.signCase(casoCode, requestData)
    
    if (response) {
      // Actualizar el caso completo con la respuesta del backend
      caseDetails.value = response
      
      // Guardar contenido para notificación
      setSavedFromSections()
      savedCaseCode.value = casoCode
      
      // Guardar las pruebas complementarias solicitadas para la notificación
      requestedComplementaryTests.value = data.tests
      requestedComplementaryTestsReason.value = data.details
      
      showSuccess('¡Caso firmado con pruebas complementarias!', `El caso ${casoCode} ha sido firmado y se creó la solicitud de pruebas complementarias.`, 0)
      validationMessage.value = ''
      hasBeenSigned.value = true
      
      // Limpiar formulario después de firmar
      clearFormAfterSign()
      needsComplementaryTests.value = false
      complementaryTestsDetails.value = ''
    } else {
      showError('Error al firmar', 'El servidor no devolvió una respuesta válida.', 0)
    }
  } catch (error: any) {
    showError('Error al firmar con pruebas complementarias', error.message || 'No se pudo firmar el resultado.', 0)
  } finally {
    signing.value = false
  }
}

// Función para cerrar notificación y limpiar pruebas complementarias
const handleNotificationClose = () => {
  closeNotification()
  // Limpiar pruebas complementarias para que no se muestren en próximas notificaciones
  requestedComplementaryTests.value = []
  requestedComplementaryTestsReason.value = ''
}


</script>
