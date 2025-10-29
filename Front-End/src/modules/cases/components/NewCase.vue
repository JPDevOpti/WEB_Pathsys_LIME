<template>
  <div class="space-y-4 lg:space-y-6">
    <!-- Card 1: Patient Search Section -->
    <ComponentCard 
      title="Buscar Paciente" 
      description="Busque y verifique el paciente antes de crear el caso médico."
    >
      <template #icon>
        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </template>
      
      <div class="space-y-4">
        <PatientSearch
          :identificationType="searchIdentificationType"
          :identificationNumber="searchIdentificationNumber"
          :errorMessage="searchError"
          :patientVerified="patientVerified"
          :loading="isSearching"
          :identificationTypeOptions="identificationTypeOptions"
          @update:identificationType="(v) => (searchIdentificationType = v as any)"
          @update:identificationNumber="(v) => (searchIdentificationNumber = v)"
          @search="searchPatient"
          @clear="clearPatientVerification"
        />

        <!-- Botón Crear Paciente al lado derecho cuando no se encuentra -->
        <div
          v-if="searchError && String(searchError).includes('No se encontró un paciente')"
          class="flex justify-end"
        >
          <BaseButton
            variant="outline"
            text="Crear Paciente"
            :customClass="'bg-white text-red-600 border-red-600 hover:bg-red-50 focus:ring-red-500 active:bg-red-100'"
            @click="goToCreatePatient"
          >
            <template #icon-left>
              <NewPatientIcon class="w-5 h-5 mr-2" />
            </template>
          </BaseButton>
        </div>

        <!-- Compact patient found summary -->
        <div 
          v-if="patientVerified && verifiedPatient" 
          ref="patientVerifiedSection"
          class="mt-4 p-3 sm:p-4 bg-green-50 border border-green-200 rounded-lg"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div>
                <h4 class="text-sm font-semibold text-green-800">Paciente Verificado</h4>
                <p class="text-xs text-green-600 mt-0.5">Complete el formulario del caso abajo</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-xs text-green-600 font-medium">Paciente</p>
              <p class="text-sm font-semibold text-green-800">{{ verifiedPatient.name }}</p>
            </div>
          </div>
        </div>

        <div>
          <Notification 
            :visible="notification.visible" 
            :type="notification.type" 
            :title="notification.title" 
            :message="notification.message" 
            :inline="true" 
            :auto-close="false" 
            @close="closeNotification" 
          />
        </div>

        <!-- Helper message when no patient verified -->
        <div v-if="!patientVerified && !notification.visible" class="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div class="flex flex-col items-center space-y-3">
            <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <h3 class="text-lg font-medium text-blue-800">Busque un paciente para crear un caso</h3>
            <p class="text-blue-600 text-sm">Ingrese los datos del paciente en el campo de búsqueda arriba para comenzar a crear un nuevo caso médico</p>
          </div>
        </div>
      </div>
    </ComponentCard>

    <!-- Cards 2 & 3: Side by side - Case Form (left 60%) and Patient Info (right 40%) -->
    <div v-if="patientVerified" class="grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6 items-start">
      <!-- Card 2: Case Form (LEFT - 60%) -->
      <div class="lg:col-span-3">
        <ComponentCard 
          title="Información del Caso" 
          description="Complete los datos médicos del caso."
        >
          <template #icon>
            <CaseIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>

          <CaseForm
            :formData="formData"
            :edit-mode="false"
            :validationState="validationState"
            :errors="errors"
            :warnings="warnings"
            :tipoAtencionOptions="tipoAtencionOptions"
            :prioridadOptions="prioridadOptions"
            :getMedicoErrors="getMedicoErrors"
            :getServicioErrors="getServicioErrors"
            :getRegionErrors="getRegionErrors"
            :getPruebaErrors="getPruebaErrors"
            @numberOfSamplesChange="(v:number) => handleNumberOfSamplesChange(String(v))"
            @addTest="addTestToSample"
            @removeTest="removeTestFromSample"
            @testSelected="onTestSelected"
          />

          <template #footer>
            <div class="flex flex-col sm:flex-row justify-end gap-3">
              <ClearButton @click="clearForm" />
              <SaveButton text="Guardar Caso" @click="handleSaveClick" />
            </div>
          </template>
        </ComponentCard>
      </div>

      <!-- Card 3: Patient Information (RIGHT - 40%) -->
      <div class="lg:col-span-2">
        <ComponentCard 
          title="Información del Paciente" 
          description="Datos del paciente verificado."
        >
          <template #icon>
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z"/>
            </svg>
          </template>

          <div class="overflow-y-auto custom-scrollbar" style="max-height: 600px;">
            <PatientInfoCard 
              :patient="verifiedPatient"
              badge-label="Verificado"
              empty-state-message="No hay paciente verificado"
              empty-state-subtext="Busque un paciente para continuar"
            />
          </div>
        </ComponentCard>
      </div>
    </div>

    <!-- Validation alert -->
    <ValidationAlert 
      :visible="validationState.showValidationError" 
      :errors="validationErrors" 
      @close="validationState.showValidationError = false" 
    />

    <!-- Success modal -->
    <div ref="notificationContainer">
      <CaseSuccessCard
        :visible="showCaseSuccessCard"
        :caseData="createdCase || {}"
        mode="created"
        @close="closeCaseSuccessCard"
      />
    </div>
  </div>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch, onMounted } from 'vue'
