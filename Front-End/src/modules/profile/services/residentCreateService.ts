// Resident creation service: handles resident creation, validation, and availability checks
import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { ResidentCreateRequest, ResidentCreateResponse } from '../types/resident.types'

class ResidentCreateService {
  private readonly residentEndpoint = API_CONFIG.ENDPOINTS.RESIDENTS
  private readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  private readonly trimOrEmpty = (v?: string) => (v ?? '').toString().trim()
  private readonly isEmailValid = (email: string) => this.EMAIL_REGEX.test(email)

  // Create new resident (includes automatic user creation)
  async createResident(residentData: ResidentCreateRequest): Promise<ResidentCreateResponse> {
    try {
      const response = await apiClient.post<ResidentCreateResponse>(`${this.residentEndpoint}/`, residentData)
      return response
    } catch (error: any) {
      if (error.response?.status === 409) {
        const errorMessage = error.response.data?.detail || error.message || 'Datos duplicados'
        const customError = new Error(errorMessage) as any
        customError.response = error.response
        throw customError
      } else if (error.response?.status === 400) {
        if (error.message?.includes('email')) throw new Error('Ya existe un residente con este email')
        if (error.message?.includes('código') || error.message?.includes('code')) throw new Error('Ya existe un residente con este código')
        if (error.message?.includes('registro')) throw new Error('Ya existe un residente con este registro médico')
        throw new Error(error.message || 'Datos duplicados')
      } else if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) {
          const errorMessages = validationErrors.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'campo'
            let fieldName = field
            switch (field) {
              case 'residente_code': fieldName = 'Código del residente'; break
              case 'residente_name': fieldName = 'Nombre del residente'; break
              case 'residente_email': fieldName = 'Email'; break
              case 'registro_medico': fieldName = 'Registro médico'; break
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
            } else if (message.includes('field required')) message = 'es requerido'
            else if (message.includes('value is not a valid email')) message = 'debe tener un formato de email válido'
            return `${fieldName} ${message}`
          }).join(', ')
          throw new Error(errorMessages)
        }
        throw new Error('Datos inválidos en el formulario')
      } else {
        throw new Error(error.message || 'Error al crear el residente')
      }
    }
  }

  // Check if resident code already exists
  async checkCodeExists(residenteCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.residentEndpoint}/${this.trimOrEmpty(residenteCode)}`)
      return true
    } catch (error: any) {
      return error.response?.status !== 404
    }
  }

  // Check if email already exists using search
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.residentEndpoint}/search`, {
        params: { q: this.trimOrEmpty(email), limit: 1 }
      })
      const data = (response as any).data ?? response
      return Array.isArray(data) && data.length > 0
    } catch (error: any) {
      return error.response?.status !== 404
    }
  }

  // Check if medical license already exists using search
  async checkMedicalLicenseExists(registro_medico: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.residentEndpoint}/search`, {
        params: { q: this.trimOrEmpty(registro_medico), limit: 1 }
      })
      const data = (response as any).data ?? response
      return Array.isArray(data) && data.length > 0
    } catch (error: any) {
      return error.response?.status !== 404
    }
  }

  // Validate form data before submission
  validateResidentData(data: ResidentCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []
    const { resident_name, resident_code, resident_email, medical_license, password, observations } = data

    if (!this.trimOrEmpty(resident_name)) errors.push('El nombre del residente es requerido')
    else if (this.trimOrEmpty(resident_name).length < 2) errors.push('El nombre debe tener al menos 2 caracteres')
    else if (this.trimOrEmpty(resident_name).length > 100) errors.push('El nombre no puede tener más de 100 caracteres')

    if (!this.trimOrEmpty(resident_code)) errors.push('El código del residente es requerido')
    else if (this.trimOrEmpty(resident_code).length < 3) errors.push('El código debe tener al menos 3 caracteres')
    else if (this.trimOrEmpty(resident_code).length > 20) errors.push('El código no puede tener más de 20 caracteres')

    if (!this.trimOrEmpty(resident_email)) errors.push('El email es requerido')
    else if (!this.isEmailValid(this.trimOrEmpty(resident_email))) errors.push('El email debe tener un formato válido')

    if (!this.trimOrEmpty(medical_license)) errors.push('El registro médico es requerido')
    else if (this.trimOrEmpty(medical_license).length < 3) errors.push('El registro médico debe tener al menos 3 caracteres')
    else if (this.trimOrEmpty(medical_license).length > 50) errors.push('El registro médico no puede tener más de 50 caracteres')

    if (!this.trimOrEmpty(password)) errors.push('La contraseña es requerida')
    else if (this.trimOrEmpty(password).length < 6) errors.push('La contraseña debe tener al menos 6 caracteres')

    if (observations && this.trimOrEmpty(observations).length > 500) errors.push('Las observaciones no pueden tener más de 500 caracteres')

    return { isValid: errors.length === 0, errors }
  }
}

export const residentCreateService = new ResidentCreateService()
export default residentCreateService
