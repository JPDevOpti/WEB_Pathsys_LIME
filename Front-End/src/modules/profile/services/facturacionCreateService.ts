import { apiClient } from '@/core/config/axios.config'
import type { AxiosResponse } from 'axios'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  FacturacionCreateRequest, 
  FacturacionCreateResponse 
} from '../types/facturacion.types'

class FacturacionCreateService {
  private readonly facturacionEndpoint = API_CONFIG.ENDPOINTS.FACTURACION

  /**
   * Crear un nuevo usuario de facturación
   */
  async createFacturacion(facturacionData: FacturacionCreateRequest): Promise<FacturacionCreateResponse> {
    try {
      const response: AxiosResponse<FacturacionCreateResponse> = await apiClient.post<FacturacionCreateResponse>(
        this.facturacionEndpoint,
        facturacionData
      )
      
      // Si response.data es undefined, el backend está devolviendo el objeto directamente
      if (response.data === undefined) {
        return response as any
      }
      
      return response.data
    } catch (error: any) {
      console.error('Error creating facturacion:', error)
      console.error('Error response:', error.response)
      console.error('Error data:', error.response?.data)
      
      if (error.response?.status === 409) {
        // Extraer el mensaje específico del detalle del error
        const detail = error.response.data?.detail || 'Ya existe un usuario de facturación con estos datos'
        throw new Error(detail)
      } else if (error.response?.status === 422) {
        throw new Error('Los datos proporcionados no son válidos')
      } else if (error.response?.status === 400) {
        throw new Error('Datos incorrectos o incompletos')
      } else if (error.response?.data?.detail) {
        throw new Error(error.response.data.detail)
      } else if (error.message) {
        throw new Error(`Error del servidor: ${error.message}`)
      } else {
        throw new Error('Error interno del servidor. Inténtelo más tarde')
      }
    }
  }

  /**
   * Verificar si existe un código de facturación
   */
  async checkCodeExists(facturacionCode: string): Promise<boolean> {
    try {
      const response = await apiClient.get(
        `${this.facturacionEndpoint}/search?facturacion_code=${encodeURIComponent(facturacionCode)}`
      )
      return response.data?.facturacion && response.data.facturacion.length > 0
    } catch (error) {
      console.error('Error checking facturacion code:', error)
      return false
    }
  }

  /**
   * Verificar si existe un email de facturación
   */
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(
        `${this.facturacionEndpoint}/search?facturacion_email=${encodeURIComponent(email)}`
      )
      return response.data?.facturacion && response.data.facturacion.length > 0
    } catch (error) {
      console.error('Error checking facturacion email:', error)
      return false
    }
  }

  /**
   * Validar datos de facturación
   */
  validateFacturacionData(data: FacturacionCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!data.facturacion_name?.trim()) {
      errors.push('El nombre es requerido')
    } else if (data.facturacion_name.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    } else if (data.facturacion_name.length > 200) {
      errors.push('El nombre no puede exceder 200 caracteres')
    }

    if (!data.facturacion_code?.trim()) {
      errors.push('El código es requerido')
    } else if (data.facturacion_code.length < 3) {
      errors.push('El código debe tener al menos 3 caracteres')
    } else if (data.facturacion_code.length > 20) {
      errors.push('El código no puede exceder 20 caracteres')
    }

    if (!data.facturacion_email?.trim()) {
      errors.push('El email es requerido')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.facturacion_email)) {
      errors.push('El email no tiene un formato válido')
    }

    if (!data.password?.trim()) {
      errors.push('La contraseña es requerida')
    } else if (data.password.length < 6) {
      errors.push('La contraseña debe tener al menos 6 caracteres')
    } else if (data.password.length > 128) {
      errors.push('La contraseña no puede exceder 128 caracteres')
    }

    if (data.observaciones && data.observaciones.length > 500) {
      errors.push('Las observaciones no pueden exceder 500 caracteres')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

export const facturacionCreateService = new FacturacionCreateService()
