import { ref } from 'vue'
import type { 
  FormPathologistInfo, 
  PathologistFormData, 
  PathologistAssignmentResult 
} from '../types'
import pathologistApi from '../services/pathologistApi.service'
import casesApi from '../services/casesApi.service'

export function usePathologistAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const pathologists = ref<FormPathologistInfo[]>([])

  const loadPathologists = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await pathologistApi.getPathologists()
      pathologists.value = response
      return { success: true, pathologists: response }
    } catch (err: any) {
      error.value = err.message || 'Error al cargar la lista de patólogos'
      return { success: false, message: error.value, pathologists: [] }
    } finally {
      isLoading.value = false
    }
  }

  const searchPathologists = async (searchTerm: string, includeInactive: boolean = false) => {
    if (!searchTerm.trim()) return await loadPathologists()

    isLoading.value = true
    error.value = ''

    try {
      const results = await pathologistApi.searchPathologists(searchTerm, includeInactive)
      pathologists.value = results
      return { success: true, pathologists: results }
    } catch (err: any) {
      error.value = err.message || 'Error al buscar patólogos'
      return { success: false, message: error.value, pathologists: [] }
    } finally {
      isLoading.value = false
    }
  }

  const assignPathologist = async (
    caseId: string, assignmentData: PathologistFormData
  ): Promise<PathologistAssignmentResult> => {
    isLoading.value = true
    error.value = ''

    try {
      if (pathologists.value.length === 0) {
        const loadResult = await loadPathologists()
        if (!loadResult.success) {
          throw new Error('No se pudieron cargar los patólogos: ' + loadResult.message)
        }
      }
      
      const selectedPathologist = findSelectedPathologist(assignmentData.patologoId)
      if (!selectedPathologist) throw new Error('Patólogo no encontrado en la lista local')
      
      const pathologistApiData = buildPathologistApiData(selectedPathologist)
      await casesApi.assignPathologist(caseId, pathologistApiData)
      
      return {
        success: true,
        message: 'Patólogo asignado exitosamente',
        assignment: {
          isAssigned: true,
          assignedDate: assignmentData.fechaAsignacion,
          pathologist: selectedPathologist
        }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error al asignar el patólogo'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const unassignPathologist = async (caseId: string): Promise<PathologistAssignmentResult> => {
    isLoading.value = true
    error.value = ''

    try {
      await casesApi.unassignPathologist(caseId)
      return {
        success: true,
        message: 'Patólogo desasignado exitosamente',
        assignment: { isAssigned: false }
      }
    } catch (err: any) {
      error.value = err.response?.data?.detail || err.message || 'Error al desasignar el patólogo'
      return { success: false, message: error.value }
    } finally {
      isLoading.value = false
    }
  }

  const findSelectedPathologist = (patologoId: string): FormPathologistInfo | undefined => {
    return pathologists.value.find(p => p.id === patologoId)
  }

  const buildPathologistApiData = (pathologist: FormPathologistInfo) => ({
    codigo: pathologist.id, nombre: pathologist.nombre
  })

  const clearState = () => {
    error.value = ''
    isLoading.value = false
  }

  return {
    isLoading, error, pathologists, loadPathologists, searchPathologists,
    assignPathologist, unassignPathologist, clearState
  }
}
