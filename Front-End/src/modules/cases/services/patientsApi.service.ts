import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PatientData } from '../types'

interface CreatePatientRequest {
  paciente_code: string
  nombre: string
  edad: number
  sexo: string
  entidad_info: { id: string; nombre: string }
  tipo_atencion: string
  observaciones?: string
}

interface PatientResponse {
  id: string
  nombre: string
  edad: number
  sexo: string
  entidad_info: { id: string; nombre: string }
  tipo_atencion: string
  cedula: string
  observaciones?: string
  fecha_creacion: string
  fecha_actualizacion: string
  id_casos: string[]
}

export class PatientsApiService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.PATIENTS

  async createPatient(patientData: PatientData): Promise<PatientResponse> {
    try {
      const patientRequest = this.buildPatientRequest(patientData)
      const response = await apiClient.post<PatientResponse>(this.endpoint, patientRequest)
      return response
    } catch (error: any) {
      if (error.response?.data?.detail) {
        let errorMessage = 'Error de validación: '
        if (Array.isArray(error.response.data.detail)) {
          errorMessage += error.response.data.detail.map((err: any) => {
            if (typeof err === 'object' && err !== null) {
              return err.msg || err.loc?.join('.') || JSON.stringify(err)
            }
            return String(err)
          }).join(', ')
        } else {
          errorMessage += JSON.stringify(error.response.data.detail)
        }
        throw new Error(errorMessage)
      } else if (error.response?.data?.message) {
        const message = String(error.response.data.message)
        if (message.toLowerCase().includes('duplicad') || message.toLowerCase().includes('ya existe') || message.toLowerCase().includes('repetid')) {
          throw new Error('Ya existe un paciente con este número de identificación')
        }
        throw new Error(message)
      } else if (error.response?.status === 409) {
        throw new Error('Ya existe un paciente con este número de identificación')
      } else if (error.response?.status === 400) {
        throw new Error('Datos del paciente inválidos')
      } else if (error.response?.status === 422) {
        throw new Error('Error de validación en los datos del paciente')
      } else if (error.response?.status === 500) {
        const errorText = error.message || 'Error interno del servidor'
        if (errorText.toLowerCase().includes('duplicad') || errorText.toLowerCase().includes('ya existe') || errorText.toLowerCase().includes('repetid')) {
          throw new Error('Ya existe un paciente con este número de identificación')
        }
        throw new Error('Error interno del servidor al registrar el paciente')
      } else {
        throw new Error(error.message || 'Error interno del servidor al registrar el paciente')
      }
    }
  }

  async getPatientByCedula(cedula: string): Promise<PatientResponse | null> {
    try {
      const response = await apiClient.get<PatientResponse>(`${this.endpoint}/codigo/${cedula}`)
      return response
    } catch (error: any) {
      if (error.response?.status === 404) return null
      throw new Error(`Error al buscar paciente: ${error.message}`)
    }
  }

  async updatePatient(cedula: string, patientData: any): Promise<PatientResponse> {
    try {
      const patientRequest = patientData.pacienteCode ? this.buildPatientRequest(patientData) : patientData
      const response = await apiClient.put<PatientResponse>(`${this.endpoint}/${cedula}`, patientRequest)
      return response
    } catch (error: any) {
      if (error.response?.data?.detail) {
        let errorMessage = 'Error de validación: '
        if (Array.isArray(error.response.data.detail)) {
          errorMessage += error.response.data.detail.map((err: any) => {
            if (typeof err === 'object' && err !== null) {
              return err.msg || err.loc?.join('.') || JSON.stringify(err)
            }
            return String(err)
          }).join(', ')
        } else {
          errorMessage += JSON.stringify(error.response.data.detail)
        }
        throw new Error(errorMessage)
      } else if (error.response?.data?.message) {
        throw new Error(error.response.data.message)
      } else {
        throw new Error(error.message || `Error al actualizar el paciente con cédula ${cedula}`)
      }
    }
  }

  async checkPatientExists(cedula: string): Promise<boolean> {
    try {
      const patient = await this.getPatientByCedula(cedula)
      return patient !== null
    } catch (error) {
      return false
    }
  }

  validatePatientData(patientData: PatientData): { isValid: boolean; errors: string[] } {
    const errors: string[] = []

    if (!patientData.pacienteCode || patientData.pacienteCode.length < 6 || patientData.pacienteCode.length > 10) {
      errors.push('La cédula debe tener entre 6 y 10 dígitos')
    }

    if (!patientData.nombrePaciente || patientData.nombrePaciente.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    }

    const edad = parseInt(patientData.edad)
    if (!edad || edad < 0 || edad > 150) {
      errors.push('La edad debe ser un número válido entre 0 y 150')
    }

    if (!patientData.sexo) errors.push('Debe seleccionar el sexo del paciente')
    if (!patientData.entidad) errors.push('Debe seleccionar una entidad de salud')
    if (!patientData.tipoAtencion) errors.push('Debe seleccionar el tipo de atención')

    return { isValid: errors.length === 0, errors }
  }

  private buildPatientRequest(patientData: PatientData): CreatePatientRequest {
    return {
      paciente_code: patientData.pacienteCode,
      nombre: patientData.nombrePaciente,
      edad: parseInt(patientData.edad),
      sexo: patientData.sexo,
      entidad_info: {
        id: patientData.entidadCodigo || this.extractEntityId(patientData.entidad),
        nombre: patientData.entidad
      },
      tipo_atencion: patientData.tipoAtencion,
      observaciones: patientData.observaciones || undefined
    }
  }

  private extractEntityId(entityName: string): string {
    const entityMap: Record<string, string> = {
      'EPS Sanitas': 'ent_001', 'Sura': 'ent_002', 'Nueva EPS': 'ent_003',
      'Compensar': 'ent_004', 'Particular': 'ent_999'
    }
    
    return entityMap[entityName] || 'ent_001'
  }
}

export const patientsApiService = new PatientsApiService()
export default patientsApiService
