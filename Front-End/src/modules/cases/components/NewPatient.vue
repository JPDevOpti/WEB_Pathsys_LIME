<template>
  <ComponentCard 
    title="Ingresar un nuevo paciente al sistema"
    description="Complete la información del paciente para ingresarlo al sistema."
  >
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    </template>

    <!-- Formulario -->
    <div class="space-y-6">
      <!-- Número de Cédula -->
      <FormInputField
        v-model="formData.numeroCedula"
        label="Cédula"
        placeholder="Ejemplo: 12345678"
        :required="true"
        :max-length="10"
        :show-counter="true"
        :errors="errors.numeroCedula"
        :warnings="warnings.numeroCedula"
        :is-validating="false"
        inputmode="numeric"
        @input="handleCedulaInput"
      />

      <!-- Nombre del Paciente -->
      <FormInputField
        v-model="formData.nombrePaciente"
        label="Nombre del Paciente"
        placeholder="Ingrese el nombre completo del paciente"
        :required="true"
        :max-length="100"
        :errors="errors.nombrePaciente"
        @input="handleNombreInput"
      />

      <!-- Edad y Sexo -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <!-- Edad -->
        <FormInputField
          v-model="formData.edad"
          label="Edad"
          placeholder="Edad en años"
          :required="true"
          :max-length="3"
          :errors="errors.edad"
          :warnings="warnings.edad"
          inputmode="numeric"
          @input="handleEdadInput"
        />
        
        <!-- Sexo -->
        <FormSelect
          v-model="formData.sexo"
          label="Sexo"
          placeholder="Seleccione el sexo"
          :required="true"
          :options="sexoOptions"
          :error="getSexoError"
        />
      </div>

      <!-- Entidad -->
      <EntityList
        v-model="formData.entidad"
        label="Entidad"
        placeholder="Buscar entidad..."
        :required="true"
        :auto-load="true"
        :error="getEntidadError"
        :key="entityListKey"
        @entity-selected="onEntitySelected"
      />

      <!-- Tipo de Atención -->
      <FormSelect
        v-model="formData.tipoAtencion"
        label="Tipo de Atención"
        placeholder="Seleccione el tipo de atención"
        :required="true"
        :options="tipoAtencionOptions"
        :error="getTipoAtencionError"
      />

      <!-- Observaciones -->
      <FormTextarea
        v-model="formData.observaciones"
        label="Observaciones"
        placeholder="Observaciones adicionales (opcional)"
        :rows="3"
        :max-length="500"
        :show-counter="true"
        help-text="Información adicional sobre el paciente o el caso"
      />

      <!-- Botones de Acción -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton
          @click="handleClearForm"
          :disabled="isLoading"
        />
        
        <SaveButton
          text="Guardar Paciente"
          @click="handleSaveClick"
          :disabled="isLoading"
          :loading="isLoading"
        />
      </div>

      <!-- Notificación -->
      <div ref="notificationContainer">
        <Notification
          :visible="notification.visible"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          @close="closeNotification"
        >
          <template v-if="notification.type === 'success' && createdPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Información principal del paciente -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPatient.nombre }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Cédula:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPatient.cedula }}</span>
                  </p>
                </div>
                
                <!-- Detalles del paciente -->
                <div class="grid grid-cols-4 gap-6 text-sm">
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Edad:</span>
                    <p class="text-gray-800 font-semibold">{{ createdPatient.edad }} años</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Sexo:</span>
                    <p class="text-gray-800 font-semibold">{{ createdPatient.sexo }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Entidad:</span>
                    <p class="text-gray-800 font-semibold">{{ createdPatient.entidad_info?.nombre }}</p>
                  </div>
                  <div>
                    <span class="text-gray-500 font-medium block mb-1">Atención:</span>
                    <p class="text-gray-800 font-semibold">{{ createdPatient.tipo_atencion }}</p>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <!-- Alerta de Validación -->
      <ValidationAlert
        :visible="validationState.showValidationError"
        :errors="validationErrors"
      />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import { usePatientForm } from '../composables/usePatientForm'
import { useNotifications } from '../composables/useNotifications'
import { usePatientAPI } from '../composables/usePatientAPI'
import type { PatientData } from '../types'

// Componentes UI
import ComponentCard from '../../../shared/components/ui/ComponentCard.vue'
import FormInputField from '../../../shared/components/ui/forms/FormInputField.vue'
import FormSelect from '../../../shared/components/ui/forms/FormSelect.vue'
import FormTextarea from '../../../shared/components/ui/forms/FormTextarea.vue'
import SaveButton from '../../../shared/components/ui/buttons/SaveButton.vue'
import ClearButton from '../../../shared/components/ui/buttons/ClearButton.vue'
import ValidationAlert from '../../../shared/components/ui/feedback/ValidationAlert.vue'
import Notification from '../../../shared/components/ui/feedback/Notification.vue'
import { EntityList } from '../../../shared/components/ui/List'

// ============================================================================
// ESTADO DEL COMPONENTE
// ============================================================================

// Referencias
const notificationContainer = ref<HTMLElement | null>(null)

// Estado del paciente creado
const createdPatient = ref<any>(null)

// Entidad seleccionada (código y nombre) para construir correctamente el payload
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)

// Key para forzar el re-renderizado del EntityList
const entityListKey = ref(0)

// ============================================================================
// COMPOSABLES
// ============================================================================

const {
  formData,
  errors,
  warnings,
  isLoading: isFormLoading,
  validationState,
  handleCedulaInput,
  handleNombreInput,
  handleEdadInput,
  clearForm,
  validateForm
} = usePatientForm()

const { notification, showNotification, closeNotification } = useNotifications()

const { createPatient, isLoading: isApiLoading, error: apiError, clearState } = usePatientAPI()

