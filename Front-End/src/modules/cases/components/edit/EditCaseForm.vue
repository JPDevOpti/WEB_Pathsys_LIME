<template>
  <div class="space-y-6">
    <!-- Título con icono -->

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

          <!-- Advertencia para casos completados -->
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
                  <p class="text-gray-900 break-words font-semibold">{{ foundCaseInfo.paciente?.nombre || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Código</p>
                  <p class="text-gray-900 font-mono font-semibold">{{ foundCaseInfo.paciente?.paciente_code || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Edad</p>
                  <p class="text-gray-900 font-semibold">{{ (foundCaseInfo.paciente?.edad ?? 'N/A') + (foundCaseInfo.paciente?.edad ? ' años' : '') }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Sexo</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ foundCaseInfo.paciente?.sexo || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Tipo de Atención</p>
                  <p class="text-gray-900 font-semibold capitalize">{{ foundCaseInfo.paciente?.tipo_atencion || 'N/A' }}</p>
                </div>
                <div class="space-y-1">
                  <p class="text-gray-600 font-medium">Entidad</p>
                  <p class="text-gray-900 break-words font-semibold">{{ foundCaseInfo.paciente?.entidad_info?.nombre || foundCaseInfo.entidad_info?.nombre || 'N/A' }}</p>
                </div>
                <div class="space-y-1 sm:col-span-2">
                  <p class="text-gray-600 font-medium">Estado del Caso</p>
                  <p class="text-red-600 font-semibold">{{ foundCaseInfo.estado || 'N/A' }}</p>
                </div>
              </div>
            </div>
          </div>

          <!-- Información normal para casos editables -->
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
                    <p class="text-gray-900 font-semibold">{{ getPrioridad() }}</p>
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
        <!-- Campos de entidad y tipo de atención -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList :key="'entity-' + resetKey" v-model="form.patientEntity" label="Entidad del Paciente" placeholder="Seleciona la entidad" :required="true" :auto-load="true" @entity-selected="onEntitySelected" />
          <FormSelect :key="'tipoAtencion-' + resetKey + '-' + form.patientCareType" v-model="form.patientCareType" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" />
        </div>

        <!-- Campos de fecha de ingreso y prioridad -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="form.entryDate" label="Fecha de Ingreso" type="date" :required="true" help-text="Fecha en que ingresa el caso al sistema" />
          <FormSelect v-model="form.casePriority" label="Prioridad del Caso" placeholder="Seleccione la prioridad" :required="true" :options="prioridadOptions" help-text="Nivel de urgencia del caso" />
        </div>

        <!-- Campos de médico solicitante y servicio -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="form.requestingPhysician" label="Médico Solicitante" placeholder="Ejemplo: Alberto Perez" :required="true" :max-length="200" help-text="Medico solicitante del estudio" />
          <FormInputField v-model="form.service" label="Servicio" placeholder="Ejemplo: Medicina Interna" :required="true" :max-length="100" help-text="Área de procedencia del caso" />
        </div>

        <!-- Estado y Patólogo en una sola línea -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormSelect :key="'estado-' + resetKey" v-model="form.state" label="Estado del Caso" placeholder="Seleccione el estado" :required="true" :options="estadoOptions" />
          <PathologistList :key="'pathologist-' + resetKey" v-model="form.assignedPathologist" label="Patólogo Asignado" placeholder="Buscar patólogo..." :required="false" :auto-load="true" @pathologist-selected="onPathologistSelected" />
        </div>

        <!-- Número de muestras debajo -->
        <div>
          <FormInputField class="max-w-xs" v-model="form.numberOfSamples" label="Número de Muestras" type="number" :min="1" :max="99" :required="true" @input="handleLocalNumberOfSamplesChange" />
        </div>

        <div v-if="form.samples.length > 0" class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(sample, sampleIndex) in form.samples" :key="sample.number + '-' + resetKey" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
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
                      <TestList :key="'test-' + sampleIndex + '-' + testIndex + '-' + resetKey" v-model="test.code" :label="`Prueba ${testIndex + 1}`" :placeholder="`Buscar y seleccionar prueba ${testIndex + 1}...`" :required="true" :auto-load="true" @test-selected="(test) => handleTestSelected(sampleIndex, testIndex, test)" />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField v-model.number="test.quantity" label="Cantidad" type="number" :min="1" :max="10" placeholder="Cantidad" />
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

        <FormTextarea v-model="form.observations" label="Observaciones del Caso" placeholder="Observaciones adicionales sobre el caso o procedimiento..." :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional relevante para el procesamiento del caso" />

        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton 
            text="Guardar Cambios" 
            @click="onSubmit" 
            :disabled="isLoading || !isFormValid || isCaseCompleted" 
            :loading="isLoading" 
          />
        </div>

        <!-- Notificación de campos faltantes -->
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
                      <div><span class="text-gray-500 font-medium">Prioridad:</span><p class="text-gray-900 font-semibold">{{ getPrioridad() }}</p></div>
                      <div><span class="text-gray-500 font-medium">Médico Solicitante:</span><p class="text-gray-900 font-semibold">{{ getMedicoSolicitante() }}</p></div>
                      <div><span class="text-gray-500 font-medium">Servicio:</span><p class="text-gray-900 font-semibold">{{ getServicio() }}</p></div>
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
import { reactive, ref, computed, watch, onMounted, nextTick } from 'vue'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton, SearchButton, AddButton, RemoveButton } from '@/shared/components/buttons'
import { EntityList, TestList, BodyRegionList, PathologistList } from '@/shared/components/List'
import { useNotifications } from '../../composables/useNotifications'
import Notification from '@/shared/components/feedback/Notification.vue'
import { useCaseForm } from '../../composables/useCaseForm'
import { casesApiService } from '../../services/casesApi.service'
import { patientsApiService } from '../../services/patientsApi.service'
import pathologistApi from '../../services/pathologistApi.service'
import type { CaseFormData, CaseModel } from '../../types'
import { TestIcon } from '@/assets/icons'

// ============================================================================
// PROPS Y EMITS
// ============================================================================

interface Props {
  caseCodeProp?: string
}

interface Emits {
  (e: 'case-updated', caseData: CaseModel): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

// ============================================================================
// COMPOSABLES
// ============================================================================

const { notification, showSuccess, showError, closeNotification } = useNotifications()

// Crear instancia independiente del composable para utilidades
const caseFormUtils = useCaseForm()
const {
  createEmptySubSample
} = caseFormUtils

// ============================================================================
// ESTADO
// ============================================================================

const isLoading = ref(false)
const originalData = ref<CaseFormData | null>(null)

// Estado del caso actualizado para la notificación
const updatedCase = ref<any>(null)
const caseLoaded = ref(false)
const patientInfo = ref<any>(null)

// Referencia para la notificación
const notificationContainer = ref<HTMLElement | null>(null)
// Evita mostrar validaciones justo después de limpiar o cerrar una notificación
const suppressValidation = ref(false)
// Clave para forzar remonte de componentes controlados y limpiar su estado interno
const resetKey = ref(0)

// Código del caso actual (para mostrar en la notificación)
const currentCaseCode = ref('')

// Estado para búsqueda de casos
const searchCaseCode = ref('')
const isSearching = ref(false)
const searchError = ref('')
const caseFound = ref(false)
const foundCaseInfo = ref<CaseModel | null>(null)

const form = reactive<CaseFormData & { state: string; assignedPathologist?: string; service: string }>({
  patientDocument: '',
  entryDate: '',
  requestingPhysician: '',
  service: '',
  patientEntity: '',
  patientCareType: '',
  casePriority: '',
  numberOfSamples: '0',
  samples: [],
  observations: '',
  state: '',
  assignedPathologist: ''
})

const tipoAtencionOptions = [
  { value: 'ambulatorio', label: 'Ambulatorio' },
  { value: 'hospitalizado', label: 'Hospitalizado' },
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

// ============================================================================
// COMPUTED
// ============================================================================

const isFormValid = computed(() => {
  const baseOk = (
    form.entryDate.trim() !== '' &&
    form.requestingPhysician.trim() !== '' &&
    form.service.trim() !== '' &&
    form.patientEntity.trim() !== '' &&
    form.patientCareType !== '' &&
    form.casePriority !== '' &&
    form.state !== '' &&
    form.numberOfSamples !== ''
  )
  const samplesOk = form.samples.length > 0 && form.samples.every(s => {
    if (!String(s.bodyRegion || '').trim()) return false
    if (!s.tests || s.tests.length === 0) return false
    return s.tests.every(t => String(t.code || '').trim() !== '' && (t.quantity ?? 0) >= 1)
  })
  return baseOk && samplesOk
})

// Computed para verificar si el caso está completado
const isCaseCompleted = computed(() => {
  const fc: any = foundCaseInfo.value || {}
  const estado = fc.estado || fc.state || ''
  const v = String(estado).toLowerCase()
  return v === 'completado' || v === 'completed'
})

// Validación de errores del formulario
const validationErrors = computed(() => {
  const validationErrorsList: string[] = []
  
  // Campos básicos del formulario
  if (!form.entryDate) validationErrorsList.push('Fecha de ingreso')
  if (!form.requestingPhysician) validationErrorsList.push('Médico solicitante')
  if (!form.service) validationErrorsList.push('Servicio')
  if (!form.casePriority) validationErrorsList.push('Prioridad del caso')
  if (!form.state) validationErrorsList.push('Estado del caso')
  if (!form.numberOfSamples) validationErrorsList.push('Número de muestras')
  if (!form.patientEntity) validationErrorsList.push('Entidad del paciente')
  if (!form.patientCareType) validationErrorsList.push('Tipo de atención')
  
  // Validación detallada de submuestras
  if (form.samples && form.samples.length > 0) {
    form.samples.forEach((sample, index) => {
      if (!sample.bodyRegion) {
        validationErrorsList.push(`Submuestra ${index + 1}: Región del cuerpo`)
      }
      if (!sample.tests || sample.tests.length === 0) {
        validationErrorsList.push(`Submuestra ${index + 1}: Al menos una prueba`)
      } else {
        sample.tests.forEach((test, testIndex) => {
          if (!test.code) {
            validationErrorsList.push(`Submuestra ${index + 1}, Prueba ${testIndex + 1}: Código de prueba`)
          }
          if (!test.quantity || test.quantity < 1) {
            validationErrorsList.push(`Submuestra ${index + 1}, Prueba ${testIndex + 1}: Cantidad`)
          }
        })
      }
    })
  }
  
  return validationErrorsList
})

// Función para verificar cambios (disponible para uso futuro)
// const hasChanges = computed(() => {
//   if (!originalData.value) return false
//   return JSON.stringify(form) !== JSON.stringify(originalData.value)
// })

// ============================================================================
// FUNCIONES
// ============================================================================
/**
 * Normaliza tipo de atención del backend al valor esperado por el select
 */
const normalizeAttentionType = (value: string | undefined | null): string => {
  if (!value) return ''
  const v = String(value).toLowerCase()
  if (v.includes('ambulator')) return 'ambulatorio'
  if (v.includes('hospital')) return 'hospitalizado'
  return ''
}

/**
 * Convierte fecha a formato input date (YYYY-MM-DD)
 */
const toInputDate = (value: string | undefined | null): string => {
  if (!value) return ''
  // Si ya viene en formato YYYY-MM-DD
  if (/^\d{4}-\d{2}-\d{2}$/.test(value)) return value
  const date = new Date(value)
  if (isNaN(date.getTime())) return ''
  return date.toISOString().split('T')[0]
}

// (normalizeBodyRegion eliminado: ahora se acepta directamente el valor devuelto por el backend o el seleccionado en el componente.)


/**
 * Carga los datos del caso desde el backend (cuando se proporciona caseCodeProp)
 */
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

/**
 * Envía los cambios al backend
 */
const onSubmit = async () => {
  // Validar que hay datos para actualizar (ya sea desde props o búsqueda)
  const caseCode = props.caseCodeProp || (foundCaseInfo.value as any)?.case_code || (foundCaseInfo.value as any)?.caso_code
  
  // Validar que el caso no esté completado
  if (isCaseCompleted.value) {
    showError('Caso completado', 'No se puede editar un caso que ya ha sido completado. Los casos completados no pueden ser modificados.')
    return
  }
  
  if (!isFormValid.value) {
    if (suppressValidation.value) {
      // Consumir la supresión y no mostrar error
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

  // Validar que hay información del paciente cargada
  const cedulaToUse = form.patientDocument || foundCaseInfo.value?.paciente?.paciente_code
  if (!cedulaToUse) {
    showError('Información incompleta', 'No se encontró información del paciente para este caso')
    return
  }

  isLoading.value = true
  try {
    // Preparar datos para la actualización
    const entityInfoToSend = (() => {
      if (selectedEntity.value?.codigo && selectedEntity.value?.nombre) {
        return { id: selectedEntity.value.codigo, nombre: selectedEntity.value.nombre }
      }
      const fromCase = (foundCaseInfo.value as any)?.entidad_info || (foundCaseInfo.value as any)?.paciente?.entidad_info
      if (fromCase?.codigo && fromCase?.nombre) {
        return { id: fromCase.codigo, nombre: fromCase.nombre }
      }
      if (form.patientEntity) {
        const nombre = selectedEntity.value?.nombre || (foundCaseInfo.value as any)?.paciente?.entidad_info?.nombre || ''
        if (nombre) return { id: form.patientEntity, nombre }
      }
      return undefined
    })()

    // Mapear tipo de atención del frontend al formato del backend
    const mapTipoAtencionToBackend = (tipo: string): string => {
      const mapping: Record<string, string> = {
        'ambulatorio': 'Outpatient',
        'hospitalizado': 'Inpatient',
        'Ambulatorio': 'Outpatient',
        'Hospitalizado': 'Inpatient'
      }
      return mapping[tipo] || 'Outpatient'
    }

    // Normalizar estado a uno de los valores válidos del backend (español -> inglés)
    const estadoBackendMap: Record<string, string> = {
      'En proceso': 'In process',
      'Por firmar': 'To sign',
      'Por entregar': 'To deliver', 
      'Completado': 'Completed',
      'Requiere cambios': 'To deliver',
      'cancelado': 'Completed'
    }
    const estadoToSend = ((): string => {
      const raw = form.state
      if (!raw) return 'In process'
      return estadoBackendMap[raw] || raw
    })()

    const prioridadToSend = ((): string => {
      const p = form.casePriority || 'Normal'
      if (['Normal','Prioritario'].includes(p)) return p
      return 'Normal'
    })()

    // Construir muestras replicando lógica de creación (sin descartar por region vacía aún)
    const existingSamples = (foundCaseInfo.value?.muestras || []) as any[]
    const samplesClean = form.samples.map((s, idx) => {
      // Fallback: si el usuario no tocó la región, usar la existente
      const region = s.bodyRegion || existingSamples[idx]?.region_cuerpo || existingSamples[idx]?.regionCuerpo || ''
      return {
        body_region: region,
        tests: s.tests
          .filter(t => String(t.code).trim() !== '')
          .map(t => ({ id: t.code, name: t.name || t.code, quantity: t.quantity || 1 }))
      }
    })
    // Si todas las regiones quedaron vacías y ya existían muestras, no enviar campo para no sobrescribir
    const allEmptyRegions = samplesClean.every(s => !s.body_region)
    if (allEmptyRegions && existingSamples.length) {
      // Reutilizar las existentes (no enviar muestras en updateData posteriormente)
    }

    const pacienteEntidad = entityInfoToSend || (form.patientEntity && selectedEntity.value?.nombre
      ? { id: form.patientEntity, nombre: selectedEntity.value?.nombre || '' }
      : undefined)

    const updateData: any = {
      state: estadoToSend as unknown as string,
      requesting_physician: form.requestingPhysician || undefined,
      service: form.service || undefined,
      priority: prioridadToSend,
      observations: form.observations || undefined,
      samples: allEmptyRegions && existingSamples.length ? undefined : samplesClean,
      patient_info: {
        patient_code: (patientInfo.value as any)?.codigo || cedulaToUse,
        name: (patientInfo.value as any)?.nombre || '',
        age: (patientInfo.value as any)?.edad || 0,
        gender: (patientInfo.value as any)?.sexo || '',
        entity_info: pacienteEntidad ? { id: pacienteEntidad.id, name: pacienteEntidad.nombre } : { id: '', name: '' },
        care_type: mapTipoAtencionToBackend(form.patientCareType),
        observations: (patientInfo.value as any)?.observaciones || undefined
      }
    }

    // El backend requiere al menos una muestra; si quedó vacío, mantener la anterior del caso existente
    if (updateData.samples && updateData.samples.length) {
      // Eliminar posibles entradas con region vacía para no violar validación backend
      updateData.samples = updateData.samples.filter((s: any) => s.body_region)
      if (!updateData.samples.length) delete updateData.samples
    } else if (!updateData.samples && foundCaseInfo.value?.muestras?.length) {
      // Mantener sin cambio
      delete updateData.samples
    }

    // Eliminar campos undefined para payload más limpio
    Object.keys(updateData).forEach(k => updateData[k] === undefined && delete updateData[k])
    if (updateData.patient_info) {
      Object.keys(updateData.patient_info).forEach(k => updateData.patient_info[k] === undefined && delete updateData.patient_info[k])
    }
    

    const updatedCaseResponse = await casesApiService.updateCase(caseCode, updateData)
    
    // Actualizar colección de pacientes para mantener coherencia
    const sexoForm = (() => {
      const s = String(patientInfo.value?.sexo || '').toLowerCase()
      if (s.startsWith('m')) return 'Masculino'
      if (s.startsWith('f')) return 'Femenino'
      return 'Masculino'
    })()
    
    const patientName = String(patientInfo.value?.nombre || patientInfo.value?.nombrePaciente || '').trim()
    const patientDataToUpdate = {
      ...(patientName && { name: patientName }),
      age: parseInt(String(patientInfo.value?.edad || '0'), 10),
      gender: sexoForm === 'Masculino' ? 'Male' : 'Female',
      entity_info: {
        id: form.patientEntity || '',
        name: String(selectedEntity.value?.nombre || foundCaseInfo.value?.entidad_info?.nombre || '')
      },
      care_type: mapTipoAtencionToBackend(form.patientCareType),
      observations: (patientInfo.value as any)?.observaciones || undefined
    }
    
    try {
      await patientsApiService.updatePatient(cedulaToUse, patientDataToUpdate)
    } catch (e: any) {
      throw new Error('El caso se actualizó, pero falló la actualización del paciente')
    }
    
    // Adaptar respuesta inglesa a campos esperados por la UI para la notificación
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
      prioridad: uc.priority || form.casePriority,
      observaciones_generales: uc.observations || form.observations,
      muestras: Array.isArray(uc.samples) ? uc.samples.map((s: any) => ({
        regionCuerpo: s.body_region,
        region_cuerpo: s.body_region,
        pruebas: (s.tests || []).map((t: any) => ({ id: t.id, nombre: t.name, cantidad: t.quantity }))
      })) : updatedCase.value?.muestras
    }
    updatedCase.value = adapted
    // Normalizar prioridad en el objeto actualizado para garantizar que la notificación la muestre
    if (updatedCase.value) {
      // Si el backend devolvió 'prioridad' simple, mapear a prioridad_caso
      if (!updatedCase.value.prioridad_caso && (updatedCase.value as any).prioridad) {
        updatedCase.value.prioridad_caso = (updatedCase.value as any).prioridad
      }
      // Si no devolvió ningún campo de prioridad, usar la del formulario
      if (!updatedCase.value.prioridad_caso && !updatedCase.value.prioridadCaso && form.casePriority) {
        updatedCase.value.prioridad_caso = form.casePriority
      }
    }
    
    // Emitir evento de actualización
    emit('case-updated', updatedCaseResponse)
    
    // Mostrar notificación de éxito con información detallada
    showSuccess('¡Caso Actualizado Exitosamente!', '')

    // Limpiar inmediatamente el formulario y la búsqueda.
    // La notificación usará únicamente los datos de updatedCase/foundCaseInfo.
    clearFormAfterSave()
  } catch (error: any) {
    // Formatear error para evitar [object Object]
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

// onReset movido arriba para consolidar funciones de limpieza

// ============================================================================
// FUNCIONES DE BÚSQUEDA
// ============================================================================

/**
 * Valida el formato del código de caso
 */
const isValidCaseCodeFormat = (code: string): boolean => {
  const regex = /^\d{4}-\d{5}$/
  return regex.test(code)
}

/**
 * Maneja cambios en el código de caso de búsqueda
 */
const handleCaseCodeChange = () => {
  searchError.value = ''
  caseFound.value = false
  foundCaseInfo.value = null
}

/**
 * Maneja la entrada de solo números y guiones en el código de caso
 */
const handleNumericInput = (value: string) => {
  // Permitir solo números y guiones, y mantener el formato YYYY-NNNNN
  const numericValue = value.replace(/[^0-9-]/g, '')
  
  // Si el usuario está escribiendo y no hay guión, agregarlo automáticamente después de 4 dígitos
  if (numericValue.length === 4 && !numericValue.includes('-')) {
    searchCaseCode.value = numericValue + '-'
  } else {
    searchCaseCode.value = numericValue
  }
}

/**
 * Busca un caso por código y carga automáticamente los datos
 */
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
      // Guardar información del caso encontrado para mostrar
      foundCaseInfo.value = caseData
      updatedCase.value = caseData  // También poblar updatedCase para las notificaciones
      caseFound.value = true
      
      // Cargar automáticamente los datos en el formulario
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

/**
 * Carga los datos del caso desde la información encontrada (equivalente a loadPatientData del EditPatientForm)
 */
const loadCaseDataFromFound = async (caseData: CaseModel) => {
  try {
    
    // Guardar el código del caso para usar en la notificación
    currentCaseCode.value = (caseData as any).case_code || (caseData as any).caso_code || (caseData as any).codigo || (caseData as any).code || searchCaseCode.value || props.caseCodeProp || ''

    
    foundCaseInfo.value = caseData
    updatedCase.value = caseData
    caseFound.value = true
    

    // Mapear datos del caso al formulario
    const formData = {
      patientDocument: 
        (caseData as any).patient_info?.patient_code ||
        caseData.paciente?.paciente_code || 
        (caseData.paciente as any)?.numeroCedula ||
        (caseData as any).cedula_paciente || 
        '',
        
      entryDate: toInputDate(
        (caseData as any).created_at ||
        (caseData as any).fecha_creacion ||
        (caseData as any).fechaCreacion ||
        (caseData as any).fecha_creacion?.$date ||
        ''
      ),
        
      requestingPhysician: 
        (caseData as any).requesting_physician ||
        (() => {
          const medico = caseData.medico_solicitante;
          if (typeof medico === 'object' && medico && 'nombre' in medico) {
            return (medico as any).nombre;
          }
          if (typeof medico === 'string') {
            return medico;
          }
          return (caseData as any).medicoSolicitante || '';
        })(),
        
      service: 
        (caseData as any).service ||
        caseData.servicio ||
        (caseData as any).servicio ||
        '',

      casePriority:
        (caseData as any).priority ||
        (caseData as any).prioridad_caso ||
        (caseData as any).prioridadCaso ||
        (caseData as any).prioridad ||
        'Normal',
        
      patientEntity: 
        (caseData as any).patient_info?.entity_info?.id ||
        (caseData as any).entidad_info?.id ||
        (caseData as any).entidad_info?.codigo ||
        (caseData.paciente?.entidad_info as any)?.id || 
        (caseData.paciente?.entidad_info as any)?.codigo || 
        (caseData as any).entidadPaciente ||
        (caseData as any).entidad_codigo ||
        '',
        
      patientCareType: normalizeAttentionType(
        (caseData as any).patient_info?.care_type ||
        caseData.paciente?.tipo_atencion || 
        (caseData as any).tipo_atencion ||
        (caseData as any).tipoAtencionPaciente ||
        ''
      ),
        
      state: (() => {
        const rawState = (caseData as any).state ||
          caseData.estado || 
          (caseData as any).estado ||
          'En proceso';
        
        // Mapear estados del backend (inglés) al frontend (español)
        const estadoMap: Record<string, string> = {
          'In process': 'En proceso',
          'To sign': 'Por firmar', 
          'To deliver': 'Por entregar',
          'Completed': 'Completado'
        };
        
        return estadoMap[rawState] || rawState;
      })(),
      
      // Código del patólogo asignado (si existe)
      assignedPathologist: 
        (caseData as any).assigned_pathologist?.pathologist_code ||
        (caseData as any).patologo_asignado?.codigo ||
        '',
        
      numberOfSamples: 
        (caseData.muestras?.length || 
         (caseData as any).numeroMuestras || 
         1).toString(),
         
      samples: (() => {
        const samples = (caseData as any).samples || caseData.muestras || (caseData as any).muestras || [];
        if (samples && samples.length > 0) {
          return samples.map((sample: any, index: number) => ({
            number: index + 1,
            // Usar directamente el valor devuelto por el backend (slug o label). El componente BodyRegionList
            // acepta tanto el label completo como el value en formato snake_case y se encarga de mostrar el label.
            // Se evita la normalización agresiva previa (normalizeBodyRegion) que reducía valores legítimos a
            // 'no_especificado' al tener una lista limitada de allowedValues.
            bodyRegion: (
              sample.body_region ||
              sample.region_cuerpo ||
              sample.regionCuerpo ||
              ''
            ),
            tests: (() => {
              const tests = sample.tests || sample.pruebas || [];
              if (tests && tests.length > 0) {
                return tests.map((test: any) => ({
                  code: 
                    test.id || 
                    test.code || 
                    test.codigo ||
                    '',
                  quantity: test.quantity || test.cantidad || 1,
                  name: 
                    test.name || 
                    test.nombre || 
                    ''
                }));
              }
              return [{ code: '', quantity: 1, name: '' }];
            })()
          }));
        }
        return [createEmptySubSample(1)];
      })(),
      
      observations: 
        caseData.observaciones_generales || 
        (caseData as any).observaciones ||
        (caseData as any).observacionesGenerales ||
        '',
    }
    


    Object.assign(form, formData)
    originalData.value = { ...formData }
    patientInfo.value = {
      pacienteCode: 
        (caseData as any).patient_info?.patient_code ||
        caseData.paciente?.paciente_code || 
        (caseData.paciente as any)?.numeroCedula ||
        (caseData as any).cedula_paciente ||
        formData.patientDocument ||
        '',
      nombrePaciente: 
        (caseData as any).patient_info?.name ||
        caseData.paciente?.nombre || 
        (caseData.paciente as any)?.nombrePaciente ||
        (caseData as any).nombre_paciente ||
        'Sin nombre',
      edad: 
        String((caseData as any).patient_info?.age ||
        caseData.paciente?.edad || 
        (caseData as any).edad_paciente ||
        0),
      sexo: 
        (caseData as any).patient_info?.gender ||
        caseData.paciente?.sexo || 
        (caseData as any).sexo_paciente ||
        'Sin especificar',
      entidad: 
        (caseData as any).patient_info?.entity_info?.name ||
        caseData.entidad_info?.nombre ||
        caseData.paciente?.entidad_info?.nombre ||
        'Sin especificar',
      tipoAtencion: 
        (caseData as any).patient_info?.care_type ||
        caseData.paciente?.tipo_atencion ||
        'Sin especificar',
      observaciones: 
        (caseData as any).patient_info?.observations ||
        (caseData.paciente as any)?.observaciones ||
        '',
      codigo: (caseData as any).id || caseData._id || ''
    }
    
    
    const patologoAsignado = (caseData as any).assigned_pathologist || (caseData as any).patologo_asignado
    
    if (patologoAsignado?.pathologist_code || patologoAsignado?.codigo) {
      const codigo = patologoAsignado.pathologist_code || patologoAsignado.codigo
      if (codigo && codigo.length === 24 && /^[0-9a-fA-F]{24}$/.test(codigo)) {
        try {
          const pathologist = await pathologistApi.getPathologist(codigo)
          if (pathologist) {
            const patologoCode = pathologist.patologo_code || codigo
            const patologoData = {
              codigo: patologoCode,
              nombre: pathologist.patologo_name || pathologist.nombre || patologoAsignado.pathologist_name || patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.assignedPathologist = patologoCode // Usar patologo_code para el v-model
            // Disparar el evento para que el componente se actualice
            onPathologistSelected(patologoData)
          } else {
            // Fallback al codigo original si no se encuentra
            const patologoData = {
              codigo: codigo,
              nombre: patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.assignedPathologist = codigo
            onPathologistSelected(patologoData)
          }
        } catch (error) {
          // Fallback al codigo original si hay error
          const patologoData = {
            codigo: codigo,
            nombre: patologoAsignado.nombre || ''
          }
          selectedPathologist.value = patologoData
          form.assignedPathologist = codigo
          onPathologistSelected(patologoData)
        }
      } else {
        // No es un ObjectId, usar directamente el patologo_code
        try {
          const pathologist = await pathologistApi.getPathologist(codigo)
          if (pathologist) {
            const patologoCode = pathologist.patologo_code || codigo
            const patologoData = {
              codigo: patologoCode,
              nombre: pathologist.patologo_name || pathologist.nombre || patologoAsignado.pathologist_name || patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.assignedPathologist = patologoCode // Usar patologo_code para el v-model
            onPathologistSelected(patologoData)
          } else {
            // Fallback si no se encuentra
            const patologoData = {
              codigo: codigo,
              nombre: patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.assignedPathologist = codigo
            console.log('⚠️ DEBUG - Patólogo no encontrado, usando código como fallback:', patologoData)
            onPathologistSelected(patologoData)
          }
        } catch (error) {
          // Fallback si hay error
          const patologoData = {
            codigo: codigo,
            nombre: patologoAsignado.nombre || ''
          }
          selectedPathologist.value = patologoData
          form.assignedPathologist = codigo
          onPathologistSelected(patologoData)
        }
      }
    } else {
      selectedPathologist.value = null
      form.assignedPathologist = ''
    }
    
    // Guardar entidad seleccionada (si viene en el caso)
    if ((caseData as any).patient_info?.entity_info?.id) {
      // Nuevo backend - usar patient_info.entity_info
      selectedEntity.value = {
        codigo: (caseData as any).patient_info.entity_info.id,
        nombre: (caseData as any).patient_info.entity_info.name
      }
    } else if (caseData.entidad_info?.codigo) {
      // Backend anterior - usar entidad_info
      selectedEntity.value = {
        codigo: caseData.entidad_info.codigo,
        nombre: caseData.entidad_info.nombre
      }
    } else if ((caseData.paciente as any)?.entidad_info?.id) {
      // El backend usa 'id' en lugar de 'codigo' para entidades
      selectedEntity.value = {
        codigo: (caseData.paciente as any).entidad_info.id,
        nombre: (caseData.paciente as any).entidad_info.nombre
      }
    } else if ((caseData.paciente as any)?.entidad_info?.codigo) {
      selectedEntity.value = {
        codigo: (caseData.paciente as any).entidad_info.codigo,
        nombre: (caseData.paciente as any).entidad_info.nombre
      }
    } else {
      selectedEntity.value = null
    }
    


    caseLoaded.value = true
            // showSuccess('Caso cargado exitosamente', '') - Removido según requerimientos
  } catch (error: any) {
    showError('Error al cargar datos del caso', error.message || 'Error desconocido')
  }
}

// Funciones de carga y limpieza consolidadas arriba

/**
 * Limpia completamente la búsqueda y resetea el formulario (equivalente a onReset del EditPatientForm)
 */
const onReset = () => {
  // Limpiar estado de búsqueda
  suppressValidation.value = true
  searchCaseCode.value = ''
  searchError.value = ''
  caseFound.value = false
  foundCaseInfo.value = null
  
  // Limpiar formulario
  Object.assign(form, {
    patientDocument: '',
    entryDate: '',
    requestingPhysician: '',
    service: '',
    patientEntity: '',
    patientCareType: '',
    casePriority: '',
    state: '',
    numberOfSamples: '1',
    samples: [createEmptySubSample(1)],
    observations: '',
    assignedPathologist: ''
  })
  
  // Limpiar información del paciente completamente
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
  
  // Resetear datos originales
  originalData.value = null
  caseLoaded.value = false
  
  // Limpiar datos de la notificación (cuando el usuario limpia manualmente)
  currentCaseCode.value = ''
  updatedCase.value = null
  
  // Cerrar cualquier notificación abierta
  closeNotification()

  // Forzar remonte de selects/listas para limpiar su estado interno
  resetKey.value++
}

// ============================================================================
// FUNCIONES DE MANEJO DE MUESTRAS Y PRUEBAS
// ============================================================================

/**
 * Maneja la selección de una entidad
 */
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const onEntitySelected = (entity: any | null) => {
  if (entity && entity.codigo) {
    selectedEntity.value = { codigo: entity.codigo, nombre: entity.nombre }
  } else {
    selectedEntity.value = null
  }
}

// Manejo de patólogo seleccionado
const selectedPathologist = ref<{ codigo: string; nombre: string } | null>(null)
const onPathologistSelected = (pathologist: any | null) => {
  if (pathologist) {
    // Mapear campos del patólogo de forma consistente con CasePathologist.vue
    const codigo = pathologist.patologo_code || pathologist.codigo || pathologist.code || pathologist.documento || pathologist.id || ''
    const nombre = pathologist.patologo_name || pathologist.nombre || pathologist.name || ''
    selectedPathologist.value = { codigo, nombre }
    form.assignedPathologist = codigo
  } else {
    selectedPathologist.value = null
    form.assignedPathologist = ''
  }
}

/**
 * Maneja cambios en el número de muestras (adaptado al formulario local)
 */
const handleLocalNumberOfSamplesChange = (newNumber: string): void => {
  const number = parseInt(newNumber)
  
  if (isNaN(number) || number < 1) return
  
  form.numberOfSamples = newNumber
  
  // Ajustar array de muestras
  if (number > form.samples.length) {
    // Agregar muestras
    while (form.samples.length < number) {
      form.samples.push(createEmptySubSample(form.samples.length + 1))
    }
  } else if (number < form.samples.length) {
    // Remover muestras
    form.samples = form.samples.slice(0, number)
  }
}

/**
 * Agrega una prueba a una muestra específica (adaptado al formulario local)
 */
const addLocalTestToSample = (sampleIndex: number): void => {
  if (sampleIndex >= 0 && sampleIndex < form.samples.length) {
    form.samples[sampleIndex].tests.push({
      code: '',
      quantity: 1,
      name: ''
    })
  }
}

/**
 * Remueve una prueba de una muestra específica (adaptado al formulario local)
 */
const removeLocalTestFromSample = (sampleIndex: number, testIndex: number): void => {
  if (sampleIndex >= 0 && sampleIndex < form.samples.length) {
    const sample = form.samples[sampleIndex]
    if (sample.tests.length > 1 && testIndex >= 0 && testIndex < sample.tests.length) {
      sample.tests.splice(testIndex, 1)
    }
  }
}

/**
 * Maneja la selección de una prueba en una muestra
 */
const handleTestSelected = (sampleIndex: number, testIndex: number, test: any) => {
  if (test && sampleIndex >= 0 && sampleIndex < form.samples.length) {
    const sample = form.samples[sampleIndex]
    if (testIndex >= 0 && testIndex < sample.tests.length) {
      // Asignar correctamente el código y nombre de la prueba
      sample.tests[testIndex].code = test.pruebaCode || test.code || ''
      sample.tests[testIndex].name = test.pruebasName || test.nombre || test.label || ''
    }
  }
}

// ============================================================================
// FUNCIONES HELPER PARA LA NOTIFICACIÓN
// ============================================================================

/**
 * Limpia los campos del formulario después de guardar exitosamente (sin cerrar notificación)
 */
const clearFormAfterSave = () => {
  // Limpiar campos del formulario y dejar valores por defecto
  Object.assign(form, {
    patientDocument: '',
    entryDate: '',
    requestingPhysician: '',
    service: '',
    patientEntity: '',
    patientCareType: '',
    casePriority: '',
    state: '',
    numberOfSamples: '1',
    samples: [createEmptySubSample(1)],
    observations: '',
    assignedPathologist: ''
  })

  // Limpiar estados de búsqueda
  searchCaseCode.value = ''
  searchError.value = ''
  caseFound.value = false
  // Mantener foundCaseInfo para que la notificación tenga fuente de datos de respaldo

  // Reset de estados auxiliares del formulario
  originalData.value = null
  caseLoaded.value = false
  // Mantener selectedPathologist y selectedEntity para que la notificación muestre nombres

  // Mantener: currentCaseCode y updatedCase para que la notificación muestre todo
}

/**
 * Obtiene información del paciente desde diferentes fuentes
 */
const getPatientInfo = (field: string): string => {
  const cp: any = patientInfo.value || {}
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}

  switch (field) {
    case 'nombre': {
      return cp.nombrePaciente || uc.patient_info?.name || fc.patient_info?.name || 'N/A'
    }
    case 'cedula': {
      return cp.pacienteCode || uc.patient_info?.patient_code || fc.patient_info?.patient_code || 'N/A'
    }
    case 'edad': {
      const edad = cp.edad ?? uc.patient_info?.age ?? fc.patient_info?.age
      return (edad !== undefined && edad !== null) ? String(edad) : 'N/A'
    }
    case 'sexo': {
      return cp.sexo || uc.patient_info?.gender || fc.patient_info?.gender || 'N/A'
    }
    case 'entidad': {
      return cp.entidad || uc.patient_info?.entity_info?.name || fc.patient_info?.entity_info?.name || 'N/A'
    }
    case 'tipoAtencion': {
      return cp.tipoAtencion || uc.patient_info?.care_type || fc.patient_info?.care_type || 'N/A'
    }
    default:
      return 'N/A'
  }
}

/**
 * Obtiene el conteo de muestras
 */
const getMuestrasCount = (): number => {
  return (updatedCase.value as any)?.samples?.length || (updatedCase.value as any)?.muestras?.length || form.samples.length
}

/**
 * Obtiene las observaciones del caso
 */
const getObservaciones = (): string => {
  const uc: any = updatedCase.value || {}
  return (
    uc.observations || uc.observaciones_generales || uc.observaciones || uc.observacionesGenerales || form.observations || ''
  )
}

/**
 * Obtiene las muestras del caso, combinando datos del backend y formulario
 */
const getMuestras = () => {
  const backendSamples = (updatedCase.value as any)?.samples || (updatedCase.value as any)?.muestras || []
  const formSamples = form.samples || []
  
  // Si no hay datos del backend, usar los del formulario
  if (!backendSamples.length) {
    return formSamples
  }
  
  // Combinar datos del backend con información faltante del formulario
  return backendSamples.map((backendSample: any, index: number) => {
    const formSample = formSamples[index]
    return {
      ...backendSample,
      // Preservar bodyRegion del formulario si no viene del backend
      bodyRegion: backendSample.body_region || 
                   backendSample.regionCuerpo || 
                   backendSample.region_cuerpo || 
                   formSample?.bodyRegion || 
                   'Sin especificar',
      // Asegurar que las pruebas incluyan cantidad
      tests: (backendSample.tests || backendSample.pruebas || []).map((test: any, tIndex: number) => ({
        ...test,
        id: test.id || test.code || test.codigo,
        name: test.name || test.nombre,
        quantity: test.quantity || test.cantidad || formSample?.tests?.[tIndex]?.quantity || 1
      }))
    }
  })
}

/**
 * Obtiene el conteo de pruebas en una muestra
 */
const getPruebasCount = (sample: any): number => {
  return (sample.tests && sample.tests.length) || (sample.pruebas && sample.pruebas.length) || 0
}

/**
 * Obtiene el texto de las pruebas de una muestra
 */
const getPruebasText = (sample: any): string => {
  return (sample.tests || sample.pruebas || []).map((t: any) => {
    const codigo = t.id || t.code || t.codigo || ''
    const nombre = t.name || t.nombre || ''
    const etiqueta = codigo || nombre || 'Sin código'
    return `${etiqueta} (${t.quantity || t.cantidad || 1})`
  }).join(', ')
}

/**
 * Obtiene el médico solicitante del caso
 */
const getMedicoSolicitante = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
  uc.requesting_physician || fc.requesting_physician || form.requestingPhysician || 'No especificado'
  )
}

/**
 * Obtiene el servicio del caso
 */
const getServicio = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
    uc.service || fc.service || form.service || 'No especificado'
  )
}

/**
 * Obtiene la prioridad del caso
 */
const getPrioridad = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
    uc.priority || fc.priority || form.casePriority || 'Normal'
  )
}

/**
 * Obtiene el código del caso desde diferentes fuentes
 */
const getCaseCode = (): string => {
  return currentCaseCode.value || 
         (updatedCase.value as any)?.case_code || 
         (updatedCase.value as any)?.CasoCode || 
         (updatedCase.value as any)?.code || 
         searchCaseCode.value || 
         props.caseCodeProp || 
         'N/A'
}

// ============================================================================
// WATCHERS
// ============================================================================

// Cargar datos cuando cambie el código del caso
watch(
  () => props.caseCodeProp,
  (newCode) => {
    if (newCode) {
      loadCaseData()
    }
  },
  { immediate: true }
)

// Hacer scroll cuando aparece la notificación
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

// Maneja el cierre explícito de la notificación por el usuario
const handleNotificationClosed = () => {
  suppressValidation.value = true
  closeNotification()
}

// ============================================================================
// CICLO DE VIDA
// ============================================================================

onMounted(() => {
  if (props.caseCodeProp) {
    loadCaseData()
  }
})
</script>