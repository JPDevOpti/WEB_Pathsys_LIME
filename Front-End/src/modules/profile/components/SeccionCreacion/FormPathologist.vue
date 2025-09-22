<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Formulario de Patólogo</h4>
    </div>

    <!-- Nombre e Iniciales -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre completo" 
      placeholder="Ejemplo: Juan Carlos Pérez González" 
      v-model="localModel.patologoName"
      :error="formErrors.patologoName"
      autocomplete="name" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Iniciales" 
      placeholder="Ejemplo: JCPG" 
      v-model="localModel.InicialesPatologo"
      :error="formErrors.InicialesPatologo"
      autocomplete="off" 
    />

    <!-- Código y Email -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código del patólogo" 
      placeholder="Ejemplo: 123456" 
      v-model="localModel.patologoCode"
      :error="formErrors.patologoCode"
      @blur="validateCode"
      autocomplete="off"
      maxlength="10"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Email" 
      type="email" 
      placeholder="juan.perez@udea.edu.co" 
      v-model="localModel.PatologoEmail"
      :error="formErrors.PatologoEmail"
      @blur="validateEmail"
      autocomplete="email" 
    />

    <!-- Registro médico y Contraseña -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Registro médico" 
      placeholder="Ejemplo: RM-12345" 
      v-model="localModel.registro_medico"
      :error="formErrors.registro_medico"
      @blur="validateMedicalLicense"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Contraseña" 
      type="password" 
      placeholder="••••••••" 
      v-model="localModel.password"
      :error="formErrors.password"
      autocomplete="new-password" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Confirmar contraseña" 
      type="password" 
      placeholder="••••••••" 
      :model-value="(localModel as any).passwordConfirm || ''"
      @update:model-value="val => ((localModel as any).passwordConfirm = val)"
      :error="(formErrors as any).passwordConfirm"
      autocomplete="new-password" 
    />

    <!-- Observaciones -->
    <FormTextarea 
      class="col-span-full md:col-span-12 w-full" 
      label="Observaciones" 
      placeholder="Notas adicionales sobre el patólogo (opcional)" 
      v-model="localModel.observaciones" 
      :rows="3"
      :error="formErrors.observaciones"
    />

    <!-- Estado activo -->
    <div class="col-span-full md:col-span-6 flex items-center pt-3">
      <FormCheckbox label="Activo" v-model="localModel.isActive" />
    </div>

    <!-- Botones de acción -->
    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton type="button" @click="onClear" :disabled="isLoading" />
      <SaveButton 
        text="Guardar Patólogo" 
        type="submit" 
        :disabled="!canSubmit || isLoading"
        :loading="isLoading"
      />
    </div>

    <!-- Notificación -->
    <div ref="notificationContainer" class="col-span-full">
      <Notification
        :visible="notification.visible"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :inline="true"
        :auto-close="false"
        @close="closeNotification"
      >
        <template v-if="notification.type === 'success' && createdPathologist" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <!-- Información principal del patólogo -->
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPathologist.pathologist_name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPathologist.pathologist_code }}</span>
                </p>
              </div>
              
              <!-- Detalles del patólogo en vertical -->
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Iniciales:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.initials }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Email:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.pathologist_email }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Registro médico:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.medical_license }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdPathologist.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdPathologist.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdPathologist.created_at) }}</p>
                </div>
              </div>
              
              <!-- Observaciones -->
              <div v-if="createdPathologist.observations">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdPathologist.observations }}</p>
              </div>
            </div>
          </div>
        </template>
      </Notification>
    </div>

    <!-- Alerta de Validación -->
    <ValidationAlert
      :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
      :errors="validationErrors"
    />
  </form>
</template>

<script setup lang="ts">
// Pathologist creation form: validates inputs, submits to API, and shows inline notifications
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { usePathologistCreation } from '../../composables/usePathologistCreation'
import type { PathologistFormModel, PathologistCreateResponse } from '../../types/pathologist.types'

