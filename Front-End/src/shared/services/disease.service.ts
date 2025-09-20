import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

// Types
export interface Disease {
  id?: string
  table: string
  code: string
  name: string
  description?: string
  is_active: boolean
  created_at?: string
  updated_at?: string
}

export interface DiseaseSearchResponse {
  diseases: Disease[]
  search_term?: string
  total: number
  skip: number
  limit: number
}

export interface DiseaseListResponse {
  diseases: Disease[]
  total: number
  skip: number
  limit: number
}

export interface DiseaseByTableResponse {
  diseases: Disease[]
  table: string
  skip: number
  limit: number
}



class DiseaseService {
  private readonly endpoint = '/diseases' // Nuevo endpoint del nuevo backend

  constructor() {
    // Constructor sin logs
  }

  /**
   * Buscar enfermedades por tabla específica
   */
  async searchDiseasesByTabla(tabla: string, limit: number = 15000): Promise<DiseaseByTableResponse> {
    try {
      const response = await apiClient.get(`${this.endpoint}/table/${tabla}`, {
        params: {
          limit,
          skip: 0
        }
      })
      
      const backendData = response.data || response
      return {
        diseases: backendData.diseases || [],
        table: backendData.table || tabla,
        skip: backendData.skip || 0,
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
        
        const response = await apiClient.get(`${this.endpoint}/search/code`, {
          params: {
            q: query,
            limit,
            skip: 0
          }
        })
        
        // El nuevo backend devuelve { diseases: [...], search_term: ..., skip: ..., limit: ... }
        const backendData = response.data || response
        
        return {
          diseases: backendData.diseases || [],
          search_term: backendData.search_term || query,
          total: backendData.diseases?.length || 0,
          skip: backendData.skip || 0,
          limit: backendData.limit || limit
        }
      }
      
      // Si no es un código, buscar por nombre
      
      const response = await apiClient.get(`${this.endpoint}/search/name`, {
        params: {
          q: query,
          limit,
          skip: 0
        }
      })
      
      // El nuevo backend devuelve { diseases: [...], search_term: ..., skip: ..., limit: ... }
      const backendData = response.data || response
      
      return {
        diseases: backendData.diseases || [],
        search_term: backendData.search_term || query,
        total: backendData.diseases?.length || 0,
        skip: backendData.skip || 0,
        limit: backendData.limit || limit
      }
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Error al buscar enfermedades')
    }
  }

  /**
   * Obtener todas las enfermedades
   */
  async getAllDiseases(): Promise<DiseaseListResponse> {
    try {
      
      // Usar el endpoint general para enfermedades (no necesita filtro activo/inactivo)
      const response = await apiClient.get(`${this.endpoint}`, {
        params: {
          skip: 0,
          limit: 15000 // Límite alto para obtener todas las enfermedades
        }
      })
      
      
      // El nuevo backend devuelve { diseases: [...], total: ..., skip: ..., limit: ... }
      const backendData = response.data || response
      
      
      const result = {
        diseases: backendData.diseases || [],
        total: backendData.total || 0,
        skip: backendData.skip || 0,
        limit: backendData.limit || 15000
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
      const response = await apiClient.get(`${this.endpoint}/code/${codigo}`)
      return response.data
    } catch (error: any) {
      throw new Error(error.response?.data?.message || 'Enfermedad no encontrada')
    }
  }

  /**
   * Obtener enfermedades por tabla de referencia
   */
  async getDiseasesByTable(tabla: string, page: number = 1, limit: number = 50): Promise<DiseaseByTableResponse> {
    try {
      const response = await apiClient.get(`${this.endpoint}/table/${tabla}`, {
        params: {
          skip: (page - 1) * limit,
          limit
        }
      })
      
      // El nuevo backend devuelve { diseases: [...], table: ..., skip: ..., limit: ... }
      const backendData = response.data
      
      return {
        diseases: backendData.diseases || [],
        table: backendData.table || tabla,
        skip: backendData.skip || 0,
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
