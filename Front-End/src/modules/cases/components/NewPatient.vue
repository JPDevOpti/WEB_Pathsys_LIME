<template>
  <ComponentCard title="Ingresar un nuevo paciente al sistema" description="Complete la información del paciente para ingresarlo al sistema.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    </template>

    <div class="space-y-6">
      <!-- Campos principales del formulario -->
      <FormInputField v-model="formData.pacienteCode" label="Documento de identidad" placeholder="Ejemplo: 12345678" :required="true" :max-length="10" :show-counter="true" :errors="errors.pacienteCode" :warnings="warnings.pacienteCode" :is-validating="false" inputmode="numeric" @input="handleCedulaInput" />
      <FormInputField v-model="formData.nombrePaciente" label="Nombre del Paciente" placeholder="Ingrese el nombre completo del paciente" :required="true" :max-length="100" :errors="errors.nombrePaciente" @input="handleNombreInput" />
      
      <!-- Campos de edad y sexo en grid responsivo -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormInputField v-model="formData.edad" label="Edad" placeholder="Edad en años" :required="true" :max-length="3" :errors="errors.edad" :warnings="warnings.edad" inputmode="numeric" @input="handleEdadInput" />
        <FormSelect v-model="formData.sexo" label="Sexo" placeholder="Seleccione el sexo" :required="true" :options="sexoOptions" :error="getSexoError" />
      </div>

      <!-- Campos de entidad y tipo de atención -->
      <EntityList v-model="formData.entidad" label="Entidad" placeholder="Buscar entidad..." :required="true" :auto-load="true" :error="getEntidadError" :key="entityListKey" @entity-selected="onEntitySelected" />
      <FormSelect v-model="formData.tipoAtencion" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" :error="getTipoAtencionError" />
      <FormTextarea v-model="formData.observaciones" label="Observaciones del paciente" placeholder="Observaciones adicionales (opcional)" :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional sobre el paciente" />

      <!-- Botones de acción -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton @click="handleClearForm" :disabled="isLoading" />
        <SaveButton text="Guardar Paciente" @click="handleSaveClick" :disabled="isLoading" :loading="isLoading" />
      </div>

      <!-- Contenedor de notificaciones -->
      <div ref="notificationContainer">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && createdPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPatient.nombre }}</h3>
                  <p class="text-gray-600"><span class="font-medium">Cédula:</span> <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPatient.cedula }}</span></p>
                </div>
                <div class="grid grid-cols-4 gap-6 text-sm">
                  <div><span class="text-gray-500 font-medium block mb-1">Edad:</span><p class="text-gray-800 font-semibold">{{ createdPatient.edad }} años</p></div>
                  <div><span class="text-gray-500 font-medium block mb-1">Sexo:</span><p class="text-gray-800 font-semibold">{{ createdPatient.sexo }}</p></div>
                  <div><span class="text-gray-500 font-medium block mb-1">Entidad:</span><p class="text-gray-800 font-semibold">{{ createdPatient.entidad_info?.nombre }}</p></div>
                  <div><span class="text-gray-500 font-medium block mb-1">Atención:</span><p class="text-gray-800 font-semibold">{{ createdPatient.tipo_atencion }}</p></div>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <!-- Alerta de validación -->
      <ValidationAlert :visible="validationState.showValidationError" :errors="validationErrors" />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePatientForm } from '../composables/usePatientForm'
import { useNotifications } from '../composables/useNotifications'
import { usePatientAPI } from '../composables/usePatientAPI'
import type { PatientData } from '../types'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { ValidationAlert, Notification } from '@/shared/components/feedback'
import { EntityList } from '@/shared/components/List'

// Referencias del DOM y estado local
const notificationContainer = ref<HTMLElement | null>(null)
const createdPatient = ref<any>(null)
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const entityListKey = ref(0)

// Composables para manejo del formulario, notificaciones y API
const { formData, errors, warnings, isLoading: isFormLoading, validationState, handleCedulaInput, handleNombreInput, handleEdadInput, clearForm, validateForm } = usePatientForm()
const { notification, showNotification, closeNotification } = useNotifications()
const { createPatient, isLoading: isApiLoading, error: apiError, clearState } = usePatientAPI()

