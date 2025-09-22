import { ref, reactive, computed } from 'vue'
import { entityCreateService } from '../services/entityCreateService'
import type { 
  EntityFormModel, 
  EntityCreateRequest, 
  EntityCreationState,
  EntityFormValidation 
} from '../types/entity.types'

/**
 * Composable para manejar la creación de entidades
 */
export function useEntityCreation() {
  // Estado reactivo
  const state = reactive<EntityCreationState>({
    isLoading: false,
    isSuccess: false,
    error: '',
    successMessage: ''
  })

  // Estados adicionales
  const isCheckingCode = ref(false)
  const codeValidationError = ref('')

  /**
   * Estado computed para verificar si se puede enviar el formulario
   */
  const canSubmit = computed(() => {
    // ✅ SIEMPRE HABILITADO: El botón de guardar nunca se bloquea
    return true
  })

  /**
   * Validar formulario en el cliente
   */
  const validateForm = (formData: EntityFormModel): EntityFormValidation => {
    const errors: EntityFormValidation['errors'] = {}

    // Validar nombre
    if (!formData.entityName?.trim()) {
      errors.entityName = 'El nombre es requerido'
    } else if (formData.entityName.length > 200) {
      errors.entityName = 'El nombre no puede tener más de 200 caracteres'
    }

    // Validar código
    if (!formData.entityCode?.trim()) {
      errors.entityCode = 'El código es requerido'
    } else if (formData.entityCode.length > 20) {
      errors.entityCode = 'El código no puede tener más de 20 caracteres'
    } else if (!/^[A-Z0-9_-]+$/i.test(formData.entityCode)) {
      errors.entityCode = 'Solo letras, números, guiones y guiones bajos'
    }

    // Validar observaciones (opcional)
    if (formData.notes && formData.notes.length > 500) {
      errors.notes = 'Máximo 500 caracteres'
    }

    return {
      isValid: Object.keys(errors).length === 0,
      errors
    }
  }

  /**
   * Verificar si un código ya existe
   */
  const checkCodeAvailability = async (code: string): Promise<boolean> => {
    if (!code?.trim()) return true

    isCheckingCode.value = true
    codeValidationError.value = ''

    try {
      const exists = await entityCreateService.checkCodeExists(code.trim())
      if (exists) {
        codeValidationError.value = 'Este código ya está en uso'
        return false
      }
      return true
    } catch (error: any) {
      codeValidationError.value = 'Error al verificar el código'
      return false
    } finally {
      isCheckingCode.value = false
    }
  }

  /**
   * Normalizar datos del formulario para que sean compatibles con el backend (snake_case)
   */
  const normalizeEntityData = (formData: EntityFormModel): EntityCreateRequest => {
    return {
      name: formData.entityName?.trim() || '',
      entity_code: formData.entityCode?.trim().toUpperCase() || '',
      notes: formData.notes?.trim() || '',
      is_active: formData.isActive ?? true
    }
  }

  /**
   * Crear una nueva entidad
   */
  const createEntity = async (formData: EntityFormModel): Promise<{ success: boolean; data?: any }> => {
    // Limpiar estados previos
    state.error = ''
    state.isSuccess = false
    state.successMessage = ''

    // Validar formulario
    const validation = validateForm(formData)
    if (!validation.isValid) {
      const errorMessages = Object.values(validation.errors).filter(Boolean)
      state.error = errorMessages.join(', ')
      return { success: false }
    }

    // ✅ REMOVIDO: Verificación de disponibilidad de datos únicos
    // Ahora permitimos que el usuario envíe el formulario y vea el error específico del backend

    state.isLoading = true

    try {
      // Preparar datos para envío normalizados al formato del backend
      const requestData = normalizeEntityData(formData)

      // Enviar al backend
      const response = await entityCreateService.createEntity(requestData)

      // Manejar éxito
      state.isSuccess = true
      state.successMessage = `Entidad "${response.entidad_name}" (${response.entidad_code}) creada exitosamente como ${response.is_active ? 'ACTIVA' : 'INACTIVA'}`

      return { 
        success: true, 
        data: response 
      }

    } catch (error: any) {
      // Manejar error con mensajes más específicos
      let errorMessage = 'Error al crear la entidad'
      
      if (error.message) {
        // Usar el mensaje específico del backend si está disponible
        errorMessage = error.message
      } else if (error.response?.data?.detail) {
        // Usar el detalle de la respuesta si está disponible
        errorMessage = error.response.data.detail
      } else if (error.response?.status) {
        // Mensajes específicos por código de estado
        switch (error.response.status) {
          case 409:
            errorMessage = 'Ya existe una entidad con los datos proporcionados'
            break
          case 422:
            errorMessage = 'Los datos proporcionados no son válidos'
            break
          case 400:
            errorMessage = 'Datos incorrectos o incompletos'
            break
          case 500:
            errorMessage = 'Error interno del servidor. Inténtelo más tarde'
            break
          default:
            errorMessage = `Error del servidor (${error.response.status})`
        }
      }
      
      state.error = errorMessage
      state.isSuccess = false
      return { success: false }
    } finally {
      state.isLoading = false
    }
  }

  /**
   * Limpiar todos los estados
   */
  const clearState = () => {
    state.isLoading = false
    state.isSuccess = false
    state.error = ''
    state.successMessage = ''
    isCheckingCode.value = false
    codeValidationError.value = ''
  }

  /**
   * Limpiar solo mensajes (mantener loading states)
   */
  const clearMessages = () => {
    state.error = ''
    state.successMessage = ''
    state.isSuccess = false
    codeValidationError.value = ''
  }

  return {
    // Estado
    state,
    isCheckingCode: readonly(isCheckingCode),
    codeValidationError: readonly(codeValidationError),
    canSubmit,

    // Métodos
    validateForm,
    checkCodeAvailability,
    createEntity,
    clearState,
    clearMessages
  }
}

// Helper para readonly refs
function readonly<T>(ref: import('vue').Ref<T>) {
  return computed(() => ref.value)
}
