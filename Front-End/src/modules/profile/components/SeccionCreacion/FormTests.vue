<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Formulario de Pruebas</h4>
    </div>

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Nombre de la prueba" 
      placeholder="Ejemplo: Biopsia" 
      v-model="localModel.testName"
      :error="formErrors.testName"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Código de prueba" 
      placeholder="Ejemplo: BIO-01" 
      v-model="localModel.testCode"
      :error="formErrors.testCode"
      @blur="validateCode"
    />

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Tiempo estimado (días)" 
      type="number"
      placeholder="Ej. 7" 
      v-model.number="localModel.timeDays"
      :error="formErrors.timeDays"
      min="1"
      max="365"
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Precio (COP)" 
      type="number"
      placeholder="Ej. 50000" 
      v-model.number="localModel.price"
      :error="formErrors.price"
      min="0"
      step="100"
    />

    <FormTextarea 
      class="col-span-full" 
      label="Descripción" 
      placeholder="Descripción detallada de la prueba" 
      v-model="localModel.testDescription" 
      :rows="3"
      :error="formErrors.testDescription"
    />

    <div class="col-span-full flex items-center justify-start pt-4">
      <FormCheckbox label="Activo" v-model="localModel.isActive" />
    </div>

    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton type="button" @click="onClear" :disabled="isLoading" />
      <SaveButton 
        text="Guardar Prueba" 
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
        <template v-if="notification.type === 'success' && createdTest" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdTest.name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Código:</span> 
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ createdTest.test_code }}</span>
                </p>
              </div>
              
              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Tiempo estimado:</span>
                  <p class="text-gray-800 font-semibold">{{ createdTest.time }} día{{ createdTest.time !== 1 ? 's' : '' }}</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Precio:</span>
                  <p class="text-gray-800 font-semibold">${{ createdTest.price?.toLocaleString('es-CO') || '0' }} COP</p>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="createdTest.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ createdTest.is_active ? 'Activo' : 'Inactivo' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Fecha de creación:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(createdTest.created_at) }}</p>
                </div>
              </div>
              
              <div v-if="createdTest.description">
                <span class="text-gray-500 font-medium block mb-2">Descripción:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ createdTest.description }}</p>
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
import { reactive, computed, watch, nextTick, ref } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton } from '@/shared/components/ui/buttons'
import { Notification, ValidationAlert } from '@/shared/components/ui/feedback'
import { useTestCreation } from '../../composables/useTestCreation'
import type { TestFormModel, TestCreateResponse } from '../../types/test.types'

// Props and emits
const modelValue = defineModel<TestFormModel>({ required: true })
const emit = defineEmits<{ (e: 'usuario-creado', payload: TestFormModel): void }>()

// Refs and reactive state
const notificationContainer = ref<HTMLElement | null>(null)
const createdTest = ref<TestCreateResponse | null>(null)
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

// Composable for backend operations
const {
  state,
  codeValidationError,
  validateForm,
  checkCodeAvailability,
  createTest,
  clearState,
  clearMessages
} = useTestCreation()

// Local form model
const localModel = reactive<TestFormModel>({ 
  ...modelValue.value,
  timeDays: modelValue.value.timeDays || 1,
  price: modelValue.value.price || 0
})

// Form validation errors
const formErrors = reactive({
  testCode: '',
  testName: '',
  testDescription: '',
  timeDays: '',
  price: ''
})

// Computed properties
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const validation = validateForm(localModel)
  return validation.isValid ? [] : Object.values(validation.errors)
})

const canSubmit = computed(() => true)

// Validation functions
const validateCode = async () => {
  formErrors.testCode = ''
  if (!localModel.testCode?.trim()) {
    formErrors.testCode = 'El código es requerido'
    return
  }
  if (!/^[A-Z0-9_-]+$/i.test(localModel.testCode)) {
    formErrors.testCode = 'Solo letras, números, guiones y guiones bajos'
    return
  }
  await checkCodeAvailability(localModel.testCode)
  if (codeValidationError.value) {
    formErrors.testCode = codeValidationError.value
  }
}

// Helper functions
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
  createdTest.value = null
}

const closeNotification = () => onClear()

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleDateString('es-ES', {
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

const scrollToNotification = async () => {
  await nextTick()
  notificationContainer.value?.scrollIntoView({
    behavior: 'smooth',
    block: 'center'
  })
}

// Form submission
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  isLoading.value = true
  
  try {
    const result = await createTest(localModel)
    if (result.success && result.data) {
      await handleTestCreated(result.data)
    } else {
      throw new Error(state.error || 'Error desconocido al crear la prueba')
    }
  } catch (error: any) {
    await handleTestCreationError(error)
  } finally {
    isLoading.value = false
  }
}

// Success handler
const handleTestCreated = async (createdTestData: TestCreateResponse) => {
  createdTest.value = createdTestData
  showNotification('success', '¡Prueba Registrada Exitosamente!', '')
  emit('usuario-creado', { ...localModel })
  await scrollToNotification()
}

// Error handler with HTTP status code mapping
const handleTestCreationError = async (error: any) => {
  console.error('Error al guardar prueba:', error)
  
  let errorMessage = 'No se pudo guardar la prueba. Por favor, inténtelo nuevamente.'
  let errorTitle = 'Error al Guardar Prueba'
  
  if (error.message) {
    errorMessage = error.message
    if (error.message.includes('código')) errorTitle = 'Datos Duplicados'
    else if (error.message.includes('válido') || error.message.includes('requerido')) errorTitle = 'Datos Inválidos'
    else if (error.message.includes('servidor')) errorTitle = 'Error del Servidor'
  } else if (error.response?.data?.detail) {
    errorMessage = error.response.data.detail
  } else if (error.response?.status) {
    const statusMessages = {
      409: { title: 'Datos Duplicados', message: 'Ya existe una prueba con los datos proporcionados' },
      422: { title: 'Datos Inválidos', message: 'Los datos proporcionados no son válidos' },
      400: { title: 'Datos Incorrectos', message: 'Datos incorrectos o incompletos' },
      500: { title: 'Error del Servidor', message: 'Error interno del servidor. Inténtelo más tarde' }
    }
    const statusError = statusMessages[error.response.status as keyof typeof statusMessages]
    if (statusError) {
      errorTitle = statusError.title
      errorMessage = statusError.message
    } else {
      errorTitle = `Error del Servidor (${error.response.status})`
      errorMessage = 'Ha ocurrido un error inesperado'
    }
  }
  
  showNotification('error', errorTitle, errorMessage)
  await scrollToNotification()
}

// Form reset functions
const clearForm = () => {
  validationState.hasAttemptedSubmit = false
  validationState.showValidationError = false
  clearFormErrors()
  clearState()
  Object.assign(localModel, { 
    testCode: '', 
    testName: '', 
    testDescription: '', 
    timeDays: 1,
    price: 0,
    isActive: true 
  })
}

const onClear = () => {
  clearForm()
  clearNotification()
}

// Watchers
watch(() => modelValue.value, (newValue) => {
  Object.assign(localModel, {
    ...newValue,
    timeDays: newValue.timeDays || 1,
    price: newValue.price || 0
  })
}, { deep: true })

watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})
</script>


