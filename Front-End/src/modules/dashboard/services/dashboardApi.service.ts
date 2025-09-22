import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  CasosPorMesResponse,
  CasoUrgente,
  DashboardMetrics,
  EstadisticasOportunidad,
  CaseStatus
} from '../types/dashboard.types'
import { CasePriority } from '../types/dashboard.types'

class DashboardApiService {
  private readonly baseUrl = API_CONFIG.ENDPOINTS


  async getMetricasDashboard(): Promise<DashboardMetrics> {
    return this._getMetricas(`${this.baseUrl.CASES}/statistics/metrics/general`, { no_cache: true })
  }

  async getMetricasPatologo(): Promise<DashboardMetrics> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = authStore.user?.pathologist_code || ''
      
      if (!code) {
        // Si no hay código de patólogo, usar endpoint general
        return this.getMetricasDashboard()
      }
      
      // Usar endpoint específico de patólogo
      return this._getMetricas(`${this.baseUrl.CASES}/statistics/metrics/pathologist/${code}`, { no_cache: true })
    } catch (error) {
      console.error('[Dashboard API] Error en getMetricasPatologo:', error)
      return this.getMetricasDashboard()
    }
  }

  private async _getMetricas(url: string, params?: any): Promise<DashboardMetrics> {
    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      return {
        pacientes: {
          mes_actual: Number(data?.pacientes?.mes_actual ?? 0),
          mes_anterior: Number(data?.pacientes?.mes_anterior ?? 0),
          cambio_porcentual: Number(data?.pacientes?.cambio_porcentual ?? 0)
        },
        casos: {
          mes_actual: Number(data?.casos?.mes_actual ?? 0),
          mes_anterior: Number(data?.casos?.mes_anterior ?? 0),
          cambio_porcentual: Number(data?.casos?.cambio_porcentual ?? 0)
        }
      }
    } catch {
      return { pacientes: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 }, casos: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 } }
    }
  }

  async getCasosPorMes(año?: number): Promise<CasosPorMesResponse> {
    // Usar nuevo endpoint de estadísticas
    return this._getCasosPorMes(`${this.baseUrl.CASES}/statistics/dashboard/cases-by-month/${año || new Date().getFullYear()}`, { no_cache: true })
  }

  async getCasosPorMesPatologo(año?: number): Promise<CasosPorMesResponse> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = authStore.user?.pathologist_code || ''
      
      if (!code) {
        // Si no hay código de patólogo, usar endpoint general
        return this.getCasosPorMes(año)
      }
      // Usar nuevo endpoint de estadísticas por patólogo
      return this._getCasosPorMes(`${this.baseUrl.CASES}/statistics/dashboard/cases-by-month/pathologist/${año || new Date().getFullYear()}`, { 
        pathologist_code: code, 
        no_cache: true 
      })
    } catch (error) {
      console.error('[Dashboard API] Error en getCasosPorMesPatologo:', error)
      return this.getCasosPorMes(año)
    }
  }

  private async _getCasosPorMes(url: string, params?: any): Promise<CasosPorMesResponse> {
    const añoActual = new Date().getFullYear()
    const defaultResponse = { datos: Array(12).fill(0), total: 0, año: añoActual }

    try {
      if (añoActual < 2020 || añoActual > 2030) return defaultResponse

      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      
      // Validar que la respuesta tenga la estructura esperada
      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) {
        return defaultResponse
      }
      
      // Los nuevos endpoints ya retornan la estructura correcta
      return { 
        datos: data.datos, 
        total: data.total || 0, 
        año: data.año || añoActual,
        meses: data.meses || ["Ene", "Feb", "Mar", "Abr", "May", "Jun", "Jul", "Ago", "Sep", "Oct", "Nov", "Dic"]
      }
    } catch (error) {
      return defaultResponse
    }
  }

  async getUrgentCasesGeneral(limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/consulta/urgentes`, { limite })
  }

  async getUrgentCasesByPathologist(patologo_code: string, limite: number = 50): Promise<CasoUrgente[]> {
    return this._getUrgentCases(`${this.baseUrl.CASES}/consulta/urgentes/patologo`, { patologo_code, limite })
  }

  private async _getUrgentCases(url: string, params: any): Promise<CasoUrgente[]> {
    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      return this.transformarCasosUrgentesOptimizados(data.casos || [])
    } catch {
      return []
    }
  }


  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/statistics/opportunity/general`, { no_cache: true })
  }

  async getEstadisticasOportunidadPatologo(): Promise<EstadisticasOportunidad> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const code = authStore.user?.pathologist_code || ''

      if (!code) {
        // Si no hay código de patólogo, usar endpoint general
        return this.getEstadisticasOportunidad()
      }

      // Usar endpoint específico de patólogo
      return this._getEstadisticasOportunidad(`${this.baseUrl.CASES}/statistics/opportunity/pathologist/${code}`, { no_cache: true })
    } catch (error) {
      console.error('[Dashboard API] Error en getEstadisticasOportunidadPatologo:', error)
      return this.getEstadisticasOportunidad()
    }
  }

  private async _getEstadisticasOportunidad(url: string, params?: any): Promise<EstadisticasOportunidad> {
    const defaultResponse = {
      porcentaje_oportunidad: 0, cambio_porcentual: 0, tiempo_promedio: 0,
      casos_dentro_oportunidad: 0, casos_fuera_oportunidad: 0, total_casos_mes_anterior: 0,
      mes_anterior: { nombre: 'Mes anterior', inicio: '', fin: '' }
    }

    try {
      const response = await apiClient.get<any>(url, { params: { ...(params || {}), _ts: Date.now() } })
      const data = response?.data ?? response
      
      // La nueva estructura del backend tiene los datos dentro de 'oportunity'
      const opportunityData = data?.oportunity || data
      
      return {
        porcentaje_oportunidad: typeof opportunityData?.porcentaje_oportunidad === 'number' ? opportunityData.porcentaje_oportunidad : 0,
        cambio_porcentual: typeof opportunityData?.cambio_porcentual === 'number' ? opportunityData.cambio_porcentual : 0,
        tiempo_promedio: typeof opportunityData?.tiempo_promedio === 'number' ? opportunityData.tiempo_promedio : 0,
        casos_dentro_oportunidad: typeof opportunityData?.casos_dentro_oportunidad === 'number' ? opportunityData.casos_dentro_oportunidad : 0,
        casos_fuera_oportunidad: typeof opportunityData?.casos_fuera_oportunidad === 'number' ? opportunityData.casos_fuera_oportunidad : 0,
        total_casos_mes_anterior: typeof opportunityData?.total_casos_mes_anterior === 'number' ? opportunityData.total_casos_mes_anterior : 0,
        mes_anterior: {
          nombre: opportunityData?.mes_anterior?.nombre || 'Mes anterior',
          inicio: opportunityData?.mes_anterior?.inicio || '',
          fin: opportunityData?.mes_anterior?.fin || ''
        }
      }
    } catch {
      return defaultResponse
    }
  }

  private transformarCasosUrgentesOptimizados(casos: any[]): CasoUrgente[] {
    return casos.map((caso: any) => ({
      codigo: caso.caso_code || 'N/A',
      paciente: {
        nombre: caso.paciente_nombre || 'N/A',
        cedula: caso.paciente_documento || 'N/A',
        entidad: caso.entidad_nombre || 'Sin entidad'
      },
      pruebas: caso.pruebas || [],
      patologo: caso.patologo_nombre || 'Sin asignar',
      fecha_creacion: caso.fecha_creacion,
      estado: caso.estado as CaseStatus,
      prioridad: (caso.prioridad as CasePriority) || CasePriority.Normal,
      dias_en_sistema: caso.dias_habiles_transcurridos || 0
    }))
  }

}

export const dashboardApiService = new DashboardApiService()
export default dashboardApiService