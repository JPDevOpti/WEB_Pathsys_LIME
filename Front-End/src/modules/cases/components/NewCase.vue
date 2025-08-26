<template>
  <ComponentCard 
    title="Crear nuevo caso"
    description="Complete la información del caso para ingresarlo al sistema."
  >
    <template #icon>
      <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
        <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12h6m-6 4h6m2 5H7a2 2 0 01-2-2V5a2 2 0 012-2h5.586a1 1 0 01.707.293l5.414 5.414a1 1 0 01.293.707V19a2 2 0 01-2 2z" />
      </svg>
    </template>

    <div class="space-y-6">
      <!-- Sección 1: Verificación del Paciente -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
          </svg>
        Buscar Paciente
        </h3>
        
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <FormInputField
              v-model="cedulaBusqueda"
              placeholder="Ingrese número de cédula"
              :required="true"
              :max-length="10"
              inputmode="numeric"
              :disabled="patientVerified"
              @input="handleCedulaInput"
            />
          </div>
          
          <div class="flex gap-2 sm:gap-3">
            <SearchButton
              v-if="!patientVerified"
              text="Buscar"
              loading-text="Buscando..."
              @click="searchPatient"
              size="md"
            />
            
            <ClearButton
              v-if="patientVerified"
              text="Limpiar"
              @click="clearPatientVerification"
            />
          </div>
        </div>

        <!-- Error de búsqueda -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ searchError }}</p>
        </div>

        <!-- Información del paciente verificado -->
        <div v-if="patientVerified && verifiedPatient" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Paciente Verificado</h4>
          </div>
          
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
            <div>
              <span class="font-medium text-green-700">Nombre:</span>
              <p class="text-green-800 break-words">{{ verifiedPatient.nombrePaciente }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Cédula:</span>
              <p class="text-green-800 font-mono">{{ verifiedPatient.numeroCedula }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Edad:</span>
              <p class="text-green-800">{{ verifiedPatient.edad }} años</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Sexo:</span>
              <p class="text-green-800">{{ verifiedPatient.sexo }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Entidad:</span>
              <p class="text-green-800 break-words">{{ verifiedPatient.entidad }}</p>
            </div>
            <div>
              <span class="font-medium text-green-700">Tipo de Atención:</span>
              <p class="text-green-800 break-words">{{ verifiedPatient.tipoAtencion }}</p>
            </div>
          </div>
        </div>
      </div>

      <!-- Sección 2: Formulario del Caso (solo visible si hay paciente verificado) -->
      <div v-if="patientVerified" class="space-y-6">
        <!-- Médico Solicitante y Servicio -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField
            v-model="formData.medicoSolicitante"
            label="Médico Solicitante"
            placeholder="Médico que solicita el estudio"
            :required="false"
            :max-length="100"
            :errors="errors.medicoSolicitante"
            :warnings="warnings.medicoSolicitante"
          />
          
          <FormInputField
            v-model="formData.servicio"
            label="Servicio"
            placeholder="Procedencia del caso"
            :required="false"
            :max-length="100"
            :errors="errors.servicio"
            :warnings="warnings.servicio"
          />
        </div>

        <!-- Entidad y Tipo de Atención -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList
            v-model="formData.entidadPaciente"
            label="Entidad del Paciente"
            placeholder="Buscar entidad..."
            :required="true"
            :auto-load="true"
            :error="validationState.hasAttemptedSubmit && !formData.entidadPaciente ? 'La entidad es obligatoria' : ''"
          />
          
          <FormSelect
            v-model="formData.tipoAtencionPaciente"
            label="Tipo de Atención"
            placeholder="Seleccione el tipo de atención"
            :required="true"
            :options="tipoAtencionOptions"
            :error="validationState.hasAttemptedSubmit && !formData.tipoAtencionPaciente ? 'Por favor seleccione el tipo de atención' : ''"
          />
        </div>

        <!-- Número de Muestras y Fecha de Ingreso -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField
            v-model="formData.numeroMuestras"
            label="Número de Muestras"
            type="number"
            :min="1"
            :max="10"
            :required="true"
            :errors="errors.numeroMuestras"
            :warnings="warnings.numeroMuestras"
            help-text="Cantidad de submuestras para este caso (máximo 10)"
            @input="handleNumeroMuestrasChange"
          />
          
          <FormInputField
            v-model="formData.fechaIngreso"
            label="Fecha de Ingreso"
            type="date"
            :required="true"
            :errors="errors.fechaIngreso"
            :warnings="warnings.fechaIngreso"
            help-text="Fecha en que ingresa el caso al sistema"
          />
        </div>

        <!-- Información de Submuestras -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10" />
            </svg>
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div 
              v-for="(muestra, muestraIndex) in formData.muestras" 
              :key="muestra.numero"
              class="border border-gray-200 rounded-lg p-4 bg-gray-50"
            >
              <h4 class="font-medium text-gray-700 mb-4">
                Submuestra {{ muestra.numero }}
              </h4>
              
              <!-- Región del Cuerpo -->
              <div class="mb-4">
                <BodyRegionList
                  v-model="muestra.regionCuerpo"
                  :label="`Región del Cuerpo - Submuestra ${muestra.numero}`"
                  placeholder="Buscar región del cuerpo..."
                  :required="true"
                  :auto-load="true"
                  help-text="Seleccione la región anatómica de donde proviene la muestra"
                />
              </div>
              
              <!-- Pruebas -->
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="block text-sm font-medium text-gray-700">
                    Pruebas a Realizar <span class="text-red-500">*</span>
                  </label>
                  <AddButton
                    text="Agregar Prueba"
                    @click="addPruebaToMuestra(muestraIndex)"
                  />
                </div>
                
                <div class="space-y-2">
                  <div 
                    v-for="(prueba, pruebaIndex) in muestra.pruebas" 
                    :key="pruebaIndex"
                    class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center"
                  >
                    <div class="flex-1 min-w-0">
                      <TestList
                        v-model="prueba.code"
                        :label="`Prueba ${pruebaIndex + 1}`"
                        :placeholder="`Buscar y seleccionar prueba ${pruebaIndex + 1}...`"
                        :required="true"
                        :auto-load="true"
                        @test-selected="(test) => handleTestSelected(muestraIndex, pruebaIndex, test)"
                      />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField
                        v-model.number="prueba.cantidad"
                        label="Cantidad"
                        type="number"
                        :min="1"
                        :max="10"
                        placeholder="Cantidad"
                      />
                    </div>
                    <div class="flex items-center justify-center sm:justify-start sm:w-10 sm:mt-6">
                      <RemoveButton
                        v-if="muestra.pruebas.length > 1"
                        @click="removePruebaFromMuestra(muestraIndex, pruebaIndex)"
                        title="Eliminar prueba"
                      />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Observaciones -->
        <FormTextarea
          v-model="formData.observaciones"
          label="Observaciones del Caso"
          placeholder="Observaciones adicionales sobre el caso o procedimiento..."
          :rows="3"
          :max-length="500"
          :show-counter="true"
          help-text="Información adicional relevante para el procesamiento del caso"
        />

        <!-- Errores de validación de muestras -->
        <div v-if="errors.muestras.length > 0" class="bg-red-50 border border-red-200 rounded-lg p-4">
          <h4 class="text-sm font-semibold text-red-800 mb-2">Errores en las Submuestras:</h4>
          <ul class="list-disc list-inside space-y-1">
            <li v-for="error in errors.muestras" :key="error" class="text-sm text-red-600">
              {{ error }}
            </li>
          </ul>
        </div>

        <!-- Botones de Acción -->
        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
          <ClearButton
            @click="clearForm"
          />
          
          <SaveButton
            text="Guardar Caso"
            @click="handleSaveClick"
            :disabled="!isFormValid"
          />
        </div>

        <!-- Alerta de Validación -->
        <ValidationAlert
          :visible="validationState.showValidationError"
          :errors="validationErrors"
        />
      </div>

      <!-- Notificación de Éxito -->
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
          <template v-if="notification.type === 'success' && createdCase" #content>
            <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <!-- Header del Caso -->
                <div class="text-center pb-3 border-b border-gray-200">
                  <div class="inline-block">
                    <p class="font-mono font-bold text-2xl text-gray-900 mb-1">{{ createdCase.codigo }}</p>
                    <p class="text-gray-500 text-sm">{{ createdDateDisplay }}</p>
                  </div>
                </div>
                
                <!-- Grid Principal - Mejor aprovechamiento horizontal -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  
                  <!-- Información del Paciente -->
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Información del Paciente</h4>
                    <div class="space-y-2 text-sm">
                      <div>
                        <span class="text-gray-500 font-medium">Nombre:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.paciente?.nombre || verifiedPatient?.nombrePaciente }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Cédula:</span>
                        <p class="text-gray-900 font-mono font-semibold">{{ createdCase.paciente?.cedula || verifiedPatient?.numeroCedula }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Edad:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.paciente?.edad || verifiedPatient?.edad }} años</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Sexo:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.paciente?.sexo || verifiedPatient?.sexo }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Entidad:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.paciente?.entidad || verifiedPatient?.entidad }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Tipo de Atención:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.paciente?.tipoAtencion || verifiedPatient?.tipoAtencion }}</p>
                      </div>
                    </div>
                  </div>
                  
                  <!-- Detalles del Caso -->
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Detalles del Caso</h4>
                    <div class="space-y-2 text-sm">
                      <div>
                        <span class="text-gray-500 font-medium">Estado:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.estado || 'Pendiente' }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Médico Solicitante:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.medicoSolicitante || formData.medicoSolicitante }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Servicio:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.servicio || formData.servicio || 'No especificado' }}</p>
                      </div>
                      <div>
                        <span class="text-gray-500 font-medium">Número de Submuestras:</span>
                        <p class="text-gray-900 font-semibold">{{ createdCase.muestras?.length || formData.muestras.length }}</p>
                      </div>
                      <div v-if="createdCase.observaciones || formData.observaciones">
                        <span class="text-gray-500 font-medium">Observaciones:</span>
                        <p class="text-gray-900">{{ createdCase.observaciones || formData.observaciones }}</p>
                      </div>
                    </div>
                  </div>
                </div>
                
                <!-- Resumen de Submuestras - Vertical -->
                <div>
                  <h4 class="font-semibold text-gray-800 mb-3 text-base">Submuestras Creadas</h4>
                  <div class="space-y-3">
                    <div 
                      v-for="(muestra, index) in (createdCase.muestras || formData.muestras)" 
                      :key="index"
                      class="border border-gray-200 rounded-lg p-3 bg-gray-50"
                    >
                      <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900 text-sm">Submuestra {{ index + 1 }}</span>
                        <span class="text-sm text-gray-500">
                          {{ (muestra.pruebas && muestra.pruebas.length) || 0 }} prueba{{ ((muestra.pruebas && muestra.pruebas.length) || 0) !== 1 ? 's' : '' }}
                        </span>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div>
                          <span class="text-gray-500 font-medium">Región:</span>
                          <p class="text-gray-900">{{ muestra.regionCuerpo || 'Sin especificar' }}</p>
                        </div>
                        <div>
                          <span class="text-gray-500 font-medium">Pruebas:</span>
                          <div class="text-gray-900">
                            <span v-if="muestra.pruebas && muestra.pruebas.length > 0">
                              {{ muestra.pruebas.map(p => `${p.code || p.nombre || 'Sin código'} (${p.cantidad || 1})`).join(', ') }}
                            </span>
                            <span v-else class="text-gray-400">Sin pruebas</span>
                          </div>
                        </div>
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
import { useCaseForm } from '../composables/useCaseForm'
import { usePatientVerification } from '../composables/usePatientVerification'
import { useNotifications } from '../composables/useNotifications'
import { useCaseAPI } from '../composables/useCaseAPI'
import type { PatientData, CreatedCase } from '../types'
import ComponentCard from '../../../shared/components/ui/ComponentCard.vue'
import FormInputField from '../../../shared/components/ui/forms/FormInputField.vue'
import FormSelect from '../../../shared/components/ui/forms/FormSelect.vue'
import FormTextarea from '../../../shared/components/ui/forms/FormTextarea.vue'
import SaveButton from '../../../shared/components/ui/buttons/SaveButton.vue'
import ClearButton from '../../../shared/components/ui/buttons/ClearButton.vue'
import SearchButton from '../../../shared/components/ui/buttons/SearchButton.vue'
import AddButton from '../../../shared/components/ui/buttons/AddButton.vue'
import RemoveButton from '../../../shared/components/ui/buttons/RemoveButton.vue'
import ValidationAlert from '../../../shared/components/ui/feedback/ValidationAlert.vue'
import Notification from '../../../shared/components/ui/feedback/Notification.vue'
import { EntityList, TestList, BodyRegionList } from '../../../shared/components/ui/List'

