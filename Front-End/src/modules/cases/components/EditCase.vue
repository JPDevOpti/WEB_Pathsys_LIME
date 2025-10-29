<template>
  <div class="space-y-4 lg:space-y-6">
    <!-- Card 1: Case Search Section -->
    <ComponentCard 
      title="Buscar Caso" 
      description="Busque y verifique el caso que desea editar por código."
    >
      <template #icon>
        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </template>

      <div class="space-y-4">
        <CaseSearch
          v-model:case-code="searchCaseCode"
          :is-searching="isSearching"
          :error-message="searchError"
          :case-found="caseFound"
          @search="searchCase"
          @clear="onReset"
        />

        <!-- Compact case found summary (similar to patient verified) -->
        <div 
          v-if="caseFound && foundCaseInfo && !isCaseCompleted" 
          ref="caseVerifiedSection"
          class="mt-4 p-3 sm:p-4 pb-0 bg-green-50 border border-green-200 rounded-lg"
        >
          <div class="flex items-center justify-between">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
              </svg>
              <div>
                <h4 class="text-sm font-semibold text-green-800">Caso Cargado</h4>
                <p class="text-xs text-green-600 mt-0.5">Complete el formulario del caso abajo</p>
              </div>
            </div>
            <div class="text-right">
              <p class="text-xs text-green-600 font-medium">Código</p>
              <p class="text-sm font-semibold text-green-800 font-mono">{{ (foundCaseInfo as any)?.case_code || (foundCaseInfo as any)?.caso_code }}</p>
            </div>
          </div>
        </div>

        <!-- Completed case warning -->
        <div 
          v-if="caseFound && foundCaseInfo && isCaseCompleted" 
          class="mt-4 p-3 sm:p-4 bg-red-50 border border-red-200 rounded-lg"
        >
          <div class="flex items-start">
            <svg class="w-5 h-5 text-red-600 mr-2 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
            </svg>
            <div>
              <h4 class="text-sm font-semibold text-red-800">Caso Completado - No Editable</h4>
              <p class="text-xs text-red-600 mt-0.5">Este caso ya ha sido completado y no puede ser modificado</p>
            </div>
          </div>
        </div>

        <div>
          <Notification 
            :visible="notification.visible" 
            :type="notification.type" 
            :title="notification.title" 
            :message="notification.message" 
            :inline="true" 
            :auto-close="false" 
            @close="closeNotification" 
          />
        </div>

        <!-- Helper message when no case found -->
        <div v-if="!caseFound && !notification.visible" class="mt-4 bg-blue-50 border border-blue-200 rounded-lg p-6 text-center">
          <div class="flex flex-col items-center space-y-3">
            <svg class="w-12 h-12 text-blue-400" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            <h3 class="text-lg font-medium text-blue-800">Busque un caso para editar</h3>
            <p class="text-blue-600 text-sm">Ingrese el código del caso en el campo de búsqueda arriba para comenzar a editar un caso existente</p>
          </div>
        </div>
      </div>

      <template #footer>
        <div class="flex justify-end">
          <BaseButton 
            v-if="caseFound && foundCaseInfo && !isCaseCompleted"
            size="xs" 
            variant="ghost"
            :custom-class="'border border-red-600 text-red-600 bg-white hover:bg-red-50 focus:ring-red-500'"
            @click="openDeleteConfirm"
            :disabled="isDeleting"
          >
            <template #icon-left>
              <TrashIcon class="w-4 h-4 mr-1" />
            </template>
            Eliminar caso
          </BaseButton>
        </div>
      </template>
    </ComponentCard>

    <!-- Cards 2 & 3: Side by side - Edit Form (left 60%) and Patient Info (right 40%) -->
    <div v-if="caseFound && !isCaseCompleted" class="grid grid-cols-1 lg:grid-cols-5 gap-4 lg:gap-6 items-start">
      <!-- Card 2: Edit Form (LEFT - 60%) -->
      <div class="lg:col-span-3">
        <ComponentCard 
          title="Información del Caso" 
          description="Modifique los datos médicos del caso."
        >
          <template #icon>
            <CaseIcon class="w-5 h-5 mr-2 text-blue-600" />
          </template>

          <CaseForm
            :form-data="formData"
            :edit-mode="true"
            :state="state"
            :assigned-pathologist="assignedPathologist"
            :tipo-atencion-options="tipoAtencionOptions"
            :prioridad-options="prioridadOptions"
            :estado-options="estadoOptions"
            @add-test="addTestToSample"
            @remove-test="removeTestFromSample"
            @test-selected="handleTestSelected"
            @entity-selected="onEntitySelected"
            @pathologist-selected="onPathologistSelected"
            @update:state="(value: string) => state = value"
            @update:assigned-pathologist="(value: string) => assignedPathologist = value"
          />

          <template #footer>
            <div class="flex flex-col sm:flex-row justify-end gap-3">
              <ClearButton @click="onReset" :disabled="isLoading" />
              <SaveButton 
                text="Guardar Cambios" 
                @click="onSubmit" 
                :disabled="isLoading || !isFormValid" 
                :loading="isLoading" 
              />
            </div>
          </template>
        </ComponentCard>
      </div>

      <!-- Card 3: Patient Info (RIGHT - 40%) -->
      <div class="lg:col-span-2">
        <ComponentCard 
          title="Información del Paciente" 
          description="Datos del paciente asociado al caso."
        >
          <template #icon>
            <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M16 7a4 4 0 11-8 0 4 4 0 018 0zM12 14a7 7 0 00-7 7h14a7 7 0 00-7-7z" />
            </svg>
          </template>

          <PatientInfoCard 
            :patient="patientDisplayInfo"
            badge-label="Cargado"
            empty-state-message="No hay información del caso"
            empty-state-subtext="Busque un caso para continuar"
          />

          <template #footer>
            <div class="flex justify-end">
              <BaseButton 
                size="sm" 
                variant="outline"
                :disabled="!patientDisplayInfo || !patientDisplayInfo.patientCode"
                @click="openEditPatientModal"
              >
                <template #icon-left>
                  <EditPatientIcon class="w-4 h-4 mr-2" />
                </template>
                Editar datos del paciente
              </BaseButton>
            </div>
          </template>
        </ComponentCard>
      </div>
    </div>

    <!-- Validation alert -->
    <div v-if="caseFound && !isFormValid && !isCaseCompleted" class="p-4 bg-yellow-50 border border-yellow-200 rounded-lg">
      <div class="flex items-start">
        <svg class="w-5 h-5 text-yellow-500 mr-2 mt-0.5 flex-shrink-0" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
        </svg>
        <div>
          <h4 class="text-sm font-semibold text-yellow-800 mb-2">Campos requeridos faltantes</h4>
          <p class="text-sm text-yellow-700 mb-2">Complete los siguientes campos:</p>
          <ul class="list-disc list-inside space-y-1 text-sm text-yellow-700">
            <li v-for="error in validationErrors" :key="error">{{ error }}</li>
          </ul>
        </div>
      </div>
    </div>

    <!-- Success notification -->
    <div ref="notificationContainer">
      <CaseSuccessCard
        :visible="showCaseSuccessCard"
        :case-data="updatedCase || foundCaseInfo || {}"
        mode="updated"
        @close="closeCaseSuccessCard"
      />
    </div>
  </div>

  <!-- Modal: Editar Paciente -->
  <Modal v-model="isEditPatientOpen" title="Editar datos del paciente" size="lg">
    <div v-if="isEditPatientLoading" class="p-6 text-center text-sm text-gray-600">Cargando datos del paciente...</div>
    <div v-else class="space-y-6">
      <!-- Encabezado visual del paciente -->
      <div class="bg-white rounded-2xl border border-gray-200 overflow-hidden shadow-sm">
        <div class="px-6 py-5 border-b border-gray-200">
          <div class="flex items-start gap-4">
            <div class="flex-shrink-0">
              <div class="w-12 h-12 bg-blue-50 rounded-xl flex items-center justify-center">
                <EditPatientIcon class="w-6 h-6 text-blue-600" />
              </div>
            </div>
            <div class="flex-1 min-w-0">
              <div class="flex flex-col md:flex-row md:items-start md:justify-between gap-3">
                <div class="min-w-0">
                  <h3 class="text-xl font-bold text-gray-900 mb-1">
                    {{ patientDisplayInfo ? patientDisplayInfo.name : 'Paciente' }}
                  </h3>
                  <div class="flex items-center flex-wrap gap-3">
                    <div class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Código</span>
                      <span class="text-lg font-bold text-gray-900 font-mono">
                        {{ patientDisplayInfo ? patientDisplayInfo.patientCode : '' }}
                      </span>
                    </div>
                    <div v-if="patientDisplayInfo?.entity" class="flex items-center gap-1.5">
                      <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Entidad</span>
                      <span class="text-sm font-semibold text-gray-900">{{ patientDisplayInfo.entity }}</span>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          </div>
        </div>

        <!-- Contenido del formulario -->
        <div class="px-6 py-5 space-y-6">
          <!-- Sección: Identificación -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Identificación</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <FormSelect 
                v-model="editPatientForm.identification_type" 
                label="Tipo de identificación" 
                :options="identificationTypeOptions" 
                placeholder="Seleccione tipo" 
              />
              <FormInputField 
                v-model="editPatientForm.identification_number" 
                label="Número de identificación" 
                placeholder="Ingrese número de identificación" 
              />
            </div>
          </div>
          <!-- Sección: Datos Personales -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Datos Personales</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <FormInputField v-model="editPatientForm.first_name" label="Primer nombre" placeholder="Ingrese primer nombre" />
              <FormInputField v-model="editPatientForm.second_name" label="Segundo nombre" placeholder="Ingrese segundo nombre" />
              <FormInputField v-model="editPatientForm.first_lastname" label="Primer apellido" placeholder="Ingrese primer apellido" />
              <FormInputField v-model="editPatientForm.second_lastname" label="Segundo apellido" placeholder="Ingrese segundo apellido" />
              <FormInputField v-model="editPatientForm.birth_date" type="date" label="Fecha de nacimiento" placeholder="Seleccione fecha" />
              <FormSelect v-model="editPatientForm.gender" label="Sexo" :options="genderOptions" placeholder="Seleccione sexo" />
            </div>
          </div>

          <!-- Sección: Ubicación y Contacto -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Ubicación y Contacto</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <MunicipalityList 
                v-model="editPatientForm.municipality_code"
                label="Municipio"
                placeholder="Buscar y seleccionar municipio"
                @municipality-code-change="handleMunicipalityCodeChange"
                @municipality-name-change="handleMunicipalityNameChange"
                @subregion-change="handleSubregionChange"
              />
              <FormInputField v-model="editPatientForm.address" label="Dirección" placeholder="Dirección del paciente" />
            </div>
          </div>

          <!-- Sección: Cobertura y Atención -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Cobertura y Atención</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <div class="grid grid-cols-1 sm:grid-cols-2 gap-4 sm:gap-6">
              <EntityList 
                v-model="editPatientForm.entity_id"
                label="Entidad"
                placeholder="Buscar y seleccionar entidad"
                @entity-selected="handleEntitySelected"
              />
              <FormSelect v-model="editPatientForm.care_type" label="Tipo de atención" :options="careTypeOptions" placeholder="Seleccione tipo" />
            </div>
          </div>

          <!-- Sección: Observaciones -->
          <div class="space-y-4">
            <div class="flex items-center gap-2">
              <span class="text-xs text-gray-500 font-medium uppercase tracking-wide">Observaciones</span>
              <div class="flex-1 h-px bg-gray-200"></div>
            </div>
            <FormTextarea v-model="editPatientForm.observations" label="Observaciones" placeholder="Observaciones del paciente" :rows="4" :max-length="500" />
          </div>
        </div>
      </div>
    </div>

    <template #footer>
      <div class="px-4 py-3 border-t border-gray-200 bg-gray-50 flex justify-end gap-2 sticky bottom-0 z-10">
        <SaveButton text="Guardar" :loading="isEditPatientLoading" @click="saveEditPatient" />
      </div>
    </template>
  </Modal>

  <!-- Confirm Delete Dialog -->
  <ConfirmDialog
    v-model="showConfirmDelete"
    title="Eliminar caso"
    subtitle="Esta acción no se puede deshacer"
    :message="`¿Está seguro de eliminar el caso ${(foundCaseInfo as any)?.case_code || (foundCaseInfo as any)?.caso_code}?`"
    confirm-text="Eliminar"
    cancel-text="Cancelar"
    :loading-confirm="isDeleting"
    :icon="TrashIcon"
    @confirm="confirmDelete"
    @cancel="showConfirmDelete = false"
  />

  <!-- Delete Success Card -->
  <CaseDeleteSuccessCard
    :visible="showDeleteSuccessCard"
    :case-data="deletedCaseData || {}"
    @close="closeDeleteSuccessCard"
  />
