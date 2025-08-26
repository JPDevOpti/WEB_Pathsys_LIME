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
      let result
      
      // Si se especifica una tabla específica, usar el endpoint de tabla
      if (tabla && tabla.trim()) {
        if (tabla === 'CIEO') {
          // Para CIEO, obtener todas las enfermedades de la tabla CIEO
          result = await diseaseService.searchDiseasesByTabla('CIEO', limit)
          // Luego filtrar por el término de búsqueda si se proporciona
          if (query && query.trim()) {
            const filteredDiseases = result.diseases.filter(disease => 
              disease.nombre.toLowerCase().includes(query.toLowerCase()) ||
              disease.codigo.toLowerCase().includes(query.toLowerCase())
            )
            result.diseases = filteredDiseases
            result.total = filteredDiseases.length
          }
        } else if (tabla === 'CIE10') {
          // Para CIE-10, obtener todas las enfermedades de la tabla CIE10
          result = await diseaseService.searchDiseasesByTabla('CIE10', limit)
          // Luego filtrar por el término de búsqueda si se proporciona
          if (query && query.trim()) {
            const filteredDiseases = result.diseases.filter(disease => 
              disease.nombre.toLowerCase().includes(query.toLowerCase()) ||
              disease.codigo.toLowerCase().includes(query.toLowerCase())
            )
            result.diseases = filteredDiseases
            result.total = filteredDiseases.length
          }
        } else {
          // Para otras tablas, usar búsqueda normal
          result = await diseaseService.searchDiseases(query, limit)
        }
      } else {
        // Búsqueda normal sin filtro de tabla
        result = await diseaseService.searchDiseases(query, limit)
      }
      
      return {
        success: true,
        diseases: result.diseases,
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
      
      console.error('Error al obtener enfermedad por ID:', err)
      
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
      
      console.error('Error al obtener enfermedad por código:', err)
      
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
