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

  const cargarCasosPorMes = async (año?: number, esPatologo: boolean = false) => {
    try {
      loadingCasosPorMes.value = true
      error.value = null
      
      if (esPatologo) {
        casosPorMes.value = await dashboardApiService.getCasosPorMesPatologo(año)
      } else {
        casosPorMes.value = await dashboardApiService.getCasosPorMes(año)
      }
    } catch (err: any) {
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

  const cargarEstadisticasOportunidad = async (esPatologo: boolean = false) => {
    try {
      loadingOportunidad.value = true
      error.value = null
      estadisticasOportunidad.value = esPatologo
        ? await dashboardApiService.getEstadisticasOportunidadPatologo()
        : await dashboardApiService.getEstadisticasOportunidad()
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