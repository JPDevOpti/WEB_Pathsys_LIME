<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Formulario de Facturación</h4>
    </div>

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre completo" 
      placeholder="Ejemplo: Ana María González" 
      v-model="localModel.billingName"
      :error="formErrors.billingName"
      autocomplete="name" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código del usuario de facturación" 
      placeholder="Ejemplo: 1234567890" 
      v-model="localModel.billingCode"
      :error="formErrors.billingCode"
      @blur="validateCode"
      autocomplete="off"
      maxlength="20"
    />

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Email" 
      type="email" 
      placeholder="ana.gonzalez@facturacion.com" 
      v-model="localModel.billingEmail"
      :error="formErrors.billingEmail"
      @blur="validateEmail"
      autocomplete="email" 
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

    <FormTextarea 
      class="col-span-full" 
      label="Observaciones" 
      placeholder="Notas adicionales sobre el usuario de facturación (opcional)" 
      v-model="localModel.observations" 
      :rows="3"
      :error="formErrors.observations"
    />

    <div class="col-span-full md:col-span-6 flex items-center pt-3">
      <FormCheckbox label="Activo" v-model="localModel.isActive" />
    </div>

    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton type="button" @click="onClear" :disabled="isLoading" />
      <SaveButton 
        text="Guardar Facturacion" 
        type="submit" 
        :disabled="!canSubmit || isLoading"
        :loading="isLoading"
      />
    </div>

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
        <template v-if="notification.type === 'success' && createdFacturacion" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdFacturacion.billing_name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdFacturacion.billing_code }}</span>
                </p>
              </div>
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Email:</span>
                  <p class="text-gray-800 font-semibold">{{ createdFacturacion.billing_email }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdFacturacion.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdFacturacion.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdFacturacion.created_at) }}</p>
                </div>
              </div>
              <div v-if="createdFacturacion.observations">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdFacturacion.observations }}</p>
              </div>
            </div>
          </div>
        </template>
      </Notification>
    </div>

    <ValidationAlert
      :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
      :errors="validationErrors"
    />
  </form>
</template>

<script setup lang="ts">
// Billing user creation form: validates inputs, submits to API, and shows inline notifications
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useBillingCreation } from '../../composables/useBillingCreation'
import type { BillingFormModel, BillingCreateResponse } from '../../types/billing.types'

const modelValue = defineModel<BillingFormModel>({ required: true })
const emit = defineEmits<{ (e: 'usuario-creado', payload: BillingFormModel): void }>()

const notificationContainer = ref<HTMLElement | null>(null)
const createdFacturacion = ref<BillingCreateResponse | null>(null)
const isLoading = ref(false)

const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

const validationState = reactive({
  showValidationError: false,
  hasAttemptedSubmit: false
})

const {
  state,
  emailValidationError,
  validateForm,
  checkEmailAvailability,
  createFacturacion,
  clearState,
  clearMessages
} = useBillingCreation()

// Local copy of model for two-way binding
// Normalize incoming model from parent to ensure all fields are defined (avoid undefined warnings)
const normalizeIncoming = (mv: Partial<BillingFormModel> | any): BillingFormModel => ({
  billingName: (mv.billingName ?? mv.facturacionName ?? '').toString(),
  billingCode: (mv.billingCode ?? mv.facturacionCode ?? '').toString(),
  billingEmail: (mv.billingEmail ?? mv.FacturacionEmail ?? '').toString(),
  password: (mv.password ?? '').toString(),
  observations: (mv.observations ?? mv.observaciones ?? '').toString(),
  isActive: mv.isActive !== undefined ? !!mv.isActive : true
})

const localModel = reactive<BillingFormModel>(normalizeIncoming(modelValue.value))
;(localModel as any).passwordConfirm = ''

// Field-level error messages
const formErrors = reactive({
  billingName: '',
  billingCode: '',
  billingEmail: '',
  password: '',
  passwordConfirm: '',
  observations: ''
})

