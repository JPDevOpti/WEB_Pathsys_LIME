<template>
  <!-- Edit patient: search by ID, edit fields, confirm update -->
  <div class="space-y-4">
    <form class="space-y-4" @submit.prevent="onSubmit">
      <!-- Search block (hidden when editing via case code prop) -->
      <div v-if="!caseCodeProp" class="bg-gray-50 rounded-lg border border-gray-200 px-4 py-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <UserSearchIcon class="w-4 h-4 mr-2 text-gray-500" />
          Buscar paciente para editar
        </h3>
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <FormInputField v-model="searchPatientCedula" placeholder="Ingrese documento de identidad" :required="true" :max-length="12" inputmode="numeric" :disabled="isSearching" @update:model-value="handleCedulaInput" @keydown.enter.prevent="searchPatient" />
          </div>
          <div class="flex gap-2 sm:gap-3">
            <SearchButton text="Buscar" loading-text="Buscando..." :loading="isSearching" @click="searchPatient" size="md" variant="primary" />
            <ClearButton v-if="patientFound" text="Limpiar" @click="onReset" />
          </div>
        </div>
        <!-- Search error -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-sm text-red-600">{{ searchError }}</p>
          </div>
        </div>
        <!-- Found banner -->
        <div v-if="patientFound" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Paciente encontrado y cargado</h4>
          </div>
        </div>
      </div>

      <!-- Helper when nothing loaded -->
      <div v-if="!patientFound && !notification.visible" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center space-y-3">
          <UserSearchIcon class="w-12 h-12 text-blue-400" />
          <h3 class="text-lg font-medium text-blue-800">Busque un paciente para editar</h3>
          <p class="text-blue-600 text-sm">Ingrese el documento de identidad del paciente para comenzar a editar</p>
        </div>
      </div>

      <!-- Edit form -->
      <div v-if="patientFound" class="space-y-6">
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInputField v-model="form.name" label="Nombre completo" placeholder="Ingrese el nombre del paciente" required :errors="getNombreErrors" :only-letters="true" />
          <FormInputField v-model="form.patientCode" label="Documento de identidad" placeholder="Documento del paciente" :required="true" :max-length="12" inputmode="numeric" :only-numbers="true" :errors="getDocumentoErrors" />
        </div>
        
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInputField v-model="form.age" type="number" label="Edad" placeholder="Ingrese la edad" required :errors="getEdadErrors" :only-numbers="true" />
          <FormSelect v-model="form.gender" :options="sexoOptions" label="Sexo" placeholder="Seleccione sexo" required :error="getSexoError" />
          <FormSelect v-model="form.careType" :options="tipoAtencionOptions" label="Tipo de atención" placeholder="Seleccione tipo de atención" required :error="getTipoAtencionError" />
          <EntityList v-model="form.entityCode" label="Entidad" placeholder="Seleciona la entidad" :required="true" :auto-load="true" :errors="entidadErrors" @entity-selected="onEntitySelected" />
        </div>
        <FormTextarea v-model="form.observations" label="Observaciones" placeholder="Observaciones del paciente" :rows="3" :max-length="500" />
        <!-- Actions -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton text="Guardar Cambios" @click="onSubmit" :disabled="isLoading" :loading="isLoading" />
        </div>
        <!-- Global validation -->
        <ValidationAlert :visible="validationState.showValidationError && validationErrors.length > 0" :errors="validationErrors" />
      </div>

      <!-- Success notification -->
      <div ref="notificationContainer" v-if="notification.visible">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && updatedPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedPatient.name || updatedPatient.nombre || 'Paciente' }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Documento de identidad:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedPatient.patient_code || updatedPatient.paciente_code || updatedPatient.cedula || 'N/A' }}</span>
                  </p>
                </div>
                <div class="space-y-3 text-sm">
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Edad:</span>
                    <span class="text-gray-800 font-semibold">{{ updatedPatient.age || updatedPatient.edad || 'N/A' }} años</span>
                  </div>
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Sexo:</span>
                    <span class="text-gray-800 font-semibold">{{ updatedPatient.gender || updatedPatient.sexo || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between py-2 border-b border-gray-100">
                    <span class="text-gray-500 font-medium">Entidad:</span>
                    <span class="text-gray-800 font-semibold text-right max-w-64 truncate">{{ updatedPatient.entity_info?.name || updatedPatient.entidad_info?.nombre || 'N/A' }}</span>
                  </div>
                  <div class="flex justify-between py-2">
                    <span class="text-gray-500 font-medium">Tipo de Atención:</span>
                    <span class="text-gray-800 font-semibold">{{ updatedPatient.care_type || updatedPatient.tipo_atencion || 'N/A' }}</span>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>
    </form>
  </div>
</template>

<script setup lang="ts">
// Edit patient form: load by case or document, normalize fields, submit updates
import { reactive, ref, computed, watch } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton } from '@/shared/components/buttons'
import { useNotifications } from '../../composables'
import casesApiService from '../../services/casesApi.service'
import patientsApiService from '../../services/patientsApi.service'
import { EntityList } from '@/shared/components/List'
import Notification from '@/shared/components/feedback/Notification.vue'
import { ValidationAlert } from '@/shared/components/feedback'
import { UserSearchIcon } from '@/assets/icons'
import type { PatientData } from '../../types'

interface Props { caseCodeProp?: string }
interface Emits { (e: 'patient-updated', patient: PatientData): void }

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { notification, showNotification, closeNotification } = useNotifications()

const isLoading = ref(false)
const originalData = ref<PatientData | null>(null)
const notificationContainer = ref<HTMLElement | null>(null)
const updatedPatient = ref<any>(null)
const searchPatientCedula = ref('')
const isSearching = ref(false)
const searchError = ref('')
const patientFound = ref(false)
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)

