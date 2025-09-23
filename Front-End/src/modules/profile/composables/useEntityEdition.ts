import { reactive, ref, computed } from 'vue'
import { entityEditService } from '../services/entityEditService'
import type {
  EntityEditFormModel,
  EntityEditionState,
  EntityEditFormValidation
} from '../types/entity.types'

export function useEntityEdition() {
  // Reactive state
  const state = reactive<EntityEditionState>({ 
    isLoading: false, 
    isSuccess: false, 
    error: '', 
    successMessage: '' 
  })
  
  const isCheckingCode = ref(false)
  const isLoadingEntity = ref(false)
  const codeValidationError = ref('')
  const originalEntityData = ref<EntityEditFormModel | null>(null)

  // Computed properties
  const canSubmit = computed(() => !state.isLoading && !isCheckingCode.value && !isLoadingEntity.value)

  // Form validation
  const validateForm = (formData: EntityEditFormModel): EntityEditFormValidation => {
    const errors: EntityEditFormValidation['errors'] = {}
    if (!formData.entityName?.trim()) errors.entityName = 'Name is required'
    if (!formData.entityCode?.trim()) errors.entityCode = 'Code is required'
    if (formData.notes && formData.notes.length > 500) errors.notes = 'Maximum 500 characters'
    return { isValid: Object.keys(errors).length === 0, errors }
  }

  // Load entity for editing
  const loadEntityForEdition = async (code: string) => {
    isLoadingEntity.value = true
    state.error = ''
    try {
      const data = await entityEditService.getByCode(code)
      originalEntityData.value = { ...data }
      return { success: true, data }
    } catch (e: any) {
      state.error = e.message || 'Error loading entity'
      return { success: false }
    } finally {
      isLoadingEntity.value = false
    }
  }

  // Code availability check
  const checkCodeAvailability = async (code: string, originalCode?: string) => {
    if (!code?.trim()) return true
    isCheckingCode.value = true
    codeValidationError.value = ''
    try {
      const exists = await entityEditService.checkCodeExists(code.trim(), originalCode)
      if (exists) {
        codeValidationError.value = 'This code is already in use'
        return false
      }
      return true
    } catch {
      codeValidationError.value = 'Error checking code availability'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  // Check for changes
  const hasChangesFactory = (current: EntityEditFormModel) => {
    if (!originalEntityData.value) return false
    return (
      originalEntityData.value.entityName !== current.entityName ||
      originalEntityData.value.entityCode !== current.entityCode ||
      originalEntityData.value.notes !== current.notes ||
      originalEntityData.value.isActive !== current.isActive
    )
  }

  // Data normalization for backend compatibility
  const normalizeEntityData = (formData: EntityEditFormModel) => {
    return {
      name: formData.entityName?.trim() || '',
      entity_code: formData.entityCode?.trim().toUpperCase() || '',
      notes: formData.notes?.trim() || '',
      is_active: formData.isActive ?? true
    }
  }

  // Entity update
  const updateEntity = async (formData: EntityEditFormModel) => {
    if (!originalEntityData.value) {
      state.error = 'Original data not loaded'
      return { success: false }
    }
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      state.error = Object.values(validation.errors).filter(Boolean).join(', ')
      return { success: false }
    }

    if (formData.entityCode !== originalEntityData.value.entityCode) {
      const available = await checkCodeAvailability(formData.entityCode, originalEntityData.value.entityCode)
      if (!available) {
        state.error = codeValidationError.value || 'Code not available'
        return { success: false }
      }
    }

    state.isLoading = true
    try {
      const updateData = normalizeEntityData(formData)
      const response = await entityEditService.updateByCode(originalEntityData.value.entityCode, updateData)
      
      // Update original data with response
      originalEntityData.value = {
        id: response.id,
        entityName: response.name,
        entityCode: response.entity_code,
        notes: response.notes,
        isActive: response.is_active
      }
      
      state.isSuccess = true
      state.successMessage = `Entity "${response.name}" updated successfully`
      return { success: true, data: response }
    } catch (e: any) {
      state.error = e.message || 'Error updating entity'
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  // State management
  const setInitialData = (data: EntityEditFormModel) => { 
    originalEntityData.value = { ...data } 
  }
  
  const resetToOriginal = (): EntityEditFormModel | null => 
    originalEntityData.value ? { ...originalEntityData.value } : null
  
  const clearState = () => { 
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    isLoadingEntity.value = false
    codeValidationError.value = ''
    originalEntityData.value = null
  }
  
  const clearMessages = () => { 
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
  }

  return {
    state,
    isCheckingCode: readonly(isCheckingCode),
    isLoadingEntity: readonly(isLoadingEntity),
    codeValidationError: readonly(codeValidationError),
    originalEntityData: readonly(originalEntityData),
    canSubmit,
    validateForm,
    loadEntityForEdition,
    checkCodeAvailability,
    updateEntity,
    setInitialData,
    resetToOriginal,
    clearState,
    clearMessages,
    hasChangesFactory
  }
}

// Helper for readonly refs
function readonly<T>(ref: import('vue').Ref<T>) { 
  return computed(() => ref.value) 
}


