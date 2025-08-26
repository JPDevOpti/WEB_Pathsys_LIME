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
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPathologist.patologoName }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPathologist.patologoCode }}</span>
                </p>
              </div>
              
              <!-- Detalles del patólogo en vertical -->
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Iniciales:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.InicialesPatologo }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Email:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.PatologoEmail }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Registro médico:</span>
                  <p class="text-gray-800 font-semibold">{{ createdPathologist.registro_medico }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdPathologist.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdPathologist.isActive ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdPathologist.fecha_creacion) }}</p>
                </div>
              </div>
              
              <!-- Observaciones -->
              <div v-if="createdPathologist.observaciones">
                <span class="text-gray-500 font-medium block mb-2">Observaciones:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdPathologist.observaciones }}</p>
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
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { usePathologistCreation } from '../../composables/usePathologistCreation'
import type { PathologistFormModel, PathologistCreateResponse } from '../../types/pathologist.types'

// Props y emits
const modelValue = defineModel<PathologistFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-creado', payload: PathologistFormModel): void 
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado del patólogo creado
const createdPathologist = ref<PathologistCreateResponse | null>(null)

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
  licenseValidationError,
  canSubmit: canSubmitFromComposable,
  validateForm,
  checkCodeAvailability,
  checkEmailAvailability,
  checkMedicalLicenseAvailability,
  createPathologist,
  clearState,
  clearMessages
} = usePathologistCreation()

// Estado de loading local
const isLoading = ref(false)

// Modelo local del formulario
const localModel = reactive<PathologistFormModel>({ 
  ...modelValue.value
})

// Errores del formulario
const formErrors = reactive({
  patologoName: '',
  InicialesPatologo: '',
  patologoCode: '',
  PatologoEmail: '',
  registro_medico: '',
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
  formErrors.patologoCode = ''
  
  if (!localModel.patologoCode?.trim()) {
    formErrors.patologoCode = 'El código es requerido'
    return
  }
  
  if (localModel.patologoCode.length < 6) {
    formErrors.patologoCode = 'Mínimo 6 caracteres'
    return
  }
  
  if (localModel.patologoCode.length > 10) {
    formErrors.patologoCode = 'Máximo 10 caracteres'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkCodeAvailability(localModel.patologoCode)
  if (codeValidationError.value) {
    formErrors.patologoCode = codeValidationError.value
  }
}

// Validación del email al perder el foco
const validateEmail = async () => {
  formErrors.PatologoEmail = ''
  
  if (!localModel.PatologoEmail?.trim()) {
    formErrors.PatologoEmail = 'El email es requerido'
    return
  }
  
  if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(localModel.PatologoEmail)) {
    formErrors.PatologoEmail = 'Formato de email inválido'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkEmailAvailability(localModel.PatologoEmail)
  if (emailValidationError.value) {
    formErrors.PatologoEmail = emailValidationError.value
  }
}

// Validación del registro médico al perder el foco
const validateMedicalLicense = async () => {
  formErrors.registro_medico = ''
  
  if (!localModel.registro_medico?.trim()) {
    formErrors.registro_medico = 'El registro médico es requerido'
    return
  }
  
  if (localModel.registro_medico.length < 5) {
    formErrors.registro_medico = 'Mínimo 5 caracteres'
    return
  }
  
  if (localModel.registro_medico.length > 50) {
    formErrors.registro_medico = 'Máximo 50 caracteres'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkMedicalLicenseAvailability(localModel.registro_medico)
  if (licenseValidationError.value) {
    formErrors.registro_medico = licenseValidationError.value
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
  createdPathologist.value = null
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
    const result = await createPathologist(localModel)
    
    if (result.success && result.data) {
      await handlePathologistCreated(result.data)
    } else {
      // ✅ El composable ya maneja los errores y los coloca en state.error
      // Solo necesitamos mostrar el error que ya está en el estado
      const errorMessage = state.error || 'Error desconocido al crear el patólogo'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handlePathologistCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Manejar la creación exitosa del patólogo
const handlePathologistCreated = async (createdPathologistData: any) => {
  // Almacenar información del patólogo creado
  createdPathologist.value = createdPathologistData
  
  // Mostrar notificación de éxito
  showNotification(
    'success',
    '¡Patólogo Registrado Exitosamente!',
    ''
  )
  
  // Emitir evento para compatibilidad
  emit('usuario-creado', { ...localModel })
  
  // Hacer scroll a la notificación
  await scrollToNotification()
}

// Manejar errores durante la creación
const handlePathologistCreationError = async (error: any) => {
  console.error('Error al guardar patólogo:', error)
  
  let errorMessage = 'No se pudo guardar el patólogo. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Patólogo'
  
  // Determinar el tipo de error y mostrar mensaje específico
  if (error.message) {
    errorMessage = error.message
    
    // Personalizar el título según el tipo de error
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

// Función para limpiar solo el formulario (para uso interno)
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


