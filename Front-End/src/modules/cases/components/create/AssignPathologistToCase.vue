<template>
  <!-- Assign a pathologist to an existing case -->
  <ComponentCard 
    title="Asignación de patólogo a un caso"
    description="Busque un caso y asigne un patólogo responsable para el análisis."
  >
    <template #icon>
      <DoctorIcon class="w-5 h-5 mr-2 text-blue-600" />
    </template>

    <div class="space-y-6">
      <!-- Case search section -->
      <div class="bg-gray-50 rounded-lg p-3 sm:p-4 lg:p-6 border border-gray-200">
        <h3 class="text-sm font-semibold text-gray-700 mb-3 flex items-center">
          <svg class="w-4 h-4 mr-2 text-gray-500" fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"/>
          </svg>
          Buscar Caso
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

        <!-- Found case summary -->
        <div v-if="casoEncontrado && casoInfo" class="mt-4 p-4 bg-green-50 border border-green-200 rounded-lg">
          <div class="flex items-center mb-3">
            <svg class="w-5 h-5 text-green-600 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"/>
            </svg>
            <h4 class="text-sm font-semibold text-green-800">Caso Encontrado</h4>
          </div>
          
          <!-- Key case fields -->
          <div class="grid grid-cols-1 sm:grid-cols-2 lg:grid-cols-3 gap-3 text-sm">
            <div><span class="font-medium text-green-700">Código:</span><p class="text-green-800 font-mono">{{ casoInfo.case_code || (casoInfo as any).caso_code || 'N/A' }}</p></div>
            <div><span class="font-medium text-green-700">Estado:</span><p class="text-green-800">{{ estadoDisplay }}</p></div>
            <div><span class="font-medium text-green-700">Paciente:</span><p class="text-green-800 break-words">{{ casoInfo.patient_info?.name || 'N/A' }}</p></div>
            <div><span class="font-medium text-green-700">Documento:</span><p class="text-green-800 font-mono">{{ casoInfo.patient_info?.patient_code || 'N/A' }}</p></div>
            <div><span class="font-medium text-green-700">Entidad:</span><p class="text-green-800 break-words">{{ ((casoInfo as any).patient_info?.entity_info?.name) || ((casoInfo as any).patient_info?.entity_info?.nombre) || 'N/A' }}</p></div>
            <div><span class="font-medium text-green-700">Patólogo Actual:</span><p class="text-green-800 break-words">{{ patologoActualDisplay }}</p></div>
          </div>
          
          <!-- Samples -->
          <div v-if="casoInfo.samples?.length > 0" class="mt-3">
            <span class="font-medium text-green-700 text-sm">Muestras:</span>
            <div class="flex flex-wrap gap-2 mt-1">
              <span v-for="muestra in casoInfo.samples" :key="muestra.body_region || muestra.region_cuerpo" class="inline-flex items-center px-2 py-1 bg-green-100 text-green-800 text-xs font-medium rounded-md">
                {{ muestra.body_region || muestra.region_cuerpo || 'Muestra' }}
              </span>
            </div>
          </div>
        </div>
      </div>

      <!-- Assignment form -->
      <div v-if="casoEncontrado && !isCaseCompleted" class="space-y-6">
        <div class="bg-white border border-gray-200 rounded-lg p-3 sm:p-4 lg:p-6">
          <div class="max-w-md">
            <PathologistList v-model="formData.patologoId" label="Patólogo Asignado" placeholder="Buscar y seleccionar patólogo..." :required="true" :errors="validationErrors.patologoId" help-text="Seleccione el patólogo asignado a este caso" />
          </div>
        </div>

        <!-- Form actions -->
        <div class="flex flex-col sm:flex-row justify-end gap-3 pt-4 border-t border-gray-200">
          <ClearButton @click="limpiarFormulario" />
          <SaveButton :text="getButtonText" loading-text="Asignando..." :loading="isLoadingAssignment" @click="handleAsignarClick" :disabled="!isFormValid" />
        </div>

        <!-- Validation alert -->
        <ValidationAlert :visible="showValidationError" :errors="validationErrorsList" />
      </div>

      <!-- Inline notification container -->
      <div>
        <Notification :visible="notification.visible" :type="notification.type" :title="notification.title" :message="notification.message" :inline="true" :auto-close="false" @close="closeNotification" />
      </div>
    </div>
  </ComponentCard>
</template>

