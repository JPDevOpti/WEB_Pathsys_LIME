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

/**
 * Composable para manejar el estado y lógica del dashboard
 */
export function useDashboard() {
  // Estados reactivos
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const metricas = ref<DashboardMetrics | null>(null)
  const casosPorMes = ref<CasosPorMesResponse | null>(null)
  const casosUrgentes = ref<CasoUrgente[]>([])
  const estadisticasOportunidad = ref<EstadisticasOportunidad | null>(null)
  const estadisticasMuestras = ref<MuestraStats | null>(null)

  // Estados de carga individuales
  const loadingMetricas = ref(false)
  const loadingCasosPorMes = ref(false)
  const loadingCasosUrgentes = ref(false)
  const loadingOportunidad = ref(false)
  const loadingMuestras = ref(false)

  // Computed properties
  const totalCasosAño = computed(() => casosPorMes.value?.total || 0)
  const añoActual = computed(() => new Date().getFullYear())

  /**
   * Cargar métricas principales del dashboard
   */
  const cargarMetricas = async () => {
    try {
      loadingMetricas.value = true
      error.value = null
      
      metricas.value = await dashboardApiService.getMetricasDashboard()
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las métricas del dashboard'
      throw err
    } finally {
      loadingMetricas.value = false
    }
  }

  /**
   * Cargar estadísticas de casos por mes
   */
  const cargarCasosPorMes = async (año?: number) => {
    try {
      loadingCasosPorMes.value = true
      error.value = null
      
      // Simular delay de red
      await new Promise(resolve => setTimeout(resolve, 500))
      
      casosPorMes.value = await dashboardApiService.getCasosPorMes(año)
    } catch (err: any) {
      error.value = err.message || 'Error al cargar estadísticas de casos por mes'
      throw err
    } finally {
      loadingCasosPorMes.value = false
    }
  }

  /**
   * Cargar casos urgentes
   */
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

  /**
   * Cargar estadísticas de oportunidad
   */
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

  /**
   * Cargar estadísticas de muestras
   */
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

  /**
   * Cargar todos los datos del dashboard
   */
  const cargarTodosDatos = async () => {
    try {
      isLoading.value = true
      error.value = null
      
      // Cargar datos en paralelo para mejor rendimiento
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

  /**
   * Recargar datos específicos
   */
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
      // Error ya manejado en las funciones individuales
    }
  }

  /**
   * Limpiar errores
   */
  const limpiarError = () => {
    error.value = null
  }

  /**
   * Formatear números con separadores de miles
   */
  const formatearNumero = (num: number): string => {
    return new Intl.NumberFormat('es-CO').format(num)
  }

  /**
   * Obtener clase CSS para porcentajes de cambio
   */
  const obtenerClasePorcentaje = (porcentaje: number): string => {
    if (porcentaje >= 0) {
      return 'bg-green-50 text-green-600 hover:bg-green-100'
    } else {
      return 'bg-red-50 text-red-600 hover:bg-red-100'
    }
  }

  /**
   * Listener para detectar cuando se crea un nuevo caso
   */
  const handleCaseCreated = (event: CustomEvent) => {
    // Recargar métricas y casos urgentes cuando se crea un nuevo caso
    cargarMetricas()
    cargarCasosUrgentes()
  }

  // Configurar listeners al montar
  onMounted(() => {
    // Agregar listener para eventos de creación de casos
    window.addEventListener('case-created', handleCaseCreated as EventListener)
  })

  // Limpiar listeners al desmontar
  onUnmounted(() => {
    window.removeEventListener('case-created', handleCaseCreated as EventListener)
  })

  return {
    // Estados
    isLoading,
    error,
    metricas,
    casosPorMes,
    casosUrgentes,
    estadisticasOportunidad,
    estadisticasMuestras,
    
    // Estados de carga individuales
    loadingMetricas,
    loadingCasosPorMes,
    loadingCasosUrgentes,
    loadingOportunidad,
    loadingMuestras,
    
    // Computed
    totalCasosAño,
    añoActual,
    
    // Métodos
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