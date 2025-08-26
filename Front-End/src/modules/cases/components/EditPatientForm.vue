<template>
  <div class="space-y-4">
    <!-- Encabezado interno removido para evitar duplicidad con ComponentCard -->

    <!-- Formulario de edición del paciente -->
    <form class="space-y-4" @submit.prevent="onSubmit">


      <!-- Sección de búsqueda de paciente (siempre visible como bloque secundario) -->
      <div v-if="!caseCodeProp" class="bg-gray-50 rounded-lg border border-gray-200">
        <div class="px-4 pt-4 pb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
            Buscar Paciente para Editar
          </h3>
      
      <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
        <div class="flex-1">
          <FormInputField
            v-model="searchPatientCedula"
            placeholder="Ingrese número de cédula"
            :required="true"
            :max-length="10"
            inputmode="numeric"
            :disabled="isSearching"
            @update:model-value="handleCedulaInput"
            @keydown.enter.prevent="searchPatient"
          />
        </div>
        
        <div class="flex gap-2 sm:gap-3">
          <SearchButton
            text="Buscar"
            loading-text="Buscando..."
            :loading="isSearching"
            @click="searchPatient"
            size="md"
            variant="primary"
          />
          <ClearButton
            v-if="patientFound"
            text="Limpiar"
            @click="onReset"
          />
        </div>
      </div>

      <!-- Mensaje de error de búsqueda -->
      <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
        <div class="flex items-center">
          <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
          </svg>
          <p class="text-sm text-red-600">{{ searchError }}</p>
        </div>
      </div>

      <!-- Información del paciente encontrado y cargado -->
      <div v-if="patientFound && foundPatientInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
        <div class="flex items-center justify-between mb-3">
          <div class="flex items-center">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Paciente Encontrado y Cargado</h4>
          </div>
        </div>
        
        <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
          <div>
            <span class="font-medium text-green-700">Nombre:</span>
            <p class="text-green-800 break-words">{{ foundPatientInfo.nombrePaciente }}</p>
          </div>
          <div>
            <span class="font-medium text-green-700">Cédula:</span>
            <p class="text-green-800 font-mono">{{ foundPatientInfo.numeroCedula }}</p>
          </div>
          <div>
            <span class="font-medium text-green-700">Edad:</span>
            <p class="text-green-800">{{ foundPatientInfo.edad }} años</p>
          </div>
          <div>
            <span class="font-medium text-green-700">Sexo:</span>
            <p class="text-green-800">{{ foundPatientInfo.sexo }}</p>
          </div>
          <div>
            <span class="font-medium text-green-700">Entidad:</span>
            <p class="text-green-800 break-words">{{ foundPatientInfo.entidad }}</p>
          </div>
          <div>
            <span class="font-medium text-green-700">Tipo de Atención:</span>
            <p class="text-green-800 break-words">{{ foundPatientInfo.tipoAtencion }}</p>
          </div>
        </div>
      </div>
      </div>
    </div>

      <!-- Mensaje informativo cuando no hay paciente encontrado -->
      <div v-if="!patientFound && !notification.visible" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center space-y-3">
          <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
          <h3 class="text-lg font-medium text-blue-800">Busque un paciente para editar</h3>
          <p class="text-blue-600 text-sm">Ingrese la cédula del paciente en el campo de búsqueda arriba para comenzar a editar</p>
        </div>
      </div>

      

      <!-- Formulario principal (solo visible cuando se encuentra un paciente) -->
      <div v-if="patientFound" class="space-y-6">
        <!-- Nombre completo (ancho completo) -->
        <FormInputField
          v-model="form.nombrePaciente"
          label="Nombre completo"
          placeholder="Ingrese el nombre del paciente"
          required
        />
        
        <!-- Campos en grid -->
        <div class="grid grid-cols-1 gap-4 md:grid-cols-2">
          <FormInputField
            v-model="form.edad"
            type="number"
            label="Edad"
            placeholder="Ingrese la edad"
            required
          />
          <FormSelect
            v-model="form.sexo"
            :options="sexoOptions"
            label="Sexo"
            placeholder="Seleccione sexo"
            required
          />
          <FormSelect
            v-model="form.tipoAtencion"
            :options="tipoAtencionOptions"
            label="Tipo de atención"
            placeholder="Seleccione tipo de atención"
            required
          />
          <EntityList
            v-model="form.entidadCodigo"
            label="Entidad"
            placeholder="Buscar entidad..."
            :required="true"
            :auto-load="true"
            :error="getEntidadError"
            @entity-selected="onEntitySelected"
          />
        </div>

        <FormTextarea
          v-model="form.observaciones"
          label="Observaciones"
          placeholder="Observaciones del paciente"
          :rows="3"
          :max-length="500"
          :show-counter="true"
          help-text="Información adicional sobre el paciente"
        />

        <!-- Botones de Acción -->
        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton
            @click="onReset"
            :disabled="isLoading"
          />
          
          <SaveButton
            text="Guardar Cambios"
            @click="onSubmit"
            :disabled="isLoading || !isFormValid"
            :loading="isLoading"
          />
        </div>
      </div>

      <!-- Notificación -->
      <div ref="notificationContainer" v-if="notification.visible">
        <Notification
          :visible="notification.visible"
          :type="notification.type"
          :title="notification.title"
          :message="notification.message"
          :inline="true"
          :auto-close="false"
          @close="closeNotification"
        >
          <template v-if="notification.type === 'success' && updatedPatient" #content>
            <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Información principal del paciente -->
                <div class="mb-4 pb-3 border-b border-gray-100">
                  <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedPatient.nombre }}</h3>
                  <p class="text-gray-600">
                    <span class="font-medium">Cédula:</span> 
                    <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedPatient.cedula }}</span>
                  </p>
                </div>
                
                <!-- Detalles del paciente -->
                <div class="space-y-4">
                  <!-- Primera fila: Edad, Sexo, Tipo de Atención -->
                  <div class="grid grid-cols-3 gap-6 text-sm">
                    <div>
                      <span class="text-gray-500 font-medium block mb-1">Edad:</span>
                      <p class="text-gray-800 font-semibold">{{ updatedPatient.nombre }}</p>
                    </div>
                    <div>
                      <span class="text-gray-500 font-medium block mb-1">Sexo:</span>
                      <p class="text-gray-800 font-semibold">{{ updatedPatient.sexo }}</p>
                    </div>
                    <div>
                      <span class="text-gray-500 font-medium block mb-1">Tipo de Atención:</span>
                      <p class="text-gray-800 font-semibold">{{ updatedPatient.tipo_atencion }}</p>
                    </div>
                  </div>
                  
                  <!-- Segunda fila: Entidad -->
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
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/ui/forms'
import { SaveButton, ClearButton, SearchButton } from '@/shared/components/ui/buttons'
import { useNotifications } from '../composables'
import casesApiService from '../services/casesApi.service'
import patientsApiService from '../services/patientsApi.service'
import { EntityList } from '@/shared/components/ui/List'
import Notification from '@/shared/components/ui/feedback/Notification.vue'
import type { PatientData } from '../types'