import { useRoute, useRouter } from 'vue-router'
import { useCaseForm } from '../composables/useCaseForm'
import { usePatientVerification } from '../composables/usePatientVerification'
import { useNotifications } from '../composables/useNotifications'
import { useCaseAPI } from '../composables/useCaseAPI'
import type { PatientData, CreatedCase } from '../types'
import { ComponentCard, BaseButton } from '@/shared/components'
import { ValidationAlert, Notification, CaseSuccessCard } from '@/shared/components/ui/feedback'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { CaseIcon } from '@/assets/icons'
import { PatientInfoCard, CaseForm, PatientSearch } from './Shared'
import { patientsApiService } from '@/modules/patients/services'
import NewPatientIcon from '@/assets/icons/NewPatientIcon.vue'

const notificationContainer = ref<HTMLElement | null>(null)
const patientVerifiedSection = ref<HTMLElement | null>(null)
const createdCase = ref<CreatedCase | null>(null)
const showCaseSuccessCard = ref(false)
const emit = defineEmits(['case-saved', 'patient-verified'])
const route = useRoute()
const router = useRouter()

const { formData, validationState, errors, warnings, validateForm, clearForm: clearCaseForm, handleNumberOfSamplesChange, addTestToSample, removeTestFromSample } = useCaseForm()
const { isSearching, searchError, patientVerified, verifiedPatient, useNewPatient, clearVerification, searchPatientByDocumento } = usePatientVerification()
const { notification, showNotification, closeNotification } = useNotifications()
const { createCase, error: apiError, clearState } = useCaseAPI()

const searchIdentificationType = ref<string | number>('')
const searchIdentificationNumber = ref('')

// Normaliza códigos de documento string (ej: 'CC', 'CE') a números del enum
const CODE_TO_IDENTIFICATION_TYPE: Record<string, number> = {
  CC: 1,
  CE: 2,
  TI: 3,
  PA: 4,
  RC: 5,
  DE: 6,
  NIT: 7,
  CD: 8,
  SC: 9
}

const normalizeIdType = (val: unknown): number | undefined => {
  if (val == null) return undefined
  if (typeof val === 'number' && !isNaN(val)) return val
  const s = String(val).trim().toUpperCase()
  if (!s) return undefined
  // Si es un número en string, conviértelo
  const asNum = Number(s)
  if (!isNaN(asNum) && asNum > 0) return asNum
  // Si es un código conocido, mapea
  return CODE_TO_IDENTIFICATION_TYPE[s]
}

const identificationTypeOptions = [
  { value: 1, label: 'Cédula de Ciudadanía' },
  { value: 2, label: 'Cédula de Extranjería' },
  { value: 3, label: 'Tarjeta de Identidad' },
  { value: 4, label: 'Pasaporte' },
  { value: 5, label: 'Registro Civil' },
  { value: 6, label: 'Documento Extranjero' },
  { value: 7, label: 'NIT' },
  { value: 8, label: 'Carnet Diplomático' },
  { value: 9, label: 'Salvoconducto' }
]

const tipoAtencionOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' }, 
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

const prioridadOptions = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Prioritario', label: 'Prioritario' }
]

const validationErrors = computed(() => {
  const fields = [
    { value: formData.entryDate, name: 'Fecha de ingreso' },
    { value: formData.requestingPhysician, name: 'Médico solicitante' },
    { value: formData.service, name: 'Servicio' },
    { value: formData.casePriority, name: 'Prioridad del caso' },
    { value: formData.numberOfSamples, name: 'Número de muestras' },
    { value: formData.patientEntity, name: 'Entidad del paciente' },
    { value: formData.patientCareType, name: 'Tipo de atención' }
  ]
  const list: string[] = []
  fields.forEach((f: any) => { 
    if (!f.value) list.push(f.name) 
  })
  const samples = formData.samples as any
  if (samples) {
    samples.forEach((sample: any, i: number) => {
      if (!(sample as any).bodyRegion) list.push(`Submuestra ${i + 1}: Región del cuerpo`)
      if (!(sample as any).tests?.length) list.push(`Submuestra ${i + 1}: Al menos una prueba`)
      const tests = (sample as any).tests
      if (tests && Array.isArray(tests)) {
        tests.forEach((test: any, j: number) => {
          if (!test.code) list.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Código de prueba`)
          if (!test.quantity || test.quantity < 1) list.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Cantidad`)
        })
      }
    })
  }
  errors.samples?.forEach((e: string) => list.push(`Submuestras: ${e}`))
  return list
})

const getMedicoErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.requestingPhysician.length > 0) return errors.requestingPhysician
  if (!formData.requestingPhysician?.trim()) return ['El médico solicitante es obligatorio']
  return []
})

const getServicioErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.service.length > 0) return errors.service
  if (!formData.service?.trim()) return ['El servicio es obligatorio']
  return []
})

const getRegionErrors = (sampleIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const sample = (formData.samples as any)[sampleIndex]
  if (!sample || !(sample as any).bodyRegion?.trim()) return ['La región del cuerpo es obligatoria']
  return [] as string[]
}

const getPruebaErrors = (sampleIndex: number, testIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const sample = (formData.samples as any)[sampleIndex]
  if (!sample) return ['Debe seleccionar una prueba']
  const test = (sample as any).tests[testIndex]
  if (!test || !String(test.code || '').trim()) return ['El código de la prueba es obligatorio']
  if (test.quantity == null || Number(test.quantity) < 1) return ['La cantidad debe ser al menos 1']
  return [] as string[]
}

const searchPatient = async () => {
  // Validate both fields are present
  if (!searchIdentificationType.value) {
    searchError.value = 'Seleccione el tipo de identificación'
    return
  }
  if (!String(searchIdentificationNumber.value || '').trim()) {
    searchError.value = 'Ingrese el número de identificación'
    return
  }

  try {
    isSearching.value = true
    searchError.value = ''
    // Fetch by text and then filter exact match (as in EditPatient.vue)
    const results = await patientsApiService.searchPatients(String(searchIdentificationNumber.value), 10)
    const match = (results || []).find((p: any) => {
      return Number(p.identification_type) === Number(searchIdentificationType.value) &&
             String(p.identification_number) === String(searchIdentificationNumber.value)
    })

    if (match) {
      // Build full name from available fields (first/second names and lastnames)
      const fullName = [match.first_name, match.second_name, match.first_lastname, match.second_lastname]
        .filter((v) => !!v && String(v).trim() !== '')
        .join(' ')
        .trim()

      // Calculate age from birth_date if age is not provided
      let calculatedAge = match.age ?? ''
      if (!calculatedAge && match.birth_date) {
        const birthDate = new Date(match.birth_date)
        const today = new Date()
        let age = today.getFullYear() - birthDate.getFullYear()
        const monthDiff = today.getMonth() - birthDate.getMonth()
        if (monthDiff < 0 || (monthDiff === 0 && today.getDate() < birthDate.getDate())) {
          age--
        }
        calculatedAge = age
      }

      // Normalize gender and care type to cases module expectations
      const genderForm: '' | 'masculino' | 'femenino' = match.gender === 'Masculino' ? 'masculino' : match.gender === 'Femenino' ? 'femenino' : ''
      const careForm: '' | 'ambulatorio' | 'hospitalizado' = match.care_type === 'Ambulatorio' ? 'ambulatorio' : match.care_type === 'Hospitalizado' ? 'hospitalizado' : ''

      const transformed: PatientData = {
        patientCode: match.patient_code || `${match.identification_type}-${match.identification_number}`,
        identification_type: match.identification_type,
        identification_number: match.identification_number,
        name: fullName || '',
        gender: genderForm,
        age: String(calculatedAge),
        birth_date: match.birth_date,
        entity: match.entity_info?.name || 'Sin entidad',
        entityCode: match.entity_info?.id,
        careType: careForm,
        observations: match.observations || '',
        location: {
          municipality_code: (match as any).municipality_code || (match as any).location?.municipality_code || '',
          municipality_name: (match as any).municipality_name || (match as any).location?.municipality_name || '',
          subregion: (match as any).subregion || (match as any).location?.subregion || '',
          address: (match as any).address || (match as any).location?.address || ''
        },
        municipality_code: (match as any).municipality_code || (match as any).location?.municipality_code || '',
        municipality_name: (match as any).municipality_name || (match as any).location?.municipality_name || '',
        subregion: (match as any).subregion || (match as any).location?.subregion || '',
        address: (match as any).address || (match as any).location?.address || ''
      } as any

      useNewPatient(transformed)
      updateFormDataWithPatient(transformed)
      emit('patient-verified', transformed)
    } else {
      searchError.value = 'No se encontró un paciente con la identificación especificada'
    }
  } catch (error: any) {
    searchError.value = error?.message || 'Error al buscar el paciente. Verifique los datos e intente nuevamente.'
  } finally {
    isSearching.value = false
  }
}

