<template>
  <!-- Create a new case: verify patient, fill case form, review summary -->
  <ComponentCard title="Crear nuevo caso" description="Complete la información del caso para ingresarlo al sistema.">
    <template #icon>
      <DocumentIcon class="w-5 h-5 mr-2" />
    </template>
    
    <div class="space-y-6">
      
      <!-- Patient verification section -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <SearchIcon class="w-4 h-4 mr-2 text-gray-500" />
        Buscar paciente
        </h3>
        
        <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
          <div class="flex-1">
            <!-- Patient code input (numeric only) -->
            <FormInputField v-model="pacienteCodeBusqueda" placeholder="Ingrese código del paciente" :required="true" :max-length="12" inputmode="numeric" :only-numbers="true" :disabled="patientVerified" @input="(v:string)=>pacienteCodeBusqueda=v" />
          </div>
          
          <div class="flex gap-2 sm:gap-3">
            <!-- Search/Clear actions -->
            <SearchButton v-if="!patientVerified" text="Buscar" loading-text="Buscando..." @click="searchPatient" size="md" />
            <ClearButton v-if="patientVerified" text="Limpiar" @click="clearPatientVerification" />
          </div>
        </div>

        <!-- Inline error for patient search -->
        <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
          <p class="text-sm text-red-600">{{ searchError }}</p>
        </div>

        <!-- Verified patient summary -->
        <div v-if="patientVerified && verifiedPatient" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-4">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm sm:text-base font-semibold text-green-800">Paciente Verificado</h4>
          </div>
          
          <!-- Key patient data -->
          <div class="bg-white border border-green-200 rounded-lg shadow-sm p-4">
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
              <div class="space-y-1"><p class="text-gray-600 font-medium">Nombre</p><p class="text-gray-900 break-words font-semibold">{{ verifiedPatient.name }}</p></div>
              <div class="space-y-1"><p class="text-gray-600 font-medium">Documento</p><p class="text-gray-900 font-mono font-semibold">{{ verifiedPatient.patientCode }}</p></div>
              <div class="space-y-1"><p class="text-gray-600 font-medium">Edad</p><p class="text-gray-900 font-semibold">{{ verifiedPatient.age }} años</p></div>
              <div class="space-y-1"><p class="text-gray-600 font-medium">Sexo</p><p class="text-gray-900 font-semibold capitalize">{{ verifiedPatient.gender }}</p></div>
              <div class="space-y-1"><p class="text-gray-600 font-medium">Tipo de Atención</p><p class="text-gray-900 font-semibold capitalize">{{ verifiedPatient.careType }}</p></div>
              <div class="space-y-1"><p class="text-gray-600 font-medium">Entidad</p><p class="text-gray-900 break-words font-semibold">{{ verifiedPatient.entity }}</p></div>
            </div>
          </div>
        </div>
      </div>

      <!-- Case form (visible only with verified patient) -->
      <div v-if="patientVerified" class="space-y-6">
        <!-- Entity and care type -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList v-model="formData.patientEntity" label="Entidad del Paciente" placeholder="Seleciona la entidad" :required="true" :auto-load="true" :error="validationState.hasAttemptedSubmit && !formData.patientEntity ? 'La entidad es obligatoria' : ''" />
          <FormSelect v-model="formData.patientCareType" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" :error="validationState.hasAttemptedSubmit && !formData.patientCareType ? 'Por favor seleccione el tipo de atención' : ''" />
        </div>

        <!-- Entry date and priority -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.entryDate" label="Fecha de Ingreso" type="date" :required="true" :errors="errors.entryDate" :warnings="warnings.entryDate" help-text="Fecha en que ingresa el caso al sistema" />
          <FormSelect v-model="formData.casePriority" label="Prioridad del Caso" placeholder="Seleccione la prioridad" :required="true" :options="prioridadOptions" :error="validationState.hasAttemptedSubmit && !formData.casePriority ? 'La prioridad es obligatoria' : ''" help-text="Nivel de urgencia del caso" />
        </div>

        <!-- Requesting physician and service -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.requestingPhysician" label="Médico Solicitante" placeholder="Ejemplo: Alberto Perez" :required="true" :max-length="200" help-text="Medico solicitante del estudio" :errors="getMedicoErrors" :only-letters="true" />
          <FormInputField v-model="formData.service" label="Servicio" placeholder="Ejemplo: Medicina Interna" :required="true" :max-length="100" help-text="Área de procedencia del caso" :errors="getServicioErrors" />
        </div>

        <!-- Number of samples -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model.number="formData.numberOfSamples" label="Número de Muestras" type="number" :min="1" :required="true" :errors="errors.numberOfSamples" :warnings="warnings.numberOfSamples" help-text="Cantidad de submuestras para este caso" @input="handleNumberOfSamplesChange" />
        </div>

        <!-- Samples details -->
        <div class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(sample, sampleIndex) in formData.samples" :key="sample.number" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">Submuestra #{{ sample.number }}</h4>
              
              <!-- Body region per sample -->
              <div class="mb-4">
                <BodyRegionList v-model="sample.bodyRegion" :label="`Región del Cuerpo`" placeholder="Buscar región del cuerpo..." :required="true" :auto-load="true" :errors="getRegionErrors(sampleIndex)" help-text="Seleccione la región anatómica de donde proviene la muestra" />
              </div>
              
              <!-- Tests per sample -->
              <div class="space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label class="block text-sm font-medium text-gray-700">Pruebas a realizar</label>
                  <div class="self-end sm:self-auto">
                    <AddButton text="Agregar Prueba" @click="addTestToSample(sampleIndex)" />
                  </div>
                </div>
                
                <div class="space-y-2">
                  <div v-for="(test, testIndex) in sample.tests" :key="testIndex" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-stretch sm:items-center">
                    <div class="flex-1 min-w-0">
                      <TestList v-model="test.code" :label="`Prueba #${testIndex + 1}`" :placeholder="`Buscar y seleccionar prueba ${testIndex + 1}...`" :required="true" :auto-load="true" :errors="getPruebaErrors(sampleIndex, testIndex)" @test-selected="(t)=>onTestSelected(sampleIndex, testIndex, t)" />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField v-model.number="test.quantity" label="Cantidad" type="number" :min="1" placeholder="Cantidad" />
                    </div>
                    <div class="flex items-center justify-center sm:justify-start sm:w-10 sm:mt-6">
                      <RemoveButton @click="removeTestFromSample(sampleIndex, testIndex)" title="Eliminar prueba" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Observations -->
        <FormTextarea v-model="formData.observations" label="Observaciones del caso" placeholder="Observaciones adicionales sobre el caso o procedimiento..." :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional relevante para el procesamiento del caso" />

        

        <!-- Form actions -->
        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
          <ClearButton @click="clearForm" />
          <SaveButton text="Guardar Caso" @click="handleSaveClick" />
        </div>

        <!-- Global validation alert -->
        <ValidationAlert :visible="validationState.showValidationError" :errors="validationErrors" @close="validationState.showValidationError = false" />
      </div>

      <!-- Notification with created case summary -->
      <div ref="notificationContainer">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification">
          <template v-if="notification.type === 'success' && createdCase" #content>
            <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                
                <!-- Case heading with copy code button -->
                <div class="text-center pb-3 border-b border-gray-200 relative">
                  <div class="inline-block">
                    <div class="relative inline-block">
                      <p class="font-mono font-bold text-2xl text-gray-900 mb-1">{{ createdCase.code }}</p>
                      <button @click="copyCaseCode" class="absolute -right-10 top-1/2 transform -translate-y-1/2 inline-flex items-center justify-center w-8 h-8 text-gray-500 hover:text-gray-700 hover:bg-gray-100 rounded-md transition-colors duración-200" title="Copiar código del caso">
                        <svg class="w-4 h-4" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 16H6a2 2 0 01-2-2V6a2 2 0 012-2h8a2 2 0 012 2v2m-6 12h8a2 2 0 002-2v-8a2 2 0 00-2-2h-8a2 2 0 00-2 2v8a2 2 0 002 2z"/>
                        </svg>
                      </button>
                    </div>
                    <p class="text-gray-500 text-sm">{{ createdDateDisplay }}</p>
                  </div>
                </div>
                
                <!-- Patient and case summary -->
                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Información del Paciente</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Nombre:</span><p class="text-gray-900 font-semibold">{{ createdCase.patient?.name || verifiedPatient?.name }}</p></div>
                      <div><span class="text-gray-500 font-medium">Documento:</span><p class="text-gray-900 font-mono font-semibold">{{ createdCase.patient?.patient_code || verifiedPatient?.patientCode || 'NO DISPONIBLE' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Edad:</span><p class="text-gray-900 font-semibold">{{ createdCase.patient?.age || verifiedPatient?.age }} años</p></div>
                      <div><span class="text-gray-500 font-medium">Sexo:</span><p class="text-gray-900 font-semibold">{{ genderDisplay }}</p></div>
                      <div><span class="text-gray-500 font-medium">Entidad:</span><p class="text-gray-900 font-semibold">{{ createdCase.patient?.entity || verifiedPatient?.entity }}</p></div>
                      <div><span class="text-gray-500 font-medium">Tipo de Atención:</span><p class="text-gray-900 font-semibold">{{ careTypeDisplay }}</p></div>
                    </div>
                  </div>
                  
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Detalles del Caso</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Estado:</span><p class="text-gray-900 font-semibold">{{ stateDisplay }}</p></div>
                      <div><span class="text-gray-500 font-medium">Prioridad:</span><p class="text-gray-900 font-semibold">{{ priorityDisplay }}</p></div>
                      <div><span class="text-gray-500 font-medium">Médico Solicitante:</span><p class="text-gray-900 font-semibold">{{ createdCase.requestingPhysician || formData.requestingPhysician || 'No especificado' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Servicio:</span><p class="text-gray-900 font-semibold">{{ createdCase.service || formData.service || 'No especificado' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Número de Submuestras:</span><p class="text-gray-900 font-semibold">{{ getMuestrasForNotification().length }}</p></div>
                      <div v-if="createdCase.observations || formData.observations"><span class="text-gray-500 font-medium">Observaciones:</span><p class="text-gray-900">{{ createdCase.observations || formData.observations }}</p></div>
                    </div>
                  </div>
                </div>
                
                <!-- Created samples summary -->
                <div>
                  <h4 class="font-semibold text-gray-800 mb-3 text-base">Submuestras Creadas</h4>
                  <div class="space-y-3">
                    <div v-for="(sample, index) in getMuestrasForNotification()" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900 text-sm">Submuestra {{ index + 1 }}</span>
                        <span class="text-sm text-gray-500">{{ (sample.tests && sample.tests.length) || 0 }} prueba{{ ((sample.tests && sample.tests.length) || 0) !== 1 ? 's' : '' }}</span>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div><span class="text-gray-500 font-medium">Región:</span><p class="text-gray-900">{{ sample.bodyRegion || 'Sin especificar' }}</p></div>
                        <div><span class="text-gray-500 font-medium">Pruebas:</span><div class="text-gray-900"><span v-if="sample.tests && sample.tests.length > 0">{{ sample.tests.map((t: any) => `${t.name || t.code || 'Sin código'} (${t.quantity || 1})`).join(', ') }}</span><span v-else class="text-gray-400">Sin pruebas</span></div></div>
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
import { DocumentIcon, TestIcon, SearchIcon } from '@/assets/icons'

// DOM refs and emitted events
const notificationContainer = ref<HTMLElement | null>(null)
const createdCase = ref<CreatedCase | null>(null)
const emit = defineEmits(['case-saved', 'patient-verified'])

// Composables for form, verification, notifications, and API
const { formData, validationState, errors, warnings, validateForm, clearForm: clearCaseForm, handleNumberOfSamplesChange, addTestToSample, removeTestFromSample } = useCaseForm()
const { searchError, patientVerified, verifiedPatient, searchPatientByDocumento, useNewPatient, clearVerification } = usePatientVerification()
const { notification, showNotification, closeNotification } = useNotifications()
const { createCase, error: apiError, clearState } = useCaseAPI()

// Local state: patient code search
const pacienteCodeBusqueda = ref('')

// Select options
const tipoAtencionOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' }, 
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]
const prioridadOptions = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Prioritario', label: 'Prioritario' }
]

// Form-level validation messages list
const validationErrors = computed(() => {
  const fields = [
    { value: formData.entryDate, name: 'Fecha de ingreso' },
    { value: formData.requestingPhysician, name: 'Médico solicitante' },
    { value: formData.service, name: 'Servicio' },
    { value: formData.casePriority, name: 'Prioridad del caso' },
    { value: formData.numberOfSamples, name: 'Número de muestras' },
    { value: formData.patientEntity, name: 'Entidad del paciente' },
    { value: formData.patientCareType, name: 'Tipo de atención' }
  ]
  const list: string[] = []
  fields.forEach(f => !f.value && list.push(f.name))
  formData.samples?.forEach((sample, i) => {
    if (!sample.bodyRegion) list.push(`Submuestra ${i + 1}: Región del cuerpo`)
    if (!sample.tests?.length) list.push(`Submuestra ${i + 1}: Al menos una prueba`)
    sample.tests?.forEach((test, j) => {
      if (!test.code) list.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Código de prueba`)
      if (!test.quantity || test.quantity < 1) list.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Cantidad`)
    })
  })
  errors.samples?.forEach(e => list.push(`Submuestras: ${e}`))
  return list
})

// Field-level validation helpers
const getMedicoErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.requestingPhysician.length > 0) return errors.requestingPhysician
  if (!formData.requestingPhysician?.trim()) return ['El médico solicitante es obligatorio']
  return []
})
const getServicioErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  if (errors.service.length > 0) return errors.service
  if (!formData.service?.trim()) return ['El servicio es obligatorio']
  return []
})
const getRegionErrors = (sampleIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const sample = formData.samples[sampleIndex]
  if (!sample || !sample.bodyRegion?.trim()) return ['La región del cuerpo es obligatoria']
  return [] as string[]
}
const getPruebaErrors = (sampleIndex: number, testIndex: number) => {
  if (!validationState.hasAttemptedSubmit) return [] as string[]
  const sample = formData.samples[sampleIndex]
  if (!sample) return ['Debe seleccionar una prueba']
  const test = sample.tests[testIndex]
  if (!test || !String(test.code || '').trim()) return ['El código de la prueba es obligatorio']
  if (test.quantity == null || Number(test.quantity) < 1) return ['La cantidad debe ser al menos 1']
  return [] as string[]
}

