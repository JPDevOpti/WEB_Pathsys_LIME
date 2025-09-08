import { apiClient } from '@/core/config/axios.config'

export interface PruebaComplementaria {
  codigo: string
  nombre: string
  cantidad: number
}

export interface CasoAprobacionCreate {
  caso_original: string
  pruebas_complementarias: PruebaComplementaria[]
  motivo: string
}

export interface CasoAprobacionResponse {
  caso_original: string
  estado_aprobacion: 'solicitud_hecha' | 'pendiente_aprobacion' | 'aprobado' | 'rechazado'
  pruebas_complementarias: PruebaComplementaria[]
  aprobacion_info: {
    solicitado_por: string
    fecha_solicitud: string
    motivo: string
    gestionado_por?: string
    fecha_gestion?: string
    aprobado_por?: string
    fecha_aprobacion?: string
    comentarios_aprobacion?: string
    comentarios_gestion?: string
  }
  fecha_creacion: string
  fecha_actualizacion: string
}

export interface CasoAprobacionSearch {
  caso_original?: string
  estado_aprobacion?: string
  solicitado_por?: string
  aprobado_por?: string
  fecha_solicitud_desde?: string
  fecha_solicitud_hasta?: string
  fecha_aprobacion_desde?: string
  fecha_aprobacion_hasta?: string
}

class CasoAprobacionService {
  private readonly baseUrl = '/aprobacion'
  private sanitize<T extends Record<string, any>>(obj: T): CasoAprobacionResponse {
    const data: any = { ...obj }
    // Asegurar que siempre haya un ID válido
    data.id = data.id || data._id || `temp-${Date.now()}`
    delete data._id
    delete data.is_active
    delete data.isActive
    delete data.actualizado_por
    return data as CasoAprobacionResponse
  }

  async createCasoAprobacion(data: CasoAprobacionCreate): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.post(this.baseUrl, data)
      const payload = response.data?.data ?? response.data
      if (!payload) {
        throw new Error('Respuesta vacía del servidor')
      }
      return this.sanitize(payload)
    } catch (error: any) {
      console.error('Error en createCasoAprobacion:', error)
      // Si el error es de validación pero el caso se creó correctamente,
      // intentar obtenerlo por caso_original
      if (error.response?.data?.detail?.includes?.('validation error') && data.caso_original) {
        try {
          const searchResponse = await this.searchCasos({ caso_original: data.caso_original }, 0, 1)
          if (searchResponse.data && searchResponse.data.length > 0) {
            return searchResponse.data[0]
          }
        } catch (searchError) {
          // Si también falla la búsqueda, lanzar el error original
        }
      }
      throw error
    }
  }

  async getCasoAprobacion(id: string): Promise<CasoAprobacionResponse> {
    const response = await apiClient.get(`${this.baseUrl}/${id}`)
    const payload = response.data?.data ?? response.data
    return this.sanitize(payload)
  }

  async searchCasos(
    searchParams: CasoAprobacionSearch,
    skip: number = 0,
    limit: number = 50
  ): Promise<any> {
    const response = await apiClient.post(
      `${this.baseUrl}/search`,
      searchParams,
      { params: { skip, limit } }
    )
    const wrapper = response.data
    const list = (wrapper?.data ?? wrapper)?.map
      ? (wrapper?.data ?? wrapper).map((i: any) => this.sanitize(i))
      : (wrapper?.data ?? []).map((i: any) => this.sanitize(i))
    return { ...wrapper, data: list }
  }

  async getCasosByEstado(estado: string, limit: number = 50): Promise<CasoAprobacionResponse[]> {
    const response = await apiClient.get(`${this.baseUrl}/estado/${estado}`, { params: { limit } })
    const payload = response.data?.data ?? response.data
    return (payload || []).map((i: any) => this.sanitize(i))
  }

  async gestionarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    const response = await apiClient.patch(`${this.baseUrl}/${id}/gestionar`, {}, { params: comentarios ? { comentarios } : {} })
    const payload = response.data?.data ?? response.data
    return this.sanitize(payload)
  }

  async aprobarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    const response = await apiClient.patch(`${this.baseUrl}/${id}/aprobar`, {}, { params: comentarios ? { comentarios } : {} })
    const payload = response.data?.data ?? response.data
    return this.sanitize(payload)
  }

  async rechazarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    const response = await apiClient.patch(`${this.baseUrl}/${id}/rechazar`, {}, { params: comentarios ? { comentarios } : {} })
    const payload = response.data?.data ?? response.data
    return this.sanitize(payload)
  }

  async deleteCasoAprobacion(id: string): Promise<boolean> {
    const response = await apiClient.delete(`${this.baseUrl}/${id}`)
    return (response.data?.data ?? response.data)?.deleted === true
  }

  async updatePruebasComplementarias(casoOriginal: string, pruebas: PruebaComplementaria[]): Promise<CasoAprobacionResponse> {
    const response = await apiClient.patch(`${this.baseUrl}/caso/${casoOriginal}/pruebas`, { pruebas_complementarias: pruebas })
    const payload = response.data?.data ?? response.data
    return this.sanitize(payload)
  }

  async getEstadisticas(): Promise<any> {
    const response = await apiClient.get(`${this.baseUrl}/estadisticas/general`)
    return response.data?.data ?? response.data
  }
}

export default new CasoAprobacionService()