</template>

<script setup lang="ts">
import { ref, computed, watch, nextTick } from 'vue'
import { ComponentCard } from '@/shared/components'
import { SaveButton, ClearButton, BaseButton } from '@/shared/components/ui/buttons'
import { useNotifications } from '../composables/useNotifications'
import Notification from '@/shared/components/ui/feedback/Notification.vue'
import { CaseSuccessCard } from '@/shared/components/ui/feedback'
import { useCaseForm } from '../composables/useCaseForm'
import { casesApiService } from '../services/casesApi.service'
import pathologistApi from '../services/pathologistApi.service'
import type { CaseModel } from '../types'
import { CaseIcon, EditPatientIcon } from '@/assets/icons'
import { PatientInfoCard, CaseForm, CaseSearch } from './Shared'
import { Modal } from '@/shared/components/layout'
import { FormInputField, FormSelect, FormTextarea } from '@/shared/components/ui/forms'
import { MunicipalityList, EntityList } from '@/shared/components/ui/lists'
import patientsApiService from '@/modules/patients/services/patientsApi.service'
import { IdentificationType } from '@/modules/patients/types'
import type { PatientData, Gender, CareType, UpdatePatientRequest } from '@/modules/patients/types'
import { ConfirmDialog } from '@/shared/components/ui/feedback'
import CaseDeleteSuccessCard from '@/shared/components/ui/feedback/CaseDeleteSuccessCard.vue'
import { TrashIcon } from '@/assets/icons'

