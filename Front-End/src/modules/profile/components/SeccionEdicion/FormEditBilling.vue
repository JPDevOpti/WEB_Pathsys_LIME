<template>
  <div v-if="localModel.billingCode" class="space-y-6">
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Editar Usuario de Facturación</h4>
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
      disabled
      autocomplete="off"
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
      label="Nueva contraseña (opcional)" 
      type="password" 
      placeholder="••••••••" 
      v-model="passwordValue"
      :error="formErrors.password"
      autocomplete="new-password" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Confirmar contraseña" 
      type="password" 
      placeholder="••••••••" 
      :model-value="localModel.passwordConfirm || ''"
      @update:model-value="val => (localModel.passwordConfirm = val)"
      :error="formErrors.passwordConfirm"
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
        text="Actualizar Usuario de Facturación" 
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
        <template v-if="notification.type === 'success' && updatedFacturacion" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedFacturacion.billingName }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span>
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedFacturacion.billingCode }}</span>
                </p>
              </div>
              <div class="space-y-3 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Email:</span>
                  <p class="text-gray-800 font-semibold">{{ updatedFacturacion.billingEmail }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full" :class="updatedFacturacion.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ updatedFacturacion.isActive ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de actualización:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(updatedFacturacion.fecha_actualizacion) }}</p>
                </div>
              </div>
              <div v-if="updatedFacturacion.observations">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedFacturacion.observations }}</p>
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
  </div>
  <div v-else class="text-center py-8">
    <p class="text-gray-500">No se pudieron cargar los datos de facturación para edición.</p>
  </div>
</template>

<script setup lang="ts">
// Edit billing user form: validates edits, updates via API, and shows inline notifications
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { useBillingEdition } from '../../composables/useBillingEdition'
import type { BillingEditFormModel } from '../../types/billing.types'

const modelValue = defineModel<BillingEditFormModel>({ required: false })
const props = defineProps<{ usuario?: any; facturacion?: any; selectedUser?: any }>()
const emit = defineEmits<{ (e: 'usuario-actualizado', payload: BillingEditFormModel): void }>()

const notificationContainer = ref<HTMLElement | null>(null)
const updatedFacturacion = ref<any | null>(null)
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
  update,
  setInitialData,
  clearMessages
} = useBillingEdition()

// Normalize incoming model (maps snake_case from API to camelCase expected here)
const normalizeIncoming = (mv: Partial<BillingEditFormModel> | any): BillingEditFormModel => ({
  id: (mv.id ?? '').toString(),
  billingName: (mv.billingName ?? mv.billing_name ?? mv.facturacionName ?? mv.nombre ?? '').toString(),
  billingCode: (mv.billingCode ?? mv.billing_code ?? mv.facturacionCode ?? mv.codigo ?? '').toString(),
  billingEmail: (mv.billingEmail ?? mv.billing_email ?? mv.FacturacionEmail ?? mv.email ?? '').toString(),
  observations: (mv.observations ?? mv.observaciones ?? '').toString(),
  isActive: mv.isActive !== undefined ? !!mv.isActive : (mv.is_active !== undefined ? !!mv.is_active : true),
  password: '',
  passwordConfirm: ''
})

const localModel = reactive<BillingEditFormModel>(normalizeIncoming(modelValue.value))

const formErrors = reactive({
  billingName: '',
  billingCode: '',
  billingEmail: '',
  password: '',
  passwordConfirm: '',
  observations: ''
})

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const validation = validateForm(localModel)
  if (!validation.isValid) return Object.values(validation.errors)
  return []
})

const canSubmit = computed(() => !isLoading.value)

const passwordValue = computed({
  get: () => localModel.password || '',
  set: (value: string) => {
    localModel.password = value
  }
})

watch(() => modelValue?.value, (newValue) => {
  if (!newValue) { console.debug('[FormEditBilling] modelValue empty'); return }
  console.debug('[FormEditBilling] modelValue received:', newValue)
  const normalized = normalizeIncoming(newValue)
  Object.assign(localModel, normalized)
  setInitialData(normalized)
}, { deep: true })

