import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

// Types
export interface Disease {
  id: string
  tabla: string
  codigo: string
  nombre: string
  descripcion?: string
  isActive: boolean
  created_at?: string
  updated_at?: string
}

export interface DiseaseSearchResponse {
  diseases: Disease[]
  total: number
  page: number
  limit: number
}

export interface DiseaseListResponse {
  data: Disease[]
  total: number
  page: number
  limit: number
}



class DiseaseService {
  private readonly endpoint = '/enfermedades'

  constructor() {
    // Constructor sin logs
  }

  /**
   * Buscar enfermedades por tabla específica
   */
  async searchDiseasesByTabla(tabla: string, limit: number = 15000): Promise<DiseaseSearchResponse> {
    try {
      const response = await apiClient.get(`${this.endpoint}/tabla/${tabla}`, {
        params: {
          limit,
          skip: 0
        }
      })
      
      const backendData = response.data || response
      return {
        diseases: backendData.enfermedades || [],
        total: backendData.total || 0,
        page: 1,
        limit: backendData.limit || limit
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Error al buscar enfermedades por tabla')
    }
  }

  /**
   * Buscar enfermedades por nombre o código
   */
  async searchDiseases(query: string, limit: number = 15000): Promise<DiseaseSearchResponse> {
    try {
      // Intentar buscar por código primero (si parece un código)
      if (/^[A-Z]\d{2,3}$/.test(query.toUpperCase())) {
        
        const response = await apiClient.get(`${this.endpoint}/search/codigo`, {
          params: {
            q: query,
            limit,
            skip: 0
          }
        })
        
        // El backend devuelve { enfermedades: [...], search_term: ..., skip: ..., limit: ... }
        const backendData = response.data || response
        
        return {
          diseases: backendData.enfermedades || [],
          total: backendData.enfermedades?.length || 0,
          page: 1,
          limit: backendData.limit || limit
        }
      }
      
      // Si no es un código, buscar por nombre
      
      const response = await apiClient.get(`${this.endpoint}/search/nombre`, {
        params: {
          q: query,
          limit,
          skip: 0
        }
      })
      
      // El backend devuelve { enfermedades: [...], search_term: ..., skip: ..., limit: ... }
      const backendData = response.data || response
      
      return {
        diseases: backendData.enfermedades || [],
        total: backendData.enfermedades?.length || 0,
        page: 1,
        limit: backendData.limit || limit
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Error al buscar enfermedades')
    }
  }

  /**
   * Obtener todas las enfermedades
   */
  async getAllDiseases(): Promise<DiseaseSearchResponse> {
    try {
      
      // Primero obtener el total de enfermedades
      const totalResponse = await apiClient.get(`${this.endpoint}`, {
        params: {
          skip: 0,
          limit: 1, // Solo necesitamos 1 para obtener el total
          is_active: true
        }
      })
      
      const totalData = totalResponse.data || totalResponse
      const total = totalData.total || 12634 // Usar el total real o fallback
      
      
      // Ahora obtener todas las enfermedades usando el total real
      const response = await apiClient.get(`${this.endpoint}`, {
        params: {
          skip: 0,
          limit: total, // Usar el total real para obtener todas las enfermedades
          is_active: true
        }
      })
      
      
      // El backend devuelve { enfermedades: [...], total: ..., skip: ..., limit: ... }
      const backendData = response.data || response
      
      
      const result = {
        diseases: backendData.enfermedades || [],
        total: backendData.total || total,
        page: 1,
        limit: backendData.limit || total
      }
      
      
      return result
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Error al obtener enfermedades')
    }
  }

  /**
   * Obtener enfermedad por ID
   */
  async getDiseaseById(id: string): Promise<Disease> {
    try {
      const response = await apiClient.get(`${this.endpoint}/${id}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Enfermedad no encontrada')
    }
  }

  /**
   * Obtener enfermedad por código
   */
  async getDiseaseByCode(codigo: string): Promise<Disease> {
    try {
      const response = await apiClient.get(`${this.endpoint}/codigo/${codigo}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Enfermedad no encontrada')
    }
  }

  /**
   * Obtener enfermedades por tabla de referencia
   */
  async getDiseasesByTable(tabla: string, page: number = 1, limit: number = 50): Promise<DiseaseListResponse> {
    try {
      const response = await apiClient.get(`${this.endpoint}/tabla/${tabla}`, {
        params: {
          skip: (page - 1) * limit,
          limit
        }
      })
      
      // El backend devuelve { enfermedades: [...], tabla: ..., skip: ..., limit: ... }
      const backendData = response.data
      
      return {
        data: backendData.enfermedades || [],
        total: backendData.enfermedades?.length || 0,
        page: page,
        limit: backendData.limit || limit
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Error al obtener enfermedades por tabla')
    }
  }

  // Métodos que no se usan en el frontend por ahora
  async createDisease(disease: Omit<Disease, 'id' | 'created_at' | 'updated_at'>): Promise<Disease> {
    throw new Error('No implementado en el frontend')
  }

  async updateDisease(id: string, disease: Partial<Omit<Disease, 'id' | 'created_at' | 'updated_at'>>): Promise<Disease> {
    throw new Error('No implementado en el frontend')
  }

  async deleteDisease(id: string): Promise<boolean> {
    throw new Error('No implementado en el frontend')
  }

  async searchByName(nombre: string, limit: number = 15000): Promise<DiseaseSearchResponse> {
    return this.searchDiseases(nombre, limit)
  }

  async searchByCode(codigo: string, limit: number = 15000): Promise<DiseaseSearchResponse> {
    return this.searchDiseases(codigo, limit)
  }
}

export const diseaseService = new DiseaseService()
export default diseaseService