// Opciones para los selectores
const sexoOptions = [{ value: 'Masculino', label: 'Masculino' }, { value: 'Femenino', label: 'Femenino' }]
const tipoAtencionOptions = [{ value: 'Ambulatorio', label: 'Ambulatorio' }, { value: 'Hospitalizado', label: 'Hospitalizado' }]

// Estado de carga combinado
const isLoading = computed(() => isFormLoading.value || isApiLoading.value)

// Validación de errores del formulario
const validationErrors = computed(() => {
  const errorsList: string[] = []
  if (!formData.pacienteCode || errors.pacienteCode?.length > 0) errorsList.push('Cédula válida requerida')
  if (!formData.nombrePaciente || errors.nombrePaciente?.length > 0) errorsList.push('Nombre completo requerido')
  if (!formData.edad || errors.edad?.length > 0) errorsList.push('Edad válida requerida')
  if (!formData.sexo) errorsList.push('Sexo requerido')
  if (!formData.entidad) errorsList.push('Entidad requerida')
  if (!formData.tipoAtencion) errorsList.push('Tipo de atención requerido')
  return errorsList
})

// Errores de validación para campos específicos
const getSexoError = computed(() => validationState.hasAttemptedSubmit && !formData.sexo ? 'Por favor seleccione el sexo' : '')
const getEntidadError = computed(() => validationState.hasAttemptedSubmit && !formData.entidad ? 'La entidad es obligatoria' : '')
const getTipoAtencionError = computed(() => validationState.hasAttemptedSubmit && !formData.tipoAtencion ? 'Por favor seleccione el tipo de atención' : '')

// Handlers de eventos
const onEntitySelected = (entity: { codigo: string; nombre: string } | null) => selectedEntity.value = entity
const handleClearForm = () => { clearForm(); selectedEntity.value = null; entityListKey.value++ }

// Manejo del guardado del paciente
const handleSaveClick = async () => {
  const isValid = validateForm()
  if (!isValid) { validationState.showValidationError = true; return }
  validationState.showValidationError = false
  clearState()

  try {
    const patientData: PatientData = {
      pacienteCode: formData.pacienteCode,
      nombrePaciente: formData.nombrePaciente,
      sexo: formData.sexo,
      edad: formData.edad,
      entidad: selectedEntity.value?.nombre || formData.entidad,
      entidadCodigo: selectedEntity.value?.codigo,
      tipoAtencion: formData.tipoAtencion,
      observaciones: formData.observaciones
    }
    
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

// Manejo exitoso de la creación del paciente
const handlePatientCreated = async (createdPatientData: any, patientData: PatientData) => {
  createdPatient.value = createdPatientData
  showNotification('success', '¡Paciente Registrado Exitosamente!', '', 15000)
  emit('patient-saved', patientData)
  clearForm()
  selectedEntity.value = null
  entityListKey.value++
}

// Manejo de errores en la creación del paciente
const handlePatientCreationError = async (error: any) => {
  let errorMessage = 'No se pudo guardar el paciente. Por favor, inténtelo nuevamente.'
  
  if (error.response?.data?.detail) {
    if (Array.isArray(error.response.data.detail)) {
      errorMessage = error.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ')
    } else {
      errorMessage = String(error.response.data.detail)
    }
  } else if (error.response?.data?.message) {
    errorMessage = String(error.response.data.message)
  } else if (error.message) {
    errorMessage = String(error.message)
  } else if (apiError.value) {
    errorMessage = String(apiError.value)
  } else if (typeof error === 'string') {
    errorMessage = error
  } else if (error && typeof error === 'object') {
    try { errorMessage = JSON.stringify(error) } catch { errorMessage = 'Error desconocido del servidor' }
  }
  
  showNotification('error', 'Error al Guardar Paciente', errorMessage, 0)
}

// Scroll automático a notificaciones
watch(() => notification.visible, (newValue) => {
  if (newValue && notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})

// Emisión de eventos
const emit = defineEmits<{ 'patient-saved': [patient: PatientData]; 'update-patient-data': [patient: PatientData] }>()
</script>