// Allow loading from prop `usuario` (like auxiliary edit)
const normalizeFromUsuario = (u: any): BillingEditFormModel => ({
  id: (u?.id ?? '').toString(),
  billingName: (u?.billingName ?? u?.billing_name ?? u?.nombre ?? u?.name ?? '').toString(),
  billingCode: (u?.billingCode ?? u?.billing_code ?? u?.codigo ?? u?.code ?? '').toString(),
  billingEmail: (u?.billingEmail ?? u?.billing_email ?? u?.email ?? '').toString(),
  observations: (u?.observations ?? u?.observaciones ?? '').toString(),
  isActive: u?.isActive !== undefined ? !!u.isActive : (u?.is_active !== undefined ? !!u.is_active : true),
  password: '',
  passwordConfirm: ''
})

const pickIncoming = (p: any) => p?.usuario ?? p?.facturacion ?? p?.selectedUser ?? null

watch(() => pickIncoming(props), (u) => {
  if (!u) { console.debug('[FormEditBilling] incoming user empty'); return }
  console.debug('[FormEditBilling] incoming user received:', u)
  const normalized = normalizeFromUsuario(u)
  Object.assign(localModel, normalized)
  setInitialData(normalized)
}, { immediate: true, deep: true })

watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

// Reusable email regex and helpers
const EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
const isEmailValid = (email: string) => EMAIL_REGEX.test(email)

// Field-level email validation with server-side availability errors surfaced from composable
const validateEmail = async () => {
  formErrors.billingEmail = ''
  if (!localModel.billingEmail?.trim()) {
    formErrors.billingEmail = 'El email es requerido'
    return
  }
  if (!isEmailValid(localModel.billingEmail)) {
    formErrors.billingEmail = 'Formato de email inválido'
    return
  }
  if (emailValidationError.value) {
    formErrors.billingEmail = emailValidationError.value
  }
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

const clearNotification = () => {
  notification.visible = false
  notification.title = ''
  notification.message = ''
}

const closeNotification = () => onClear()

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// Submit handler: validates optional password rules, runs schema validation, updates and shows result
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  const pwd = (localModel.password || '').trim()
  const pwdConfirm = (localModel.passwordConfirm || '').trim()
  if (pwd.length > 0) {
    if (pwd.length < 6) {
      formErrors.password = 'La contraseña debe tener al menos 6 caracteres'
      validationState.showValidationError = true
      return
    }
    if (pwd !== pwdConfirm) {
      formErrors.passwordConfirm = 'Las contraseñas no coinciden'
      validationState.showValidationError = true
      return
    }
  }
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    const result = await update(localModel)
    if (result.success && result.data) {
      await handleFacturacionUpdated(result.data)
    } else {
      const errorMessage = state.error || 'Error desconocido al actualizar el usuario de facturación'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleFacturacionUpdateError(error)
  } finally {
    isLoading.value = false
  }
}

const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
    return date.toLocaleDateString('es-ES', {
      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch {
    return 'Fecha no disponible'
  }
}

const handleFacturacionUpdated = async (data: any) => {
  updatedFacturacion.value = {
    billingName: data.billing_name,
    billingCode: data.billing_code,
    billingEmail: data.billing_email,
    observations: data.observations,
    isActive: data.is_active,
    fecha_actualizacion: data.updated_at
  }
  
  showNotification('success', '¡Usuario de Facturación Actualizado Exitosamente!', '')
  emit('usuario-actualizado', { ...localModel })
  // Clear sensitive password fields after successful update
  localModel.password = ''
  localModel.passwordConfirm = ''
  await scrollToNotification()
}

const handleFacturacionUpdateError = async (error: any) => {
  console.error('Error al actualizar usuario de facturación:', error)
  
  let errorMessage = 'No se pudo actualizar el usuario de facturación. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Actualizar Usuario de Facturación'
  
  if (error.message) {
    errorMessage = error.message
    if (error.message.includes('email')) {
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
      case 409: errorTitle = 'Datos Duplicados'; errorMessage = 'Ya existe un usuario de facturación con estos datos'; break
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
  clearMessages()
  const originalData = modelValue.value
  Object.assign(localModel, originalData)
  localModel.password = ''
  localModel.passwordConfirm = ''
}

const onClear = () => {
  clearForm()
  clearNotification()
}

watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})
</script>
