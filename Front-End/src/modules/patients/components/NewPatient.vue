<template>
  <!-- Register a new patient -->
  <ComponentCard 
    title="Registro de Nuevo Paciente" 
    description="Complete el formulario con la información del paciente. Los campos marcados con asterisco (*) son obligatorios."
  >
    <template #icon>
      <NewUserIcon class="w-6 h-6 text-blue-600 mr-2" />
    </template>
    <div class="space-y-6">
      <!-- Identification Section -->
      <div class="bg-gray-50 p-6 rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Información de Identificación</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormSelect 
            v-model="formData.identification_type" 
            label="Tipo de Identificación" 
            placeholder="Seleccione el tipo" 
            :required="true" 
            :options="identificationTypeOptions" 
            :error="getIdentificationTypeError" 
          />
          <FormInputField 
            v-model="formData.identification_number" 
            label="Número de Identificación" 
            placeholder="Ejemplo: 12345678" 
            :required="true" 
            :max-length="12" 
            inputmode="numeric" 
            :only-numbers="true" 
            :errors="getIdentificationNumberErrors" 
            @input="handleIdentificationInput" 
          />
        </div>
      </div>

      <!-- Personal Information Section -->
      <div class="bg-gray-50 p-6 rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Información Personal</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <FormInputField 
            v-model="formData.first_name" 
            label="Primer Nombre" 
            placeholder="Ejemplo: Juan" 
            :required="true" 
            :max-length="50" 
            :only-letters="true" 
            :errors="getFirstNameErrors" 
            @input="handleNameInput" 
          />
          <FormInputField 
            v-model="formData.second_name" 
            label="Segundo Nombre" 
            placeholder="Ejemplo: Carlos" 
            :max-length="50" 
            :only-letters="true" 
            :errors="getSecondNameErrors" 
          />
          <FormInputField 
            v-model="formData.first_lastname" 
            label="Primer Apellido" 
            placeholder="Ejemplo: Pérez" 
            :required="true" 
            :max-length="50" 
            :only-letters="true" 
            :errors="getFirstLastnameErrors" 
            @input="handleNameInput" 
          />
          <FormInputField 
            v-model="formData.second_lastname" 
            label="Segundo Apellido" 
            placeholder="Ejemplo: García" 
            :max-length="50" 
            :only-letters="true" 
            :errors="getSecondLastnameErrors" 
          />
        </div>
        
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
          <DateInputField 
            v-model="formData.birth_date" 
            label="Fecha de Nacimiento" 
            :required="true" 
            :max="maxBirthDate" 
            :errors="getBirthDateErrors" 
            @update:model-value="handleBirthDateInput" 
          />
          <FormSelect 
            v-model="formData.gender" 
            label="Género" 
            placeholder="Seleccione el género" 
            :required="true" 
            :options="genderOptions" 
            :error="getGenderError" 
          />
        </div>
      </div>

      <!-- Entity and Care Type Section -->
      <div class="bg-gray-50 p-6 rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Información de Atención</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <EntityList
            v-model="formData.entity_id"
            label="Entidad de Salud"
            placeholder="Buscar y seleccionar entidad..."
            :required="true"
            :errors="getEntityIdErrors"
            @entity-selected="handleEntitySelected"
          />
          <FormSelect 
            v-model="formData.care_type" 
            label="Tipo de Atención" 
            placeholder="Seleccione el tipo de atención" 
            :required="true" 
            :options="careTypeOptions" 
            :error="getCareTypeError" 
          />
        </div>
      </div>

      <!-- Location Section -->
      <div class="bg-gray-50 p-6 rounded-lg">
        <h3 class="text-lg font-medium text-gray-900 mb-4">Información de Ubicación</h3>
        <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
          <MunicipalityList 
            v-model="formData.municipality_code" 
            label="Municipio" 
            placeholder="Buscar y seleccionar municipio..." 
            :required="false" 
            :errors="getMunicipalityCodeErrors" 
            @municipality-code-change="handleMunicipalityCodeChange"
            @municipality-name-change="handleMunicipalityNameChange"
            @subregion-change="handleSubregionChange"
          />
          <FormInputField 
            v-model="formData.address" 
            label="Dirección" 
            placeholder="Ejemplo: Calle 123 #45-67" 
            :required="false" 
            :max-length="200" 
            :errors="getAddressErrors" 
          />
        </div>
      </div>
      
      <!-- Notes -->
      <FormTextarea 
        v-model="formData.observations" 
        label="Observaciones del paciente" 
        placeholder="Observaciones adicionales del paciente" 
        :rows="3" 
        :max-length="500" 
      />

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton @click="handleClearForm" :disabled="isLoading" />
        <SaveButton text="Guardar Paciente" @click="handleSaveClick" :disabled="isLoading" :loading="isLoading" />
      </div>

      <!-- Success Card -->
      <div ref="notificationContainer">
        <PatientSuccessCard 
          :visible="showSuccessCard" 
          :patientData="createdPatient || {}"
          @close="closeSuccessCard"
        />
      </div>

      <!-- Error notification -->
      <Notification 
        :visible="notification.visible && notification.type === 'error'" 
        :type="notification.type" 
        :title="notification.title" 
        :message="notification.message" 
        :inline="true" 
        :auto-close="false" 
        @close="closeNotification"
      />

      <!-- Global validation -->
      <ValidationAlert :visible="validationState.showValidationError && validationErrors.length > 0" :errors="validationErrors" />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, watch, reactive } from 'vue'