// Referencia para el contenedor de notificación
const notificationContainer = ref<HTMLElement | null>(null)

// Almacenar información del caso creado
const createdCase = ref<CreatedCase | null>(null)

// Define events que puede emitir este componente
const emit = defineEmits(['case-saved', 'patient-verified'])

// Use composables
const {
  formData,
  validationState,
  errors,
  warnings,
  isFormValid,
  validateForm,
  clearForm: clearCaseForm,
  handleNumeroMuestrasChange,
  addPruebaToMuestra,
  removePruebaFromMuestra
} = useCaseForm()

const {
  searchError,
  patientVerified,
  verifiedPatient,
  searchPatientByCedula,
  useNewPatient,
  clearVerification
} = usePatientVerification()

const { notification, showNotification, closeNotification } = useNotifications()

const { createCase, error: apiError, clearState } = useCaseAPI()

// Estado local para búsqueda de paciente
const cedulaBusqueda = ref('')

// Opciones para los selects
const tipoAtencionOptions = [
  { value: 'ambulatorio', label: 'Ambulatorio' },
  { value: 'hospitalizado', label: 'Hospitalizado' }
]

// Computed para errores de validación
const validationErrors = computed(() => {
  const validationErrorsList: string[] = []
  
  if (!patientVerified.value) {
    validationErrorsList.push('Debe verificar un paciente antes de crear el caso')
  }
  
  if (!formData.fechaIngreso || errors.fechaIngreso?.length > 0) {
    validationErrorsList.push('Fecha de ingreso válida requerida')
  }
  if (errors.medicoSolicitante?.length > 0) {
    validationErrorsList.push('Médico solicitante debe tener formato válido')
  }
  if (!formData.numeroMuestras || errors.numeroMuestras?.length > 0) {
    validationErrorsList.push('Número de muestras válido requerido')
  }
  if (errors.muestras?.length > 0) {
    validationErrorsList.push('Complete la información de todas las submuestras')
  }
  if (!formData.entidadPaciente) {
    validationErrorsList.push('Entidad requerida')
  }
  if (!formData.tipoAtencionPaciente) {
    validationErrorsList.push('Tipo de atención requerido')
  }
  
  return validationErrorsList
})

