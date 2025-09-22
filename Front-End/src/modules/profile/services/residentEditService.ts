/**
 * Servicio para la edición de residentes
 */
import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  ResidentEditFormModel, 
  ResidentUpdateRequest, 
  ResidentUpdateResponse 
} from '../types/resident.types'

export interface ResidentEditResult {
  success: boolean
  data?: ResidentUpdateResponse
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
  /**
   * Obtiene un residente por código
   */
  async getResidentByCode(code: string): Promise<ResidentEditResult> {
    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`)
      return {
        success: true,
        data: response.data
      }
    } catch (error: any) {
      return {
        success: false,
        error: error.response?.data?.detail || 'Error al obtener residente'
      }
    }
  },

  /**
   * Actualiza un residente por código
   */
  async updateResident(code: string, residentData: ResidentUpdateRequest): Promise<ResidentEditResult> {
    try {
      // console.log('🔧 Datos a enviar para actualización:', { code, residentData })
      const response = await apiClient.put(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`, residentData)
      // console.log('✅ Respuesta actualización residente:', response)
      return {
        success: true,
        data: response.data || response
      }
    } catch (error: any) {
      // console.error('❌ Error en actualización residente:', error)
      const errorMessage = error.response?.data?.detail || error.message || 'Error al actualizar residente'
      return {
        success: false,
        error: Array.isArray(errorMessage) ? errorMessage.join(', ') : errorMessage
      }
    }
  },

  /**
   * Verifica si un código está disponible (excluyendo el actual)
   */
  async checkCodeExists(code: string, currentCode: string): Promise<CodeCheckResult> {
    // Si es el mismo código actual, está disponible
    if (code === currentCode) {
      return { available: true }
    }

    try {
      await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/${code}`)
      // Si encuentra el residente, el código no está disponible
      return {
        available: false,
        error: 'Este código ya está en uso'
      }
    } catch (error: any) {
      // Si no encuentra el residente (404), el código está disponible
      if (error.response?.status === 404) {
        return { available: true }
      }
      // Otros errores
      return {
        available: false,
        error: 'Error al verificar disponibilidad del código'
      }
    }
  },

  /**
   * Verifica si un email está disponible (excluyendo el actual)
   */
  async checkEmailExists(email: string, currentEmail: string): Promise<EmailCheckResult> {
    // Si es el mismo email actual, está disponible
    if (email === currentEmail) {
      return { available: true }
    }

    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
        params: { q: email, limit: 1 }
      })
      
      // Si hay resultados, el email no está disponible
      if (Array.isArray(response) && response.length > 0) {
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

  /**
   * Verifica si un registro médico está disponible (excluyendo el actual)
   */
  async checkLicenseExists(license: string, currentLicense: string): Promise<LicenseCheckResult> {
    // Si es el mismo registro actual, está disponible
    if (license === currentLicense) {
      return { available: true }
    }

    try {
      const response = await apiClient.get(`${API_CONFIG.ENDPOINTS.RESIDENTS}/search`, {
        params: { q: license, limit: 1 }
      })
      
      // Si hay resultados, el registro no está disponible
      if (Array.isArray(response) && response.length > 0) {
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

  /**
   * Prepara los datos para actualización
   */
  prepareUpdateData(formModel: ResidentEditFormModel): ResidentUpdateRequest {
    const data = {
      residente_name: formModel.residenteName.trim(),
      iniciales_residente: formModel.InicialesResidente.trim(),
      residente_email: formModel.ResidenteEmail.trim(),
      registro_medico: formModel.registro_medico.trim(),
      observaciones: formModel.observaciones.trim(),
      is_active: formModel.isActive,
      // Incluir password solo si el usuario ingresó un valor
      ...(formModel.password && formModel.password.trim().length >= 6 ? { password: formModel.password } : {})
    }
    // console.log('📋 Datos preparados para actualización:', data)
    return data
  },

  // Función para normalizar datos del backend (snake_case) al frontend (camelCase)
  normalizeResidentData(backendData: any): ResidentUpdateResponse {
    return {
      id: backendData.id || backendData._id,
      residenteName: backendData.residente_name,
      InicialesResidente: backendData.iniciales_residente,
      residenteCode: backendData.residente_code,
      ResidenteEmail: backendData.residente_email,
      registro_medico: backendData.registro_medico,
      observaciones: backendData.observaciones || '',
      isActive: backendData.is_active,
      fecha_creacion: backendData.fecha_creacion,
      fecha_actualizacion: backendData.fecha_actualizacion
    }
  }
}