// Props and emits
const modelValue = defineModel<PathologistFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-creado', payload: PathologistFormModel): void 
}>()

// Refs
const notificationContainer = ref<HTMLElement | null>(null)

// Created pathologist state
const createdPathologist = ref<PathologistCreateResponse | null>(null)

// Inline notification state
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

// Backend composable for validations and API calls
const {
  state,
  codeValidationError,
  emailValidationError,
  licenseValidationError,
  validateForm,
  checkCodeAvailability,
  checkEmailAvailability,
  checkMedicalLicenseAvailability,
  createPathologist,
  clearState,
  clearMessages
} = usePathologistCreation()

// Local loading state
const isLoading = ref(false)

// Local form model
const localModel = reactive<PathologistFormModel>({ 
  ...modelValue.value
})
;(localModel as any).passwordConfirm = ''

// Field-level errors
const formErrors = reactive({
  patologoName: '',
  InicialesPatologo: '',
  patologoCode: '',
  PatologoEmail: '',
  registro_medico: '',
  password: '',
  passwordConfirm: '',
  observaciones: ''
})

// Aggregated banner errors from composable validation
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) {
    return []
  }
  const validation = validateForm(localModel)
  const base = validation.isValid ? [] : Object.values(validation.errors)
  const extra: string[] = []
  if ((formErrors as any).password) extra.push((formErrors as any).password)
  if ((formErrors as any).passwordConfirm) extra.push((formErrors as any).passwordConfirm)
  return [...base, ...extra]
})

// Submit availability (kept always enabled by product decision)
const canSubmit = computed(() => {
  return true
})

// Sync incoming v-model into local model
watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, newValue)
}, { deep: true })

// When user edits after a failed submit, clear previous messages/errors
watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

// Validation: code on blur
const validateCode = async () => {
  formErrors.patologoCode = ''
  
  if (!localModel.patologoCode?.trim()) {
    formErrors.patologoCode = 'El código es requerido'
    return
  }
  
  if (localModel.patologoCode.length > 10) {
    formErrors.patologoCode = 'Máximo 10 caracteres'
    return
  }
  
  // Backend availability check
  await checkCodeAvailability(localModel.patologoCode)
  if (codeValidationError.value) {
    formErrors.patologoCode = codeValidationError.value
  }
}

// Reusable email regex and helpers
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const isEmailValid = (email: string) => EMAIL_REGEX.test(email)

// Validation: email on blur
const validateEmail = async () => {
  formErrors.PatologoEmail = ''
  
  if (!localModel.PatologoEmail?.trim()) {
    formErrors.PatologoEmail = 'El email es requerido'
    return
  }
  
  if (!isEmailValid(localModel.PatologoEmail)) {
    formErrors.PatologoEmail = 'Formato de email inválido'
    return
  }
  
  // Backend availability check
  await checkEmailAvailability(localModel.PatologoEmail)
  if (emailValidationError.value) {
    formErrors.PatologoEmail = emailValidationError.value
  }
}

// Validation: medical license on blur
const validateMedicalLicense = async () => {
  formErrors.registro_medico = ''
  
  if (!localModel.registro_medico?.trim()) {
    formErrors.registro_medico = 'El registro médico es requerido'
    return
  }
  
  if (localModel.registro_medico.length > 50) {
    formErrors.registro_medico = 'Máximo 50 caracteres'
    return
  }
  
  // Backend availability check
  await checkMedicalLicenseAvailability(localModel.registro_medico)
  if (licenseValidationError.value) {
    formErrors.registro_medico = licenseValidationError.value
  }
}

// Clear all field errors
const clearFormErrors = () => {
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
}

// Inline notification helpers
const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

// Clear only notification content
const clearNotification = () => {
  notification.visible = false
  notification.title = ''
  notification.message = ''
  createdPathologist.value = null
}

const closeNotification = () => {
  // Reuse same behavior as the Clear button
  onClear()
}

