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
    const response = await apiClient.get<any>(`${this.baseUrl.PATIENTS}/estadisticas`)
    return response?.data ?? response
  }

  async getEstadisticasCasos(): Promise<CasoStats> {
    const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas`)
    const data = response?.data ?? response
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
  }

  async getEstadisticasMuestras(): Promise<MuestraStats> {
    const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas-muestras`)
    const data = response?.data ?? response
    return {
      total_muestras: data.total_muestras || 0,
      muestras_mes_anterior: data.muestras_mes_anterior || 0,
      muestras_mes_anterior_anterior: data.muestras_mes_anterior_anterior || 0,
      cambio_porcentual: data.cambio_porcentual || 0,
      muestras_por_region: data.muestras_por_region || {},
      muestras_por_tipo_prueba: data.muestras_por_tipo_prueba || {},
      tiempo_promedio_procesamiento: data.tiempo_promedio_procesamiento || 0
    }
  }

  async getMetricasDashboard(): Promise<DashboardMetrics> {
    try {
      // Nuevo endpoint mensual (mes actual vs anterior)
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas/mes-actual`)
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
      return {
        pacientes: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 },
        casos: { mes_actual: 0, mes_anterior: 0, cambio_porcentual: 0 }
      }
    }
  }

  async getMetricasPatologo(): Promise<DashboardMetrics> {
    try {
      // Obtener código del patólogo desde el store si es posible
      const code = ''
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas/mes-actual/patologo`, { params: { patologo_codigo: code } })
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
      return await this._getMetricasPatologoFallback()
    }
  }

  private async _getMetricasPatologoFallback(): Promise<DashboardMetrics> {
    try {
      const { useAuthStore } = await import('@/stores/auth.store')
      const authStore = useAuthStore()
      const user = authStore.user
      
      if (!user || user.rol !== 'patologo') return await this.getMetricasDashboard()

      const patologosResponse = await apiClient.get(`${this.baseUrl.PATHOLOGISTS}/search?q=${user.nombre}`)
      let patologos = patologosResponse.data || []
      
      if (patologos.length === 0) {
        const patologosEmailResponse = await apiClient.get(`${this.baseUrl.PATHOLOGISTS}/search?q=${user.email}`)
        const patologosEmail = patologosEmailResponse.data || []
        if (patologosEmail.length === 0) return await this.getMetricasDashboard()
        patologos.push(...patologosEmail)
      }

      const nombreUsuarioLower = (user.nombre || '').toLowerCase()
      const patologoEncontrado = patologos.find((p: any) => {
        if (!p.patologo_name) return false
        const nombrePatologo = p.patologo_name.toLowerCase()
        return nombrePatologo.includes(nombreUsuarioLower) || 
               nombreUsuarioLower.includes(nombrePatologo) ||
               (p.iniciales_patologo && p.iniciales_patologo.toLowerCase().includes(nombreUsuarioLower))
      })

      if (!patologoEncontrado) return await this.getMetricasDashboard()

      const casosResponse = await apiClient.get(`${this.baseUrl.CASES}/patologo/${patologoEncontrado.patologo_code}`)
      const casos = casosResponse.data || []

      return {
        pacientes: this._calcularMetricasPacientes(casos),
        casos: this._calcularMetricasCasos(casos)
      }
    } catch {
      return await this.getMetricasDashboard()
    }
  }

  private _calcularMetricasCasos(casos: any[]): any {
    const ahora = new Date()
    const inicioMesActual = new Date(ahora.getFullYear(), ahora.getMonth(), 1)
    const inicioMesAnterior = new Date(ahora.getFullYear(), ahora.getMonth() - 1, 1)
    const inicioMesAnteriorAnterior = new Date(ahora.getFullYear(), ahora.getMonth() - 2, 1)

    const casosMesActual = casos.filter(caso => new Date(caso.fecha_creacion) >= inicioMesActual).length
    const casosMesAnterior = casos.filter(caso => {
      const fecha = new Date(caso.fecha_creacion)
      return fecha >= inicioMesAnterior && fecha < inicioMesActual
    }).length
    const casosMesAnteriorAnterior = casos.filter(caso => {
      const fecha = new Date(caso.fecha_creacion)
      return fecha >= inicioMesAnteriorAnterior && fecha < inicioMesAnterior
    }).length

    const cambioPorcentual = casosMesAnteriorAnterior > 0 
      ? Math.round(((casosMesAnterior - casosMesAnteriorAnterior) / casosMesAnteriorAnterior) * 100)
      : casosMesAnterior > 0 ? 100 : 0

    return { mes_actual: casosMesActual, mes_anterior: casosMesAnterior, cambio_porcentual: cambioPorcentual }
  }

  private _calcularMetricasPacientes(casos: any[]): any {
    const ahora = new Date()
    const inicioMesActual = new Date(ahora.getFullYear(), ahora.getMonth(), 1)
    const inicioMesAnterior = new Date(ahora.getFullYear(), ahora.getMonth() - 1, 1)

    const casosMesActual = casos.filter(caso => new Date(caso.fecha_creacion) >= inicioMesActual)
    const casosMesAnterior = casos.filter(caso => {
      const fecha = new Date(caso.fecha_creacion)
      return fecha >= inicioMesAnterior && fecha < inicioMesActual
    })

    const pacientesMesActual = [...new Set(casosMesActual.map(caso => caso.paciente?.id).filter(Boolean))].length
    const pacientesMesAnterior = [...new Set(casosMesAnterior.map(caso => caso.paciente?.id).filter(Boolean))].length

    const cambioPorcentual = pacientesMesAnterior > 0 
      ? Math.round(((pacientesMesActual - pacientesMesAnterior) / pacientesMesAnterior) * 100)
      : pacientesMesActual > 0 ? 100 : 0

    return { mes_actual: pacientesMesActual, mes_anterior: pacientesMesAnterior, cambio_porcentual: cambioPorcentual }
  }

  async getCasosPorMes(año?: number): Promise<CasosPorMesResponse> {
    const añoActual = año || new Date().getFullYear()
    const defaultResponse = { datos: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], total: 0, año: añoActual }

    try {
      if (añoActual < 2020 || añoActual > 2030) return defaultResponse

      // Endpoint nuevo de estadísticas para mensual por laboratorio
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas/por-mes/${añoActual}`)
      const data = response?.data ?? response
      
      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) return defaultResponse
      
      return { datos: data.datos, total: data.total || 0, año: data.año || añoActual }
    } catch {
      return defaultResponse
    }
  }

  async getCasosPorMesPatologo(año?: number): Promise<CasosPorMesResponse> {
    const añoActual = año || new Date().getFullYear()
    const defaultResponse = { datos: [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0], total: 0, año: añoActual }

    try {
      if (añoActual < 2020 || añoActual > 2030) return defaultResponse

      // Endpoint nuevo de estadísticas para mensual por patólogo
      const response = await apiClient.get<any>(`${this.baseUrl.CASES}/estadisticas/por-mes/patologo/${añoActual}`)
      const data = response?.data ?? response
      
      if (!data || !Array.isArray(data.datos) || data.datos.length !== 12) return defaultResponse
      
      return { datos: data.datos, total: data.total || 0, año: data.año || añoActual }
    } catch {
      return await this.getCasosPorMes(año)
    }
  }

  async getCasosUrgentes(filtros: FiltrosCasosUrgentes = {}): Promise<CasoUrgente[]> {
    const searchParams: any = {}
    if (filtros.patologo) searchParams.patologo_codigo = filtros.patologo
    if (filtros.estado) searchParams.estado = filtros.estado
      
    const url = `${this.baseUrl.CASES}/buscar?skip=0&limit=1000`
    const response = await apiClient.post<any>(url, searchParams)
    const data = Array.isArray(response) ? response : (response?.data ?? response?.items ?? [])
    
    const todosCasos = this.transformarCasosUrgentes(data)
    const casosUrgentes = todosCasos.filter(caso => caso.dias_en_sistema >= 5 && caso.estado !== 'Completado')
    
    casosUrgentes.sort((a, b) => {
      const getNumeroFromCodigo = (codigo: string): number => {
        const match = codigo.match(/(\d{4})-(\d{5})/)
        return match ? parseInt(match[1]) * 100000 + parseInt(match[2]) : 0
      }
      return getNumeroFromCodigo(b.codigo) - getNumeroFromCodigo(a.codigo)
    })
    
    return casosUrgentes.slice(0, filtros.limite || casosUrgentes.length)
  }

  async getEstadisticasOportunidad(): Promise<EstadisticasOportunidad> {
    const defaultResponse = {
      porcentaje_oportunidad: 0, cambio_porcentual: 0, tiempo_promedio: 0,
      casos_dentro_oportunidad: 0, casos_fuera_oportunidad: 0, total_casos_mes_anterior: 0,
      mes_anterior: { nombre: 'Mes anterior', inicio: '', fin: '' }
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
    } catch {
      return defaultResponse
    }
  }

  private transformarCasosUrgentes(casos: any[]): CasoUrgente[] {
    return casos.map((caso: any) => {
      const fechaCreacion = new Date(caso.fecha_creacion)
      const diasEnSistema = Math.floor((Date.now() - fechaCreacion.getTime()) / (1000 * 60 * 60 * 24))

      const pruebas: string[] = []
      if (caso.muestras?.length) {
        caso.muestras.forEach((muestra: any) => {
          if (muestra.pruebas?.length) {
            muestra.pruebas.forEach((prueba: any) => {
              const code = prueba.id || ''
              const name = prueba.nombre || ''
              if (code) pruebas.push(name ? `${code} - ${name}` : code)
              else if (name) pruebas.push(name)
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