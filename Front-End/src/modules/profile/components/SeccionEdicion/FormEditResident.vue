<template>
  <div v-if="localModel.residenteCode" class="space-y-6">
    <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
      <!-- Header Section -->
      <div class="col-span-full">
        <h4 class="text-base font-semibold text-gray-800">Edit Resident</h4>
        <p class="text-sm text-gray-500 mt-1">Modify the medical resident's data</p>
      </div>

      <!-- Code and Name Fields -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Resident Code" 
        placeholder="Example: 12345678" 
        v-model="localModel.residenteCode"
        :error="formErrors.residenteCode || codeValidationError"
        :disabled="true"
        autocomplete="off"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Full Name" 
        placeholder="Example: María Elena Rodríguez" 
        v-model="localModel.residenteName"
        :error="formErrors.residenteName"
        autocomplete="name" 
      />

      <!-- Initials and Email Fields -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Resident Initials" 
        placeholder="Example: MER" 
        v-model="localModel.InicialesResidente"
        :error="formErrors.InicialesResidente"
        autocomplete="off"
        maxlength="10"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Email" 
        type="email" 
        placeholder="maria.rodriguez@udea.edu.co" 
        v-model="localModel.ResidenteEmail"
        :error="formErrors.ResidenteEmail || emailValidationError"
        @blur="validateEmail"
        autocomplete="email" 
      />

      <!-- Medical License Field -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Medical License" 
        placeholder="Example: RM-2024-001" 
        v-model="localModel.registro_medico"
        :error="formErrors.registro_medico || licenseValidationError"
        @blur="validateMedicalLicense"
      />

      <!-- Password and Confirmation Fields -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="New Password (optional)" 
        type="password" 
        placeholder="••••••••" 
        :model-value="localModel.password || ''"
        @update:model-value="val => (localModel.password = val)"
        :error="formErrors.password"
        autocomplete="new-password"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Confirm Password" 
        type="password" 
        placeholder="••••••••" 
        :model-value="localModel.passwordConfirm || ''"
        @update:model-value="val => (localModel.passwordConfirm = val)"
        :error="formErrors.passwordConfirm"
        autocomplete="new-password"
      />

      <!-- Observations Field -->
      <FormTextarea 
        class="col-span-full" 
        label="Observations" 
        placeholder="Additional notes about the resident (optional)" 
        v-model="localModel.observaciones" 
        :rows="3"
        :error="formErrors.observaciones"
      />

      <!-- Active Status -->
      <div class="col-span-full md:col-span-6 flex items-center pt-3">
        <FormCheckbox label="Active" v-model="localModel.isActive" />
      </div>

      <!-- Action Buttons -->
      <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
        <ClearButton 
          type="button" 
          @click="onReset" 
          :disabled="isLoading || !hasChanges" 
          variant="secondary" 
          :text="'Reset'" 
          :icon="'reset'"
        >
          <template #icon>
            <RefreshIcon class="w-4 h-4 mr-2" />
          </template>
        </ClearButton>
        <SaveButton 
          text="Update Resident" 
          type="submit" 
          :disabled="!canSubmit || isLoading || !hasChanges" 
          :loading="isLoading" 
        />
      </div>

      <!-- Success Notification -->
      <div v-if="notification.visible" ref="notificationContainer" class="col-span-full">
        <Notification
          :visible="true"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          @close="() => {}"
        >
          <template v-if="notification.type === 'success' && updatedResident" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Resident main info -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedResident.residenteName }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Code:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedResident.residenteCode }}</span>
                  </p>
                </div>
                
                <!-- Resident details -->
                <div class="space-y-4 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Initials:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.InicialesResidente }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Email:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.ResidenteEmail }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Medical License:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedResident.registro_medico }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Status:</span>
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="updatedResident.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ updatedResident.isActive ? 'Active' : 'Inactive' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Update Date:</span>
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedResident.fecha_actualizacion) }}</p>
                  </div>
                </div>
                
                <!-- Observations -->
                <div v-if="updatedResident.observaciones">
                  <span class="text-gray-500 font-medium block mb-2">Observations:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedResident.observaciones }}</p>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <!-- Validation Alert -->
      <ValidationAlert
        :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
        :errors="validationErrors"
      />
    </form>
  </div>
  <div v-else class="text-center py-8">
    <p class="text-gray-500">Could not load resident data for editing.</p>
    <p class="text-sm text-gray-400 mt-2">Missing critical data: ID or resident code.</p>
  </div>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useResidentEdition } from '../../composables/useResidentEdition'
