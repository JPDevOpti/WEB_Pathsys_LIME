// Entity API composable: load and expose list
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
      return { success: true, message: 'Entidades cargadas exitosamente', entities: response }
    } catch (err: any) {
      const errorMessage = err.message || 'Error al cargar entidades'
      error.value = errorMessage
      return { success: false, message: errorMessage, entities: [] }
    } finally {
      isLoading.value = false
    }
  }

  const clearState = () => { entities.value = []; error.value = ''; isLoading.value = false }

  return { isLoading, error, entities, loadEntities, clearState }
}
