import { ref, computed } from 'vue'
import { dashboardApiService } from '../services/dashboardApi.service'
import type {
  DashboardMetrics,
  CasosPorMesResponse,
  CasoUrgente,
  EstadisticasOportunidad,
  FiltrosCasosUrgentes
} from '../types/dashboard.types'

export function useDashboard() {
  const error = ref<string | null>(null)
  const metricas = ref<DashboardMetrics | null>(null)
  const casosPorMes = ref<CasosPorMesResponse | null>(null)
  const casosUrgentes = ref<CasoUrgente[]>([])
  const estadisticasOportunidad = ref<EstadisticasOportunidad | null>(null)

  const loadingMetricas = ref(false)
  const loadingCasosPorMes = ref(false)
  const loadingCasosUrgentes = ref(false)
  const loadingOportunidad = ref(false)

  // Simple caches to avoid duplicate network calls across components
  const casosPorMesCache = new Map<string, CasosPorMesResponse>()
  const metricasCache = new Map<string, DashboardMetrics>()
  const oportunidadCache = new Map<string, EstadisticasOportunidad>()

  const totalCasosAño = computed(() => casosPorMes.value?.total || 0)
  const añoActual = computed(() => new Date().getFullYear())

  // Fetch dashboard metrics; cached by role
  const cargarMetricas = async (esPatologo: boolean = false) => {
    try {
      if (loadingMetricas.value) return
      loadingMetricas.value = true
      error.value = null
      const cacheKey = esPatologo ? 'pathologist' : 'general'
      const cached = metricasCache.get(cacheKey)
      if (cached) {
        metricas.value = cached
        return
      }
      if (esPatologo) {
        metricas.value = await dashboardApiService.getMetricasPatologo()
      } else {
        metricas.value = await dashboardApiService.getMetricasDashboard()
      }
      if (metricas.value) metricasCache.set(cacheKey, metricas.value)
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las métricas del dashboard'
      throw err
    } finally {
      loadingMetricas.value = false
    }
  }

// Fetch monthly cases; cached by year and role
const cargarCasosPorMes = async (año?: number, esPatologo: boolean = false) => {
  try {
    if (loadingCasosPorMes.value) return
    loadingCasosPorMes.value = true
    error.value = null
    const resolvedYear = año ?? new Date().getFullYear()
    const cacheKey = `${resolvedYear}-${esPatologo ? 'pathologist' : 'general'}`
    const cached = casosPorMesCache.get(cacheKey)
    if (cached) {
      casosPorMes.value = cached
      return
    }
    if (esPatologo) {
      casosPorMes.value = await dashboardApiService.getCasosPorMesPatologo(resolvedYear)
    } else {
      casosPorMes.value = await dashboardApiService.getCasosPorMes(resolvedYear)
    }
    if (casosPorMes.value) casosPorMesCache.set(cacheKey, casosPorMes.value)
  } catch (err: any) {
    console.error('[Dashboard] Error al cargar casos por mes:', err)
    error.value = err.message || 'Error al cargar estadísticas de casos por mes'
    throw err
  } finally {
    loadingCasosPorMes.value = false
  }
}

  const cargarCasosUrgentes = async (filtros: FiltrosCasosUrgentes = {}) => {
    try {
      loadingCasosUrgentes.value = true
      error.value = null
      
      // Usar nuevos endpoints optimizados
      if (filtros.patologo) {
        casosUrgentes.value = await dashboardApiService.getUrgentCasesByPathologist(
          filtros.patologo, 
          filtros.limite || 50
        )
      } else {
        casosUrgentes.value = await dashboardApiService.getUrgentCasesGeneral(
          filtros.limite || 50
        )
      }
    } catch (err: any) {
      error.value = err.message || 'Error al cargar casos urgentes'
      throw err
    } finally {
      loadingCasosUrgentes.value = false
    }
  }

  // Fetch opportunity stats; cached by role
  const cargarEstadisticasOportunidad = async (esPatologo: boolean = false) => {
    try {
      if (loadingOportunidad.value) return
      loadingOportunidad.value = true
      error.value = null
      const cacheKey = esPatologo ? 'pathologist' : 'general'
      const cached = oportunidadCache.get(cacheKey)
      if (cached) {
        estadisticasOportunidad.value = cached
        return
      }
      estadisticasOportunidad.value = esPatologo
        ? await dashboardApiService.getEstadisticasOportunidadPatologo()
        : await dashboardApiService.getEstadisticasOportunidad()
      if (estadisticasOportunidad.value) oportunidadCache.set(cacheKey, estadisticasOportunidad.value)
    } catch (err: any) {
      error.value = err.message || 'Error al cargar estadísticas de oportunidad'
      throw err
    } finally {
      loadingOportunidad.value = false
    }
  }


  return {
    error,
    metricas,
    casosPorMes,
    casosUrgentes,
    estadisticasOportunidad,
    loadingMetricas,
    loadingCasosPorMes,
    loadingCasosUrgentes,
    loadingOportunidad,
    totalCasosAño,
    añoActual,
    cargarMetricas,
    cargarCasosPorMes,
    cargarCasosUrgentes,
    cargarEstadisticasOportunidad
  }
}