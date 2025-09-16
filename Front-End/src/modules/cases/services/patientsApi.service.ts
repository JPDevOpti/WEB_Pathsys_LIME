import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PatientData } from '../types'

interface CreatePatientRequest {
  patient_code: string
  name: string
  age: number
  gender: string
  entity_info: { id: string; name: string }
  care_type: string
  observations?: string
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
  async getPatientByDocumento(documento: string): Promise<PatientResponse | null> {
    try {
      const response = await apiClient.get<any>(`${this.endpoint}/${documento}`)
      // Verificar si los datos ya vienen en español o necesitan transformación
      if (response.nombre || response.cedula || response.sexo) {
        // Ya vienen en español, devolver directamente
        return response
      } else {
        // Vienen en inglés, transformar a español
        return this.transformToSpanishResponse(response)
      }
    } catch (error: any) {
      if (error.response?.status === 404) return null
      throw new Error(`Error al buscar paciente: ${error.message}`)
    }
  }

  async createPatient(patientData: PatientData): Promise<PatientResponse> {
    try {
      const patientRequest = this.buildPatientRequest(patientData)
      const response = await apiClient.post<any>(this.endpoint, patientRequest)
      return this.transformToSpanishResponse(response)
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
          throw new Error('Ya existe un paciente con este documento de identidad')
        }
        throw new Error(message)
      } else if (error.response?.status === 409) {
        throw new Error('Ya existe un paciente con este documento de identidad')
      } else if (error.response?.status === 400) {
        throw new Error('Datos del paciente inválidos')
      } else if (error.response?.status === 422) {
        throw new Error('Error de validación en los datos del paciente')
      } else if (error.response?.status === 500) {
        const errorText = error.message || 'Error interno del servidor'
        if (errorText.toLowerCase().includes('duplicad') || errorText.toLowerCase().includes('ya existe') || errorText.toLowerCase().includes('repetid')) {
          throw new Error('Ya existe un paciente con este documento de identidad')
        }
        throw new Error('Error interno del servidor al registrar el paciente')
      } else {
        throw new Error(error.message || 'Error interno del servidor al registrar el paciente')
      }
    }
  }

  async getPatientByCedula(cedula: string): Promise<PatientResponse | null> {
    // Mantener por compatibilidad en otros lugares por ahora si existiera
    return this.getPatientByDocumento(cedula)
  }

  async updatePatient(cedula: string, patientData: any): Promise<PatientResponse> {
    try {
      const patientRequest = patientData.patientCode ? this.buildPatientRequest(patientData) : patientData
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

  async changePatientCode(currentCedula: string, newCode: string): Promise<PatientResponse> {
    try {
      const response = await apiClient.put<PatientResponse>(`${this.endpoint}/${currentCedula}/change-code?new_code=${encodeURIComponent(newCode)}`)
      return response
    } catch (error: any) {
      if (error.response?.data?.detail) {
        let errorMessage = 'Error al cambiar código: '
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
        throw new Error(error.message || `Error al cambiar el código del paciente ${currentCedula}`)
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

    if (!patientData.patientCode || patientData.patientCode.length < 6 || patientData.patientCode.length > 10) {
      errors.push('La cédula debe tener entre 6 y 10 dígitos')
    }

    if (!patientData.name || patientData.name.length < 2) {
      errors.push('El nombre debe tener al menos 2 caracteres')
    }

    const edad = parseInt(patientData.age)
    if (!edad || edad < 0 || edad > 150) {
      errors.push('La edad debe ser un número válido entre 0 y 150')
    }

    if (!patientData.gender) errors.push('Debe seleccionar el sexo del paciente')
    if (!patientData.entity) errors.push('Debe seleccionar una entidad de salud')
    if (!patientData.careType) errors.push('Debe seleccionar el tipo de atención')

    return { isValid: errors.length === 0, errors }
  }

  private buildPatientRequest(patientData: PatientData): CreatePatientRequest {
    const entidadNombre = (patientData.entity || '').toString().trim() || 'UNKNOWN'
    const entidadCodigo = (patientData.entityCode || entidadNombre || 'UNKNOWN').toString().trim()
    return {
      patient_code: String(patientData.patientCode || '').trim(),
      name: String(patientData.name || '').trim(),
      age: parseInt(String(patientData.age || '0'), 10),
      gender: String(patientData.gender || '').trim() === 'masculino' ? 'Male' : 'Female',
      entity_info: { id: entidadCodigo, name: entidadNombre },
      care_type: String(patientData.careType || '').trim() === 'ambulatorio' ? 'Outpatient' : 'Inpatient',
      observations: patientData.observations?.toString().trim() || undefined
    }
  }

  private transformToSpanishResponse(api: any): PatientResponse {
    return {
      id: api.id,
      nombre: api.name,
      edad: api.age,
      sexo: api.gender === 'Male' ? 'Masculino' : 'Femenino',
      entidad_info: { id: api.entity_info?.id, nombre: api.entity_info?.name },
      tipo_atencion: api.care_type === 'Outpatient' ? 'Ambulatorio' : 'Hospitalizado',
      cedula: api.patient_code,
      observaciones: api.observations,
      fecha_creacion: api.created_at,
      fecha_actualizacion: api.updated_at,
      id_casos: []
    }
  }

}

export const patientsApiService = new PatientsApiService()
export default patientsApiService
