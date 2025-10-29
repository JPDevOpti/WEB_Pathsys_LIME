<template>
  <!-- Edit patient: search by ID, edit fields, confirm update -->
  <div class="space-y-6">
      <!-- Search block -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <SearchPatientIcon class="w-4 h-4 mr-2 text-gray-500" />
          Buscar paciente
        </h3>

        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="sm:w-64">
            <FormSelect 
              v-model="searchIdentificationType" 
              placeholder="Tipo de identificación" 
              :options="identificationTypeOptions" 
              :disabled="isSearching"
            />
          </div>
          <div class="flex-1">
            <FormInputField 
              v-model="searchIdentificationNumber" 
              placeholder="Número de identificación" 
              :max-length="12" 
              :only-numbers="true" 
              :disabled="isSearching" 
              @keydown.enter.prevent="searchPatient" 
            />
          </div>
          <div class="flex gap-2 sm:gap-3">
            <SearchButton 
              text="Buscar" 
              loading-text="Buscando..." 
              :loading="isSearching" 
              @click="searchPatient" 
              size="md" 
            />
            <ClearButton v-if="patientFound" text="Limpiar" @click="onReset" />
          </div>
        </div>
        <!-- Search error -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-sm text-red-600">{{ searchError }}</p>
          </div>
        </div>
        <!-- Found banner -->
        <div v-if="patientFound" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Paciente encontrado y cargado</h4>
          </div>
        </div>

        <!-- Delete button below banner -->
        <div v-if="patientFound" class="mt-2 flex justify-end">
          <BaseButton
            size="xs"
            variant="ghost"
            :custom-class="'border border-red-600 text-red-600 bg-white hover:bg-red-50 focus:ring-red-500'"
            @click="openDeleteConfirm"
          >
            <template #icon-left>
              <TrashIcon class="w-4 h-4 mr-1" />
            </template>
            Eliminar paciente
          </BaseButton>
        </div>
      </div>

      <!-- Helper when nothing loaded -->
      <div v-if="!patientFound && !notification.visible" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center space-y-3">
          <SearchPatientIcon class="w-12 h-12 text-blue-400" />
          <h3 class="text-lg font-medium text-blue-800">Busque un paciente para editar</h3>
          <p class="text-blue-600 text-sm">Ingrese el código del paciente para comenzar a editar</p>
        </div>
      </div>

      <!-- Edit form -->
      <div v-if="patientFound" class="space-y-6">
        <!-- Identification Section -->
        <div class="bg-gray-50 p-6 rounded-lg">
          <h3 class="text-lg font-medium text-gray-900 mb-4">Información de Identificación</h3>
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
            <FormSelect 
              v-model="form.identification_type" 
              label="Tipo de Identificación" 
              placeholder="Seleccione el tipo" 
              :required="true" 
              :options="identificationTypeOptions" 
              :error="getIdentificationTypeError"
            />
            <FormInputField 
              v-model="form.identification_number" 
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
              v-model="form.first_name" 
              label="Primer Nombre" 
              placeholder="Ejemplo: Juan" 
              :required="true" 
              :max-length="50" 
              :only-letters="true" 
              :errors="getFirstNameErrors"
              @input="handleNameInput"
            />
            <FormInputField 
              v-model="form.second_name" 
              label="Segundo Nombre" 
              placeholder="Ejemplo: Carlos" 
              :max-length="50" 
              :only-letters="true" 
              :errors="getSecondNameErrors"
            />
            <FormInputField 
              v-model="form.first_lastname" 
              label="Primer Apellido" 
              placeholder="Ejemplo: Pérez" 
              :required="true" 
              :max-length="50" 
              :only-letters="true" 
              :errors="getFirstLastnameErrors"
              @input="handleNameInput"
            />
            <FormInputField 
              v-model="form.second_lastname" 
              label="Segundo Apellido" 
              placeholder="Ejemplo: García" 
              :max-length="50" 
              :only-letters="true" 
              :errors="getSecondLastnameErrors"
            />
          </div>
          
          <div class="grid grid-cols-1 md:grid-cols-2 gap-6 mt-6">
            <DateInputField 
              v-model="form.birth_date" 
              label="Fecha de Nacimiento" 
              :required="true" 
              :max="maxBirthDate" 
              :errors="getBirthDateErrors"
              @update:model-value="handleBirthDateInput"
            />
            <FormSelect 
              v-model="form.gender" 
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
              v-model="form.entity_id"
              label="Entidad de Salud"
              placeholder="Buscar y seleccionar entidad..."
              :required="true"
              :errors="getEntityIdErrors"
              @entity-selected="handleEntitySelected"
            />
            <FormSelect 
              v-model="form.care_type" 
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
              v-model="form.municipality_code" 
              :selectedName="form.municipality_name"
              label="Municipio" 
              placeholder="Buscar y seleccionar municipio..." 
              :errors="getMunicipalityCodeErrors"
              @municipality-code-change="handleMunicipalityCodeChange"
              @municipality-name-change="handleMunicipalityNameChange"
              @subregion-change="handleSubregionChange"
            />
            <FormInputField 
              v-model="form.address" 
              label="Dirección" 
              placeholder="Ejemplo: Calle 123 #45-67" 
              :max-length="200" 
              :errors="getAddressErrors"
            />
          </div>
        </div>
        
        <!-- Notes -->
        <FormTextarea 
          v-model="form.observations" 
          label="Observaciones del paciente" 
          placeholder="Observaciones adicionales del paciente" 
          :rows="3" 
          :max-length="500" 
        />

        <!-- Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton text="Guardar Cambios" @click="onSubmit" :disabled="isLoading" :loading="isLoading" />
        </div>

        <!-- Global validation -->
        <ValidationAlert :visible="validationState.showValidationError && validationErrors.length > 0" :errors="validationErrors" />
  </div>

  <!-- Success Card -->
  <div ref="notificationContainer">
    <PatientSuccessCard 
      :visible="showSuccessCard" 
      :patientData="updatedPatient || {}"
      @close="closeSuccessCard"
    />
  </div>

  <!-- Delete Success Card -->
  <div ref="notificationContainer">
    <PatientDeleteSuccessCard
      :visible="showDeleteSuccessCard"
      :patientData="patientDeleted || {}"
      @close="closeDeleteSuccessCard"
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

  <!-- Confirm deletion dialog -->
  <ConfirmDialog
    :model-value="showConfirmDelete"
    title="Eliminar paciente"
    subtitle="Esta acción no se puede deshacer"
    :message="`¿Está seguro de eliminar al paciente ${originalData?.first_name || ''} ${originalData?.first_lastname || ''}?\nDocumento: ${IDENTIFICATION_TYPE_NAMES[originalData?.identification_type as IdentificationType] || originalData?.identification_type} - ${originalData?.identification_number || ''}`"
    confirm-text="Eliminar"
    cancel-text="Cancelar"
    :loading-confirm="isDeleting"
    :icon="TrashIcon"
    @update:modelValue="v => showConfirmDelete = v as boolean"
    @confirm="confirmDelete"
    @cancel="showConfirmDelete = false"
  />
    </div>
