import { ref } from 'vue'
import diseaseService from '../services/disease.service'
import type { Disease } from '../services/disease.service'

export interface DiseaseOperationResult {
  success: boolean
  diseases?: Disease[]
  error?: string
  message?: string
}

/**
 * Composable para manejar operaciones con enfermedades
 */
export function useDiseaseAPI() {
  // Estado reactivo
  const diseases = ref<Disease[]>([])
  const isLoading = ref(false)
  const error = ref('')

  /**
   * Cargar todas las enfermedades activas
   */
  const loadDiseases = async (): Promise<DiseaseOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const result = await diseaseService.getAllDiseases()
      
      diseases.value = result.diseases
      
      return {
        success: true,
        diseases: result.diseases,
        message: 'Enfermedades cargadas exitosamente'
      }
    } catch (err: any) {
      let errorMessage = 'Error al cargar enfermedades'
      
      if (err.response?.status === 307) {
        errorMessage = 'Error de redirección en el servidor. Verificar configuración de endpoints.'
      } else if (err.response?.data?.detail) {
        errorMessage = `Error de validación: ${JSON.stringify(err.response.data.detail)}`
      } else if (err.response?.data?.message) {
        errorMessage = err.response.data.message
      } else if (err.message) {
        errorMessage = err.message
      }
      
      error.value = errorMessage
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Buscar enfermedades por término
   */
  const searchDiseases = async (query: string, tabla?: string, limit: number = 15000): Promise<DiseaseOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      let diseasesList: Disease[] = []
      const searchTerm = query.trim().toLowerCase()

      if (tabla && tabla.trim()) {
        if (tabla === 'CIEO') {
          const response = await diseaseService.searchDiseasesByTabla('CIEO', limit)
          diseasesList = searchTerm
            ? response.diseases.filter(disease =>
                disease.name.toLowerCase().includes(searchTerm) ||
                disease.code.toLowerCase().includes(searchTerm)
              )
            : response.diseases
        } else if (tabla === 'CIE10') {
          const response = await diseaseService.searchDiseasesByTabla('CIE10', limit)
          diseasesList = searchTerm
            ? response.diseases.filter(disease =>
                disease.name.toLowerCase().includes(searchTerm) ||
                disease.code.toLowerCase().includes(searchTerm)
              )
            : response.diseases
        } else {
          const response = await diseaseService.searchDiseases(query, limit)
          diseasesList = response.diseases
        }
      } else {
        const response = await diseaseService.searchDiseases(query, limit)
        diseasesList = response.diseases
      }

      return {
        success: true,
        diseases: diseasesList,
        message: 'Búsqueda completada'
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error en la búsqueda'
      error.value = errorMessage
      
      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener enfermedad por ID
   */
  const getDiseaseById = async (id: string): Promise<DiseaseOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const disease = await diseaseService.getDiseaseById(id)
      
      return {
        success: true,
        diseases: [disease],
        message: 'Enfermedad encontrada'
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error al obtener enfermedad'
      error.value = errorMessage

      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Obtener enfermedad por código
   */
  const getDiseaseByCode = async (codigo: string): Promise<DiseaseOperationResult> => {
    isLoading.value = true
    error.value = ''

    try {
      const disease = await diseaseService.getDiseaseByCode(codigo)
      
      return {
        success: true,
        diseases: [disease],
        message: 'Enfermedad encontrada'
      }
    } catch (err: any) {
      const errorMessage = err.response?.data?.message || err.message || 'Error al obtener enfermedad'
      error.value = errorMessage

      return {
        success: false,
        error: errorMessage
      }
    } finally {
      isLoading.value = false
    }
  }

  return {
    // Estado
    diseases,
    isLoading,
    error,
    
    // Métodos
    loadDiseases,
    searchDiseases,
    getDiseaseById,
    getDiseaseByCode
  }
}
