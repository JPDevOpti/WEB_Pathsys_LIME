<template>
  <form @submit.prevent="submit" class="grid grid-cols-1 md:grid-cols-12 gap-3 md:gap-4">
    <div class="col-span-full">
      <h4 class="text-base font-semibold text-gray-800">Edit Entity</h4>
      <p class="text-sm text-gray-600 mt-1">Modify entity data</p>
    </div>

    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Entity Code" 
      v-model="localModel.entityCode" 
      :error="formErrors.entityCode" 
      @blur="validateCode" 
      :disabled="true" 
    />
    <FormInputField 
      class="col-span-full md:col-span-6" 
      label="Entity Name" 
      v-model="localModel.entityName" 
      :error="formErrors.entityName" 
    />

    <FormTextarea 
      class="col-span-full" 
      label="Observations" 
      v-model="localModel.notes" 
      :rows="3" 
      :error="formErrors.notes" 
    />

    <div class="col-span-full md:col-span-6 flex items-center pt-3">
      <FormCheckbox label="Active" v-model="localModel.isActive" />
    </div>

    <div class="col-span-full flex flex-col sm:flex-row gap-2 sm:gap-3 sm:justify-end pt-4 border-t border-gray-200">
      <ClearButton 
        type="button" 
        @click="onReset" 
        :disabled="isLoading || !hasChanges" 
        variant="secondary" 
        :text="'Reset'" 
        :icon="'reset'"
      >
        <template #icon>
          <RefreshIcon class="w-4 h-4 mr-2" />
        </template>
      </ClearButton>
      <SaveButton 
        text="Update Entity" 
        type="submit" 
        :disabled="!canSubmit || isLoading || !hasChanges" 
        :loading="isLoading" 
      />
    </div>

    <div v-if="notification.visible" ref="notificationContainer" class="col-span-full">
      <Notification
        :visible="true"
        :type="notification.type"
        :title="notification.title"
        :message="notification.message"
        :inline="true"
        :auto-close="false"
        @close="() => {}"
      >
        <template v-if="notification.type === 'success' && updatedEntity" #content>
          <div class="p-6 bg-white border border-gray-200 rounded-lg shadow-sm">
            <div class="space-y-4">
              <div class="mb-4 pb-3 border-b border-gray-100">
                <h3 class="text-xl font-bold text-gray-900 mb-2">{{ updatedEntity.name }}</h3>
                <p class="text-gray-600">
                  <span class="font-medium">Code:</span>
                  <span class="font-mono font-bold text-gray-800 ml-1">{{ updatedEntity.entity_code }}</span>
                </p>
              </div>

              <div class="space-y-4 text-sm">
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Status:</span>
                  <span class="inline-flex px-2 py-1 text-xs font-semibold rounded-full"
                    :class="updatedEntity.is_active ? 'bg-green-100 text-green-800' : 'bg-red-100 text-red-800'">
                    {{ updatedEntity.is_active ? 'Active' : 'Inactive' }}
                  </span>
                </div>
                <div>
                  <span class="text-gray-500 font-medium block mb-1">Last Update:</span>
                  <p class="text-gray-800 font-semibold">{{ formatDate(updatedEntity.updated_at) }}</p>
                </div>
              </div>

              <div v-if="updatedEntity.notes">
                <span class="text-gray-500 font-medium block mb-2">Observations:</span>
                <p class="text-gray-800 bg-gray-50 p-3 rounded-lg">{{ updatedEntity.notes }}</p>
              </div>
            </div>
          </div>
        </template>
      </Notification>
    </div>

    <ValidationAlert 
      :visible="validationState.showValidationError && validationState.hasAttemptedSubmit" 
      :errors="validationErrors" 
    />
  </form>
</template>

<script setup lang="ts">
import { reactive, computed, watch, ref, nextTick } from 'vue'
import { FormInputField, FormCheckbox, FormTextarea } from '@/shared/components/forms'
import { SaveButton, ClearButton } from '@/shared/components/buttons'
import { Notification, ValidationAlert } from '@/shared/components/feedback'
import { useEntityEdition } from '../../composables/useEntityEdition'
import type { EntityEditFormModel, EntityUpdateResponse } from '../../types/entity.types'
import { RefreshIcon } from '@/assets/icons'

// Props and emits
const props = defineProps<{ usuario: any; usuarioActualizado: boolean; mensajeExito: string }>()
const emit = defineEmits<{ (e: 'usuario-actualizado', payload: any): void; (e: 'cancelar'): void }>()

// Composable for backend operations
const {
  state,
  codeValidationError,
  originalEntityData,
  canSubmit,
  validateForm,
  checkCodeAvailability,
  updateEntity,
  setInitialData,
  resetToOriginal,
  clearState,
  hasChangesFactory
} = useEntityEdition()

