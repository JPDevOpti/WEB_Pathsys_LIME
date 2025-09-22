import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  AuxiliaryCreateRequest, 
  AuxiliaryCreateResponse
} from '../types/auxiliary.types'

// Service to create and validate auxiliaries
class AuxiliaryCreateService {
  private readonly auxiliaryEndpoint = API_CONFIG.ENDPOINTS.AUXILIARIES

  // Small helper to map backend validation errors to readable Spanish
  private mapValidationErrors(detail: any[]): string {
    return detail.map((err: any) => {
      const field = err.loc?.[err.loc.length - 1] || 'campo'
      let fieldName = field
      switch (field) {
        case 'auxiliar_code': fieldName = 'Código del auxiliar'; break
        case 'auxiliar_name': fieldName = 'Nombre del auxiliar'; break
        case 'auxiliar_email': fieldName = 'Email'; break
        case 'password': fieldName = 'Contraseña'; break
        case 'observaciones': fieldName = 'Observaciones'; break
      }
      let message = err.msg
      if (message.includes('String should have at most')) {
        const maxChars = message.match(/\d+/)?.[0]
        message = `debe tener máximo ${maxChars} caracteres`
      } else if (message.includes('String should have at least')) {
        const minChars = message.match(/\d+/)?.[0]
        message = `debe tener mínimo ${minChars} caracteres`
      } else if (message.includes('field required')) {
        message = 'es requerido'
      } else if (message.includes('value is not a valid email')) {
        message = 'debe tener un formato de email válido'
      }
      return `${fieldName} ${message}`
    }).join(', ')
  }

  // Create auxiliary (also creates user under the hood)
  async createAuxiliary(auxiliaryData: AuxiliaryCreateRequest): Promise<AuxiliaryCreateResponse> {
    try {
      const response = await apiClient.post<AuxiliaryCreateResponse>(`${this.auxiliaryEndpoint}/`, auxiliaryData)
      return response
    } catch (error: any) {
      // Prefer precise backend messages when available
      if (error.response?.status === 409) {
        const errorMessage = error.response.data?.detail || error.message || 'Datos duplicados'
        const customError = new Error(errorMessage) as any
        customError.response = error.response
        throw customError
      }
      if (error.response?.status === 400) {
        if (error.message?.includes('email')) throw new Error('Ya existe un auxiliar con este email')
        if (error.message?.includes('código') || error.message?.includes('code')) throw new Error('Ya existe un auxiliar con este código')
        throw new Error(error.message || 'Datos duplicados')
      }
      if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) throw new Error(this.mapValidationErrors(validationErrors))
        throw new Error('Datos inválidos en el formulario')
      }
      throw new Error(error.message || 'Error al crear el auxiliar')
    }
  }

  // Check if email already exists via search endpoint
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.auxiliaryEndpoint}/search?auxiliar_email=${email}`)
      return Array.isArray(response) && response.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) return false
      return false
    }
  }

  // Synchronous pre-submit validation for UI
  validateAuxiliaryData(data: AuxiliaryCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []
    if (!data.auxiliar_name?.trim()) errors.push('El nombre del auxiliar es requerido')
    else if (data.auxiliar_name.length < 2) errors.push('El nombre debe tener al menos 2 caracteres')
    else if (data.auxiliar_name.length > 100) errors.push('El nombre no puede tener más de 100 caracteres')

    if (!data.auxiliar_code?.trim()) errors.push('El código del auxiliar es requerido')
    else if (data.auxiliar_code.length < 3) errors.push('El código debe tener al menos 3 caracteres')
    else if (data.auxiliar_code.length > 20) errors.push('El código no puede tener más de 20 caracteres')

    if (!data.auxiliar_email?.trim()) errors.push('El email es requerido')
    else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.auxiliar_email)) errors.push('El email debe tener un formato válido')

    if (!data.password?.trim()) errors.push('La contraseña es requerida')
    else if (data.password.length < 6) errors.push('La contraseña debe tener al menos 6 caracteres')

    if (data.observaciones && data.observaciones.length > 500) errors.push('Las observaciones no pueden tener más de 500 caracteres')

    return { isValid: errors.length === 0, errors }
  }
}

export const auxiliaryCreateService = new AuxiliaryCreateService()
export default auxiliaryCreateService