interface Props {
  caseCodeProp?: string
}

interface Emits {
  (e: 'case-updated', caseData: CaseModel): void
}

const props = defineProps<Props>()
const emit = defineEmits<Emits>()

const { notification, showError, closeNotification } = useNotifications()
const { formData, errors, clearForm: clearCaseForm, addTestToSample, removeTestFromSample, createEmptySubSample } = useCaseForm()

// UI and data state
const isLoading = ref(false)
const updatedCase = ref<any>(null)
const patientInfo = ref<any>(null)
const notificationContainer = ref<HTMLElement | null>(null)
const caseVerifiedSection = ref<HTMLElement | null>(null)
const suppressValidation = ref(false)
const resetKey = ref(0)
const showCaseSuccessCard = ref(false)
const currentCaseCode = ref('')
const searchCaseCode = ref('')
const isSearching = ref(false)
const searchError = ref('')
const caseFound = ref(false)
const foundCaseInfo = ref<CaseModel | null>(null)

// Delete case state
const showConfirmDelete = ref(false)
const isDeleting = ref(false)
const showDeleteSuccessCard = ref(false)
const deletedCaseData = ref<any>(null)
const state = ref('')
const assignedPathologist = ref('')
const selectedEntity = ref<{ codigo: string; nombre: string } | null>(null)
const selectedPathologist = ref<{ codigo: string; nombre: string } | null>(null)

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
  const samplesOk = formData.samples.length > 0 && (formData.samples as any).every((s: any) => {
    if (!String(s.bodyRegion || '').trim()) return false
    if (!s.tests || s.tests.length === 0) return false
    return s.tests.every((t: any) => String(t.code || '').trim() !== '' && (t.quantity ?? 0) >= 1)
  })
  return baseOk && samplesOk
})