// Formateo de fecha legible en español
const formatDateDisplay = (value: string | undefined | null): string => {
  if (!value) return ''
  let date: Date
  const isDateOnly = /^\d{4}-\d{2}-\d{2}$/.test(String(value))
  if (isDateOnly) {
    date = new Date(`${value}T00:00:00`)
  } else {
    date = new Date(String(value))
  }
  if (isNaN(date.getTime())) return String(value)
  const datePart = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'long', year: 'numeric' }).format(date)
  if (isDateOnly) return datePart
  const timePart = new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit' }).format(date)
  return `${datePart} ${timePart}`
}

const createdDateDisplay = computed(() => {
  const raw = createdCase.value?.fechaIngreso || formData.fechaIngreso
  return formatDateDisplay(raw)
})

// Función para manejar entrada de cédula
const handleCedulaInput = (value: string) => {
  // Solo permitir números
  const numericValue = value.replace(/\D/g, '')
  cedulaBusqueda.value = numericValue
}

// Función para manejar selección de prueba
const handleTestSelected = (muestraIndex: number, pruebaIndex: number, test: any) => {
  if (test && muestraIndex >= 0 && muestraIndex < formData.muestras.length) {
    const muestra = formData.muestras[muestraIndex]
    if (pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      // Actualizar tanto el código como el nombre de la prueba
      muestra.pruebas[pruebaIndex].code = test.pruebaCode
      muestra.pruebas[pruebaIndex].nombre = test.pruebasName
    }
  }
}