import { useNotifications } from '../composables/useNotifications'
import patientsApiService from '../services/patientsApi.service'
import { IdentificationType } from '../types'
import type { CreatePatientRequest, PatientData, Gender, CareType, PatientFormData } from '../types'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect, FormTextarea, DateInputField } from '@/shared/components/ui/forms'
import { MunicipalityList, EntityList } from '@/shared/components/ui/lists'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { ValidationAlert, Notification, PatientSuccessCard } from '@/shared/components/ui/feedback'
import { NewUserIcon } from '@/assets/icons'

// UI refs/state
const notificationContainer = ref<HTMLElement | null>(null)
const createdPatient = ref<PatientData | null>(null)
const showSuccessCard = ref(false)
const isLoading = ref(false)

// Form data
const formData = reactive<PatientFormData>({
  identification_type: '',
  identification_number: '',
  first_name: '',
  second_name: '',
  first_lastname: '',
  second_lastname: '',
  birth_date: '',
  gender: '',
  municipality_code: '',
  municipality_name: '',
  subregion: '',
  address: '',
  entity_id: '',
  entity_name: '',
  care_type: '',
  observations: ''
})

// Validation state
const validationState = reactive({
  hasAttemptedSubmit: false,
  showValidationError: false
})

// Validation errors
const errors = reactive({
  identification_type: [] as string[],
  identification_number: [] as string[],
  first_name: [] as string[],
  second_name: [] as string[],
  first_lastname: [] as string[],
  second_lastname: [] as string[],
  birth_date: [] as string[],
  gender: [] as string[],
  municipality_code: [] as string[],
  municipality_name: [] as string[],
  subregion: [] as string[],
  address: [] as string[],
  entity_id: [] as string[],
  entity_name: [] as string[],
  care_type: [] as string[]
})

// Composables
const { notification, showNotification, closeNotification } = useNotifications()

// Select options
const identificationTypeOptions = [
  { value: IdentificationType.CEDULA_CIUDADANIA, label: 'Cédula de Ciudadanía' },
  { value: IdentificationType.TARJETA_IDENTIDAD, label: 'Tarjeta de Identidad' },
  { value: IdentificationType.CEDULA_EXTRANJERIA, label: 'Cédula de Extranjería' },
  { value: IdentificationType.PASAPORTE, label: 'Pasaporte' },
  { value: IdentificationType.REGISTRO_CIVIL, label: 'Registro Civil' },
  { value: IdentificationType.DOCUMENTO_EXTRANJERO, label: 'Documento Extranjero' },
  { value: IdentificationType.NIT, label: 'NIT' }
]

const genderOptions = [
  { value: 'Masculino', label: 'Masculino' },
  { value: 'Femenino', label: 'Femenino' }
]

const careTypeOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

// Fecha máxima para el campo de nacimiento (hoy)
const maxBirthDate = computed(() => {
  const today = new Date()
  return today.toISOString().split('T')[0]
})