<script setup lang="ts">
import { computed, ref, reactive, watch } from 'vue'
import { usePathologistAPI } from '../../composables/usePathologistAPI'
import { useNotifications } from '../../composables/useNotifications'
import casesApiService from '../../services/casesApi.service'
import type { PathologistFormData, CaseModel } from '../../types'
import { ComponentCard } from '@/shared/components'
import { FormInputField } from '@/shared/components/forms'
import { PathologistList } from '@/shared/components/List'
import { SearchButton, SaveButton, ClearButton } from '@/shared/components/buttons'
import { ValidationAlert, Notification } from '@/shared/components/feedback'
import { DoctorIcon } from '@/assets/icons'

// UI state
const codigoCaso = ref('')
const isLoadingSearch = ref(false)
const casoEncontrado = ref(false)
const searchError = ref('')

// Case data
const casoInfo = ref<CaseModel | null>(null)

// Form state
const formData = reactive<PathologistFormData>({ patologoId: '', fechaAsignacion: '' })
const hasAttemptedSubmit = ref(false)
const showValidationError = ref(false)
const isLoadingAssignment = ref(false)

// APIs
const { assignPathologist, unassignPathologist } = usePathologistAPI()
const { notification, showNotification, closeNotification } = useNotifications()

// Allow submit only when case found, not completed, and pathologist selected
const isFormValid = computed(() => casoEncontrado.value && formData.patologoId.trim() !== '' && !isCaseCompleted.value)

// Completed when backend state matches "completed"
const isCaseCompleted = computed(() => {
  const info: any = casoInfo.value as any
  if (!info?.state && !info?.estado) return false
  const estado: string = info.state || info.estado || ''
  return estado.toLowerCase() === 'completado' || estado.toLowerCase() === 'completed'
})

// Localized status label
const estadoDisplay = computed(() => {
  const raw = String((casoInfo.value as any)?.state || (casoInfo.value as any)?.estado || '').toLowerCase()
  const map: Record<string, string> = { 'in process': 'En proceso', in_process: 'En proceso', processing: 'En proceso', pending: 'Pendiente', completed: 'Completado', finished: 'Completado', cancelled: 'Cancelado', canceled: 'Cancelado' }
  if (!raw) return 'N/A'
  return map[raw] || (casoInfo.value as any)?.estado || 'En proceso'
})

// Current pathologist name or fallback
const patologoActualDisplay = computed(() => (casoInfo.value as any)?.assigned_pathologist?.name || (casoInfo.value as any)?.patologo_asignado?.nombre || 'Sin asignar')

// Field-level validation errors
const validationErrors = computed(() => ({ patologoId: hasAttemptedSubmit.value && !formData.patologoId ? ['Debe seleccionar un patólogo'] : [] }))

// Aggregate validation errors for alert
const validationErrorsList = computed(() => {
  return [
    !casoEncontrado.value ? 'Debe buscar y encontrar un caso primero' : null,
    isCaseCompleted.value ? 'No se puede asignar patólogo a un caso completado' : null,
    !formData.patologoId ? 'Debe seleccionar un patólogo' : null
  ].filter(Boolean) as string[]
})

// Primary action button label
const getButtonText = computed(() => (isCaseCompleted.value ? 'No se puede asignar' : (casoInfo.value as any)?.assigned_pathologist ? 'Reasignar Patólogo' : 'Asignar Patólogo'))

// Strict code format: YYYY-NNNNN
const isValidCodigoFormat = (codigo: string | undefined | null): boolean => {
  if (!codigo || typeof codigo !== 'string' || codigo.trim() === '') return false
  return /^\d{4}-\d{5}$/.test(codigo.trim())
}

// Normalize and auto-format code input
const handleCodigoChange = (value: string) => {
  value = value.replace(/[^\d-]/g, '').slice(0, 10)
  if (value.length >= 4 && !value.includes('-')) value = value.slice(0, 4) + '-' + value.slice(4)
  const parts = value.split('-')
  if (parts.length > 2) value = parts[0] + '-' + parts.slice(1).join('')
  if (value.includes('-') && value.indexOf('-') !== 4) {
    const digits = value.replace(/-/g, '')
    value = digits.length >= 4 ? digits.slice(0, 4) + '-' + digits.slice(4, 9) : digits
  }
  codigoCaso.value = value
}

