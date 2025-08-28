import { ref } from 'vue'
import { patientsApiService } from '../services'
import type { PatientData } from '../types'

export function usePatientVerification() {
  const isSearching = ref(false)
  const searchError = ref('')
  const patientVerified = ref(false)
  const verifiedPatient = ref<PatientData | null>(null)

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
      pacienteCode: apiPatient.paciente_code || apiPatient.cedula,
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
        const patientData = transformApiPatientToFormData(apiPatient)
        verifiedPatient.value = patientData
        patientVerified.value = true
        return { found: true, patient: patientData }
      } else {
        searchError.value = 'Paciente no encontrado en el sistema'
        patientVerified.value = false
        verifiedPatient.value = null
        return { found: false, message: 'Paciente no encontrado' }
      }
    } catch (error: any) {
      searchError.value = error.message || 'Error al buscar el paciente'
      patientVerified.value = false
      verifiedPatient.value = null
      return { found: false, error: searchError.value }
    } finally {
      isSearching.value = false
    }
  }

  const useNewPatient = (patientData: PatientData): void => {
    verifiedPatient.value = patientData
    patientVerified.value = true
  }

  const clearVerification = (): void => {
    patientVerified.value = false
    verifiedPatient.value = null
    searchError.value = ''
    isSearching.value = false
  }

  return {
    isSearching, searchError, patientVerified, verifiedPatient,
    searchPatientByCedula, useNewPatient, clearVerification
  }
}
