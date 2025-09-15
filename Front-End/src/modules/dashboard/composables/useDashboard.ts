import { ref, computed, onMounted, onUnmounted } from 'vue'
import { dashboardApiService } from '../services/dashboardApi.service'
import type {
  DashboardMetrics,
  CasosPorMesResponse,
  CasoUrgente,
  EstadisticasOportunidad,
  FiltrosCasosUrgentes,
  MuestraStats
} from '../types/dashboard.types'

// Cache global para optimizar rendimiento
const globalCache = new Map<string, { data: any; timestamp: number }>()
const CACHE_DURATION = 5 * 60 * 1000 // 5 minutos
// Coalescencia de peticiones en curso por clave
const inflightCasosPorMes = new Map<string, Promise<CasosPorMesResponse>>()

// Función helper para cache
const getCachedData = (key: string) => {
  const cached = globalCache.get(key)
  if (cached && (Date.now() - cached.timestamp) < CACHE_DURATION) {
    return cached.data
  }
  return null
}

const setCachedData = (key: string, data: any) => {
  globalCache.set(key, { data, timestamp: Date.now() })
}

export function useDashboard() {
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const metricas = ref<DashboardMetrics | null>(null)
  const casosPorMes = ref<CasosPorMesResponse | null>(null)
  const casosUrgentes = ref<CasoUrgente[]>([])
  const estadisticasOportunidad = ref<EstadisticasOportunidad | null>(null)
  const estadisticasMuestras = ref<MuestraStats | null>(null)

  const loadingMetricas = ref(false)
  const loadingCasosPorMes = ref(false)
  const loadingCasosUrgentes = ref(false)
  const loadingOportunidad = ref(false)
  const loadingMuestras = ref(false)

  const totalCasosAño = computed(() => casosPorMes.value?.total || 0)
  const añoActual = computed(() => new Date().getFullYear())

  const cargarMetricas = async (esPatologo: boolean = false) => {
    try {
      loadingMetricas.value = true
      error.value = null
      
      if (esPatologo) {
        metricas.value = await dashboardApiService.getMetricasPatologo()
      } else {
        metricas.value = await dashboardApiService.getMetricasDashboard()
      }
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las métricas del dashboard'
      throw err
    } finally {
      loadingMetricas.value = false
    }
  }

  const cargarCasosPorMes = async (año?: number, esPatologo: boolean = false, forceRefresh = false) => {
    const añoActual = año || new Date().getFullYear()
    const cacheKey = `casos-por-mes-${añoActual}-${esPatologo}`
    
    // Verificar cache si no es refresh forzado
    if (!forceRefresh) {
      const cachedData = getCachedData(cacheKey)
      if (cachedData) {
        casosPorMes.value = cachedData
        return
      }
      // Si hay una petición en curso con la misma clave, reutilizar
      const inflight = inflightCasosPorMes.get(cacheKey)
      if (inflight) {
        const data = await inflight
        casosPorMes.value = data
        return
      }
    }
    
    try {
      loadingCasosPorMes.value = true
      error.value = null
      
      // Crear petición y registrarla para coalescencia
      const fetchPromise = (async (): Promise<CasosPorMesResponse> => {
        if (esPatologo) return await dashboardApiService.getCasosPorMesPatologo(año)
        return await dashboardApiService.getCasosPorMes(año)
      })()
      inflightCasosPorMes.set(cacheKey, fetchPromise)
      const data = await fetchPromise
      
      casosPorMes.value = data
      setCachedData(cacheKey, data)
    } catch (err: any) {
      error.value = err.message || 'Error al cargar estadísticas de casos por mes'
      throw err
    } finally {
      loadingCasosPorMes.value = false
      inflightCasosPorMes.delete(cacheKey)
    }
  }

  const cargarCasosUrgentes = async (filtros: FiltrosCasosUrgentes = {}) => {
    try {
      loadingCasosUrgentes.value = true
      error.value = null
      casosUrgentes.value = await dashboardApiService.getCasosUrgentes(filtros)
    } catch (err: any) {
      error.value = err.message || 'Error al cargar casos urgentes'
      throw err
    } finally {
      loadingCasosUrgentes.value = false
    }
  }

  const cargarEstadisticasOportunidad = async () => {
    try {
      loadingOportunidad.value = true
      error.value = null
      estadisticasOportunidad.value = await dashboardApiService.getEstadisticasOportunidad()
    } catch (err: any) {
      error.value = err.message || 'Error al cargar estadísticas de oportunidad'
      throw err
    } finally {
      loadingOportunidad.value = false
    }
  }

  const cargarEstadisticasMuestras = async () => {
    try {
      loadingMuestras.value = true
      error.value = null
      estadisticasMuestras.value = await dashboardApiService.getEstadisticasMuestras()
    } catch (err: any) {
      error.value = err.message || 'Error al cargar estadísticas de muestras'
      throw err
    } finally {
      loadingMuestras.value = false
    }
  }

  const cargarTodosDatos = async () => {
    try {
      isLoading.value = true
      error.value = null
      await Promise.all([
        cargarMetricas(),
        cargarCasosPorMes(),
        cargarCasosUrgentes({ limite: 10 }),
        cargarEstadisticasOportunidad(),
        cargarEstadisticasMuestras()
      ])
    } catch (err: any) {
      error.value = err.message || 'Error al cargar los datos del dashboard'
    } finally {
      isLoading.value = false
    }
  }

  const recargarDatos = async (tipo: 'metricas' | 'casos-mes' | 'casos-urgentes' | 'oportunidad' | 'muestras' | 'todos') => {
    try {
      switch (tipo) {
        case 'metricas':
          await cargarMetricas()
          break
        case 'casos-mes':
          await cargarCasosPorMes()
          break
        case 'casos-urgentes':
          await cargarCasosUrgentes()
          break
        case 'oportunidad':
          await cargarEstadisticasOportunidad()
          break
        case 'muestras':
          await cargarEstadisticasMuestras()
          break
        case 'todos':
          await cargarTodosDatos()
          break
      }
    } catch (err) {
    }
  }

  const limpiarError = () => {
    error.value = null
  }

  const formatearNumero = (num: number): string => {
    return new Intl.NumberFormat('es-CO').format(num)
  }

  const obtenerClasePorcentaje = (porcentaje: number): string => {
    return porcentaje >= 0 
      ? 'bg-green-50 text-green-600 hover:bg-green-100'
      : 'bg-red-50 text-red-600 hover:bg-red-100'
  }

  const handleCaseCreated = () => {
    cargarMetricas()
    cargarCasosUrgentes()
  }

  onMounted(() => {
    window.addEventListener('case-created', handleCaseCreated as EventListener)
  })

  onUnmounted(() => {
    window.removeEventListener('case-created', handleCaseCreated as EventListener)
  })

  return {
    isLoading,
    error,
    metricas,
    casosPorMes,
    casosUrgentes,
    estadisticasOportunidad,
    estadisticasMuestras,
    loadingMetricas,
    loadingCasosPorMes,
    loadingCasosUrgentes,
    loadingOportunidad,
    loadingMuestras,
    totalCasosAño,
    añoActual,
    cargarMetricas,
    cargarCasosPorMes,
    cargarCasosUrgentes,
    cargarEstadisticasOportunidad,
    cargarEstadisticasMuestras,
    cargarTodosDatos,
    recargarDatos,
    limpiarError,
    formatearNumero,
    obtenerClasePorcentaje
  }
}