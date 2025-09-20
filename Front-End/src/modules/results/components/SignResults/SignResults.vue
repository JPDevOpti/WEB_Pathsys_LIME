<template>
  <div class="space-y-6">
    <div class="grid gap-6 items-start grid-cols-1 lg:grid-cols-3">
      <ComponentCard 
        :class="[
          'flex flex-col',
          casoEncontrado ? 'lg:col-span-2 min-h-[640px]' : 'lg:col-span-2 min-h-[160px]'
        ]" 
        :dense="false"
      >
        <div class="flex items-center justify-between mb-2">
          <div>
            <h2 class="text-lg font-semibold">
              {{ casoEncontrado ? 'Firmar Resultados' : 'Buscar caso para firmar resultados' }}
            </h2>
            <p v-if="!casoEncontrado" class="text-sm text-gray-500 mt-1">
              Ingresa el código del caso para acceder a la firma de resultados
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
              <FormInputField id="codigo-caso" :model-value="codigoCaso" @update:model-value="handleCodigoChange"
                type="text" placeholder="Ejemplo: 2025-00001" maxlength="10" autocomplete="off" :disabled="isLoadingSearch"
                @keydown.enter.prevent="buscarCaso" @keydown="keydownHandler" @paste="handlePaste" class="flex-1" />

            </div>

            <div class="flex gap-2 md:gap-3 md:mt-0 mt-2">
              <SearchButton v-if="!casoEncontrado" text="Buscar" loading-text="Buscando..." :loading="isLoadingSearch"
                @click="buscarCaso" size="md" variant="primary" />

              <ClearButton v-if="casoEncontrado" text="Limpiar" @click="limpiarBusqueda" />
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

        <div v-if="casoEncontrado" class="flex-1 flex flex-col min-h-0 mt-0">
          <ResultEditor class="flex-1 min-h-0" :model-value="sections[activeSection]"
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
            :caso-original="caseDetails?.caso_code || codigoCaso"
            @needs-tests-change="handleNeedsTestsChange"
            @details-change="handleDetailsChange"
            @create-approval-request="handleCreateApprovalRequest"
            @sign-with-changes="handleSignWithChanges"
          />

          <ValidationAlert :visible="!!validationMessage" class="mt-2"
            :errors="validationMessage ? [validationMessage] : []" />
          <ErrorMessage v-if="errorMessage" class="mt-2" :message="errorMessage" />

          <div v-if="caseDetails?.caso_code && !caseDetails.patologo_asignado?.nombre && authStore.user?.rol === 'patologo'"
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

          <div v-if="caseDetails?.caso_code && !caseDetails.patologo_asignado?.nombre && authStore.user?.rol === 'administrador'"
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

          <div v-if="caseDetails?.caso_code && caseDetails.patologo_asignado?.nombre && !canUserSign"
            class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <ErrorIcon class="w-5 h-5 text-red-500 mr-2 flex-shrink-0" />
              <div>
                <p class="text-sm font-medium text-red-800">No autorizado para firmar</p>
                <p class="text-sm text-red-700">
                  <template v-if="authStore.user?.rol === 'patologo'">
                    Este caso está asignado a <strong>{{ caseDetails.patologo_asignado.nombre }}</strong>. 
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
          <div v-if="caseDetails?.caso_code && !canSignByStatus && !hasBeenSigned"
            class="mt-3 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-3 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <div>
                <p class="text-sm font-bold text-red-800">Caso ya completado</p>
                <p class="text-sm text-red-700 mt-1">
                  Este caso ya ha sido completado y firmado. No se puede firmar nuevamente.
                </p>
                <p class="text-xs text-red-600 mt-2">
                  Estado actual: <span class="font-semibold">{{ caseDetails?.estado }}</span>
                </p>
              </div>
            </div>
          </div>

          <div class="mt-3 flex flex-wrap items-center gap-3 justify-end">
            <ClearButton :disabled="loading" @click="limpiarBusqueda" />
            <!-- Botón de previsualización temporalmente deshabilitado -->
            <button
              :disabled="loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature"
              :class="['px-4 py-2 text-sm font-medium rounded-md flex items-center gap-2', (loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature) ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700']"
              @click="handleSign"
            >
              <SignIcon :size="16" />
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
          :case-code="savedCaseCode || caseDetails?.caso_code || props.sampleId"
          :saved-content="savedContent"
          :diagnoses="{
            cie10: (hasDisease && primaryDisease) ? { codigo: primaryDisease.codigo, nombre: primaryDisease.nombre } : undefined,
            cieo: (hasDiseaseCIEO && primaryDiseaseCIEO) ? { codigo: primaryDiseaseCIEO.codigo, nombre: primaryDiseaseCIEO.nombre } : undefined
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
import { useRouter } from 'vue-router'
import { ComponentCard } from '@/shared/components'
import { ErrorMessage, ValidationAlert } from '@/shared/components/feedback'
import { FormInputField } from '@/shared/components/forms'
import { SearchButton, ClearButton } from '@/shared/components/buttons'
import { DiseaseList } from '@/shared/components/List'
import DocsIcon from '@/assets/icons/DocsIcon.vue'
import WarningIcon from '@/assets/icons/WarningIcon.vue'
import ErrorIcon from '@/assets/icons/ErrorIcon.vue'
import SignIcon from '@/assets/icons/SignIcon.vue'
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
import resultsApiService from '../../services/resultsApiService'
import casoAprobacionService from '@/modules/results/services/casoAprobacion.service'
import type { PruebaComplementaria } from '@/modules/results/services/casoAprobacion.service'