const form = reactive<any>({
  patientCode: '', name: '', gender: '', age: '', entity: '', entityCode: '', careType: '', observations: ''
})

const sexoOptions = [{ value: 'masculino', label: 'Masculino' }, { value: 'femenino', label: 'Femenino' }]
const tipoAtencionOptions = [{ value: 'ambulatorio', label: 'Ambulatorio' }, { value: 'hospitalizado', label: 'Hospitalizado' }]

// Mirror validation UX from NewPatient.vue
const validationState = reactive({ hasAttemptedSubmit: false, showValidationError: false })
const isFormValid = computed(() => form.name.trim() !== '' && form.gender !== '' && form.age.trim() !== '' && form.entityCode && form.careType !== '')
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const list: string[] = []
  if (!form.patientCode?.trim()) list.push('Documento de identidad')
  if (!form.name?.trim()) list.push('Nombre del paciente')
  if (!form.age?.trim()) list.push('Edad')
  if (!form.gender) list.push('Sexo')
  if (!form.entityCode) list.push('Entidad')
  if (!form.careType) list.push('Tipo de atención')
  if (getDocumentoErrors.value.length > 0) list.push(`Documento: ${getDocumentoErrors.value[0]}`)
  if (getNombreErrors.value.length > 0) list.push(`Nombre: ${getNombreErrors.value[0]}`)
  if (getEdadErrors.value.length > 0) list.push(`Edad: ${getEdadErrors.value[0]}`)
  return list
})
const getDocumentoErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (!/^[0-9]{6,12}$/.test(form.patientCode) ? ['La cédula debe tener entre 6 y 12 dígitos y solo números'] : []))
const getNombreErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (form.name.trim().length < 2 ? ['El nombre del paciente es obligatorio'] : []))
const getEdadErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (!/^[0-9]+$/.test(form.age) || parseInt(form.age) < 0 || parseInt(form.age) > 150 ? ['La edad debe ser un número válido entre 0 y 150'] : []))
const getSexoError = computed(() => !validationState.hasAttemptedSubmit ? '' : (!form.gender ? 'Por favor seleccione el sexo' : ''))
const getTipoAtencionError = computed(() => !validationState.hasAttemptedSubmit ? '' : (!form.careType ? 'Por favor seleccione el tipo de atención' : ''))
const entidadErrors = computed(() => !validationState.hasAttemptedSubmit ? [] : (!form.entityCode ? ['La entidad es obligatoria'] : []))


