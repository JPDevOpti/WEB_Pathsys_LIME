import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestCreateRequest, TestCreateResponse } from '../types/test.types'

class TestCreateService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  async createTest(testData: TestCreateRequest): Promise<TestCreateResponse> {
    try {
      const response = await apiClient.post<TestCreateResponse>(`${this.endpoint}/`, testData)
      return response
    } catch (error: any) {
      if (error.response?.status === 409) {
        const errorMessage = error.response.data?.detail || error.message || 'Datos duplicados'
        const customError = new Error(errorMessage) as any
        customError.response = error.response
        throw customError
      } else if (error.response?.status === 400) {
        throw new Error(error.message || 'Ya existe una prueba con este código')
      } else if (error.response?.status === 422) {
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
        throw new Error(error.message || 'Error al crear la prueba')
      }
    }
  }

  async checkCodeExists(testCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.endpoint}/code/${testCode}`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return true
    }
  }

  validateTestData(data: Partial<TestCreateRequest>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!data.test_code?.trim()) {
      errors.push('El código de prueba es requerido')
    } else if (data.test_code.length < 3) {
      errors.push('El código debe tener al menos 3 caracteres')
    } else if (!/^[A-Z0-9_-]+$/i.test(data.test_code)) {
      errors.push('El código solo puede contener letras, números, guiones y guiones bajos')
    }

    if (!data.name?.trim()) {
      errors.push('El nombre de la prueba es requerido')
    } else if (data.name.length < 3) {
      errors.push('El nombre debe tener al menos 3 caracteres')
    }

    if (!data.description?.trim()) {
      errors.push('La descripción es requerida')
    } else if (data.description.length < 10) {
      errors.push('La descripción debe tener al menos 10 caracteres')
    }

    if (!data.time || data.time <= 0) {
      errors.push('El tiempo estimado debe ser mayor a 0 días')
    } else if (data.time > 365) {
      errors.push('El tiempo estimado no puede ser mayor a 365 días')
    }

    if (data.price === undefined || data.price === null) {
      errors.push('El precio es requerido')
    } else if (data.price < 0) {
      errors.push('El precio no puede ser negativo')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

export const testCreateService = new TestCreateService()
export default testCreateService
