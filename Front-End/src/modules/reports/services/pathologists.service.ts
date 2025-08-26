import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PathologistMetrics, PathologistsReportData } from '../types/pathologists.types'

export class PathologistsApiService {
  private readonly baseCases = API_CONFIG.ENDPOINTS.CASES

  async getMonthlyPathologists(month?: number, year?: number): Promise<PathologistsReportData> {
    try {
      const params: Record<string, any> = {}
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      
      const resp: any = await apiClient.get(`${this.baseCases}/estadisticas-oportunidad-mensual-detalle`, { params })
      const data = resp?.data ?? resp
      return this.mapApiToFront(data)
    } catch (err) {
      console.warn('Fallo en /estadisticas-oportunidad-mensual-detalle. Se intenta fallback /estadisticas', err)
      try {
        const url2 = `${this.baseCases}/estadisticas`
        const resp2: any = await apiClient.get(url2)
        const data2 = resp2?.data ?? resp2
        return this.mapGeneralStatsToFront(data2)
      } catch (err2) {
        console.error('Fallo en /estadisticas', err2)
        return { pathologists: [] }
      }
    }
  }

  private mapApiToFront(raw: any): PathologistsReportData {
    const pathologists: PathologistMetrics[] = []

    // Mapeo flexible de patólogos
    const patoBlocks: any[] = raw?.patologos || raw?.rendimiento_patologos || raw?.pathologists || []
    if (Array.isArray(patoBlocks)) {
      for (const p of patoBlocks) {
        pathologists.push({
          name: String(p.nombre || p.name || p.patologo || ''),
          withinOpportunity: Number(p.dentroOportunidad || p.within || p.en_oportunidad || 0),
          outOfOpportunity: Number(p.fueraOportunidad || p.out || p.fuera || 0),
          avgTime: Number(p.tiempoPromedio || p.avgTime || p.tiempo || 0)
        })
      }
    }

    // Mapeo del resumen
    const res = raw?.resumen || {}
    const summary = {
      total: Number(res.total || 0),
      within: Number(res.dentro || 0),
      out: Number(res.fuera || 0)
    }

    return { pathologists, summary }
  }

  private mapGeneralStatsToFront(raw: any): PathologistsReportData {
    // Este endpoint no trae detalle de patólogos; solo podemos mapear como totales
    const pathologists: PathologistMetrics[] = []
    const casosPorPatologo = raw?.casos_por_patologo || raw?.by_pathologist || {}
    
    if (casosPorPatologo && typeof casosPorPatologo === 'object') {
      for (const [name, total] of Object.entries(casosPorPatologo)) {
        pathologists.push({ 
          name, 
          withinOpportunity: Number(total), 
          outOfOpportunity: 0, 
          avgTime: 0 
        })
      }
    }
    
    return { pathologists }
  }

  async getPathologistEntities(pathologistName: string, month?: number, year?: number): Promise<any> {
    try {
      const params: Record<string, any> = { patologo: pathologistName }
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      
      console.log('Llamando API entidades con params:', params) // Debug temporal
      const resp: any = await apiClient.get(`${this.baseCases}/entidades-por-patologo`, { params })
      const data = resp?.data ?? resp
      console.log('Respuesta API entidades:', data) // Debug temporal
      return data
    } catch (error) {
      console.error('Error obteniendo entidades del patólogo:', error)
      throw new Error('Error de conexión con el servidor')
    }
  }

  async getPathologistTests(pathologistName: string, month?: number, year?: number): Promise<any> {
    try {
      const params: Record<string, any> = { patologo: pathologistName }
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      
      const resp: any = await apiClient.get(`${this.baseCases}/pruebas-por-patologo`, { params })
      const data = resp?.data ?? resp
      return data
    } catch (error) {
      console.error('Error obteniendo pruebas del patólogo:', error)
      throw new Error('Error de conexión con el servidor')
    }
  }
}

export const pathologistsApiService = new PathologistsApiService()
