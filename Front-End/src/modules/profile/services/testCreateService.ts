import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestCreateRequest, TestCreateResponse } from '../types/test.types'

/**
 * Servicio para la creación y gestión de pruebas médicas
 */
class TestCreateService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  /**
   * Crear una nueva prueba
   */
  async createTest(testData: TestCreateRequest): Promise<TestCreateResponse> {
    try {
      // Enviar los datos directamente (tiempo en días)
      const response = await apiClient.post<TestCreateResponse>(
        `${this.endpoint}/`,
        testData
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
        throw new Error(error.message || 'Ya existe una prueba con este código')
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
        throw new Error(error.message || 'Error al crear la prueba')
      }
    }
  }

  /**
   * Verificar si un código de prueba ya existe
   */
  async checkCodeExists(pruebaCode: string): Promise<boolean> {
    try {
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
   * Validar datos del formulario antes de enviar
   */
  validateTestData(data: Partial<TestCreateRequest>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar código de prueba
    if (!data.pruebaCode?.trim()) {
      errors.push('El código de prueba es requerido')
    } else if (data.pruebaCode.length < 3) {
      errors.push('El código debe tener al menos 3 caracteres')
    } else if (!/^[A-Z0-9_-]+$/i.test(data.pruebaCode)) {
      errors.push('El código solo puede contener letras, números, guiones y guiones bajos')
    }

    // Validar nombre
    if (!data.pruebasName?.trim()) {
      errors.push('El nombre de la prueba es requerido')
    } else if (data.pruebasName.length < 3) {
      errors.push('El nombre debe tener al menos 3 caracteres')
    }

    // Validar descripción
    if (!data.pruebasDescription?.trim()) {
      errors.push('La descripción es requerida')
    } else if (data.pruebasDescription.length < 10) {
      errors.push('La descripción debe tener al menos 10 caracteres')
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
export const testCreateService = new TestCreateService()
export default testCreateService