// Refs and reactive state
const isLoading = computed(() => state.isLoading)
const notificationContainer = ref<HTMLElement | null>(null)
const updatedEntity = ref<EntityUpdateResponse | null>(null)

const notification = reactive({
  visible: false,
  type: 'success' as 'success' | 'error' | 'warning' | 'info',
  title: '',
  message: ''
})

const localModel = reactive<EntityEditFormModel>({
  id: '',
  entityName: '',
  entityCode: '',
  notes: '',
  isActive: true
})

const formErrors = reactive({
  entityName: '',
  entityCode: '',
  notes: ''
})

const validationState = reactive({ 
  showValidationError: false, 
  hasAttemptedSubmit: false 
})

// Computed properties
const validationErrors = computed(() => {
  if (!validationState.hasAttemptedSubmit) return []
  const errors: string[] = []
  if (!localModel.entityName || formErrors.entityName) errors.push('Valid name required')
  if (!localModel.entityCode || formErrors.entityCode) errors.push('Valid code required')
  if (formErrors.notes) errors.push('Valid observations required')
  return errors
})

const hasChanges = computed(() => hasChangesFactory(localModel))

// Helper functions
const showNotification = (type: typeof notification.type, title: string, message: string) => {
  notification.type = type
  notification.title = title
  notification.message = message
  notification.visible = true
}

const scrollToNotification = async () => {
  await nextTick()
  if (notificationContainer.value) {
    notificationContainer.value.scrollIntoView({ behavior: 'smooth', block: 'center' })
  }
}

const formatDate = (dateString: string): string => {
  try {
    return new Date(dateString).toLocaleDateString('es-ES', {
      year: 'numeric', month: 'long', day: 'numeric', hour: '2-digit', minute: '2-digit'
    })
  } catch { return 'Date not available' }
}

const clearFormErrors = () => Object.keys(formErrors).forEach(k => (formErrors as any)[k] = '')

// Validation functions
const validateCode = async () => {
  formErrors.entityCode = ''
  if (!localModel.entityCode?.trim()) { formErrors.entityCode = 'Code is required'; return }
  if (localModel.entityCode.length > 20) { formErrors.entityCode = 'Maximum 20 characters'; return }
  if (!/^[A-Z0-9_-]+$/i.test(localModel.entityCode)) { formErrors.entityCode = 'Only letters, numbers, hyphens and underscores'; return }
  const originalCode = originalEntityData.value?.entityCode
  await checkCodeAvailability(localModel.entityCode, originalCode)
  if (codeValidationError.value) formErrors.entityCode = codeValidationError.value
}

// Form submission
const submit = async () => {
  validationState.hasAttemptedSubmit = true
  clearFormErrors()
  const validation = validateForm(localModel)
  if (!validation.isValid) { 
    Object.assign(formErrors, validation.errors)
    validationState.showValidationError = true
    return 
  }
  validationState.showValidationError = false
  try {
    const result = await updateEntity(localModel)
    if (result.success && result.data) {
      updatedEntity.value = result.data as EntityUpdateResponse
      showNotification('success', 'Entity Updated Successfully!', '')
      await scrollToNotification()
      emit('usuario-actualizado', { 
        ...result.data, 
        nombre: result.data.name, 
        codigo: result.data.entity_code, 
        tipo: 'entidad' 
      })
    } else {
      showNotification('error', 'Error Updating Entity', 'Could not update entity')
    }
  } catch (error: any) {
    showNotification('error', 'Error Updating Entity', error.message || 'Unexpected error')
  }
}

// Form reset functions
const onReset = () => {
  const original = resetToOriginal()
  if (original) { 
    Object.assign(localModel, original)
    clearFormErrors()
    validationState.hasAttemptedSubmit = false
    validationState.showValidationError = false 
  }
}

// Data normalization for backend compatibility
const normalizeEntity = (raw: any): EntityEditFormModel | null => {
  if (!raw) return null
  const entityName = raw.EntidadName || raw.entidadName || raw.nombre || raw.name || ''
  const entityCode = raw.EntidadCode || raw.entidadCode || raw.codigo || raw.code || ''
  const notes = raw.observaciones || raw.observations || raw.notes || ''
  const isActive = raw.isActive !== undefined ? raw.isActive :
    raw.is_active !== undefined ? raw.is_active :
    raw.activo !== undefined ? raw.activo : true
  const id = raw.id || raw._id || entityCode
  return {
    id: id,
    entityName: String(entityName),
    entityCode: String(entityCode),
    notes: String(notes),
    isActive: !!isActive
  }
}

// Watchers
watch(
  () => props.usuario,
  (u) => {
    const mapped = normalizeEntity(u)
    if (mapped) {
      Object.assign(localModel, mapped)
      setInitialData(mapped)
    } else {
      clearState()
    }
  },
  { immediate: true, deep: true }
)
</script>


