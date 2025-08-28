import { ref } from 'vue'
import type { EntityInfo } from '../types'
import { entitiesApiService } from '../services'

export function useEntityAPI() {
  const isLoading = ref(false)
  const error = ref('')
  const entities = ref<EntityInfo[]>([])

  const loadEntities = async () => {
    isLoading.value = true
    error.value = ''

    try {
      const response = await entitiesApiService.getEntities()
      entities.value = response
      return { success: true, message: 'Entidades cargadas exitosamente', entities: entities.value }
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar entidades'
      error.value = errorMessage
      return { success: false, message: errorMessage, entities: [] }
    } finally {
      isLoading.value = false
    }
  }

  const clearState = () => {
    entities.value = []
    error.value = ''
    isLoading.value = false
  }

  const getEntityByCode = (code: string): EntityInfo | undefined => {
    return entities.value.find(entity => entity.codigo === code)
  }

  const searchEntitiesByName = (searchTerm: string): EntityInfo[] => {
    if (!searchTerm.trim()) return entities.value
    
    const term = searchTerm.toLowerCase().trim()
    return entities.value.filter(entity => 
      entity.nombre.toLowerCase().includes(term) || entity.codigo.toLowerCase().includes(term)
    )
  }

  return {
    isLoading, error, entities, loadEntities, clearState, getEntityByCode, searchEntitiesByName
  }
}