const isCaseCompleted = computed(() => {
  const fc: any = foundCaseInfo.value || {}
  const estado = fc.estado || fc.state || ''
  const v = String(estado).toLowerCase()
  return v === 'completado' || v === 'completed'
})

const patientDisplayInfo = computed(() => {
  if (!patientInfo.value) return null
  
  return {
    name: patientInfo.value.nombrePaciente || 'Sin nombre',
    patientCode: patientInfo.value.pacienteCode || 'Sin código',
    age: patientInfo.value.edad || '0',
    gender: patientInfo.value.sexo || 'Sin especificar',
    careType: patientInfo.value.tipoAtencion || 'Sin especificar',
    entity: patientInfo.value.entidad || 'Sin especificar',
    observations: patientInfo.value.observaciones || ''
  }
})

// ===== Estado del Modal de edición de paciente =====
const isEditPatientOpen = ref(false)
const isEditPatientLoading = ref(false)
const editPatientCode = ref('')
const originalEditPatientData = ref<PatientData | null>(null)
const editPatientForm = ref({
  patient_code: '',
  identification_type: '' as IdentificationType | '',
  identification_number: '',
  first_name: '',
  second_name: '',
  first_lastname: '',
  second_lastname: '',
  birth_date: '',
  gender: '' as Gender | '',
  municipality_code: '',
  municipality_name: '',
  subregion: '',
  address: '',
  entity_id: '',
  entity_name: '',
  care_type: '' as CareType | '',
  observations: ''
})

