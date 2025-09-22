// Resident edit service: handles resident fetching, uniqueness checks, updates, and data normalization
import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  ResidentEditFormModel, 
  ResidentUpdateRequest
} from '../types/resident.types'

export interface ResidentEditResult {
  success: boolean
  data?: any
  error?: string
}

export interface CodeCheckResult {
  available: boolean
  error?: string
}

export interface EmailCheckResult {
  available: boolean
  error?: string
}

export interface LicenseCheckResult {
  available: boolean
  error?: string
}

export const residentEditService = {
  // Helper to safely trim string values
  trimOrEmpty(value?: string) {
    return (value ?? '').toString().trim()
  },
  
  // Helper to unwrap API response data
  unwrap<T = any>(response: any): T {
    return (response && response.data) ? response.data : response
  },

  // Fetch resident by code
  async getResidentByCode(code: string): Promise<ResidentEditResult> {
    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${this.trimOrEmpty(code)}`)
      return {
        success: true,
        data: this.unwrap(response)
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al obtener residente'
      }
    }
  },

  // Update resident by code
  async updateResident(code: string, residentData: ResidentUpdateRequest): Promise<ResidentEditResult> {
    try {
      console.log('🔧 Sending update request:', { code, residentData })
      const response = await apiClient.put(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${this.trimOrEmpty(code)}`, residentData)
      console.log('📡 Raw API response:', response)
      const unwrappedData = this.unwrap(response)
      console.log('📦 Unwrapped data:', unwrappedData)
      return {
        success: true,
        data: unwrappedData
      }
    } catch (error: any) {
      console.error('❌ Update error:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar residente'
      return {
        success: false,
        error: Array.isArray(errorMessage) ? errorMessage.join(', ') : errorMessage
      }
    }
  },

  // Check if resident code is available (excluding current code)
  async checkCodeExists(code: string, currentCode: string): Promise<CodeCheckResult> {
    if (code === currentCode) {
      return { available: true }
    }

    try {
      await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`)
      return {
        available: false,
        error: 'Este código ya está en uso'
      }
    } catch (error: any) {
      if (error.response?.status === 404) {
        return { available: true }
      }
      return {
        available: false,
        error: 'Error al verificar disponibilidad del código'
      }
    }
  },

  // Check if email is available (excluding current email)
  async checkEmailExists(email: string, currentEmail: string): Promise<EmailCheckResult> {
    if (email === currentEmail) {
      return { available: true }
    }

    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
        params: { q: this.trimOrEmpty(email), limit: 1 }
      })
      const data = this.unwrap(response)
      if (Array.isArray(data) && data.length > 0) {
        return {
          available: false,
          error: 'Este email ya está en uso'
        }
      }
      
      return { available: true }
    } catch (error: any) {
      return {
        available: false,
        error: 'Error al verificar disponibilidad del email'
      }
    }
  },

  // Check if medical license is available (excluding current license)
  async checkLicenseExists(license: string, currentLicense: string): Promise<LicenseCheckResult> {
    if (license === currentLicense) {
      return { available: true }
    }

    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
        params: { q: this.trimOrEmpty(license), limit: 1 }
      })
      const data = this.unwrap(response)
      if (Array.isArray(data) && data.length > 0) {
        return {
          available: false,
          error: 'Este registro médico ya está en uso'
        }
      }
      
      return { available: true }
    } catch (error: any) {
      return {
        available: false,
        error: 'Error al verificar disponibilidad del registro médico'
      }
    }
  },

  // Prepare form data for backend update (convert to snake_case)
  prepareUpdateData(formModel: ResidentEditFormModel): ResidentUpdateRequest {
    const data = {
      resident_name: this.trimOrEmpty(formModel.residenteName),
      initials: this.trimOrEmpty(formModel.InicialesResidente),
      resident_email: this.trimOrEmpty(formModel.ResidenteEmail),
      medical_license: this.trimOrEmpty(formModel.registro_medico),
      observations: this.trimOrEmpty(formModel.observaciones),
      is_active: !!formModel.isActive,
      ...(formModel.password && this.trimOrEmpty(formModel.password).length >= 6 ? { password: formModel.password } : {})
    }
    return data
  },

  // Normalize backend data to frontend form model (convert to camelCase)
  normalizeResidentData(backendData: any): any {
    console.log('🔄 Normalize - input backendData:', backendData)
    const normalized = {
      id: backendData.id || backendData._id,
      residenteName: backendData.resident_name,
      InicialesResidente: backendData.initials,
      residenteCode: backendData.resident_code,
      ResidenteEmail: backendData.resident_email,
      registro_medico: backendData.medical_license,
      observaciones: backendData.observations || '',
      isActive: backendData.is_active,
      fecha_creacion: backendData.created_at,
      fecha_actualizacion: backendData.updated_at
    }
    console.log('🔄 Normalize - output normalized:', normalized)
    return normalized
  }
}