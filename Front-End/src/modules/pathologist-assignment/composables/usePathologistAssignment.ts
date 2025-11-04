import { ref } from 'vue'
import type { 
  PathologistAssignmentFormData, 
  CaseModel, 
  AssignmentResult
} from '../types'
import casesApiService from '../../cases/services/casesApi.service'

export function usePathologistAssignment() {
  const isLoading = ref(false)
  const isLoadingSearch = ref(false)
  const error = ref('')
  const searchError = ref('')
  const casoEncontrado = ref(false)
  const casoInfo = ref<CaseModel | null>(null)

  // Buscar caso por código
  const buscarCaso = async (codigoCaso: string): Promise<boolean> => {
    if (!codigoCaso.trim()) {
      searchError.value = 'Por favor, ingrese un código de caso'
      return false
    }
    
    if (!isValidCodigoFormat(codigoCaso)) {
      searchError.value = 'El código debe tener el formato YYYY-NNNNN (Ejemplo: 2025-00001)'
      return false
    }

    isLoadingSearch.value = true
    searchError.value = ''
    casoEncontrado.value = false

    try {
      const casoResponse = await casesApiService.getCaseByCode(codigoCaso.trim())
      casoEncontrado.value = true
      casoInfo.value = casoResponse
      return true
    } catch (error: any) {
      casoEncontrado.value = false
      casoInfo.value = null
      const message = error?.message || ''
      
      if (message.includes('404') || message.includes('no encontrado')) {
        searchError.value = `No existe un caso con el código "${codigoCaso}"`
      } else if (message.includes('400')) {
        searchError.value = 'Formato de código de caso inválido'
      } else if (message.includes('500')) {
        searchError.value = 'Error interno del servidor. Inténtelo más tarde.'
      } else {
        searchError.value = 'Error al buscar el caso. Inténtelo nuevamente.'
      }
      
      return false
    } finally {
      isLoadingSearch.value = false
    }
  }

  // Asignar patólogo a caso
  const asignarPatologo = async (
    codigoCaso: string, 
    assignmentData: PathologistAssignmentFormData
  ): Promise<AssignmentResult> => {
    if (!casoInfo.value) {
      return { success: false, message: 'No hay información del caso disponible' }
    }

    if (isCaseCompleted(casoInfo.value)) {
      return { success: false, message: 'No se puede asignar patólogo a un caso completado' }
    }

    isLoading.value = true
    error.value = ''

    try {
      const tienePatologo = (casoInfo.value as any)?.assigned_pathologist?.id
      
      // Si ya tiene patólogo, desasignarlo primero
      if (tienePatologo) {
        try {
          await casesApiService.unassignPathologist(codigoCaso)
        } catch (e: any) {
          return { success: false, message: e?.message || 'No fue posible desasignar al patólogo previo' }
        }
      }

      // Asignar nuevo patólogo
      const updatedCase = await casesApiService.assignPathologist(codigoCaso, {
        codigo: assignmentData.patologoId,
        nombre: assignmentData.patologoId
      })
      const assigned = (updatedCase as any)?.assigned_pathologist || {}
      
      return {
        success: true,
        message: 'Patólogo asignado exitosamente',
        assignment: {
          pathologist: {
            id: assignmentData.patologoId,
            name: assigned.name || assignmentData.patologoId,
            patologo_code: assignmentData.patologoId
          }
        }
      }
    } catch (error: any) {
      const errorMessage = error.response?.data?.detail || error.message || 'Error al asignar el patólogo'
      return { success: false, message: errorMessage }
    } finally {
      isLoading.value = false
    }
  }

  // Validar formato de código de caso
  const isValidCodigoFormat = (codigo: string): boolean => {
    if (!codigo || typeof codigo !== 'string' || codigo.trim() === '') return false
    return /^\d{4}-\d{5}$/.test(codigo.trim())
  }

  // Verificar si el caso está completado
  const isCaseCompleted = (caso: CaseModel): boolean => {
    const estado = (caso as any)?.state || (caso as any)?.estado || ''
    return estado.toLowerCase() === 'completado' || estado.toLowerCase() === 'completed'
  }

  // Obtener estado localizado
  const getEstadoDisplay = (caso: CaseModel): string => {
    const raw = String((caso as any)?.state || (caso as any)?.estado || '').toLowerCase()
    const map: Record<string, string> = {
      'in process': 'En proceso',
      in_process: 'En proceso',
      processing: 'En proceso',
      pending: 'Pendiente',
      completed: 'Completado',
      finished: 'Completado',
      cancelled: 'Cancelado',
      canceled: 'Cancelado'
    }
    if (!raw) return 'N/A'
    return map[raw] || (caso as any)?.estado || 'En proceso'
  }

  // Obtener patólogo actual
  const getPatologoActual = (caso: CaseModel): string => {
    return (caso as any)?.assigned_pathologist?.name || 
           (caso as any)?.patologo_asignado?.nombre || 
           'Sin asignar'
  }

  // Limpiar estado del formulario
  const limpiarFormulario = () => {
    casoEncontrado.value = false
    searchError.value = ''
    casoInfo.value = null
    error.value = ''
  }

  // Limpiar errores
  const clearErrors = () => {
    error.value = ''
    searchError.value = ''
  }

  return {
    // Estado
    isLoading,
    isLoadingSearch,
    error,
    searchError,
    casoEncontrado,
    casoInfo,
    
    // Métodos
    buscarCaso,
    asignarPatologo,
    isValidCodigoFormat,
    isCaseCompleted,
    getEstadoDisplay,
    getPatologoActual,
    limpiarFormulario,
    clearErrors
  }
}

