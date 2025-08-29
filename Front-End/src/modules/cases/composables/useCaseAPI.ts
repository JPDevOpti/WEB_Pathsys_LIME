import { ref } from 'vue'
import { casesApiService } from '../services'
import { patientsApiService } from '../services'
import { entitiesApiService } from '../services'
import type { CaseFormData, CaseCreationResult, CreateCaseRequest, CreatedCase, CaseState } from '../types'

export function useCaseAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const entitiesCache = ref<Map<string, string>>(new Map())

  const getEntityNameByCode = async (entityCode: string): Promise<string> => {
    if (entitiesCache.value.has(entityCode)) {
      return entitiesCache.value.get(entityCode) || entityCode
    }
    
    try {
      if (!entityCode) return 'Entidad no especificada'
      
      const entity = await entitiesApiService.getEntityByCode(entityCode)
      const entityName = entity?.nombre || entityCode
      entitiesCache.value.set(entityCode, entityName)
      return entityName
    } catch {
      return entityCode || 'Entidad no especificada'
    }
  }

  const normalizeSexo = (sexo: string): string => {
    const sexoLower = sexo.toLowerCase()
    if (sexoLower === 'masculino' || sexoLower === 'm' || sexoLower === 'hombre') return 'Masculino'
    if (sexoLower === 'femenino' || sexoLower === 'f' || sexoLower === 'mujer') return 'Femenino'
    return 'Masculino'
  }

  const normalizeTipoAtencion = (tipoAtencion: string): string => {
    const tipoLower = tipoAtencion.toLowerCase()
    if (tipoLower === 'ambulatorio' || tipoLower === 'ambulatoria') return 'Ambulatorio'
    if (tipoLower === 'hospitalizado' || tipoLower === 'hospitalizada' || tipoLower === 'hospitalizacion') return 'Hospitalizado'
    return 'Ambulatorio'
  }

  const transformCaseFormToApiRequest = async (formData: CaseFormData, verifiedPatient: any): Promise<CreateCaseRequest> => {
    let entidadNombre = verifiedPatient.entidad
    if (formData.entidadPaciente) {
      entidadNombre = await getEntityNameByCode(formData.entidadPaciente)
    }
    
    return {
      paciente: {
        paciente_code: verifiedPatient.pacienteCode || verifiedPatient.codigo || `PAC_${verifiedPatient.numeroCedula}`,
        cedula: verifiedPatient.numeroCedula || verifiedPatient.cedula || formData.pacienteCedula,
        nombre: verifiedPatient.nombrePaciente,
        edad: parseInt(verifiedPatient.edad),
        sexo: normalizeSexo(verifiedPatient.sexo),
        entidad_info: {
          id: formData.entidadPaciente || verifiedPatient.entidadCodigo || 'ent_default',
          nombre: entidadNombre
        },
        tipo_atencion: normalizeTipoAtencion(formData.tipoAtencionPaciente),
        observaciones: verifiedPatient.observaciones || undefined
      },
      medico_solicitante: formData.medicoSolicitante ? { nombre: formData.medicoSolicitante } : undefined,
      servicio: formData.servicio || undefined,
      muestras: formData.muestras.map(muestra => ({
        region_cuerpo: muestra.regionCuerpo,
        pruebas: muestra.pruebas.map(prueba => ({
          id: prueba.code,
          nombre: prueba.code,
          cantidad: prueba.cantidad || 1
        }))
      })),
      estado: 'En proceso' as CaseState,
      observaciones_generales: formData.observaciones || undefined
    }
  }

  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: CaseFormData): CreatedCase => {
    const codigoCaso = (apiResponse as any).caso_code || (apiResponse as any).CasoCode || (apiResponse as any).codigo || (apiResponse as any).code
    
    return {
      id: apiResponse._id || apiResponse.id || codigoCaso,
      codigo: codigoCaso,
      paciente: {
        cedula: apiResponse.paciente?.cedula || verifiedPatient.numeroCedula,
        nombre: apiResponse.paciente?.nombre || verifiedPatient.nombrePaciente,
        edad: apiResponse.paciente?.edad || parseInt(verifiedPatient.edad),
        sexo: apiResponse.paciente?.sexo || verifiedPatient.sexo,
        entidad: apiResponse.paciente?.entidad_info?.nombre || verifiedPatient.entidad,
        tipoAtencion: apiResponse.paciente?.tipo_atencion || caseData.tipoAtencionPaciente
      },
      fechaIngreso: apiResponse.fecha_ingreso || caseData.fechaIngreso,
      medicoSolicitante: apiResponse.medico_solicitante?.nombre || caseData.medicoSolicitante,
      servicio: caseData.servicio,
      muestras: caseData.muestras,
      observaciones: apiResponse.observaciones_generales || caseData.observaciones || '',
      estado: apiResponse.estado || 'Pendiente',
      fechaCreacion: apiResponse.fecha_ingreso || new Date().toISOString()
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
        let entidadNombre = verifiedPatient.entidad
        if (caseData.entidadPaciente && caseData.entidadPaciente !== verifiedPatient.entidadCodigo) {
          entidadNombre = await getEntityNameByCode(caseData.entidadPaciente)
        }
        
        const patientUpdateData = {
          numeroCedula: verifiedPatient.numeroCedula,
          nombrePaciente: verifiedPatient.nombrePaciente,
          sexo: verifiedPatient.sexo,
          edad: verifiedPatient.edad,
          entidad: entidadNombre,
          entidadCodigo: caseData.entidadPaciente || verifiedPatient.entidadCodigo,
          tipoAtencion: caseData.tipoAtencionPaciente || verifiedPatient.tipoAtencion,
          observaciones: verifiedPatient.observaciones || ''
        }
        
        await patientsApiService.updatePatient(verifiedPatient.numeroCedula, patientUpdateData)
      } catch {
        // No fallar la creación del caso por un error en la actualización del paciente
      }
      
      return {
        success: true,
        codigo: apiResponse.caso_code,
        message: 'Caso creado exitosamente',
        case: buildCreatedCase(apiResponse, verifiedPatient, caseData)
      }
      
    } catch (err: any) {
      error.value = err.message || 'Error desconocido al crear el caso'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const searchCases = async (searchTerm: string) => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await casesApiService.searchCases({ query: searchTerm, limit: 10 })
      return { success: true, cases: response.casos }
    } catch (err: any) {
      error.value = err.message || 'Error al buscar casos'
      return { success: false, message: error.value, cases: [] }
    } finally {
      isLoading.value = false
    }
  }

  const clearState = () => {
    error.value = ''
    isLoading.value = false
  }

  return {
    isLoading,
    error,
    createCase,
    searchCases,
    clearState
  }
}

