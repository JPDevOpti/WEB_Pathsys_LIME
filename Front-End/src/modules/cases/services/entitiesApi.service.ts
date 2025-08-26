import type { EntityInfo } from '../types'
import { API_CONFIG, buildApiUrl, getAuthHeaders } from '@/core/config/api.config'

/**
 * Servicio para gestionar entidades de salud
 */
export class EntitiesApiService {
  private async makeRequest<T>(endpoint: string, options: RequestInit = {}): Promise<T> {
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
      throw error
    }
  }

  // ============================================================================
  // FUNCIONES DE CONSULTA
  // ============================================================================

  /**
   * Obtiene todas las entidades de salud
   * @returns Lista de entidades
   */
  async getEntities(): Promise<EntityInfo[]> {
    try {
      // Usar el endpoint correcto para entidades con barra final
      const response = await this.makeRequest<any>(`${API_CONFIG.ENDPOINTS.ENTITIES}/`)
      
      if (response.entidades && Array.isArray(response.entidades)) {
        return response.entidades.map((entity: any) => ({
          codigo: entity.EntidadCode || entity.codigo || entity.id || '',
          nombre: entity.EntidadName || entity.nombre || entity.name || ''
        }))
      } else if (Array.isArray(response)) {
        return response.map((entity: any) => ({
          codigo: entity.EntidadCode || entity.codigo || entity.id || '',
          nombre: entity.EntidadName || entity.nombre || entity.name || ''
        }))
      } else {
        return []
      }
    } catch (error) {
      return []
    }
  }

  /**
   * Obtiene una entidad específica por código
   * @param codigo - Código de la entidad
   * @returns Información de la entidad
   */
  async getEntityByCode(codigo: string): Promise<EntityInfo> {
    try {
      const entities = await this.getEntities()
      const entity = entities.find(e => e.codigo === codigo)
      
      if (entity) {
        return entity
      } else {
        throw new Error(`Entidad con código ${codigo} no encontrada`)
      }
    } catch (error: any) {
      throw new Error(error.message || `Error al obtener la entidad ${codigo}`)
    }
  }

  /**
   * Busca entidades por nombre
   * @param searchTerm - Término de búsqueda
   * @returns Lista de entidades que coinciden con la búsqueda
   */
  async searchEntities(searchTerm: string): Promise<EntityInfo[]> {
    try {
      const entities = await this.getEntities()
      
      if (!searchTerm.trim()) return entities
      
      const term = searchTerm.toLowerCase().trim()
      return entities.filter(entity => 
        entity.nombre.toLowerCase().includes(term) ||
        entity.codigo.toLowerCase().includes(term)
      )
    } catch (error: any) {
      throw new Error(error.message || 'Error al buscar entidades')
    }
  }

  // ============================================================================
  // FUNCIONES DE CREACIÓN Y MODIFICACIÓN
  // ============================================================================

  /**
   * Crea una nueva entidad
   * @param entityData - Datos de la entidad a crear
   * @returns Entidad creada
   */
  async createEntity(entityData: Omit<EntityInfo, 'codigo'>): Promise<EntityInfo> {
    try {
      // Por ahora, solo simulamos la creación
      const newEntity: EntityInfo = {
        codigo: `ENT-${Date.now()}`,
        nombre: entityData.nombre
      }
      return newEntity
    } catch (error: any) {
      throw new Error(error.message || 'Error al crear la entidad')
    }
  }

  /**
   * Actualiza una entidad existente
   * @param codigo - Código de la entidad
   * @param entityData - Datos de actualización
   * @returns Entidad actualizada
   */
  async updateEntity(codigo: string, entityData: Partial<EntityInfo>): Promise<EntityInfo> {
    try {
      // Por ahora, solo simulamos la actualización
      const entity = await this.getEntityByCode(codigo)
      return { ...entity, ...entityData }
    } catch (error: any) {
      throw new Error(error.message || `Error al actualizar la entidad ${codigo}`)
    }
  }

  /**
   * Elimina una entidad
   * @param codigo - Código de la entidad
   * @returns Confirmación de eliminación
   */
  async deleteEntity(codigo: string): Promise<{ message: string }> {
    try {
      // Por ahora, solo simulamos la eliminación
      await this.getEntityByCode(codigo) // Verificar que existe
      return { message: `Entidad ${codigo} eliminada exitosamente` }
    } catch (error: any) {
      throw new Error(error.message || `Error al eliminar la entidad ${codigo}`)
    }
  }

  // ============================================================================
  // FUNCIONES DE UTILIDAD
  // ============================================================================

  /**
   * Verifica la conectividad con el backend
   * @returns true si hay conexión, false en caso contrario
   */
  async checkBackendConnection(): Promise<boolean> {
    try {
      // Intentar hacer una petición simple al endpoint de entidades
      const response = await this.makeRequest<any>(API_CONFIG.ENDPOINTS.ENTITIES)
      return true
    } catch (error) {
      return false
    }
  }
}

// Exportar instancia singleton
export const entitiesApiService = new EntitiesApiService()
export default entitiesApiService