interface Props {
  sampleId: string
  autoSearch?: boolean
}
const props = defineProps<Props>()

const { loading, patient, caseDetails, activeSection, errorMessage, validationMessage, initialize, previousCases, sections, loadCaseByCode, primaryDiseaseCIEO, hasDiseaseCIEO, showCIEODiagnosis, setPrimaryDiseaseCIEO, clearPrimaryDiseaseCIEO } = usePerformResults(props.sampleId)
const { isPatologo } = usePermissions()
const authStore = useAuthStore()
const { notification, showSuccess, showError, closeNotification } = useNotifications()
const { primaryDisease, hasDisease, setPrimaryDisease, clearDiagnosis, formatDiagnosisForReport, getDiagnosisData, validateDiagnosis } = useDiseaseDiagnosis()
const router = useRouter()

const handleClearSearch = () => limpiarBusqueda()
onMounted(() => {
  initialize()
  if (props.autoSearch && props.sampleId) ejecutarBusquedaAutomatica()
  window.addEventListener('clear-search', handleClearSearch)
  // Refrescar firma del patólogo desde backend si no está en memoria
  try {
    const email = authStore.user?.email
    if (authStore.user?.rol === 'patologo' && email) {
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

const ejecutarBusquedaAutomatica = async () => {
  if (!props.sampleId) return
  codigoCaso.value = props.sampleId
  await buscarCaso()
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
  if (!caseDetails.value?.patologo_asignado?.nombre || !authStore.user) return false
  const assignedPathologist = caseDetails.value.patologo_asignado.nombre
  const currentUser = getCurrentUserName()
  return assignedPathologist === currentUser
})

// Reglas de autorización: administradores pueden firmar cualquier caso, patólogos solo sus casos asignados
const canUserSign = computed(() => {
  if (!authStore.user) return false
  if (authStore.user.rol === 'administrador') return true
  if (authStore.user.rol === 'patologo') return isAssignedPathologist.value
  return false
})

// Patólogo sin firma digital configurada
const isPathologistWithoutSignature = computed(() => {
  if (!authStore.user) return false
  if (authStore.user.rol !== 'patologo') return false
  let firma = (authStore.user as any).firma || (authStore.user as any).firma_url || (authStore.user as any).signatureUrl || (authStore.user as any).firmaDigital
  if (!firma) {
    try { firma = localStorage.getItem('signature_url') || firma } catch {}
    try { firma = sessionStorage.getItem('signature_url') || firma } catch {}
  }
  return !firma || (typeof firma === 'string' && firma.trim() === '')
})

// Solo los patólogos requieren que el caso tenga un patólogo asignado
const needsAssignedPathologist = computed(() => {
  if (!authStore.user || !caseDetails.value?.caso_code) return false
  if (authStore.user.rol === 'patologo') return !caseDetails.value.patologo_asignado?.nombre
  return false
})

// Normaliza estados a formato de BD (mayúsculas y guiones bajos)
const normalizeStatus = (status: string): string => {
  if (!status) return status
  return status.toUpperCase().replace(/\s+/g, '_')
}

// Solo se puede firmar si el caso NO está en estado COMPLETADO
const canSignByStatus = computed(() => {
  if (!caseDetails.value?.estado) return false
  const normalizedStatus = normalizeStatus(caseDetails.value.estado)
  return normalizedStatus !== 'COMPLETADO'
})

const invalidStatusMessage = computed(() => {
  if (!caseDetails.value?.estado) return ''
  const estado = caseDetails.value.estado
  const normalizedStatus = normalizeStatus(estado)
  if (normalizedStatus === 'COMPLETADO') {
    return 'Este caso ya ha sido completado y firmado. No se puede firmar nuevamente.'
  }
  return `El estado "${estado}" no permite la firma del caso.`
})

const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')
const selectedPreviousCase = ref<any>(null)


// Extrae el nombre completo del usuario desde diferentes formatos posibles
const getCurrentUserName = (): string | null => {
  if (!authStore.user) return null
  let userName = (authStore.user as any).username ||
    authStore.user.nombre ||
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
    
    codigoCaso.value = formattedText
  }
}

const buscarCaso = async () => {
  if (!codigoCaso.value.trim()) {
    searchError.value = 'Por favor, ingrese un código de caso';
    return
  }

  isLoadingSearch.value = true
  searchError.value = ''
  casoEncontrado.value = false

  try {
    const data = await casesApiService.getCaseByCode(codigoCaso.value.trim())
    // Validación de permisos específica para patólogos
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
    await loadExistingDiagnosis(data)
    await hydrateAssignedSignature(data)
  } catch (error: any) {
    casoEncontrado.value = false
    searchError.value = error.message || 'Error al buscar el caso'
  } finally {
    isLoadingSearch.value = false
  }
}
// Hidratar firma del patólogo asignado - usar la que ya viene del backend
const hydrateAssignedSignature = async (caseData: any) => {
  try {
    console.log('SignResults - DEBUG caso completo:', caseData)
    console.log('SignResults - DEBUG patologo_asignado:', caseData?.patologo_asignado)
    console.log('SignResults - DEBUG firma en caso:', caseData?.patologo_asignado?.firma ? 'SÍ' : 'NO')
    
    // La firma ya debería estar en el caso que viene del backend
    const assigned: any = caseData?.patologo_asignado as any
    if (assigned?.firma) {
      console.log('SignResults - FIRMA ENCONTRADA EN EL CASO')
      // Asegurar que la firma se propague a caseDetails
      if (caseDetails.value?.patologo_asignado) {
        (caseDetails.value.patologo_asignado as any).firma = assigned.firma
      }
    } else {
      console.log('SignResults - NO HAY FIRMA EN EL CASO')
    }
  } catch (error) {
    console.warn('SignResults - error en hydrateAssignedSignature:', error)
  }
}

// Carga diagnósticos existentes del caso (CIE-10 y CIE-O) si ya están firmados
const loadExistingDiagnosis = async (caseData: any) => {
  if (caseData.resultado) {
    const resultado = caseData.resultado as any
    
    if (resultado.diagnostico_cie10) {
      const diseaseData = { code: resultado.diagnostico_cie10.codigo, name: resultado.diagnostico_cie10.nombre, table: 'CIE-10', is_active: true }
      setPrimaryDisease(diseaseData)
    }
    
    if (resultado.diagnostico_cieo) {
      const diseaseDataCIEO = { code: resultado.diagnostico_cieo.codigo, name: resultado.diagnostico_cieo.nombre, table: 'CIE-O', is_active: true }
      setPrimaryDiseaseCIEO(diseaseDataCIEO)
      showCIEODiagnosis.value = true
    }
  }
}

const limpiarBusqueda = () => {
  codigoCaso.value = ''
  casoEncontrado.value = false
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


function goToPreview() {
  const payload = {
    sampleId: caseDetails?.value?.caso_code || props.sampleId,
    patient: patient?.value || null,
    caseDetails: caseDetails?.value || null,
    sections: sections?.value || null,
    diagnosis: {
      cie10: getDiagnosisData(),
      cieo: hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? { codigo: primaryDiseaseCIEO.value.code, nombre: primaryDiseaseCIEO.value.name } : undefined,
      formatted: formatDiagnosisForReport()
    },
    generatedAt: new Date().toISOString()
  }
  // Función de previsualización temporalmente deshabilitada
  console.log('Previsualización temporalmente deshabilitada')
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
    let patologoCodigo = caseDetails?.value?.patologo_asignado?.codigo
    if (!patologoCodigo && authStore.user?.rol === 'administrador') {
      patologoCodigo = authStore.user.id || 'admin'
    }
    if (!patologoCodigo) {
      showError('Error al firmar', 'No se pudo identificar el patólogo para firmar el caso.', 0)
      return
    }
    const casoCode = caseDetails?.value?.caso_code || props.sampleId
    const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
      codigo: primaryDisease.value.code,
      nombre: primaryDisease.value.name
    } : undefined
    const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      codigo: primaryDiseaseCIEO.value.code,
      nombre: primaryDiseaseCIEO.value.name
    } : undefined
    const requestData = {
      metodo: sections.value?.method || [],
      resultado_macro: sections.value?.macro || '',
      resultado_micro: sections.value?.micro || '',
      diagnostico: sections.value?.diagnosis || '',
      observaciones: '',
      diagnostico_cie10: diagnosticoCie10,
      diagnostico_cieo: diagnosticoCIEO
    }
    const response = await resultsApiService.firmarResultado(casoCode, requestData, patologoCodigo)
    console.log('Respuesta del backend al firmar:', response)
    if (response) {
      if (caseDetails.value) {
        if (response.estado) caseDetails.value.estado = response.estado
        if (response.fecha_firma) caseDetails.value.fecha_firma = response.fecha_firma
        console.log('CaseDetails actualizado:', caseDetails.value)
      }
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
    showError('Error al firmar', error.response?.data?.message || error.message || 'No se pudo firmar el resultado.', 0)
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
    const caseCode = caseItem.caso_code || caseItem.CasoCode || caseItem.id
    if (!caseCode) {
      console.error('No se encontró código de caso en:', caseItem)
      return
    }
    
    // Cargar el caso completo desde la base de datos
    const fullCase = await casesApiService.getCaseByCode(caseCode)
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
const requestedComplementaryTests = ref<PruebaComplementaria[]>([])
const requestedComplementaryTestsReason = ref('')

// Crear solicitud de aprobación (sin lógica de firma ni CIE-10 aquí)
const handleCreateApprovalRequest = async (payload: { caso_original: string; motivo: string; pruebas_complementarias: PruebaComplementaria[] }) => {
  try {
    if (!payload?.caso_original || !/^[0-9]{4}-[0-9]{5}$/.test(payload.caso_original)) throw new Error('Código de caso inválido')
    if (!payload?.motivo?.trim()) throw new Error('Motivo requerido')
    if (!payload?.pruebas_complementarias?.length) throw new Error('Debe seleccionar al menos una prueba')
    
    const response = await casoAprobacionService.createCasoAprobacion({
      caso_original: payload.caso_original,
      motivo: payload.motivo.trim(),
      pruebas_complementarias: payload.pruebas_complementarias.map(p => ({ codigo: p.codigo, nombre: p.nombre || p.codigo, cantidad: p.cantidad || 1 }))
    })
    
    if (response) {
      // Guardar el contenido actual del formulario para la notificación
      setSavedFromSections()
      savedCaseCode.value = payload.caso_original
      
      // Guardar las pruebas complementarias solicitadas para la notificación
      requestedComplementaryTests.value = payload.pruebas_complementarias
      requestedComplementaryTestsReason.value = payload.motivo.trim()
      
      showSuccess('Solicitud de aprobación creada', `Se creó la solicitud de pruebas complementarias para ${payload.caso_original}.`, 0)
      needsComplementaryTests.value = false
      complementaryTestsDetails.value = ''
    }
  } catch (error: any) {
    showError('Error al crear solicitud', error.message || 'No se pudo crear la solicitud de aprobación.', 0)
  }
}

// Firmar caso con pruebas complementarias
const handleSignWithChanges = async (data: { details: string; tests: PruebaComplementaria[] }) => {
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
    
    // Obtener código del patólogo
    let patologoCodigo = caseDetails?.value?.patologo_asignado?.codigo
    if (!patologoCodigo && authStore.user?.rol === 'administrador') {
      patologoCodigo = authStore.user.id || 'admin'
    }
    if (!patologoCodigo) {
      showError('Error al firmar', 'No se pudo identificar el patólogo para firmar el caso.', 0)
      return
    }
    
    const casoCode = caseDetails?.value?.caso_code || props.sampleId
    
    // Preparar diagnósticos CIE-10 y CIE-O (igual que en handleSign normal)
    const diagnosticoCie10 = hasDisease.value && primaryDisease.value ? {
      codigo: primaryDisease.value.code,
      nombre: primaryDisease.value.name
    } : undefined
    const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      codigo: primaryDiseaseCIEO.value.code,
      nombre: primaryDiseaseCIEO.value.name
    } : undefined
    
    // Preparar datos para firmar (incluyendo diagnósticos CIE-10/CIEO)
    const requestData = {
      metodo: sections.value?.method || [],
      resultado_macro: sections.value?.macro || '',
      resultado_micro: sections.value?.micro || '',
      diagnostico: sections.value?.diagnosis || '',
      observaciones: data.details, // Usar el motivo de las pruebas complementarias
      diagnostico_cie10: diagnosticoCie10,
      diagnostico_cieo: diagnosticoCIEO
    }
    
    // Firmar el caso
    const response = await resultsApiService.firmarResultado(casoCode, requestData, patologoCodigo)
    console.log('Respuesta del backend al firmar con pruebas complementarias:', response)
    
    if (response) {
      // Actualizar el estado del caso
      if (caseDetails.value) {
        if (response.estado) caseDetails.value.estado = response.estado
        if (response.fecha_firma) caseDetails.value.fecha_firma = response.fecha_firma
        console.log('CaseDetails actualizado con fecha de firma:', caseDetails.value)
      }
      
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
    showError('Error al firmar con pruebas complementarias', error.response?.data?.message || error.message || 'No se pudo firmar el resultado.', 0)
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
