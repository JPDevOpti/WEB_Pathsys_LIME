import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  ResidentCreateRequest, 
  ResidentCreateResponse
} from '../types/resident.types'

/**
 * Servicio para la creación y gestión de residentes
 */
class ResidentCreateService {
  private readonly residentEndpoint = API_CONFIG.ENDPOINTS.RESIDENTS

  /**
   * Crear un nuevo residente (colección residentes + usuario)
   */
  async createResident(residentData: ResidentCreateRequest): Promise<ResidentCreateResponse> {
    try {
      // Crear el residente en la colección residentes (incluye creación de usuario automáticamente)
      const response = await apiClient.post<ResidentCreateResponse>(
        `${this.residentEndpoint}/`,
        residentData
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
          throw new Error('Ya existe un residente con este email')
        } else if (error.message?.includes('código') || error.message?.includes('code')) {
          throw new Error('Ya existe un residente con este código')
        } else if (error.message?.includes('registro')) {
          throw new Error('Ya existe un residente con este registro médico')
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
              case 'residente_code':
                fieldName = 'Código del residente'
                break
              case 'residente_name':
                fieldName = 'Nombre del residente'
                break
              case 'residente_email':
                fieldName = 'Email'
                break
              case 'registro_medico':
                fieldName = 'Registro médico'
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
        throw new Error(error.message || 'Error al crear el residente')
      }
    }
  }

  /**
   * Verificar si un código de residente ya existe
   */
  async checkCodeExists(residenteCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.residentEndpoint}/${residenteCode}`)
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
   * Verificar si un email ya existe (usando búsqueda de residentes)
   */
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.residentEndpoint}/search?residente_email=${email}`)
      // Si encuentra resultados, el email existe
      return response.residentes && response.residentes.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false // Email no existe, está disponible
      }
      // Para otros errores, asumir que NO existe para permitir continuar
      return false
    }
  }

  /**
   * Verificar si un registro médico ya existe
   */
  async checkMedicalLicenseExists(registro_medico: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.residentEndpoint}/search?registro_medico=${registro_medico}`)
      // Si encuentra resultados, el registro existe
      return response.residentes && response.residentes.length > 0
    } catch (error: any) {
      if (error.response?.status === 404) {
        return false // Registro no existe, está disponible
      }
      // Para otros errores, asumir que NO existe para permitir continuar
      return false
    }
  }

  /**
   * Validar datos del formulario antes de enviar
   */
  validateResidentData(data: ResidentCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar nombre del residente
    if (!data.residente_name?.trim()) {
      errors.push('El nombre del residente es requerido')
    } else if (data.residente_name.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    } else if (data.residente_name.length > 100) {
      errors.push('El nombre no puede tener más de 100 caracteres')
    }

    // Validar código del residente
    if (!data.residente_code?.trim()) {
      errors.push('El código del residente es requerido')
    } else if (data.residente_code.length < 3) {
      errors.push('El código debe tener al menos 3 caracteres')
    } else if (data.residente_code.length > 20) {
      errors.push('El código no puede tener más de 20 caracteres')
    }

    // Validar email
    if (!data.residente_email?.trim()) {
      errors.push('El email es requerido')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.residente_email)) {
      errors.push('El email debe tener un formato válido')
    }

    // Validar registro médico
    if (!data.registro_medico?.trim()) {
      errors.push('El registro médico es requerido')
    } else if (data.registro_medico.length < 3) {
      errors.push('El registro médico debe tener al menos 3 caracteres')
    } else if (data.registro_medico.length > 50) {
      errors.push('El registro médico no puede tener más de 50 caracteres')
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
export const residentCreateService = new ResidentCreateService()
export default residentCreateService
