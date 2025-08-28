import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type {
  PacienteStats,
  CasoStats,
  CasosPorMesResponse,
  CasoUrgente,
  DashboardMetrics,
  EstadisticasOportunidad,
  FiltrosCasosUrgentes,
  MuestraStats
} from '../types/dashboard.types'

class DashboardApiService {
  private readonly baseUrl = API_CONFIG.ENDPOINTS

  async getEstadisticasPacientes(): Promise<PacienteStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.PATIENTS}/estadisticas`)
      return response?.data ?? response
    } catch (error) {
      throw error
    }
  }

  async getEstadisticasCasos(): Promise<CasoStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas`)
      return response?.data ?? response
    } catch (error) {
      throw error
    }
  }

  async getEstadisticasMuestras(): Promise<MuestraStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-muestras`)
      return response?.data ?? response
    } catch (error) {
      throw error
    }
  }

  async getMetricasDashboard(): Promise<DashboardMetrics> {
    try {
      const [pacientesStats, casosStats] = await Promise.all([
        this.getEstadisticasPacientes(),
        this.getEstadisticasCasos()
      ])

      return {
        pacientes: {
          mes_actual: pacientesStats.pacientes_mes_actual || 0,
          mes_anterior: pacientesStats.pacientes_mes_anterior || 0,
          cambio_porcentual: pacientesStats.cambio_porcentual || 0
        },
        casos: {
          mes_actual: casosStats.casos_mes_actual || 0,
          mes_anterior: casosStats.casos_mes_anterior || 0,
          cambio_porcentual: casosStats.cambio_porcentual || 0
        }
      }
    } catch (error) {
      return {
        pacientes: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 },
        casos: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 }
      }
    }
  }

  async getCasosPorMes(año?: number): Promise<CasosPorMesResponse> {
    const añoActual = año || new Date().getFullYear()
    const defaultResponse = {
      datos: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
      total: 0,
      año: añoActual
    }

    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/casos-por-mes/${añoActual}`)
      const data = response?.data ?? response
      
      if (!data || !Array.isArray(data.datos)) {
        return defaultResponse
      }
      
      return data as CasosPorMesResponse
    } catch (error) {
      return defaultResponse
    }
  }

  async getCasosUrgentes(filtros: FiltrosCasosUrgentes = {}): Promise<CasoUrgente[]> {
    try {
      const searchParams: any = {}
      
      if (filtros.patologo) {
        searchParams.patologo_codigo = filtros.patologo
      }
      
      if (filtros.estado) {
        searchParams.estado = filtros.estado
      }
      
      const url = `${this.baseUrl.CASES}/buscar?skip=0&limit=1000`
      const response = await apiClient.post<any>(url, searchParams)
      const data = Array.isArray(response) ? response : (response?.data ?? response?.items ?? [])
      
      const todosCasos = this.transformarCasosUrgentes(data)
      
      const casosUrgentes = todosCasos.filter(caso => 
        caso.dias_en_sistema > 6 && caso.estado !== 'Completado'
      )
      
      casosUrgentes.sort((a, b) => {
        const getNumeroFromCodigo = (codigo: string): number => {
          const match = codigo.match(/(\d{4})-(\d{5})/)
          if (match) {
            const año = parseInt(match[1])
            const numero = parseInt(match[2])
            return año * 100000 + numero
          }
          return 0
        }
        
        return getNumeroFromCodigo(b.codigo) - getNumeroFromCodigo(a.codigo)
      })
      
      const limite = filtros.limite || casosUrgentes.length
      return casosUrgentes.slice(0, limite)
      
    } catch (error) {
      throw error
    }
  }

  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    const defaultResponse = {
      porcentaje_oportunidad: 0,
      cambio_porcentual: 0,
      tiempo_promedio: 0,
      casos_dentro_oportunidad: 0,
      casos_fuera_oportunidad: 0,
      total_casos_mes_anterior: 0,
      mes_anterior: {
        nombre: 'Mes anterior',
        inicio: '',
        fin: ''
      }
    }

    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-oportunidad-mensual`)
      const data = response?.data ?? response
      
      return {
        porcentaje_oportunidad: typeof data?.porcentaje_oportunidad === 'number' ? data.porcentaje_oportunidad : 0,
        cambio_porcentual: typeof data?.cambio_porcentual === 'number' ? data.cambio_porcentual : 0,
        tiempo_promedio: typeof data?.tiempo_promedio === 'number' ? data.tiempo_promedio : 0,
        casos_dentro_oportunidad: typeof data?.casos_dentro_oportunidad === 'number' ? data.casos_dentro_oportunidad : 0,
        casos_fuera_oportunidad: typeof data?.casos_fuera_oportunidad === 'number' ? data.casos_fuera_oportunidad : 0,
        total_casos_mes_anterior: typeof data?.total_casos_mes_anterior === 'number' ? data.total_casos_mes_anterior : 0,
        mes_anterior: {
          nombre: data?.mes_anterior?.nombre || 'Mes anterior',
          inicio: data?.mes_anterior?.inicio || '',
          fin: data?.mes_anterior?.fin || ''
        }
      }
    } catch (error) {
      return defaultResponse
    }
  }



  private transformarCasosUrgentes(casos: any[]): CasoUrgente[] {
    return casos.map((caso: any) => {
      const fechaCreacion = new Date(caso.fecha_creacion)
      const hoy = new Date()
      const diasEnSistema = Math.floor((hoy.getTime() - fechaCreacion.getTime()) / (1000 * 60 * 60 * 24))

      const pruebas: string[] = []
      if (caso.muestras && Array.isArray(caso.muestras)) {
        caso.muestras.forEach((muestra: any) => {
          if (muestra.pruebas && Array.isArray(muestra.pruebas)) {
            muestra.pruebas.forEach((prueba: any) => {
              const code = prueba.id || ''
              const name = prueba.nombre || ''
              
              if (code) {
                const pruebaFormateada = name ? `${code} - ${name}` : code
                pruebas.push(pruebaFormateada)
              } else if (name) {
                pruebas.push(name)
              }
            })
          }
        })
      }

      return {
        codigo: caso.CasoCode || caso.codigo || caso.id || 'N/A',
        paciente: {
          nombre: caso.paciente?.nombre || 'N/A',
          cedula: caso.paciente?.cedula || 'N/A',
          entidad: caso.paciente?.entidad_info?.nombre || 'Entidad'
        },
        pruebas,
        patologo: caso.patologo_asignado?.nombre || 'Sin asignar',
        fecha_creacion: caso.fecha_creacion,
        estado: caso.estado,
        dias_en_sistema: diasEnSistema
      }
    })
  }
}

export const dashboardApiService = new DashboardApiService()
export default dashboardApiService