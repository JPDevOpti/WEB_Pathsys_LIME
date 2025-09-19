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
      return response.nombre || response.cedula || response.sexo 
        ? response 
        : this.transformToSpanishResponse(response)
    } catch (error: any) {
      if (error.response?.status === 404) {
        throw new Error(`No se encontró un paciente con el código ${documento}`)
      }
      throw new Error(`Error al buscar paciente: ${error.message}`)
    }
  }

  async createPatient(patientData: PatientData): Promise<PatientResponse> {
    try {
      const patientRequest = this.buildPatientRequest(patientData)
      const response = await apiClient.post<any>(this.endpoint, patientRequest)
      return this.transformToSpanishResponse(response)
    } catch (error: any) {
      throw this.handleApiError(error, 'registrar el paciente')
    }
  }

  async getPatientByCedula(cedula: string): Promise<PatientResponse | null> {
    try {
      return await this.getPatientByDocumento(cedula)
    } catch (error: any) {
      if (error.message?.includes('No se encontró un paciente con el código')) {
        throw new Error(`No se encontró un paciente con el código ${cedula}`)
      }
      throw error
    }
  }

  async updatePatient(cedula: string, patientData: any): Promise<PatientResponse> {
    try {
      const patientRequest = patientData.patientCode ? this.buildPatientRequest(patientData) : patientData
      const response = await apiClient.put<PatientResponse>(`${this.endpoint}/${cedula}`, patientRequest)
      return response
    } catch (error: any) {
      throw this.handleApiError(error, `actualizar el paciente con cédula ${cedula}`)
    }
  }

  async changePatientCode(currentCedula: string, newCode: string): Promise<PatientResponse> {
    try {
      const response = await apiClient.put<PatientResponse>(
        `${this.endpoint}/${currentCedula}/change-code?new_code=${encodeURIComponent(newCode)}`
      )
      return response
    } catch (error: any) {
      throw this.handleApiError(error, `cambiar el código del paciente ${currentCedula}`, 'Error al cambiar código: ')
    }
  }

  async checkPatientExists(cedula: string): Promise<boolean> {
    try {
      const patient = await this.getPatientByCedula(cedula)
      return patient !== null
    } catch {
      return false
    }
  }

  validatePatientData(patientData: PatientData): { isValid: boolean; errors: string[] } {
    const errors: string[] = []
    const validations = [
      { 
        condition: !patientData.patientCode || patientData.patientCode.length < 6 || patientData.patientCode.length > 10,
        message: 'La cédula debe tener entre 6 y 10 dígitos'
      },
      {
        condition: !patientData.name || patientData.name.length < 2,
        message: 'El nombre debe tener al menos 2 caracteres'
      },
      {
        condition: !parseInt(patientData.age) || parseInt(patientData.age) < 0 || parseInt(patientData.age) > 150,
        message: 'La edad debe ser un número válido entre 0 y 150'
      },
      { condition: !patientData.gender, message: 'Debe seleccionar el sexo del paciente' },
      { condition: !patientData.entity, message: 'Debe seleccionar una entidad de salud' },
      { condition: !patientData.careType, message: 'Debe seleccionar el tipo de atención' }
    ]

    validations.forEach(({ condition, message }) => condition && errors.push(message))
    return { isValid: errors.length === 0, errors }
  }

  private buildPatientRequest(patientData: PatientData): CreatePatientRequest {
    const requiredFields = [
      { field: patientData.patientCode, name: 'código del paciente' },
      { field: patientData.name, name: 'nombre del paciente' },
      { field: patientData.gender, name: 'sexo del paciente' },
      { field: patientData.age, name: 'edad del paciente' },
      { field: patientData.careType, name: 'tipo de atención' },
      { field: patientData.entity, name: 'entidad' }
    ]

    requiredFields.forEach(({ field, name }) => {
      if (!field || !String(field).trim()) {
        throw new Error(`El ${name} es requerido`)
      }
    })
    
    const entidadNombre = String(patientData.entity).trim()
    const entidadCodigo = String(patientData.entityCode || entidadNombre || 'UNKNOWN').trim()
    
    return {
      patient_code: String(patientData.patientCode).trim(),
      name: String(patientData.name).trim(),
      age: parseInt(String(patientData.age)),
      gender: patientData.gender === 'masculino' ? 'Masculino' : 'Femenino',
      entity_info: { id: entidadCodigo, name: entidadNombre },
      care_type: patientData.careType === 'ambulatorio' ? 'Ambulatorio' : 'Hospitalizado',
      observations: patientData.observations?.trim() || undefined
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

  private handleApiError(error: any, context: string, customPrefix: string = 'Error de validación: '): Error {
    const isDuplicateError = (message: string) => 
      ['duplicad', 'ya existe', 'repetid'].some(keyword => message.toLowerCase().includes(keyword))

    if (error.response?.data?.detail) {
      const detail = error.response.data.detail
      const errorMessage = Array.isArray(detail)
        ? detail.map(err => 
            typeof err === 'object' && err !== null
              ? err.msg || err.loc?.join('.') || JSON.stringify(err)
              : String(err)
          ).join(', ')
        : JSON.stringify(detail)
      
      return new Error(customPrefix + errorMessage)
    }

    if (error.response?.data?.message) {
      const message = String(error.response.data.message)
      return new Error(isDuplicateError(message) 
        ? 'Ya existe un paciente con este documento de identidad'
        : message)
    }

    const statusMessages = {
      400: 'Datos del paciente inválidos',
      409: 'Ya existe un paciente con este documento de identidad',
      422: 'Error de validación en los datos del paciente',
      500: 'Error interno del servidor al registrar el paciente'
    }

    const statusMessage = statusMessages[error.response?.status as keyof typeof statusMessages]
    if (statusMessage) {
      return new Error(statusMessage)
    }

    return new Error(error.message || `Error al ${context}`)
  }
}

export const patientsApiService = new PatientsApiService()
export default patientsApiService
