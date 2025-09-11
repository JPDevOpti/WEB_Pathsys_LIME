<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Editar Prueba</h4>
      <p class="text-sm text-gray-600 mt-1">Modifica los datos de la prueba médica</p>
    </div>

    <!-- Loading state inicial -->
    <div v-if="isLoadingTest" class="col-span-full flex justify-center items-center py-8">
      <div class="flex items-center space-x-2">
        <div class="animate-spin rounded-full h-5 w-5 border-b-2 border-blue-600"></div>
        <span class="text-gray-600">Cargando datos de la prueba...</span>
      </div>
    </div>

    <!-- Formulario de edición -->
    <template v-else-if="localModel.pruebaCode">
      <!-- Nombre y Código -->
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Nombre de la prueba" 
        placeholder="Ejemplo: Biopsia" 
        v-model="localModel.pruebasName"
        :error="formErrors.pruebasName"
      />
      <FormInputField 
        class="col-span-full md:col-span-6" 
        label="Código de prueba" 
        placeholder="Ejemplo: BIO-01" 
        v-model="localModel.pruebaCode"
        :error="formErrors.pruebaCode"
        @blur="validateCode"
        :disabled="true"
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

      <!-- Notificación -->
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
                <!-- Información principal de la prueba -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedTest.prueba_name }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Código:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedTest.prueba_code }}</span>
                  </p>
                </div>
                
                <!-- Detalles de la prueba en vertical -->
                <div class="space-y-4 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Tiempo estimado:</span>
                    <p class="text-gray-800 font-semibold">{{ updatedTest.tiempo }} día{{ updatedTest.tiempo !== 1 ? 's' : '' }}</p>
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
                    <p class="text-gray-800 font-semibold">{{ formatDate(updatedTest.fecha_actualizacion) }}</p>
                  </div>
                </div>
                
                <!-- Descripción -->
                <div v-if="updatedTest.prueba_description">
                  <span class="text-gray-500 font-medium block mb-2">Descripción:</span>
                  <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedTest.prueba_description }}</p>
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
    </template>

    <!-- Estado de error al cargar (solo mostrar si hay datos pero faltan campos críticos) -->
    <div v-else-if="!isLoadingTest && props.usuario && !localModel.pruebaCode" class="col-span-full">
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

    <!-- Estado sin selección (cuando no hay usuario seleccionado) -->
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

// Props y emits
const props = defineProps<{ 
  usuario: any // Objeto con datos de la prueba a editar
  usuarioActualizado: boolean
  mensajeExito: string
}>()

const emit = defineEmits<{ 
  (e: 'usuario-actualizado', payload: any): void 
  (e: 'cancelar'): void 
}>()

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado de la prueba actualizada
const updatedTest = ref<TestUpdateResponse | null>(null)

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
  // isCheckingCode, // No usado en el template actual
  isLoadingTest,
  codeValidationError,
  originalTestData,
  canSubmit,
  validateForm,
  // loadTestForEdition, // No usado porque cargamos desde props
  checkCodeAvailability,
  updateTest,
  setInitialData,
  resetToOriginal,
  clearState,
  clearMessages,
  createHasChanges
} = useTestEdition()

// Estado de loading local
const isLoading = computed(() => state.isLoading)

// Computed para detectar cambios en el formulario
const hasChanges = computed(() => {
  return createHasChanges(localModel)
})

// Modelo local del formulario
const localModel = reactive<TestEditFormModel>({
  id: '',
  pruebaCode: '',
  pruebasName: '',
  pruebasDescription: '',
  tiempo: 1,
  isActive: true
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
  
  const validationErrorsList: string[] = []
  
  if (!localModel.pruebaCode || formErrors.pruebaCode) {
    validationErrorsList.push('Código de prueba válido requerido')
  }
  if (!localModel.pruebasName || formErrors.pruebasName) {
    validationErrorsList.push('Nombre de la prueba requerido')
  }
  if (!localModel.pruebasDescription || formErrors.pruebasDescription) {
    validationErrorsList.push('Descripción requerida')
  }
  if (!localModel.tiempo || localModel.tiempo <= 0) {
    validationErrorsList.push('Tiempo estimado válido requerido')
  }
  
  return validationErrorsList
})



