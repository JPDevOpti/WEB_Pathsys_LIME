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
              {{ casoEncontrado ? 'Firmar Resultados' : 'Buscar Caso para Firmar Resultados' }}
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
          <h3 class="text-sm font-semibold text-gray-700 mb-3">
            Buscar Caso
          </h3>

          <div class="flex flex-col md:flex-row gap-3 md:gap-4 items-stretch md:items-end">
            <div class="flex-1">
              <FormInputField id="codigo-caso" :model-value="codigoCaso" @update:model-value="handleCodigoChange"
                type="text" placeholder="Ejemplo: 2025-00001" maxlength="10" autocomplete="off" :disabled="isLoadingSearch"
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
              <DiseaseList :model-value="primaryDisease" @update:model-value="handlePrimaryDiseaseChange"
                @cieo-disease-selected="handlePrimaryDiseaseCIEOChange" label="Diagnóstico CIE-10"
                placeholder="Buscar enfermedad CIE-10..." :required="true" />
            </div>
          </div>

          <ComplementaryTestsSection
            :initial-needs-tests="needsComplementaryTests"
            :initial-details="complementaryTestsDetails"
            @needs-tests-change="handleNeedsTestsChange"
            @details-change="handleDetailsChange"
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
            <button
              :disabled="loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature"
              :class="['px-4 py-2 text-sm font-medium rounded-md', (loading || !hasDisease || needsAssignedPathologist || !canUserSign || (!canSignByStatus && !hasBeenSigned) || isPathologistWithoutSignature) ? 'bg-gray-300 text-gray-500 cursor-not-allowed' : 'bg-blue-600 text-white hover:bg-blue-700']"
              @click="handleSign"
            >
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
          context="sign"
          @close="closeNotification"
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
import { SearchButton, ClearButton, PreviewButton } from '@/shared/components/buttons'
import { DiseaseList } from '@/shared/components/List'
import DocsIcon from '@/assets/icons/DocsIcon.vue'
import WarningIcon from '@/assets/icons/WarningIcon.vue'
import ErrorIcon from '@/assets/icons/ErrorIcon.vue'
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
import casoAprobacionService from '@/modules/cases/services/casoAprobacionApi.service'
import type { PruebaComplementaria } from '@/modules/cases/services/casoAprobacionApi.service'

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
  if (normalizedStatus === 'COMPLETADO') return 'Este caso ya ha sido completado y firmado.'
  return ''
})

const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')
const selectedPreviousCase = ref<any>(null)

const isValidCodigoFormat = (codigo: string | undefined | null): boolean => {
  if (!codigo || typeof codigo !== 'string' || codigo.trim() === '') return false
  const regex = /^\d{4}-\d{5}$/
  return regex.test(codigo.trim())
}

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
// Hidratar firma del patólogo asignado desde backend si no está presente en el caso
const hydrateAssignedSignature = async (caseData: any) => {
  try {
    const assigned: any = caseData?.patologo_asignado as any
    const currentAssigned: any = (caseDetails.value as any)?.patologo_asignado as any
    const code = assigned?.codigo || currentAssigned?.codigo
    const hasFirma = assigned?.firma || currentAssigned?.firma
    if (!code || hasFirma) return
    const pb = await profileApiService.getPathologistByCode(code)
    const firmaUrl = (pb as any)?.firma || ''
    if (firmaUrl) {
      if (caseData?.patologo_asignado) (caseData.patologo_asignado as any).firma = firmaUrl
      if (caseDetails.value?.patologo_asignado) (caseDetails.value.patologo_asignado as any).firma = firmaUrl
    }
  } catch {}
}

