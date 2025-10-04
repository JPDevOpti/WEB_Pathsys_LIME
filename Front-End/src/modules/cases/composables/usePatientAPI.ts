// Patient API composable: create patient, track minimal status/stats
import { ref, reactive } from 'vue'
import { patientsApiService } from '@/modules/patients/services'
import type { CreatePatientRequest } from '@/modules/patients/types'

export function usePatientAPI() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)
  const stats = reactive({ totalCreated: 0, lastCreatedId: null as string | null })

  // Validate and send creation request
  async function createPatient(patientData: CreatePatientRequest) {
    isLoading.value = true
    error.value = null
    success.value = false

    try {
      const newPatient = await patientsApiService.createPatient(patientData)

      const fullName = [
        newPatient.first_name,
        newPatient.second_name,
        newPatient.first_lastname,
        newPatient.second_lastname
      ].filter(Boolean).join(' ')

      updateStats(newPatient.patient_code)
      success.value = true

      return {
        success: true,
        patient: newPatient,
        message: `Paciente ${fullName} registrado exitosamente`
      }
    } catch (err: any) {
      const errorMessage = (err?.response?.data?.detail as string) || err.message || 'Error desconocido al crear el paciente'
      const lower = errorMessage.toLowerCase()
      if (lower.includes('duplicad') || lower.includes('ya existe') || lower.includes('repetid')) {
        error.value = 'Ya existe un paciente con este documento de identidad'
        return { success: false, patient: null, message: 'Ya existe un paciente con este documento de identidad' }
      }
      error.value = errorMessage
      return { success: false, patient: null, message: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Stats for UI widgets
  function updateStats(patientId: string): void {
    stats.totalCreated++
    stats.lastCreatedId = patientId
  }

  // Reset flags
  function clearState(): void { error.value = null; success.value = false; isLoading.value = false }


  return { isLoading, error, success, stats, createPatient, clearState }
}
