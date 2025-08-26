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
    console.log('🔍 getEntityNameByCode llamado con código:', entityCode)
    
    // Verificar si ya tenemos el nombre en cache
    if (entitiesCache.value.has(entityCode)) {
      const cachedName = entitiesCache.value.get(entityCode)
      console.log('✅ Nombre encontrado en cache:', cachedName)
      return cachedName || entityCode
    }
    
    try {
      console.log('📡 Llamando a la API para obtener entidad:', entityCode)
      // Buscar la entidad por código
      const entity = await entitiesApiService.getEntityByCode(entityCode)
      console.log('📋 Respuesta de la API para entidad:', entity)
      
      const entityName = entity.nombre || entityCode
      console.log('🏷️ Nombre de entidad extraído:', entityName)
      
      // Guardar en cache
      entitiesCache.value.set(entityCode, entityName)
      console.log('💾 Entidad guardada en cache:', entityCode, '->', entityName)
      
      return entityName
    } catch (error) {
      console.error('💥 Error al obtener nombre de entidad:', entityCode, error)
      console.warn(`No se pudo obtener el nombre de la entidad ${entityCode}:`, error)
      return entityCode // Fallback al código si no se puede obtener el nombre
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
    console.log('🔄 transformCaseFormToApiRequest - Datos de entrada:', {
      entidadPaciente: formData.entidadPaciente,
      entidadCodigo: verifiedPatient.entidadCodigo,
      entidad: verifiedPatient.entidad
    })
    
    // Obtener el nombre de la entidad
    let entidadNombre = verifiedPatient.entidad
    if (formData.entidadPaciente) {
      console.log('🏥 Obteniendo nombre de entidad para código:', formData.entidadPaciente)
      entidadNombre = await getEntityNameByCode(formData.entidadPaciente)
      console.log('🏷️ Nombre de entidad obtenido:', entidadNombre)
    }
    

    
    const requestData = {
      paciente: {
        codigo: verifiedPatient.codigo || `PAC_${verifiedPatient.numeroCedula}`,
        cedula: verifiedPatient.numeroCedula,
        nombre: verifiedPatient.nombrePaciente,
        edad: parseInt(verifiedPatient.edad),
        sexo: normalizeSexo(verifiedPatient.sexo),
        entidad_info: {
          codigo: formData.entidadPaciente || verifiedPatient.entidadCodigo || 'ent_default',
          nombre: entidadNombre
        },
        tipo_atencion: normalizeTipoAtencion(formData.tipoAtencionPaciente),
        observaciones: verifiedPatient.observaciones || undefined
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
    
    console.log('📤 Datos finales enviados a la API:', JSON.stringify(requestData, null, 2))
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
      id: apiResponse._id || apiResponse.CasoCode,
      codigo: apiResponse.CasoCode,
      paciente: {
        cedula: apiResponse.paciente?.cedula || verifiedPatient.numeroCedula,
        nombre: apiResponse.paciente?.nombre || verifiedPatient.nombrePaciente,
        edad: apiResponse.paciente?.edad || parseInt(verifiedPatient.edad),
        sexo: apiResponse.paciente?.sexo || verifiedPatient.sexo,
        entidad: apiResponse.paciente?.entidad_info?.nombre || verifiedPatient.entidad,
        entidadCodigo: apiResponse.paciente?.entidad_info?.codigo || caseData.entidadPaciente,
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
        console.log('Paciente actualizado con nuevos valores del formulario:', {
          entidad: entidadNombre,
          entidadCodigo: caseData.entidadPaciente,
          tipoAtencion: caseData.tipoAtencionPaciente
        })
      } catch (updateError) {
        console.warn('El caso se creó pero falló la actualización del paciente:', updateError)
        // No fallar la creación del caso por un error en la actualización del paciente
      }
      
      // Construir respuesta exitosa
      const result: CaseCreationResult = {
        success: true,
        codigo: apiResponse.CasoCode,
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

