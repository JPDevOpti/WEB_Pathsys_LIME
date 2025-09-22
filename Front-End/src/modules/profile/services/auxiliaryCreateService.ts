import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  AuxiliaryCreateRequest, 
  AuxiliaryCreateResponse
} from '../types/auxiliary.types'

/**
 * Servicio para la creación y gestión de auxiliares
 */
class AuxiliaryCreateService {
  private readonly auxiliaryEndpoint = API_CONFIG.ENDPOINTS.AUXILIARIES

  /**
   * Crear un nuevo auxiliar (colección auxiliares + usuario)
   */
  async createAuxiliary(auxiliaryData: AuxiliaryCreateRequest): Promise<AuxiliaryCreateResponse> {
    try {
      // Crear el auxiliar en la colección auxiliares (incluye creación de usuario automáticamente)
      const response = await apiClient.post<AuxiliaryCreateResponse>(
        `${this.auxiliaryEndpoint}/`,
        auxiliaryData
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
        // Error de datos duplicados (Bad Request)
        if (error.message?.includes('email')) {
          throw new Error('Ya existe un auxiliar con este email')
        } else if (error.message?.includes('código') || error.message?.includes('code')) {
          throw new Error('Ya existe un auxiliar con este código')
        }
        throw new Error(error.message || 'Datos duplicados')
      } else if (error.response?.status === 422) {
        // Error de validación
        const validationErrors = error.response.data?.detail
        if (Array.isArray(validationErrors)) {
          const errorMessages = validationErrors.map((err: any) => {
            const field = err.loc?.[err.loc.length - 1] || 'campo'
            let fieldName = field
            
            // Traducir nombres de campos
            switch (field) {
              case 'auxiliarCode':
                fieldName = 'Código del auxiliar'
                break
              case 'auxiliarName':
                fieldName = 'Nombre del auxiliar'
                break
              case 'AuxiliarEmail':
                fieldName = 'Email'
                break
              case 'password':
                fieldName = 'Contraseña'
                break
              case 'observaciones':
                fieldName = 'Observaciones'
                break
            }
            
            // Traducir mensajes de error
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
        // Error genérico
        throw new Error(error.message || 'Error al crear el auxiliar')
      }
    }
  }


  /**
   * Verificar si un email ya existe (usando búsqueda de auxiliares)
   */
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.auxiliaryEndpoint}/search?auxiliar_email=${email}`)
      // Si encuentra resultados, el email existe
      return response && response.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false // Email no existe, está disponible
      }
      // Para otros errores, asumir que NO existe para permitir continuar
      return false
    }
  }

  /**
   * Validar datos del formulario antes de enviar
   */
  validateAuxiliaryData(data: AuxiliaryCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar nombre del auxiliar
    if (!data.auxiliarName?.trim()) {
      errors.push('El nombre del auxiliar es requerido')
    } else if (data.auxiliarName.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    } else if (data.auxiliarName.length > 100) {
      errors.push('El nombre no puede tener más de 100 caracteres')
    }

    // Validar código del auxiliar
    if (!data.auxiliarCode?.trim()) {
      errors.push('El código del auxiliar es requerido')
    } else if (data.auxiliarCode.length < 3) {
      errors.push('El código debe tener al menos 3 caracteres')
    } else if (data.auxiliarCode.length > 20) {
      errors.push('El código no puede tener más de 20 caracteres')
    }

    // Validar email
    if (!data.AuxiliarEmail?.trim()) {
      errors.push('El email es requerido')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.AuxiliarEmail)) {
      errors.push('El email debe tener un formato válido')
    }

    // Validar contraseña
    if (!data.password?.trim()) {
      errors.push('La contraseña es requerida')
    } else if (data.password.length < 6) {
      errors.push('La contraseña debe tener al menos 6 caracteres')
    }

    // Validar observaciones (opcional pero con límite)
    if (data.observaciones && data.observaciones.length > 500) {
      errors.push('Las observaciones no pueden tener más de 500 caracteres')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }
}

// Exportar instancia singleton
export const auxiliaryCreateService = new AuxiliaryCreateService()
export default auxiliaryCreateService
