import { ref } from 'vue'
import type { 
  FormPathologistInfo, 
  PathologistFormData, 
  PathologistAssignmentResult 
} from '../types'
import pathologistApi from '../services/pathologistApi.service'
import casesApi from '../services/casesApi.service'

export function usePathologistAPI() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const isLoading = ref(false)
  const error = ref('')
  const pathologists = ref<FormPathologistInfo[]>([])

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Carga la lista de patólogos desde la API
   * @returns Resultado de la carga de patólogos
   */
  const loadPathologists = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await pathologistApi.getPathologists()
      pathologists.value = response
      
      return {
        success: true,
        pathologists: response
      }
      
    } catch (err: any) {
      error.value = err.message || 'Error al cargar la lista de patólogos'
      
      return {
        success: false,
        message: error.value,
        pathologists: []
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Busca patólogos por término de búsqueda
   * @param searchTerm - Término de búsqueda
   * @returns Resultado de la búsqueda
   */
  const searchPathologists = async (searchTerm: string) => {
    if (!searchTerm.trim()) {
      return await loadPathologists()
    }

    isLoading.value = true
    error.value = ''

    try {
      const results = await pathologistApi.searchPathologists(searchTerm)
      pathologists.value = results
      
      return {
        success: true,
        pathologists: results
      }
      
    } catch (err: any) {
      error.value = err.message || 'Error al buscar patólogos'
      
      return {
        success: false,
        message: error.value,
        pathologists: []
      }
    } finally {
      isLoading.value = false
    }
  }

  // ============================================================================
  // FUNCIONES DE ASIGNACIÓN
  // ============================================================================

  /**
   * Asigna un patólogo a un caso específico
   * @param caseId - ID del caso
   * @param assignmentData - Datos de la asignación
   * @returns Resultado de la asignación
   */
  const assignPathologist = async (
    caseId: string, 
    assignmentData: PathologistFormData
  ): Promise<PathologistAssignmentResult> => {
    isLoading.value = true
    error.value = ''

    try {
      // Cargar patólogos si la lista está vacía
      if (pathologists.value.length === 0) {
        const loadResult = await loadPathologists()
        if (!loadResult.success) {
          throw new Error('No se pudieron cargar los patólogos: ' + loadResult.message)
        }
      }
      
      // Buscar el patólogo seleccionado
      const selectedPathologist = findSelectedPathologist(assignmentData.patologoId)
      
      if (!selectedPathologist) {
        throw new Error('Patólogo no encontrado en la lista local')
      }
      
      // Preparar datos para la API
      const pathologistApiData = buildPathologistApiData(selectedPathologist)
      
      // Realizar asignación
      await casesApi.assignPathologist(caseId, pathologistApiData)
      
      const result: PathologistAssignmentResult = {
        success: true,
        message: 'Patólogo asignado exitosamente',
        assignment: {
          isAssigned: true,
          assignedDate: assignmentData.fechaAsignacion,
          pathologist: selectedPathologist
        }
      }
      
      return result
      
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error al asignar el patólogo'
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Desasigna un patólogo de un caso
   * @param caseId - ID del caso
   * @returns Resultado de la desasignación
   */
  const unassignPathologist = async (caseId: string): Promise<PathologistAssignmentResult> => {
    isLoading.value = true
    error.value = ''

    try {
      await casesApi.unassignPathologist(caseId)
      
      const result: PathologistAssignmentResult = {
        success: true,
        message: 'Patólogo desasignado exitosamente',
        assignment: {
          isAssigned: false
        }
      }
      
      return result
      
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error al desasignar el patólogo'
      
      return {
        success: false,
        message: error.value
      }
    } finally {
      isLoading.value = false
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Busca un patólogo específico en la lista local
   * @param patologoId - ID del patólogo a buscar
   * @returns Patólogo encontrado o undefined
   */
  const findSelectedPathologist = (patologoId: string): FormPathologistInfo | undefined => {
    return pathologists.value.find(p => p.id === patologoId)
  }

  /**
   * Construye los datos del patólogo para la API
   * @param pathologist - Información del patólogo
   * @returns Datos formateados para la API
   */
  const buildPathologistApiData = (pathologist: FormPathologistInfo) => {
    return {
      codigo: pathologist.id,
      nombre: pathologist.nombre
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
    pathologists,
    
    // Métodos
    loadPathologists,
    searchPathologists,
    assignPathologist,
    unassignPathologist,
    clearState
  }
}
