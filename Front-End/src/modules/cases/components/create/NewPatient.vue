<template>
  <!-- Register a new patient -->
  <ComponentCard title="Ingresar un nuevo paciente al sistema" description="Complete la información del paciente para ingresarlo al sistema.">
    <template #icon>
      <NewUserIcon class="w-5 h-5 mr-2" />
    </template>

    <div class="space-y-6">
      <!-- Basic identity fields -->
      <FormInputField v-model="formData.patientCode" label="Documento de identidad" placeholder="Ejemplo: 12345678" :required="true" :max-length="12" inputmode="numeric" :only-numbers="true" :errors="getDocumentoErrors" @input="handleCedulaInput" />
      <FormInputField v-model="formData.name" label="Nombre del Paciente" placeholder="Ejemplo: Juan Perez" :required="true" :max-length="200" :only-letters="true" :errors="getNombreErrors" @input="handleNombreInput" />
      
      <!-- Demographics -->
      <div class="grid grid-cols-1 md:grid-cols-2 gap-6">
        <FormInputField v-model="formData.age" label="Edad" placeholder="Edad en años" :required="true" :max-length="3" inputmode="numeric" :only-numbers="true" :errors="getEdadErrors" @input="handleEdadInput" />
        <FormSelect v-model="formData.gender" label="Sexo" placeholder="Seleccione el sexo" :required="true" :options="sexoOptions" :error="getSexoError" />
      </div>

      <!-- Entity and care type -->
      <EntityList v-model="formData.entity" label="Entidad" placeholder="Seleciona la entidad" :required="true" :auto-load="true" :errors="entidadErrors" :key="entityListKey" @entity-selected="onEntitySelected" />
      <FormSelect v-model="formData.careType" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" :error="getTipoAtencionError" />
      
      <!-- Notes -->
      <FormTextarea v-model="formData.observations" label="Observaciones del paciente" placeholder="Observaciones adicionales del paciente" :rows="3" :max-length="500" />

      <!-- Actions -->
      <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
        <ClearButton @click="handleClearForm" :disabled="isLoading" />
        <SaveButton text="Guardar Paciente" @click="handleSaveClick" :disabled="isLoading" :loading="isLoading" />
      </div>

      <!-- Inline notification with success summary -->
      <div ref="notificationContainer">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && createdPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Header -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ createdPatient.nombre }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Documento de identidad:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ createdPatient.cedula || 'NO DISPONIBLE' }}</span>
                  </p>
                </div>
                
                <!-- Key fields -->
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

      <!-- Global validation -->
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
import { NewUserIcon } from '@/assets/icons'

// UI refs/state
const notificationContainer = ref<HTMLElement | null>(null)
const createdPatient = ref<any>(null)
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const entityListKey = ref(0)

// Composables
const { formData, validationState, errors, handleCedulaInput, handleNombreInput, handleEdadInput, clearForm, validateForm } = usePatientForm()
const { notification, showNotification, closeNotification } = useNotifications()
const { createPatient, isLoading, clearState } = usePatientAPI()

// Select options
const sexoOptions = [{ value: 'Masculino', label: 'Masculino' }, { value: 'Femenino', label: 'Femenino' }]
const tipoAtencionOptions = [{ value: 'Ambulatorio', label: 'Ambulatorio' }, { value: 'Hospitalizado', label: 'Hospitalizado' }]

// Aggregate validation messages for banner (avoid duplicates with field errors)
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const list: string[] = []
  // Prefer specific field errors when present, else show required label
  if (errors.patientCode.length > 0) list.push(`Documento: ${errors.patientCode[0]}`)
  else if (!formData.patientCode?.trim()) list.push('Documento de identidad')

  if (errors.name.length > 0) list.push(`Nombre: ${errors.name[0]}`)
  else if (!formData.name?.trim()) list.push('Nombre del paciente')

  if (errors.age.length > 0) list.push(`Edad: ${errors.age[0]}`)
  else if (!formData.age?.trim()) list.push('Edad')

  if (!formData.gender) list.push('Sexo')
  if (!formData.entity) list.push('Entidad')
  if (!formData.careType) list.push('Tipo de atención')
  return list
})

// Field-level validation helpers
const getDocumentoErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (errors.patientCode.length > 0 ? errors.patientCode : (!formData.patientCode?.trim() ? ['El documento de identidad es obligatorio'] : [])))
const getNombreErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (errors.name.length > 0 ? errors.name : (!formData.name?.trim() ? ['El nombre del paciente es obligatorio'] : [])))
const getEdadErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (errors.age.length > 0 ? errors.age : (!formData.age?.trim() ? ['La edad es obligatoria'] : [])))
const getSexoError = computed(() => !validationState.hasAttemptedSubmit ? '' : (!formData.gender ? 'Por favor seleccione el sexo' : ''))
const getTipoAtencionError = computed(() => !validationState.hasAttemptedSubmit ? '' : (!formData.careType ? 'Por favor seleccione el tipo de atención' : ''))
const entidadErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (!formData.entity ? ['La entidad es obligatoria'] : []))

// Entity selected from list (normalize to expected shape)
const onEntitySelected = (entity: any) => {
  if (!entity) { selectedEntity.value = null; return }
  selectedEntity.value = { codigo: entity.codigo || entity.code || entity.id || '', nombre: entity.nombre || entity.name || '' }
}

// Reset inputs and entity selector
const handleClearForm = () => { clearForm(); selectedEntity.value = null; entityListKey.value++ }

// Create patient flow
const handleSaveClick = async () => {
  const isValid = validateForm()
  if (!isValid) { validationState.showValidationError = true; return }
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
      try { window.dispatchEvent(new CustomEvent('patient-created')) } catch {}
      clearForm(); selectedEntity.value = null; entityListKey.value++
    } else {
      if (result.message?.toLowerCase().includes('duplicad') || result.message?.toLowerCase().includes('ya existe') || result.message?.toLowerCase().includes('repetid')) {
        showNotification('error', 'Documento Duplicado', 'Ya existe un paciente con este documento de identidad. Por favor, verifique el número e intente con otro.', 0)
      } else {
        throw new Error(result.message || 'Error desconocido al crear el paciente')
      }
    }
  } catch (error: any) {
    let errorMessage = 'No se pudo guardar el paciente. Por favor, inténtelo nuevamente.'
    if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') errorMessage = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    else if (error.response?.data?.detail) errorMessage = Array.isArray(error.response.data.detail) ? error.response.data.detail.map((err: any) => err.msg || err.message || String(err)).join(', ') : String(error.response.data.detail)
    else if (error.message?.toLowerCase().includes('duplicad') || error.message?.toLowerCase().includes('ya existe') || error.message?.toLowerCase().includes('repetid')) errorMessage = 'Ya existe un paciente con este documento de identidad. Por favor, verifique el número e intente con otro.'
    else if (error.response?.data?.message) errorMessage = String(error.response.data.message)
    else if (error.message) errorMessage = String(error.message)
    else if (typeof error === 'string') errorMessage = error
    showNotification('error', 'Error al Guardar Paciente', errorMessage, 0)
  }
}

// Smooth-scroll to notification when visible
watch(() => notification.visible, (v) => { if (v && notificationContainer.value) notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' }) })

// Emit for parent listeners
const emit = defineEmits<{ 'patient-saved': [patient: PatientData] }>()
</script>
