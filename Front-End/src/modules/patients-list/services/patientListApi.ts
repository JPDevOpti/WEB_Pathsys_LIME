import { apiClient } from '../../../core/config/axios.config'
import { API_CONFIG } from '../../../core/config/api.config'
import type { PatientFilters, IdentificationType } from '../types/patient.types'
import { casesApiService } from '../../cases/services/casesApi.service'

const PATIENTS_BASE = '/patients'

export interface BackendPatient {
  id?: string
  _id?: string | { $oid: string }
  patient_code: string
  identification_type: number
  identification_number: string
  first_name: string
  second_name?: string
  first_lastname: string
  second_lastname?: string
  birth_date: string
  gender: 'Masculino' | 'Femenino'
  location: {
    municipality_code: string
    municipality_name: string
    subregion: string
    address?: string
  }
  entity_info: {
    id: string
    name: string
  }
  care_type: 'Ambulatorio' | 'Hospitalizado'
  observations?: string
  created_at: string
  updated_at: string
}

export interface BackendEntity {
  id: string
  name: string
  code?: string
  isActive?: boolean
}

export async function searchPatients(params: Partial<PatientFilters> = {}): Promise<{ patients: BackendPatient[], total: number }> {
  try {
    const toISO = (v?: string) => {
      if (!v) return v
      const m = /^([0-3]\d)\/(0\d|1[0-2])\/(\d{4})$/.exec(v)
      return m ? `${m[3]}-${m[2]}-${m[1]}` : v
    }
    const queryParams: Record<string, any> = {
      skip: params.skip || 0,
      limit: params.limit || 100
    }

    if (params.search) queryParams.search = params.search
    if (params.identification_type) queryParams.identification_type = params.identification_type
    if (params.identification_number) queryParams.identification_number = params.identification_number
    if (params.first_name) queryParams.first_name = params.first_name
    if (params.first_lastname) queryParams.first_lastname = params.first_lastname
    if (params.birth_date_from) queryParams.birth_date_from = toISO(params.birth_date_from)
    if (params.birth_date_to) queryParams.birth_date_to = toISO(params.birth_date_to)
    if (params.municipality_code) queryParams.municipality_code = params.municipality_code
    if (params.municipality_name) queryParams.municipality_name = params.municipality_name
    if (params.subregion) queryParams.subregion = params.subregion
    if (params.age_min) queryParams.age_min = params.age_min
    if (params.age_max) queryParams.age_max = params.age_max
    if (params.entity) queryParams.entity = params.entity
    if (params.gender) queryParams.gender = params.gender
    if (params.care_type) queryParams.care_type = params.care_type
    if (params.date_from) queryParams.date_from = toISO(params.date_from)
    if (params.date_to) queryParams.date_to = toISO(params.date_to)

    const data = await apiClient.get(`${PATIENTS_BASE}/search`, { params: queryParams }) as any

    const patients: BackendPatient[] = Array.isArray(data?.patients) ? data.patients : []
    const total: number = typeof data?.total === 'number' ? data.total : 0

    return { patients, total }
  } catch (error: any) {
    console.error('Error al buscar pacientes:', error)
    throw error
  }
}

export async function getTotalPatients(): Promise<number> {
  try {
    const response = await apiClient.get(`${PATIENTS_BASE}/count`)
    return response.data?.total || 0
  } catch (error) {
    console.error('Error al obtener total de pacientes:', error)
    return 0
  }
}

export async function getPatientByCode(patientCode: string): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.get(`${PATIENTS_BASE}/${patientCode}`)
    return response.data || null
  } catch (error) {
    console.error('Error al obtener paciente:', error)
    return null
  }
}

export async function getPatientCases(patientCode: string): Promise<any[]> {
  try {
    const cases = await casesApiService.getCasesByPatient(patientCode)
    return cases || []
  } catch (error) {
    console.error('Error al obtener casos del paciente:', error)
    return []
  }
}

export async function createPatient(patientData: Partial<BackendPatient>): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.post(PATIENTS_BASE, patientData)
    return response.data || null
  } catch (error) {
    console.error('Error al crear paciente:', error)
    throw error
  }
}

export async function updatePatient(patientCode: string, patientData: Partial<BackendPatient>): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.put(`${PATIENTS_BASE}/${patientCode}`, patientData)
    return response.data || null
  } catch (error) {
    console.error('Error al actualizar paciente:', error)
    throw error
  }
}

export async function changePatientIdentification(
  patientCode: string,
  newIdentificationType: IdentificationType,
  newIdentificationNumber: string
): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.put(
      `${PATIENTS_BASE}/${patientCode}/change-identification`,
      null,
      {
        params: {
          new_identification_type: newIdentificationType,
          new_identification_number: newIdentificationNumber
        }
      }
    )
    return response.data || null
  } catch (error) {
    console.error('Error al cambiar identificación:', error)
    throw error
  }
}

export async function deletePatient(patientCode: string): Promise<boolean> {
  try {
    await apiClient.delete(`${PATIENTS_BASE}/${patientCode}`)
    return true
  } catch (error) {
    console.error('Error al eliminar paciente:', error)
    throw error
  }
}

export async function listEntities(): Promise<BackendEntity[]> {
  try {
    const response = await apiClient.get(`${API_CONFIG.VERSION}/entities`)
    return response.data?.data || response.data || []
  } catch (error) {
    console.error('Error al listar entidades:', error)
    return []
  }
}
