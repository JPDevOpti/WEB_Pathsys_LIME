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

          <div v-if="caseFound && foundCaseInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
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
                  <p class="text-gray-900 font-semibold">{{ foundCaseInfo.estado || 'N/A' }}</p>
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

      <div v-if="caseFound" class="space-y-6">
        <!-- Campos de entidad y tipo de atención -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList :key="'entity-' + resetKey" v-model="form.entidadPaciente" label="Entidad del Paciente" placeholder="Seleciona la entidad" :required="true" :auto-load="true" @entity-selected="onEntitySelected" />
          <FormSelect :key="'tipoAtencion-' + resetKey + '-' + form.tipoAtencionPaciente" v-model="form.tipoAtencionPaciente" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" />
        </div>

        <!-- Campos de fecha de ingreso y prioridad -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="form.fechaIngreso" label="Fecha de Ingreso" type="date" :required="true" help-text="Fecha en que ingresa el caso al sistema" />
          <FormSelect v-model="form.prioridadCaso" label="Prioridad del Caso" placeholder="Seleccione la prioridad" :required="true" :options="prioridadOptions" help-text="Nivel de urgencia del caso" />
        </div>

        <!-- Campos de médico solicitante y servicio -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="form.medicoSolicitante" label="Médico Solicitante" placeholder="Ejemplo: Alberto Perez" :required="true" :max-length="200" help-text="Medico solicitante del estudio" />
          <FormInputField v-model="form.servicio" label="Servicio" placeholder="Ejemplo: Medicina Interna" :required="true" :max-length="100" help-text="Área de procedencia del caso" />
        </div>

        <!-- Estado y Patólogo en una sola línea -->
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormSelect :key="'estado-' + resetKey" v-model="form.estado" label="Estado del Caso" placeholder="Seleccione el estado" :required="true" :options="estadoOptions" />
          <PathologistList :key="'pathologist-' + resetKey" v-model="form.patologoAsignado" label="Patólogo Asignado" placeholder="Buscar patólogo..." :required="false" :auto-load="true" @pathologist-selected="onPathologistSelected" />
        </div>

        <!-- Número de muestras debajo -->
        <div>
          <FormInputField class="max-w-xs" v-model="form.numeroMuestras" label="Número de Muestras" type="number" :min="1" :max="99" :required="true" @input="handleLocalNumeroMuestrasChange" />
        </div>

        <div v-if="form.muestras.length > 0" class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <TestIcon class="w-5 h-5 mr-2 text-blue-600" />
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(muestra, muestraIndex) in form.muestras" :key="muestra.numero + '-' + resetKey" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">Submuestra #{{ muestra.numero }}</h4>
              
              <div class="mb-4">
                <BodyRegionList :key="'region-' + muestraIndex + '-' + resetKey" v-model="muestra.regionCuerpo" :label="`Región del Cuerpo`" placeholder="Buscar región del cuerpo..." :required="true" help-text="Seleccione la región anatómica de donde proviene la muestra" />
              </div>
              
              <div class="space-y-3">
                <div class="flex flex-col sm:flex-row sm:items-center justify-between gap-2">
                  <label class="block text-sm font-medium text-gray-700">Pruebas a realizar</label>
                  <div class="self-end sm:self-auto">
                    <AddButton text="Agregar Prueba" @click="addLocalPruebaToMuestra(muestraIndex)" />
                  </div>
                </div>
                
                <div class="space-y-2">
                  <div v-for="(prueba, pruebaIndex) in muestra.pruebas" :key="pruebaIndex + '-' + resetKey" class="flex flex-col sm:flex-row gap-2 sm:gap-3 items-end">
                    <div class="flex-1 min-w-0">
                      <TestList :key="'test-' + muestraIndex + '-' + pruebaIndex + '-' + resetKey" v-model="prueba.code" :label="`Prueba ${pruebaIndex + 1}`" :placeholder="`Buscar y seleccionar prueba ${pruebaIndex + 1}...`" :required="true" :auto-load="true" @test-selected="(test) => handleTestSelected(muestraIndex, pruebaIndex, test)" />
                    </div>
                    <div class="w-full sm:w-24">
                      <FormInputField v-model.number="prueba.cantidad" label="Cantidad" type="number" :min="1" :max="10" placeholder="Cantidad" />
                    </div>
                    <div class="flex items-end justify-center sm:w-10 pb-1">
                      <RemoveButton @click="removeLocalPruebaFromMuestra(muestraIndex, pruebaIndex)" title="Eliminar prueba" />
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <FormTextarea v-model="form.observaciones" label="Observaciones del Caso" placeholder="Observaciones adicionales sobre el caso o procedimiento..." :rows="3" :max-length="500" :show-counter="true" help-text="Información adicional relevante para el procesamiento del caso" />

        <div class="flex justify-end space-x-3 pt-4 border-t border-gray-200">
          <ClearButton @click="onReset" :disabled="isLoading" />
          <SaveButton text="Guardar Cambios" @click="onSubmit" :disabled="isLoading || !isFormValid" :loading="isLoading" />
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
                      <div><span class="text-gray-500 font-medium">Estado:</span><p class="text-gray-900 font-semibold">{{ updatedCase.estado || 'Pendiente' }}</p></div>
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
                    <div v-for="(muestra, index) in getMuestras()" :key="index" class="border border-gray-200 rounded-lg p-3 bg-gray-50">
                      <div class="flex items-center justify-between mb-2">
                        <span class="font-medium text-gray-900 text-sm">Submuestra #{{ index + 1 }}</span>
                        <span class="text-sm text-gray-500">{{ getPruebasCount(muestra) }} prueba{{ getPruebasCount(muestra) !== 1 ? 's' : '' }}</span>
                      </div>
                      <div class="grid grid-cols-1 sm:grid-cols-2 gap-3 text-sm">
                        <div><span class="text-gray-500 font-medium">Región:</span><p class="text-gray-900">{{ muestra.regionCuerpo || 'Sin especificar' }}</p></div>
                        <div><span class="text-gray-500 font-medium">Pruebas:</span><div class="text-gray-900"><span v-if="muestra.pruebas?.length > 0">{{ getPruebasText(muestra) }}</span><span v-else class="text-gray-400">Sin pruebas</span></div></div>
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
import { useNotifications } from '../composables/useNotifications'
import Notification from '@/shared/components/feedback/Notification.vue'
import { useCaseForm } from '../composables/useCaseForm'
import { casesApiService } from '../services/casesApi.service'
import { patientsApiService } from '../services/patientsApi.service'
import pathologistApi from '../services/pathologistApi.service'
import type { CaseFormData, CaseModel, CaseState, PatientData } from '../types'
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