const genderOptions = [
  { value: 'Masculino', label: 'Masculino' },
  { value: 'Femenino', label: 'Femenino' }
]

const careTypeOptions = [
  { value: 'Ambulatorio', label: 'Ambulatorio' },
  { value: 'Hospitalizado', label: 'Hospitalizado' }
]

const identificationTypeOptions = [
  { value: IdentificationType.CEDULA_CIUDADANIA, label: 'Cédula de Ciudadanía' },
  { value: IdentificationType.TARJETA_IDENTIDAD, label: 'Tarjeta de Identidad' },
  { value: IdentificationType.CEDULA_EXTRANJERIA, label: 'Cédula de Extranjería' },
  { value: IdentificationType.PASAPORTE, label: 'Pasaporte' },
  { value: IdentificationType.REGISTRO_CIVIL, label: 'Registro Civil' },
  { value: IdentificationType.DOCUMENTO_EXTRANJERO, label: 'Documento Extranjero' },
  { value: IdentificationType.NIT, label: 'NIT' }
]

const openEditPatientModal = async () => {
  if (!patientInfo.value?.pacienteCode) return
  isEditPatientLoading.value = true
  isEditPatientOpen.value = true
  try {
    const code = String(patientInfo.value.pacienteCode)
    editPatientCode.value = code
    const patient: PatientData = await patientsApiService.getPatientByCode(code)
    editPatientForm.value = {
      patient_code: patient.patient_code || '',
      identification_type: (patient.identification_type as IdentificationType) || '',
      identification_number: patient.identification_number || '',
      first_name: patient.first_name || '',
      second_name: patient.second_name || '',
      first_lastname: patient.first_lastname || '',
      second_lastname: patient.second_lastname || '',
      birth_date: patient.birth_date || '',
      gender: patient.gender || '',
      municipality_code: patient.location?.municipality_code || '',
      municipality_name: patient.location?.municipality_name || '',
      subregion: patient.location?.subregion || '',
      address: patient.location?.address || '',
      entity_id: patient.entity_info?.id || '',
      entity_name: patient.entity_info?.name || '',
      care_type: patient.care_type || '',
      observations: patient.observations || ''
    }
    originalEditPatientData.value = patient
  } catch (e) {
    // Mantener el modal abierto para permitir reintento
  } finally {
    isEditPatientLoading.value = false
  }
}

const handleMunicipalityCodeChange = (code: string) => { editPatientForm.value.municipality_code = code }
const handleMunicipalityNameChange = (name: string) => { editPatientForm.value.municipality_name = name }
const handleSubregionChange = (subregion: string) => { editPatientForm.value.subregion = subregion }
const handleEntitySelected = (entity: any) => {
  if (entity) {
    editPatientForm.value.entity_id = entity.codigo || entity.id || ''
    editPatientForm.value.entity_name = entity.nombre || entity.name || ''
  } else {
    editPatientForm.value.entity_id = ''
    editPatientForm.value.entity_name = ''
  }
}