// Friendly date/time rendering for the created case banner
const createdDateDisplay = computed(() => {
  const value = createdCase.value?.entryDate || formData.entryDate
  if (!value) return ''
  const isDateOnly = /^\d{4}-\d{2}-\d{2}$/.test(String(value))
  const date = new Date(isDateOnly ? `${value}T00:00:00` : String(value))
  if (isNaN(date.getTime())) return String(value)
  const datePart = new Intl.DateTimeFormat('es-CO', { day: '2-digit', month: 'long', year: 'numeric' }).format(date)
  return isDateOnly ? datePart : `${datePart} ${new Intl.DateTimeFormat('es-CO', { hour: '2-digit', minute: '2-digit' }).format(date)}`
})

// Normalize samples for notification (merge backend and form)
const getMuestrasForNotification = () => {
  const backendSamples = createdCase.value?.samples || []
  const formSamples = formData.samples || []
  return !backendSamples.length ? formSamples : backendSamples.map((s: any, i: number) => ({
    ...s,
    bodyRegion: s.bodyRegion || s.body_region || formSamples[i]?.bodyRegion || 'Sin especificar',
    tests: (s.tests || []).map((t: any, ti: number) => ({ ...t, quantity: t.quantity || formSamples[i]?.tests?.[ti]?.quantity || 1 }))
  }))
}

