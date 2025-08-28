import { ref, reactive } from 'vue'
import { patientsApiService } from '../services/patientsApi.service'
import type { PatientData } from '../types'

/**
 * Composable para manejar operaciones de pacientes
 * Se enfoca ÚNICAMENTE en la colección de pacientes, NO en casos
 */
export function usePatientAPI() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const success = ref(false)

  // Estadísticas simples
  const stats = reactive({
    totalCreated: 0,
    lastCreatedId: null as string | null
  })

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Crea un nuevo paciente en la colección de pacientes
   * @param patientData - Datos del paciente a crear
   * @returns Resultado de la creación
   */
  async function createPatient(patientData: PatientData) {
    isLoading.value = true
    error.value = null
    success.value = false

    try {
      // Validar datos antes del envío
      const validation = validatePatientData(patientData)
      if (!validation.isValid) {
        throw new Error(validation.errors.join(', '))
      }

      // El backend valida automáticamente si el paciente ya existe
      // No es necesario verificar previamente

      // Crear el paciente
      const newPatient = await patientsApiService.createPatient(patientData)
      
      // Actualizar estadísticas
      updateStats(newPatient.id)

      success.value = true

      return {
        success: true,
        patient: newPatient,
        message: `Paciente ${newPatient.nombre} registrado exitosamente`
      }

    } catch (err: any) {
      error.value = err.message || 'Error desconocido al crear el paciente'
      
      return {
        success: false,
        patient: null,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Busca un paciente por cédula
   * @param cedula - Número de cédula del paciente
   * @returns Resultado de la búsqueda
   */
  async function findPatientByCedula(cedula: string) {
    isLoading.value = true
    error.value = null

    try {
      const patient = await patientsApiService.getPatientByCedula(cedula)
      
      return {
        success: true,
        patient,
        found: patient !== null
      }

    } catch (err: any) {
      error.value = err.message || 'Error al buscar el paciente'
      
      return {
        success: false,
        patient: null,
        found: false
      }
    } finally {
      isLoading.value = false
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Verifica si un paciente existe sin mostrar errores
   * @param cedula - Número de cédula a verificar
   * @returns true si el paciente existe
   */
  async function checkPatientExists(cedula: string): Promise<boolean> {
    try {
      return await patientsApiService.checkPatientExists(cedula)
    } catch (error) {
      return false
    }
  }

  /**
   * Valida datos del formulario de paciente
   * @param patientData - Datos del paciente a validar
   * @returns Resultado de la validación
   */
  function validatePatientData(patientData: PatientData) {
    return patientsApiService.validatePatientData(patientData)
  }

  /**
   * Actualiza las estadísticas del composable
   * @param patientId - ID del paciente creado
   */
  function updateStats(patientId: string): void {
    stats.totalCreated++
    stats.lastCreatedId = patientId
  }

  /**
   * Limpia el estado del composable
   */
  function clearState(): void {
    error.value = null
    success.value = false
    isLoading.value = false
  }

  /**
   * Resetea las estadísticas del composable
   */
  function resetStats(): void {
    stats.totalCreated = 0
    stats.lastCreatedId = null
  }

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    isLoading,
    error,
    success,
    stats,

    // Métodos principales
    createPatient,
    findPatientByCedula,
    checkPatientExists,

    // Utilidades
    validatePatientData,
    clearState,
    resetStats
  }
}
