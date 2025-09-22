import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PathologistCreateRequest, PathologistCreateResponse } from '../types/pathologist.types'

// Service responsible for creating pathologists and performing simple availability checks
class PathologistCreateService {
  private readonly pathologistEndpoint = API_CONFIG.ENDPOINTS.PATHOLOGISTS
  // Shared helpers
  private readonly EMAIL_REGEX = /^[^\s@]+@[^\s@]+\.[^\s@]+$/
  private trimOrEmpty = (v?: string) => (v ?? '').toString().trim()
  private isEmailValid = (email: string) => this.EMAIL_REGEX.test(email)

  // Create a pathologist (backend returns response.data already via apiClient)
  async createPathologist(pathologistData: PathologistCreateRequest): Promise<PathologistCreateResponse> {
    try {
      // Normalize payload to expected backend format
      const payload: PathologistCreateRequest = {
        pathologist_name: this.trimOrEmpty(pathologistData.pathologist_name),
        initials: this.trimOrEmpty(pathologistData.initials).toUpperCase(),
        pathologist_code: this.trimOrEmpty(pathologistData.pathologist_code).toUpperCase(),
        pathologist_email: this.trimOrEmpty(pathologistData.pathologist_email),
        medical_license: this.trimOrEmpty(pathologistData.medical_license),
        password: this.trimOrEmpty(pathologistData.password),
        signature: this.trimOrEmpty(pathologistData.signature),
        observations: this.trimOrEmpty(pathologistData.observations),
        is_active: !!pathologistData.is_active
      }
      const response = await apiClient.post<PathologistCreateResponse>(`${this.pathologistEndpoint}/`, payload)
      return response
    } catch (error: any) {
      // Map common server errors to user-friendly messages
      if (error.response?.status === 409) {
        const errorMessage = error.response.data?.detail || error.message || 'Datos duplicados'
        const customError = new Error(errorMessage) as any
        customError.response = error.response
        throw customError
      } else if (error.response?.status === 400) {
        if (error.message?.includes('email')) {
          throw new Error('Ya existe un patólogo con este email')
        } else if (error.message?.includes('código') || error.message?.includes('code')) {
          throw new Error('Ya existe un patólogo con este código')
        } else if (error.message?.includes('registro')) {
          throw new Error('Ya existe un patólogo con este registro médico')
        }
        throw new Error(error.message || 'Datos duplicados')
      } else if (error.response?.status === 422) {
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) {
          // Build a single, readable validation error message
          const errorMessages = validationErrors.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'campo'
            let fieldName = field
            switch (field) {
              case 'pathologist_code': fieldName = 'Código del patólogo'; break
              case 'pathologist_name': fieldName = 'Nombre del patólogo'; break
              case 'pathologist_email': fieldName = 'Email'; break
              case 'medical_license': fieldName = 'Registro médico'; break
              case 'initials': fieldName = 'Iniciales'; break
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
          throw new Error(errorMessages)
        }
        throw new Error('Datos inválidos en el formulario')
      } else {
        throw new Error(error.message || 'Error al crear el patólogo')
      }
    }
  }

  // Existence checks (simple best-effort calls used for UX prevalidation)
  async checkCodeExists(patologoCode: string): Promise<boolean> {
    try {
      const code = this.trimOrEmpty(patologoCode)
      if (!code) return false
      await apiClient.get(`${this.pathologistEndpoint}/${code}`)
      return true
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return true
    }
  }

  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const normalized = this.trimOrEmpty(email)
      if (!normalized || !this.isEmailValid(normalized)) return false
      const response: any = await apiClient.get(`${this.pathologistEndpoint}/search`, { params: { q: normalized, limit: 1 } })
      const list = Array.isArray(response) ? response : response?.data
      return Array.isArray(list) && list.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return false
    }
  }

  async checkMedicalLicenseExists(registro_medico: string): Promise<boolean> {
    try {
      const license = this.trimOrEmpty(registro_medico)
      if (!license) return false
      const response: any = await apiClient.get(`${this.pathologistEndpoint}/search`, { params: { q: license, limit: 1 } })
      const list = Array.isArray(response) ? response : response?.data
      return Array.isArray(list) && list.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false
      }
      return false
    }
  }

  // Client-side data validation used before sending to the API
  validatePathologistData(data: PathologistCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []
    if (!data.pathologist_name?.trim()) {
      errors.push('El nombre del patólogo es requerido')
    } else if (data.pathologist_name.length > 200) {
      errors.push('El nombre no puede tener más de 200 caracteres')
    }
    if (!data.initials?.trim()) {
      errors.push('Las iniciales son requeridas')
    } else if (data.initials.length > 10) {
      errors.push('Las iniciales no pueden tener más de 10 caracteres')
    }
    if (!data.pathologist_code?.trim()) {
      errors.push('El código del patólogo es requerido')
    } else if (data.pathologist_code.length > 10) {
      errors.push('El código no puede tener más de 10 caracteres')
    }
    if (!data.pathologist_email?.trim()) {
      errors.push('El email es requerido')
    } else if (!this.isEmailValid(data.pathologist_email)) {
      errors.push('El email debe tener un formato válido')
    }
    if (!data.medical_license?.trim()) {
      errors.push('El registro médico es requerido')
    } else if (data.medical_license.length > 50) {
      errors.push('El registro médico no puede tener más de 50 caracteres')
    }
    if (data.observations && data.observations.length > 500) {
      errors.push('Las observaciones no pueden tener más de 500 caracteres')
    }
    return { isValid: errors.length === 0, errors }
  }
}

export const pathologistCreateService = new PathologistCreateService()
export default pathologistCreateService
