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
  MuestraStats,
  CaseStatus
} from '../types/dashboard.types'
import { CasePriority } from '../types/dashboard.types'

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
      // Endpoint según documentación: GET /api/v1/casos/estadisticas
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas`)
      const data = response?.data ?? response
      
      // Validar que los datos tengan la estructura esperada según documentación
      return {
        total_casos: data.total_casos || 0,
        casos_en_proceso: data.casos_en_proceso || 0,
        casos_por_firmar: data.casos_por_firmar || 0,
        casos_por_entregar: data.casos_por_entregar || 0,
        casos_completados: data.casos_completados || 0,
        casos_vencidos: data.casos_vencidos || 0,
        casos_sin_patologo: data.casos_sin_patologo || 0,
        tiempo_promedio_procesamiento: data.tiempo_promedio_procesamiento || null,
        casos_mes_actual: data.casos_mes_actual || 0,
        casos_mes_anterior: data.casos_mes_anterior || 0,
        casos_semana_actual: data.casos_semana_actual || 0,
        cambio_porcentual: data.cambio_porcentual || 0,
        casos_por_patologo: data.casos_por_patologo || {},
        casos_por_tipo_prueba: data.casos_por_tipo_prueba || {}
      }
    } catch (error) {
      console.error('Error obteniendo estadísticas de casos:', error)
      throw error
    }
  }

  async getEstadisticasMuestras(): Promise<MuestraStats> {
    try {
      // Endpoint según documentación: GET /api/v1/casos/estadisticas-muestras
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-muestras`)
      const data = response?.data ?? response
      
      // Validar estructura según documentación
      return {
        total_muestras: data.total_muestras || 0,
        muestras_mes_anterior: data.muestras_mes_anterior || 0,
        muestras_mes_anterior_anterior: data.muestras_mes_anterior_anterior || 0,
        cambio_porcentual: data.cambio_porcentual || 0,
        muestras_por_region: data.muestras_por_region || {},
        muestras_por_tipo_prueba: data.muestras_por_tipo_prueba || {},
        tiempo_promedio_procesamiento: data.tiempo_promedio_procesamiento || 0
      }
    } catch (error) {
      console.error('Error obteniendo estadísticas de muestras:', error)
      throw error
    }
  }

  async getMetricasDashboard(): Promise<DashboardMetrics> {
    try {
      const [casosStats, pacientesStats] = await Promise.all([
        this.getEstadisticasCasos(),
        this.getEstadisticasPacientes()
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
      console.error('Error obteniendo métricas del dashboard:', error)
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
      // Endpoint según documentación: GET /api/v1/casos/casos-por-mes/{year}
      // Rango permitido: 2020-2030
      if (añoActual < 2020 || añoActual > 2030) {
        console.warn(`Año ${añoActual} fuera del rango permitido (2020-2030)`)
        return defaultResponse
      }

      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/casos-por-mes/${añoActual}`)
      const data = response?.data ?? response
      
      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) {
        console.warn('Estructura de datos inválida para casos por mes')
        return defaultResponse
      }
      
      return {
        datos: data.datos,
        total: data.total || 0,
        año: data.año || añoActual
      }
    } catch (error) {
      console.error(`Error obteniendo casos por mes para ${añoActual}:`, error)
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
        codigo: caso.caso_code || caso.codigo || caso.id || 'N/A',
        paciente: {
          nombre: caso.paciente?.nombre || 'N/A',
          cedula: caso.paciente?.paciente_code || caso.paciente?.cedula || 'N/A',
          entidad: caso.paciente?.entidad_info?.nombre || 'Sin entidad'
        },
        pruebas,
        patologo: caso.patologo_asignado?.nombre || 'Sin asignar',
        fecha_creacion: caso.fecha_creacion,
        estado: caso.estado as CaseStatus,
        prioridad: (caso.prioridad as CasePriority) || CasePriority.Normal,
        dias_en_sistema: diasEnSistema
      }
    })
  }
}

export const dashboardApiService = new DashboardApiService()
export default dashboardApiService