// Search patient and prefill form
const searchPatient = async () => {
  if (!pacienteCodeBusqueda.value.trim()) return
  const result = await searchPatientByDocumento(pacienteCodeBusqueda.value)
  if ((result as any).found && (result as any).patient) {
    const patient = (result as any).patient as PatientData
    updateFormDataWithPatient(patient)
    emit('patient-verified', patient)
  }
}

// Prefill entity and care type from verified patient
const updateFormDataWithPatient = (patientData: PatientData) => {
  const careType = String(patientData.careType || '').toLowerCase()
  Object.assign(formData, {
    patientDocument: patientData.patientCode,
    patientEntity: patientData.entityCode || '',
    patientCareType: careType.includes('ambulator') || careType === 'ambulatorio' ? 'Ambulatorio' : careType.includes('hospital') || careType === 'hospitalizado' ? 'Hospitalizado' : ''
  })
}

// Translation helpers (backend -> Spanish labels)
const translateCaseState = (value: any): string => {
  const raw = String(value || '').toLowerCase()
  const map: Record<string, string> = { 'in process': 'En proceso', 'in_process': 'En proceso', processing: 'En proceso', 'to sign': 'Para firma', 'to deliver': 'Para entregar', completed: 'Completado', finished: 'Completado', cancelled: 'Cancelado', canceled: 'Cancelado', pending: 'Pendiente' }
  return map[raw] || 'En proceso'
}
const translateCasePriority = (value: any): string => {
  const raw = String(value || '').toLowerCase()
  const map: Record<string, string> = { normal: 'Normal', priority: 'Prioritario', prioritario: 'Prioritario' }
  return map[raw] || 'Normal'
}
const translateGender = (value: any): string => {
  const raw = String(value || '').toLowerCase()
  const map: Record<string, string> = { male: 'Masculino', masculino: 'Masculino', m: 'Masculino', female: 'Femenino', femenino: 'Femenino', f: 'Femenino' }
  return map[raw] || String(value || '')
}
const translateCareType = (value: any): string => {
  const raw = String(value || '').toLowerCase()
  const map: Record<string, string> = { ambulatory: 'Ambulatorio', ambulatorio: 'Ambulatorio', hospitalized: 'Hospitalizado', hospitalizado: 'Hospitalizado' }
  return map[raw] || String(value || '')
}

