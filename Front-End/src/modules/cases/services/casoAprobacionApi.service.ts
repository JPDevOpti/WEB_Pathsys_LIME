import { apiClient } from '@/core/config/axios.config'

// Interfaces
export interface PruebaComplementaria {
  codigo: string
  nombre: string
  cantidad: number
  costo?: number
  observaciones?: string
}

export interface CasoAprobacionCreate {
  caso_original_id: string
  caso_code: string
  pruebas_complementarias: PruebaComplementaria[]
  motivo: string
  solicitado_por: string
}

export interface CasoAprobacionResponse {
  id: string
  caso_original_id: string
  caso_code: string
  paciente: any
  estado_aprobacion: 'pendiente' | 'gestionando' | 'aprobado' | 'rechazado'
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
  query?: string
  caso_code?: string
  paciente_code?: string
  paciente_nombre?: string
  estado_aprobacion?: string
  solicitado_por?: string
  aprobado_por?: string
  fecha_solicitud_desde?: string
  fecha_solicitud_hasta?: string
  fecha_aprobacion_desde?: string
  fecha_aprobacion_hasta?: string
  incluir_inactivos?: boolean
}

class CasoAprobacionService {
  private readonly baseUrl = '/aprobacion'

  /**
   * Crear un nuevo caso de aprobación
   */
  async createCasoAprobacion(data: CasoAprobacionCreate): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.post(this.baseUrl, data)
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al crear caso de aprobación')
    }
  }

  /**
   * Obtener caso de aprobación por ID
   */
  async getCasoAprobacion(id: string): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/${id}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener caso de aprobación')
    }
  }

  /**
   * Obtener caso de aprobación por código de caso
   */
  async getCasoAprobacionByCodigo(casoCode: string): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/codigo/${casoCode}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener caso de aprobación')
    }
  }

  /**
   * Buscar casos de aprobación activos
   */
  async searchCasosActive(
    searchParams: CasoAprobacionSearch,
    skip: number = 0,
    limit: number = 50
  ): Promise<any> {
    try {
      const response = await apiClient.post(
        `${this.baseUrl}/search/active`,
        searchParams,
        { params: { skip, limit } }
      )
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al buscar casos de aprobación')
    }
  }

  /**
   * Buscar todos los casos de aprobación (incluye inactivos)
   */
  async searchCasosAll(
    searchParams: CasoAprobacionSearch,
    skip: number = 0,
    limit: number = 50
  ): Promise<any> {
    try {
      const response = await apiClient.post(
        `${this.baseUrl}/search/all`,
        searchParams,
        { params: { skip, limit } }
      )
      return response
    } catch (error: any) {
      throw new Error(error.message || 'Error al buscar casos de aprobación')
    }
  }

  /**
   * Obtener casos por estado
   */
  async getCasosByEstado(
    estado: string,
    limit: number = 50
  ): Promise<CasoAprobacionResponse[]> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/estado/${estado}`,
        { params: { limit } }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener casos por estado')
    }
  }

  /**
   * Obtener casos pendientes de un usuario
   */
  async getCasosPendientesUsuario(
    usuarioId: string,
    limit: number = 50
  ): Promise<CasoAprobacionResponse[]> {
    try {
      const response = await apiClient.get(
        `${this.baseUrl}/usuario/${usuarioId}/pendientes`,
        { params: { limit } }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener casos pendientes')
    }
  }

  /**
   * Cambiar estado a gestionando
   */
  async gestionarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.patch(
        `${this.baseUrl}/${id}/gestionar`,
        {},
        { params: comentarios ? { comentarios } : {} }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al gestionar caso')
    }
  }

  /**
   * Aprobar un caso
   */
  async aprobarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.patch(
        `${this.baseUrl}/${id}/aprobar`,
        {},
        { params: comentarios ? { comentarios } : {} }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al aprobar caso')
    }
  }

  /**
   * Rechazar un caso
   */
  async rechazarCaso(id: string, comentarios?: string): Promise<CasoAprobacionResponse> {
    try {
      const response = await apiClient.patch(
        `${this.baseUrl}/${id}/rechazar`,
        {},
        { params: comentarios ? { comentarios } : {} }
      )
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al rechazar caso')
    }
  }

  /**
   * Eliminar caso de aprobación (soft delete)
   */
  async deleteCasoAprobacion(id: string): Promise<boolean> {
    try {
      const response = await apiClient.delete(`${this.baseUrl}/${id}`)
      return response.data.deleted
    } catch (error: any) {
      throw new Error(error.message || 'Error al eliminar caso de aprobación')
    }
  }

  /**
   * Obtener estadísticas de casos de aprobación
   */
  async getEstadisticas(): Promise<any> {
    try {
      const response = await apiClient.get(`${this.baseUrl}/estadisticas/general`)
      return response.data
    } catch (error: any) {
      throw new Error(error.message || 'Error al obtener estadísticas')
    }
  }

  /**
   * Crear solicitud de aprobación desde firma de caso
   */
  async createFromSignature(
    casoId: string,
    casoCode: string,
    pruebasComplementarias: PruebaComplementaria[],
    motivo: string
  ): Promise<CasoAprobacionResponse> {
    const data: CasoAprobacionCreate = {
      caso_original_id: casoId,
      caso_code: casoCode,
      pruebas_complementarias: pruebasComplementarias,
      motivo,
      solicitado_por: 'current_user' // Se obtendrá del contexto de autenticación
    }

    return this.createCasoAprobacion(data)
  }
}

export default new CasoAprobacionService()
