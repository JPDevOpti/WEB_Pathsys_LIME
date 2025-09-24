import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'
import type { PathologistMetrics, PathologistsReportData } from '../types/pathologists.types'

export class PathologistsApiService {
  private readonly baseCases = API_CONFIG.ENDPOINTS.CASES

  async getMonthlyPathologists(month?: number, year?: number): Promise<PathologistsReportData> {
    try {
      const params: Record<string, any> = { thresholdDays: 7 }
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      
      // Use the new optimized endpoint
      const resp: any = await apiClient.get(`${this.baseCases}/statistics/pathologists/monthly-performance`, { params })
      const data = resp?.data ?? resp
      return this.mapApiToFront(data)
    } catch (err) {
      console.error('Error obteniendo datos de patólogos:', err)
      return { pathologists: [] }
    }
  }

  private mapApiToFront(raw: any): PathologistsReportData {
    const pathologists: PathologistMetrics[] = []

    // Mapeo para nuevos endpoints optimizados
    const patoBlocks: any[] = raw?.pathologists || []
    if (Array.isArray(patoBlocks)) {
      for (const p of patoBlocks) {
        pathologists.push({
          code: String(p.code || ''),
          name: String(p.name || ''),
          withinOpportunity: Number(p.withinOpportunity || 0),
          outOfOpportunity: Number(p.outOfOpportunity || 0),
          averageDays: Number(p.averageDays || 0)
        })
      }
    }

    // Calcular resumen desde los datos de patólogos
    const total_within = pathologists.reduce((sum, p) => sum + p.withinOpportunity, 0)
    const total_out = pathologists.reduce((sum, p) => sum + p.outOfOpportunity, 0)
    
    const summary = {
      total: total_within + total_out,
      within: total_within,
      out: total_out
    }

    return { pathologists, summary }
  }


  async getPathologistEntities(pathologistName: string, month?: number, year?: number): Promise<any> {
    try {
      const params: Record<string, any> = { patologo: pathologistName }
      if (typeof month === 'number') params.month = month
      if (typeof year === 'number') params.year = year
      
      // Use the new optimized endpoint
      const resp: any = await apiClient.get(`${this.baseCases}/statistics/pathologists/entities`, { params })
      const data = resp?.data ?? resp
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
      
      // Use the new optimized endpoint
      const resp: any = await apiClient.get(`${this.baseCases}/statistics/pathologists/tests`, { params })
      const data = resp?.data ?? resp
      return data
    } catch (error) {
      console.error('Error obteniendo pruebas del patólogo:', error)
      throw new Error('Error de conexión con el servidor')
    }
  }
}

export const pathologistsApiService = new PathologistsApiService()
