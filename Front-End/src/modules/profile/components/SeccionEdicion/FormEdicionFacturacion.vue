<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Editar Usuario de Facturación</h4>
    </div>

    <!-- Nombre y Código -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre completo" 
      placeholder="Ejemplo: Ana María González" 
      v-model="localModel.facturacionName"
      :error="formErrors.facturacionName"
      autocomplete="name" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código del usuario de facturación" 
      placeholder="Ejemplo: 1234567890" 
      v-model="localModel.facturacionCode"
      :error="formErrors.facturacionCode"
      disabled
      autocomplete="off"
    />

    <!-- Email -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Email" 
      type="email" 
      placeholder="ana.gonzalez@facturacion.com" 
      v-model="localModel.FacturacionEmail"
      :error="formErrors.FacturacionEmail"
      @blur="validateEmail"
      autocomplete="email" 
    />

    <!-- Contraseña y Confirmación -->
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

    <!-- Observaciones -->
    <FormTextarea 
      class="col-span-full" 
      label="Observaciones" 
      placeholder="Notas adicionales sobre el usuario de facturación (opcional)" 
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
        text="Actualizar Usuario de Facturación" 
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
      />
    </div>

    <!-- Alerta de Validación -->
    <ValidationAlert
      :visible="validationState.showValidationError && validationState.hasAttemptedSubmit"
      :errors="validationErrors"
    />
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useFacturacionEdition } from '../../composables/useFacturacionEdition'
import type { FacturacionEditFormModel } from '../../types/facturacion.types'

// Props y emits
const modelValue = defineModel<FacturacionEditFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-actualizado', payload: FacturacionEditFormModel): void 
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado de notificación
const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

// Estado de validación
const validationState = reactive({
  showValidationError: false,
  hasAttemptedSubmit: false
})

// Composable para manejo de backend
const {
  state,
  emailValidationError,
  validateForm,
  update,
  setInitialData,
  clearMessages
} = useFacturacionEdition()

// Estado de loading local
const isLoading = ref(false)

// Modelo local del formulario
const localModel = reactive<FacturacionEditFormModel>({ 
  ...modelValue.value,
  password: '',
  passwordConfirm: ''
})

// Errores del formulario
const formErrors = reactive({
  facturacionName: '',
  facturacionCode: '',
  FacturacionEmail: '',
  password: '',
  passwordConfirm: '',
  observaciones: ''
})

// Lista de errores de validación para mostrar en la alerta
const validationErrors = computed(() => {
  // Solo mostrar errores si se ha intentado enviar el formulario
  if (!validationState.hasAttemptedSubmit) {
    return []
  }
  
  // ✅ Usar la validación del composable para obtener errores estándar
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    return Object.values(validation.errors)
  }
  
  return []
})

// Computed para verificar si se puede enviar
const canSubmit = computed(() => {
  // Siempre habilitado (sin restricción de cambios)
  return !isLoading.value
})

// Computed para manejar el campo de contraseña
const passwordValue = computed({
  get: () => localModel.password || '',
  set: (value: string) => {
    localModel.password = value
  }
})

// Watchers
watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, newValue)
  setInitialData(newValue)
}, { deep: true })

// Watcher para detectar cambios en el modelo solo cuando el usuario está escribiendo
watch(() => localModel, () => {
  // Solo reaccionar a cambios si el usuario ya intentó enviar Y hay una notificación activa
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

// Validación del email al perder el foco
const validateEmail = async () => {
  formErrors.FacturacionEmail = ''
  
  if (!localModel.FacturacionEmail?.trim()) {
    formErrors.FacturacionEmail = 'El email es requerido'
    return
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.FacturacionEmail)) {
    formErrors.FacturacionEmail = 'Formato de email inválido'
    return
  }
  
  // Verificar disponibilidad en el backend (si cambió el email)
  if (emailValidationError.value) {
    formErrors.FacturacionEmail = emailValidationError.value
  }
}

// Limpiar errores del formulario
const clearFormErrors = () => {
  Object.keys(formErrors).forEach(key => {
    formErrors[key as keyof typeof formErrors] = ''
  })
}

// Funciones de notificación
const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

// Función para limpiar solo la notificación
const clearNotification = () => {
  notification.visible = false
  notification.title = ''
  notification.message = ''
}

const closeNotification = () => {
  // Usar exactamente la misma función que el botón Limpiar
  onClear()
}

// Hacer scroll a la notificación
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Envío del formulario
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  // Validar contraseñas
  if (localModel.password && localModel.password.trim().length > 0) {
    if (localModel.password.trim().length < 6) {
      formErrors.password = 'La contraseña debe tener al menos 6 caracteres'
      validationState.showValidationError = true
      return
    }
    if (localModel.password !== localModel.passwordConfirm) {
      formErrors.passwordConfirm = 'Las contraseñas no coinciden'
      validationState.showValidationError = true
      return
    }
  }
  
  // Validación local primero
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    // ✅ SOLO usar la validación estándar, no mostrar errores en campos individuales
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    // Enviar al backend
    const result = await update(localModel)
    
    if (result.success) {
      await handleFacturacionUpdated()
    } else {
      // ✅ El composable ya maneja los errores y los coloca en state.error
      // Solo necesitamos mostrar el error que ya está en el estado
      const errorMessage = state.error || 'Error desconocido al actualizar el usuario de facturación'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleFacturacionUpdateError(error)
  } finally {
    isLoading.value = false
  }
}

// Manejar la actualización exitosa del usuario de facturación
const handleFacturacionUpdated = async () => {
  // Mostrar notificación de éxito
  showNotification(
    'success',
    '¡Usuario de Facturación Actualizado Exitosamente!',
    'Los cambios se han guardado correctamente.'
  )
  
  // Emitir evento para compatibilidad
  emit('usuario-actualizado', { ...localModel })
  
  // Hacer scroll a la notificación
  await scrollToNotification()
}

// Manejar errores durante la actualización
const handleFacturacionUpdateError = async (error: any) => {
  console.error('Error al actualizar usuario de facturación:', error)
  
  let errorMessage = 'No se pudo actualizar el usuario de facturación. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Actualizar Usuario de Facturación'
  
  // Determinar el tipo de error y mostrar mensaje específico
  if (error.message) {
    errorMessage = error.message
    
    // Personalizar el título según el tipo de error
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
      case 409:
        errorTitle = 'Datos Duplicados'
        errorMessage = 'Ya existe un usuario de facturación con estos datos'
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

// Función para limpiar solo el formulario (para uso interno)
const clearForm = () => {
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
  clearFormErrors()
  clearMessages()
  
  // Resetear a los datos originales
  const originalData = modelValue.value
  Object.assign(localModel, originalData)
  localModel.password = ''
  localModel.passwordConfirm = ''
}

// Limpiar formulario (función pública para el botón Limpiar)
const onClear = () => {
  clearForm()
  clearNotification()
}

// Watcher para hacer scroll cuando aparece la notificación
watch(
  () => notification.visible,
  (newValue) => {
    if (newValue) {
      scrollToNotification()
    }
  }
)
</script>
