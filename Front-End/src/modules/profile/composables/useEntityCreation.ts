import { ref, reactive, computed } from 'vue'
import { entityCreateService } from '../services/entityCreateService'
import type { 
  EntityFormModel, 
  EntityCreateRequest, 
  EntityCreationState,
  EntityFormValidation 
} from '../types/entity.types'

const CODE_REGEX = /^[A-Z0-9_-]+$/i

export function useEntityCreation() {
  // Reactive state
  const state = reactive<EntityCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  const isCheckingCode = ref(false)
  const codeValidationError = ref('')

  // Computed properties
  const canSubmit = computed(() => true)

  // Form validation
  const validateForm = (formData: EntityFormModel): EntityFormValidation => {
    const errors: EntityFormValidation['errors'] = {}

    if (!formData.entityName?.trim()) {
      errors.entityName = 'Name is required'
    } else if (formData.entityName.length > 200) {
      errors.entityName = 'Maximum 200 characters'
    }

    if (!formData.entityCode?.trim()) {
      errors.entityCode = 'Code is required'
    } else if (formData.entityCode.length > 20) {
      errors.entityCode = 'Maximum 20 characters'
    } else if (!CODE_REGEX.test(formData.entityCode)) {
      errors.entityCode = 'Only letters, numbers, hyphens and underscores'
    }

    if (formData.notes && formData.notes.length > 500) {
      errors.notes = 'Maximum 500 characters'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  // Code availability check
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    if (!code?.trim()) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await entityCreateService.checkCodeExists(code.trim())
      if (exists) {
        codeValidationError.value = 'This code is already in use'
        return false
      }
      return true
    } catch (error: any) {
      codeValidationError.value = 'Error checking code availability'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  // Data normalization for backend compatibility
  const normalizeEntityData = (formData: EntityFormModel): EntityCreateRequest => {
    return {
      name: formData.entityName?.trim() || '',
      entity_code: formData.entityCode?.trim().toUpperCase() || '',
      notes: formData.notes?.trim() || '',
      is_active: formData.isActive ?? true
    }
  }

  // Entity creation
  const createEntity = async (formData: EntityFormModel): Promise<{ success: boolean; data?: any }> => {
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }

    state.isLoading = true

    try {
      const requestData = normalizeEntityData(formData)
      const response = await entityCreateService.createEntity(requestData)

      state.isSuccess = true
      state.successMessage = `Entity "${response.name}" (${response.entity_code}) created successfully as ${response.is_active ? 'ACTIVE' : 'INACTIVE'}`

      return { 
        success: true, 
        data: response 
      }

    } catch (error: any) {
      let errorMessage = 'Error creating entity'
      
      if (error.message) {
        errorMessage = error.message
      } else if (error.response?.data?.detail) {
        errorMessage = error.response.data.detail
      } else if (error.response?.status) {
        const errorMap: Record<number, string> = {
          409: 'An entity with the provided data already exists',
          422: 'The provided data is not valid',
          400: 'Incorrect or incomplete data',
          500: 'Internal server error. Please try later'
        }
        errorMessage = errorMap[error.response.status] || `Server error (${error.response.status})`
      }
      
      state.error = errorMessage
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  // State management
  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    codeValidationError.value = ''
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
    codeValidationError: readonly(codeValidationError),
    canSubmit,
    validateForm,
    checkCodeAvailability,
    createEntity,
    clearState,
    clearMessages
  }
}

// Helper for readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
