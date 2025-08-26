import { ref } from 'vue'
import { bodyRegionsApiService, type BodyRegionItem } from '../services/bodyRegionsApi.service'

export function useBodyRegionsAPI() {
  const regions = ref<BodyRegionItem[]>([])
  const isLoading = ref(false)
  const error = ref('')

  const fallbackRegions: BodyRegionItem[] = [
    { value: 'cabeza', label: 'Cabeza', category: 'Cabeza y Cuello' },
    { value: 'cuello', label: 'Cuello', category: 'Cabeza y Cuello' },
    { value: 'cara', label: 'Cara', category: 'Cabeza y Cuello' },
    { value: 'torax', label: 'Tórax', category: 'Tórax' },
    { value: 'abdomen', label: 'Abdomen', category: 'Abdomen' },
    { value: 'brazo_derecho', label: 'Brazo Derecho', category: 'Extremidades Superiores' },
    { value: 'brazo_izquierdo', label: 'Brazo Izquierdo', category: 'Extremidades Superiores' },
    { value: 'muslo_derecho', label: 'Muslo Derecho', category: 'Extremidades Inferiores' },
    { value: 'muslo_izquierdo', label: 'Muslo Izquierdo', category: 'Extremidades Inferiores' },
    { value: 'piel_torax', label: 'Piel de Tórax', category: 'Piel' },
    { value: 'no_especificado', label: 'No Especificado', category: 'Otros' }
  ]

  const loadRegions = async () => {
    isLoading.value = true
    error.value = ''
    try {
      const data = await bodyRegionsApiService.getAll()
      if (Array.isArray(data) && data.length > 0) {
        regions.value = data
      } else {
        regions.value = fallbackRegions
      }
      return { success: true, regions: regions.value }
    } catch (e: any) {
      error.value = e?.message || 'Error al cargar regiones'
      regions.value = fallbackRegions
      return { success: false, error: error.value, regions: regions.value }
    } finally {
      isLoading.value = false
    }
  }

  return { regions, isLoading, error, loadRegions }
}


