import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

class TestSearchService {
  private readonly endpoint = API_CONFIG.ENDPOINTS.TESTS

  async searchTests(query: string, includeInactive: boolean = false): Promise<any[]> {
    try {
      const q = query?.trim()
      if (!q) return []

      const results: any[] = []

      // 1) Exact match by code
      const byCode = await this.getTestByCode(q)
      if (byCode) results.push(byCode)

      // 2) Direct fetch by id (if looks like ObjectId or UUID)
      if (this.looksLikeId(q)) {
        try {
          const byIdResp = await apiClient.get(`${this.endpoint}/${q}`)
          if (byIdResp) results.push(this.normalizeTest(byIdResp))
        } catch {}
      }

      // 3) Name/code contains search (active or including inactive)
      const endpoint = includeInactive 
        ? `${this.endpoint}/inactive`
        : `${this.endpoint}/`
      const params = { query: q, limit: 50 }
      try {
        const response = await apiClient.get(endpoint, { params })
        const list = Array.isArray(response) ? response : []
        results.push(...list.map((t: any) => this.normalizeTest(t)))
      } catch (e: any) {
        if (e?.response?.status !== 404) throw e
      }

      // 4) Deduplicate by code/id and prioritize exact code or exact name matches
      const seen = new Set<string>()
      const deduped: any[] = []
      for (const item of results) {
        const key = (item.codigo || '') + '|' + (item.id || '')
        if (!seen.has(key)) {
          seen.add(key)
          deduped.push(item)
        }
      }

      deduped.sort((a, b) => {
        const aExactCode = a.codigo?.toUpperCase() === q.toUpperCase() ? 1 : 0
        const bExactCode = b.codigo?.toUpperCase() === q.toUpperCase() ? 1 : 0
        if (aExactCode !== bExactCode) return bExactCode - aExactCode
        const aExactName = a.nombre?.toLowerCase() === q.toLowerCase() ? 1 : 0
        const bExactName = b.nombre?.toLowerCase() === q.toLowerCase() ? 1 : 0
        return bExactName - aExactName
      })

      return deduped
    } catch (error: any) {
      if (error.response?.status === 404) {
        return []
      }
      throw new Error(error.message || 'Error al buscar pruebas')
    }
  }

  async getTestByCode(code: string): Promise<any | null> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${code}`)
      
      if (response) {
        return this.normalizeTest(response)
      }

      return null
    } catch (error: any) {
      if (error.response?.status === 404) {
        return null
      }
      throw new Error(error.message || 'Error al obtener la prueba')
    }
  }

  private looksLikeId(value: string): boolean {
    const v = value.trim()
    const isHex24 = /^[a-fA-F0-9]{24}$/.test(v)
    const isUuid = /^[0-9a-fA-F]{8}-[0-9a-fA-F]{4}-[1-5][0-9a-fA-F]{3}-[89abAB][0-9a-fA-F]{3}-[0-9a-fA-F]{12}$/.test(v)
    return isHex24 || isUuid
  }

  private normalizeTest(test: any) {
    const name = test.name || test.test_name || test.prueba_name || test.pruebasName || test.nombre || ''
    const code = test.test_code || test.prueba_code || test.pruebaCode || test.codigo || test.code || ''
    const description = test.description || test.test_description || test.prueba_description || test.pruebasDescription || test.descripcion || ''
    const time = test.time || test.tiempo || 1
    const price = test.price || test.precio || 0
    const isActive = test.is_active !== undefined ? test.is_active : (test.isActive !== undefined ? test.isActive : test.activo)
    
    return {
      id: test._id || test.id,
      nombre: name,
      codigo: code,
      descripcion: description,
      tiempo: time,
      precio: price,
      activo: isActive,
      tipo: 'pruebas',
      fecha_creacion: test.created_at || test.fecha_creacion,
      fecha_actualizacion: test.updated_at || test.fecha_actualizacion
    }
  }
}

export const testSearchService = new TestSearchService()
export default testSearchService