// Cargar datos iniciales
onMounted(() => {
  if (props.usuario) {
    loadInitialData()
  }
})

// Función para cargar datos iniciales
// Normalizador de campos para pruebas (pruebas -> test, etc.)
const normalizeTest = (raw: any): TestEditFormModel | null => {
  if (!raw) return null
  const code = raw.pruebaCode || raw.testCode || raw.codigo || raw.code || ''
  const name = raw.pruebasName || raw.testName || raw.nombre || raw.name || ''
  const desc = raw.pruebasDescription || raw.testDescription || raw.descripcion || raw.description || ''
  const tiempo = raw.tiempo !== undefined ? Number(raw.tiempo) : 1
  const active = raw.isActive !== undefined ? raw.isActive : (raw.is_active !== undefined ? raw.is_active : (raw.activo !== undefined ? raw.activo : true))
  const id = raw.id || raw._id || code
  return {
    id: id,
    pruebaCode: String(code),
    pruebasName: String(name),
    pruebasDescription: String(desc),
    tiempo: tiempo > 0 ? tiempo : 1,
    isActive: !!active
  }
}

const loadInitialData = () => {
  try {
    const mappedData = normalizeTest(props.usuario)
    if (!mappedData) throw new Error('No se recibieron datos de la prueba')
    if (!mappedData.pruebaCode || !mappedData.pruebasName) throw new Error('Código y nombre de la prueba son requeridos')
    Object.assign(localModel, mappedData)
    setInitialData(mappedData)
  } catch (error: any) {
    showNotification('error', 'Error al cargar datos', error.message || 'No se pudieron cargar los datos de la prueba')
  }
}

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
  
  if (!/^[A-Z0-9_-]+$/i.test(localModel.pruebaCode)) {
    formErrors.pruebaCode = 'Solo letras, números, guiones y guiones bajos'
    return
  }
  
  // Verificar disponibilidad en el backend (excluyendo el código original)
  const originalCode = originalTestData.value?.pruebaCode
  await checkCodeAvailability(localModel.pruebaCode, originalCode)
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
  updatedTest.value = null
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
    Object.assign(formErrors, validation.errors)
    validationState.showValidationError = true
    return
  }
  
  validationState.showValidationError = false
  
  try {
    // Enviar al backend
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

// Manejar la actualización exitosa de la prueba
const handleTestUpdated = async (updatedTestData: TestUpdateResponse) => {
  // Almacenar información de la prueba actualizada
  updatedTest.value = updatedTestData
  
  // Mostrar notificación de éxito
  showNotification('success', '¡Prueba Actualizada Exitosamente!', '')
  
  // Emitir evento para compatibilidad con la estructura existente
  emit('usuario-actualizado', {
    ...updatedTestData,
    nombre: updatedTestData.prueba_name,
    codigo: updatedTestData.prueba_code,
    tipo: 'pruebas'
  })
  
  // Hacer scroll a la notificación
  await scrollToNotification()
}

// Manejar errores durante la actualización
const handleTestUpdateError = async (error: any) => {
  console.error('Error al actualizar prueba:', error)
  
  const errorMessage = error.message || 'No se pudo actualizar la prueba. Por favor, inténtelo nuevamente.'
  
  showNotification(
    'error',
    'Error al Actualizar Prueba',
    errorMessage
  )
  
  await scrollToNotification()
}

// Restablecer formulario a los datos originales
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



// Watcher para hacer scroll cuando aparece la notificación
watch(
  () => notification.visible,
  (newValue) => {
    if (newValue) {
      scrollToNotification()
    }
  }
)



// Watcher para cambios en el usuario seleccionado
watch(() => props.usuario, (newUsuario) => {
  if (newUsuario && newUsuario.id !== localModel.id) {
    clearState()
    loadInitialData()
  }
}, { deep: true })

// Watcher para mostrar mensaje de éxito externo
watch(() => props.usuarioActualizado, (isUpdated) => {
  if (isUpdated && props.mensajeExito) {
    showNotification('success', '¡Actualización Exitosa!', props.mensajeExito)
  }
})
</script>
