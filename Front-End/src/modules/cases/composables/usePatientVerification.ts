import { ref } from 'vue'
import { patientsApiService } from '../services'
import type { PatientData } from '../types'

export function usePatientVerification() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const isSearching = ref(false)
  const searchError = ref('')
  const patientVerified = ref(false)
  const verifiedPatient = ref<PatientData | null>(null)

  // ============================================================================
  // FUNCIONES DE TRANSFORMACIÓN
  // ============================================================================

  /**
   * Transforma la respuesta de la API al formato del formulario
   * @param apiPatient - Datos del paciente desde la API
   * @returns Datos del paciente en formato del formulario
   */
  const transformApiPatientToFormData = (apiPatient: any): PatientData => {
    const tipoAtencionApi: string = apiPatient.tipo_atencion || ''
    const tipoAtencionForm = (() => {
      const v = String(tipoAtencionApi).toLowerCase()
      if (v.includes('ambulator')) return 'ambulatorio'
      if (v.includes('hospital')) return 'hospitalizado'
      return ''
    })()
    const entidadCodigo = apiPatient.entidad_info?.codigo || apiPatient.entidad_info?.id
    return {
      numeroCedula: apiPatient.cedula,
      nombrePaciente: apiPatient.nombre,
      sexo: apiPatient.sexo.toLowerCase(),
      edad: apiPatient.edad.toString(),
      entidad: apiPatient.entidad_info?.nombre || 'Sin entidad',
      entidadCodigo,
      tipoAtencion: tipoAtencionForm as any,
      observaciones: apiPatient.observaciones,
      codigo: apiPatient.id
    }
  }

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Busca un paciente por número de cédula
   * @param cedula - Número de cédula del paciente
   * @returns Resultado de la búsqueda
   */
  const searchPatientByCedula = async (cedula: string) => {
    if (!cedula.trim()) {
      searchError.value = 'La cédula es obligatoria'
      return { found: false }
    }

    isSearching.value = true
    searchError.value = ''
    
    try {
  
      
      const apiPatient = await patientsApiService.getPatientByCedula(cedula)
      
      if (apiPatient) {
        return handlePatientFound(apiPatient)
      } else {
        return handlePatientNotFound()
      }
      
    } catch (error: any) {
      return handleSearchError(error)
    } finally {
      isSearching.value = false
    }
  }

  /**
   * Usa un paciente recién creado para la verificación
   * @param patientData - Datos del paciente creado
   */
  const useNewPatient = (patientData: PatientData): void => {
    
    verifiedPatient.value = patientData
    patientVerified.value = true
  }

  /**
   * Limpia el estado de verificación
   */
  const clearVerification = (): void => {
    patientVerified.value = false
    verifiedPatient.value = null
    searchError.value = ''
    isSearching.value = false
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Maneja el caso cuando se encuentra un paciente
   * @param apiPatient - Datos del paciente desde la API
   * @returns Resultado de la búsqueda exitosa
   */
  const handlePatientFound = (apiPatient: any) => {
    const patientData = transformApiPatientToFormData(apiPatient)
    
    verifiedPatient.value = patientData
    patientVerified.value = true
    
    
    
    return {
      found: true,
      patient: patientData
    }
  }

  /**
   * Maneja el caso cuando no se encuentra un paciente
   * @returns Resultado de la búsqueda fallida
   */
  const handlePatientNotFound = () => {
    searchError.value = 'Paciente no encontrado en el sistema'
    patientVerified.value = false
    verifiedPatient.value = null
    
    return {
      found: false,
      message: 'Paciente no encontrado'
    }
  }

  /**
   * Maneja errores durante la búsqueda
   * @param error - Error capturado
   * @returns Resultado de la búsqueda con error
   */
  const handleSearchError = (error: any) => {
    
    searchError.value = error.message || 'Error al buscar el paciente'
    patientVerified.value = false
    verifiedPatient.value = null
    
    return {
      found: false,
      error: searchError.value
    }
  }

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    isSearching,
    searchError,
    patientVerified,
    verifiedPatient,
    
    // Métodos
    searchPatientByCedula,
    useNewPatient,
    clearVerification
  }
}
