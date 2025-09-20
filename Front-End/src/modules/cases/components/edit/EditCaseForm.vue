<template>
  <div class="space-y-6">
    <form class="space-y-4" @submit.prevent="onSubmit">
      <div v-if="!caseCodeProp" class="bg-gray-50 rounded-lg border border-gray-200">
        <div class="px-4 pt-4 pb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Buscar caso para editar
          </h3>
      
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
            <div class="flex-1">
              <FormInputField
                v-model="searchCaseCode"
                type="text"
                placeholder="Ejemplo: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isSearching"
                @update:model-value="handleCaseCodeChange"
                @keydown.enter.prevent="searchCase"
                @input="handleNumericInput"
              />
              <div v-if="searchCaseCode && !isValidCaseCodeFormat(searchCaseCode)" class="mt-1 text-xs text-red-600">
                El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
              </div>
            </div>
            <div class="flex gap-2 sm:gap-3">
              <SearchButton text="Buscar" loading-text="Buscando..." :loading="isSearching" @click="searchCase" size="md" variant="primary" />
              <ClearButton v-if="caseFound" text="Limpiar" @click="onReset" />
            </div>
          </div>

          <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <p class="text-sm text-red-600">{{ searchError }}</p>
            </div>
          </div>

          <div v-if="caseFound && foundCaseInfo && isCaseCompleted" class="mt-4 p-4 bg-red-50 border-l-4 border-red-400 rounded-r-lg">
            <div class="flex items-center mb-4">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <h4 class="text-sm sm:text-base font-semibold text-red-800">Caso Completado - No Editable</h4>
            </div>
            <div class="bg-white border border-red-200 rounded-lg shadow-sm p-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Nombre</p>
                  <p class="text-gray-900 break-words font-semibold">{{ foundCaseInfo.patient_info?.name || foundCaseInfo.paciente?.nombre || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Código</p>
                  <p class="text-gray-900 font-mono font-semibold">{{ foundCaseInfo.patient_info?.patient_code || foundCaseInfo.paciente?.paciente_code || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Edad</p>
                  <p class="text-gray-900 font-semibold">{{ (foundCaseInfo.patient_info?.age ?? foundCaseInfo.paciente?.edad ?? 'N/A') + (foundCaseInfo.patient_info?.age || foundCaseInfo.paciente?.edad ? ' años' : '') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Sexo</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ translateGender(foundCaseInfo.patient_info?.gender || foundCaseInfo.paciente?.sexo) }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Tipo de Atención</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ translateCareType(foundCaseInfo.patient_info?.care_type || foundCaseInfo.paciente?.tipo_atencion) }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Entidad</p>
                  <p class="text-gray-900 break-words font-semibold">{{ (foundCaseInfo.patient_info?.entity_info as any)?.name || foundCaseInfo.paciente?.entidad_info?.nombre || foundCaseInfo.entidad_info?.nombre || 'N/A' }}</p>
                </div>
                <div class="space-y-1 sm:col-span-2">
                  <p class="text-gray-600 font-medium">Estado del Caso</p>
                  <p class="text-red-600 font-semibold">{{ translateCaseState(foundCaseInfo.state || foundCaseInfo.estado) }}</p>
                </div>
              </div>
            </div>
          </div>

          <div v-if="caseFound && foundCaseInfo && !isCaseCompleted" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center mb-4">
              <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <h4 class="text-sm sm:text-base font-semibold text-green-800">Caso Encontrado y Cargado</h4>
            </div>
            <div class="bg-white border border-green-200 rounded-lg shadow-sm p-4">
              <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 text-sm">
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Nombre</p>
                  <p class="text-gray-900 break-words font-semibold">{{ getPatientInfo('nombre') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Código</p>
                  <p class="text-gray-900 font-mono font-semibold">{{ getPatientInfo('cedula') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Edad</p>
                  <p class="text-gray-900 font-semibold">{{ getPatientInfo('edad') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Sexo</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ getPatientInfo('sexo') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Tipo de Atención</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ getPatientInfo('tipoAtencion') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Entidad</p>
                  <p class="text-gray-900 break-words font-semibold">{{ getPatientInfo('entidad') }}</p>
                </div>
                  <div class="space-y-1">
                    <p class="text-gray-600 font-medium">Prioridad</p>
                    <p class="text-gray-900 font-semibold">{{ getFieldValue('prioridad', 'Normal') }}</p>
                  </div>
                  <div class="space-y-1">
                    <p class="text-gray-600 font-medium">Estado del Caso</p>
                    <p class="text-gray-900 font-semibold">{{ updatedCase?.state || updatedCase?.estado || 'Pendiente' }}</p>
                  </div>
              </div>
            </div>
          </div>
        </div>
      </div>


      <div v-if="!caseFound && !notification.visible" class="bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
        <div class="flex flex-col items-center space-y-3">
          <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          <h3 class="text-lg font-medium text-blue-800">Busque un caso para editar</h3>
          <p class="text-blue-600 text-sm">Ingrese el código del caso en el campo de búsqueda arriba para comenzar a editar</p>
        </div>
      </div>

      <div v-if="caseFound && !isCaseCompleted" class="space-y-6">
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList :key="'entity-' + resetKey" v-model="formData.patientEntity" label="Entidad del Paciente" placeholder="Seleciona la entidad" :required="true" :auto-load="true" @entity-selected="onEntitySelected" />
          <FormSelect :key="'tipoAtencion-' + resetKey + '-' + formData.patientCareType" v-model="formData.patientCareType" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.entryDate" label="Fecha de Ingreso" type="date" :required="true" help-text="Fecha en que ingresa el caso al sistema" />
          <FormSelect v-model="formData.casePriority" label="Prioridad del Caso" placeholder="Seleccione la prioridad" :required="true" :options="prioridadOptions" help-text="Nivel de urgencia del caso" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="formData.requestingPhysician" label="Médico Solicitante" placeholder="Ejemplo: Alberto Perez" :required="true" :max-length="200" help-text="Medico solicitante del estudio" />
          <FormInputField v-model="formData.service" label="Servicio" placeholder="Ejemplo: Medicina Interna" :required="true" :max-length="100" help-text="Área de procedencia del caso" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormSelect :key="'estado-' + resetKey" v-model="state" label="Estado del Caso" placeholder="Seleccione el estado" :required="true" :options="estadoOptions" />
          <PathologistList :key="'pathologist-' + resetKey" v-model="assignedPathologist" label="Patólogo Asignado" placeholder="Buscar patólogo..." :required="false" :auto-load="true" @pathologist-selected="onPathologistSelected" />
        </div>

        <div>
          <FormInputField class="max-w-xs" v-model="formData.numberOfSamples" label="Número de Muestras" type="number" :min="1" :max="99" :required="true" @input="handleLocalNumberOfSamplesChange" />
        </div>

        <div v-if="formData.samples.length > 0" class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(sample, sampleIndex) in formData.samples" :key="sample.number + '-' + resetKey" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">Submuestra #{{ sample.number }}</h4>
              
              <div class="mb-4">
                <BodyRegionList :key="'region-' + sampleIndex + '-' + resetKey" v-model="sample.bodyRegion" :label="`Región del Cuerpo`" placeholder="Buscar región del cuerpo..." :required="true" help-text="Seleccione la región anatómica de donde proviene la muestra" />
              </div>
              
              <div class="space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label class="block text-sm font-medium text-gray-700">Pruebas a realizar</label>
                  <div class="self-end sm:self-auto">
                    <AddButton text="Agregar Prueba" @click="addLocalTestToSample(sampleIndex)" />
                  </div>
                </div>
                
                <div class="space-y-2">
                  <div v-for="(test, testIndex) in sample.tests" :key="testIndex + '-' + resetKey" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-end">
                    <div class="flex-1 min-w-0">
                      <TestList 
                        :key="'test-' + sampleIndex + '-' + testIndex + '-' + resetKey" 
                        v-model="test.code" 
                        :label="`Prueba ${testIndex + 1}`" 
                        :placeholder="`Buscar y seleccionar prueba ${testIndex + 1}...`" 
                        :required="true" 
                        :auto-load="true" 
                        @test-selected="(test) => handleTestSelected(sampleIndex, testIndex, test)"
                      />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField v-model.number="test.quantity" label="Cantidad" type="number" :min="1" placeholder="Cantidad" />
                    </div>
                    <div class="flex items-end justify-center sm:w-10 pb-1">
                      <RemoveButton @click="removeLocalTestFromSample(sampleIndex, testIndex)" title="Eliminar prueba" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <FormTextarea v-model="formData.observations" label="Observaciones del Caso" placeholder="Observaciones adicionales sobre el caso o procedimiento..." :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional relevante para el procesamiento del caso" />

        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton 
            text="Guardar Cambios" 
            @click="onSubmit" 
            :disabled="isLoading || !isFormValid || isCaseCompleted" 
            :loading="isLoading" 
          />
        </div>

        <div v-if="caseFound && !isFormValid" class="mt-4 p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
          <div class="flex items-start">
            <svg class="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <div>
              <h4 class="text-sm font-semibold text-yellow-800 mb-2">Campos requeridos faltantes</h4>
              <p class="text-sm text-yellow-700 mb-2">Para guardar los cambios, debe completar los siguientes campos:</p>
              <ul class="list-disc list-inside space-y-1 text-sm text-yellow-700">
                <li v-for="error in validationErrors" :key="error">{{ error }}</li>
              </ul>
            </div>
          </div>
        </div>
      </div>
      
      <div ref="notificationContainer" v-if="notification.visible">
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="handleNotificationClosed">
          <template v-if="notification.type === 'success' && updatedCase" #content>
            <div class="relative p-4 sm:p-5 bg-white border border-gray-200 rounded-lg shadow-sm">
              <div class="space-y-4">
                <div class="text-center pb-3 border-b border-gray-200">
                  <p class="font-mono font-bold text-2xl text-gray-900">{{ getCaseCode() }}</p>
                </div>


                <div class="grid grid-cols-1 lg:grid-cols-2 gap-6">
                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Información del Paciente</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Nombre:</span><p class="text-gray-900 font-semibold">{{ getPatientInfo('nombre') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Cédula:</span><p class="text-gray-900 font-mono font-semibold">{{ getPatientInfo('cedula') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Edad:</span><p class="text-gray-900 font-semibold">{{ getPatientInfo('edad') }} años</p></div>
                      <div><span class="text-gray-500 font-medium">Sexo:</span><p class="text-gray-900 font-semibold">{{ getPatientInfo('sexo') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Entidad:</span><p class="text-gray-900 font-semibold">{{ getPatientInfo('entidad') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Tipo de Atención:</span><p class="text-gray-900 font-semibold">{{ getPatientInfo('tipoAtencion') }}</p></div>
                    </div>
                  </div>

                  <div>
                    <h4 class="font-semibold text-gray-800 mb-3 text-base">Detalles del Caso</h4>
                    <div class="space-y-2 text-sm">
                      <div><span class="text-gray-500 font-medium">Estado:</span><p class="text-gray-900 font-semibold">{{ updatedCase?.state || updatedCase?.estado || 'Pendiente' }}</p></div>
                      <div><span class="text-gray-500 font-medium">Prioridad:</span><p class="text-gray-900 font-semibold">{{ getFieldValue('prioridad', 'Normal') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Médico Solicitante:</span><p class="text-gray-900 font-semibold">{{ getFieldValue('medico') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Servicio:</span><p class="text-gray-900 font-semibold">{{ getFieldValue('servicio') }}</p></div>
                      <div><span class="text-gray-500 font-medium">Número de Submuestras:</span><p class="text-gray-900 font-semibold">{{ getMuestrasCount() }}</p></div>
                      <div v-if="getObservaciones()"><span class="text-gray-500 font-medium">Observaciones:</span><p class="text-gray-900">{{ getObservaciones() }}</p></div>
                    </div>
                  </div>
                </div>

                <div>
                  <h4 class="font-semibold text-gray-800 mb-3 text-base">Submuestras Actualizadas</h4>
                  <div class="space-y-3">
                    <div v-for="(sample, index) in getMuestras()" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900 text-sm">Submuestra #{{ index + 1 }}</span>
                        <span class="text-sm text-gray-500">{{ getPruebasCount(sample) }} prueba{{ getPruebasCount(sample) !== 1 ? 's' : '' }}</span>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div><span class="text-gray-500 font-medium">Región:</span><p class="text-gray-900">{{ sample.bodyRegion || 'Sin especificar' }}</p></div>
                        <div><span class="text-gray-500 font-medium">Pruebas:</span><div class="text-gray-900"><span v-if="sample.tests?.length > 0">{{ getPruebasText(sample) }}</span><span v-else class="text-gray-400">Sin pruebas</span></div></div>
                      </div>
                    </div>
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
import { ref, computed, watch, onMounted, nextTick } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { EntityList, TestList, BodyRegionList, PathologistList } from '@/shared/components/List'
import { useNotifications } from '../../composables/useNotifications'
import Notification from '@/shared/components/feedback/Notification.vue'
import { useCaseForm } from '../../composables/useCaseForm'
import { casesApiService } from '../../services/casesApi.service'
import pathologistApi from '../../services/pathologistApi.service'
import type { CaseModel } from '../../types'
import { TestIcon } from '@/assets/icons'

interface Props {
  caseCodeProp?: string
}

interface Emits {
  (e: 'case-updated', caseData: CaseModel): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { notification, showSuccess, showError, closeNotification } = useNotifications()
const { formData, errors, clearForm: clearCaseForm, handleNumberOfSamplesChange, addTestToSample, removeTestFromSample, createEmptySubSample } = useCaseForm()

const isLoading = ref(false)
const updatedCase = ref<any>(null)
const caseLoaded = ref(false)
const patientInfo = ref<any>(null)
const notificationContainer = ref<HTMLElement | null>(null)
const suppressValidation = ref(false)
const resetKey = ref(0)
const currentCaseCode = ref('')
const searchCaseCode = ref('')
const isSearching = ref(false)
const searchError = ref('')
const caseFound = ref(false)
const foundCaseInfo = ref<CaseModel | null>(null)

// Campos adicionales para edición
const state = ref('')
const assignedPathologist = ref('')

const tipoAtencionOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

const prioridadOptions = [
  { value: 'Normal', label: 'Normal' },
  { value: 'Prioritario', label: 'Prioritario' }
]

const estadoOptions = [
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Por firmar', label: 'Por firmar' },
  { value: 'Por entregar', label: 'Por entregar' },
  { value: 'Completado', label: 'Completado' }
]

const isFormValid = computed(() => {
  const baseOk = (
    formData.entryDate.trim() !== '' &&
    formData.requestingPhysician.trim() !== '' &&
    formData.service.trim() !== '' &&
    formData.patientEntity.trim() !== '' &&
    formData.patientCareType !== '' &&
    formData.casePriority !== '' &&
    state.value !== '' &&
    formData.numberOfSamples !== ''
  )
  const samplesOk = formData.samples.length > 0 && formData.samples.every(s => {
    if (!String(s.bodyRegion || '').trim()) return false
    if (!s.tests || s.tests.length === 0) return false
    return s.tests.every(t => String(t.code || '').trim() !== '' && (t.quantity ?? 0) >= 1)
  })
  return baseOk && samplesOk
})

const isCaseCompleted = computed(() => {
  const fc: any = foundCaseInfo.value || {}
  const estado = fc.estado || fc.state || ''
  const v = String(estado).toLowerCase()
  return v === 'completado' || v === 'completed'
})
const validationErrors = computed(() => {
  const errorsList: string[] = []
  const fields = [
    { value: formData.entryDate, name: 'Fecha de ingreso' },
    { value: formData.requestingPhysician, name: 'Médico solicitante' },
    { value: formData.service, name: 'Servicio' },
    { value: formData.casePriority, name: 'Prioridad del caso' },
    { value: state.value, name: 'Estado del caso' },
    { value: formData.numberOfSamples, name: 'Número de muestras' },
    { value: formData.patientEntity, name: 'Entidad del paciente' },
    { value: formData.patientCareType, name: 'Tipo de atención' }
  ]
  
  fields.forEach(field => !field.value && errorsList.push(field.name))
  
  formData.samples?.forEach((sample, i) => {
    if (!sample.bodyRegion) errorsList.push(`Submuestra ${i + 1}: Región del cuerpo`)
    if (!sample.tests?.length) errorsList.push(`Submuestra ${i + 1}: Al menos una prueba`)
    sample.tests?.forEach((test, j) => {
      if (!test.code) errorsList.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Código de prueba`)
      if (!test.quantity || test.quantity < 1) errorsList.push(`Submuestra ${i + 1}, Prueba ${j + 1}: Cantidad`)
    })
  })
  
  errors.samples?.forEach(error => errorsList.push(`Submuestras: ${error}`))
  return errorsList
})
const normalizeAttentionType = (value: string | undefined | null): string => {
  if (!value) return ''
  const v = String(value).toLowerCase()
  
  if (v.includes('ambulator') || v === 'outpatient' || v === 'ambulatory' || v === 'ambulatorio') return 'Ambulatorio'
  if (v.includes('hospital') || v === 'inpatient' || v === 'hospitalized' || v === 'hospitalizado') return 'Hospitalizado'
  
  return ''
}

const toInputDate = (value: string | undefined | null): string => {
  if (!value) return ''
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  const date = new Date(value)
  if (isNaN(date.getTime())) return ''
  return date.toISOString().split('T')[0]
}


const loadCaseData = async () => {
  if (!props.caseCodeProp) return

  isLoading.value = true
  try {
    const caseData = await casesApiService.getCaseByCode(props.caseCodeProp)
    await loadCaseDataFromFound(caseData)
  } catch (error: any) {
    showError('Error al cargar los datos del caso', error.message || 'Error desconocido')
  } finally {
    isLoading.value = false
  }
}

const onSubmit = async () => {
  const caseCode = props.caseCodeProp || (foundCaseInfo.value as any)?.case_code || (foundCaseInfo.value as any)?.caso_code
  
  if (isCaseCompleted.value) {
    showError('Caso completado', 'No se puede editar un caso que ya ha sido completado. Los casos completados no pueden ser modificados.')
    return
  }
  
  if (!isFormValid.value) {
    if (suppressValidation.value) {
      suppressValidation.value = false
      return
    }
    showError('Datos incompletos', 'Por favor complete todos los campos requeridos')
    return
  }
  
  if (!caseCode) {
    showError('Caso no identificado', 'Debe buscar un caso primero para poder editar sus datos')
    return
  }

  const cedulaToUse = formData.patientDocument || foundCaseInfo.value?.paciente?.paciente_code
  if (!cedulaToUse) {
    showError('Información incompleta', 'No se encontró información del paciente para este caso')
    return
  }

  isLoading.value = true
  try {
    const entityInfoToSend = selectedEntity.value?.codigo && selectedEntity.value?.nombre 
      ? { id: selectedEntity.value.codigo, nombre: selectedEntity.value.nombre }
      : undefined

    const mapTipoAtencionToBackend = (tipo: string): string => {
      // Mantener el formato original en español como lo espera el backend
      return tipo || 'Ambulatorio'
    }

    // Mantener valores en español como lo espera el backend
    const estadoToSend = state.value || 'En proceso'
    const prioridadToSend = formData.casePriority || 'Normal'

    const existingSamples = (foundCaseInfo.value?.muestras || []) as any[]
    const samplesClean = formData.samples.map((s, idx) => {
      const region = s.bodyRegion || existingSamples[idx]?.region_cuerpo || existingSamples[idx]?.regionCuerpo || ''
      return {
        body_region: region,
        tests: s.tests
          .filter(t => String(t.code).trim() !== '')
          .map(t => ({ id: t.code, name: t.name || t.code, quantity: t.quantity || 1 }))
      }
    })
    
    const allEmptyRegions = samplesClean.every(s => !s.body_region)
    const pacienteEntidad = entityInfoToSend || (formData.patientEntity && selectedEntity.value?.nombre
      ? { id: formData.patientEntity, nombre: selectedEntity.value?.nombre || '' }
      : undefined)

    const updateData: any = {
      state: estadoToSend as unknown as string,
      requesting_physician: formData.requestingPhysician || undefined,
      service: formData.service || undefined,
      priority: prioridadToSend,
      observations: formData.observations || undefined,
      assigned_pathologist: assignedPathologist.value ? {
        id: assignedPathologist.value,
        pathologist_code: assignedPathologist.value,
        name: selectedPathologist.value?.nombre || ''
      } : undefined,
      samples: allEmptyRegions && existingSamples.length ? undefined : samplesClean,
      patient_info: {
        patient_code: cedulaToUse,
        name: getPatientInfo('nombre') || '',
        age: parseInt(getPatientInfo('edad')) || 0,
        gender: getPatientInfo('sexo') || '',
        entity_info: pacienteEntidad ? { id: pacienteEntidad.id, name: pacienteEntidad.nombre } : { id: '', name: '' },
        care_type: mapTipoAtencionToBackend(formData.patientCareType),
        observations: (patientInfo.value as any)?.observaciones || undefined
      }
    }

    if (updateData.samples && updateData.samples.length) {
      updateData.samples = updateData.samples.filter((s: any) => s.body_region)
      if (!updateData.samples.length) delete updateData.samples
    } else if (!updateData.samples && foundCaseInfo.value?.muestras?.length) {
      delete updateData.samples
    }

    Object.keys(updateData).forEach(k => updateData[k] === undefined && delete updateData[k])
    if (updateData.patient_info) {
      Object.keys(updateData.patient_info).forEach(k => updateData.patient_info[k] === undefined && delete updateData.patient_info[k])
    }

    const updatedCaseResponse = await casesApiService.updateCase(caseCode, updateData)
    
    const uc = updatedCaseResponse as any
    const adapted = {
      ...uc,
      caso_code: uc.case_code || (foundCaseInfo.value as any)?.caso_code,
      paciente: uc.patient_info ? {
        paciente_code: uc.patient_info.patient_code,
        nombre: uc.patient_info.name,
        edad: uc.patient_info.age,
        sexo: uc.patient_info.gender,
        entidad_info: { nombre: uc.patient_info.entity_info?.name, id: uc.patient_info.entity_info?.id },
        tipo_atencion: uc.patient_info.care_type
      } : (updatedCase.value?.paciente || {}),
      prioridad: uc.priority || formData.casePriority,
      observaciones_generales: uc.observations || formData.observations,
      muestras: Array.isArray(uc.samples) ? uc.samples.map((s: any) => ({
        regionCuerpo: s.body_region,
        region_cuerpo: s.body_region,
        pruebas: (s.tests || []).map((t: any) => ({ id: t.id, nombre: t.name, cantidad: t.quantity }))
      })) : updatedCase.value?.muestras
    }
    updatedCase.value = adapted
    
    if (updatedCase.value) {
      if (!updatedCase.value.prioridad_caso && (updatedCase.value as any).prioridad) {
        updatedCase.value.prioridad_caso = (updatedCase.value as any).prioridad
      }
      if (!updatedCase.value.prioridad_caso && !updatedCase.value.prioridadCaso && formData.casePriority) {
        updatedCase.value.prioridad_caso = formData.casePriority
      }
    }
    
    emit('case-updated', updatedCaseResponse)
    showSuccess('¡Caso Actualizado Exitosamente!', '')
    clearFormAfterSave()
  } catch (error: any) {
    let msg = ''
    if (error?.response?.data) {
      const data = error.response.data
      if (typeof data === 'string') msg = data
      else if (data.detail) {
        if (Array.isArray(data.detail)) {
          msg = data.detail.map((d: any) => d.msg || d.message || JSON.stringify(d)).join(', ')
        } else if (typeof data.detail === 'object') {
          try { msg = JSON.stringify(data.detail) } catch { msg = String(data.detail) }
        } else msg = String(data.detail)
      } else if (data.message) {
        msg = data.message
      } else {
        try { msg = JSON.stringify(data) } catch { msg = 'Error desconocido del servidor' }
      }
    } else if (error?.message) {
      msg = error.message
    } else {
      try { msg = JSON.stringify(error) } catch { msg = 'Error desconocido' }
    }
    console.error('Error updateCase:', error)
    showError('Error al actualizar el caso', msg || 'Error desconocido')
  } finally {
    isLoading.value = false
  }
}

const isValidCaseCodeFormat = (code: string): boolean => {
  return /^\d{4}-\d{5}$/.test(code)
}

const handleCaseCodeChange = () => {
  searchError.value = ''
  caseFound.value = false
  foundCaseInfo.value = null
}

const handleNumericInput = (value: string) => {
  const numericValue = value.replace(/[^0-9-]/g, '')
  
  if (numericValue.length === 4 && !numericValue.includes('-')) {
    searchCaseCode.value = numericValue + '-'
  } else {
    searchCaseCode.value = numericValue
  }
}
const searchCase = async () => {
  if (!searchCaseCode.value.trim()) {
    searchError.value = 'Por favor ingrese un código de caso'
    return
  }

  if (!isValidCaseCodeFormat(searchCaseCode.value)) {
    searchError.value = 'El código debe tener el formato YYYY-NNNNN'
    return
  }

  isSearching.value = true
  searchError.value = ''
  caseFound.value = false

  try {
    const caseData = await casesApiService.getCaseByCode(searchCaseCode.value)
    
    if (caseData) {
      foundCaseInfo.value = caseData
      updatedCase.value = caseData
      caseFound.value = true
      await loadCaseDataFromFound(caseData)
    } else {
      searchError.value = `No se encontró un caso con el código ${searchCaseCode.value}`
      caseFound.value = false
      foundCaseInfo.value = null
    }
  } catch (error: any) {
    if (error.message.includes('404') || error.message.includes('No encontrado')) {
      searchError.value = 'No se encontró un caso con el código especificado.'
    } else {
      searchError.value = 'Error al buscar el caso. Verifique el código e intente nuevamente.'
    }
    caseFound.value = false
    foundCaseInfo.value = null
  } finally {
    isSearching.value = false
  }
}

const loadCaseDataFromFound = async (caseData: CaseModel) => {
  try {
    currentCaseCode.value = (caseData as any).case_code || (caseData as any).caso_code || searchCaseCode.value || props.caseCodeProp || ''

    foundCaseInfo.value = caseData
    updatedCase.value = caseData
    caseFound.value = true
    const getField = (paths: string[], fallback: any = '') => {
      for (const path of paths) {
        const value = path.split('.').reduce((obj: any, key: string) => obj?.[key], caseData)
        if (value !== undefined && value !== null) return value
      }
      return fallback
    }

    const caseFormData = {
      patientDocument: getField([
        'patient_info.patient_code',
        'paciente.paciente_code', 
        'paciente.numeroCedula',
        'cedula_paciente'
      ]),
        
      entryDate: toInputDate(getField([
        'created_at',
        'fecha_creacion',
        'fechaCreacion',
        'fecha_creacion.$date'
      ])),
        
      requestingPhysician: (() => {
        const medico = getField(['requesting_physician', 'medico_solicitante', 'medicoSolicitante'])
        return typeof medico === 'object' && medico?.nombre ? medico.nombre : medico || ''
      })(),
        
      service: getField(['service', 'servicio']),
      casePriority: getField(['priority', 'prioridad_caso', 'prioridadCaso', 'prioridad'], 'Normal'),
        
      patientEntity: getField([
        'patient_info.entity_info.id',
        'entidad_info.id',
        'entidad_info.codigo',
        'paciente.entidad_info.id',
        'paciente.entidad_info.codigo',
        'entidadPaciente',
        'entidad_codigo'
      ]),
        
      patientCareType: normalizeAttentionType(getField([
        'patient_info.care_type',
        'paciente.tipo_atencion',
        'tipo_atencion',
        'tipoAtencionPaciente'
      ])),
        
      numberOfSamples: (getField(['muestras.length', 'samples.length', 'numeroMuestras'], 1)).toString(),
         
      samples: (() => {
        const samples = getField(['samples', 'muestras'], [])
        
        if (samples?.length > 0) {
          return samples.map((sample: any, index: number) => ({
            number: index + 1,
            bodyRegion: sample?.body_region || sample?.region_cuerpo || sample?.regionCuerpo || '',
            tests: (() => {
              const tests = sample?.tests || sample?.pruebas || []
              return tests?.length > 0 ? tests.map((test: any) => ({
                code: test?.id || test?.code || test?.codigo || '',
                quantity: test?.quantity || test?.cantidad || 1,
                name: test?.name || test?.nombre || ''
              })) : [{ code: '', quantity: 1, name: '' }]
            })()
          }))
        }
        return [createEmptySubSample(1)]
      })(),
      
      observations: getField(['observations', 'observaciones_generales', 'observacionesGenerales', 'patient_info.observations'])
    }
    
    Object.assign(formData, caseFormData)
    state.value = translateCaseState(getField(['state', 'estado'], 'En proceso'))
    assignedPathologist.value = getField([
      'assigned_pathologist.id',
      'assigned_pathologist.pathologist_code',
      'patologo_asignado.codigo'
    ])
    patientInfo.value = {
      pacienteCode: getField(['patient_info.patient_code', 'paciente.paciente_code', 'paciente.numeroCedula', 'cedula_paciente'], formData.patientDocument),
      nombrePaciente: getField(['patient_info.name', 'paciente.nombre', 'paciente.nombrePaciente', 'nombre_paciente'], 'Sin nombre'),
      edad: String(getField(['patient_info.age', 'paciente.edad', 'edad_paciente'], 0)),
      sexo: getField(['patient_info.gender', 'paciente.sexo', 'sexo_paciente'], 'Sin especificar'),
      entidad: getField(['patient_info.entity_info.name', 'entidad_info.nombre', 'paciente.entidad_info.nombre'], 'Sin especificar'),
      tipoAtencion: getField(['patient_info.care_type', 'paciente.tipo_atencion'], 'Sin especificar'),
      observaciones: getField(['patient_info.observations', 'paciente.observaciones']),
      codigo: getField(['case_code', 'caso_code'])
    }
    
    const patologoAsignado = (caseData as any).assigned_pathologist || (caseData as any).patologo_asignado
    
    if (patologoAsignado?.id || patologoAsignado?.pathologist_code || patologoAsignado?.codigo) {
      const codigo = patologoAsignado.id || patologoAsignado.pathologist_code || patologoAsignado.codigo
      try {
        const pathologist = await pathologistApi.getPathologist(codigo)
        if (pathologist) {
        const patologoCode = pathologist.patologo_code || codigo
        const patologoData = {
          codigo: patologoCode,
          nombre: pathologist.patologo_name || pathologist.nombre || patologoAsignado.name || patologoAsignado.pathologist_name || patologoAsignado.nombre || ''
        }
        selectedPathologist.value = patologoData
        assignedPathologist.value = patologoCode
        onPathologistSelected(patologoData)
      } else {
        const patologoData = { codigo: codigo, nombre: patologoAsignado.nombre || '' }
        selectedPathologist.value = patologoData
        assignedPathologist.value = codigo
        onPathologistSelected(patologoData)
      }
    } catch (error) {
      const patologoData = { codigo: codigo, nombre: patologoAsignado.nombre || '' }
      selectedPathologist.value = patologoData
      assignedPathologist.value = codigo
      onPathologistSelected(patologoData)
    }
  } else {
    selectedPathologist.value = null
    assignedPathologist.value = ''
  }
    
    const entityPaths = [
      'patient_info.entity_info',
      'entidad_info',
      'paciente.entidad_info'
    ]
    
    const entityData = entityPaths.find(path => {
      const entity = getField([path])
      return entity?.id || entity?.codigo
    })
    
    if (entityData) {
      const entity = getField([entityData])
      selectedEntity.value = {
        codigo: entity.id || entity.codigo,
        nombre: entity.name || entity.nombre
      }
    } else {
      selectedEntity.value = null
    }

    caseLoaded.value = true
  } catch (error: any) {
    showError('Error al cargar datos del caso', error.message || 'Error desconocido')
  }
}

const onReset = () => {
  suppressValidation.value = true
  searchCaseCode.value = ''
  searchError.value = ''
  caseFound.value = false
  foundCaseInfo.value = null
  
  clearCaseForm()
  state.value = ''
  assignedPathologist.value = ''
  
  patientInfo.value = {
    nombre: '',
    cedula: '',
    edad: 0,
    sexo: '',
    entidad: '',
    tipoAtencion: ''
  }
  selectedPathologist.value = null
  selectedEntity.value = null
  caseLoaded.value = false
  currentCaseCode.value = ''
  updatedCase.value = null
  closeNotification()
  resetKey.value++
}

const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const onEntitySelected = (entity: any | null) => {
  if (entity && entity.codigo) {
    selectedEntity.value = { codigo: entity.codigo, nombre: entity.nombre }
  } else {
    selectedEntity.value = null
  }
}

const selectedPathologist = ref<{ codigo: string; nombre: string } | null>(null)
const onPathologistSelected = (pathologist: any | null) => {
  if (pathologist) {
    const codigo = pathologist.patologo_code || pathologist.codigo || pathologist.code || pathologist.documento || pathologist.id || ''
    const nombre = pathologist.patologo_name || pathologist.nombre || pathologist.name || ''
    selectedPathologist.value = { codigo, nombre }
    assignedPathologist.value = codigo
  } else {
    selectedPathologist.value = null
    assignedPathologist.value = ''
  }
}

const handleLocalNumberOfSamplesChange = (newNumber: string): void => {
  handleNumberOfSamplesChange(newNumber)
}

const addLocalTestToSample = (sampleIndex: number): void => {
  addTestToSample(sampleIndex)
}

const removeLocalTestFromSample = (sampleIndex: number, testIndex: number): void => {
  removeTestFromSample(sampleIndex, testIndex)
}

const handleTestSelected = (sampleIndex: number, testIndex: number, test: any) => {
  if (test && sampleIndex >= 0 && sampleIndex < formData.samples.length) {
    const sample = formData.samples[sampleIndex]
    if (testIndex >= 0 && testIndex < sample.tests.length) {
      sample.tests[testIndex].code = test.pruebaCode || test.code || ''
      sample.tests[testIndex].name = test.pruebasName || test.nombre || test.label || ''
    }
  }
}

const clearFormAfterSave = () => {
  clearCaseForm()
  state.value = ''
  assignedPathologist.value = ''

  searchCaseCode.value = ''
  searchError.value = ''
  caseFound.value = false
  caseLoaded.value = false
}

const getPatientInfo = (field: string): string => {
  const cp: any = patientInfo.value || {}
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}

  switch (field) {
    case 'nombre': 
      return cp.nombrePaciente || uc.patient_info?.name || fc.patient_info?.name || uc.paciente?.nombre || fc.paciente?.nombre || 'N/A'
    case 'cedula': 
      return cp.pacienteCode || uc.patient_info?.patient_code || fc.patient_info?.patient_code || uc.paciente?.paciente_code || fc.paciente?.paciente_code || 'N/A'
    case 'edad': {
      const edad = cp.edad ?? uc.patient_info?.age ?? fc.patient_info?.age ?? uc.paciente?.edad ?? fc.paciente?.edad
      return edad !== undefined && edad !== null ? String(edad) : 'N/A'
    }
    case 'sexo': 
      return translateGender(cp.sexo || uc.patient_info?.gender || fc.patient_info?.gender || uc.paciente?.sexo || fc.paciente?.sexo)
    case 'entidad': 
      return cp.entidad || uc.patient_info?.entity_info?.name || fc.patient_info?.entity_info?.name || uc.paciente?.entidad_info?.nombre || fc.paciente?.entidad_info?.nombre || 'N/A'
    case 'tipoAtencion': 
      return translateCareType(cp.tipoAtencion || uc.patient_info?.care_type || fc.patient_info?.care_type || uc.paciente?.tipo_atencion || fc.paciente?.tipo_atencion)
    default: return 'N/A'
  }
}

const getMuestrasCount = (): number => {
  const uc: any = updatedCase.value || {}
  return uc?.samples?.length || uc?.muestras?.length || formData.samples.length
}

const getObservaciones = (): string => {
  const uc: any = updatedCase.value || {}
  return uc?.observations || uc?.observaciones_generales || uc?.observacionesGenerales || formData.observations || ''
}

const getMuestras = () => {
  const backendSamples = (updatedCase.value as any)?.samples || (updatedCase.value as any)?.muestras || []
  const formSamples = formData.samples || []
  
  if (!backendSamples.length) return formSamples
  
  return backendSamples.map((backendSample: any, index: number) => {
    const formSample = formSamples[index]
    return {
      ...backendSample,
      bodyRegion: backendSample.body_region || backendSample.regionCuerpo || backendSample.region_cuerpo || formSample?.bodyRegion || 'Sin especificar',
      tests: (backendSample.tests || backendSample.pruebas || []).map((test: any, tIndex: number) => ({
        ...test,
        id: test.id || test.code || test.codigo,
        name: test.name || test.nombre,
        quantity: test.quantity || test.cantidad || formSample?.tests?.[tIndex]?.quantity || 1
      }))
    }
  })
}

const getPruebasCount = (sample: any): number => {
  return (sample.tests && sample.tests.length) || (sample.pruebas && sample.pruebas.length) || 0
}

const getPruebasText = (sample: any): string => {
  return (sample.tests || sample.pruebas || []).map((t: any) => {
    const codigo = t.id || t.code || t.codigo || ''
    const nombre = t.name || t.nombre || ''
    const etiqueta = codigo || nombre || 'Sin código'
    return `${etiqueta} (${t.quantity || t.cantidad || 1})`
  }).join(', ')
}

const getFieldValue = (field: string, fallback: string = 'No especificado'): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  const fieldMap: Record<string, string> = {
    'medico': uc.requesting_physician || fc.requesting_physician || formData.requestingPhysician,
    'servicio': uc.service || fc.service || formData.service,
    'prioridad': uc.priority || fc.priority || formData.casePriority
  }
  return fieldMap[field] || fallback
}

const getCaseCode = (): string => {
  return currentCaseCode.value || 
         (foundCaseInfo.value as any)?.case_code || 
         (foundCaseInfo.value as any)?.caso_code || 
         (updatedCase.value as any)?.case_code || 
         (updatedCase.value as any)?.caso_code || 
         (updatedCase.value as any)?.code || 
         searchCaseCode.value || 
         props.caseCodeProp || 
         'N/A'
}

watch(
  () => props.caseCodeProp,
  (newCode) => {
    if (newCode) {
      loadCaseData()
    }
  },
  { immediate: true }
)

watch(
  () => notification.visible,
  async (newValue) => {
    if (newValue) {
      await nextTick()
      if (notificationContainer.value) {
        notificationContainer.value.scrollIntoView({
          behavior: 'smooth',
          block: 'center'
        })
      }
    }
  }
)

const handleNotificationClosed = () => {
  suppressValidation.value = true
  closeNotification()
}

onMounted(() => {
  if (props.caseCodeProp) {
    loadCaseData()
  }
})

const translateValue = (value: any, type: 'state' | 'gender' | 'careType'): string => {
  const raw = String(value || '').toLowerCase()
  
  const maps: Record<string, Record<string, string>> = {
    state: {
      'in process': 'En proceso',
      'in_process': 'En proceso',
      'processing': 'En proceso',
      'to sign': 'Para firma',
      'to deliver': 'Para entregar',
      'completed': 'Completado',
      'finished': 'Completado',
      'cancelled': 'Cancelado',
      'canceled': 'Cancelado',
      'pending': 'Pendiente'
    },
    gender: {
      'male': 'Masculino',
      'masculino': 'Masculino',
      'm': 'Masculino',
      'female': 'Femenino',
      'femenino': 'Femenino',
      'f': 'Femenino'
    },
    careType: {
      'ambulatory': 'Ambulatorio',
      'ambulatorio': 'Ambulatorio',
      'outpatient': 'Ambulatorio',
      'hospitalized': 'Hospitalizado',
      'hospitalizado': 'Hospitalizado',
      'inpatient': 'Hospitalizado'
    }
  }
  
  const fallbacks = {
    state: 'En proceso',
    gender: String(value || ''),
    careType: String(value || '')
  }
  
  return maps[type]?.[raw] || fallbacks[type]
}

const translateCaseState = (value: any) => translateValue(value, 'state')
const translateGender = (value: any) => translateValue(value, 'gender')
const translateCareType = (value: any) => translateValue(value, 'careType')
</script>