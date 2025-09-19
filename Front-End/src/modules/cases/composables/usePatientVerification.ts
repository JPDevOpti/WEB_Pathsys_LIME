import { ref } from 'vue'
import { patientsApiService } from '../services'
import type { PatientData } from '../types'

export function usePatientVerification() {
  const isSearching = ref(false)
  const searchError = ref('')
  const patientVerified = ref(false)
  const verifiedPatient = ref<PatientData | null>(null)

  const transformApiPatientToFormData = (apiPatient: any): PatientData => {
    // Mapear campos del backend en inglés a campos del frontend
    const tipoAtencionApi: string = apiPatient.care_type || apiPatient.tipo_atencion || ''
    const tipoAtencionForm = (() => {
      const v = String(tipoAtencionApi || '').toLowerCase()
      if (v.includes('ambulator') || v === 'ambulatory' || v === 'outpatient') return 'ambulatorio'
      if (v.includes('hospital') || v === 'inpatient') return 'hospitalizado'
      return ''
    })()
    const entidadCodigo = apiPatient.entity_info?.id || apiPatient.entidad_info?.codigo || apiPatient.entidad_info?.id
    const rawSexo = String(apiPatient?.gender || apiPatient?.sexo || '').toLowerCase()
    const sexoForm: '' | 'masculino' | 'femenino' = rawSexo.startsWith('f') ? 'femenino' : rawSexo.startsWith('m') ? 'masculino' : ''
    
    // Debug: mostrar el mapeo para verificar
    console.log('Mapeo de paciente:', {
      original: apiPatient,
      mapeado: {
        patientCode: apiPatient.patient_code,
        name: apiPatient?.name,
        gender: rawSexo,
        age: apiPatient.age,
        entity: apiPatient.entity_info?.name,
        entityCode: entidadCodigo,
        careType: tipoAtencionApi,
        observations: apiPatient.observations
      }
    })
    
    return {
      patientCode: apiPatient.patient_code || apiPatient.documento || apiPatient.paciente_code || apiPatient.cedula,
      name: apiPatient?.name || apiPatient?.nombre || '',
      gender: sexoForm,
      age: (apiPatient.age || apiPatient.edad).toString(),
      entity: apiPatient.entity_info?.name || apiPatient.entidad_info?.nombre || 'Sin entidad',
      entityCode: entidadCodigo,
      careType: tipoAtencionForm as any,
      observations: apiPatient.observations || apiPatient.observaciones || '',
      code: apiPatient._id || apiPatient.id
    }
  }
  const searchPatientByDocumento = async (documento: string) => {
    isSearching.value = true
    searchError.value = ''
    try {
      const apiPatient = await patientsApiService.getPatientByDocumento(documento)
      patientVerified.value = !!apiPatient
      verifiedPatient.value = apiPatient ? transformApiPatientToFormData(apiPatient) : null
      return { found: !!apiPatient, patient: verifiedPatient.value }
    } catch (e: any) {
      searchError.value = e.message || 'Error al buscar paciente'
      patientVerified.value = false
      verifiedPatient.value = null
      return { found: false }
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
    searchPatientByDocumento, useNewPatient, clearVerification
  }
}
