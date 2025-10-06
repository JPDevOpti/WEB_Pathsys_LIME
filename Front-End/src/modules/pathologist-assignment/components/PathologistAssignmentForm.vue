<template>
  <!-- Assign a pathologist to an existing case -->
  <div class="space-y-4 lg:space-y-6">
    <!-- Card 1: Search Section -->
    <ComponentCard 
      title="Buscar Caso"
      description="Ingrese el código del caso para asignar o reasignar un patólogo."
    >
      <template #icon>
        <svg class="w-5 h-5 mr-2 text-blue-600" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
        </svg>
      </template>

      <div class="space-y-4">
        <!-- Case search input -->
        <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
          <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
            <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
            </svg>
            Código del Caso
          </h3>
          
          <div class="flex flex-col sm:flex-row gap-3 sm:gap-4 items-stretch sm:items-end">
            <div class="flex-1">
              <!-- Code input with auto-format (YYYY-NNNNN) -->
              <FormInputField
                id="codigo-caso"
                v-model="codigoCaso"
                type="text"
                placeholder="Ejemplo: 2025-00001"
                maxlength="10"
                autocomplete="off"
                :disabled="isLoadingSearch"
                @update:model-value="handleCodigoChange"
                @keydown.enter.prevent="buscarCaso"
                @input="handleCodigoChange"
                class="flex-1"
              />
              
              <!-- Client-side format validation hint -->
              <div v-if="codigoCaso && !isValidCodigoFormat(codigoCaso)" class="mt-1 text-xs text-red-600">
                El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)
              </div>
            </div>
            
            <div class="flex gap-2 sm:gap-3">
              <!-- Search / Clear actions -->
              <SearchButton v-if="!casoEncontrado" text="Buscar" loading-text="Buscando..." :loading="isLoadingSearch" @click="buscarCaso" size="md" variant="primary" />
              <ClearButton v-if="casoEncontrado" text="Limpiar" @click="limpiarFormulario" />
            </div>
          </div>

          <!-- Search error banner -->
          <div v-if="searchError" class="mt-3 p-3 bg-red-50 border border-red-200 rounded-lg">
            <div class="flex items-center">
              <svg class="w-5 h-5 text-red-500 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"/>
              </svg>
              <p class="text-sm text-red-600">{{ searchError }}</p>
            </div>
          </div>

          <!-- Compact case found summary -->
          <div v-if="casoEncontrado && casoInfo" class="mt-4 p-3 sm:p-4 bg-green-50 border border-green-200 rounded-lg">
            <div class="flex items-center justify-between">
              <div class="flex items-center">
                <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
                </svg>
                <div>
                  <h4 class="text-sm font-semibold text-green-800">Caso Encontrado</h4>
                  <p class="text-xs text-green-600 mt-0.5">Revise los detalles y asigne un patólogo abajo</p>
                </div>
              </div>
              <div class="text-right">
                <p class="text-xs text-green-600 font-medium">Código</p>
                <p class="text-sm font-mono font-bold text-green-800">{{ casoInfo.case_code || (casoInfo as any).caso_code || 'N/A' }}</p>
              </div>
            </div>
          </div>
        </div>

        <!-- Inline notification container -->
        <div>
          <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification" />
        </div>
      </div>
    </ComponentCard>

    <!-- Cards 2 & 3: Side by side - Pathologist Assignment (left) and Case Details (right) -->
    <div ref="assignmentSection" class="grid grid-cols-1 lg:grid-cols-2 gap-4 lg:gap-6 items-start">
      <!-- Card 2: Pathologist Assignment with Actions (LEFT) -->
      <PathologistSelector
        v-model="formData.patologoId"
        :current-pathologist-info="patologoActualDisplay !== 'Sin asignar' ? patologoActualDisplay : null"
        :assignment-preview="assignmentPreview"
        :errors="validationErrors.patologoId"
        :disabled="!casoEncontrado || (!!casoInfo && isCaseCompleted(casoInfo))"
        :show-actions="casoEncontrado && !(casoInfo && isCaseCompleted(casoInfo))"
        :is-loading-assignment="isLoadingAssignment"
        :is-form-valid="isFormValid"
        :button-text="getButtonText"
        @pathologist-selected="handlePathologistSelected"
        @load-success="handlePathologistListLoaded"
        @update:assignment-preview="assignmentPreview = $event"
        @clear="limpiarFormulario"
        @assign="handleAsignarClick"
      />

      <!-- Card 3: Case Detail (RIGHT) -->
      <CaseDetailCard
        :case-info="casoInfo"
        :case-state="estadoDisplay"
        :current-pathologist="patologoActualDisplay"
      />
    </div>

    <!-- Validation alert -->
    <ValidationAlert :visible="showValidationError" :errors="validationErrorsList" />
  </div>
</template>

