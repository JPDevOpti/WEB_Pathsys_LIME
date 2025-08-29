<template>
  <div class="space-y-4">
    <form class="space-y-4" @submit.prevent="onSubmit">
      <!-- Sección de búsqueda de paciente (solo visible cuando no hay caseCodeProp) -->
      <div v-if="!caseCodeProp" class="bg-gray-50 rounded-lg border border-gray-200 px-4 py-4">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          Buscar Paciente para Editar
        </h3>
        <!-- Campo de búsqueda por cédula -->
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <FormInputField v-model="searchPatientCedula" placeholder="Ingrese documento de identidad" :required="true" :max-length="10" inputmode="numeric" :disabled="isSearching" @update:model-value="handleCedulaInput" @keydown.enter.prevent="searchPatient" />
          </div>
          <div class="flex gap-2 sm:gap-3">
            <SearchButton text="Buscar" loading-text="Buscando..." :loading="isSearching" @click="searchPatient" size="md" variant="primary" />
            <ClearButton v-if="patientFound" text="Limpiar" @click="onReset" />
          </div>
        </div>
        <!-- Mensaje de error en búsqueda -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <p class="text-sm text-red-600">{{ searchError }}</p>
          </div>
        </div>
        <!-- Información del paciente encontrado -->
        <div v-if="patientFound && foundPatientInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Paciente Encontrado y Cargado</h4>
          </div>
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
            <div><span class="font-medium text-green-700">Nombre:</span><p class="text-green-800 break-words">{{ foundPatientInfo.nombrePaciente }}</p></div>
            <div><span class="font-medium text-green-700">Identificación:</span><p class="text-green-800 font-mono">{{ foundPatientInfo.pacienteCode }}</p></div>
            <div><span class="font-medium text-green-700">Edad:</span><p class="text-green-800">{{ foundPatientInfo.edad }} años</p></div>
            <div><span class="font-medium text-green-700">Sexo:</span><p class="text-green-800">{{ foundPatientInfo.sexo }}</p></div>
            <div><span class="font-medium text-green-700">Entidad:</span><p class="text-green-800 break-words">{{ foundPatientInfo.entidad }}</p></div>
            <div><span class="font-medium text-green-700">Tipo de Atención:</span><p class="text-green-800 break-words">{{ foundPatientInfo.tipoAtencion }}</p></div>
          </div>
        </div>
      </div>

      <!-- Mensaje instructivo cuando no hay paciente seleccionado -->
      <div v-if="!patientFound && !notification.visible" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center space-y-3">
          <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <h3 class="text-lg font-medium text-blue-800">Busque un paciente para editar</h3>
          <p class="text-blue-600 text-sm">Ingrese el documento de identidad del paciente en el campo de búsqueda arriba para comenzar a editar</p>
        </div>
      </div>

      <!-- Formulario de edición (visible solo cuando se encuentra un paciente) -->
      <div v-if="patientFound" class="space-y-6">
        <FormInputField v-model="form.nombrePaciente" label="Nombre completo" placeholder="Ingrese el nombre del paciente" required />
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInputField v-model="form.edad" type="number" label="Edad" placeholder="Ingrese la edad" required />
          <FormSelect v-model="form.sexo" :options="sexoOptions" label="Sexo" placeholder="Seleccione sexo" required />
          <FormSelect v-model="form.tipoAtencion" :options="tipoAtencionOptions" label="Tipo de atención" placeholder="Seleccione tipo de atención" required />
          <EntityList v-model="form.entidadCodigo" label="Entidad" placeholder="Buscar entidad..." :required="true" :auto-load="true" :error="getEntidadError" @entity-selected="onEntitySelected" />
        </div>
        <FormTextarea v-model="form.observaciones" label="Observaciones" placeholder="Observaciones del paciente" :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional sobre el paciente" />
        <!-- Botones de acción -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton text="Guardar Cambios" @click="onSubmit" :disabled="isLoading || !isFormValid" :loading="isLoading" />
        </div>
      </div>

      <!-- Notificación de resultado -->
      <div ref="notificationContainer" v-if="notification.visible">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && updatedPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedPatient.nombre }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Identificación:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedPatient.paciente_code || updatedPatient.cedula }}</span>
                  </p>
                </div>
                <div class="space-y-4">
                  <div class="grid grid-cols-3 gap-6 text-sm">
                    <div><span class="text-gray-500 font-medium block mb-1">Edad:</span><p class="text-gray-800 font-semibold">{{ updatedPatient.edad }}</p></div>
                    <div><span class="text-gray-500 font-medium block mb-1">Sexo:</span><p class="text-gray-800 font-semibold">{{ updatedPatient.sexo }}</p></div>
                    <div><span class="text-gray-500 font-medium block mb-1">Tipo de Atención:</span><p class="text-gray-800 font-semibold">{{ updatedPatient.tipo_atencion }}</p></div>
                  </div>
                  <div class="text-sm">
                    <span class="text-gray-500 font-medium block mb-1">Entidad:</span>
                    <p class="text-gray-800 font-semibold break-words">{{ updatedPatient.entidad_info?.nombre }}</p>
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
import { reactive, ref, computed, watch, onMounted, nextTick } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton } from '@/shared/components/buttons'
import { useNotifications } from '../composables'
import casesApiService from '../services/casesApi.service'
import patientsApiService from '../services/patientsApi.service'
import { EntityList } from '@/shared/components/List'
import Notification from '@/shared/components/feedback/Notification.vue'
import type { PatientData } from '../types'

