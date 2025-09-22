import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { TestUpdateRequest, TestUpdateResponse, TestEditFormModel } from '../types/test.types'

class TestEditService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  async getTestByCode(testCode: string): Promise<TestEditFormModel> {
    try {
      const response = await apiClient.get<TestUpdateResponse>(`${this.endpoint}/code/${testCode}`)
      
      return {
        id: response._id,
        testCode: response.test_code,
        testName: response.name,
        testDescription: response.description,
        timeDays: response.time,
        price: response.price,
        isActive: response.is_active
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error('Prueba no encontrada')
      }
      throw new Error(error.message || 'Error al obtener los datos de la prueba')
    }
  }

  async updateTest(originalCode: string, testData: TestUpdateRequest): Promise<TestUpdateResponse> {
    try {
      const response = await apiClient.put<TestUpdateResponse>(`${this.endpoint}/${originalCode}`, testData)
      return response
    } catch (error: any) {
      if (error.response?.status === 400) {
        throw new Error(error.message || 'Ya existe una prueba con este código')
      } else if (error.response?.status === 404) {
        throw new Error('Prueba no encontrada')
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
        throw new Error(error.message || 'Error al actualizar la prueba')
      }
    }
  }

  async checkCodeExists(testCode: string, originalCode?: string): Promise<boolean> {
    try {
      if (originalCode && testCode === originalCode) {
        return false
      }

      await apiClient.get(`${this.endpoint}/${testCode}`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return true
    }
  }

  validateTestData(data: Partial<TestEditFormModel>): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!data.testCode?.trim()) {
      errors.push('El código de prueba es requerido')
    } else if (!/^[A-Z0-9_-]+$/i.test(data.testCode)) {
      errors.push('El código solo puede contener letras, números, guiones y guiones bajos')
    }

    if (!data.testName?.trim()) {
      errors.push('El nombre de la prueba es requerido')
    }

    if (!data.testDescription?.trim()) {
      errors.push('La descripción es requerida')
    }

    if (!data.timeDays || data.timeDays <= 0) {
      errors.push('El tiempo estimado debe ser mayor a 0 días')
    } else if (data.timeDays > 365) {
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

export const testEditService = new TestEditService()
export default testEditService