<script setup lang="ts">
import { ref, computed, watch, reactive, nextTick } from 'vue'
import { usePathologistAssignment } from '../composables/usePathologistAssignment'
import { usePathologistAPI } from '@/modules/cases/composables/usePathologistAPI'
import { useNotifications } from '@/modules/cases/composables/useNotifications'
import type { PathologistAssignmentFormData, CaseModel } from '../types'
import type { FormPathologistInfo } from '@/modules/cases/types/pathologist'
import ComponentCard from '@/shared/components/layout/ComponentCard.vue'
import FormInputField from '@/shared/components/ui/forms/FormInputField.vue'
import SearchButton from '@/shared/components/ui/buttons/SearchButton.vue'
import ClearButton from '@/shared/components/ui/buttons/ClearButton.vue'
import Notification from '@/shared/components/ui/feedback/Notification.vue'
import ValidationAlert from '@/shared/components/ui/feedback/ValidationAlert.vue'
import PathologistSelector from './PathologistSelector.vue'
import CaseDetailCard from './CaseDetailCard.vue'

// UI state
const codigoCaso = ref('')
const hasAttemptedSubmit = ref(false)
const showValidationError = ref(false)
const isLoadingAssignment = ref(false)
const assignmentSection = ref<HTMLElement>()

// Form state
const formData = reactive<PathologistAssignmentFormData>({ 
  patologoId: '', 
  fechaAsignacion: '' 
})

interface AssignmentPreviewInfo {
  id: string
  name: string
  code?: string
  initials?: string
  document?: string
}

// Composables
const {
  isLoadingSearch,
  searchError,
  casoEncontrado,
  casoInfo,
  buscarCaso: buscarCasoComposable,
  isValidCodigoFormat,
  isCaseCompleted,
  getEstadoDisplay,
  getPatologoActual,
  limpiarFormulario: limpiarFormularioComposable
} = usePathologistAssignment()

const { assignPathologist } = usePathologistAPI()
const { notification, showNotification, closeNotification } = useNotifications()
const assignmentPreview = ref<AssignmentPreviewInfo | null>(null)

// Computed properties
const isFormValid = computed(() => 
  casoEncontrado.value && 
  formData.patologoId.trim() !== '' && 
  !isCaseCompleted(casoInfo.value!)
)

const estadoDisplay = computed(() => 
  casoInfo.value ? getEstadoDisplay(casoInfo.value) : 'N/A'
)

const patologoActualDisplay = computed(() => 
  casoInfo.value ? getPatologoActual(casoInfo.value) : 'Sin asignar'
)

const validationErrors = computed(() => ({
  patologoId: hasAttemptedSubmit.value && !formData.patologoId 
    ? ['Debe seleccionar un patólogo'] 
    : []
}))

const validationErrorsList = computed(() => {
  return [
    !casoEncontrado.value ? 'Debe buscar y encontrar un caso primero' : null,
    casoInfo.value && isCaseCompleted(casoInfo.value) ? 'No se puede asignar patólogo a un caso completado' : null,
    !formData.patologoId ? 'Debe seleccionar un patólogo' : null
  ].filter(Boolean) as string[]
})

const getButtonText = computed(() => {
  if (!casoInfo.value) return 'Asignar Patólogo'
  if (isCaseCompleted(casoInfo.value)) return 'No se puede asignar'
  const tienePatologo = (casoInfo.value as any)?.assigned_pathologist
  return tienePatologo ? 'Reasignar Patólogo' : 'Asignar Patólogo'
})

// Methods
const handleCodigoChange = (value: string) => {
  value = value.replace(/[^\d-]/g, '').slice(0, 10)
  if (value.length >= 4 && !value.includes('-')) {
    value = value.slice(0, 4) + '-' + value.slice(4)
  }
  const parts = value.split('-')
  if (parts.length > 2) {
    value = parts[0] + '-' + parts.slice(1).join('')
  }
  if (value.includes('-') && value.indexOf('-') !== 4) {
    const digits = value.replace(/-/g, '')
    value = digits.length >= 4 ? digits.slice(0, 4) + '-' + digits.slice(4, 9) : digits
  }
  codigoCaso.value = value
}

const buscarCaso = async () => {
  await buscarCasoComposable(codigoCaso.value)
}

const handleAsignarClick = async () => {
  hasAttemptedSubmit.value = true
  if (!isFormValid.value) {
    showValidationError.value = true
    return
  }
  showValidationError.value = false
  
  isLoadingAssignment.value = true
  try {
    const codigo = (casoInfo.value as any)?.case_code || (casoInfo.value as any)?.caso_code
    if (!codigo) {
      throw new Error('Código del caso no disponible')
    }

    // Usar el composable de pathologist API para la asignación
    const assignmentData = {
      patologoId: formData.patologoId,
      fechaAsignacion: new Date().toISOString().split('T')[0]
    }

    const result = await assignPathologist(codigo, assignmentData)
    
    if (result.success) {
      await handleAsignacionExitosa(result, codigo)
    } else {
      throw new Error(result.message || 'Error al asignar patólogo')
    }
  } catch (error: any) {
    await handleErrorAsignacion(error)
  } finally {
    isLoadingAssignment.value = false
  }
}