// Validation functions
const validateForm = (): boolean => {
  clearErrors()
  let isValid = true

  // Validate identification type
  if (!formData.identification_type) {
    errors.identification_type.push('El tipo de identificación es obligatorio')
    isValid = false
  }

  // Validate identification number
  if (!formData.identification_number.trim()) {
    errors.identification_number.push('El número de identificación es obligatorio')
    isValid = false
  } else if (formData.identification_number.length < 6) {
    errors.identification_number.push('El número de identificación debe tener al menos 6 caracteres')
    isValid = false
  }

  // Validate first name
  if (!formData.first_name.trim()) {
    errors.first_name.push('El primer nombre es obligatorio')
    isValid = false
  }

  // Validate first lastname
  if (!formData.first_lastname.trim()) {
    errors.first_lastname.push('El primer apellido es obligatorio')
    isValid = false
  }

  // Validate birth date
  if (!formData.birth_date) {
    errors.birth_date.push('La fecha de nacimiento es obligatoria')
    isValid = false
  } else {
    const birthDate = new Date(formData.birth_date)
    const today = new Date()
    const age = today.getFullYear() - birthDate.getFullYear()
    
    if (birthDate > today) {
      errors.birth_date.push('La fecha de nacimiento no puede ser futura')
      isValid = false
    } else if (age > 120) {
      errors.birth_date.push('La edad no puede ser mayor a 120 años')
      isValid = false
    }
  }

  // Validate gender
  if (!formData.gender) {
    errors.gender.push('El género es obligatorio')
    isValid = false
  }

  // Municipality, subregion and address are now optional fields
  // Only validate length if address is provided
  if (formData.address.trim() && formData.address.trim().length < 5) {
    errors.address.push('La dirección debe tener al menos 5 caracteres')
    isValid = false
  }

  if (!formData.entity_id.trim()) {
    errors.entity_id.push('El ID de entidad es obligatorio')
    isValid = false
  }

  if (!formData.entity_name.trim()) {
    errors.entity_name.push('El nombre de entidad es obligatorio')
    isValid = false
  }

  if (!formData.care_type) {
    errors.care_type.push('El tipo de atención es obligatorio')
    isValid = false
  }

  return isValid
}

const clearErrors = () => {
  Object.keys(errors).forEach(key => {
    (errors as any)[key] = []
  })
}

// Aggregate validation messages for banner
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const list: string[] = []
  
  Object.entries(errors).forEach(([_, fieldErrors]) => {
    if (fieldErrors.length > 0) {
      list.push(fieldErrors[0])
    }
  })

  return Array.from(new Set(list))
})

// Field-level validation helpers
const getIdentificationTypeError = computed(() => 
  !validationState.hasAttemptedSubmit ? '' : 
  (errors.identification_type.length > 0 ? errors.identification_type[0] : '')
)

const getIdentificationNumberErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.identification_number
)

const getFirstNameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.first_name
)

const getSecondNameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.second_name
)

const getFirstLastnameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.first_lastname
)

const getSecondLastnameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.second_lastname
)

const getBirthDateErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.birth_date
)

const getGenderError = computed(() => 
  !validationState.hasAttemptedSubmit ? '' : 
  (errors.gender.length > 0 ? errors.gender[0] : '')
)

const getMunicipalityCodeErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.municipality_code
)

// const getMunicipalityNameErrors = computed(() => 
//   !validationState.hasAttemptedSubmit ? [] : errors.municipality_name
// )

// const getSubregionErrors = computed(() => 
//   !validationState.hasAttemptedSubmit ? [] : errors.subregion
// )

const getAddressErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.address
)

const getEntityIdErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.entity_id
)

// const getEntityNameErrors = computed(() => 
//   !validationState.hasAttemptedSubmit ? [] : errors.entity_name
// )

const getCareTypeError = computed(() => 
  !validationState.hasAttemptedSubmit ? '' : 
  (errors.care_type.length > 0 ? errors.care_type[0] : '')
)

// Input handlers
const handleIdentificationInput = () => {
  if (validationState.hasAttemptedSubmit) {
    errors.identification_number = []
  }
}

const handleNameInput = () => {
  if (validationState.hasAttemptedSubmit) {
    errors.first_name = []
    errors.first_lastname = []
  }
}

const handleBirthDateInput = () => {
  if (validationState.hasAttemptedSubmit) {
    errors.birth_date = []
  }
}

// Municipality handlers
const handleMunicipalityCodeChange = (code: string) => {
  formData.municipality_code = code
}

const handleMunicipalityNameChange = (name: string) => {
  formData.municipality_name = name
}

const handleSubregionChange = (subregion: string) => {
  formData.subregion = subregion
}

