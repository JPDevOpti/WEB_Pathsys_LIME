import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { EntityCreateRequest, EntityCreateResponse } from '../types/entity.types'

/**
 * Servicio para la creación y gestión de entidades
 */
class EntityCreateService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.ENTITIES

  /**
   * Crear una nueva entidad
   */
  async createEntity(entityData: EntityCreateRequest): Promise<EntityCreateResponse> {
    try {
      // Enviar los datos directamente
      const response = await apiClient.post<EntityCreateResponse>(
        `${this.endpoint}/`,
        entityData
      )
      return response  // ✅ CORREGIDO: El cliente axios ya retorna response.data
    } catch (error: any) {
      // Manejo específico de errores del backend
      if (error.response?.status === 409) {
        // Error de datos duplicados (Conflict)
        const errorMessage = error.response.data?.detail || error.message || 'Datos duplicados'
        const customError = new Error(errorMessage) as any
        customError.response = error.response // Preservar la respuesta original
        throw customError
      } else if (error.response?.status === 400) {
        // Error de código duplicado
        throw new Error(error.message || 'Ya existe una entidad con este código')
      } else if (error.response?.status === 422) {
        // Error de validación
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) {
          const errorMessages = validationErrors.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'campo'
            return `${field}: ${err.msg}`
          }).join(', ')
          throw new Error(`Errores de validación: ${errorMessages}`)
        }
        throw new Error('Datos inválidos en el formulario')
      } else {
        // Error genérico
        throw new Error(error.message || 'Error al crear la entidad')
      }
    }
  }

  /**
   * Verificar si un código de entidad ya existe
   */
  async checkCodeExists(entidadCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.endpoint}/code/${entidadCode}`)
      return true // Si no lanza error, el código existe
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false // Código no existe, está disponible
      }
      // Para otros errores, asumir que existe para evitar duplicados
      return true
    }
  }

  /**
   * Validar datos del formulario antes de enviar
   */
  validateEntityData(data: Partial<EntityCreateRequest>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar nombre de entidad
    if (!data.EntidadName?.trim()) {
      errors.push('El nombre de la entidad es requerido')
    } else if (data.EntidadName.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    } else if (data.EntidadName.length > 200) {
      errors.push('El nombre no puede tener más de 200 caracteres')
    }

    // Validar código de entidad
    if (!data.EntidadCode?.trim()) {
      errors.push('El código de la entidad es requerido')
    } else if (data.EntidadCode.length < 2) {
      errors.push('El código debe tener al menos 2 caracteres')
    } else if (data.EntidadCode.length > 20) {
      errors.push('El código no puede tener más de 20 caracteres')
    } else if (!/^[A-Z0-9_-]+$/i.test(data.EntidadCode)) {
      errors.push('El código solo puede contener letras, números, guiones y guiones bajos')
    }

    // Validar observaciones (opcional pero con límite)
    if (data.observaciones && data.observaciones.length > 500) {
      errors.push('Las observaciones no pueden tener más de 500 caracteres')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

// Exportar instancia singleton
export const entityCreateService = new EntityCreateService()
export default entityCreateService
