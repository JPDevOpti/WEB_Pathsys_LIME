import { apiClient } from '../../../core/config/axios.config'
import { API_CONFIG } from '../../../core/config/api.config'
import type { PatientFilters, IdentificationType } from '../types/patient.types'

const PATIENTS_BASE = '/patients'

// Interfaz del backend (PatientResponse según documentación)
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

/**
 * Listar pacientes con filtros básicos
 * GET /api/v1/patients/
 */
export async function listPatients(params: Partial<PatientFilters> = {}): Promise<BackendPatient[]> {
  try {
    const queryParams: Record<string, any> = {
      skip: params.skip || 0,
      limit: params.limit || 100
    }
    
    if (params.search) queryParams.search = params.search
    if (params.entity) queryParams.entity = params.entity
    if (params.gender) queryParams.gender = params.gender
    if (params.care_type) queryParams.care_type = params.care_type
    
    const url = PATIENTS_BASE
    console.log('🌐 [API] GET', url)
    console.log('📝 [API] Query params:', queryParams)
    
    const response = await apiClient.get(PATIENTS_BASE, { params: queryParams })
    
    console.log('✅ [API] Respuesta completa recibida:', response)
    console.log('📦 [API] response.data:', response.data)
    console.log('� [API] typeof response:', typeof response)
    console.log('🔍 [API] Array.isArray(response):', Array.isArray(response))
    console.log('🔍 [API] Array.isArray(response.data):', Array.isArray(response.data))
    
    // Si response es directamente un array (sin .data), usarlo directamente
    let patients: BackendPatient[] = []
    
    if (Array.isArray(response)) {
      console.log('⚠️ [API] response es directamente un array!')
      patients = response
    } else if (Array.isArray(response.data)) {
      console.log('✅ [API] response.data es un array')
      patients = response.data
    } else if (response.data?.patients) {
      console.log('✅ [API] response.data.patients existe')
      patients = response.data.patients
    } else {
      console.log('⚠️ [API] No se pudo extraer pacientes de la respuesta')
    }
    
    console.log('👥 [API] Pacientes extraídos:', patients.length, 'items')
    if (patients.length > 0) {
      console.log('👤 [API] Primer paciente:', patients[0])
    }
    
    return patients
  } catch (error: any) {
    console.error('Error al listar pacientes:', error)
    throw error
  }
}

/**
 * Búsqueda avanzada de pacientes
 * GET /api/v1/patients/search/advanced
 */
export async function searchPatientsAdvanced(params: Partial<PatientFilters> = {}): Promise<{ patients: BackendPatient[], total: number }> {
  try {
    const queryParams: Record<string, any> = {
      skip: params.skip || 0,
      limit: params.limit || 100
    }
    
    // Búsqueda general (nombre o identificación)
    if (params.search) queryParams.search = params.search
    
    // Filtros de ubicación
    if (params.municipality_code) queryParams.municipality_code = params.municipality_code
    if (params.municipality_name) queryParams.municipality_name = params.municipality_name
    if (params.subregion) queryParams.subregion = params.subregion
    
    // Filtros de entidad y atención
    if (params.entity) queryParams.entity = params.entity
    if (params.gender) queryParams.gender = params.gender
    if (params.care_type) queryParams.care_type = params.care_type
    
    // Filtros de fecha de creación
    if (params.date_from) queryParams.date_from = params.date_from
    if (params.date_to) queryParams.date_to = params.date_to
    
    const url = `${PATIENTS_BASE}/search/advanced`
    console.log('🌐 [API] GET', url)
    console.log('📝 [API] Query params:', queryParams)
    
    const response = await apiClient.get(url, { params: queryParams })
    
    console.log('✅ [API] Respuesta búsqueda avanzada completa:', response)
    console.log('📦 [API] response.data:', response.data)
    console.log('� [API] typeof response:', typeof response)
    console.log('🔍 [API] Array.isArray(response):', Array.isArray(response))
    
    let result: { patients: BackendPatient[], total: number }
    
    if (Array.isArray(response)) {
      console.log('⚠️ [API] response es directamente un array en búsqueda avanzada')
      result = {
        patients: response,
        total: response.length
      }
    } else if (response.data) {
      console.log('✅ [API] response.data existe')
      result = {
        patients: response.data?.patients || response.data || [],
        total: response.data?.total || (Array.isArray(response.data) ? response.data.length : 0)
      }
    } else {
      console.log('⚠️ [API] No se pudo extraer datos de búsqueda avanzada')
      result = { patients: [], total: 0 }
    }
    
    console.log('👥 [API] Pacientes encontrados:', result.patients.length)
    console.log('📊 [API] Total:', result.total)
    if (result.patients.length > 0) {
      console.log('👤 [API] Primer paciente búsqueda avanzada:', result.patients[0])
    }
    
    return result
  } catch (error: any) {
    console.error('Error en búsqueda avanzada:', error)
    return { patients: [], total: 0 }
  }
}

/**
 * Obtener total de pacientes
 * GET /api/v1/patients/count
 */
export async function getTotalPatients(): Promise<number> {
  try {
    const response = await apiClient.get(`${PATIENTS_BASE}/count`)
    return response.data?.total || 0
  } catch (error) {
    console.error('Error al obtener total de pacientes:', error)
    return 0
  }
}

/**
 * Obtener un paciente por código
 * GET /api/v1/patients/{patient_code}
 */
export async function getPatientByCode(patientCode: string): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.get(`${PATIENTS_BASE}/${patientCode}`)
    return response.data || null
  } catch (error) {
    console.error('Error al obtener paciente:', error)
    return null
  }
}

/**
 * Obtener casos de un paciente
 * Nota: Este endpoint debe existir en el backend
 */
export async function getPatientCases(patientCode: string): Promise<any[]> {
  try {
    const response = await apiClient.get(`${PATIENTS_BASE}/${patientCode}/cases`)
    return response.data || []
  } catch (error) {
    console.error('Error al obtener casos del paciente:', error)
    return []
  }
}

/**
 * Crear un nuevo paciente
 * POST /api/v1/patients/
 */
export async function createPatient(patientData: Partial<BackendPatient>): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.post(PATIENTS_BASE, patientData)
    return response.data || null
  } catch (error) {
    console.error('Error al crear paciente:', error)
    throw error
  }
}

/**
 * Actualizar un paciente
 * PUT /api/v1/patients/{patient_code}
 */
export async function updatePatient(patientCode: string, patientData: Partial<BackendPatient>): Promise<BackendPatient | null> {
  try {
    const response = await apiClient.put(`${PATIENTS_BASE}/${patientCode}`, patientData)
    return response.data || null
  } catch (error) {
    console.error('Error al actualizar paciente:', error)
    throw error
  }
}

/**
 * Cambiar identificación de un paciente
 * PUT /api/v1/patients/{patient_code}/change-identification
 */
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

/**
 * Eliminar un paciente
 * DELETE /api/v1/patients/{patient_code}
 */
export async function deletePatient(patientCode: string): Promise<boolean> {
  try {
    await apiClient.delete(`${PATIENTS_BASE}/${patientCode}`)
    return true
  } catch (error) {
    console.error('Error al eliminar paciente:', error)
    throw error
  }
}

/**
 * Listar entidades (endpoint auxiliar)
 */
export async function listEntities(): Promise<BackendEntity[]> {
  try {
    const response = await apiClient.get(`${API_CONFIG.VERSION}/entities`)
    return response.data?.data || response.data || []
  } catch (error) {
    console.error('Error al listar entidades:', error)
    return []
  }
}
