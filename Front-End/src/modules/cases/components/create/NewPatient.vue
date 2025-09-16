<template>
  <ComponentCard title="Ingresar un nuevo paciente al sistema" description="Complete la información del paciente para ingresarlo al sistema.">
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
      </svg>
    </template>

    <div class="space-y-6">
      <FormInputField v-model="formData.patientCode" label="Documento de identidad" placeholder="Ejemplo: 12345678" :required="true" :max-length="12" inputmode="numeric" :only-numbers="true" :errors="getDocumentoErrors" @input="handleCedulaInput" />
      <FormInputField v-model="formData.name" label="Nombre del Paciente" placeholder="Ejemplo: Juan Perez" :required="true" :max-length="200" :only-letters="true" :errors="getNombreErrors" @input="handleNombreInput" />
      
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormInputField v-model="formData.age" label="Edad" placeholder="Edad en años" :required="true" :max-length="3" inputmode="numeric" :only-numbers="true" :errors="getEdadErrors" @input="handleEdadInput" />
        <FormSelect v-model="formData.gender" label="Sexo" placeholder="Seleccione el sexo" :required="true" :options="sexoOptions" :error="getSexoError" />
      </div>

      <EntityList v-model="formData.entity" label="Entidad" placeholder="Seleciona la entidad" :required="true" :auto-load="true" :errors="entidadErrors" :key="entityListKey" @entity-selected="onEntitySelected" />
      <FormSelect v-model="formData.careType" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" :error="getTipoAtencionError" />
      <FormTextarea v-model="formData.observations" label="Observaciones del paciente" placeholder="Observaciones adicionales del paciente" :rows="3" :max-length="500" />

      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton @click="handleClearForm" :disabled="isLoading" />
        <SaveButton text="Guardar Paciente" @click="handleSaveClick" :disabled="isLoading" :loading="isLoading" />
      </div>

      <div ref="notificationContainer">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && createdPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPatient.nombre }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Documento de identidad:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPatient.cedula || 'NO DISPONIBLE' }}</span>
                  </p>
                </div>
                
                <div class="space-y-3 text-sm">
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Edad:</span>
                    <span class="text-gray-800 font-semibold">{{ createdPatient.edad }} años</span>
                  </div>
                  
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Sexo:</span>
                    <span class="text-gray-800 font-semibold">{{ createdPatient.sexo }}</span>
                  </div>
                  
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Entidad:</span>
                    <span class="text-gray-800 font-semibold text-right max-w-64 truncate">{{ createdPatient.entidad_info?.nombre }}</span>
                  </div>
                  
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500 font-medium">Tipo de Atención:</span>
                    <span class="text-gray-800 font-semibold">{{ createdPatient.tipo_atencion }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>

      <ValidationAlert :visible="validationState.showValidationError && validationErrors.length > 0" :errors="validationErrors" />
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, watch } from 'vue'
import { usePatientForm } from '../../composables/usePatientForm'
import { useNotifications } from '../../composables/useNotifications'
import { usePatientAPI } from '../../composables/usePatientAPI'
import type { PatientData } from '../../types'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { ValidationAlert, Notification } from '@/shared/components/feedback'
import { EntityList } from '@/shared/components/List'

const notificationContainer = ref<HTMLElement | null>(null)
const createdPatient = ref<any>(null)
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const entityListKey = ref(0)

const { formData, validationState, errors, handleCedulaInput, handleNombreInput, handleEdadInput, clearForm, validateForm } = usePatientForm()
const { notification, showNotification, closeNotification } = useNotifications()
const { createPatient, isLoading, clearState } = usePatientAPI()

const sexoOptions = [{ value: 'Masculino', label: 'Masculino' }, { value: 'Femenino', label: 'Femenino' }]
const tipoAtencionOptions = [{ value: 'Ambulatorio', label: 'Ambulatorio' }, { value: 'Hospitalizado', label: 'Hospitalizado' }]

const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  
  const errorsList: string[] = []
  
  // Errores de campos requeridos
  if (!formData.patientCode?.trim()) errorsList.push('Documento de identidad')
  if (!formData.name?.trim()) errorsList.push('Nombre del paciente')
  if (!formData.age?.trim()) errorsList.push('Edad')
  if (!formData.gender) errorsList.push('Sexo')
  if (!formData.entity) errorsList.push('Entidad')
  if (!formData.careType) errorsList.push('Tipo de atención')
  
  // Errores de validación específicos
  if (errors.patientCode.length > 0) errorsList.push(`Documento: ${errors.patientCode[0]}`)
  if (errors.name.length > 0) errorsList.push(`Nombre: ${errors.name[0]}`)
  if (errors.age.length > 0) errorsList.push(`Edad: ${errors.age[0]}`)
  
  return errorsList
})

const getDocumentoErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.patientCode.length > 0) return errors.patientCode
  if (!formData.patientCode?.trim()) return ['El documento de identidad es obligatorio']
  return []
})

const getNombreErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.name.length > 0) return errors.name
  if (!formData.name?.trim()) return ['El nombre del paciente es obligatorio']
  return []
})

const getEdadErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.age.length > 0) return errors.age
  if (!formData.age?.trim()) return ['La edad es obligatoria']
  return []
})

const getSexoError = computed(() => {
  return !validationState.hasAttemptedSubmit ? '' : (!formData.gender ? 'Por favor seleccione el sexo' : '')
})

const getTipoAtencionError = computed(() => {
  return !validationState.hasAttemptedSubmit ? '' : (!formData.careType ? 'Por favor seleccione el tipo de atención' : '')
})

const entidadErrors = computed(() => {
  return !validationState.hasAttemptedSubmit ? [] : (!formData.entity ? ['La entidad es obligatoria'] : [])
})

const onEntitySelected = (entity: { codigo: string; nombre: string } | null) => selectedEntity.value = entity
const handleClearForm = () => { clearForm(); selectedEntity.value = null; entityListKey.value++ }

const handleSaveClick = async () => {
  // Validar formulario
  const isValid = validateForm()
  if (!isValid) { 
    validationState.showValidationError = true
    // No mostrar notificación aquí, solo mostrar ValidationAlert
    return 
  }
  
  validationState.showValidationError = false
  clearState()

  try {
    const patientData: PatientData = {
      patientCode: formData.patientCode,
      name: formData.name,
      gender: formData.gender,
      age: formData.age,
      entity: selectedEntity.value?.nombre || formData.entity,
      entityCode: selectedEntity.value?.codigo,
      careType: formData.careType,
      observations: formData.observations
    }
    
    const result = await createPatient(patientData)
    if (result.success && result.patient) {
      createdPatient.value = result.patient
      showNotification('success', '¡Paciente Registrado Exitosamente!', '', 15000)
      emit('patient-saved', patientData)
      // Notificar al dashboard para refrescar métricas
      try { window.dispatchEvent(new CustomEvent('patient-created')) } catch {}
      clearForm()
      selectedEntity.value = null
      entityListKey.value++
    } else {
      // Manejar errores específicos del API
      if (result.message?.toLowerCase().includes('duplicad') || 
          result.message?.toLowerCase().includes('ya existe') || 
          result.message?.toLowerCase().includes('repetid')) {
        showNotification('error', 'Documento Duplicado', 'Ya existe un paciente con este documento de identidad. Por favor, verifique el número e intente con otro.', 0)
      } else {
        throw new Error(result.message || 'Error desconocido al crear el paciente')
      }
    }
  } catch (error: any) {
    let errorMessage = 'No se pudo guardar el paciente. Por favor, inténtelo nuevamente.'
    
    // Manejar errores de conexión
    if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') {
      errorMessage = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    }
    // Manejar errores de validación del backend
    else if (error.response?.data?.detail) {
      if (Array.isArray(error.response.data.detail)) {
        errorMessage = error.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ')
      } else {
        errorMessage = String(error.response.data.detail)
      }
    } 
    // Manejar errores de duplicado
    else if (error.message?.toLowerCase().includes('duplicad') || 
             error.message?.toLowerCase().includes('ya existe') || 
             error.message?.toLowerCase().includes('repetid')) {
      errorMessage = 'Ya existe un paciente con este documento de identidad. Por favor, verifique el número e intente con otro.'
    }
    // Manejar otros errores
    else if (error.response?.data?.message) {
      errorMessage = String(error.response.data.message)
    } else if (error.message) {
      errorMessage = String(error.message)
    } else if (typeof error === 'string') {
      errorMessage = error
    }
    
    showNotification('error', 'Error al Guardar Paciente', errorMessage, 0)
  }
}

watch(() => notification.visible, (newValue) => {
  if (newValue && notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
})

const emit = defineEmits<{ 'patient-saved': [patient: PatientData] }>()
</script>
