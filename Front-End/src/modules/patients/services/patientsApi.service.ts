import axios from 'axios'
import { API_CONFIG, buildApiUrl } from '@/core/config/api.config'
import type { 
  PatientData, 
  CreatePatientRequest, 
  UpdatePatientRequest,
  PatientSearchResult,
  PatientCountResponse,
  IdentificationType
} from '../types'
import type { 
  PaginatedResponse, 
  PatientListParams, 
  AdvancedSearchParams 
} from '../types/api'

class PatientsApiService {
  private baseURL = buildApiUrl(API_CONFIG.ENDPOINTS.PATIENTS)

  /**
   * Crear un nuevo paciente
   */
  async createPatient(patientData: CreatePatientRequest): Promise<PatientData> {
    try {
      console.debug('➡️ [patients:create] POST', `${this.baseURL}/`, { payload: patientData })
      const response = await axios.post(`${this.baseURL}/`, patientData)
      console.debug('✅ [patients:create] Response', { status: response.status, data: response.data })
      return response.data
    } catch (error: any) {
      const detail = error?.response?.data?.detail || error?.message || 'Error al crear el paciente'
      console.error('🛑 [patients:create] Error', { status: error?.response?.status, detail, data: error?.response?.data })
      // Reemitir el error original para conservar `response.data.errors` y otros metadatos
      ;(error as any).__normalizedMessage = detail
      throw error
    }
  }

  /**
   * Obtener lista de pacientes con filtros y paginación
   */
  async listPatients(params: PatientListParams = {}): Promise<PaginatedResponse<PatientData>> {
    try {
      const response = await axios.get(`${this.baseURL}/`, { params })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al obtener los pacientes')
    }
  }

  /**
   * Obtener paciente por código
   */
  async getPatientByCode(patientCode: string): Promise<PatientData> {
    try {
      const response = await axios.get(`${this.baseURL}/${encodeURIComponent(patientCode)}`)
      return response.data
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error(`Paciente con código ${patientCode} no encontrado`)
      }
      throw new Error(error.response?.data?.detail || error.message || 'Error al buscar el paciente')
    }
  }

  /**
   * Actualizar paciente
   */
  async updatePatient(patientCode: string, patientData: UpdatePatientRequest): Promise<PatientData> {
    try {
      const response = await axios.put(`${this.baseURL}/${patientCode}`, patientData)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al actualizar el paciente')
    }
  }

  /**
   * Cambiar identificación del paciente
   */
  async changeIdentification(
    patientCode: string, 
    newIdentificationType: IdentificationType, 
    newIdentificationNumber: string
  ): Promise<PatientData> {
    try {
      const response = await axios.put(
        `${this.baseURL}/${patientCode}/change-identification`,
        null,
        { 
          params: { 
            new_identification_type: newIdentificationType,
            new_identification_number: newIdentificationNumber
          } 
        }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al cambiar la identificación del paciente')
    }
  }

  /**
   * Eliminar paciente
   */
  async deletePatient(patientCode: string): Promise<void> {
    try {
      await axios.delete(`${this.baseURL}/${patientCode}`)
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al eliminar el paciente')
    }
  }

  /**
   * Búsqueda avanzada de pacientes
   */
  async advancedSearch(params: AdvancedSearchParams): Promise<PaginatedResponse<PatientSearchResult>> {
    try {
      const response = await axios.get(`${this.baseURL}/search/advanced`, { params })
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error en la búsqueda avanzada')
    }
  }

  /**
   * Contar total de pacientes
   */
  async countPatients(): Promise<PatientCountResponse> {
    try {
      const response = await axios.get(`${this.baseURL}/count`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al contar pacientes')
    }
  }

  /**
   * Búsqueda simple por texto
   */
  async searchPatients(query: string, limit: number = 10): Promise<PatientData[]> {
    try {
      const response = await axios.get(`${this.baseURL}/search`, {
        params: { search: query, limit }
      })
      // El backend devuelve { patients, total, skip, limit }
      return (response.data?.patients as PatientData[]) || []
    } catch (error: any) {
      throw new Error(error.response?.data?.detail || error.message || 'Error al buscar pacientes')
    }
  }

  /**
   * Obtener paciente por documento (identification_number)
   */
  async getPatientByDocumento(documento: string): Promise<PatientData | null> {
    try {
      const response = await axios.get(`${this.baseURL}/search`, {
        params: { identification_number: documento, limit: 1 }
      })
      const list = (response.data?.patients as PatientData[]) || []
      return list.length ? list[0] : null
    } catch (error: any) {
      if (error.response?.status === 404) return null
      throw new Error(error.response?.data?.detail || error.message || 'Error al buscar por documento')
    }
  }

  /**
   * Verificar si existe un paciente con la identificación dada
   */
  async checkPatientExists(identificationType: IdentificationType, identificationNumber: string): Promise<boolean> {
    try {
      const response = await axios.get(`${this.baseURL}/search/advanced`, {
        params: {
          identification_type: identificationType,
          identification_number: identificationNumber,
          limit: 1
        }
      })
      return response.data.total > 0
    } catch (error: any) {
      return false
    }
  }

  /**
   * Obtener estadísticas básicas de pacientes
   */
  async getPatientStats(): Promise<{
    total: number
    by_gender: Record<string, number>
    by_care_type: Record<string, number>
    by_age_group: Record<string, number>
  }> {
    try {
      // Esta funcionalidad podría implementarse en el backend
      const [total, maleCount, femaleCount, ambulatoryCount, hospitalizedCount] = await Promise.all([
        this.countPatients(),
        this.advancedSearch({ gender: 'Masculino', limit: 0 }),
        this.advancedSearch({ gender: 'Femenino', limit: 0 }),
        this.advancedSearch({ care_type: 'Ambulatorio', limit: 0 }),
        this.advancedSearch({ care_type: 'Hospitalizado', limit: 0 })
      ])

      return {
        total: total.total,
        by_gender: {
          'Masculino': maleCount.total,
          'Femenino': femaleCount.total
        },
        by_care_type: {
          'Ambulatorio': ambulatoryCount.total,
          'Hospitalizado': hospitalizedCount.total
        },
        by_age_group: {
          // Esto requeriría consultas más específicas
          '0-18': 0,
          '19-65': 0,
          '65+': 0
        }
      }
    } catch (error: any) {
      throw new Error('Error al obtener estadísticas de pacientes')
    }
  }
}

export default new PatientsApiService()