// ============================================================================
// PROPS Y EMITS
// ============================================================================

interface Props {
  caseCodeProp?: string
}

interface Emits {
  (e: 'patient-updated', patient: PatientData): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// COMPOSABLES
// ============================================================================

const { notification, showNotification, closeNotification } = useNotifications()

// ============================================================================
// ESTADO
// ============================================================================

const isLoading = ref(false)
const originalData = ref<PatientData | null>(null)

// Referencias para la notificación
const notificationContainer = ref<HTMLElement | null>(null)

// Estado del paciente actualizado
const updatedPatient = ref<any>(null)

// Estado para búsqueda de pacientes
const searchPatientCedula = ref('')
const isSearching = ref(false)
const searchError = ref('')
const patientFound = ref(false)
const foundPatientInfo = ref<PatientData | null>(null)
// const showSearchSection = ref(false) // No usado actualmente

// Estado para entidad seleccionada
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)

const form = reactive<PatientData>({
  numeroCedula: '',
  nombrePaciente: '',
  sexo: '',
  edad: '',
  entidad: '',
  entidadCodigo: '',
  tipoAtencion: '',
  observaciones: '',
})

const sexoOptions = [
  { value: 'masculino', label: 'Masculino' },
  { value: 'femenino', label: 'Femenino' }
]