// Format a date string into a friendly Spanish representation
const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'Fecha no disponible'
  
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
      return 'Fecha no disponible'
    }
    
    return date.toLocaleDateString('es-ES', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    })
  } catch {
    return 'Fecha no disponible'
  }
}

// Scroll helper to bring notification into view
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Submit handler: runs validation, calls API, and routes success/error to inline notification
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  // Local password confirmation validation
  const pwd = (localModel.password || '').trim()
  const pwdConfirm = (((localModel as any).passwordConfirm as string) || '').trim()
  if (!pwd) {
    formErrors.password = 'La contraseña es requerida'
  } else if (pwd.length < 6) {
    formErrors.password = 'La contraseña debe tener al menos 6 caracteres'
  }
  if (pwdConfirm && pwd !== pwdConfirm) {
    ;(formErrors as any).passwordConfirm = 'Las contraseñas no coinciden'
  } else if (!pwdConfirm) {
    ;(formErrors as any).passwordConfirm = 'La confirmación de contraseña es requerida'
  }
  if (formErrors.password || (formErrors as any).passwordConfirm) {
    validationState.showValidationError = true
    return
  }
  
  // Schema-level validation first
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    // Create via backend
    const result = await createPathologist(localModel)
    
    if (result.success && result.data) {
      await handlePathologistCreated(result.data)
    } else {
      const errorMessage = state.error || 'Error desconocido al crear el patólogo'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handlePathologistCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Handle success response
const handlePathologistCreated = async (createdPathologistData: any) => {
  createdPathologist.value = createdPathologistData
  showNotification(
    'success',
    '¡Patólogo Registrado Exitosamente!',
    ''
  )
  emit('usuario-creado', { ...localModel })
  ;(localModel as any).passwordConfirm = ''
  await scrollToNotification()
}

// Handle API errors
const handlePathologistCreationError = async (error: any) => {
  console.error('Error al guardar patólogo:', error)
  
  let errorMessage = 'No se pudo guardar el patólogo. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Patólogo'
  
  if (error.message) {
    errorMessage = error.message
    if (error.message.includes('email') || error.message.includes('código') || error.message.includes('registro')) {
      errorTitle = 'Datos Duplicados'
    } else if (error.message.includes('válido') || error.message.includes('requerido')) {
      errorTitle = 'Datos Inválidos'
    } else if (error.message.includes('servidor')) {
      errorTitle = 'Error del Servidor'
    }
  } else if (error.response?.data?.detail) {
    errorMessage = error.response.data.detail
  } else if (error.response?.status) {
    switch (error.response.status) {
      case 409:
        errorTitle = 'Datos Duplicados'
        errorMessage = 'Ya existe un patólogo con los datos proporcionados'
        break
      case 422:
        errorTitle = 'Datos Inválidos'
        errorMessage = 'Los datos proporcionados no son válidos'
        break
      case 400:
        errorTitle = 'Datos Incorrectos'
        errorMessage = 'Datos incorrectos o incompletos'
        break
      case 500:
        errorTitle = 'Error del Servidor'
        errorMessage = 'Error interno del servidor. Inténtelo más tarde'
        break
      default:
        errorTitle = `Error del Servidor (${error.response.status})`
        errorMessage = 'Ha ocurrido un error inesperado'
    }
  }
  
  showNotification(
    'error',
    errorTitle,
    errorMessage
  )
  
  await scrollToNotification()
}

// Reset only the form (internal use)
const clearForm = () => {
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
  clearFormErrors()
  clearState()
  
  Object.assign(localModel, { 
    patologoName: '', 
    InicialesPatologo: '', 
    patologoCode: '', 
    PatologoEmail: '', 
    registro_medico: '', 
    password: '', 
    observaciones: '', 
    isActive: true,
    firma: ''
  })
  ;(localModel as any).passwordConfirm = ''
}

// Public Clear action (button)
const onClear = () => {
  clearForm()
  clearNotification()
}

// Auto-scroll when notification becomes visible
watch(
  () => notification.visible,
  (newValue) => {
    if (newValue) {
      scrollToNotification()
    }
  }
)
</script>


