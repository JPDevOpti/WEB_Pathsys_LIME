import type { 
  TecnicaComplementaria, 
  FiltrosComplementaryTechniques, 
  RespuestaComplementaryTechniques,
  CrearTecnicaComplementaria,
  ActualizarTecnicaComplementaria 
} from '../types/complementaryTechniques.types'
import { buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

export class ComplementaryTechniquesService {
  private static readonly BASE_URL = '/complementary-techniques'

  private static async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
    const url = buildApiUrl(endpoint)
    
    const defaultOptions: RequestInit = {
      headers: getAuthHeaders(),
      ...options,
    }

    try {
      const response = await fetch(url, defaultOptions)
      
      if (!response.ok) {
        const errorData = await response.json().catch(() => ({}))
        throw new Error(errorData.detail || `HTTP error! status: ${response.status}`)
      }

      return await response.json()
    } catch (error) {
      console.error('API request failed:', error)
      throw error
    }
  }

  static async obtenerTecnicas(filtros?: FiltrosComplementaryTechniques): Promise<RespuestaComplementaryTechniques> {
    try {
      const params = new URLSearchParams()
      
      if (filtros?.estado) params.append('estado', filtros.estado)
      if (filtros?.tipo) params.append('tipo', filtros.tipo)
      if (filtros?.categoria) params.append('categoria', filtros.categoria)
      if (filtros?.busqueda) params.append('busqueda', filtros.busqueda)

      return await this.makeRequest<RespuestaComplementaryTechniques>(`${this.BASE_URL}?${params.toString()}`)
    } catch (error) {
      console.error('Error al obtener técnicas complementarias:', error)
      throw new Error('No se pudieron cargar las técnicas complementarias')
    }
  }

  static async obtenerTecnicaPorId(id: string): Promise<TecnicaComplementaria> {
    try {
      return await this.makeRequest<TecnicaComplementaria>(`${this.BASE_URL}/${id}`)
    } catch (error) {
      console.error('Error al obtener técnica complementaria:', error)
      throw new Error('No se pudo cargar la técnica complementaria')
    }
  }

  static async crearTecnica(tecnica: CrearTecnicaComplementaria): Promise<TecnicaComplementaria> {
    try {
      return await this.makeRequest<TecnicaComplementaria>(this.BASE_URL, {
        method: 'POST',
        body: JSON.stringify(tecnica)
      })
    } catch (error) {
      console.error('Error al crear técnica complementaria:', error)
      throw new Error('No se pudo crear la técnica complementaria')
    }
  }

  static async actualizarTecnica(id: string, tecnica: ActualizarTecnicaComplementaria): Promise<TecnicaComplementaria> {
    try {
      return await this.makeRequest<TecnicaComplementaria>(`${this.BASE_URL}/${id}`, {
        method: 'PUT',
        body: JSON.stringify(tecnica)
      })
    } catch (error) {
      console.error('Error al actualizar técnica complementaria:', error)
      throw new Error('No se pudo actualizar la técnica complementaria')
    }
  }

  static async eliminarTecnica(id: string): Promise<void> {
    try {
      await this.makeRequest<void>(`${this.BASE_URL}/${id}`, {
        method: 'DELETE'
      })
    } catch (error) {
      console.error('Error al eliminar técnica complementaria:', error)
      throw new Error('No se pudo eliminar la técnica complementaria')
    }
  }

  static async cambiarEstadoTecnica(id: string, estado: 'En proceso' | 'Por entregar' | 'Completado'): Promise<TecnicaComplementaria> {
    try {
      return await this.makeRequest<TecnicaComplementaria>(`${this.BASE_URL}/${id}/estado`, {
        method: 'PATCH',
        body: JSON.stringify({ estado })
      })
    } catch (error) {
      console.error('Error al cambiar estado de técnica complementaria:', error)
      throw new Error('No se pudo cambiar el estado de la técnica complementaria')
    }
  }
}