// Helper: convertir fechas DD/MM/YYYY a ISO YYYY-MM-DD
const toIsoDate = (value: string): string => {
  const s = (value || '').trim()
  if (s.includes('/')) {
    const parts = s.split('/')
    if (parts.length === 3) {
      const [dd, mm, yyyy] = parts
      if (yyyy && mm && dd) return `${yyyy}-${mm}-${dd}`
    }
  }
  return s
}

// Handle entity selection
const handleEntitySelected = (entity: any) => {
  if (entity) {
    formData.entity_id = entity.codigo || entity.id || ''
    formData.entity_name = entity.nombre || entity.name || ''
  } else {
    formData.entity_id = ''
    formData.entity_name = ''
  }
}

// Clear form
const clearForm = () => {
  Object.assign(formData, {
    identification_type: '',
    identification_number: '',
    first_name: '',
    second_name: '',
    first_lastname: '',
    second_lastname: '',
    birth_date: '',
    gender: '',
    municipality_code: '',
    municipality_name: '',
    subregion: '',
    address: '',
    entity_id: '',
    entity_name: '',
    care_type: '',
    observations: ''
  })
  clearErrors()
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
}

// Reset inputs
const handleClearForm = () => {
  clearForm()
}

// Create patient flow
const handleSaveClick = async () => {
  validationState.hasAttemptedSubmit = true
  const isValid = validateForm()
  
  if (!isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    // Preparar objeto location solo si al menos un campo tiene contenido
    const hasLocation = formData.municipality_code.trim() || 
                        formData.municipality_name.trim() || 
                        formData.subregion.trim() || 
                        formData.address.trim()
    
    const patientData: CreatePatientRequest = {
      identification_type: formData.identification_type as IdentificationType,
      identification_number: formData.identification_number.trim(),
      first_name: formData.first_name.trim(),
      second_name: formData.second_name.trim() || undefined,
      first_lastname: formData.first_lastname.trim(),
      second_lastname: formData.second_lastname.trim() || undefined,
      birth_date: toIsoDate(formData.birth_date),
      gender: formData.gender as Gender,
      location: hasLocation ? {
        municipality_code: formData.municipality_code.trim(),
        municipality_name: formData.municipality_name.trim(),
        subregion: formData.subregion.trim(),
        address: formData.address.trim()
      } : undefined,
      entity_info: {
        id: formData.entity_id.trim(),
        name: formData.entity_name.trim()
      },
      care_type: formData.care_type as CareType,
      observations: formData.observations.trim() || undefined
    }
    
    const result = await patientsApiService.createPatient(patientData)
    
    createdPatient.value = result
    showSuccessCard.value = true
    emit('patient-saved', result)
    
    try {
      window.dispatchEvent(new CustomEvent('patient-created'))
    } catch {}
    
    clearForm()
    
  } catch (error: any) {
    let errorMessage = 'No se pudo guardar el paciente. Por favor, inténtelo nuevamente.'
    
    if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') {
      errorMessage = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    } else if (Array.isArray(error.response?.data?.errors)) {
      // Backend 422: estructura { detail: 'Validation error', errors: [...] }
      const errs = error.response.data.errors
      errorMessage = errs.map((err: any) => {
        const field = Array.isArray(err.loc) ? err.loc.join('.') : ''
        return `${field ? field + ': ' : ''}${err.msg || err.message || String(err)}`
      }).join(', ')
    } else if (error.response?.data?.detail) {
      errorMessage = Array.isArray(error.response.data.detail) 
        ? error.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ')
        : String(error.response.data.detail)
    } else if (error.message?.toLowerCase().includes('duplicad') || 
               error.message?.toLowerCase().includes('ya existe') || 
               error.message?.toLowerCase().includes('repetid')) {
      errorMessage = 'Ya existe un paciente con este documento de identidad. Por favor, verifique el número e intente con otro.'
    } else if (error.response?.data?.message) {
      errorMessage = String(error.response.data.message)
    } else if (error.message) {
      errorMessage = String(error.message)
    } else if (typeof error === 'string') {
      errorMessage = error
    }
    
    showNotification('error', 'Error al Guardar Paciente', errorMessage, 0)
  } finally {
    isLoading.value = false
  }
}

// Close success card and clear patient data
const closeSuccessCard = () => {
  showSuccessCard.value = false
  createdPatient.value = null
}

// Smooth-scroll to notification when visible
watch(() => showSuccessCard.value, (v) => {
  if (v && notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})

// Emit for parent listeners
const emit = defineEmits<{ 'patient-saved': [patient: PatientData] }>()
</script>
