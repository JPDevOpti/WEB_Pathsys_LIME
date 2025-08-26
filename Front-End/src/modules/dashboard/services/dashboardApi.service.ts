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

/**
 * Servicio para las APIs del dashboard
 */
class DashboardApiService {
  private readonly baseUrl = API_CONFIG.ENDPOINTS

  constructor() {
    // Dashboard API Service inicializado
  }

  /**
   * Obtener estadísticas de pacientes
   */
  async getEstadisticasPacientes(): Promise<PacienteStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.PATIENTS}/estadisticas`)
      const data = response?.data ?? response
      return data as PacienteStats
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener estadísticas de casos
   */
  async getEstadisticasCasos(): Promise<CasoStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas`)
      const data = response?.data ?? response
      return data as CasoStats
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener estadísticas de muestras
   */
  async getEstadisticasMuestras(): Promise<MuestraStats> {
    try {
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-muestras`)
      const data = response?.data ?? response
      return data as MuestraStats
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener métricas principales del dashboard
   */
  async getMetricasDashboard(): Promise<DashboardMetrics> {
    try {
      // Obtener estadísticas de pacientes y casos en paralelo
      const [pacientesStats, casosStats] = await Promise.all([
        this.getEstadisticasPacientes(),
        this.getEstadisticasCasos()
      ])

      return {
        pacientes: {
          mes_actual: pacientesStats.pacientes_mes_actual,
          mes_anterior: pacientesStats.pacientes_mes_anterior,
          cambio_porcentual: pacientesStats.cambio_porcentual
        },
        casos: {
          mes_actual: casosStats.casos_mes_actual,
          mes_anterior: casosStats.casos_mes_anterior,
          cambio_porcentual: casosStats.cambio_porcentual
        }
      }
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener casos por mes del año actual
   */
  async getCasosPorMes(año?: number): Promise<CasosPorMesResponse> {
    try {
      const añoActual = año || new Date().getFullYear()
      
      // Conectar con el endpoint real del backend
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/casos-por-mes/${añoActual}`)
      const data = response?.data ?? response
      
      // Validar y asegurar que los datos tengan el formato correcto
      const validatedData = data as CasosPorMesResponse
      
      // Si no hay datos o no es un array válido, devolver datos por defecto
      if (!validatedData || !Array.isArray(validatedData.datos)) {
        return {
          datos: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
          total: 0,
          año: añoActual
        }
      }
      
      return validatedData
    } catch (error) {
      // En caso de error, devolver datos por defecto
      const añoActual = año || new Date().getFullYear()
      return {
        datos: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0],
        total: 0,
        año: añoActual
      }
    }
  }

  /**
   * Obtener casos urgentes (últimos 1000 casos, filtrados por urgencia)
   */
  async getCasosUrgentes(filtros: FiltrosCasosUrgentes = {}): Promise<CasoUrgente[]> {
    try {
      // Usar el endpoint de búsqueda para filtros avanzados
      const searchParams: any = {}
      
      // Mapear parámetros al formato de búsqueda del backend
      if (filtros.patologo) {
        searchParams.patologo_codigo = filtros.patologo
      }
      
      if (filtros.estado) {
        searchParams.estado = filtros.estado
      }
      
      // SIEMPRE usar el endpoint de búsqueda para obtener ordenamiento correcto
      // El endpoint de búsqueda ordena por fecha_creacion DESC (más recientes primero)
      const url = `${this.baseUrl.CASES}/buscar?skip=0&limit=1000`
      const response = await apiClient.post<any>(url, searchParams)
      const data = Array.isArray(response) ? response : (response?.data ?? response?.items ?? [])
      
      // Transformar todos los casos
      const todosCasos = this.transformarCasosUrgentes(data)
      
      // Filtrar casos urgentes (más de 6 días en el sistema y no completados)
      const casosUrgentes = todosCasos.filter(caso => {
        const esUrgente = caso.dias_en_sistema > 6 && caso.estado !== 'Completado'
        return esUrgente
      })
      
      // Ordenar casos urgentes por código de caso (más alto = más reciente primero)
      casosUrgentes.sort((a, b) => {
        // Extraer el número del código de caso (formato: YYYY-NNNNN)
        const getNumeroFromCodigo = (codigo: string): number => {
          const match = codigo.match(/(\d{4})-(\d{5})/)
          if (match) {
            const año = parseInt(match[1])
            const numero = parseInt(match[2])
            // Crear un número único combinando año y número consecutivo
            return año * 100000 + numero
          }
          return 0
        }
        
        const numeroA = getNumeroFromCodigo(a.codigo)
        const numeroB = getNumeroFromCodigo(b.codigo)
        
        // Ordenar por código descendente (más alto primero = más reciente)
        return numeroB - numeroA
      })
      
      // Aplicar límite final si se especifica
      const limite = filtros.limite || casosUrgentes.length
      const casosLimitados = casosUrgentes.slice(0, limite)
      
      return casosLimitados
      
    } catch (error) {
      throw error
    }
  }

  /**
   * Obtener estadísticas de oportunidad mensual
   */
  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    try {
      // Usar el endpoint del backend que ya calcula correctamente las estadísticas
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-oportunidad-mensual`)
      const data = response?.data ?? response
      
      // Transformar la respuesta del backend al formato esperado por el frontend
      const backendData = data as any
      
      const result = {
        porcentaje_oportunidad: typeof backendData?.porcentaje_oportunidad === 'number' ? backendData.porcentaje_oportunidad : 0,
        cambio_porcentual: typeof backendData?.cambio_porcentual === 'number' ? backendData.cambio_porcentual : 0,
        tiempo_promedio: typeof backendData?.tiempo_promedio === 'number' ? backendData.tiempo_promedio : 0,
        casos_dentro_oportunidad: typeof backendData?.casos_dentro_oportunidad === 'number' ? backendData.casos_dentro_oportunidad : 0,
        casos_fuera_oportunidad: typeof backendData?.casos_fuera_oportunidad === 'number' ? backendData.casos_fuera_oportunidad : 0,
        total_casos_mes_anterior: typeof backendData?.total_casos_mes_anterior === 'number' ? backendData.total_casos_mes_anterior : 0,
        mes_anterior: {
          nombre: backendData?.mes_anterior?.nombre || 'Mes anterior',
          inicio: backendData?.mes_anterior?.inicio || '',
          fin: backendData?.mes_anterior?.fin || ''
        }
      }
      
      return result
    } catch (error) {
      // En caso de error, devolver datos por defecto
      return {
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
    }
  }



  /**
   * Transformar casos del backend al formato de casos urgentes
   */
  private transformarCasosUrgentes(casos: any[]): CasoUrgente[] {
    return casos.map((caso: any) => {
      const fechaCreacion = new Date(caso.fecha_creacion)
      const hoy = new Date()
      const diasEnSistema = Math.floor((hoy.getTime() - fechaCreacion.getTime()) / (1000 * 60 * 60 * 24))

      // Extraer pruebas de las muestras (formato "CODIGO - NOMBRE")
      const pruebas: string[] = []
      if (caso.muestras && Array.isArray(caso.muestras)) {
        caso.muestras.forEach((muestra: any) => {
          if (muestra.pruebas && Array.isArray(muestra.pruebas)) {
            muestra.pruebas.forEach((prueba: any) => {
              // Extraer código y nombre de la prueba
              const code = prueba.id || ''
              const name = prueba.nombre || ''
              
              // Crear formato "CODIGO - NOMBRE" como en case-list
              if (code) {
                const pruebaFormateada = name ? `${code} - ${name}` : code
                pruebas.push(pruebaFormateada)
              } else if (name) {
                // Si no hay código pero hay nombre, usar el nombre
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
        pruebas: pruebas,
        patologo: caso.patologo_asignado?.nombre || 'Sin asignar',
        fecha_creacion: caso.fecha_creacion,
        estado: caso.estado,
        dias_en_sistema: diasEnSistema
      }
    })
  }


}

// Exportar instancia singleton
export const dashboardApiService = new DashboardApiService()
export default dashboardApiService