const mapApiResponseToPatientData = (patient: any): any => ({
  patientCode: patient.cedula || patient.paciente_code || patient.patient_code || '',
  name: patient.nombre || patient.name || '',
  gender: patient.sexo === 'Masculino' ? 'masculino' : patient.sexo === 'Femenino' ? 'femenino' : (patient.sexo || ''),
  age: String(patient.edad || patient.age || ''),
  entity: patient.entidad_info?.nombre || patient.entity_info?.name || '',
  entityCode: patient.entidad_info?.id || patient.entity_info?.id || '',
  careType: patient.tipo_atencion === 'Ambulatorio' ? 'ambulatorio' : patient.tipo_atencion === 'Hospitalizado' ? 'hospitalizado' : (patient.tipo_atencion || ''),
  observations: patient.observaciones || patient.observations || ''
})

// Keep selection state in sync with patient entity
const updateSelectedEntity = (patient: any) => {
  const entityInfo = patient.entidad_info || patient.entity_info
  if (entityInfo) {
    selectedEntity.value = { codigo: entityInfo.id, nombre: entityInfo.nombre || entityInfo.name }
    form.entityCode = entityInfo.id
  } else {
    selectedEntity.value = null
    form.entityCode = undefined
  }
}

const resetFormData = () => {
  Object.assign(form, { patientCode: '', name: '', gender: '', age: '', entity: '', entityCode: '', careType: '', observations: '' })
  searchPatientCedula.value = ''
  searchError.value = ''
  patientFound.value = false
  selectedEntity.value = null
  originalData.value = null
}

