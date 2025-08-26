import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { 
  PathologistCreateRequest, 
  PathologistCreateResponse,
  UserCreateRequest,
  UserCreateResponse 
} from '../types/pathologist.types'

/**
 * Servicio para la creación y gestión de patólogos
 */
class PathologistCreateService {
  private readonly pathologistEndpoint = API_CONFIG.ENDPOINTS.PATHOLOGISTS
  private readonly authEndpoint = API_CONFIG.ENDPOINTS.AUTH

  /**
   * Crear un nuevo patólogo (solo colección patólogos por ahora)
   */
  async createPathologist(pathologistData: PathologistCreateRequest): Promise<PathologistCreateResponse> {
    try {
      // Crear el patólogo en la colección patólogos
      const response = await apiClient.post<PathologistCreateResponse>(
        `${this.pathologistEndpoint}/`,
        pathologistData
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
          throw new Error('Ya existe un patólogo con este email')
        } else if (error.message?.includes('código') || error.message?.includes('code')) {
          throw new Error('Ya existe un patólogo con este código')
        } else if (error.message?.includes('registro')) {
          throw new Error('Ya existe un patólogo con este registro médico')
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
              case 'patologoCode':
                fieldName = 'Código del patólogo'
                break
              case 'patologoName':
                fieldName = 'Nombre del patólogo'
                break
              case 'PatologoEmail':
                fieldName = 'Email'
                break
              case 'registro_medico':
                fieldName = 'Registro médico'
                break
              case 'InicialesPatologo':
                fieldName = 'Iniciales'
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
        throw new Error(error.message || 'Error al crear el patólogo')
      }
    }
  }

  /**
   * Verificar si un código de patólogo ya existe
   */
  async checkCodeExists(patologoCode: string): Promise<boolean> {
    try {
      await apiClient.get(`${this.pathologistEndpoint}/${patologoCode}`)
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
   * Verificar si un email ya existe (usando búsqueda de patólogos)
   */
  async checkEmailExists(email: string): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.pathologistEndpoint}/search?q=${email}`)
      // Si encuentra resultados, el email existe
      return response.patologos && response.patologos.length > 0
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
      const response = await apiClient.get(`${this.pathologistEndpoint}/search?q=${registro_medico}`)
      // Si encuentra resultados, el registro existe
      return response.patologos && response.patologos.length > 0
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
  validatePathologistData(data: PathologistCreateRequest): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    // Validar nombre del patólogo
    if (!data.patologoName?.trim()) {
      errors.push('El nombre del patólogo es requerido')
    } else if (data.patologoName.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    } else if (data.patologoName.length > 200) {
      errors.push('El nombre no puede tener más de 200 caracteres')
    }

    // Validar iniciales
    if (!data.InicialesPatologo?.trim()) {
      errors.push('Las iniciales son requeridas')
    } else if (data.InicialesPatologo.length < 2) {
      errors.push('Las iniciales deben tener al menos 2 caracteres')
    } else if (data.InicialesPatologo.length > 10) {
      errors.push('Las iniciales no pueden tener más de 10 caracteres')
    }

    // Validar código del patólogo
    if (!data.patologoCode?.trim()) {
      errors.push('El código del patólogo es requerido')
    } else if (data.patologoCode.length < 6) {
      errors.push('El código debe tener al menos 6 caracteres')
    } else if (data.patologoCode.length > 10) {
      errors.push('El código no puede tener más de 10 caracteres')
    }

    // Validar email
    if (!data.PatologoEmail?.trim()) {
      errors.push('El email es requerido')
    } else if (!/^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(data.PatologoEmail)) {
      errors.push('El email debe tener un formato válido')
    }

    // Validar registro médico
    if (!data.registro_medico?.trim()) {
      errors.push('El registro médico es requerido')
    } else if (data.registro_medico.length < 5) {
      errors.push('El registro médico debe tener al menos 5 caracteres')
    } else if (data.registro_medico.length > 50) {
      errors.push('El registro médico no puede tener más de 50 caracteres')
    }

    // La contraseña será validada en el frontend

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
export const pathologistCreateService = new PathologistCreateService()
export default pathologistCreateService
