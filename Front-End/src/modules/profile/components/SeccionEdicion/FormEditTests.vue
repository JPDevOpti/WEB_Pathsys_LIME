<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Editar Prueba</h4>
      <p class="text-sm text-gray-600 mt-1">Modifica los datos de la prueba médica</p>
    </div>

    <div v-if="isLoadingTest" class="col-span-full flex justify-center items-center py-8">
      <div class="flex items-center space-x-2">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
        <span class="text-gray-600">Cargando datos de la prueba...</span>
      </div>
    </div>

    <template v-else-if="localModel.testCode">
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
        :disabled="true"
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
        <ClearButton 
          type="button" 
          @click="onReset" 
          :disabled="isLoading || !hasChanges"
          variant="secondary"
          :text="'Reiniciar'"
          :icon="'reset'"
        >
          <template #icon>
            <RefreshIcon class="w-4 h-4 mr-2" />
          </template>
        </ClearButton>
        <SaveButton 
          text="Actualizar Prueba" 
          type="submit" 
          :disabled="!canSubmit || isLoading || !hasChanges"
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
          @close="() => {}"
        >
          <template v-if="notification.type === 'success' && updatedTest" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedTest.name }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Código:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedTest.test_code }}</span>
                  </p>
                </div>
                
                <div class="space-y-4 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Tiempo estimado:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedTest.time }} día{{ updatedTest.time !== 1 ? 's' : '' }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Precio:</span>
                    <p class="text-gray-800 font-semibold">${{ updatedTest.price?.toLocaleString('es-CO') || '0' }} COP</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Estado:</span>
                    <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                      :class="updatedTest.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                      {{ updatedTest.is_active ? 'Activo' : 'Inactivo' }}
                    </span>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Última actualización:</span>
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedTest.updated_at) }}</p>
                  </div>
                </div>
                
                <div v-if="updatedTest.description">
                  <span class="text-gray-500 font-medium block mb-2">Descripción:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedTest.description }}</p>
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
    </template>

    <div v-else-if="!isLoadingTest && props.usuario && !localModel.testCode" class="col-span-full">
      <div class="text-center py-8">
        <div class="text-red-600 mb-2">
          <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.694-.833-2.464 0L3.34 16.5c-.77.833.192 2.5 1.732 2.5z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Error al cargar la prueba</h3>
        <p class="text-gray-600">No se pudieron cargar los datos de la prueba para edición.</p>
        <p class="text-sm text-gray-500 mt-2">Falta el código de la prueba.</p>
      </div>
    </div>

    <div v-else-if="!props.usuario" class="col-span-full">
      <div class="text-center py-8">
        <div class="text-gray-400 mb-2">
          <svg class="mx-auto h-12 w-12" fill="none" viewBox="0 0 24 24" stroke="currentColor">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
          </svg>
        </div>
        <h3 class="text-lg font-medium text-gray-900 mb-1">Selecciona una prueba</h3>
        <p class="text-gray-600">Busca y selecciona una prueba de la lista para editarla.</p>
      </div>
    </div>
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, watch, nextTick, ref, onMounted } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useTestEdition } from '../../composables/useTestEdition'
import type { TestEditFormModel, TestUpdateResponse } from '../../types/test.types'
import { RefreshIcon } from '@/assets/icons'

// Props and emits
const props = defineProps<{ 
  usuario: any
  usuarioActualizado: boolean
  mensajeExito: string
}>()

const emit = defineEmits<{ 
  (e: 'usuario-actualizado', payload: any): void 
  (e: 'cancelar'): void 
}>()

// Refs and reactive state
const notificationContainer = ref<HTMLElement | null>(null)
const updatedTest = ref<TestUpdateResponse | null>(null)

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
  isLoadingTest,
  codeValidationError,
  originalTestData,
  canSubmit,
  validateForm,
  checkCodeAvailability,
  updateTest,
  setInitialData,
  resetToOriginal,
  clearState,
  clearMessages,
  createHasChanges
} = useTestEdition()

// Computed properties
const isLoading = computed(() => state.isLoading)

const hasChanges = computed(() => {
  return createHasChanges(localModel)
})