// ============================================================================
// CONSTANTES
// ============================================================================

// Opciones para el select de sexo
const sexoOptions = [
  { value: 'masculino', label: 'Masculino' },
  { value: 'femenino', label: 'Femenino' }
]

// Opciones para el select de tipo de atención
const tipoAtencionOptions = [
  { value: 'ambulatorio', label: 'Ambulatorio' },
  { value: 'hospitalizado', label: 'Hospitalizado' }
]

// ============================================================================
// COMPUTED PROPERTIES
// ============================================================================

/**
 * Estado de carga combinado del formulario y la API
 */
const isLoading = computed(() => isFormLoading.value || isApiLoading.value)

/**
 * Lista de errores de validación para mostrar en la alerta
 */
const validationErrors = computed(() => {
  const validationErrorsList: string[] = []
  
  if (!formData.numeroCedula || errors.numeroCedula?.length > 0) {
    validationErrorsList.push('Cédula válida requerida')
  }
  if (!formData.nombrePaciente || errors.nombrePaciente?.length > 0) {
    validationErrorsList.push('Nombre completo requerido')
  }
  if (!formData.edad || errors.edad?.length > 0) {
    validationErrorsList.push('Edad válida requerida')
  }
  if (!formData.sexo) {
    validationErrorsList.push('Sexo requerido')
  }
  if (!formData.entidad) {
    validationErrorsList.push('Entidad requerida')
  }
  if (!formData.tipoAtencion) {
    validationErrorsList.push('Tipo de atención requerido')
  }
  
  return validationErrorsList
})

/**
 * Error para el campo sexo
 */
const getSexoError = computed(() => {
  return validationState.hasAttemptedSubmit && !formData.sexo ? 'Por favor seleccione el sexo' : ''
})

/**
 * Error para el campo entidad
 */
const getEntidadError = computed(() => {
  return validationState.hasAttemptedSubmit && !formData.entidad ? 'La entidad es obligatoria' : ''
})

/**
 * Error para el campo tipo de atención
 */
const getTipoAtencionError = computed(() => {
  return validationState.hasAttemptedSubmit && !formData.tipoAtencion ? 'Por favor seleccione el tipo de atención' : ''
})

// ============================================================================
// FUNCIONES DE UTILIDAD
// ============================================================================

/**
 * Hace scroll a la notificación
 */
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// ============================================================================
// FUNCIONES DE MANIPULACIÓN DE DATOS
// ============================================================================

/**
 * Maneja la selección de entidad
 * @param entity - Entidad seleccionada
 */
const onEntitySelected = (entity: { codigo: string; nombre: string } | null) => {
  selectedEntity.value = entity
}

/**
 * Maneja la limpieza completa del formulario
 */
const handleClearForm = () => {
  clearForm()
  selectedEntity.value = null
  
  // Forzar re-renderizado del EntityList para limpiar su estado interno
  entityListKey.value++
}

// ============================================================================
// FUNCIONES DE GUARDADO
// ============================================================================

/**
 * Maneja el click del botón guardar
 */
const handleSaveClick = async () => {
  const isValid = validateForm()
  
  if (!isValid) {
    validationState.showValidationError = true
    return
  }

  validationState.showValidationError = false
  clearState()

  try {
    // Preparar datos del paciente
    const patientData: PatientData = {
      numeroCedula: formData.numeroCedula,
      nombrePaciente: formData.nombrePaciente,
      sexo: formData.sexo,
      edad: String(formData.edad),
      entidad: selectedEntity.value?.nombre || formData.entidad,
      entidadCodigo: selectedEntity.value?.codigo,
      tipoAtencion: formData.tipoAtencion,
      observaciones: formData.observaciones
    }

    // Crear paciente usando la API
    const result = await createPatient(patientData)
    
    if (result.success && result.patient) {
      await handlePatientCreated(result.patient, patientData)
    } else {
      throw new Error(result.message || 'Error desconocido al crear el paciente')
    }
    
  } catch (error: any) {
    await handlePatientCreationError(error)
  }
}

/**
 * Maneja la creación exitosa del paciente
 * @param createdPatientData - Datos del paciente creado
 * @param patientData - Datos del formulario
 */
const handlePatientCreated = async (createdPatientData: any, patientData: PatientData) => {
  // Almacenar información del paciente creado
  createdPatient.value = createdPatientData
  
  // Mostrar notificación de éxito
  showNotification(
    'success',
    '¡Paciente Registrado Exitosamente!',
    '',
    15000
  )
  
  // Emitir evento con los datos del paciente guardado
  emit('patient-saved', patientData)
  
  // Limpiar formulario
  clearForm()
  
  // Limpiar también la entidad seleccionada
  selectedEntity.value = null
  
  // Forzar re-renderizado del EntityList para limpiar su estado interno
  entityListKey.value++
}

/**
 * Maneja errores durante la creación del paciente
 * @param error - Error capturado
 */
const handlePatientCreationError = async (error: any) => {
  console.error('Error al guardar paciente:', error)
  
  const errorMessage = apiError.value || error.message || 'No se pudo guardar el paciente. Por favor, inténtelo nuevamente.'
  
  showNotification(
    'error',
    'Error al Guardar Paciente',
    errorMessage,
    0
  )
}

// ============================================================================
// WATCHERS
// ============================================================================

// Hacer scroll cuando aparece la notificación
watch(
  () => notification.visible,
  (newValue) => {
    if (newValue) {
      scrollToNotification()
    }
  }
)

// ============================================================================
// EMITS Y EXPOSICIÓN
// ============================================================================

// Definir eventos que emite el componente
const emit = defineEmits<{
  'patient-saved': [patient: PatientData]
  'update-patient-data': [patient: PatientData]
}>()
</script>
