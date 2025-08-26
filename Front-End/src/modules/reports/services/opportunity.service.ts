import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { OpportunityTest, PathologistPerformance } from '../types/opportunity.types'

export interface OpportunityReportData {
  tests: OpportunityTest[]
  pathologists: PathologistPerformance[]
  monthlyPct?: number[]
  summary?: { total: number; within: number; out: number }
}

export class OpportunityApiService {
  private readonly baseCases = API_CONFIG.ENDPOINTS.CASES

  async getMonthlyOpportunity(month?: number, year?: number): Promise<OpportunityReportData> {
    try {
      const params: Record<string, any> = {}
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      const resp: any = await apiClient.get(`${this.baseCases}/estadisticas-oportunidad-mensual-detalle`, { params })
      const data = resp?.data ?? resp
      return this.mapMonthlyApiToFront(data)
    } catch (err) {
      console.warn('Fallo en /estadisticas-oportunidad-mensual. Se intenta fallback /estadisticas', err)
      try {
        const url2 = `${this.baseCases}/estadisticas`
        const resp2: any = await apiClient.get(url2)
        const data2 = resp2?.data ?? resp2
        return this.mapGeneralStatsToFront(data2)
      } catch (err2) {
        console.error('Fallo en /estadisticas', err2)
        return { tests: [], pathologists: [] }
      }
    }
  }

  async getYearlyOpportunity(year: number): Promise<number[]> {
    const url = `${this.baseCases}/oportunidad-por-mes/${year}`
    const resp: any = await apiClient.get(url)
    const data = resp?.data ?? resp
    return Array.isArray(data?.porcentaje_por_mes) ? data.porcentaje_por_mes.map((n: any) => Number(n)) : []
  }

  private mapMonthlyApiToFront(raw: any): OpportunityReportData {
    const tests: OpportunityTest[] = []
    const pathologists: PathologistPerformance[] = []

    // Intentos de mapeo flexible
    const testBlocks: any[] = raw?.pruebas || raw?.detalle_por_prueba || raw?.procedimientos || []
    if (Array.isArray(testBlocks)) {
      for (const t of testBlocks) {
        tests.push({
          code: String(t.codigo || t.codigoPrueba || t.code || ''),
          name: String(t.nombre || t.prueba || t.name || ''),
          withinOpportunity: Number(t.dentroOportunidad || t.within || t.en_oportunidad || 0),
          outOfOpportunity: Number(t.fueraOportunidad || t.out || t.fuera || 0),
          opportunityTime: String(t.tiempoOportunidad || t.tiempo || t.opportunityTime || '')
        })
      }
    }

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

    const monthlyPct = Array.isArray(raw?.porcentaje_por_mes) ? raw.porcentaje_por_mes.map((n: any) => Number(n)) : undefined
    const res = raw?.resumen || {}
    const summary = {
      total: Number(res.total || 0),
      within: Number(res.dentro || 0),
      out: Number(res.fuera || 0)
    }
    return { tests, pathologists, monthlyPct, summary }
  }

  private mapGeneralStatsToFront(raw: any): OpportunityReportData {
    // Este endpoint no trae detalle de oportunidad; solo podemos mapear patólogos como totales
    const pathologists: PathologistPerformance[] = []
    const casosPorPatologo = raw?.casos_por_patologo || raw?.by_pathologist || {}
    if (casosPorPatologo && typeof casosPorPatologo === 'object') {
      for (const [name, total] of Object.entries(casosPorPatologo)) {
        pathologists.push({ name, withinOpportunity: Number(total), outOfOpportunity: 0, avgTime: 0 })
      }
    }
    return { tests: [], pathologists }
  }
}

export const opportunityApiService = new OpportunityApiService()


