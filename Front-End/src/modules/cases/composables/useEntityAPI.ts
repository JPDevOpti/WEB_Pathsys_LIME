import { ref } from 'vue'
import type { EntityInfo } from '../types'
import { entitiesApiService } from '../services'

export function useEntityAPI() {
  // ============================================================================
  // ESTADO
  // ============================================================================
  
  const isLoading = ref(false)
  const error = ref('')
  const entities = ref<EntityInfo[]>([])

  // ============================================================================
  // FUNCIONES PRINCIPALES
  // ============================================================================

  /**
   * Carga la lista de entidades desde la API
   * @returns Resultado de la carga de entidades
   */
  const loadEntities = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await entitiesApiService.getEntities()
      entities.value = response
      
      return {
        success: true,
        message: 'Entidades cargadas exitosamente',
        entities: entities.value
      }
      
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar entidades'
      error.value = errorMessage
      
      return {
        success: false,
        message: errorMessage,
        entities: []
      }
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Limpia el estado del composable
   */
  const clearState = () => {
    entities.value = []
    error.value = ''
    isLoading.value = false
  }

  // ============================================================================
  // FUNCIONES DE BÚSQUEDA
  // ============================================================================

  /**
   * Obtiene una entidad por su código
   * @param code - Código de la entidad
   * @returns Entidad encontrada o undefined
   */
  const getEntityByCode = (code: string): EntityInfo | undefined => {
    return entities.value.find(entity => entity.codigo === code)
  }

  /**
   * Busca entidades por nombre o código
   * @param searchTerm - Término de búsqueda
   * @returns Lista de entidades que coinciden con la búsqueda
   */
  const searchEntitiesByName = (searchTerm: string): EntityInfo[] => {
    if (!searchTerm.trim()) return entities.value
    
    const term = searchTerm.toLowerCase().trim()
    return entities.value.filter(entity => 
      entity.nombre.toLowerCase().includes(term) ||
      entity.codigo.toLowerCase().includes(term)
    )
  }

  // ============================================================================
  // RETORNO
  // ============================================================================

  return {
    // Estado reactivo
    isLoading,
    error,
    entities,
    
    // Métodos
    loadEntities,
    clearState,
    getEntityByCode,
    searchEntitiesByName
  }
}