import type { ResidentEditFormModel } from '../../types/resident.types'
import { RefreshIcon } from '@/assets/icons'

// Types
type Usuario = {
  id: string;
  residenteName?: string;
  nombre?: string;
  tipo: string;
  residenteCode?: string;
  codigo?: string;
  documento?: string;
  ResidenteEmail?: string;
  email?: string;
  InicialesResidente?: string;
  registro_medico?: string;
  observaciones?: string;
  activo?: boolean;
  isActive?: boolean;
}

// Props and emits
const props = defineProps<{
  usuario: Usuario;
}>()

const emit = defineEmits<{
  (e: 'usuario-actualizado', data: any): void;
}>()

// Refs
const notificationContainer = ref<HTMLElement | null>(null)
const updatedResident = ref<any>(null)

// Notification state
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// Validation state
const validationState = reactive({
  showValidationError: false,
  hasAttemptedSubmit: false
})

// Composable for backend handling
const {
  isLoading,
  codeValidationError,
  emailValidationError,
  licenseValidationError,
  canSubmit: canSubmitFromComposable,
  validateForm,
  checkEmailAvailability,
  checkLicenseAvailability,
  updateResident,
  setInitialData,
  resetToOriginal,
  clearMessages,
  createHasChanges
} = useResidentEdition()

// Local form model
const localModel = reactive<ResidentEditFormModel>({
  id: '',
  residenteName: '',
  InicialesResidente: '',
  residenteCode: '',
  ResidenteEmail: '',
  registro_medico: '',
  observaciones: '',
  isActive: true,
  password: '',
  passwordConfirm: ''
})

// Form errors
const formErrors = reactive({
  residenteName: '',
  InicialesResidente: '',
  residenteCode: '',
  ResidenteEmail: '',
  registro_medico: '',
  observaciones: '',
  password: '',
  passwordConfirm: ''
})

// Computed properties
const hasChanges = computed(() => createHasChanges(localModel))

const canSubmit = computed(() => {
  const passwordOnlyValid = !!localModel.password && localModel.password.trim().length >= 6
  const baseValid = canSubmitFromComposable.value && 
    localModel.residenteName?.trim().length >= 2 &&
    localModel.InicialesResidente?.trim().length >= 2 &&
    localModel.residenteCode?.trim().length >= 3 &&
    localModel.ResidenteEmail?.trim().length > 0 &&
    localModel.registro_medico?.trim().length >= 3

  return baseValid || passwordOnlyValid
})

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  
  const errors: string[] = []
  
  if (!localModel.residenteName || formErrors.residenteName) {
    errors.push('Valid full name required')
  }
  if (!localModel.InicialesResidente || formErrors.InicialesResidente) {
    errors.push('Valid initials required')
  }
  if (!localModel.residenteCode || formErrors.residenteCode) {
    errors.push('Valid resident code required')
  }
  if (!localModel.ResidenteEmail || formErrors.ResidenteEmail) {
    errors.push('Valid email required')
  }
  if (!localModel.registro_medico || formErrors.registro_medico) {
    errors.push('Valid medical license required')
  }
  if (formErrors.observaciones) {
    errors.push('Valid observations required')
  }
  
  return errors
})