// Función para buscar paciente
const searchPatient = async () => {
  // Validar que la cédula no esté vacía
  if (!cedulaBusqueda.value.trim()) {
    return
  }

  const result = await searchPatientByCedula(cedulaBusqueda.value)
  
  if ((result as any).found && 'patient' in (result as any) && (result as any).patient) {
    const patient = (result as any).patient as PatientData
    // Actualizar datos del formulario con información del paciente
    updateFormDataWithPatient(patient)
    
    // Emitir evento
    emit('patient-verified', patient)
  }
}

// Normaliza tipo de atención del paciente a valores del select
const normalizeAttentionType = (value: string): string => {
  const v = String(value || '').toLowerCase()
  if (v.includes('ambulator')) return 'ambulatorio'
  if (v.includes('hospital')) return 'hospitalizado'
  return ''
}

// Función para actualizar datos del formulario con información del paciente
const updateFormDataWithPatient = (patientData: PatientData) => {
  formData.pacienteCedula = patientData.numeroCedula
  // Cargar SIEMPRE desde el paciente verificado
  formData.entidadPaciente = patientData.entidadCodigo || ''
  formData.tipoAtencionPaciente = normalizeAttentionType(patientData.tipoAtencion)
}

// Función para limpiar datos del formulario relacionados con el paciente
const clearPatientFormData = () => {
  formData.pacienteCedula = ''
  formData.entidadPaciente = ''
  formData.tipoAtencionPaciente = ''
  formData.servicio = ''
}

