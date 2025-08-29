import { ref, reactive } from 'vue'
import { patientsApiService } from '../services/patientsApi.service'
import type { PatientData } from '../types'

export function usePatientAPI() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)
  const stats = reactive({ totalCreated: 0, lastCreatedId: null as string | null })

  async function createPatient(patientData: PatientData) {
    isLoading.value = true
    error.value = null
    success.value = false

    try {
      const validation = validatePatientData(patientData)
      if (!validation.isValid) throw new Error(validation.errors.join(', '))

      const newPatient = await patientsApiService.createPatient(patientData)
      updateStats(newPatient.id)
      success.value = true

      return {
        success: true,
        patient: newPatient,
        message: `Paciente ${newPatient.nombre} registrado exitosamente`
      }
    } catch (err: any) {
      const errorMessage = err.message || 'Error desconocido al crear el paciente'
      if (errorMessage.toLowerCase().includes('duplicad') || errorMessage.toLowerCase().includes('ya existe') || errorMessage.toLowerCase().includes('repetid')) {
        error.value = 'Ya existe un paciente con este documento de identidad'
        return { success: false, patient: null, message: 'Ya existe un paciente con este documento de identidad' }
      }
      error.value = errorMessage
      return { success: false, patient: null, message: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  async function findPatientByCedula(cedula: string) {
    isLoading.value = true
    error.value = null

    try {
      const patient = await patientsApiService.getPatientByCedula(cedula)
      return { success: true, patient, found: patient !== null }
    } catch (err: any) {
      error.value = err.message || 'Error al buscar el paciente'
      return { success: false, patient: null, found: false }
    } finally {
      isLoading.value = false
    }
  }

  async function checkPatientExists(cedula: string): Promise<boolean> {
    try {
      return await patientsApiService.checkPatientExists(cedula)
    } catch {
      return false
    }
  }

  function validatePatientData(patientData: PatientData) {
    return patientsApiService.validatePatientData(patientData)
  }

  function updateStats(patientId: string): void {
    stats.totalCreated++
    stats.lastCreatedId = patientId
  }

  function clearState(): void {
    error.value = null
    success.value = false
    isLoading.value = false
  }

  function resetStats(): void {
    stats.totalCreated = 0
    stats.lastCreatedId = null
  }

  return {
    isLoading, error, success, stats, createPatient, findPatientByCedula,
    checkPatientExists, validatePatientData, clearState, resetStats
  }
}