// Helper functions
const normalizeResident = (raw: any): ResidentEditFormModel | null => {
  if (!raw) return null
  
  const name = raw.residenteName || raw.residentName || raw.nombre || raw.name || ''
  const code = raw.residenteCode || raw.residentCode || raw.codigo || raw.code || raw.documento || ''
  const initials = raw.InicialesResidente || raw.inicialesResidente || raw.initials || ''
  const email = raw.ResidenteEmail || raw.residentEmail || raw.email || ''
  const registro = raw.registro_medico || raw.medicalLicense || raw.medical_license || ''
  const obs = raw.observaciones || raw.observations || raw.notes || ''
  const active = raw.isActive !== undefined ? raw.isActive : (raw.is_active !== undefined ? raw.is_active : (raw.activo !== undefined ? raw.activo : true))
  
  return {
    id: raw.id || raw._id || code,
    residenteName: String(name),
    InicialesResidente: String(initials),
    residenteCode: String(code),
    ResidenteEmail: String(email),
    registro_medico: String(registro),
    observaciones: String(obs),
    isActive: !!active,
    password: '',
    passwordConfirm: ''
  }
}

const loadInitialData = () => {
  const mappedData = normalizeResident(props.usuario)
  if (!mappedData) return
  Object.assign(localModel, mappedData)
  setInitialData(mappedData)
}

const clearFormErrors = () => {
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
}

const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'Date not available'
  
  try {
    let date: Date
    
    if (typeof dateString === 'string') {
      if (dateString.includes('T')) {
        date = new Date(dateString)
      } else {
        date = new Date(dateString + 'T00:00:00.000Z')
      }
    } else {
      date = new Date(dateString)
    }
    
    if (isNaN(date.getTime())) {
      return 'Date not available'
    }
    
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Date not available'
  }
}

// Validation functions
const validateEmail = async () => {
  formErrors.ResidenteEmail = ''
  
  if (!localModel.ResidenteEmail?.trim()) {
    formErrors.ResidenteEmail = 'Email is required'
    return
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.ResidenteEmail)) {
    formErrors.ResidenteEmail = 'Invalid email format'
    return
  }
  
  await checkEmailAvailability(localModel.ResidenteEmail)
  if (emailValidationError.value) {
    formErrors.ResidenteEmail = emailValidationError.value
  }
}

const validateMedicalLicense = async () => {
  formErrors.registro_medico = ''
  
  if (!localModel.registro_medico?.trim()) {
    formErrors.registro_medico = 'Medical license is required'
    return
  }
  
  if (localModel.registro_medico.length < 3) {
    formErrors.registro_medico = 'Minimum 3 characters'
    return
  }
  
  if (localModel.registro_medico.length > 50) {
    formErrors.registro_medico = 'Maximum 50 characters'
    return
  }
  
  await checkLicenseAvailability(localModel.registro_medico)
  if (licenseValidationError.value) {
    formErrors.registro_medico = licenseValidationError.value
  }
}

// Form submission
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  
  // Validate passwords
  if (localModel.password && localModel.password.trim().length > 0) {
    if (localModel.password.trim().length < 6) {
      formErrors.password = 'Password must be at least 6 characters'
      validationState.showValidationError = true
      return
    }
    if (localModel.password !== localModel.passwordConfirm) {
      formErrors.passwordConfirm = 'Passwords do not match'
      validationState.showValidationError = true
      return
    }
  }
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    Object.assign(formErrors, validation.errors)
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  
  try {
    const result = await updateResident(localModel)
    if ((result as any).success && (result as any).data) {
      const data = (result as any).data
      console.log('🔍 Backend response data:', data)
      console.log('🔍 Normalized data from composable:', data)
      
      updatedResident.value = data
      showNotification('success', 'Resident Updated Successfully!', '')
      await scrollToNotification()
      emit('usuario-actualizado', { ...data, nombre: data.residenteName, codigo: data.residenteCode, tipo: 'residente' })
    } else {
      showNotification('error', 'Error Updating Resident', 'Could not update the resident')
    }
  } catch (error: any) {
    showNotification('error', 'Error Updating Resident', error.message || 'Unexpected error')
  }
}

const onReset = () => {
  const original = resetToOriginal()
  if (original) {
    Object.assign(localModel, original)
    localModel.password = ''
    localModel.passwordConfirm = ''
    clearFormErrors()
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
  }
}

// Watchers
watch(() => props.usuario, () => {
  if (props.usuario) {
    loadInitialData()
  }
}, { immediate: true, deep: true })

watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })
</script>