</template>

<script setup lang="ts">
import { reactive, ref, computed, watch } from 'vue'
import { FormInputField, FormSelect, FormTextarea, DateInputField } from '@/shared/components/ui/forms'
import { MunicipalityList, EntityList } from '@/shared/components/ui/lists'
import { SaveButton, ClearButton, SearchButton, BaseButton } from '@/shared/components/ui/buttons'
import { useNotifications } from '../composables/useNotifications'
import patientsApiService from '../services/patientsApi.service'
import { Notification, PatientSuccessCard, ValidationAlert, ConfirmDialog } from '@/shared/components/ui/feedback'
import PatientDeleteSuccessCard from '@/shared/components/ui/feedback/PatientDeleteSuccessCard.vue'
import SearchPatientIcon from '@/assets/icons/SearchPatientIcon.vue'
import { TrashIcon } from '@/assets/icons'
import { IdentificationType, IDENTIFICATION_TYPE_NAMES } from '../types'
import type { PatientData, UpdatePatientRequest, Gender, CareType } from '../types'

interface Props { 
  caseCodeProp?: string 
}

interface Emits { 
  (e: 'patient-updated', patient: PatientData): void 
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { notification, showNotification, closeNotification } = useNotifications()

// UI state
const isLoading = ref(false)
const originalData = ref<PatientData | null>(null)
const notificationContainer = ref<HTMLElement | null>(null)
const updatedPatient = ref<PatientData | null>(null)
const patientDeleted = ref<PatientData | null>(null)
const searchIdentificationType = ref<IdentificationType | ''>('')
const searchIdentificationNumber = ref('')
const isSearching = ref(false)
const searchError = ref('')
const patientFound = ref(false)
const showSuccessCard = ref(false)
const showDeleteSuccessCard = ref(false)
const showConfirmDelete = ref(false)
const isDeleting = ref(false)

// Form data
const form = reactive({
  patient_code: '',
  identification_type: '' as IdentificationType | '',
  identification_number: '',
  first_name: '',
  second_name: '',
  first_lastname: '',
  second_lastname: '',
  birth_date: '',
  gender: '' as Gender | '',
  municipality_code: '',
  municipality_name: '',
  subregion: '',
  address: '',
  entity_id: '',
  entity_name: '',
  care_type: '' as CareType | '',
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
  if (!form.identification_type) {
    errors.identification_type.push('El tipo de identificación es obligatorio')
    isValid = false
  }

  // Validate identification number
  if (!form.identification_number.trim()) {
    errors.identification_number.push('El número de identificación es obligatorio')
    isValid = false
  } else if (form.identification_number.length < 6) {
    errors.identification_number.push('El número de identificación debe tener al menos 6 caracteres')
    isValid = false
  }

  // Validate first name
  if (!form.first_name.trim()) {
    errors.first_name.push('El primer nombre es obligatorio')
    isValid = false
  }

  // Validate first lastname
  if (!form.first_lastname.trim()) {
    errors.first_lastname.push('El primer apellido es obligatorio')
    isValid = false
  }

  // Validate birth date
  if (!form.birth_date) {
    errors.birth_date.push('La fecha de nacimiento es obligatoria')
    isValid = false
  } else {
    const birthDate = new Date(form.birth_date)
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
  if (!form.gender) {
    errors.gender.push('El género es obligatorio')
    isValid = false
  }

  // Municipality, subregion and address are now optional fields
  // Only validate length if address is provided
  if (form.address.trim() && form.address.trim().length < 5) {
    errors.address.push('La dirección debe tener al menos 5 caracteres')
    isValid = false
  }

  if (!form.entity_id.trim()) {
    errors.entity_id.push('El ID de entidad es obligatorio')
    isValid = false
  }

  if (!form.entity_name.trim()) {
    errors.entity_name.push('El nombre de entidad es obligatorio')
    isValid = false
  }

  if (!form.care_type) {
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
  
  Object.entries(errors).forEach(([field, fieldErrors]) => {
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

const getMunicipalityNameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.municipality_name
)

const getSubregionErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.subregion
)

const getAddressErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.address
)

const getEntityIdErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.entity_id
)

const getEntityNameErrors = computed(() => 
  !validationState.hasAttemptedSubmit ? [] : errors.entity_name
)

const getCareTypeError = computed(() => 
  !validationState.hasAttemptedSubmit ? '' : 
  (errors.care_type.length > 0 ? errors.care_type[0] : '')
)

// Input handlers
const handleNameInput = (value: string) => {
  // Clear validation errors when user starts typing
  if (validationState.hasAttemptedSubmit) {
    errors.first_name = []
    errors.second_name = []
    errors.first_lastname = []
    errors.second_lastname = []
  }
}

const handleBirthDateInput = (value: string) => {
  // Clear validation errors when user starts typing
  if (validationState.hasAttemptedSubmit) {
    errors.birth_date = []
  }
}

// Nuevo: limpiar errores al escribir identificación
const handleIdentificationInput = (_value: string) => {
  if (validationState.hasAttemptedSubmit) {
    errors.identification_number = []
  }
}

// Nuevo: limpiar errores al cambiar tipo de identificación
watch(() => form.identification_type, () => {
  if (validationState.hasAttemptedSubmit) {
    errors.identification_type = []
  }
})

// Form validation state
const isFormValid = computed(() => {
  return form.first_name.trim() !== '' && 
         form.first_lastname.trim() !== '' && 
         form.gender !== '' && 
         form.birth_date !== '' && 
         form.entity_id && 
         form.care_type !== ''
})

// Load patient data from API
const loadPatientData = (patient: PatientData) => {
  Object.assign(form, {
    patient_code: patient.patient_code,
    identification_type: patient.identification_type,
    identification_number: patient.identification_number,
    first_name: patient.first_name,
    second_name: patient.second_name || '',
    first_lastname: patient.first_lastname,
    second_lastname: patient.second_lastname || '',
    birth_date: patient.birth_date,
    gender: patient.gender,
    municipality_code: patient.location?.municipality_code || '',
    municipality_name: patient.location?.municipality_name || '',
    subregion: patient.location?.subregion || '',
    address: patient.location?.address || '',
    entity_id: patient.entity_info.id,
    entity_name: patient.entity_info.name,
    care_type: patient.care_type,
    observations: patient.observations || ''
  })
  originalData.value = { ...patient }
}

// Municipality handlers
const handleMunicipalityCodeChange = (code: string) => {
  form.municipality_code = code
}

const handleMunicipalityNameChange = (name: string) => {
  form.municipality_name = name
}

const handleSubregionChange = (subregion: string) => {
  form.subregion = subregion
}

// Handle entity selection
const handleEntitySelected = (entity: any) => {
  if (entity) {
    form.entity_id = entity.codigo || entity.id || ''
    form.entity_name = entity.nombre || entity.name || ''
  } else {
    form.entity_id = ''
    form.entity_name = ''
  }
}

// Reset form
const resetFormData = () => {
  Object.assign(form, {
    patient_code: '',
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
  searchIdentificationType.value = ''
  searchIdentificationNumber.value = ''
  searchError.value = ''
  patientFound.value = false
  originalData.value = null
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
}

// Search patient
const searchPatient = async () => {
  // Validar que ambos campos estén llenos
  if (!searchIdentificationType.value) {
    searchError.value = 'Seleccione el tipo de identificación'
    return
  }

  if (!searchIdentificationNumber.value.trim()) {
    searchError.value = 'Ingrese el número de identificación'
    return
  }

  isSearching.value = true
  searchError.value = ''
  patientFound.value = false

  try {
    // Buscar por identificación usando searchPatients
    const searchResults = await patientsApiService.searchPatients(searchIdentificationNumber.value, 10)
    
    console.log('Search results:', searchResults)
    console.log('Search identification type:', searchIdentificationType.value, typeof searchIdentificationType.value)
    console.log('Search identification number:', searchIdentificationNumber.value, typeof searchIdentificationNumber.value)
    
    // Filtrar por tipo de identificación exacto
    const matchingPatient = searchResults.find(p => {
      console.log('Comparing patient:', p.identification_type, typeof p.identification_type, 'vs', searchIdentificationType.value, typeof searchIdentificationType.value)
      console.log('Number comparison:', p.identification_number, typeof p.identification_number, 'vs', searchIdentificationNumber.value, typeof searchIdentificationNumber.value)
      return p.identification_type === Number(searchIdentificationType.value) && 
             p.identification_number === searchIdentificationNumber.value
    })
    
    if (matchingPatient) {
      loadPatientData(matchingPatient)
      patientFound.value = true
    } else {
      const identificationTypeName = IDENTIFICATION_TYPE_NAMES[searchIdentificationType.value] || searchIdentificationType.value
      searchError.value = `No se encontró un paciente con identificación ${identificationTypeName} ${searchIdentificationNumber.value}`
      patientFound.value = false
    }
  } catch (error: any) {
    if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') {
      searchError.value = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    } else if (error.message?.includes('404') || error.message?.includes('No encontrado')) {
      const identificationTypeName = IDENTIFICATION_TYPE_NAMES[searchIdentificationType.value] || searchIdentificationType.value
      searchError.value = `No se encontró un paciente con identificación ${identificationTypeName} ${searchIdentificationNumber.value}`
    } else {
      searchError.value = error.message || 'Error al buscar el paciente. Verifique los datos e intente nuevamente.'
    }
      patientFound.value = false
    } finally {
      isSearching.value = false
    }
}

// Submit form
const onSubmit = async () => {
  validationState.hasAttemptedSubmit = true
  
  if (!validateForm()) {
    validationState.showValidationError = true
    return
  }

  validationState.showValidationError = false
  isLoading.value = true

  try {
    // Preparar objeto location solo si al menos un campo tiene contenido válido
    const hasLocation = form.municipality_code?.trim() || 
                        form.municipality_name?.trim() || 
                        form.subregion?.trim() || 
                        form.address?.trim()
    
    const updateData: UpdatePatientRequest = {
      first_name: form.first_name.trim(),
      second_name: form.second_name.trim() || undefined,
      first_lastname: form.first_lastname.trim(),
      second_lastname: form.second_lastname.trim() || undefined,
      birth_date: form.birth_date,
      gender: form.gender as Gender,
      location: hasLocation ? {
        municipality_code: form.municipality_code?.trim() || '',
        municipality_name: form.municipality_name?.trim() || '',
        subregion: form.subregion?.trim() || '',
        address: form.address?.trim() || ''
      } : undefined,
      // Enviar entidad sólo si ambos campos están completos
      entity_info: (
        form.entity_id?.trim() &&
        form.entity_name?.trim()
      ) ? {
        id: form.entity_id.trim(),
        name: form.entity_name.trim()
      } : undefined,
      care_type: form.care_type as CareType,
      observations: form.observations.trim() || undefined
    }

    // Limpiar claves undefined para evitar validaciones innecesarias
    Object.keys(updateData).forEach((k) => {
      if ((updateData as any)[k] === undefined) delete (updateData as any)[k]
    })

    // Paso 1: si cambió la identificación, validar duplicados y actualizar identificación primero
    if (originalData.value && (
      form.identification_type !== originalData.value.identification_type ||
      form.identification_number !== originalData.value.identification_number
    )) {
      // Validar que no exista otro paciente con la misma identificación
      const exists = await patientsApiService.checkPatientExists(
        form.identification_type as IdentificationType,
        form.identification_number.trim()
      )
      if (exists) {
        throw new Error('Ya existe un paciente con el tipo y número de identificación proporcionados')
      }

      // Ejecutar cambio de identificación y sincronizar el nuevo código del paciente
      const changedPatient = await patientsApiService.changeIdentification(
        form.patient_code,
        form.identification_type as IdentificationType,
        form.identification_number.trim()
      )
      // El backend puede cambiar el patient_code cuando cambia la identificación
      form.patient_code = changedPatient.patient_code
      originalData.value = { ...changedPatient }
    }

    // Paso 2: actualizar el resto de datos
    const result = await patientsApiService.updatePatient(form.patient_code, updateData)
    
    updatedPatient.value = result
    // Actualizar originalData para reflejar nuevos datos (incluye identificación ya cambiada)
    originalData.value = { ...result }

    showSuccessCard.value = true
    emit('patient-updated', result)
    
    try {
      window.dispatchEvent(new CustomEvent('patient-updated'))
    } catch {}

    showNotification('success', 'Paciente actualizado', 'Los datos del paciente se han actualizado correctamente', 4000)

    // Limpiar todos los campos y estado como si se presionara "Limpiar",
    // pero conservando la notificación de éxito visible
    const previousSuccessCard = showSuccessCard.value
    const previousNotification = { ...notification }
    onReset()
    // Restaurar notificación y tarjeta de éxito
    showSuccessCard.value = previousSuccessCard
    Object.assign(notification, previousNotification)
    
  } catch (error: any) {
    let errorMessage = 'No se pudo actualizar el paciente. Por favor, inténtelo nuevamente.'

    // Mensajes específicos para identificación duplicada o cambio fallido
    if (error.message?.includes('Ya existe un paciente')) {
      errorMessage = error.message
      errors.identification_number = [error.message]
    } else if (error.message?.includes('Error al cambiar la identificación')) {
      errorMessage = error.message
    } else if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') {
      errorMessage = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    } else if (error.response?.data?.detail) {
      errorMessage = Array.isArray(error.response.data.detail) 
        ? error.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ')
        : String(error.response.data.detail)
    } else if (error.message) {
      errorMessage = error.message
    }
    
    showNotification('error', 'Error al actualizar', errorMessage, 0)
  } finally {
    isLoading.value = false
  }
}

// Reset
const onReset = () => {
  resetFormData()
  closeNotification()
}

// Close success card
const closeSuccessCard = () => {
  showSuccessCard.value = false
}

// Delete patient flow
const openDeleteConfirm = () => {
  showConfirmDelete.value = true
}

const confirmDelete = async () => {
  if (!form.patient_code) {
    showConfirmDelete.value = false
    return
  }
  isDeleting.value = true
  try {
    // Preserve data for success card before reset
    patientDeleted.value = originalData.value ? { ...originalData.value } : null
    await patientsApiService.deletePatient(form.patient_code)
    showConfirmDelete.value = false
    showNotification('success', 'Paciente eliminado', 'El paciente ha sido eliminado correctamente', 4000)
    // Reset UI state as if clearing
    const prevNotification = { ...notification }
    onReset()
    Object.assign(notification, prevNotification)
    showDeleteSuccessCard.value = true
  } catch (error: any) {
    const msg = error.response?.data?.detail || error.message || 'Error al eliminar el paciente'
    showNotification('error', 'Error al eliminar', msg, 0)
    showConfirmDelete.value = false
  } finally {
    isDeleting.value = false
  }
}

const closeDeleteSuccessCard = () => {
  showDeleteSuccessCard.value = false
}

// Watch for case code prop changes
watch(
  () => props.caseCodeProp,
  async (newCode) => {
    if (newCode) {
      try {
        isSearching.value = true
        searchError.value = ''
        patientFound.value = false

        const patient = await patientsApiService.getPatientByCode(newCode)
        loadPatientData(patient)
        patientFound.value = true
      } catch (error: any) {
        const msg = error?.message || `No se pudo cargar el paciente con código ${newCode}`
        showNotification('error', 'Error al cargar paciente', msg, 0)
        patientFound.value = false
      } finally {
        isSearching.value = false
      }
    }
  },
  { immediate: true }
)

// Scroll to notification when visible
watch(
  () => showSuccessCard.value,
  (newValue) => {
    if (newValue && notificationContainer.value) {
      notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
    }
  }
)

</script>