// Local form model
const localModel = reactive<TestEditFormModel>({
  id: '',
  testCode: '',
  testName: '',
  testDescription: '',
  timeDays: 1,
  price: 0,
  isActive: true
})

// Form validation errors
const formErrors = reactive({
  testCode: '',
  testName: '',
  testDescription: '',
  timeDays: '',
  price: ''
})

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const validation = validateForm(localModel)
  return validation.isValid ? [] : Object.values(validation.errors)
})

// Data normalization for backend compatibility
const normalizeTest = (raw: any): TestEditFormModel | null => {
  if (!raw) return null
  const code = raw.testCode || raw.pruebaCode || raw.codigo || raw.code || ''
  const name = raw.testName || raw.pruebasName || raw.nombre || raw.name || ''
  const desc = raw.testDescription || raw.pruebasDescription || raw.descripcion || raw.description || ''
  const timeDays = raw.timeDays || raw.tiempo || raw.time || 1
  const price = raw.price || raw.precio || 0
  const active = raw.isActive !== undefined ? raw.isActive : (raw.is_active !== undefined ? raw.is_active : (raw.activo !== undefined ? raw.activo : true))
  const id = raw.id || raw._id || code
  return {
    id: id,
    testCode: String(code),
    testName: String(name),
    testDescription: String(desc),
    timeDays: Number(timeDays) > 0 ? Number(timeDays) : 1,
    price: Number(price) >= 0 ? Number(price) : 0,
    isActive: !!active
  }
}

// Initial data loading
const loadInitialData = () => {
  try {
    const mappedData = normalizeTest(props.usuario)
    if (!mappedData) throw new Error('No se recibieron datos de la prueba')
    if (!mappedData.testCode || !mappedData.testName) throw new Error('Código y nombre de la prueba son requeridos')
    Object.assign(localModel, mappedData)
    setInitialData(mappedData)
  } catch (error: any) {
    showNotification('error', 'Error al cargar datos', error.message || 'No se pudieron cargar los datos de la prueba')
  }
}

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
  const originalCode = originalTestData.value?.testCode
  await checkCodeAvailability(localModel.testCode, originalCode)
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
  updatedTest.value = null
}

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

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Form submission
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  clearNotification()
  
  const validation = validateForm(localModel)
  if (!validation.isValid) {
    Object.assign(formErrors, validation.errors)
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  
  try {
    const result = await updateTest(localModel)
    if (result.success && result.data) {
      await handleTestUpdated(result.data)
    } else {
      throw new Error('Error desconocido al actualizar la prueba')
    }
  } catch (error: any) {
    await handleTestUpdateError(error)
  }
}

// Success handler
const handleTestUpdated = async (updatedTestData: TestUpdateResponse) => {
  updatedTest.value = updatedTestData
  showNotification('success', '¡Prueba Actualizada Exitosamente!', '')
  emit('usuario-actualizado', {
    ...updatedTestData,
    nombre: updatedTestData.name,
    codigo: updatedTestData.test_code,
    tipo: 'pruebas'
  })
  await scrollToNotification()
}

// Error handler
const handleTestUpdateError = async (error: any) => {
  console.error('Error al actualizar prueba:', error)
  const errorMessage = error.message || 'No se pudo actualizar la prueba. Por favor, inténtelo nuevamente.'
  showNotification('error', 'Error al Actualizar Prueba', errorMessage)
  await scrollToNotification()
}

// Form reset functions
const onReset = () => {
  const original = resetToOriginal()
  if (original) {
    Object.assign(localModel, original)
    clearFormErrors()
    clearNotification()
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false
  }
}

// Lifecycle hooks
onMounted(() => {
  if (props.usuario) {
    loadInitialData()
  }
})

// Watchers
watch(() => localModel, () => {
  if (validationState.hasAttemptedSubmit && !notification.visible) {
    clearMessages()
    clearFormErrors()
  }
}, { deep: true })

watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})

watch(() => props.usuario, (newUsuario) => {
  if (newUsuario && newUsuario.id !== localModel.id) {
    clearState()
    loadInitialData()
  }
}, { deep: true })

watch(() => props.usuarioActualizado, (isUpdated) => {
  if (isUpdated && props.mensajeExito) {
    showNotification('success', '¡Actualización Exitosa!', props.mensajeExito)
  }
})
</script>