// Función para limpiar verificación de paciente
const clearPatientVerification = () => {
  clearVerification()
  cedulaBusqueda.value = ''
  
  // Limpiar datos relacionados del formulario
  clearPatientFormData()
}

// Función para usar paciente recién creado
const handleNewPatient = (patientData: PatientData) => {
  useNewPatient(patientData)
  cedulaBusqueda.value = patientData.numeroCedula
  
  // Actualizar datos del formulario
  updateFormDataWithPatient(patientData)
  
  emit('patient-verified', patientData)
}

// Función para hacer scroll a la notificación
const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({
      behavior: 'smooth',
      block: 'center'
    })
  }
}

// Watch para detectar cuando aparece la notificación y hacer scroll
watch(
  () => notification.visible,
  (newValue) => {
    if (newValue) {
      scrollToNotification()
    }
  }
)

// Función para limpiar todo el formulario
const clearForm = () => {
  clearCaseForm()
  clearPatientVerification()
}

// Manejar click del botón guardar
const handleSaveClick = async () => {
  if (!patientVerified.value || !verifiedPatient.value) {
    validationState.showValidationError = true
    return
  }

  const isValid = validateForm()
  
  if (!isValid) {
    validationState.showValidationError = true
    return
  }

  validationState.showValidationError = false
  clearState() // Limpiar errores previos de la API



  try {
    // Crear el caso usando la API (el backend generará el consecutivo automáticamente)
    const result = await createCase(formData, verifiedPatient.value)
    
    if (result.success && result.case) {
      // Almacenar información del caso creado
      createdCase.value = result.case
      
      // Mostrar notificación de éxito
      showNotification(
        'success',
        '¡Caso Creado Exitosamente!',
        '', // Sin mensaje descriptivo
        0 // Sin auto-close, solo manual
      )
      
      // Emitir evento con los datos del caso guardado
      emit('case-saved', result.case)
      
      // Limpiar formulario inmediatamente después de guardar
      clearForm()
    } else {
      throw new Error(result.message || 'Error desconocido al crear el caso')
    }
    
  } catch (error: any) {
    // Mostrar notificación de error específica
    const errorMessage = apiError.value || error.message || 'No se pudo guardar el caso. Por favor, inténtelo nuevamente.'
    
    showNotification(
      'error',
      'Error al Guardar Caso',
      errorMessage,
      0 // No auto-close para errores
    )
  }
}

// Exponer función para uso desde componente padre
defineExpose({
  handleNewPatient
})
</script>