const tipoAtencionOptions = [
  { value: 'ambulatorio', label: 'Ambulatorio' },
  { value: 'hospitalizado', label: 'Hospitalizado' },
]

// ============================================================================
// COMPUTED
// ============================================================================

const isFormValid = computed(() => {
  return (
    form.nombrePaciente.trim() !== '' &&
    form.sexo !== '' &&
    form.edad.trim() !== '' &&
    form.entidadCodigo &&
    form.tipoAtencion !== ''
  )
})

// const hasChanges = computed(() => {
//   if (!originalData.value) return false
//   
//   return JSON.stringify(form) !== JSON.stringify(originalData.value)
// }) // No usado actualmente

/**
 * Error para el campo entidad
 */
const getEntidadError = computed(() => {
  return !form.entidadCodigo ? 'La entidad es obligatoria' : ''
})

// ============================================================================
// FUNCIONES HELPER
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

/**
 * Mapea la respuesta de la API a PatientData del formulario
 */
const mapApiResponseToPatientData = (patient: any): PatientData => {
  return {
    numeroCedula: patient.cedula,
    nombrePaciente: patient.nombre,
    sexo: (patient.sexo?.toLowerCase() === 'masculino' ? 'masculino' : 
           patient.sexo?.toLowerCase() === 'femenino' ? 'femenino' : ''),
    edad: String(patient.edad),
    entidad: patient.entidad_info?.nombre || '',
    entidadCodigo: patient.entidad_info?.id || '',
    tipoAtencion: (patient.tipo_atencion?.toLowerCase() === 'ambulatorio' ? 'ambulatorio' : 
                  patient.tipo_atencion?.toLowerCase() === 'hospitalizado' ? 'hospitalizado' : ''),
    observaciones: patient.observaciones || ''
  }
}

/**
 * Actualiza la entidad seleccionada basada en la información del paciente
 */
const updateSelectedEntity = (patient: any) => {
  if (patient.entidad_info) {
    selectedEntity.value = {
      codigo: patient.entidad_info.id,
      nombre: patient.entidad_info.nombre
    }
    // Asegurar que el formulario tenga el código correcto
    form.entidadCodigo = patient.entidad_info.id
  } else {
    selectedEntity.value = null
    form.entidadCodigo = undefined
  }
}

// ============================================================================
// FUNCIONES
// ============================================================================

/**
 * Carga los datos del paciente asociado al caso
 */