const saveEditPatient = async () => {
  if (!editPatientCode.value) return
  isEditPatientLoading.value = true
  try {
    // Si cambia identificación, validar duplicados y actualizar primero
    if (originalEditPatientData.value && (
      editPatientForm.value.identification_type !== originalEditPatientData.value.identification_type ||
      editPatientForm.value.identification_number !== originalEditPatientData.value.identification_number
    )) {
      const exists = await patientsApiService.checkPatientExists(
        editPatientForm.value.identification_type as IdentificationType,
        String(editPatientForm.value.identification_number || '').trim()
      )
      if (exists) {
        showError('Identificación duplicada', 'Ya existe un paciente con el tipo y número de identificación proporcionados')
        return
      }
      const changed = await patientsApiService.changeIdentification(
        editPatientForm.value.patient_code || editPatientCode.value,
        editPatientForm.value.identification_type as IdentificationType,
        String(editPatientForm.value.identification_number || '').trim()
      )
      editPatientCode.value = changed.patient_code
      editPatientForm.value.patient_code = changed.patient_code
      originalEditPatientData.value = changed
    }

    const hasLocation = !!(
      editPatientForm.value.municipality_code?.trim() ||
      editPatientForm.value.municipality_name?.trim() ||
      editPatientForm.value.subregion?.trim() ||
      editPatientForm.value.address?.trim()
    )

    const payload: UpdatePatientRequest = {
      first_name: editPatientForm.value.first_name.trim() || undefined,
      second_name: editPatientForm.value.second_name.trim() || undefined,
      first_lastname: editPatientForm.value.first_lastname.trim() || undefined,
      second_lastname: editPatientForm.value.second_lastname.trim() || undefined,
      birth_date: editPatientForm.value.birth_date || undefined,
      gender: (editPatientForm.value.gender || undefined) as Gender | undefined,
      care_type: (editPatientForm.value.care_type || undefined) as CareType | undefined,
      observations: editPatientForm.value.observations.trim() || undefined
    }
    if (hasLocation) {
      payload.location = {
        municipality_code: editPatientForm.value.municipality_code.trim(),
        municipality_name: editPatientForm.value.municipality_name.trim(),
        subregion: editPatientForm.value.subregion.trim(),
        address: editPatientForm.value.address.trim()
      }
    }
    if (editPatientForm.value.entity_id?.trim() && editPatientForm.value.entity_name?.trim()) {
      payload.entity_info = {
        id: editPatientForm.value.entity_id.trim(),
        name: editPatientForm.value.entity_name.trim()
      }
    }

    const updated: PatientData = await patientsApiService.updatePatient(editPatientCode.value, payload)

    // Refrescar información del paciente en la UI del caso
    patientInfo.value = {
      ...patientInfo.value,
      pacienteCode: updated.patient_code || patientInfo.value?.pacienteCode || '',
      nombrePaciente: `${updated.first_name} ${updated.second_name || ''} ${updated.first_lastname} ${updated.second_lastname || ''}`.replace(/\s+/g, ' ').trim(),
      sexo: updated.gender || patientInfo.value?.sexo || '',
      entidad: updated.entity_info?.name || patientInfo.value?.entidad || '',
      tipoAtencion: updated.care_type || patientInfo.value?.tipoAtencion || '',
      observaciones: updated.observations || (patientInfo.value as any)?.observaciones || ''
    }

    isEditPatientOpen.value = false
  } catch (e: any) {
    // En caso de error se podría mostrar notificación reutilizando useNotifications
  } finally {
    isEditPatientLoading.value = false
  }
}

