<template>
  <ComponentCard title="Crear nuevo caso" description="Complete la información del caso para ingresarlo al sistema.">
    <template #icon>
      <DocsIcon class="w-5 h-5 mr-2 text-blue-600" />
    </template>
    

    <div class="space-y-6">
      <!-- Sección de verificación del paciente -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <SearchIcon class="w-4 h-4 mr-2 text-gray-500" />
        Buscar paciente
        </h3>
        
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <FormInputField v-model="pacienteCodeBusqueda" placeholder="Ingrese código del paciente" :required="true" :max-length="12" inputmode="numeric" :only-numbers="true" :disabled="patientVerified" @input="handlePacienteCodeInput" />
          </div>
          
          <div class="flex gap-2 sm:gap-3">
            <SearchButton v-if="!patientVerified" text="Buscar" loading-text="Buscando..." @click="searchPatient" size="md" />
            <ClearButton v-if="patientVerified" text="Limpiar" @click="clearPatientVerification" />
          </div>
        </div>

        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ searchError }}</p>
        </div>

        <!-- Información del paciente verificado -->
        <div v-if="patientVerified && verifiedPatient" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-4">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm sm:text-base font-semibold text-green-800">Paciente Verificado</h4>
          </div>
          
          <div class="bg-white border border-green-200 rounded-lg shadow-sm p-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Nombre</p>
                <p class="text-gray-900 break-words font-semibold">{{ verifiedPatient.nombrePaciente }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Código</p>
                <p class="text-gray-900 font-mono font-semibold">{{ verifiedPatient.pacienteCode }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Edad</p>
                <p class="text-gray-900 font-semibold">{{ verifiedPatient.edad }} años</p>
              </div>
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Sexo</p>
                <p class="text-gray-900 font-semibold capitalize">{{ verifiedPatient.sexo }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Tipo de Atención</p>
                <p class="text-gray-900 font-semibold capitalize">{{ verifiedPatient.tipoAtencion }}</p>
              </div>
              <div class="space-y-1">
                <p class="text-gray-600 font-medium">Entidad</p>
                <p class="text-gray-900 break-words font-semibold">{{ verifiedPatient.entidad }}</p>
              </div>
            </div>
          </div>
        </div>
      </div>

      <!-- Formulario del caso (visible solo si hay paciente verificado) -->
      <div v-if="patientVerified" class="space-y-6">
        <!-- Campos de entidad y tipo de atención -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList v-model="formData.entidadPaciente" label="Entidad del Paciente" placeholder="Seleciona la entidad" :required="true" :auto-load="true" :error="validationState.hasAttemptedSubmit && !formData.entidadPaciente ? 'La entidad es obligatoria' : ''" />
          <FormSelect v-model="formData.tipoAtencionPaciente" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" :error="validationState.hasAttemptedSubmit && !formData.tipoAtencionPaciente ? 'Por favor seleccione el tipo de atención' : ''" />
        </div>

        <!-- Campos de fecha de ingreso y prioridad -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.fechaIngreso" label="Fecha de Ingreso" type="date" :required="true" :errors="errors.fechaIngreso" :warnings="warnings.fechaIngreso" help-text="Fecha en que ingresa el caso al sistema" />
          <FormSelect v-model="formData.prioridadCaso" label="Prioridad del Caso" placeholder="Seleccione la prioridad" :required="true" :options="prioridadOptions" :error="validationState.hasAttemptedSubmit && !formData.prioridadCaso ? 'La prioridad es obligatoria' : ''" help-text="Nivel de urgencia del caso" />
        </div>

        <!-- Campos de médico solicitante y servicio -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.medicoSolicitante" label="Médico Solicitante" placeholder="Ejemplo: Alberto Perez" :required="true" :max-length="200" help-text="Medico solicitante del estudio" :errors="getMedicoErrors" :only-letters="true" />
          <FormInputField v-model="formData.servicio" label="Servicio" placeholder="Ejemplo: Medicina Interna" :required="true" :max-length="100" help-text="Área de procedencia del caso" :errors="getServicioErrors" />
        </div>

        <!-- Campo de número de muestras -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.numeroMuestras" label="Número de Muestras" type="number" :min="1" :max="10" :required="true" :errors="errors.numeroMuestras" :warnings="warnings.numeroMuestras" help-text="Cantidad de submuestras para este caso" @input="handleNumeroMuestrasChange" />
        </div>

        <!-- Sección de información de submuestras -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(muestra, muestraIndex) in formData.muestras" :key="muestra.numero" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">Submuestra #{{ muestra.numero }}</h4>
              
              <!-- Selección de región del cuerpo -->
              <div class="mb-4">
                <BodyRegionList v-model="muestra.regionCuerpo" :label="`Región del Cuerpo`" placeholder="Buscar región del cuerpo..." :required="true" :auto-load="true" :errors="getRegionErrors(muestraIndex)" help-text="Seleccione la región anatómica de donde proviene la muestra" />
              </div>
              
              <!-- Configuración de pruebas -->
              <div class="space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label class="block text-sm font-medium text-gray-700">Pruebas a realizar</label>
                  <div class="self-end sm:self-auto">
                    <AddButton text="Agregar Prueba" @click="addPruebaToMuestra(muestraIndex)" />
                  </div>
                </div>
                
                <div class="space-y-2">
                  <div v-for="(prueba, pruebaIndex) in muestra.pruebas" :key="pruebaIndex" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center">
                    <div class="flex-1 min-w-0">
                      <TestList v-model="prueba.code" :label="`Prueba #${pruebaIndex + 1}`" :placeholder="`Buscar y seleccionar prueba ${pruebaIndex + 1}...`" :required="true" :auto-load="true" :errors="getPruebaErrors(muestraIndex, pruebaIndex)" @test-selected="(test) => handleTestSelected(muestraIndex, pruebaIndex, test)" />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField v-model.number="prueba.cantidad" label="Cantidad" type="number" :min="1" :max="10" placeholder="Cantidad" />
                    </div>
                    <div class="flex items-center justify-center sm:justify-start sm:w-10 sm:mt-6">
                      <RemoveButton @click="removePruebaFromMuestra(muestraIndex, pruebaIndex)" title="Eliminar prueba" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Campo de observaciones -->
        <FormTextarea v-model="formData.observaciones" label="Observaciones del caso" placeholder="Observaciones adicionales sobre el caso o procedimiento..." :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional relevante para el procesamiento del caso" />

        <div v-if="errors.muestras.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-red-800 mb-2">Errores en las Submuestras:</h4>
          <ul class="list-disc list-inside space-y-1">
            <li v-for="error in errors.muestras" :key="error" class="text-sm text-red-600">{{ error }}</li>
          </ul>
        </div>

        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
          <ClearButton @click="clearForm" />
          <SaveButton text="Guardar Caso" @click="handleSaveClick" />
        </div>

        <ValidationAlert :visible="validationState.showValidationError" :errors="validationErrors" @close="validationState.showValidationError = false" />
      </div>

      <div ref="notificationContainer">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && createdCase" #content>
            <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Encabezado del caso creado -->
                <div class="text-center pb-3 border-b border-gray-200 relative">
                  <div class="inline-block">
                    <div class="relative inline-block">
                      <p class="font-mono font-bold text-2xl text-gray-900 mb-1">{{ createdCase.codigo }}</p>
                      <button
                        @click="copyCaseCode"
                        class="absolute -right-10 top-1/2 transform -translate-y-1/2 inline-flex items-center justify-center w-8 h-8 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors duration-200"
                        title="Copiar código del caso"
                      >
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                        </svg>
                      </button>
                    </div>
                    <p class="text-gray-500 text-sm">{{ createdDateDisplay }}</p>
                  </div>
                </div>
                
                <!-- Grid de información del caso -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <!-- Información del paciente -->
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Información del Paciente</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Nombre:</span><p class="text-gray-900 font-semibold">{{ createdCase.paciente?.nombre || verifiedPatient?.nombrePaciente }}</p></div>
                      <div><span class="text-gray-500 font-medium">Documento:</span><p class="text-gray-900 font-mono font-semibold">{{ createdCase.paciente?.paciente_code || verifiedPatient?.pacienteCode || 'NO DISPONIBLE' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Edad:</span><p class="text-gray-900 font-semibold">{{ createdCase.paciente?.edad || verifiedPatient?.edad }} años</p></div>
                      <div><span class="text-gray-500 font-medium">Sexo:</span><p class="text-gray-900 font-semibold">{{ createdCase.paciente?.sexo || verifiedPatient?.sexo }}</p></div>
                      <div><span class="text-gray-500 font-medium">Entidad:</span><p class="text-gray-900 font-semibold">{{ createdCase.paciente?.entidad || verifiedPatient?.entidad }}</p></div>
                      <div><span class="text-gray-500 font-medium">Tipo de Atención:</span><p class="text-gray-900 font-semibold">{{ createdCase.paciente?.tipoAtencion || verifiedPatient?.tipoAtencion }}</p></div>
                    </div>
                  </div>
                  
                  <!-- Detalles del caso -->
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Detalles del Caso</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Estado:</span><p class="text-gray-900 font-semibold">{{ createdCase.estado || 'En proceso' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Prioridad:</span><p class="text-gray-900 font-semibold">{{ createdCase.prioridad || formData.prioridadCaso || 'Normal' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Médico Solicitante:</span><p class="text-gray-900 font-semibold">{{ createdCase.medicoSolicitante || formData.medicoSolicitante || 'No especificado' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Servicio:</span><p class="text-gray-900 font-semibold">{{ createdCase.servicio || formData.servicio || 'No especificado' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Número de Submuestras:</span><p class="text-gray-900 font-semibold">{{ getMuestrasForNotification().length }}</p></div>
                      <div v-if="createdCase.observaciones || formData.observaciones"><span class="text-gray-500 font-medium">Observaciones:</span><p class="text-gray-900">{{ createdCase.observaciones || formData.observaciones }}</p></div>
                    </div>
                  </div>
                </div>
                
                <!-- Resumen de submuestras creadas -->
                <div>
                  <h4 class="font-semibold text-gray-800 mb-3 text-base">Submuestras Creadas</h4>
                  <div class="space-y-3">
                    <div v-for="(muestra, index) in getMuestrasForNotification()" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900 text-sm">Submuestra {{ index + 1 }}</span>
                        <span class="text-sm text-gray-500">{{ (muestra.pruebas && muestra.pruebas.length) || 0 }} prueba{{ ((muestra.pruebas && muestra.pruebas.length) || 0) !== 1 ? 's' : '' }}</span>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div><span class="text-gray-500 font-medium">Región:</span><p class="text-gray-900">{{ muestra.regionCuerpo || 'Sin especificar' }}</p></div>
                        <div><span class="text-gray-500 font-medium">Pruebas:</span><div class="text-gray-900"><span v-if="muestra.pruebas && muestra.pruebas.length > 0">{{ muestra.pruebas.map((p: any) => `${p.code || p.nombre || 'Sin código'} (${p.cantidad || 1})`).join(', ') }}</span><span v-else class="text-gray-400">Sin pruebas</span></div></div>
                      </div>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </template>
        </Notification>
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, nextTick, watch } from 'vue'
import { useCaseForm } from '../../composables/useCaseForm'
import { usePatientVerification } from '../../composables/usePatientVerification'
import { useNotifications } from '../../composables/useNotifications'
import { useCaseAPI } from '../../composables/useCaseAPI'
import type { PatientData, CreatedCase } from '../../types'
import { ComponentCard } from '@/shared/components'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { ValidationAlert, Notification } from '@/shared/components/feedback'
import { EntityList, TestList, BodyRegionList } from '@/shared/components/List'
import { DocsIcon, TestIcon, SearchIcon } from '@/assets/icons'



// Referencias del DOM y estado local
const notificationContainer = ref<HTMLElement | null>(null)
const createdCase = ref<CreatedCase | null>(null)
const emit = defineEmits(['case-saved', 'patient-verified'])

// Composables para manejo del formulario, verificación de pacientes, notificaciones y API
const { formData, validationState, errors, warnings, validateForm, clearForm: clearCaseForm, handleNumeroMuestrasChange, addPruebaToMuestra, removePruebaFromMuestra } = useCaseForm()
const { searchError, patientVerified, verifiedPatient, searchPatientByDocumento, useNewPatient, clearVerification } = usePatientVerification()
const { notification, showNotification, closeNotification } = useNotifications()
const { createCase, error: apiError, clearState } = useCaseAPI()

// Estado local para búsqueda de paciente
const pacienteCodeBusqueda = ref('')

// Opciones para los selectores
const tipoAtencionOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' }, 
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

const prioridadOptions = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Prioritario', label: 'Prioritario' }
]

const validationErrors = computed(() => {
  const errorsList: string[] = []
  const fields = [
    { value: formData.fechaIngreso, name: 'Fecha de ingreso' },
    { value: formData.medicoSolicitante, name: 'Médico solicitante' },
    { value: formData.servicio, name: 'Servicio' },
    { value: formData.prioridadCaso, name: 'Prioridad del caso' },
    { value: formData.numeroMuestras, name: 'Número de muestras' },
    { value: formData.entidadPaciente, name: 'Entidad del paciente' },
    { value: formData.tipoAtencionPaciente, name: 'Tipo de atención' }
  ]
  
  fields.forEach(field => !field.value && errorsList.push(field.name))
  
  formData.muestras?.forEach((muestra, i) => {
    if (!muestra.regionCuerpo) errorsList.push(`Submuestra ${i + 1}: Región del cuerpo`)
    if (!muestra.pruebas?.length) errorsList.push(`Submuestra ${i + 1}: Al menos una prueba`)
    muestra.pruebas?.forEach((prueba, j) => {
      if (!prueba.code) errorsList.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Código de prueba`)
      if (!prueba.cantidad || prueba.cantidad < 1) errorsList.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Cantidad`)
    })
  })
  
  errors.muestras?.forEach(error => errorsList.push(`Submuestras: ${error}`))
  return errorsList
})

const getMedicoErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.medicoSolicitante.length > 0) return errors.medicoSolicitante
  if (!formData.medicoSolicitante?.trim()) return ['El médico solicitante es obligatorio']
  return []
})

const getServicioErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.servicio.length > 0) return errors.servicio
  if (!formData.servicio?.trim()) return ['El servicio es obligatorio']
  return []
})

const getRegionErrors = (muestraIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const muestra = formData.muestras[muestraIndex]
  if (!muestra || !muestra.regionCuerpo?.trim()) return ['La región del cuerpo es obligatoria']
  return [] as string[]
}

const getPruebaErrors = (muestraIndex: number, pruebaIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const muestra = formData.muestras[muestraIndex]
  if (!muestra) return ['Debe seleccionar una prueba']
  const prueba = muestra.pruebas[pruebaIndex]
  if (!prueba || !String(prueba.code || '').trim()) return ['El código de la prueba es obligatorio']
  if (prueba.cantidad == null || Number(prueba.cantidad) < 1) return ['La cantidad debe ser al menos 1']
  return [] as string[]
}

const createdDateDisplay = computed(() => {
  const value = createdCase.value?.fechaIngreso || formData.fechaIngreso
  if (!value) return ''
  const isDateOnly = /^\d{4}-\d{2}-\d{2}$/.test(String(value))
  const date = new Date(isDateOnly ? `${value}T00:00:00` : String(value))
  if (isNaN(date.getTime())) return String(value)
  const datePart = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'long', year: 'numeric' }).format(date)
  return isDateOnly ? datePart : `${datePart} ${new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit' }).format(date)}`
})

const getMuestrasForNotification = () => {
  const backendMuestras = createdCase.value?.muestras || []
  const formMuestras = formData.muestras || []
  return !backendMuestras.length ? formMuestras : backendMuestras.map((backendMuestra: any, index: number) => ({
    ...backendMuestra,
    regionCuerpo: backendMuestra.regionCuerpo || backendMuestra.region_cuerpo || formMuestras[index]?.regionCuerpo || 'Sin especificar',
    pruebas: (backendMuestra.pruebas || []).map((prueba: any, pIndex: number) => ({
      ...prueba,
      cantidad: prueba.cantidad || formMuestras[index]?.pruebas?.[pIndex]?.cantidad || 1
    }))
  }))
}

// Handlers de eventos
const handlePacienteCodeInput = (value: string) => {
  pacienteCodeBusqueda.value = value
}

const handleTestSelected = (muestraIndex: number, pruebaIndex: number, test: any) => {
  if (test && muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
    const muestra = formData.muestras[muestraIndex]
    if (pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      // Asignar correctamente el código y nombre de la prueba
      muestra.pruebas[pruebaIndex].code = test.pruebaCode || test.code || ''
      muestra.pruebas[pruebaIndex].nombre = test.pruebasName || test.nombre || test.label || ''
    }
  }
}

const searchPatient = async () => {
  if (!pacienteCodeBusqueda.value.trim()) return
  const result = await searchPatientByDocumento(pacienteCodeBusqueda.value)
  if ((result as any).found && (result as any).patient) {
    const patient = (result as any).patient as PatientData
    updateFormDataWithPatient(patient)
    emit('patient-verified', patient)
  }
}

const updateFormDataWithPatient = (patientData: PatientData) => {
  const tipo = String(patientData.tipoAtencion || '').toLowerCase()
  Object.assign(formData, {
    pacienteDocumento: patientData.pacienteCode,
    entidadPaciente: patientData.entidadCodigo || '',
    tipoAtencionPaciente: tipo.includes('ambulator') || tipo === 'ambulatorio' ? 'Ambulatorio' : tipo.includes('hospital') || tipo === 'hospitalizado' ? 'Hospitalizado' : ''
  })
}

const clearPatientFormData = () => {
  Object.assign(formData, {
    pacienteDocumento: '',
    entidadPaciente: '',
    tipoAtencionPaciente: '',
    prioridadCaso: 'Normal',
    servicio: ''
  })
}

// Limpieza de la verificación del paciente
const clearPatientVerification = () => {
  clearVerification()
  pacienteCodeBusqueda.value = ''
  clearPatientFormData()
}

const handleNewPatient = (patientData: PatientData) => {
  useNewPatient(patientData)
  pacienteCodeBusqueda.value = patientData.pacienteCode
  updateFormDataWithPatient(patientData)
  emit('patient-verified', patientData)
}

// Scroll automático a notificaciones
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

// Watcher para scroll automático
watch(() => notification.visible, (newValue) => {
  if (newValue) scrollToNotification()
})

const copyCaseCode = async () => {
  if (!createdCase.value?.codigo) return
  const code = createdCase.value.codigo
  const message = `El código ${code} se ha copiado al portapapeles.`
  
  try {
    await navigator.clipboard.writeText(code)
    showNotification('success', 'Código copiado', message, 3000)
  } catch {
    const textArea = document.createElement('textarea')
    textArea.value = code
    document.body.appendChild(textArea)
    textArea.select()
    document.execCommand('copy')
    document.body.removeChild(textArea)
    showNotification('success', 'Código copiado', message, 3000)
  }
}

const clearForm = () => {
  clearCaseForm()
  clearPatientVerification()
}

const handleSaveClick = async () => {
  // Validar formulario
  const isValid = validateForm()
  if (!isValid) { 
    validationState.showValidationError = true
    // Solo mostrar ValidationAlert; no disparar notificación para evitar duplicados
    return 
  }
  
  // Verificar que hay paciente verificado
  if (!patientVerified.value || !verifiedPatient.value) {
    showNotification('error', 'Paciente Requerido', 'Debe buscar y verificar un paciente antes de crear el caso.', 5000)
    return
  }

  validationState.showValidationError = false
  clearState()

  try {
    const result = await createCase(formData, verifiedPatient.value)
    if (result.success && result.case) {
      createdCase.value = result.case
      showNotification('success', '¡Caso Creado Exitosamente!', '', 0)
      emit('case-saved', result.case)
      clearForm()
    } else {
      throw new Error(result.message || 'Error desconocido al crear el caso')
    }
  } catch (error: any) {
    showNotification('error', 'Error al Guardar Caso', apiError.value || error.message || 'No se pudo guardar el caso. Por favor, inténtelo nuevamente.', 0)
  }
}

// Exposición de funciones para uso externo
defineExpose({ handleNewPatient })
</script>