const loadPatientData = async () => {
  if (!props.caseCodeProp) return

  isLoading.value = true
  try {
    // 1) Obtener caso por código para extraer cédula de paciente
    const caseInfo = await casesApiService.getCaseByCode(props.caseCodeProp)
    const cedula = caseInfo?.paciente?.cedula
    if (!cedula) {
      throw new Error('El caso no contiene cédula de paciente')
    }

    // 2) Buscar paciente por cédula en la colección de pacientes
    const patient = await patientsApiService.getPatientByCedula(cedula)
    if (!patient) {
      throw new Error('Paciente no encontrado en la colección de pacientes')
    }

    // 3) Mapear respuesta a PatientData del formulario
    const mapped = mapApiResponseToPatientData(patient)

    Object.assign(form, mapped)
    originalData.value = { ...mapped }

    // Actualizar también la entidad seleccionada
    updateSelectedEntity(patient)
    
    // Marcar que se encontró un paciente para mostrar el formulario
    patientFound.value = true
    foundPatientInfo.value = mapped
  } catch (error: any) {
    console.error('Error al cargar datos del paciente:', error)
    showNotification('error', 'Error', error.message || 'Error al cargar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

/**
 * Envía los cambios del paciente al backend
 */
const onSubmit = async () => {
  // Permitir edición tanto si hay caseCodeProp como si se busca un paciente independientemente
  if (!isFormValid.value) return

  // Validar que hay una cédula disponible (del paciente encontrado o del formulario)
  const cedulaToUse = form.numeroCedula || searchPatientCedula.value
  if (!cedulaToUse) {
    showNotification('error', 'Error', 'Debe buscar un paciente primero para poder editar sus datos')
    return
  }

  isLoading.value = true
  try {
    // Validar datos del paciente antes de enviar
    const validation = patientsApiService.validatePatientData(form as PatientData)
    if (!validation.isValid) {
      throw new Error(`Datos inválidos: ${validation.errors.join(', ')}`)
    }

    // Asegurar que la entidad tenga el código correcto
    if (selectedEntity.value) {
      form.entidadCodigo = selectedEntity.value.codigo
      form.entidad = selectedEntity.value.nombre
    }

    // Llamada a API para actualizar
    const updatedPatientResponse = await patientsApiService.updatePatient(cedulaToUse, form as PatientData)

    // Actualizar datos originales con la respuesta del servidor
    const mappedUpdatedData = mapApiResponseToPatientData(updatedPatientResponse)

    originalData.value = { ...mappedUpdatedData }

    // Guardar información del paciente actualizado para la notificación
    updatedPatient.value = updatedPatientResponse

    // Emitir evento de actualización
    emit('patient-updated', mappedUpdatedData)

    // Mostrar notificación de éxito con detalles (sin auto-cierre)
    showNotification(
      'success',
      '¡Paciente Actualizado Exitosamente!',
      '',
      0
    )

    // Limpiar todos los campos después del guardado exitoso
    clearFormAfterSave()
  } catch (error: any) {
    console.error('Error al actualizar paciente:', error)
    showNotification('error', 'Error', error.message || 'Error al actualizar los datos del paciente')
  } finally {
    isLoading.value = false
  }
}

/**
 * Limpia completamente todos los campos del formulario
 */
const onReset = () => {
  // Cerrar cualquier notificación abierta
  closeNotification()
  
  // Limpiar todos los campos del formulario
  Object.assign(form, {
    numeroCedula: '',
    nombrePaciente: '',
    sexo: '',
    edad: '',
    entidad: '',
    entidadCodigo: '',
    tipoAtencion: '',
    observaciones: '',
  })
  
  // Limpiar estado de búsqueda
  searchPatientCedula.value = ''
  searchError.value = ''
  patientFound.value = false
  foundPatientInfo.value = null
  
  // Limpiar entidad seleccionada
  selectedEntity.value = null
  
  // Resetear datos originales
  originalData.value = null
  
  // Limpiar paciente actualizado
  updatedPatient.value = null
}

/**
 * Limpia los campos del formulario después de guardar exitosamente (sin cerrar notificación)
 */
const clearFormAfterSave = () => {
  // Limpiar todos los campos del formulario
  Object.assign(form, {
    numeroCedula: '',
    nombrePaciente: '',
    sexo: '',
    edad: '',
    entidad: '',
    entidadCodigo: '',
    tipoAtencion: '',
    observaciones: '',
  })
  
  // Limpiar estado de búsqueda
  searchPatientCedula.value = ''
  searchError.value = ''
  patientFound.value = false  // Ocultar el formulario
  foundPatientInfo.value = null
  
  // Limpiar entidad seleccionada
  selectedEntity.value = null
  
  // Resetear datos originales
  originalData.value = null
  
  // NO limpiar updatedPatient.value ni cerrar notificación para que siga mostrando el éxito
}

// ============================================================================
// WATCHERS
// ============================================================================

// Cargar datos cuando cambie el código del caso
watch(
  () => props.caseCodeProp,
  (newCode) => {
    if (newCode) {
      loadPatientData()
    }
  },
  { immediate: true }
)

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
// CICLO DE VIDA
// ============================================================================

onMounted(() => {
  if (props.caseCodeProp) {
    loadPatientData()
  }
})

// ============================================================================
// FUNCIONES DE BÚSQUEDA
// ============================================================================

/**
 * Maneja cambios en la cédula de búsqueda
 */
const handleCedulaInput = (value: string) => {
  let cleanValue = value.replace(/\D/g, '') // Solo números
  
  // Limitar a 10 dígitos
  if (cleanValue.length > 10) {
    cleanValue = cleanValue.substring(0, 10)
  }
  
  searchPatientCedula.value = cleanValue
  searchError.value = ''
  patientFound.value = false
  foundPatientInfo.value = null
}

/**
 * Busca un paciente por cédula
 */
const searchPatient = async () => {
  if (!searchPatientCedula.value.trim()) {
    searchError.value = 'Por favor ingrese un número de cédula'
    return
  }

  if (searchPatientCedula.value.length < 6) {
    searchError.value = 'La cédula debe tener al menos 6 dígitos'
    return
  }

  isSearching.value = true
  searchError.value = ''
  patientFound.value = false

  try {

    
    // Llamada real a la API para buscar paciente
    const patient = await patientsApiService.getPatientByCedula(searchPatientCedula.value)
    
    if (patient) {
      // Mapear respuesta de la API a PatientData del formulario
      const mappedPatientData = mapApiResponseToPatientData(patient)
      
      // Guardar información del paciente encontrado para mostrar
      foundPatientInfo.value = mappedPatientData
      patientFound.value = true
      
      // Cargar automáticamente los datos en el formulario
      Object.assign(form, mappedPatientData)
      originalData.value = { ...mappedPatientData }
      
      // Actualizar entidad seleccionada
      updateSelectedEntity(patient)
    } else {
      searchError.value = `No se encontró un paciente con la cédula ${searchPatientCedula.value}`
      patientFound.value = false
      foundPatientInfo.value = null
    }
  } catch (error: any) {
    console.error('Error al buscar paciente:', error)
    searchError.value = error.message || 'Error al buscar el paciente. Verifique la cédula e intente nuevamente.'
    patientFound.value = false
    foundPatientInfo.value = null
  } finally {
    isSearching.value = false
  }
}

/**
 * Limpia la búsqueda de pacientes y resetea el formulario
 */
const clearSearch = () => {
  // Limpiar estado de búsqueda
  searchPatientCedula.value = ''
  searchError.value = ''
  patientFound.value = false
  foundPatientInfo.value = null
  
  // Resetear formulario a estado inicial
  Object.assign(form, {
    numeroCedula: '',
    nombrePaciente: '',
    sexo: '',
    edad: '',
    entidad: '',
    entidadCodigo: '',
    tipoAtencion: '',
    observaciones: '',
  })
  
  // Limpiar entidad seleccionada
  selectedEntity.value = null
  
  // Resetear datos originales
  originalData.value = null
  
  showNotification('info', 'Información', 'Búsqueda limpiada. Puede realizar una nueva búsqueda')
}

/**
 * Maneja la selección de entidad
 */
const onEntitySelected = (entity: { codigo: string; nombre: string } | null) => {
  selectedEntity.value = entity
  
  // Actualizar el formulario con la entidad seleccionada
  if (entity) {
    form.entidad = entity.nombre
    form.entidadCodigo = entity.codigo
  } else {
    form.entidad = ''
    form.entidadCodigo = undefined
  }
}
</script>