<template>
  <div class="space-y-4">
    <form class="space-y-4" @submit.prevent="onSubmit">
      <div v-if="!caseCodeProp" class="bg-gray-50 rounded-lg border border-gray-200">
        <div class="px-4 pt-4 pb-4">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Buscar Caso para Editar
          </h3>
      
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
            <div class="flex-1">
              <FormInputField
                v-model="searchCaseCode"
                type="text"
                placeholder="Ej: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isSearching"
                @update:model-value="handleCaseCodeChange"
                @keydown.enter.prevent="searchCase"
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
            <div class="flex items-center justify-between mb-3">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <h4 class="text-sm font-semibold text-green-800">Caso Encontrado y Cargado</h4>
              </div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
              <div><span class="font-medium text-green-700">Código del Caso:</span><p class="text-green-800 font-mono">{{ foundCaseInfo.CasoCode || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Nombre del Paciente:</span><p class="text-green-800 break-words">{{ foundCaseInfo.paciente?.nombre || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Cédula del Paciente:</span><p class="text-green-800 font-mono">{{ foundCaseInfo.paciente?.paciente_code || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Edad:</span><p class="text-green-800">{{ foundCaseInfo.paciente?.edad || 'N/A' }} años</p></div>
              <div><span class="font-medium text-green-700">Sexo:</span><p class="text-green-800">{{ foundCaseInfo.paciente?.sexo || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Entidad:</span><p class="text-green-800 break-words">{{ foundCaseInfo.paciente?.entidad_info?.nombre || foundCaseInfo.entidad_info?.nombre || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Tipo de Atención:</span><p class="text-green-800 break-words">{{ foundCaseInfo.paciente?.tipo_atencion || 'N/A' }}</p></div>
              <div><span class="font-medium text-green-700">Estado del Caso:</span><p class="text-green-800">{{ foundCaseInfo.estado || 'N/A' }}</p></div>
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
        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <FormInputField v-model="form.medicoSolicitante" label="Médico Solicitante" placeholder="Médico que solicita el estudio" :required="false" :max-length="100" />
          <FormInputField v-model="form.servicio" label="Servicio" placeholder="Procedencia del caso" :required="false" :max-length="100" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6">
          <EntityList :key="'entity-' + resetKey" v-model="form.entidadPaciente" label="Entidad del Paciente" placeholder="Buscar entidad..." :required="true" :auto-load="true" @entity-selected="onEntitySelected" />
          <FormSelect :key="'tipoAtencion-' + resetKey + '-' + form.tipoAtencionPaciente" v-model="form.tipoAtencionPaciente" label="Tipo de Atención" placeholder="Seleccione el tipo de atención" :required="true" :options="tipoAtencionOptions" />
        </div>

        <div class="grid grid-cols-1 lg:grid-cols-3 gap-4 lg:gap-6">
          <FormInputField v-model="form.numeroMuestras" label="Número de Muestras" type="number" :min="1" :max="99" :required="true" @input="handleLocalNumeroMuestrasChange" />
          <FormInputField v-model="form.fechaIngreso" label="Fecha de creación" type="date" :required="true" />
          <FormSelect :key="'estado-' + resetKey" v-model="form.estado" label="Estado del Caso" placeholder="Seleccione el estado" :required="true" :options="estadoOptions" />
        </div>

        <div class="max-w-md">
          <PathologistList :key="'pathologist-' + resetKey" v-model="form.patologoAsignado" label="Patólogo Asignado" placeholder="Buscar patólogo..." :required="false" :auto-load="true" @pathologist-selected="onPathologistSelected" />
        </div>

        <div v-if="form.muestras.length > 0" class="space-y-4">
          <h3 class="text-lg font-semibold text-gray-800 flex items-center">
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"/>
            </svg>
            Información de Submuestras
          </h3>
          
          <div class="space-y-6">
            <div v-for="(muestra, muestraIndex) in form.muestras" :key="muestra.numero + '-' + resetKey" class="border border-gray-200 rounded-lg p-4 bg-gray-50">
              <h4 class="font-medium text-gray-700 mb-4">Submuestra {{ muestra.numero }}</h4>
              
              <div class="mb-4">
                <BodyRegionList :key="'region-' + muestraIndex + '-' + resetKey" v-model="muestra.regionCuerpo" :label="`Región del Cuerpo - Submuestra ${muestra.numero}`" placeholder="Buscar región del cuerpo..." :required="true" help-text="Seleccione la región anatómica de donde proviene la muestra" />
              </div>
              
              <div class="space-y-3">
                <div class="flex items-center justify-between">
                  <label class="block text-sm font-medium text-gray-700">Pruebas a Realizar <span class="text-red-500">*</span></label>
                  <AddButton text="Agregar Prueba" @click="addLocalPruebaToMuestra(muestraIndex)" />
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
                      <RemoveButton v-if="muestra.pruebas.length > 1" @click="removeLocalPruebaFromMuestra(muestraIndex, pruebaIndex)" title="Eliminar prueba" />
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
                        <span class="font-medium text-gray-900 text-sm">Submuestra {{ index + 1 }}</span>
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
import type { CaseFormData, CaseModel, CaseState, PatientData } from '../types'

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

const estadoOptions = [
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Por firmar', label: 'Por firmar' },
  { value: 'Por entregar', label: 'Por entregar' },
  { value: 'Completado', label: 'Completado' },
  { value: 'cancelado', label: 'Cancelado' }
]

// ============================================================================
// COMPUTED
// ============================================================================

const isFormValid = computed(() => {
  return (
    form.fechaIngreso.trim() !== '' &&
    // Médico solicitante es opcional
    form.entidadPaciente.trim() !== '' &&
    form.tipoAtencionPaciente !== '' &&
    form.estado !== '' &&
    form.numeroMuestras !== ''
  )
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

/**
 * Normaliza la región del cuerpo del backend al valor esperado por BodyRegionList
 */
const normalizeBodyRegion = (value: string | undefined | null): string => {
  if (!value) return ''
  const allowedValues = new Set([
    'cabeza','cuello','cara','cuero_cabelludo','oreja','nariz','boca','lengua','garganta','tiroides',
    'torax','mama_derecha','mama_izquierda','pulmon_derecho','pulmon_izquierdo','corazon','mediastino',
    'abdomen','estomago','intestino_delgado','intestino_grueso','colon','recto','higado','vesicula_biliar','pancreas','bazo','rinon_derecho','rinon_izquierdo','vejiga','utero','ovario_derecho','ovario_izquierdo','prostata','testiculo_derecho','testiculo_izquierdo',
    'brazo_derecho','brazo_izquierdo','antebrazo_derecho','antebrazo_izquierdo','mano_derecha','mano_izquierda','dedo_derecho','dedo_izquierdo',
    'muslo_derecho','muslo_izquierdo','pierna_derecha','pierna_izquierda','pie_derecho','pie_izquierdo','dedo_pie_derecho','dedo_pie_izquierdo',
    'piel_cabeza','piel_torax','piel_abdomen','piel_brazo','piel_pierna','piel_espalda','piel_gluteo',
    'ganglio_cervical','ganglio_axilar','ganglio_inguinal','ganglio_mediastinico','ganglio_abdominal',
    'otro','no_especificado'
  ])
  const basic = String(value)
    .toLowerCase()
    .normalize('NFD').replace(/[\u0300-\u036f]/g, '')
    .replace(/\s+/g, '_')
    .replace(/[-]+/g, '_')
    .replace(/__+/g, '_')
    .trim()

  // Mapeos especiales
  const specials: Record<string, string> = {
    'piel_de_torax': 'piel_torax',
    'piel_de_abdomen': 'piel_abdomen',
    'piel_de_brazo': 'piel_brazo',
    'piel_de_pierna': 'piel_pierna',
    'piel_de_espalda': 'piel_espalda',
    'piel_de_gluteo': 'piel_gluteo',
  }
  if (basic in specials) return specials[basic]

  // Remover artículos comunes y preposiciones sueltas
  const cleaned = basic
    .replace(/^el_/, '')
    .replace(/^la_/, '')
    .replace(/^los_/, '')
    .replace(/^las_/, '')
    .replace(/_de_/g, '_')
    .replace(/_del_/g, '_')

  if (allowedValues.has(basic)) return basic
  if (allowedValues.has(cleaned)) return cleaned

  // Heurísticas por palabras clave
  const contains = (text: string) => cleaned.includes(text)
  const side = contains('derech') ? 'derecho' : contains('izqu') ? 'izquierdo' : ''

  if (contains('torax')) return 'torax'
  if (contains('mama')) return side === 'izquierdo' ? 'mama_izquierda' : 'mama_derecha'
  if (contains('pulmon')) return side === 'izquierdo' ? 'pulmon_izquierdo' : 'pulmon_derecho'
  if (contains('rinon')) return side === 'izquierdo' ? 'rinon_izquierdo' : 'rinon_derecho'
  if (contains('ovario')) return side === 'izquierdo' ? 'ovario_izquierdo' : 'ovario_derecho'
  if (contains('testiculo')) return side === 'izquierdo' ? 'testiculo_izquierdo' : 'testiculo_derecho'
  if (contains('brazo')) return side === 'izquierdo' ? 'brazo_izquierdo' : 'brazo_derecho'
  if (contains('antebrazo')) return side === 'izquierdo' ? 'antebrazo_izquierdo' : 'antebrazo_derecho'
  if (contains('mano')) return side === 'izquierdo' ? 'mano_izquierda' : 'mano_derecha'
  if (contains('muslo')) return side === 'izquierdo' ? 'muslo_izquierdo' : 'muslo_derecho'
  if (contains('pierna')) return side === 'izquierdo' ? 'pierna_izquierda' : 'pierna_derecha'
  if (contains('pie')) return side === 'izquierdo' ? 'pie_izquierdo' : 'pie_derecho'
  if (contains('dedo_pie')) return side === 'izquierdo' ? 'dedo_pie_izquierdo' : 'dedo_pie_derecho'
  if (contains('abdomen')) return 'abdomen'
  if (contains('colon')) return 'colon'
  if (contains('recto')) return 'recto'
  if (contains('higado')) return 'higado'
  if (contains('vesicula')) return 'vesicula_biliar'
  if (contains('pancreas')) return 'pancreas'
  if (contains('bazo')) return 'bazo'
  if (contains('vejiga')) return 'vejiga'
  if (contains('utero')) return 'utero'
  if (contains('prostata')) return 'prostata'
  if (contains('intestino_delgado')) return 'intestino_delgado'
  if (contains('intestino_grueso')) return 'intestino_grueso'
  if (contains('ganglio') && contains('cervical')) return 'ganglio_cervical'
  if (contains('ganglio') && contains('axilar')) return 'ganglio_axilar'
  if (contains('ganglio') && contains('inguinal')) return 'ganglio_inguinal'
  if (contains('ganglio') && contains('mediastinico')) return 'ganglio_mediastinico'
  if (contains('ganglio') && contains('abdominal')) return 'ganglio_abdominal'

  // Fallback seguro: no especificado
  return 'no_especificado'
}


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
  const caseCode = props.caseCodeProp || foundCaseInfo.value?.CasoCode
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
      return mapping[tipo] || tipo
    }

    const updateData = {
      estado: form.estado as CaseState,
      medico_solicitante: form.medicoSolicitante ? { nombre: form.medicoSolicitante } : undefined,
      servicio: form.servicio || undefined,
      observaciones_generales: form.observaciones,
      muestras: form.muestras.map(muestra => ({
        region_cuerpo: muestra.regionCuerpo,
        pruebas: muestra.pruebas
          .filter(prueba => String(prueba.code).trim() !== '')
          .map(prueba => ({ 
            id: prueba.code, 
            nombre: prueba.nombre || prueba.code,
            cantidad: prueba.cantidad || 1
          }))
      })),
      patologo_asignado: form.patologoAsignado
        ? { codigo: form.patologoAsignado, nombre: selectedPathologist.value?.nombre || '' }
        : undefined,
      entidad_info: entityInfoToSend,
      // Incluir paciente con tipo_atencion actualizado
      paciente: {
        paciente_code: patientInfo.value?.codigo || cedulaToUse,
        cedula: cedulaToUse,
        nombre: patientInfo.value?.nombre || '',
        edad: patientInfo.value?.edad || 0,
        sexo: patientInfo.value?.sexo || '',
        entidad_info: entityInfoToSend || {
          id: form.entidadPaciente,
          nombre: selectedEntity.value?.nombre || ''
        },
        tipo_atencion: mapTipoAtencionToBackend(form.tipoAtencionPaciente),
        observaciones: patientInfo.value?.observaciones || '',
        // fecha_actualizacion se maneja automáticamente en el backend
      }
    }
    

    const updatedCaseResponse = await casesApiService.updateCase(caseCode, updateData)
    
    // Actualizar colección de pacientes para mantener coherencia
    const sexoForm = (() => {
      const s = String(patientInfo.value?.sexo || '').toLowerCase()
      if (s.startsWith('m')) return 'masculino'
      if (s.startsWith('f')) return 'femenino'
      return ''
    })()
    const patientDataToUpdate: PatientData = {
      pacienteCode: cedulaToUse,
      nombrePaciente: String(patientInfo.value?.nombre || ''),
      sexo: sexoForm as any,
      edad: String(patientInfo.value?.edad || ''),
      entidad: String(selectedEntity.value?.nombre || foundCaseInfo.value?.entidad_info?.nombre || ''),
      entidadCodigo: form.entidadPaciente,
      tipoAtencion: form.tipoAtencionPaciente as any,
      observaciones: ''
    }
    try {
      await patientsApiService.updatePatient(cedulaToUse, patientDataToUpdate)
    } catch (e: any) {
      throw new Error('El caso se actualizó, pero falló la actualización del paciente')
    }
    
    // Guardar caso actualizado para la notificación
    updatedCase.value = updatedCaseResponse
    
    // Emitir evento de actualización
    emit('case-updated', updatedCaseResponse)
    
    // Mostrar notificación de éxito con información detallada
    showSuccess('¡Caso Actualizado Exitosamente!', '')

    // Limpiar inmediatamente el formulario y la búsqueda.
    // La notificación usará únicamente los datos de updatedCase/foundCaseInfo.
    clearFormAfterSave()
  } catch (error: any) {
    showError('Error al actualizar el caso', error.message || 'Error desconocido')
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
        caseData.medico_solicitante?.nombre || 
        (caseData as any).medico_solicitante ||
        (caseData as any).medicoSolicitante ||
        '',
        
      servicio: 
        caseData.servicio ||
        (caseData as any).servicio ||
        '',
        
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
            regionCuerpo: 
              normalizeBodyRegion(
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
    
    // Guardar patólogo seleccionado (si viene en el caso)
    if ((caseData as any).patologo_asignado?.codigo) {
      selectedPathologist.value = {
        codigo: (caseData as any).patologo_asignado.codigo,
        nombre: (caseData as any).patologo_asignado.nombre || ''
      }
    } else {
      selectedPathologist.value = null
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
    selectedPathologist.value = {
      codigo: pathologist.documento,
      nombre: pathologist.nombre
    }
  } else {
    selectedPathologist.value = null
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
      muestra.pruebas[pruebaIndex].code = test.pruebaCode || test.code
      muestra.pruebas[pruebaIndex].nombre = test.pruebasName || test.nombre
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
 * Obtiene las muestras del caso
 */
const getMuestras = () => {
  return (updatedCase.value as any)?.muestras || form.muestras
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
    uc.medico_solicitante?.nombre ||
    uc.medicoSolicitante?.nombre ||
    fc.medico_solicitante?.nombre ||
    fc.medicoSolicitante ||
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