// Props y emits del componente
interface Props { caseCodeProp?: string }
interface Emits { (e: 'patient-updated', patient: PatientData): void }

const props = defineProps<Props>()
const emit = defineEmits<Emits>()
const { notification, showNotification, closeNotification } = useNotifications()

// Estados reactivos del componente
const isLoading = ref(false)
const originalData = ref<PatientData | null>(null)
const notificationContainer = ref<HTMLElement | null>(null)
const updatedPatient = ref<any>(null)
const searchPatientCedula = ref('')
const isSearching = ref(false)
const searchError = ref('')
const patientFound = ref(false)
const foundPatientInfo = ref<PatientData | null>(null)
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)

// Formulario reactivo con datos del paciente
const form = reactive<PatientData>({
  pacienteCode: '', nombrePaciente: '', sexo: '', edad: '', entidad: '', entidadCodigo: '', tipoAtencion: '', observaciones: ''
})

// Opciones para los campos select
const sexoOptions = [{ value: 'masculino', label: 'Masculino' }, { value: 'femenino', label: 'Femenino' }]
const tipoAtencionOptions = [{ value: 'ambulatorio', label: 'Ambulatorio' }, { value: 'hospitalizado', label: 'Hospitalizado' }]

// Validación del formulario
const isFormValid = computed(() => (
  form.nombrePaciente.trim() !== '' && form.sexo !== '' && form.edad.trim() !== '' && 
  form.entidadCodigo && form.tipoAtencion !== ''
))

const getEntidadError = computed(() => !form.entidadCodigo ? 'La entidad es obligatoria' : '')

// Función para hacer scroll a la notificación
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// Mapea la respuesta de la API al formato PatientData
const mapApiResponseToPatientData = (patient: any): PatientData => ({
  pacienteCode: patient.paciente_code || patient.cedula,
  nombrePaciente: patient.nombre,
  sexo: (patient.sexo?.toLowerCase() === 'masculino' ? 'masculino' : 'femenino'),
  edad: String(patient.edad),
  entidad: patient.entidad_info?.nombre || '',
  entidadCodigo: patient.entidad_info?.id || '',
  tipoAtencion: (patient.tipo_atencion?.toLowerCase() === 'ambulatorio' ? 'ambulatorio' : 'hospitalizado'),
  observaciones: patient.observaciones || ''
})

// Actualiza la entidad seleccionada del paciente
const updateSelectedEntity = (patient: any) => {
  if (patient.entidad_info) {
    selectedEntity.value = { codigo: patient.entidad_info.id, nombre: patient.entidad_info.nombre }
    form.entidadCodigo = patient.entidad_info.id
  } else {
    selectedEntity.value = null
    form.entidadCodigo = undefined
  }
}

// Resetea todos los datos del formulario
const resetFormData = () => {
  Object.assign(form, {
    pacienteCode: '', nombrePaciente: '', sexo: '', edad: '', entidad: '', entidadCodigo: '', tipoAtencion: '', observaciones: ''
  })
  searchPatientCedula.value = ''
  searchError.value = ''
  patientFound.value = false
  foundPatientInfo.value = null
  selectedEntity.value = null
  originalData.value = null
}

