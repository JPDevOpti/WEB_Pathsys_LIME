// Case creation API composable: normalize form, call backend, map response
import { ref } from 'vue'
import { casesApiService, entitiesApiService } from '../services'
import type { CaseFormData, CaseCreationResult, CreatedCase } from '../types'

export function useCaseAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const entitiesCache = ref<Map<string, string>>(new Map())

  // Resolve entity name by code with simple in-memory cache
  const getEntityNameByCode = async (entityCode: string): Promise<string> => {
    if (!entityCode) return 'Entidad no especificada'
    const cached = entitiesCache.value.get(entityCode)
    if (cached) return cached
    try {
      const entity: any = await entitiesApiService.getEntityByCode(entityCode)
      const entityName = entity?.nombre || entity?.name || entityCode
      entitiesCache.value.set(entityCode, entityName)
      return entityName
    } catch {
      return 'Entidad no especificada'
    }
  }

  // Normalize gender to backend-expected Spanish values
  const normalizeSexo = (sexo?: string): string => {
    const v = String(sexo || '').toLowerCase()
    if (v.startsWith('m') || v.includes('hombre')) return 'Masculino'
    if (v.startsWith('f') || v.includes('mujer')) return 'Femenino'
    return 'Masculino'
  }

  // Normalize care type to backend-expected Spanish values
  const normalizeTipoAtencion = (tipoAtencion?: string): string => {
    const v = String(tipoAtencion || '').toLowerCase()
    if (v.includes('ambulator')) return 'Ambulatorio'
    if (v.includes('hospital')) return 'Hospitalizado'
    return 'Ambulatorio'
  }

  // Map form state + verified patient to backend request body
  const transformCaseFormToApiRequest = async (formData: CaseFormData, verifiedPatient: any): Promise<any> => {
    const entityName = formData.patientEntity
      ? await getEntityNameByCode(formData.patientEntity)
      : (verifiedPatient?.entity || 'Entidad no especificada')
    return {
      patient_info: {
        patient_code: verifiedPatient?.patientCode || verifiedPatient?.codigo || '',
        name: verifiedPatient?.name || '',
        age: Number.parseInt(String(verifiedPatient?.age || 0)) || 0,
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
        tests: (s?.tests || []).map(t => ({
          id: t?.code || '',
          name: t?.name || t?.code || '',
          quantity: t?.quantity || 1
        }))
      })),
      state: 'En proceso',
      priority: formData?.casePriority || 'Normal',
      observations: formData?.observations || undefined
    }
  }

  // Build a minimal CreatedCase object for UI from backend response
  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: CaseFormData): CreatedCase => {
    const codigoCaso = apiResponse.case_code || apiResponse.caso_code || apiResponse.code || apiResponse.codigo
    const stateRaw = String(apiResponse.state || '').toLowerCase()
    const stateMap: Record<string, string> = {
      'in process': 'En proceso',
      'in_process': 'En proceso',
      'processing': 'En proceso',
      'pending': 'Pendiente',
      'completed': 'Completado',
      'finished': 'Completado',
      'cancelled': 'Cancelado',
      'canceled': 'Cancelado'
    }
    const stateEs = stateMap[stateRaw] || apiResponse.state || 'En proceso'
    
    return {
      id: apiResponse._id || apiResponse.id || codigoCaso,
      code: codigoCaso,
      patient: {
        patient_code: apiResponse.patient_info?.patient_code || verifiedPatient.patientCode,
        cedula: apiResponse.patient_info?.patient_code || verifiedPatient.patientCode,
        name: apiResponse.patient_info?.name || verifiedPatient.name,
        age: apiResponse.patient_info?.age || Number.parseInt(String(verifiedPatient.age || 0)) || 0,
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
      state: stateEs,
      creationDate: apiResponse.created_at || new Date().toISOString()
    }
  }

  // Public API: create case and return success/result for UI handling
  const createCase = async (caseData: CaseFormData, verifiedPatient?: any): Promise<CaseCreationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      if (!verifiedPatient) throw new Error('Información del paciente verificado requerida')

      const apiRequest = await transformCaseFormToApiRequest(caseData, verifiedPatient)
      const apiResponse = await casesApiService.createCase(apiRequest)
      
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

