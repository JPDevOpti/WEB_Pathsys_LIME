import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestUpdateRequest, TestUpdateResponse, TestEditFormModel } from '../types/test.types'

/**
 * Servicio para la edición y actualización de pruebas médicas
 */
class TestEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  /**
   * Obtener una prueba por código para edición
   */
  async getTestByCode(pruebaCode: string): Promise<TestEditFormModel> {
    try {
      const response = await apiClient.get<TestUpdateResponse>(
        `${this.endpoint}/code/${pruebaCode}`
      )
      
      // Convertir la respuesta del backend (snake_case) al modelo del formulario (camelCase)
      return {
        id: response.id,
        pruebaCode: response.prueba_code,
        pruebasName: response.prueba_name,
        pruebasDescription: response.prueba_description,
        tiempo: response.tiempo,
        isActive: response.is_active
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Prueba no encontrada')
      }
      throw new Error(error.message || 'Error al obtener los datos de la prueba')
    }
  }

  /**
   * Actualizar una prueba existente
   */
  async updateTest(originalCode: string, testData: TestUpdateRequest): Promise<TestUpdateResponse> {
    try {
      const response = await apiClient.put<TestUpdateResponse>(
        `${this.endpoint}/code/${originalCode}`,
        testData
      )
      return response
    } catch (error: any) {
      // Manejo específico de errores del backend
      if (error.response?.status === 400) {
        // Error de código duplicado o validación
        throw new Error(error.message || 'Ya existe una prueba con este código')
      } else if (error.response?.status === 404) {
        // Prueba no encontrada
        throw new Error('Prueba no encontrada')
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
        throw new Error(error.message || 'Error al actualizar la prueba')
      }
    }
  }

  /**
   * Verificar si un código de prueba ya existe (excluyendo el código actual)
   */
  async checkCodeExists(pruebaCode: string, originalCode?: string): Promise<boolean> {
    try {
      // Si es el mismo código original, no hay conflicto
      if (originalCode && pruebaCode === originalCode) {
        return false
      }

      await apiClient.get(`${this.endpoint}/code/${pruebaCode}`)
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
   * Validar datos del formulario de edición antes de enviar
   */
  validateTestData(data: Partial<TestEditFormModel>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar código de prueba
    if (!data.pruebaCode?.trim()) {
      errors.push('El código de prueba es requerido')
    } else if (!/^[A-Z0-9_-]+$/i.test(data.pruebaCode)) {
      errors.push('El código solo puede contener letras, números, guiones y guiones bajos')
    }

    // Validar nombre
    if (!data.pruebasName?.trim()) {
      errors.push('El nombre de la prueba es requerido')
    }

    // Validar descripción
    if (!data.pruebasDescription?.trim()) {
      errors.push('La descripción es requerida')
    }

    // Validar tiempo (en días)
    if (!data.tiempo || data.tiempo <= 0) {
      errors.push('El tiempo estimado debe ser mayor a 0 días')
    } else if (data.tiempo > 365) { // máximo 1 año
      errors.push('El tiempo estimado no puede ser mayor a 365 días')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

// Exportar instancia singleton
export const testEditService = new TestEditService()
export default testEditService
