<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Formulario de Auxiliar</h4>
    </div>

    <!-- Nombre y Código -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre completo" 
      placeholder="Ejemplo: Ana María González" 
      v-model="localModel.auxiliarName"
      :error="formErrors.auxiliarName"
      autocomplete="name" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código del auxiliar" 
      placeholder="Ejemplo: 1234567890" 
      v-model="localModel.auxiliarCode"
      :error="formErrors.auxiliarCode"
      @blur="validateCode"
      autocomplete="off"
      maxlength="20"
    />

    <!-- Email y Contraseña -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Email" 
      type="email" 
      placeholder="ana.gonzalez@udea.edu.co" 
      v-model="localModel.AuxiliarEmail"
      :error="formErrors.AuxiliarEmail"
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

    <!-- Observaciones -->
    <FormTextarea 
      class="col-span-full" 
      label="Observaciones" 
      placeholder="Notas adicionales sobre el auxiliar (opcional)" 
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
        text="Guardar Auxiliar" 
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
        <template v-if="notification.type === 'success' && createdAuxiliary" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <!-- Información principal del auxiliar -->
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdAuxiliary.auxiliar_name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdAuxiliary.auxiliar_code }}</span>
                </p>
              </div>
              
              <!-- Detalles del auxiliar en vertical -->
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Email:</span>
                  <p class="text-gray-800 font-semibold">{{ createdAuxiliary.auxiliar_email }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdAuxiliary.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdAuxiliary.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdAuxiliary.fecha_creacion) }}</p>
                </div>
              </div>
              
              <!-- Observaciones -->
              <div v-if="createdAuxiliary.observaciones">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdAuxiliary.observaciones }}</p>
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
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useAuxiliaryCreation } from '../../composables/useAuxiliaryCreation'
import type { AuxiliaryFormModel, AuxiliaryCreateResponse } from '../../types/auxiliary.types'

// Props y emits
const modelValue = defineModel<AuxiliaryFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-creado', payload: AuxiliaryFormModel): void 
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado del auxiliar creado
const createdAuxiliary = ref<AuxiliaryCreateResponse | null>(null)

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
  codeValidationError,
  emailValidationError,
  canSubmit: canSubmitFromComposable,
  validateForm,
  checkCodeAvailability,
  checkEmailAvailability,
  createAuxiliary,
  clearState,
  clearMessages
} = useAuxiliaryCreation()

// Estado de loading local
const isLoading = ref(false)

// Modelo local del formulario
const localModel = reactive<AuxiliaryFormModel>({ 
  ...modelValue.value
})

// Errores del formulario
const formErrors = reactive({
  auxiliarName: '',
  auxiliarCode: '',
  AuxiliarEmail: '',
  password: '',
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
  // ✅ SIEMPRE HABILITADO: El botón de guardar nunca se bloquea
  return true
})

// Watchers
watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, newValue)
}, { deep: true })

// Watcher para detectar cambios en el modelo solo cuando el usuario está escribiendo
watch(() => localModel, () => {
  // Solo reaccionar a cambios si el usuario ya intentó enviar Y hay una notificación activa
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

// Validación del código al perder el foco
const validateCode = async () => {
  formErrors.auxiliarCode = ''
  
  if (!localModel.auxiliarCode?.trim()) {
    formErrors.auxiliarCode = 'El código es requerido'
    return
  }
  
  if (localModel.auxiliarCode.length < 3) {
    formErrors.auxiliarCode = 'Mínimo 3 caracteres'
    return
  }
  
  if (localModel.auxiliarCode.length > 20) {
    formErrors.auxiliarCode = 'Máximo 20 caracteres'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkCodeAvailability(localModel.auxiliarCode)
  if (codeValidationError.value) {
    formErrors.auxiliarCode = codeValidationError.value
  }
}

// Validación del email al perder el foco
const validateEmail = async () => {
  formErrors.AuxiliarEmail = ''
  
  if (!localModel.AuxiliarEmail?.trim()) {
    formErrors.AuxiliarEmail = 'El email es requerido'
    return
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.AuxiliarEmail)) {
    formErrors.AuxiliarEmail = 'Formato de email inválido'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkEmailAvailability(localModel.AuxiliarEmail)
  if (emailValidationError.value) {
    formErrors.AuxiliarEmail = emailValidationError.value
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
  createdAuxiliary.value = null
}

const closeNotification = () => {
  // Usar exactamente la misma función que el botón Limpiar
  onClear()
}

// Función para formatear fecha
const formatDate = (dateString: string): string => {
  try {
    const date = new Date(dateString)
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
    const result = await createAuxiliary(localModel)
    
    if (result.success && result.data) {
      await handleAuxiliaryCreated(result.data)
    } else {
      // ✅ El composable ya maneja los errores y los coloca en state.error
      // Solo necesitamos mostrar el error que ya está en el estado
      const errorMessage = state.error || 'Error desconocido al crear el auxiliar'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleAuxiliaryCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Manejar la creación exitosa del auxiliar
const handleAuxiliaryCreated = async (createdAuxiliaryData: any) => {
  // Almacenar información del auxiliar creado
  createdAuxiliary.value = createdAuxiliaryData
  
  // Mostrar notificación de éxito
  showNotification(
    'success',
    '¡Auxiliar Registrado Exitosamente!',
    ''
  )
  
  // Emitir evento para compatibilidad
  emit('usuario-creado', { ...localModel })
  
  // Hacer scroll a la notificación
  await scrollToNotification()
}

// Manejar errores durante la creación
const handleAuxiliaryCreationError = async (error: any) => {
  console.error('Error al guardar auxiliar:', error)
  
  let errorMessage = 'No se pudo guardar el auxiliar. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Auxiliar'
  
  // Determinar el tipo de error y mostrar mensaje específico
  if (error.message) {
    errorMessage = error.message
    
    // Personalizar el título según el tipo de error
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
      case 409:
        errorTitle = 'Datos Duplicados'
        errorMessage = 'Ya existe un auxiliar con los datos proporcionados'
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
  clearState()
  
  Object.assign(localModel, { 
    auxiliarName: '', 
    auxiliarCode: '', 
    AuxiliarEmail: '', 
    password: '', 
    observaciones: '', 
    isActive: true
  })
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


