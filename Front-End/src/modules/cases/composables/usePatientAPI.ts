// Patient API composable: create patient, track minimal status/stats
import { ref, reactive } from 'vue'
import { patientsApiService } from '../services/patientsApi.service'
import type { PatientData } from '../types'

export function usePatientAPI() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)
  const stats = reactive({ totalCreated: 0, lastCreatedId: null as string | null })

  // Validate and send creation request
  async function createPatient(patientData: any) {
    isLoading.value = true
    error.value = null
    success.value = false

    try {
      // LOG: Datos que llegan al createPatient
      console.log('🔍 [LOG usePatientAPI] patientData recibido:', JSON.stringify(patientData, null, 2))
      
      const validation = patientsApiService.validatePatientData(patientData)
      console.log('🔍 [LOG usePatientAPI] validation result:', JSON.stringify(validation, null, 2))
      
      if (!validation.isValid) throw new Error(validation.errors.join(', '))

      const newPatient = await patientsApiService.createPatient(patientData)
      console.log('🔍 [LOG usePatientAPI] newPatient creado:', JSON.stringify(newPatient, null, 2))
      
      updateStats(newPatient.id)
      success.value = true

      return {
        success: true,
        patient: newPatient,
        message: `Paciente ${newPatient.nombre} registrado exitosamente`
      }
    } catch (err: any) {
      console.error('❌ [ERROR usePatientAPI] Error al crear paciente:', err)
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
