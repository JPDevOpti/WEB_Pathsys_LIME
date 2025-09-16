import { ref } from 'vue'
import { casesApiService, patientsApiService, entitiesApiService } from '../services'
import type { CaseFormData, CaseCreationResult, CreateCaseRequest, CreatedCase } from '../types'

export function useCaseAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const entitiesCache = ref<Map<string, string>>(new Map())

  const getEntityNameByCode = async (entityCode: string): Promise<string> => {
    if (entitiesCache.value.has(entityCode)) return entitiesCache.value.get(entityCode) || entityCode
    
    if (!entityCode) return 'Entidad no especificada'
    
    try {
      const entity = await entitiesApiService.getEntityByCode(entityCode)
      const entityName = entity?.nombre || entityCode
      entitiesCache.value.set(entityCode, entityName)
      return entityName
    } catch {
      return 'Entidad no especificada'
    }
  }

  const normalizeSexo = (sexo?: string): string => {
    const sexoLower = String(sexo || '').toLowerCase()
    if (['masculino', 'm', 'hombre'].includes(sexoLower)) return 'Masculino'
    if (['femenino', 'f', 'mujer'].includes(sexoLower)) return 'Femenino'
    return 'Masculino'
  }

  const normalizeTipoAtencion = (tipoAtencion?: string): string => {
    const tipoLower = String(tipoAtencion || '').toLowerCase()
    if (['ambulatorio', 'ambulatoria'].includes(tipoLower)) return 'Ambulatorio'
    if (['hospitalizado', 'hospitalizada', 'hospitalizacion'].includes(tipoLower)) return 'Hospitalizado'
    return 'Ambulatorio'
  }

  const transformCaseFormToApiRequest = async (formData: CaseFormData, verifiedPatient: any): Promise<any> => {
    const entityName = formData.patientEntity 
      ? await getEntityNameByCode(formData.patientEntity)
      : (verifiedPatient?.entity || 'Entidad no especificada')
    return {
      patient_info: {
        patient_code: verifiedPatient?.patientCode || verifiedPatient?.codigo || '',
        name: verifiedPatient?.name || '',
        age: Number(verifiedPatient?.age || 0),
        gender: normalizeSexo(verifiedPatient?.gender),
        entity_info: {
          id: formData.patientEntity || verifiedPatient?.entityCode || 'ent_default',
          name: entityName
        },
        care_type: normalizeTipoAtencion(formData?.patientCareType),
        observations: verifiedPatient?.observations || undefined
      },
      requesting_physician: formData?.requestingPhysician || undefined,
      service: formData?.service || undefined,
      samples: (formData?.samples || []).map(s => ({
        body_region: s?.bodyRegion || '',
        tests: (s?.tests || []).map(t => ({ id: t?.code || '', name: t?.name || t?.code || '', quantity: t?.quantity || 1 }))
      })),
      state: 'In process',
      priority: formData?.casePriority || 'Normal',
      observations: formData?.observations || undefined
    }
  }

  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: CaseFormData): CreatedCase => {
    const codigoCaso = apiResponse.case_code || apiResponse.caso_code || apiResponse.code || apiResponse.codigo
    
    return {
      id: apiResponse._id || apiResponse.id || codigoCaso,
      code: codigoCaso,
      patient: {
        patient_code: apiResponse.patient_info?.patient_code || verifiedPatient.patientCode,
        cedula: apiResponse.patient_info?.patient_code || verifiedPatient.patientCode,
        name: apiResponse.patient_info?.name || verifiedPatient.name,
        age: apiResponse.patient_info?.age || parseInt(verifiedPatient.age),
        gender: apiResponse.patient_info?.gender || verifiedPatient.gender,
        entity: apiResponse.patient_info?.entity_info?.name || verifiedPatient.entity,
        careType: apiResponse.patient_info?.care_type || caseData.patientCareType
      },
      entryDate: caseData.entryDate,
      requestingPhysician: apiResponse.requesting_physician || caseData.requestingPhysician,
      service: caseData.service,
      priority: apiResponse.priority || caseData.casePriority || 'Normal',
      samples: caseData.samples,
      observations: apiResponse.observations || caseData.observations || '',
      state: apiResponse.state || 'En proceso',
      creationDate: apiResponse.created_at || new Date().toISOString()
    }
  }

  const createCase = async (caseData: CaseFormData, verifiedPatient?: any): Promise<CaseCreationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      if (!verifiedPatient) throw new Error('Información del paciente verificado requerida')

      const apiRequest = await transformCaseFormToApiRequest(caseData, verifiedPatient)
      const apiResponse = await casesApiService.createCase(apiRequest)
      
      try {
        const entidadNombre = caseData.patientEntity && caseData.patientEntity !== verifiedPatient.entityCode
          ? await getEntityNameByCode(caseData.patientEntity)
          : verifiedPatient.entity
        
        await patientsApiService.updatePatient(verifiedPatient.patientCode, {
          name: verifiedPatient.name,
          age: parseInt(verifiedPatient.age),
          gender: normalizeSexo(verifiedPatient.gender),
          entity_info: {
            id: caseData.patientEntity || verifiedPatient.entityCode || 'ent_default',
            name: entidadNombre
          },
          care_type: normalizeTipoAtencion(caseData.patientCareType || verifiedPatient.careType),
          observations: verifiedPatient.observations || undefined
        })
      } catch {
      }
      
      if (apiResponse?.case_code) {
        return {
          success: true,
          codigo: apiResponse.case_code,
          message: 'Caso creado exitosamente',
          case: buildCreatedCase(apiResponse, verifiedPatient, caseData)
        }
      }
      
      throw new Error('Error al crear el caso: respuesta inválida del servidor')
      
    } catch (err: any) {
      error.value = err.message || 'Error desconocido al crear el caso'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }


  const clearState = () => {
    error.value = ''
    isLoading.value = false
  }

  return { isLoading, error, createCase, clearState }
}

