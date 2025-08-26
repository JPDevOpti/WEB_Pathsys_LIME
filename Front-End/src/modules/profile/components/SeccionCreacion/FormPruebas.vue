<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Formulario de Pruebas</h4>
    </div>

    <!-- Código y Nombre -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código de prueba" 
      placeholder="Ejemplo: BIO-01" 
      v-model="localModel.pruebaCode"
      :error="formErrors.pruebaCode"
      @blur="validateCode"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre de la prueba" 
      placeholder="Ejemplo: Biopsia" 
      v-model="localModel.pruebasName"
      :error="formErrors.pruebasName"
    />

    <!-- Descripción -->
    <FormTextarea 
      class="col-span-full" 
      label="Descripción" 
      placeholder="Descripción detallada de la prueba" 
      v-model="localModel.pruebasDescription" 
      :rows="3"
      :error="formErrors.pruebasDescription"
    />

    <!-- Tiempo estimado y Estado activo -->
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Tiempo estimado (días)" 
      type="number"
      placeholder="Ej. 7" 
      v-model.number="localModel.tiempo"
      :error="formErrors.tiempo"
      min="1"
      max="365"
    />
    <div class="col-span-full md:col-span-6 flex items-center justify-center pt-6">
      <FormCheckbox label="Activo" v-model="localModel.isActive" />
    </div>



    <!-- Botones de acción -->
    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton type="button" @click="onClear" :disabled="isLoading" />
      <SaveButton 
        text="Guardar Prueba" 
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
        <template v-if="notification.type === 'success' && createdTest" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <!-- Información principal de la prueba -->
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdTest.pruebasName }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdTest.pruebaCode }}</span>
                </p>
              </div>
              
              <!-- Detalles de la prueba en vertical -->
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Tiempo estimado:</span>
                  <p class="text-gray-800 font-semibold">{{ createdTest.tiempo }} día{{ createdTest.tiempo !== 1 ? 's' : '' }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdTest.isActive ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdTest.isActive ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdTest.fecha_creacion) }}</p>
                </div>
              </div>
              
              <!-- Descripción -->
              <div v-if="createdTest.pruebasDescription">
                <span class="text-gray-500 font-medium block mb-2">Descripción:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdTest.pruebasDescription }}</p>
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
import { useTestCreation } from '../../composables/useTestCreation'
import type { TestFormModel, TestCreateResponse } from '../../types/test.types'

// Props y emits
const modelValue = defineModel<TestFormModel>({ required: true })
const emit = defineEmits<{ 
  (e: 'usuario-creado', payload: TestFormModel): void 
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado de la prueba creada
const createdTest = ref<TestCreateResponse | null>(null)

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
  canSubmit: canSubmitFromComposable,
  validateForm,
  checkCodeAvailability,
  createTest,
  clearState,
  clearMessages
} = useTestCreation()

// Estado de loading local
const isLoading = ref(false)

// Modelo local del formulario
const localModel = reactive<TestFormModel>({ 
  ...modelValue.value,
  tiempo: modelValue.value.tiempo || 1
})

// Errores del formulario
const formErrors = reactive({
  pruebaCode: '',
  pruebasName: '',
  pruebasDescription: '',
  tiempo: ''
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
  Object.assign(localModel, {
    ...newValue,
    tiempo: newValue.tiempo || 1
  })
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
  formErrors.pruebaCode = ''
  
  if (!localModel.pruebaCode?.trim()) {
    formErrors.pruebaCode = 'El código es requerido'
    return
  }
  
  if (localModel.pruebaCode.length < 3) {
    formErrors.pruebaCode = 'Mínimo 3 caracteres'
    return
  }
  
  if (!/^[A-Z0-9_-]+$/i.test(localModel.pruebaCode)) {
    formErrors.pruebaCode = 'Solo letras, números, guiones y guiones bajos'
    return
  }
  
  // Verificar disponibilidad en el backend
  await checkCodeAvailability(localModel.pruebaCode)
  if (codeValidationError.value) {
    formErrors.pruebaCode = codeValidationError.value
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
  createdTest.value = null
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
    const result = await createTest(localModel)
    
    if (result.success && result.data) {
      await handleTestCreated(result.data)
    } else {
      // ✅ El composable ya maneja los errores y los coloca en state.error
      // Solo necesitamos mostrar el error que ya está en el estado
      const errorMessage = state.error || 'Error desconocido al crear la prueba'
      throw new Error(errorMessage)
    }
  } catch (error: any) {
    await handleTestCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Manejar la creación exitosa de la prueba
const handleTestCreated = async (createdTestData: TestCreateResponse) => {
  // Almacenar información de la prueba creada
  createdTest.value = createdTestData
  
  // Mostrar notificación de éxito
  showNotification(
    'success',
    '¡Prueba Registrada Exitosamente!',
    ''
  )
  
  // Emitir evento para compatibilidad
  emit('usuario-creado', { ...localModel })
  
  // Hacer scroll a la notificación
  await scrollToNotification()
}

// Manejar errores durante la creación
const handleTestCreationError = async (error: any) => {
  console.error('Error al guardar prueba:', error)
  
  let errorMessage = 'No se pudo guardar la prueba. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Prueba'
  
  // Determinar el tipo de error y mostrar mensaje específico
  if (error.message) {
    errorMessage = error.message
    
    // Personalizar el título según el tipo de error
    if (error.message.includes('código')) {
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
        errorMessage = 'Ya existe una prueba con los datos proporcionados'
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
    pruebaCode: '', 
    pruebasName: '', 
    pruebasDescription: '', 
    tiempo: 1,
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