// Load patient data using case code prop
const loadPatientData = async () => {
  if (!props.caseCodeProp) return
  isLoading.value = true
  try {
    const caseInfo = await casesApiService.getCaseByCode(props.caseCodeProp)
    const ci: any = caseInfo as any
    const pacienteCode = ci?.patient_info?.patient_code || 
                        ci?.paciente?.paciente_code || 
                        ci?.paciente?.patient_code ||
                        ci?.patient_info?.paciente_code
    if (!pacienteCode) {
      throw new Error('El caso no contiene código de paciente')
    }
    const patient = await patientsApiService.getPatientByCedula(pacienteCode)
    if (!patient) throw new Error('Paciente no encontrado en la colección de pacientes')
    const mapped = mapApiResponseToPatientData(patient)
    Object.assign(form, mapped)
    originalData.value = { ...mapped }
    updateSelectedEntity(patient)
    patientFound.value = true
  } catch (error: any) {
    showNotification('error', 'Error', error.message || 'Error al cargar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

// Validate and submit update payload
const onSubmit = async () => {
  validationState.hasAttemptedSubmit = true
  if (!isFormValid.value) { validationState.showValidationError = true; return }
  
  const originalPatientCode = (originalData.value as any)?.patientCode || searchPatientCedula.value
  if (!originalPatientCode) {
    showNotification('error', 'Error', 'Debe buscar un paciente primero para poder editar sus datos')
    return
  }

  isLoading.value = true
  try {
    if (selectedEntity.value) Object.assign(form, { entityCode: selectedEntity.value.codigo, entity: selectedEntity.value.nombre })

    const codeChanged = form.patientCode.trim() !== originalPatientCode
    let updatedPatientResponse: any

    if (codeChanged) {
      // updatedPatientResponse = await patientsApiService.changePatientCode(originalPatientCode, form.patientCode.trim())
      showNotification('success', '¡Código de Paciente Actualizado!', 'El código del paciente ha sido cambiado exitosamente', 5000)
    } else {
      const patientUpdateData = {
        name: form.name.trim(),
        age: parseInt(form.age),
        gender: form.gender === 'masculino' ? 'Masculino' : form.gender === 'femenino' ? 'Femenino' : form.gender,
        entity_info: { id: form.entityCode || '', name: form.entity.trim() },
        care_type: form.careType === 'ambulatorio' ? 'Ambulatorio' : form.careType === 'hospitalizado' ? 'Hospitalizado' : form.careType,
        observations: form.observations.trim() || null
      }
      
      if (!patientUpdateData.name || !patientUpdateData.entity_info.name) {
        throw new Error('El nombre del paciente y la entidad son obligatorios')
      }
      
      if (patientUpdateData.age <= 0 || patientUpdateData.age > 150) {
        throw new Error('La edad debe estar entre 1 y 150 años')
      }
      
      if (!patientUpdateData.gender || !patientUpdateData.care_type) {
        throw new Error('El sexo y tipo de atención son obligatorios')
      }
      
      updatedPatientResponse = await patientsApiService.updatePatient(originalPatientCode, patientUpdateData as any)
      showNotification('success', '¡Paciente Actualizado Exitosamente!', '', 0)
    }
    
    const mappedUpdatedData = mapApiResponseToPatientData(updatedPatientResponse)
    originalData.value = { ...mappedUpdatedData }
    updatedPatient.value = updatedPatientResponse
    emit('patient-updated', mappedUpdatedData)
    if (!codeChanged) resetFormData()
  } catch (error: any) {
    showNotification('error', 'Error de Validación', error.message || 'Error al actualizar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

// Reset form and clear success toast
const onReset = () => {
  closeNotification()
  resetFormData()
  updatedPatient.value = null
}

// Sanitize numeric input and clear previous results
const handleCedulaInput = (value: string) => {
  let cleanValue = value.replace(/\D/g, '')
  if (cleanValue.length > 12) cleanValue = cleanValue.substring(0, 12)
  searchPatientCedula.value = cleanValue
  searchError.value = ''
  patientFound.value = false
}

// Fetch patient by document and populate form
const searchPatient = async () => {
  if (!searchPatientCedula.value.trim()) {
    searchError.value = 'Por favor ingrese un documento de identidad'
    return
  }
  if (searchPatientCedula.value.length < 6) {
    searchError.value = 'El documento de identidad debe tener al menos 6 dígitos'
    return
  }

  isSearching.value = true
  searchError.value = ''
  patientFound.value = false

  try {
    const patient = await patientsApiService.getPatientByCedula(searchPatientCedula.value)
    
    if (patient) {
      const mappedPatientData = mapApiResponseToPatientData(patient)
      patientFound.value = true
      Object.assign(form, mappedPatientData)
      originalData.value = { ...mappedPatientData }
      updateSelectedEntity(patient)
      searchPatientCedula.value = (mappedPatientData as any).patientCode
    } else {
      searchError.value = `No se encontró un paciente con el código ${searchPatientCedula.value}`
      patientFound.value = false
    }
  } catch (error: any) {
    if (error.message?.includes('ERR_CONNECTION_REFUSED') || error.code === 'ERR_NETWORK') {
      searchError.value = 'Error de conexión: El servidor no está disponible. Verifique que el backend esté ejecutándose.'
    } else if (error.message?.includes('404') || error.message?.includes('No encontrado')) {
      searchError.value = `No se encontró un paciente con el código ${searchPatientCedula.value}`
    } else {
      searchError.value = error.message || 'Error al buscar el paciente. Verifique la cédula e intente nuevamente.'
    }
    patientFound.value = false
  } finally {
    isSearching.value = false
  }
}

// Normalize entity selection from list component
const onEntitySelected = (entity: any | null) => {
  if (entity && (entity.codigo || entity.id)) {
    const codigo = entity.codigo || entity.id
    const nombre = entity.nombre || entity.name || ''
    selectedEntity.value = { codigo, nombre }
    form.entity = nombre
    form.entityCode = codigo
  } else {
    selectedEntity.value = null
    form.entity = ''
    form.entityCode = undefined
  }
}

// Load by prop immediately; scroll to notification when visible
watch(() => props.caseCodeProp, (newCode) => { if (newCode) loadPatientData() }, { immediate: true })
watch(() => notification.visible, (newValue) => { if (newValue && notificationContainer.value) notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' }) })
</script>