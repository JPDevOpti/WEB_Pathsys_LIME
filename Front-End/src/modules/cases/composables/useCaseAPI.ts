import { ref } from 'vue'
import { casesApiService } from '../services'
import { patientsApiService } from '../services'
import { entitiesApiService } from '../services'
import type { CaseFormData, CaseCreationResult, CreateCaseRequest, CreatedCase } from '../types'

export function useCaseAPI() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const isLoading = ref(false)
  const error = ref('')
  
  // Cache para entidades para evitar llamadas repetidas a la API
  const entitiesCache = ref<Map<string, string>>(new Map())

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================
  
  /**
   * Obtiene el nombre de una entidad por su código
   * @param entityCode - Código de la entidad
   * @returns Nombre de la entidad
   */
  const getEntityNameByCode = async (entityCode: string): Promise<string> => {
    // Verificar si ya tenemos el nombre en cache
    if (entitiesCache.value.has(entityCode)) {
      const cachedName = entitiesCache.value.get(entityCode)
      return cachedName || entityCode
    }
    
    try {
      // Validar que entityCode no sea undefined
      if (!entityCode) {
        return 'Entidad no especificada'
      }
      
      // Buscar la entidad por código
      const entity = await entitiesApiService.getEntityByCode(entityCode)
      
      const entityName = entity?.nombre || entityCode
      
      // Guardar en cache
      entitiesCache.value.set(entityCode, entityName)
      
      return entityName
    } catch (error) {
      return entityCode || 'Entidad no especificada' // Fallback al código si no se puede obtener el nombre
    }
  }
  
  // ============================================================================
  // FUNCIONES DE NORMALIZACIÓN
  // ============================================================================

  /**
   * Normaliza el sexo al formato esperado por el backend
   * @param sexo - Sexo a normalizar
   * @returns Sexo normalizado
   */
  const normalizeSexo = (sexo: string): string => {
    const sexoLower = sexo.toLowerCase()
    
    if (sexoLower === 'masculino' || sexoLower === 'm' || sexoLower === 'hombre') {
      return 'Masculino'
    }
    if (sexoLower === 'femenino' || sexoLower === 'f' || sexoLower === 'mujer') {
      return 'Femenino'
    }
    
    return 'Masculino' // Default fallback
  }

  /**
   * Normaliza el tipo de atención al formato esperado por el backend
   * @param tipoAtencion - Tipo de atención a normalizar
   * @returns Tipo de atención normalizado
   */
  const normalizeTipoAtencion = (tipoAtencion: string): string => {
    const tipoLower = tipoAtencion.toLowerCase()
    
    if (tipoLower === 'ambulatorio' || tipoLower === 'ambulatoria') {
      return 'Ambulatorio'
    }
    if (tipoLower === 'hospitalizado' || tipoLower === 'hospitalizada' || tipoLower === 'hospitalizacion') {
      return 'Hospitalizado'
    }
    
    return 'Ambulatorio' // Default fallback
  }

  // ============================================================================
  // FUNCIONES DE TRANSFORMACIÓN DE DATOS
  // ============================================================================

  /**
   * Transforma los datos del formulario al formato requerido por la API
   * @param formData - Datos del formulario
   * @param verifiedPatient - Información del paciente verificado
   * @returns Datos transformados para la API
   */
  const transformCaseFormToApiRequest = async (formData: CaseFormData, verifiedPatient: any): Promise<CreateCaseRequest> => {
    // Obtener el nombre de la entidad
    let entidadNombre = verifiedPatient.entidad
    if (formData.entidadPaciente) {
      entidadNombre = await getEntityNameByCode(formData.entidadPaciente)
    }
    
    const requestData = {
      paciente: {
        paciente_code: verifiedPatient.pacienteCode || verifiedPatient.codigo || `PAC_${verifiedPatient.numeroCedula}`,  // ✅ REQUERIDO
        cedula: verifiedPatient.numeroCedula || verifiedPatient.cedula || formData.pacienteCedula,  // ✅ REQUERIDO
        nombre: verifiedPatient.nombrePaciente,                                  // ✅ REQUERIDO
        edad: parseInt(verifiedPatient.edad),                                   // ✅ REQUERIDO
        sexo: normalizeSexo(verifiedPatient.sexo),                              // ✅ REQUERIDO
        entidad_info: {                                                         // ✅ REQUERIDO
          id: formData.entidadPaciente || verifiedPatient.entidadCodigo || 'ent_default',
          nombre: entidadNombre
        },
        tipo_atencion: normalizeTipoAtencion(formData.tipoAtencionPaciente),    // ✅ REQUERIDO
        observaciones: verifiedPatient.observaciones || undefined                // ❌ OPCIONAL
      },
      medico_solicitante: formData.medicoSolicitante ? {
        nombre: formData.medicoSolicitante
      } : undefined,
      servicio: formData.servicio || undefined,
      muestras: formData.muestras.map(muestra => ({
        region_cuerpo: muestra.regionCuerpo,
        pruebas: muestra.pruebas.map(prueba => ({
          id: prueba.code,
          nombre: prueba.code,
          cantidad: prueba.cantidad || 1
        }))
      })),
      estado: 'En proceso',
      observaciones_generales: formData.observaciones || undefined
    }
    
    return requestData
  }

  /**
   * Construye el objeto de respuesta del caso creado
   * @param apiResponse - Respuesta de la API
   * @param verifiedPatient - Información del paciente verificado
   * @param caseData - Datos del formulario
   * @returns Objeto del caso creado
   */
  const buildCreatedCase = (apiResponse: any, verifiedPatient: any, caseData: CaseFormData): CreatedCase => {
    return {
      id: apiResponse._id || apiResponse.caso_code,
      codigo: apiResponse.caso_code,
      paciente: {
        cedula: apiResponse.paciente?.cedula || verifiedPatient.numeroCedula,
        nombre: apiResponse.paciente?.nombre || verifiedPatient.nombrePaciente,
        edad: apiResponse.paciente?.edad || parseInt(verifiedPatient.edad),
        sexo: apiResponse.paciente?.sexo || verifiedPatient.sexo,
        entidad: apiResponse.paciente?.entidad_info?.nombre || verifiedPatient.entidad,
        entidadCodigo: apiResponse.paciente?.entidad_info?.id || caseData.entidadPaciente,
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

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Crea un nuevo caso en el sistema
   * @param caseData - Datos del formulario del caso
   * @param verifiedPatient - Información del paciente verificado
   * @returns Resultado de la creación del caso
   */
  const createCase = async (caseData: CaseFormData, verifiedPatient?: any): Promise<CaseCreationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      if (!verifiedPatient) {
        throw new Error('Información del paciente verificado requerida')
      }

      // Transformar datos del formulario al formato de la API
      const apiRequest = await transformCaseFormToApiRequest(caseData, verifiedPatient)
      
      // Realizar llamada a la API
      const apiResponse = await casesApiService.createCase(apiRequest)
      
      // Actualizar el paciente con los nuevos valores del formulario
      try {
        // Obtener el nombre de la entidad si se cambió
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
      } catch (updateError) {
        // No fallar la creación del caso por un error en la actualización del paciente
      }
      
      // Construir respuesta exitosa
      const result: CaseCreationResult = {
        success: true,
        codigo: apiResponse.caso_code,
        message: 'Caso creado exitosamente',
        case: buildCreatedCase(apiResponse, verifiedPatient, caseData)
      }
      
      return result
      
    } catch (err: any) {
      error.value = err.message || 'Error desconocido al crear el caso'
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Busca casos existentes en el sistema
   * @param searchTerm - Término de búsqueda
   * @returns Resultado de la búsqueda
   */
  const searchCases = async (searchTerm: string) => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await casesApiService.searchCases({
        query: searchTerm,
        limit: 10
      })
      
      return {
        success: true,
        cases: response.casos
      }
      
    } catch (err: any) {
      error.value = err.message || 'Error al buscar casos'
      
      return {
        success: false,
        message: error.value,
        cases: []
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpia el estado del composable
   */
  const clearState = () => {
    error.value = ''
    isLoading.value = false
  }

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado
    isLoading,
    error,
    
    // Métodos
    createCase,
    searchCases,
    clearState
  }
}