// Carga los datos del paciente desde un caso existente
const loadPatientData = async () => {
  if (!props.caseCodeProp) return
  isLoading.value = true
  try {
    const caseInfo = await casesApiService.getCaseByCode(props.caseCodeProp)
    const pacienteCode = caseInfo?.paciente?.paciente_code
    if (!pacienteCode) throw new Error('El caso no contiene código de paciente')
    
    const patient = await patientsApiService.getPatientByCedula(pacienteCode)
    if (!patient) throw new Error('Paciente no encontrado en la colección de pacientes')
    
    const mapped = mapApiResponseToPatientData(patient)
    Object.assign(form, mapped)
    originalData.value = { ...mapped }
    updateSelectedEntity(patient)
    patientFound.value = true
    foundPatientInfo.value = mapped
  } catch (error: any) {
    showNotification('error', 'Error', error.message || 'Error al cargar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

// Maneja el envío del formulario para actualizar el paciente
const onSubmit = async () => {
  if (!isFormValid.value) return
  
  const pacienteCodeToUse = form.pacienteCode || searchPatientCedula.value
  if (!pacienteCodeToUse) {
    showNotification('error', 'Error', 'Debe buscar un paciente primero para poder editar sus datos')
    return
  }

  isLoading.value = true
  try {
    // Validación de datos antes de enviar
    const validation = patientsApiService.validatePatientData(form as PatientData)
    if (!validation.isValid) throw new Error(`Datos inválidos: ${validation.errors.join(', ')}`)

    if (selectedEntity.value) {
      form.entidadCodigo = selectedEntity.value.codigo
      form.entidad = selectedEntity.value.nombre
    }

    // Prepara los datos para la actualización
    const patientUpdateData = {
      nombre: form.nombrePaciente.trim(),
      edad: parseInt(form.edad),
      sexo: form.sexo === 'masculino' ? 'Masculino' : 'Femenino',
      entidad_info: { id: form.entidadCodigo || '', nombre: form.entidad.trim() },
      tipo_atencion: form.tipoAtencion === 'ambulatorio' ? 'Ambulatorio' : 'Hospitalizado',
      observaciones: form.observaciones.trim()
    }
    
    // Validaciones adicionales
    if (!patientUpdateData.nombre || !patientUpdateData.entidad_info.nombre) {
      throw new Error('El nombre del paciente y la entidad son obligatorios')
    }
    
    if (patientUpdateData.edad <= 0 || patientUpdateData.edad > 150) {
      throw new Error('La edad debe estar entre 1 y 150 años')
    }
    
    if (!patientUpdateData.sexo || !patientUpdateData.tipo_atencion) {
      throw new Error('El sexo y tipo de atención son obligatorios')
    }
    
    // Actualiza el paciente en la API
    const updatedPatientResponse = await patientsApiService.updatePatient(pacienteCodeToUse, patientUpdateData as any)
    const mappedUpdatedData = mapApiResponseToPatientData(updatedPatientResponse)
    originalData.value = { ...mappedUpdatedData }
    updatedPatient.value = updatedPatientResponse
    emit('patient-updated', mappedUpdatedData)
    showNotification('success', '¡Paciente Actualizado Exitosamente!', '', 0)
    resetFormData()
  } catch (error: any) {
    showNotification('error', 'Error de Validación', error.message || 'Error al actualizar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

// Resetea el formulario y limpia las notificaciones
const onReset = () => {
  closeNotification()
  resetFormData()
  updatedPatient.value = null
}

// Maneja la entrada de la cédula con validación de formato
const handleCedulaInput = (value: string) => {
  let cleanValue = value.replace(/\D/g, '')
  if (cleanValue.length > 10) cleanValue = cleanValue.substring(0, 10)
  searchPatientCedula.value = cleanValue
  searchError.value = ''
  patientFound.value = false
  foundPatientInfo.value = null
}

// Busca un paciente por su cédula
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
      foundPatientInfo.value = mappedPatientData
      patientFound.value = true
      Object.assign(form, mappedPatientData)
      originalData.value = { ...mappedPatientData }
      updateSelectedEntity(patient)
    } else {
      searchError.value = `No se encontró un paciente con el código ${searchPatientCedula.value}`
      patientFound.value = false
      foundPatientInfo.value = null
    }
  } catch (error: any) {
    showNotification('error', 'Error', error.message || 'Error al buscar el paciente. Verifique la cédula e intente nuevamente.')
    patientFound.value = false
    foundPatientInfo.value = null
  } finally {
    isSearching.value = false
  }
}

// Maneja la selección de entidad desde el componente EntityList
const onEntitySelected = (entity: { codigo: string; nombre: string } | null) => {
  selectedEntity.value = entity
  if (entity) {
    form.entidad = entity.nombre
    form.entidadCodigo = entity.codigo
  } else {
    form.entidad = ''
    form.entidadCodigo = undefined
  }
}

// Watchers para cambios en props y notificaciones
watch(() => props.caseCodeProp, (newCode) => { if (newCode) loadPatientData() }, { immediate: true })
watch(() => notification.visible, (newValue) => { if (newValue) scrollToNotification() })

// Carga inicial de datos si hay un caseCodeProp
onMounted(() => { if (props.caseCodeProp) loadPatientData() })
</script>