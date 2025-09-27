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
  const transformCaseFormToApiRequest = async (formData: any, verifiedPatient: any): Promise<any> => {
    const entityName = (formData as any).patientEntity
      ? await getEntityNameByCode((formData as any).patientEntity)
      : ((verifiedPatient as any)?.entity || 'Entidad no especificada')
    return {
      patient_info: {
        patient_code: (verifiedPatient as any)?.patientCode || (verifiedPatient as any)?.codigo || '',
        name: (verifiedPatient as any)?.name || '',
        age: Number.parseInt(String((verifiedPatient as any)?.age || 0)) || 0,
        gender: normalizeSexo((verifiedPatient as any)?.gender),
        entity_info: {
          id: (formData as any).patientEntity || (verifiedPatient as any)?.entityCode || 'ent_default',
          name: entityName
        },
        care_type: normalizeTipoAtencion((formData as any)?.patientCareType),
        observations: (verifiedPatient as any)?.observations || undefined
      },
      requesting_physician: (formData as any)?.requestingPhysician || undefined,
      service: (formData as any)?.service || undefined,
      samples: ((formData as any)?.samples || []).map((s: any) => ({
        body_region: (s as any)?.bodyRegion || '',
        tests: ((s as any)?.tests || []).map((t: any) => ({
          id: (t as any)?.code || '',
          name: (t as any)?.name || (t as any)?.code || '',
          quantity: (t as any)?.quantity || 1
        }))
      })),
      state: 'En proceso',
      priority: (formData as any)?.casePriority || 'Normal',
      observations: (formData as any)?.observations || undefined
    }
  }

  // Build a minimal CreatedCase object for UI from backend response
  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: any): any => {
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
      codigo: codigoCaso,
      paciente: {
        patient_code: apiResponse.patient_info?.patient_code || (verifiedPatient as any).patientCode,
        cedula: apiResponse.patient_info?.patient_code || (verifiedPatient as any).patientCode,
        name: apiResponse.patient_info?.name || (verifiedPatient as any).name,
        age: apiResponse.patient_info?.age || Number.parseInt(String((verifiedPatient as any).age || 0)) || 0,
        gender: apiResponse.patient_info?.gender || (verifiedPatient as any).gender,
        entity: apiResponse.patient_info?.entity_info?.name || (verifiedPatient as any).entity,
        careType: apiResponse.patient_info?.care_type || (caseData as any).patientCareType
      },
      entryDate: (caseData as any).entryDate,
      requestingPhysician: apiResponse.requesting_physician || (caseData as any).requestingPhysician,
      service: (caseData as any).service,
      priority: apiResponse.priority || (caseData as any).casePriority || 'Normal',
      samples: (caseData as any).samples,
      observations: apiResponse.observations || (caseData as any).observations || '',
      state: stateEs,
      creationDate: apiResponse.created_at || new Date().toISOString()
    }
  }

  // Public API: create case and return success/result for UI handling
  const createCase = async (caseData: any, verifiedPatient?: any): Promise<any> => {
    isLoading.value = true
    error.value = ''

    try {
      if (!verifiedPatient) throw new Error('Información del paciente verificado requerida')

      // LOG: Datos que llegan al createCase
      console.log('🔍 [LOG useCaseAPI] caseData recibido:', JSON.stringify(caseData, null, 2))
      console.log('🔍 [LOG useCaseAPI] verifiedPatient recibido:', JSON.stringify(verifiedPatient, null, 2))

      const apiRequest = await transformCaseFormToApiRequest(caseData, verifiedPatient)
      
      // LOG: Request que se envía al backend
      console.log('🔍 [LOG useCaseAPI] apiRequest enviado al backend:', JSON.stringify(apiRequest, null, 2))
      
      const apiResponse = await casesApiService.createCase(apiRequest)
      
      // LOG: Respuesta del backend
      console.log('🔍 [LOG useCaseAPI] apiResponse del backend:', JSON.stringify(apiResponse, null, 2))
      
      if (apiResponse?.case_code) {
        const builtCase = buildCreatedCase(apiResponse, verifiedPatient, caseData)
        
        // LOG: Caso construido para la UI
        console.log('🔍 [LOG useCaseAPI] buildCreatedCase resultado:', JSON.stringify(builtCase, null, 2))
        
        return {
          success: true,
          codigo: apiResponse.case_code,
          message: 'Caso creado exitosamente',
          case: builtCase
        }
      }
      
      throw new Error('Error al crear el caso: respuesta inválida del servidor')
      
    } catch (err: any) {
      console.error('❌ [ERROR useCaseAPI] Error al crear caso:', err)
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