// Fetch case by code; set UI states and errors
const buscarCaso = async () => {
  if (!codigoCaso.value.trim()) { searchError.value = 'Por favor, ingrese un código de caso'; return }
  if (!isValidCodigoFormat(codigoCaso.value)) { searchError.value = 'El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)'; return }
  isLoadingSearch.value = true; searchError.value = ''; casoEncontrado.value = false
  try {
    const casoResponse = await casesApiService.getCaseByCode(codigoCaso.value.trim())
    casoEncontrado.value = true
    casoInfo.value = casoResponse
  } catch (error: any) {
    casoEncontrado.value = false; casoInfo.value = null
    const m = error?.message || ''
    searchError.value = m.includes('404') || m.includes('no encontrado') ? `No existe un caso con el código "${codigoCaso.value}"` : m.includes('400') ? 'Formato de código de caso inválido' : m.includes('500') ? 'Error interno del servidor. Inténtelo más tarde.' : 'Error al buscar el caso. Inténtelo nuevamente.'
  } finally {
    isLoadingSearch.value = false
  }
}

// Assign or reassign pathologist; enforce completion rule
const asignarPatologo = async () => {
  if (!isFormValid.value || !casoInfo.value) return
  if (isCaseCompleted.value) { showNotification('error', 'Caso completado', 'No se puede asignar patólogo a un caso que ya ha sido completado.', 0); return }
  isLoadingAssignment.value = true
  try {
    const codigo = (casoInfo.value as any).case_code || (casoInfo.value as any).caso_code
    if (!codigo) throw new Error(`Código del caso no disponible. Estructura: ${JSON.stringify(casoInfo.value)}`)
    const tienePatologo = (casoInfo.value as any)?.assigned_pathologist?.id
    if (tienePatologo) { try { await unassignPathologist(codigo) } catch (e: any) { console.warn('Error al desasignar patólogo anterior:', e.message) } }
    const result = await assignPathologist(codigo, { patologoId: formData.patologoId, fechaAsignacion: new Date().toISOString().split('T')[0] })
    if (result.success) { await handleAsignacionExitosa(result) } else { throw new Error(result.message || 'Error al asignar patólogo') }
  } catch (error: any) {
    await handleErrorAsignacion(error)
  } finally {
    isLoadingAssignment.value = false
  }
}

// Success: update local case, notify, emit, and reset
const handleAsignacionExitosa = async (result: any) => {
  if (result.assignment?.pathologist) {
    const p = result.assignment.pathologist as any
    const codigo = p.patologo_code || p.codigo || p.code || p.documento || formData.patologoId
    const nombre = p.patologo_name || p.nombre || p.name || ''
    const ci: any = casoInfo.value; if (!ci) return
    ci.assigned_pathologist = { id: codigo, name: nombre }
  }
  const codigoCaso = (casoInfo.value as any)?.case_code || (casoInfo.value as any)?.caso_code
  const teniaPrev = (casoInfo.value as any)?.assigned_pathologist && (casoInfo.value as any).assigned_pathologist.id !== formData.patologoId
  const accion = teniaPrev ? 'reasignado' : 'asignado'
  showNotification('success', `¡Patólogo ${accion} exitosamente!`, `El patólogo ha sido ${accion} al caso ${codigoCaso} correctamente.`, 0)
  emit('patologo-asignado', { codigoCaso, patologo: formData.patologoId })
  limpiarFormulario()
}

// Error: surface message to user
const handleErrorAsignacion = async (error: any) => {
  showNotification('error', 'Error al Asignar Patólogo', error.message || 'No se pudo asignar el patólogo. Por favor, inténtelo nuevamente.', 0)
}

// Reset component UI state
const limpiarFormulario = () => {
  codigoCaso.value = ''
  casoEncontrado.value = false
  searchError.value = ''
  casoInfo.value = null
  formData.patologoId = ''
  formData.fechaAsignacion = ''
  showValidationError.value = false
  hasAttemptedSubmit.value = false
}

// Validate and trigger assignment
const handleAsignarClick = () => {
  hasAttemptedSubmit.value = true
  if (!isFormValid.value) { showValidationError.value = true; return }
  showValidationError.value = false
  asignarPatologo()
}

// Hide validation alert as soon as the form becomes valid
watch([() => formData.patologoId, casoEncontrado], () => { if (showValidationError.value && isFormValid.value) showValidationError.value = false })

// Emit assignment event for parent usage
const emit = defineEmits<{ 'patologo-asignado': [data: { codigoCaso: string; patologo: string }] }>()

// Expose search and reset to parent if needed
defineExpose({ limpiarFormulario, buscarCaso })
</script>


