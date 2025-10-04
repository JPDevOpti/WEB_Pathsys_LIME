import { ref } from 'vue'
import type { PatientFormData, CreatePatientRequest, UpdatePatientRequest, PatientData, IdentificationType, Gender, CareType } from '../types'
import patientsApiService from '../services/patientsApi.service'

export function usePatientAPI() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const createPatient = async (formData: PatientFormData): Promise<PatientData | null> => {
    isLoading.value = true
    error.value = null

    try {
      const request: CreatePatientRequest = {
        identification_type: formData.identification_type as IdentificationType,
        identification_number: formData.identification_number,
        first_name: formData.first_name,
        second_name: formData.second_name || undefined,
        first_lastname: formData.first_lastname,
        second_lastname: formData.second_lastname || undefined,
        birth_date: formData.birth_date,
        gender: formData.gender as Gender,
        location: {
          municipality_code: formData.municipality_code,
          municipality_name: formData.municipality_name,
          subregion: formData.subregion,
          address: formData.address
        },
        entity_info: {
          id: formData.entity_id,
          name: formData.entity_name
        },
        care_type: formData.care_type as CareType,
        observations: formData.observations || undefined
      }

      const response = await patientsApiService.createPatient(request)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error al crear el paciente'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const updatePatient = async (patientCode: string, formData: PatientFormData): Promise<PatientData | null> => {
    isLoading.value = true
    error.value = null

    try {
      const request: UpdatePatientRequest = {
        first_name: formData.first_name,
        second_name: formData.second_name || undefined,
        first_lastname: formData.first_lastname,
        second_lastname: formData.second_lastname || undefined,
        birth_date: formData.birth_date,
        gender: formData.gender ? formData.gender as Gender : undefined,
        location: {
          municipality_code: formData.municipality_code,
          municipality_name: formData.municipality_name,
          subregion: formData.subregion,
          address: formData.address
        },
        entity_info: {
          id: formData.entity_id,
          name: formData.entity_name
        },
        care_type: formData.care_type ? formData.care_type as CareType : undefined,
        observations: formData.observations || undefined
      }

      const response = await patientsApiService.updatePatient(patientCode, request)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error al actualizar el paciente'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const getPatientByCode = async (patientCode: string): Promise<PatientData | null> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await patientsApiService.getPatientByCode(patientCode)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error al obtener el paciente'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const listPatients = async (params: any = {}): Promise<PatientData[] | null> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await patientsApiService.listPatients(params)
      return response.data
    } catch (err: any) {
      error.value = err.message || 'Error al obtener los pacientes'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const searchPatients = async (query: string, limit: number = 10): Promise<PatientData[] | null> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await patientsApiService.searchPatients(query, limit)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error al buscar pacientes'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const advancedSearch = async (params: any): Promise<any | null> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await patientsApiService.advancedSearch(params)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error en la búsqueda avanzada'
      return null
    } finally {
      isLoading.value = false
    }
  }

  const checkPatientExists = async (identificationType: IdentificationType, identificationNumber: string): Promise<boolean> => {
    isLoading.value = true
    error.value = null

    try {
      const response = await patientsApiService.checkPatientExists(identificationType, identificationNumber)
      return response
    } catch (err: any) {
      error.value = err.message || 'Error al verificar existencia del paciente'
      return false
    } finally {
      isLoading.value = false
    }
  }

  return {
    isLoading,
    error,
    createPatient,
    updatePatient,
    getPatientByCode,
    listPatients,
    searchPatients,
    advancedSearch,
    checkPatientExists
  }
}

