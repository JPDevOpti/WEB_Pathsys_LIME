import { reactive, ref, computed } from 'vue'
import { entityEditService } from '../services/entityEditService'
import type {
  EntityEditFormModel,
  EntityEditionState,
  EntityEditFormValidation
} from '../types/entity.types'

export function useEntityEdition() {
  const state = reactive<EntityEditionState>({ isLoading: false, isSuccess: false, error: '', successMessage: '' })
  const isCheckingCode = ref(false)
  const isLoadingEntity = ref(false)
  const codeValidationError = ref('')
  const originalEntityData = ref<EntityEditFormModel | null>(null)

  const canSubmit = computed(() => !state.isLoading && !isCheckingCode.value && !isLoadingEntity.value)

  const validateForm = (formData: EntityEditFormModel): EntityEditFormValidation => {
    const errors: EntityEditFormValidation['errors'] = {}
    if (!formData.EntidadName?.trim()) errors.EntidadName = 'El nombre es requerido'
    if (!formData.EntidadCode?.trim()) errors.EntidadCode = 'El código es requerido'
    if (formData.observaciones && formData.observaciones.length > 500) errors.observaciones = 'Máximo 500 caracteres'
    return { isValid: Object.keys(errors).length === 0, errors }
  }

  const loadEntityForEdition = async (code: string) => {
    isLoadingEntity.value = true
    state.error = ''
    try {
      const data = await entityEditService.getByCode(code)
      originalEntityData.value = { ...data }
      return { success: true, data }
    } catch (e: any) {
      state.error = e.message || 'Error al cargar la entidad'
      return { success: false }
    } finally {
      isLoadingEntity.value = false
    }
  }

  const checkCodeAvailability = async (code: string, originalCode?: string) => {
    if (!code?.trim()) return true
    isCheckingCode.value = true
    codeValidationError.value = ''
    try {
      const exists = await entityEditService.checkCodeExists(code.trim(), originalCode)
      if (exists) {
        codeValidationError.value = 'Este código ya está en uso'
        return false
      }
      return true
    } catch {
      codeValidationError.value = 'Error al verificar el código'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  const hasChangesFactory = (current: EntityEditFormModel) => {
    if (!originalEntityData.value) return false
    return (
      originalEntityData.value.EntidadName !== current.EntidadName ||
      originalEntityData.value.EntidadCode !== current.EntidadCode ||
      originalEntityData.value.observaciones !== current.observaciones ||
      originalEntityData.value.isActive !== current.isActive
    )
  }

  /**
   * Normalizar datos del formulario para que sean compatibles con el backend (snake_case)
   */
  const normalizeEntityData = (formData: EntityEditFormModel) => {
    return {
      entidad_name: formData.EntidadName?.trim() || '',
      entidad_code: formData.EntidadCode?.trim().toUpperCase() || '',
      observaciones: formData.observaciones?.trim() || '',
      is_active: formData.isActive ?? true
    }
  }

  const updateEntity = async (formData: EntityEditFormModel) => {
    if (!originalEntityData.value) {
      state.error = 'No se han cargado los datos originales'
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

    if (formData.EntidadCode !== originalEntityData.value.EntidadCode) {
      const available = await checkCodeAvailability(formData.EntidadCode, originalEntityData.value.EntidadCode)
      if (!available) {
        state.error = codeValidationError.value || 'Código no disponible'
        return { success: false }
      }
    }

    state.isLoading = true
    try {
      // Preparar datos para actualización normalizados al formato del backend
      const updateData = normalizeEntityData(formData)
      
      // Enviar al backend usando el código original
      const response = await entityEditService.updateByCode(originalEntityData.value.EntidadCode, updateData)
      
      originalEntityData.value = {
        id: response.id,
        EntidadName: response.entidad_name,
        EntidadCode: response.entidad_code,
        observaciones: response.observaciones,
        isActive: response.is_active
      }
      state.isSuccess = true
      state.successMessage = `Entidad "${response.entidad_name}" actualizada exitosamente`
      return { success: true, data: response }
    } catch (e: any) {
      state.error = e.message || 'Error al actualizar la entidad'
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  const setInitialData = (data: EntityEditFormModel) => { originalEntityData.value = { ...data } }
  const resetToOriginal = (): EntityEditFormModel | null => originalEntityData.value ? { ...originalEntityData.value } : null
  const clearState = () => { state.isLoading = false; state.isSuccess = false; state.error = ''; state.successMessage=''; isCheckingCode.value=false; isLoadingEntity.value=false; codeValidationError.value=''; originalEntityData.value=null }
  const clearMessages = () => { state.error=''; state.successMessage=''; state.isSuccess=false; codeValidationError.value='' }

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

function readonly<T>(ref: import('vue').Ref<T>) { return computed(() => ref.value) }