// Carga diagnósticos existentes del caso (CIE-10 y CIE-O) si ya están firmados
const loadExistingDiagnosis = async (caseData: any) => {
  if (caseData.resultado) {
    const resultado = caseData.resultado as any
    if (resultado.diagnostico_cie10) {
      const diseaseData = { codigo: resultado.diagnostico_cie10.codigo, nombre: resultado.diagnostico_cie10.nombre, tabla: 'CIE-10', isActive: true }
      setPrimaryDisease(diseaseData)
    }
    if (resultado.diagnostico_cieo) {
      const diseaseDataCIEO = { codigo: resultado.diagnostico_cieo.codigo, nombre: resultado.diagnostico_cieo.nombre, tabla: 'CIE-O', isActive: true }
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

function handleClearResults() { resetEditorAndDiagnosis() }

function goToPreview() {
  const payload = {
    sampleId: caseDetails?.value?.caso_code || props.sampleId,
    patient: patient?.value || null,
    caseDetails: caseDetails?.value || null,
    sections: sections?.value || null,
    diagnosis: {
      cie10: getDiagnosisData(),
      cieo: hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? { codigo: primaryDiseaseCIEO.value.codigo, nombre: primaryDiseaseCIEO.value.nombre } : undefined,
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
      codigo: primaryDisease.value.codigo,
      nombre: primaryDisease.value.nombre
    } : undefined
    const diagnosticoCIEO = hasDiseaseCIEO.value && primaryDiseaseCIEO.value ? {
      codigo: primaryDiseaseCIEO.value.codigo,
      nombre: primaryDiseaseCIEO.value.nombre
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
    const fullCase = await casesApiService.getCaseByCode(caseItem.caso_code)
    selectedPreviousCase.value = fullCase
  } catch (error) {
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

// Flujo para firmar caso y crear solicitud de pruebas complementarias
const handleSignWithChanges = async (data: { details: string; tests: { code: string; name: string; quantity: number }[] }) => {
  try {
    if (!caseDetails.value) {
      showError('Error al crear solicitud', 'No se encontraron los detalles del caso.', 0)
      return
    }
    if (!canUserSign.value) {
      showError('No autorizado', 'Solo el patólogo asignado al caso o un administrador pueden solicitar pruebas complementarias.', 0)
      return
    }
    const diagnosticoCie10 = getDiagnosisData()
    const resultData = {
      metodo: sections.value.method || [],
      resultado_macro: sections.value.macro || '',
      resultado_micro: sections.value.micro || '',
      diagnostico: sections.value.diagnosis || '',
      observaciones: '',
      diagnostico_cie10: diagnosticoCie10?.primary ? {
        codigo: diagnosticoCie10.primary.codigo,
        nombre: diagnosticoCie10.primary.nombre
      } : undefined,
      diagnostico_cieo: primaryDiseaseCIEO.value ? {
        codigo: primaryDiseaseCIEO.value.codigo,
        nombre: primaryDiseaseCIEO.value.nombre
      } : undefined
    }
    const patologoCodigo = authStore.user?.id || 'unknown'
    // 1. Firmar el resultado
    await resultsApiService.firmarResultado(caseDetails.value.caso_code, resultData, patologoCodigo)
    // 2. Marcar caso como completado para pruebas complementarias
    try {
      await resultsApiService.cambiarEstadoResultado(caseDetails.value.caso_code, 'COMPLETADO')
      if (caseDetails.value) caseDetails.value.estado = 'COMPLETADO'
    } catch (e) {
      if (caseDetails.value) caseDetails.value.estado = 'COMPLETADO'
    }
    // 3. Recargar datos del caso completado
    const casoCompletado = await casesApiService.getCaseByCode(caseDetails.value.caso_code)
    if (!casoCompletado) {
      throw new Error('No se pudo obtener el caso completado')
    }
    // 4. Crear solicitud de aprobación para pruebas complementarias
    const pruebasComplementarias: PruebaComplementaria[] = data.tests.map(test => ({
      codigo: test.code,
      nombre: test.name,
      cantidad: test.quantity || 1,
      observaciones: ''
    }))
    const response = await casoAprobacionService.createFromSignature(
      casoCompletado.caso_code,
      pruebasComplementarias,
      data.details,
      authStore.user?.id || getCurrentUserName() || 'unknown_user'
    )
    if (response) {
      setSavedFromSections()
      savedCaseCode.value = casoCompletado.caso_code
      showSuccess(
        '¡Caso completado y solicitud creada!',
        `El caso ${casoCompletado.caso_code} ha sido firmado y completado. Se ha creado una solicitud de aprobación para las pruebas complementarias que está pendiente de autorización administrativa.`,
        8000
      )
      needsComplementaryTests.value = false
      complementaryTestsDetails.value = ''
      clearFormAfterSign()
    }
  } catch (error: any) {
    showError('Error al procesar solicitud', error.message || 'No se pudo completar el caso y crear la solicitud de aprobación.', 0)
  }
}


</script>