// Banner errors: include base validation + password specific ones
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const validation = validateForm(localModel)
  const base = validation.isValid ? [] : Object.values(validation.errors)
  const extra: string[] = []
  if ((formErrors as any).password) extra.push((formErrors as any).password)
  if ((formErrors as any).passwordConfirm) extra.push((formErrors as any).passwordConfirm)
  return [...base, ...extra]
})

const canSubmit = computed(() => true)

watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, normalizeIncoming(newValue))
}, { deep: true, immediate: true })

watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

const validateCode = async () => {
  formErrors.billingCode = ''
  if (!localModel.billingCode?.trim()) {
    formErrors.billingCode = 'El código es requerido'
    return
  }
  if (localModel.billingCode.length < 3) {
    formErrors.billingCode = 'Mínimo 3 caracteres'
    return
  }
  if (localModel.billingCode.length > 20) {
    formErrors.billingCode = 'Máximo 20 caracteres'
    return
  }
}

const validateEmail = async () => {
  formErrors.billingEmail = ''
  if (!localModel.billingEmail?.trim()) {
    formErrors.billingEmail = 'El email es requerido'
    return
  }
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.billingEmail)) {
    formErrors.billingEmail = 'Formato de email inválido'
    return
  }
  await checkEmailAvailability(localModel.billingEmail)
  if (emailValidationError.value) {
    formErrors.billingEmail = emailValidationError.value
  }
}

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

const clearNotification = () => {
  notification.visible = false
  notification.title = ''
  notification.message = ''
  createdFacturacion.value = null
}

const closeNotification = () => onClear()

const formatDate = (dateString: string | undefined): string => {
  if (!dateString) return 'Fecha no disponible'
  try {
    let date: Date
    if (typeof dateString === 'string') {
      date = dateString.includes('T') ? new Date(dateString) : new Date(dateString + 'T00:00:00.000Z')
    } else {
      date = new Date(dateString)
    }
    if (isNaN(date.getTime())) return 'Fecha no disponible'
    return date.toLocaleDateString('es-ES', {
      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return 'Fecha no disponible'
  }
}

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

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

  const validation = validateForm(localModel)
  if (!validation.isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    const result = await createFacturacion(localModel)
    if (result.success && result.data) {
      await handleFacturacionCreated(result.data)
    } else {
      const errorMessage = state.error || 'Error desconocido al crear el usuario de facturación'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleFacturacionCreationError(error)
  } finally {
    isLoading.value = false
  }
}

const handleFacturacionCreated = async (createdFacturacionData: any) => {
  createdFacturacion.value = createdFacturacionData
  showNotification('success', '¡Usuario de Facturación Registrado Exitosamente!', '')
  emit('usuario-creado', { ...localModel })
  await scrollToNotification()
}

const handleFacturacionCreationError = async (error: any) => {
  let errorMessage = 'No se pudo guardar el usuario de facturación. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Usuario de Facturación'
  
  if (error.message) {
    errorMessage = error.message
    if (error.message.includes('email') || error.message.includes('código')) {
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
      case 409: errorTitle = 'Datos Duplicados'; errorMessage = 'Ya existe un usuario de facturación con los datos proporcionados'; break
      case 422: errorTitle = 'Datos Inválidos'; errorMessage = 'Los datos proporcionados no son válidos'; break
      case 400: errorTitle = 'Datos Incorrectos'; errorMessage = 'Datos incorrectos o incompletos'; break
      case 500: errorTitle = 'Error del Servidor'; errorMessage = 'Error interno del servidor. Inténtelo más tarde'; break
      default: errorTitle = `Error del Servidor (${error.response.status})`; errorMessage = 'Ha ocurrido un error inesperado'
    }
  }
  
  showNotification('error', errorTitle, errorMessage)
  await scrollToNotification()
}

const clearForm = () => {
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
  clearFormErrors()
  clearState()
  Object.assign(localModel, { 
    billingName: '', billingCode: '', billingEmail: '', password: '', observations: '', isActive: true
  })
  ;(localModel as any).passwordConfirm = ''
}

const onClear = () => {
  clearForm()
  clearNotification()
}

watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})
</script>