const form = reactive<CaseFormData & { estado: string; patologoAsignado?: string; servicio: string }>({
  pacienteCedula: '',
  fechaIngreso: '',
  medicoSolicitante: '',
  servicio: '',
  entidadPaciente: '',
  tipoAtencionPaciente: '',
  prioridadCaso: '',
  numeroMuestras: '0',
  muestras: [],
  observaciones: '',
  estado: '',
  patologoAsignado: ''
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
  return (
    form.fechaIngreso.trim() !== '' &&
    form.medicoSolicitante.trim() !== '' &&
    form.servicio.trim() !== '' &&
    form.entidadPaciente.trim() !== '' &&
    form.tipoAtencionPaciente !== '' &&
    form.prioridadCaso !== '' &&
    form.estado !== '' &&
    form.numeroMuestras !== ''
  )
})

// Validación de errores del formulario
const validationErrors = computed(() => {
  const validationErrorsList: string[] = []
  
  // Campos básicos del formulario
  if (!form.fechaIngreso) validationErrorsList.push('Fecha de ingreso')
  if (!form.medicoSolicitante) validationErrorsList.push('Médico solicitante')
  if (!form.servicio) validationErrorsList.push('Servicio')
  if (!form.prioridadCaso) validationErrorsList.push('Prioridad del caso')
  if (!form.estado) validationErrorsList.push('Estado del caso')
  if (!form.numeroMuestras) validationErrorsList.push('Número de muestras')
  if (!form.entidadPaciente) validationErrorsList.push('Entidad del paciente')
  if (!form.tipoAtencionPaciente) validationErrorsList.push('Tipo de atención')
  
  // Validación detallada de submuestras
  if (form.muestras && form.muestras.length > 0) {
    form.muestras.forEach((muestra, index) => {
      if (!muestra.regionCuerpo) {
        validationErrorsList.push(`Submuestra ${index + 1}: Región del cuerpo`)
      }
      if (!muestra.pruebas || muestra.pruebas.length === 0) {
        validationErrorsList.push(`Submuestra ${index + 1}: Al menos una prueba`)
      } else {
        muestra.pruebas.forEach((prueba, pruebaIndex) => {
          if (!prueba.code) {
            validationErrorsList.push(`Submuestra ${index + 1}, Prueba ${pruebaIndex + 1}: Código de prueba`)
          }
          if (!prueba.cantidad || prueba.cantidad < 1) {
            validationErrorsList.push(`Submuestra ${index + 1}, Prueba ${pruebaIndex + 1}: Cantidad`)
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
  const caseCode = props.caseCodeProp || foundCaseInfo.value?.caso_code
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
  const cedulaToUse = form.pacienteCedula || foundCaseInfo.value?.paciente?.paciente_code
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
      if (form.entidadPaciente) {
        const nombre = selectedEntity.value?.nombre || (foundCaseInfo.value as any)?.paciente?.entidad_info?.nombre || ''
        if (nombre) return { id: form.entidadPaciente, nombre }
      }
      return undefined
    })()

    // Mapear tipo de atención del frontend al formato del backend
    const mapTipoAtencionToBackend = (tipo: string): string => {
      const mapping: Record<string, string> = {
        'ambulatorio': 'Ambulatorio',
        'hospitalizado': 'Hospitalizado'
      }
      return mapping[tipo] || 'Ambulatorio'
    }

    // Normalizar estado a uno de los valores válidos del backend
    const estadoBackendMap: Record<string, string> = {
      'Requiere cambios': 'Por entregar', // UI -> backend enum existente
      'cancelado': 'Completado' // fallback (estado cancelado no existe ya)
    }
    const estadoToSend = ((): string => {
      const raw = form.estado
      if (!raw) return 'En proceso'
      return estadoBackendMap[raw] || raw
    })()

    const prioridadToSend = ((): string => {
      const p = form.prioridadCaso || 'Normal'
      if (['Normal','Prioritario'].includes(p)) return p
      return 'Normal'
    })()

    // Construir muestras replicando lógica de creación (sin descartar por region vacía aún)
    const existingMuestras = (foundCaseInfo.value?.muestras || []) as any[]
    const muestrasClean = form.muestras.map((m, idx) => {
      // Fallback: si el usuario no tocó la región, usar la existente
      const region = m.regionCuerpo || existingMuestras[idx]?.region_cuerpo || existingMuestras[idx]?.regionCuerpo || ''
      return {
        region_cuerpo: region,
        pruebas: m.pruebas
          .filter(p => String(p.code).trim() !== '')
          .map(p => ({
            id: p.code,
            nombre: p.nombre || p.code,
            cantidad: p.cantidad || 1
          }))
      }
    })
    // Si todas las regiones quedaron vacías y ya existían muestras, no enviar campo para no sobrescribir
    const allEmptyRegions = muestrasClean.every(m => !m.region_cuerpo)
    if (allEmptyRegions && existingMuestras.length) {
      // Reutilizar las existentes (no enviar muestras en updateData posteriormente)
    }

    const pacienteEntidad = entityInfoToSend || (form.entidadPaciente && selectedEntity.value?.nombre
      ? { id: form.entidadPaciente, nombre: selectedEntity.value?.nombre || '' }
      : undefined)

    const updateData: any = {
      estado: estadoToSend as CaseState,
      medico_solicitante: form.medicoSolicitante || undefined,
      servicio: form.servicio || undefined,
      prioridad: prioridadToSend,
      observaciones_generales: form.observaciones || undefined,
      muestras: allEmptyRegions && existingMuestras.length ? undefined : muestrasClean,
      patologo_asignado: form.patologoAsignado ? { 
        codigo: selectedPathologist.value?.codigo || form.patologoAsignado, 
        nombre: selectedPathologist.value?.nombre || '' 
      } : undefined,
      entidad_info: pacienteEntidad,
      paciente: {
        paciente_code: patientInfo.value?.codigo || cedulaToUse,
        nombre: patientInfo.value?.nombre || '',
        edad: patientInfo.value?.edad || 0,
        sexo: patientInfo.value?.sexo || '',
        entidad_info: pacienteEntidad || { id: '', nombre: '' },
        tipo_atencion: mapTipoAtencionToBackend(form.tipoAtencionPaciente),
        observaciones: patientInfo.value?.observaciones || undefined
      }
    }

    // El backend requiere al menos una muestra; si quedó vacío, mantener la anterior del caso existente
    if (updateData.muestras && updateData.muestras.length) {
      // Eliminar posibles entradas con region vacía para no violar validación backend
      updateData.muestras = updateData.muestras.filter((m: any) => m.region_cuerpo)
      if (!updateData.muestras.length) delete updateData.muestras
    } else if (!updateData.muestras && foundCaseInfo.value?.muestras?.length) {
      // Mantener sin cambio
      delete updateData.muestras
    }

    // Eliminar campos undefined para payload más limpio
    Object.keys(updateData).forEach(k => updateData[k] === undefined && delete updateData[k])
    if (updateData.paciente) {
      Object.keys(updateData.paciente).forEach(k => updateData.paciente[k] === undefined && delete updateData.paciente[k])
    }
    

    const updatedCaseResponse = await casesApiService.updateCase(caseCode, updateData)
    
    // Actualizar colección de pacientes para mantener coherencia
    const sexoForm = (() => {
      const s = String(patientInfo.value?.sexo || '').toLowerCase()
      if (s.startsWith('m')) return 'Masculino'
      if (s.startsWith('f')) return 'Femenino'
      return 'Masculino'
    })()
    
    const patientDataToUpdate: PatientData = {
      pacienteCode: cedulaToUse,
      nombrePaciente: String(patientInfo.value?.nombre || ''),
      sexo: sexoForm as any,
      edad: String(patientInfo.value?.edad || ''),
      entidad: String(selectedEntity.value?.nombre || foundCaseInfo.value?.entidad_info?.nombre || ''),
      entidadCodigo: form.entidadPaciente,
      tipoAtencion: mapTipoAtencionToBackend(form.tipoAtencionPaciente) as any,
      observaciones: ''
    }
    try {
      await patientsApiService.updatePatient(cedulaToUse, patientDataToUpdate)
    } catch (e: any) {
      throw new Error('El caso se actualizó, pero falló la actualización del paciente')
    }
    
    // Guardar caso actualizado para la notificación
    updatedCase.value = updatedCaseResponse
    // Normalizar prioridad en el objeto actualizado para garantizar que la notificación la muestre
    if (updatedCase.value) {
      // Si el backend devolvió 'prioridad' simple, mapear a prioridad_caso
      if (!updatedCase.value.prioridad_caso && (updatedCase.value as any).prioridad) {
        updatedCase.value.prioridad_caso = (updatedCase.value as any).prioridad
      }
      // Si no devolvió ningún campo de prioridad, usar la del formulario
      if (!updatedCase.value.prioridad_caso && !updatedCase.value.prioridadCaso && form.prioridadCaso) {
        updatedCase.value.prioridad_caso = form.prioridadCaso
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
    currentCaseCode.value = (caseData as any).codigo || (caseData as any).code || searchCaseCode.value || props.caseCodeProp || ''

    
    // Marcar como encontrado cuando proviene de navegación con código
    foundCaseInfo.value = caseData
    caseFound.value = true

    // Mapear datos del caso al formulario con información completa
    // Intentar múltiples posibles estructuras de datos del backend
    const formData = {
      pacienteCedula: 
        caseData.paciente?.paciente_code || 
        (caseData.paciente as any)?.numeroCedula ||
        (caseData as any).cedula_paciente || 
        '',
        
      fechaIngreso: toInputDate(
        (caseData as any).fecha_creacion ||
        (caseData as any).fechaCreacion ||
        (caseData as any).fecha_creacion?.$date ||
        ''
      ),
        
      medicoSolicitante: 
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
        
      servicio: 
        caseData.servicio ||
        (caseData as any).servicio ||
        '',

      prioridadCaso:
        (caseData as any).prioridad_caso ||
        (caseData as any).prioridadCaso ||
        (caseData as any).prioridad ||
        'Normal',
        
      entidadPaciente: 
        caseData.entidad_info?.codigo || 
        (caseData.paciente?.entidad_info as any)?.id || 
        caseData.paciente?.entidad_info?.codigo || 
        (caseData as any).entidadPaciente ||
        (caseData as any).entidad_codigo ||
        '',
        
      tipoAtencionPaciente: normalizeAttentionType(
        caseData.paciente?.tipo_atencion || 
        (caseData as any).tipo_atencion ||
        (caseData as any).tipoAtencionPaciente ||
        ''
      ),
        
      estado: 
        caseData.estado || 
        (caseData as any).estado ||
        'En proceso',
      
      // Código del patólogo asignado (si existe)
      patologoAsignado: 
        (caseData as any).patologo_asignado?.codigo ||
        '',
        
      numeroMuestras: 
        (caseData.muestras?.length || 
         (caseData as any).numeroMuestras || 
         1).toString(),
         
      muestras: (() => {
        const muestras = caseData.muestras || (caseData as any).muestras || [];
        if (muestras && muestras.length > 0) {
          return muestras.map((muestra: any, index: number) => ({
            numero: index + 1,
            // Usar directamente el valor devuelto por el backend (slug o label). El componente BodyRegionList
            // acepta tanto el label completo como el value en formato snake_case y se encarga de mostrar el label.
            // Se evita la normalización agresiva previa (normalizeBodyRegion) que reducía valores legítimos a
            // 'no_especificado' al tener una lista limitada de allowedValues.
            regionCuerpo: (
              muestra.region_cuerpo ||
              muestra.regionCuerpo ||
              ''
            ),
            pruebas: (() => {
              const pruebas = muestra.pruebas || muestra.tests || [];
              if (pruebas && pruebas.length > 0) {
                return pruebas.map((prueba: any) => ({
                  code: 
                    prueba.id || 
                    prueba.code || 
                    prueba.codigo ||
                    '',
                  cantidad: prueba.cantidad || 1,
                  nombre: 
                    prueba.nombre || 
                    prueba.name ||
                    ''
                }));
              }
              return [{ code: '', cantidad: 1, nombre: '' }];
            })()
          }));
        }
        return [createEmptySubSample(1)];
      })(),
      
      observaciones: 
        caseData.observaciones_generales || 
        (caseData as any).observaciones ||
        (caseData as any).observacionesGenerales ||
        '',
    }
    


    // Asignar datos al formulario
    Object.assign(form, formData)
    
    // Verificar después de asignación
    originalData.value = { ...formData }

    // Guardar información del paciente para mostrar
    patientInfo.value = {
      nombre: 
        caseData.paciente?.nombre || 
        (caseData.paciente as any)?.nombrePaciente ||
        (caseData as any).nombre_paciente ||
        '',
      cedula: 
        caseData.paciente?.paciente_code || 
        (caseData.paciente as any)?.numeroCedula ||
        (caseData as any).cedula_paciente ||
        formData.pacienteCedula ||
        '',
      edad: 
        caseData.paciente?.edad || 
        (caseData as any).edad_paciente ||
        0,
      sexo: 
        caseData.paciente?.sexo || 
        (caseData as any).sexo_paciente ||
        ''
    }
    
    // Guardar patólogo seleccionado (si viene en el caso) - mapeo consistente
    const patologoAsignado = (caseData as any).patologo_asignado
    
    if (patologoAsignado?.codigo) {
      // Si el codigo parece ser un ObjectId (24 hex), necesitamos buscar el patologo_code real
      const codigo = patologoAsignado.codigo
      if (codigo && codigo.length === 24 && /^[0-9a-fA-F]{24}$/.test(codigo)) {
        // Es un ObjectId, necesitamos buscar el patólogo para obtener el patologo_code
        try {
          const pathologist = await pathologistApi.getPathologist(codigo)
          if (pathologist) {
            const patologoCode = pathologist.patologo_code || codigo
            const patologoData = {
              codigo: patologoCode,
              nombre: pathologist.patologo_name || pathologist.nombre || patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.patologoAsignado = patologoCode // Usar patologo_code para el v-model
            // Disparar el evento para que el componente se actualice
            onPathologistSelected(patologoData)
          } else {
            // Fallback al codigo original si no se encuentra
            const patologoData = {
              codigo: codigo,
              nombre: patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.patologoAsignado = codigo
            onPathologistSelected(patologoData)
          }
        } catch (error) {
          // Fallback al codigo original si hay error
          const patologoData = {
            codigo: codigo,
            nombre: patologoAsignado.nombre || ''
          }
          selectedPathologist.value = patologoData
          form.patologoAsignado = codigo
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
              nombre: pathologist.patologo_name || pathologist.nombre || patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.patologoAsignado = patologoCode // Usar patologo_code para el v-model
            onPathologistSelected(patologoData)
          } else {
            // Fallback si no se encuentra
            const patologoData = {
              codigo: codigo,
              nombre: patologoAsignado.nombre || ''
            }
            selectedPathologist.value = patologoData
            form.patologoAsignado = codigo
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
          form.patologoAsignado = codigo
          onPathologistSelected(patologoData)
        }
      }
    } else {
      selectedPathologist.value = null
      form.patologoAsignado = ''
    }
    
    // Guardar entidad seleccionada (si viene en el caso)
    if (caseData.entidad_info?.codigo) {
      selectedEntity.value = {
        codigo: caseData.entidad_info.codigo,
        nombre: caseData.entidad_info.nombre
      }
    } else if ((caseData.paciente?.entidad_info as any)?.id) {
      // El backend usa 'id' en lugar de 'codigo' para entidades
      selectedEntity.value = {
        codigo: (caseData.paciente.entidad_info as any).id,
        nombre: caseData.paciente.entidad_info.nombre
      }
    } else if (caseData.paciente?.entidad_info?.codigo) {
      selectedEntity.value = {
        codigo: caseData.paciente.entidad_info.codigo,
        nombre: caseData.paciente.entidad_info.nombre
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
    pacienteCedula: '',
    fechaIngreso: '',
    medicoSolicitante: '',
    servicio: '',
    entidadPaciente: '',
    tipoAtencionPaciente: '',
    prioridadCaso: '',
    estado: '',
    numeroMuestras: '1',
    muestras: [createEmptySubSample(1)],
    observaciones: '',
    patologoAsignado: ''
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
    form.patologoAsignado = codigo
  } else {
    selectedPathologist.value = null
    form.patologoAsignado = ''
  }
}

/**
 * Maneja cambios en el número de muestras (adaptado al formulario local)
 */
const handleLocalNumeroMuestrasChange = (nuevoNumero: string): void => {
  const numero = parseInt(nuevoNumero)
  
  if (isNaN(numero) || numero < 1) return
  
  form.numeroMuestras = nuevoNumero
  
  // Ajustar array de muestras
  if (numero > form.muestras.length) {
    // Agregar muestras
    while (form.muestras.length < numero) {
      form.muestras.push(createEmptySubSample(form.muestras.length + 1))
    }
  } else if (numero < form.muestras.length) {
    // Remover muestras
    form.muestras = form.muestras.slice(0, numero)
  }
}

/**
 * Agrega una prueba a una muestra específica (adaptado al formulario local)
 */
const addLocalPruebaToMuestra = (muestraIndex: number): void => {
  if (muestraIndex >= 0 && muestraIndex < form.muestras.length) {
    form.muestras[muestraIndex].pruebas.push({
      code: '',
      cantidad: 1,
      nombre: ''
    })
  }
}

/**
 * Remueve una prueba de una muestra específica (adaptado al formulario local)
 */
const removeLocalPruebaFromMuestra = (muestraIndex: number, pruebaIndex: number): void => {
  if (muestraIndex >= 0 && muestraIndex < form.muestras.length) {
    const muestra = form.muestras[muestraIndex]
    if (muestra.pruebas.length > 1 && pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      muestra.pruebas.splice(pruebaIndex, 1)
    }
  }
}

/**
 * Maneja la selección de una prueba en una muestra
 */
const handleTestSelected = (muestraIndex: number, pruebaIndex: number, test: any) => {
  if (test && muestraIndex >= 0 && muestraIndex < form.muestras.length) {
    const muestra = form.muestras[muestraIndex]
    if (pruebaIndex >= 0 && pruebaIndex < muestra.pruebas.length) {
      // Asignar correctamente el código y nombre de la prueba
      muestra.pruebas[pruebaIndex].code = test.pruebaCode || test.code || ''
      muestra.pruebas[pruebaIndex].nombre = test.pruebasName || test.nombre || test.label || ''
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
    pacienteCedula: '',
    fechaIngreso: '',
    medicoSolicitante: '',
    servicio: '',
    entidadPaciente: '',
    tipoAtencionPaciente: '',
    prioridadCaso: '',
    estado: '',
    numeroMuestras: '1',
    muestras: [createEmptySubSample(1)],
    observaciones: '',
    patologoAsignado: ''
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
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  const cp: any = patientInfo.value || {}

  switch (field) {
    case 'nombre': {
      return (
        uc.paciente?.nombre || fc.paciente?.nombre || cp.nombre || 'N/A'
      )
    }
    case 'cedula': {
      return (
        uc.paciente?.paciente_code || fc.paciente?.paciente_code || cp.cedula || 'N/A'
      )
    }
    case 'edad': {
      const edad = uc.paciente?.edad ?? fc.paciente?.edad ?? cp.edad
      return (edad !== undefined && edad !== null) ? String(edad) : 'N/A'
    }
    case 'sexo': {
      return (
        uc.paciente?.sexo || fc.paciente?.sexo || cp.sexo || 'N/A'
      )
    }
    case 'entidad': {
      return (
        uc.entidad_info?.nombre ||
        uc.paciente?.entidad_info?.nombre ||
        fc.entidad_info?.nombre ||
        fc.paciente?.entidad_info?.nombre ||
        cp.entidad ||
        (selectedEntity.value?.nombre || '') ||
        'N/A'
      )
    }
    case 'tipoAtencion': {
      return (
        uc.paciente?.tipo_atencion ||
        uc.tipo_atencion ||
        fc.paciente?.tipo_atencion ||
        fc.tipo_atencion ||
        cp.tipoAtencion ||
        'N/A'
      )
    }
    default:
      return 'N/A'
  }
}

/**
 * Obtiene el conteo de muestras
 */
const getMuestrasCount = (): number => {
  return updatedCase.value?.muestras?.length || form.muestras.length
}

/**
 * Obtiene las observaciones del caso
 */
const getObservaciones = (): string => {
  const uc: any = updatedCase.value || {}
  return (
    uc.observaciones_generales || uc.observaciones || uc.observacionesGenerales || form.observaciones || ''
  )
}

/**
 * Obtiene las muestras del caso, combinando datos del backend y formulario
 */
const getMuestras = () => {
  const backendMuestras = (updatedCase.value as any)?.muestras || []
  const formMuestras = form.muestras || []
  
  // Si no hay datos del backend, usar los del formulario
  if (!backendMuestras.length) {
    return formMuestras
  }
  
  // Combinar datos del backend con información faltante del formulario
  return backendMuestras.map((backendMuestra: any, index: number) => {
    const formMuestra = formMuestras[index]
    return {
      ...backendMuestra,
      // Preservar region_cuerpo del formulario si no viene del backend
      regionCuerpo: backendMuestra.regionCuerpo || 
                   backendMuestra.region_cuerpo || 
                   formMuestra?.regionCuerpo || 
                   'Sin especificar',
      // Asegurar que las pruebas incluyan cantidad
      pruebas: (backendMuestra.pruebas || []).map((prueba: any, pIndex: number) => ({
        ...prueba,
        cantidad: prueba.cantidad || formMuestra?.pruebas?.[pIndex]?.cantidad || 1
      }))
    }
  })
}

/**
 * Obtiene el conteo de pruebas en una muestra
 */
const getPruebasCount = (muestra: any): number => {
  return (muestra.pruebas && muestra.pruebas.length) || 0
}

/**
 * Obtiene el texto de las pruebas de una muestra
 */
const getPruebasText = (muestra: any): string => {
  return (muestra.pruebas || []).map((p: any) => {
    const codigo = p.id || p.codigo || p.code || ''
    const nombre = p.nombre || p.name || ''
    const etiqueta = codigo || nombre || 'Sin código'
    return `${etiqueta} (${p.cantidad || 1})`
  }).join(', ')
}

/**
 * Obtiene el médico solicitante del caso
 */
const getMedicoSolicitante = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
  (typeof uc.medico_solicitante === 'string' && uc.medico_solicitante) ||
  (typeof fc.medico_solicitante === 'string' && fc.medico_solicitante) ||
  uc.medico_solicitante?.nombre ||
  uc.medicoSolicitante?.nombre ||
  fc.medico_solicitante?.nombre ||
  fc.medicoSolicitante ||
  form.medicoSolicitante ||
  'No especificado'
  )
}

/**
 * Obtiene el servicio del caso
 */
const getServicio = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
    uc.servicio ||
    fc.servicio ||
    form.servicio ||
    'No especificado'
  )
}

/**
 * Obtiene la prioridad del caso
 */
const getPrioridad = (): string => {
  const uc: any = updatedCase.value || {}
  const fc: any = foundCaseInfo.value || {}
  return (
    uc.prioridad_caso ||
    uc.prioridadCaso ||
  uc.prioridad ||
    fc.prioridad_caso ||
    fc.prioridadCaso ||
  fc.prioridad ||
    form.prioridadCaso ||
    'Normal'
  )
}

/**
 * Obtiene el código del caso desde diferentes fuentes
 */
const getCaseCode = (): string => {
  return currentCaseCode.value || 
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