const updateFormDataWithPatient = (patientData: any) => {
  const careType = String((patientData as any).careType || '').toLowerCase()
  Object.assign(formData, {
    patientDocument: (patientData as any).patientCode || '',
    patientEntity: (patientData as any).entityCode || '',
    patientCareType: careType.includes('ambulator') || careType === 'ambulatorio' ? 'Ambulatorio' : careType.includes('hospital') || careType === 'hospitalizado' ? 'Hospitalizado' : ''
  })
}

const clearPatientFormData = () => { 
  Object.assign(formData, { 
    patientDocument: '', 
    patientEntity: '', 
    patientCareType: '', 
    casePriority: 'Normal', 
    service: '' 
  }) 
}

const clearPatientVerification = () => { 
  clearVerification()
  searchIdentificationType.value = ''
  searchIdentificationNumber.value = ''
  clearPatientFormData()
}

const goToCreatePatient = () => {
  // Navegar a la ruta de crear paciente, enviando los datos buscados como query para posible prellenado
  const idType = normalizeIdType(searchIdentificationType.value)
  const idNumber = String(searchIdentificationNumber.value || '')
  router.push({
    name: 'patients-new',
    query: {
      identification_type: idType ? String(idType) : '',
      identification_number: idNumber
    }
  })
}

const scrollToNotification = async () => { 
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const scrollToPatientVerified = async () => {
  await nextTick()
  if (patientVerifiedSection.value) {
    patientVerifiedSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
  }
}

watch(() => notification.visible, (v) => { 
  if (v) scrollToNotification() 
})

watch(() => patientVerified.value, (v) => {
  if (v) scrollToPatientVerified()
})

watch(() => showCaseSuccessCard.value, (v) => { 
  if (v) scrollToNotification() 
})

// Prefill and auto-search when arriving with query params from PatientSuccessCard
onMounted(async () => {
  const q: any = route.query || {}
  const rawType = q.idType ?? q.identification_type
  const rawNumber = q.idNumber ?? q.identification_number
  const normalizedType = normalizeIdType(rawType)

  if (normalizedType && rawNumber) {
    searchIdentificationType.value = normalizedType
    searchIdentificationNumber.value = String(rawNumber)
    await searchPatient()
    return
  }

  // Respaldo: si solo tenemos el número, intenta búsqueda directa por documento
  if (rawNumber) {
    try {
      const result = await searchPatientByDocumento(String(rawNumber))
      if (result.found && result.patient) {
        useNewPatient(result.patient as any)
        updateFormDataWithPatient(result.patient as any)
        emit('patient-verified', result.patient as any)
      }
    } catch (e) {
      // Ignorar errores aquí; se mostrarán mediante searchError si corresponde
    }
  }
})

const clearForm = () => { 
  clearCaseForm()
  clearPatientVerification()
}

const closeCaseSuccessCard = () => {
  showCaseSuccessCard.value = false
  createdCase.value = null
}

const handleSaveClick = async () => {
  const isValid = validateForm()
  if (!isValid) { 
    validationState.showValidationError = true
    return 
  }
  
  if (!patientVerified.value || !verifiedPatient.value) { 
    showNotification('error', 'Paciente Requerido', 'Debe buscar y verificar un paciente antes de crear el caso.', 5000)
    return 
  }
  
  validationState.showValidationError = false
  showCaseSuccessCard.value = false
  createdCase.value = null
  clearState()
  
  try {
    const result = await createCase(formData as any, verifiedPatient.value)
    
    if (result.success && result.case) {
      createdCase.value = result.case as any
      closeNotification()
      showCaseSuccessCard.value = true
      emit('case-saved', result.case)
      clearForm()
    } else {
      throw new Error(result.message || 'Error desconocido al crear el caso')
    }
  } catch (error: any) {
    console.error('❌ [ERROR] Error al crear caso:', error)
    showNotification('error', 'Error al Guardar Caso', apiError.value || error.message || 'No se pudo guardar el caso. Por favor, inténtelo nuevamente.', 0)
  }
}

const onTestSelected = (sampleIndex: number, testIndex: number, test: any) => {
  if (!test) return
  const sample = (formData.samples as any)?.[sampleIndex]
  if (!sample) return
  const t = (sample as any).tests?.[testIndex]
  if (!t) return
  t.code = test.pruebaCode || test.code || ''
  t.name = test.pruebasName || test.nombre || test.label || ''
}

</script>
