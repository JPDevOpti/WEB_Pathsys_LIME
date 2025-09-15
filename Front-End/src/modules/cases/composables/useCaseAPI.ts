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

  const normalizeSexo = (sexo: string): string => {
    const sexoLower = sexo.toLowerCase()
    if (['masculino', 'm', 'hombre'].includes(sexoLower)) return 'Masculino'
    if (['femenino', 'f', 'mujer'].includes(sexoLower)) return 'Femenino'
    return 'Masculino'
  }

  const normalizeTipoAtencion = (tipoAtencion: string): string => {
    const tipoLower = tipoAtencion.toLowerCase()
    if (['ambulatorio', 'ambulatoria'].includes(tipoLower)) return 'Ambulatorio'
    if (['hospitalizado', 'hospitalizada', 'hospitalizacion'].includes(tipoLower)) return 'Hospitalizado'
    return 'Ambulatorio'
  }

  const transformCaseFormToApiRequest = async (formData: CaseFormData, verifiedPatient: any): Promise<CreateCaseRequest> => {
    const entidadNombre = formData.entidadPaciente 
      ? await getEntityNameByCode(formData.entidadPaciente)
      : verifiedPatient.entidad
    
    return {
      paciente: {
        paciente_code: verifiedPatient.pacienteCode || verifiedPatient.codigo,
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
      medico_solicitante: formData.medicoSolicitante || undefined,
      servicio: formData.servicio || undefined,
      muestras: formData.muestras.map(muestra => ({
        region_cuerpo: muestra.regionCuerpo,
        pruebas: muestra.pruebas.map(prueba => ({
          id: prueba.code,
          nombre: prueba.nombre || prueba.code,
          cantidad: prueba.cantidad || 1
        }))
      })),
      estado: 'En proceso',
      prioridad: formData.prioridadCaso || 'Normal',
      observaciones_generales: formData.observaciones || undefined
    }
  }

  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: CaseFormData): CreatedCase => {
    const codigoCaso = apiResponse.caso_code || apiResponse.CasoCode || apiResponse.codigo || apiResponse.code
    
    return {
      id: apiResponse._id || apiResponse.id || codigoCaso,
      codigo: codigoCaso,
      paciente: {
        paciente_code: apiResponse.paciente?.paciente_code || verifiedPatient.pacienteCode,
        cedula: apiResponse.paciente?.cedula || verifiedPatient.pacienteCode,
        nombre: apiResponse.paciente?.nombre || verifiedPatient.nombrePaciente,
        edad: apiResponse.paciente?.edad || parseInt(verifiedPatient.edad),
        sexo: apiResponse.paciente?.sexo || verifiedPatient.sexo,
        entidad: apiResponse.paciente?.entidad_info?.nombre || verifiedPatient.entidad,
        tipoAtencion: apiResponse.paciente?.tipo_atencion || caseData.tipoAtencionPaciente
      },
      fechaIngreso: apiResponse.fecha_ingreso || caseData.fechaIngreso,
      medicoSolicitante: apiResponse.medico_solicitante || caseData.medicoSolicitante,
      servicio: caseData.servicio,
      prioridad: apiResponse.prioridad || caseData.prioridadCaso || 'Normal',
      muestras: caseData.muestras,
      observaciones: apiResponse.observaciones_generales || caseData.observaciones || '',
      estado: apiResponse.estado || 'Pendiente',
      fechaCreacion: apiResponse.fecha_creacion || apiResponse.fecha_ingreso || new Date().toISOString()
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
        const entidadNombre = caseData.entidadPaciente && caseData.entidadPaciente !== verifiedPatient.entidadCodigo
          ? await getEntityNameByCode(caseData.entidadPaciente)
          : verifiedPatient.entidad
        
        await patientsApiService.updatePatient(verifiedPatient.pacienteCode, {
          nombre: verifiedPatient.nombrePaciente,
          edad: parseInt(verifiedPatient.edad),
          sexo: normalizeSexo(verifiedPatient.sexo),
          entidad_info: {
            id: caseData.entidadPaciente || verifiedPatient.entidadCodigo || 'ent_default',
            nombre: entidadNombre
          },
          tipo_atencion: normalizeTipoAtencion(caseData.tipoAtencionPaciente || verifiedPatient.tipoAtencion),
          observaciones: verifiedPatient.observaciones || undefined
        })
      } catch {
      }
      
      if (apiResponse?.caso_code) {
        return {
          success: true,
          codigo: apiResponse.caso_code,
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