// Displays for notification dialog
const stateDisplay = computed(() => translateCaseState((createdCase.value?.state as any) || 'In process'))
const priorityDisplay = computed(() => translateCasePriority((createdCase.value?.priority as any) || (formData.casePriority as any) || 'Normal'))
const genderDisplay = computed(() => translateGender((createdCase.value?.patient?.gender as any) || (verifiedPatient.value?.gender as any)))
const careTypeDisplay = computed(() => translateCareType((createdCase.value?.patient?.careType as any) || (verifiedPatient.value?.careType as any)))

// Clear fields when resetting patient verification
const clearPatientFormData = () => { Object.assign(formData, { patientDocument: '', patientEntity: '', patientCareType: '', casePriority: 'Normal', service: '' }) }
const clearPatientVerification = () => { clearVerification(); pacienteCodeBusqueda.value = ''; clearPatientFormData() }

// Handle new patient created elsewhere
const handleNewPatient = (patientData: PatientData) => { useNewPatient(patientData); pacienteCodeBusqueda.value = patientData.patientCode; updateFormDataWithPatient(patientData); emit('patient-verified', patientData) }

// Auto-scroll to notification when visible
const scrollToNotification = async () => { await nextTick(); if (notificationContainer.value) notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' }) }
watch(() => notification.visible, (v) => { if (v) scrollToNotification() })

// Copy created case code to clipboard
const copyCaseCode = async () => {
  if (!createdCase.value?.code) return
  const code = createdCase.value.code
  const message = `El código ${code} se ha copiado al portapapeles.`
  try { await navigator.clipboard.writeText(code); showNotification('success', 'Código copiado', message, 3000) }
  catch { const t = document.createElement('textarea'); t.value = code; document.body.appendChild(t); t.select(); document.execCommand('copy'); document.body.removeChild(t); showNotification('success', 'Código copiado', message, 3000) }
}

// Clear full form and related verification
const clearForm = () => { clearCaseForm(); clearPatientVerification() }

// Create case with validations and feedback
const handleSaveClick = async () => {
  const isValid = validateForm()
  if (!isValid) { validationState.showValidationError = true; return }
  if (!patientVerified.value || !verifiedPatient.value) { showNotification('error', 'Paciente Requerido', 'Debe buscar y verificar un paciente antes de crear el caso.', 5000); return }
  validationState.showValidationError = false
  clearState()
  try {
    const result = await createCase(formData, verifiedPatient.value)
    if (result.success && result.case) {
      createdCase.value = result.case
      showNotification('success', '¡Caso Creado Exitosamente!', '', 0)
      emit('case-saved', result.case)
      try { window.dispatchEvent(new CustomEvent('case-created')) } catch {}
      clearForm()
    } else {
      throw new Error(result.message || 'Error desconocido al crear el caso')
    }
  } catch (error: any) {
    showNotification('error', 'Error al Guardar Caso', apiError.value || error.message || 'No se pudo guardar el caso. Por favor, inténtelo nuevamente.', 0)
  }
}

// Update selected test for a given sample/test index
const onTestSelected = (sampleIndex: number, testIndex: number, test: any) => {
  if (!test) return
  const sample = formData.samples?.[sampleIndex]
  if (!sample) return
  const t = sample.tests?.[testIndex]
  if (!t) return
  t.code = test.pruebaCode || test.code || ''
  t.name = test.pruebasName || test.nombre || test.label || ''
}

defineExpose({ handleNewPatient, stateDisplay, priorityDisplay, genderDisplay, careTypeDisplay })
</script>