const handleAsignacionExitosa = async (result: any, codigoCaso: string) => {
  // Actualizar información local del caso
  if (result.assignment?.pathologist) {
    const p = result.assignment.pathologist as any
    const codigo = p.patologo_code || p.codigo || p.code || p.documento || formData.patologoId
    const nombre = p.patologo_name || p.nombre || p.name || ''
    
    if (casoInfo.value) {
      (casoInfo.value as any).assigned_pathologist = { id: codigo, name: nombre }
    }
  }

  const teniaPrev = (casoInfo.value as any)?.assigned_pathologist && 
                   (casoInfo.value as any).assigned_pathologist.id !== formData.patologoId
  const accion = teniaPrev ? 'reasignado' : 'asignado'
  
  showNotification(
    'success', 
    `¡Patólogo ${accion} exitosamente!`, 
    `El patólogo ha sido ${accion} al caso ${codigoCaso} correctamente.`, 
    0
  )
  
  emit('patologo-asignado', { codigoCaso, patologo: formData.patologoId })
  limpiarFormulario()
}

const handleErrorAsignacion = async (error: any) => {
  showNotification(
    'error', 
    'Error al Asignar Patólogo', 
    error.message || 'No se pudo asignar el patólogo. Por favor, inténtelo nuevamente.', 
    0
  )
}

const limpiarFormulario = () => {
  codigoCaso.value = ''
  formData.patologoId = ''
  formData.fechaAsignacion = ''
  showValidationError.value = false
  hasAttemptedSubmit.value = false
  assignmentPreview.value = null
  limpiarFormularioComposable()
}

// Watch for form validation
watch([() => formData.patologoId, casoEncontrado], () => {
  if (showValidationError.value && isFormValid.value) {
    showValidationError.value = false
  }
})

const normalizePathologistFromCase = (caso: CaseModel | null): AssignmentPreviewInfo | null => {
  if (!caso) return null
  const raw = (caso as any)?.assigned_pathologist || (caso as any)?.patologo_asignado
  if (!raw) return null

  const id = raw.id || raw.codigo || raw.patologo_code || raw.documento || ''
  const name = raw.name || raw.nombre || ''
  if (!id && !name) return null

  return {
    id,
    name: name || 'Patólogo asignado',
    code: raw.patologo_code || raw.codigo || id,
    initials: raw.iniciales,
    document: raw.documento
  }
}

const normalizePathologistFromList = (pathologist: FormPathologistInfo | null): AssignmentPreviewInfo | null => {
  if (!pathologist) return null
  const id = pathologist.patologo_code || pathologist.id || ''
  return {
    id,
    name: pathologist.nombre,
    code: pathologist.patologo_code || pathologist.id,
    initials: pathologist.iniciales,
    document: pathologist.documento
  }
}

const handlePathologistSelected = (pathologist: FormPathologistInfo | null) => {
  assignmentPreview.value = normalizePathologistFromList(pathologist)
  if (pathologist) {
    const id = pathologist.patologo_code || pathologist.id
    if (id) {
      formData.patologoId = id
    }
  }
}

const handlePathologistListLoaded = (pathologists: FormPathologistInfo[]) => {
  if (assignmentPreview.value?.id) return
  const currentCasePathologist = normalizePathologistFromCase(casoInfo.value)
  if (!currentCasePathologist?.id) return

  const match = pathologists.find(p => {
    const code = p.patologo_code || p.id
    return code && code === currentCasePathologist.id
  })
  assignmentPreview.value = match ? normalizePathologistFromList(match) : currentCasePathologist
}

watch(casoInfo, (newCase) => {
  if (!newCase) {
    assignmentPreview.value = null
    formData.patologoId = ''
    return
  }

  const normalized = normalizePathologistFromCase(newCase)
  if (normalized?.id) {
    formData.patologoId = normalized.id
    assignmentPreview.value = normalized
  } else {
    assignmentPreview.value = null
    if (!hasAttemptedSubmit.value) {
      formData.patologoId = ''
    }
  }
}, { immediate: true })

// Auto-scroll when case is found
watch(casoEncontrado, (found) => {
  if (found && assignmentSection.value) {
    nextTick(() => {
      assignmentSection.value?.scrollIntoView({ 
        behavior: 'smooth', 
        block: 'start' 
      })
    })
  }
})

// Emit assignment event for parent usage
const emit = defineEmits<{ 
  'patologo-asignado': [data: { codigoCaso: string; patologo: string }] 
}>()

// Expose methods to parent if needed
defineExpose({ limpiarFormulario, buscarCaso })

</script>