const validationErrors = computed(() => {
  const errorsList: string[] = []
  const fields: Array<{value: any, name: string}> = [
    { value: formData.entryDate, name: 'Fecha de ingreso' },
    { value: formData.requestingPhysician, name: 'Médico solicitante' },
    { value: formData.service, name: 'Servicio' },
    { value: formData.casePriority, name: 'Prioridad del caso' },
    { value: state.value, name: 'Estado del caso' },
    { value: formData.numberOfSamples, name: 'Número de muestras' },
    { value: formData.patientEntity, name: 'Entidad del paciente' },
    { value: formData.patientCareType, name: 'Tipo de atención' }
  ]
  
  for (const field of fields) {
    if (!field.value) errorsList.push(field.name)
  }
  
  (formData.samples as any)?.forEach((sample: any, i: number) => {
    if (!sample.bodyRegion) errorsList.push(`Submuestra ${i + 1}: Región del cuerpo`)
    if (!sample.tests?.length) errorsList.push(`Submuestra ${i + 1}: Al menos una prueba`)
    sample.tests?.forEach((test: any, j: number) => {
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

const searchCase = async () => {
  if (!searchCaseCode.value.trim()) {
    searchError.value = 'Por favor ingrese un código de caso'
    return
  }

  if (!/^\d{4}-\d{5}$/.test(searchCaseCode.value)) {
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
          return samples.map((s: any, i: number) => ({
            number: i + 1,
            bodyRegion: s.body_region || s.regionCuerpo || s.region_cuerpo || '',
            tests: (s.tests || s.pruebas || []).map((t: any) => ({
              code: t.id || t.code || t.codigo || '',
              name: t.name || t.nombre || '',
              quantity: t.quantity || t.cantidad || 1
            }))
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
      nombrePaciente: getField(['patient_info.name', 'paciente.nombre', 'patient_info.nombrePaciente', 'nombre_paciente'], 'Sin nombre'),
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
         const patologoCode = (pathologist as any).patologo_code || codigo
         const patologoData = {
           codigo: patologoCode,
           nombre: (pathologist as any).patologo_name || (pathologist as any).nombre || ''
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

  } catch (error: any) {
    showError('Error al cargar datos del caso', error.message || 'Error desconocido')
  }
}

const onSubmit = async () => {
  const caseCode = props.caseCodeProp || (foundCaseInfo.value as any)?.case_code || (foundCaseInfo.value as any)?.caso_code

  if (isCaseCompleted.value) {
    showError('Caso completado', 'No se puede editar un caso que ya ha sido completado.')
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

  const cedulaToUse = formData.patientDocument || (foundCaseInfo.value as any)?.paciente?.paciente_code || (foundCaseInfo.value as any)?.patient_info?.patient_code
  if (!cedulaToUse) {
    showError('Información incompleta', 'No se encontró información del paciente para este caso')
    return
  }

  isLoading.value = true
  try {
    const entityInfoToSend = selectedEntity.value?.codigo && selectedEntity.value?.nombre
      ? { id: selectedEntity.value.codigo, nombre: selectedEntity.value.nombre }
      : undefined

    const mapTipoAtencionToBackend = (tipo: string): string => tipo || 'Ambulatorio'

    const estadoToSend = state.value || 'En proceso'
    const prioridadToSend = formData.casePriority || 'Normal'

    const existingSamples = (((foundCaseInfo.value as any)?.muestras) || []) as any[]
    const samplesClean = (formData.samples as any).map((s: any, idx: number) => {
      const region = s.bodyRegion || existingSamples[idx]?.region_cuerpo || existingSamples[idx]?.regionCuerpo || ''
      return {
        body_region: region,
        tests: s.tests.map((t: any) => ({ id: String(t.code), name: t.name || String(t.code), quantity: Number(t.quantity) || 1 }))
      }
    })

    const allEmptyRegions = samplesClean.every((s: any) => !s.body_region)
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
        name: patientInfo.value?.nombrePaciente || '',
        age: parseInt(patientInfo.value?.edad) || 0,
        gender: patientInfo.value?.sexo || '',
        entity_info: pacienteEntidad ? { id: pacienteEntidad.id, name: pacienteEntidad.nombre } : { id: '', name: '' },
        care_type: mapTipoAtencionToBackend(formData.patientCareType),
        observations: (patientInfo.value as any)?.observaciones || undefined
      }
    }

    if (updateData.samples && updateData.samples.length) {
      updateData.samples = updateData.samples.filter((s: any) => s.body_region)
      if (!updateData.samples.length) delete updateData.samples
    } else if (!updateData.samples && (foundCaseInfo.value as any)?.muestras?.length) {
      delete updateData.samples
    }

    Object.keys(updateData).forEach(k => updateData[k] === undefined && delete updateData[k])
    if (updateData.patient_info) {
      Object.keys(updateData.patient_info).forEach(k => updateData.patient_info[k] === undefined && delete updateData.patient_info[k])
    }

    const updatedCaseResponse = await casesApiService.updateCase(caseCode, updateData)

    const uc = updatedCaseResponse as any
    
    // Obtener el nombre de la entidad desde selectedEntity o desde el response
    const entityName = selectedEntity.value?.nombre || 
                      uc.patient_info?.entity_info?.name || 
                      formData.patientEntity || 
                      'No especificada'
    const entityId = selectedEntity.value?.codigo || 
                    uc.patient_info?.entity_info?.id || 
                    formData.patientEntity || 
                    ''
    
    const adapted = {
      ...uc,
      case_code: uc.case_code || (foundCaseInfo.value as any)?.caso_code || caseCode,
      entity_info: {
        id: entityId,
        name: entityName
      },
      paciente: uc.patient_info ? {
        paciente_code: uc.patient_info.patient_code,
        nombre: uc.patient_info.name,
        edad: uc.patient_info.age,
        sexo: uc.patient_info.gender,
        entity_info: { 
          nombre: entityName, 
          id: entityId,
          name: entityName
        },
        entity: entityName,
        tipo_atencion: uc.patient_info.care_type,
        care_type: uc.patient_info.care_type,
        careType: uc.patient_info.care_type
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
    closeNotification()
    showCaseSuccessCard.value = true
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
    showError('Error al actualizar el caso', msg || 'Error desconocido')
  } finally {
    isLoading.value = false
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
  currentCaseCode.value = ''
  updatedCase.value = null
  closeNotification()
  resetKey.value++
}

const onEntitySelected = (entity: any | null) => {
  if (entity && entity.codigo) {
    selectedEntity.value = { codigo: entity.codigo, nombre: entity.nombre }
  } else {
    selectedEntity.value = null
  }
}

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

const handleTestSelected = (sampleIndex: number, testIndex: number, test: any) => {
  if (test && sampleIndex >= 0 && sampleIndex < (formData.samples as any).length) {
    const sample = (formData.samples as any)[sampleIndex]
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
}

const translateCaseState = (value: any): string => {
  const raw = String(value || '').toLowerCase()
  const map: Record<string, string> = {
    'in process': 'En proceso',
    'in_process': 'En proceso',
    'processing': 'En proceso',
    'to sign': 'Por firmar',
    'to deliver': 'Por entregar',
    'completed': 'Completado',
    'finished': 'Completado'
  }
  return map[raw] || String(value || 'En proceso')
}

const closeCaseSuccessCard = () => {
  showCaseSuccessCard.value = false
}

// Delete case functions
const openDeleteConfirm = () => {
  showConfirmDelete.value = true
}

const confirmDelete = async () => {
  if (!foundCaseInfo.value) {
    showConfirmDelete.value = false
    return
  }
  
  isDeleting.value = true
  try {
    const caseCode = (foundCaseInfo.value as any)?.case_code || (foundCaseInfo.value as any)?.caso_code
    if (!caseCode) {
      throw new Error('Código de caso no encontrado')
    }
    
    // Store case data before deletion
    deletedCaseData.value = {
      case_code: caseCode,
      codigo: caseCode,
      code: caseCode
    }
    
    await casesApiService.deleteCase(caseCode)
    showConfirmDelete.value = false
    
    // Show success card instead of toast notification
    showDeleteSuccessCard.value = true
    
    // Reset form state
    onReset()
  } catch (error: any) {
    const msg = error.response?.data?.detail || error.message || 'Error al eliminar el caso'
    showError('Error al eliminar', msg)
    showConfirmDelete.value = false
  } finally {
    isDeleting.value = false
  }
}

const closeDeleteSuccessCard = () => {
  showDeleteSuccessCard.value = false
  deletedCaseData.value = null
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

watch(
  () => showCaseSuccessCard.value,
  async (visible) => {
    if (visible) {
      await nextTick()
      if (notificationContainer.value) {
        notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
      }
    }
  }
)

watch(
  () => caseFound.value,
  async (found) => {
    if (found && !isCaseCompleted.value) {
      await nextTick()
      if (caseVerifiedSection.value) {
        caseVerifiedSection.value.scrollIntoView({ behavior: 'smooth', block: 'start' })
      }
    }
  }
)
</script>
