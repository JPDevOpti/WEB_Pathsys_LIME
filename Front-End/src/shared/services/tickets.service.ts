/**
 * Servicio API para gestión de tickets de soporte
 * Implementa todos los endpoints del módulo de tickets según planning
 */

import { apiClient } from '@/core/config/axios.config'
import type { 
  SupportTicket, 
  NewTicketForm, 
  TicketFilters, 
  TicketStatusEnum,
  TicketSearch
} from '@/modules/support/types/support.types'

export class TicketsService {
  // Use trailing slash to match FastAPI routes and avoid 3xx redirects
  private baseURL = '/tickets/'

  /**
   * Listar tickets con paginación y filtros
   * Todos los usuarios ven todos los tickets
   */
  async getTickets(
    skip: number = 0,
    limit: number = 20,
    sortBy: string = 'ticket_date',
    sortOrder: string = 'desc'
  ): Promise<SupportTicket[]> {
    const params = { skip, limit, sort_by: sortBy, sort_order: sortOrder }
    const response = await apiClient.get(this.baseURL, { params })
    return response
  }

  /**
   * Obtener ticket específico por código
   */
  async getTicketByCode(ticketCode: string): Promise<SupportTicket> {
    const response = await apiClient.get(`${this.baseURL}${ticketCode}`)
    return response
  }

  /**
   * Crear nuevo ticket
   */
  async createTicket(data: NewTicketForm): Promise<SupportTicket> {
    // Preparar datos para envío (campos en inglés para nuevo backend)
    const ticketData = {
      title: data.title,
      category: data.category,
      description: data.description,
      // No enviar imagen en la creación inicial, se sube por separado
    }

    const response = await apiClient.post(this.baseURL, ticketData)
    const newTicket = response

    // Si hay imagen, subirla después
    if (data.image) {
      try {
        await this.uploadImage(newTicket.ticket_code, data.image)
        return await this.getTicketByCode(newTicket.ticket_code)
      } catch {
        return newTicket
      }
    }

    return newTicket
  }

  /**
   * Actualizar ticket existente
   */
  async updateTicket(ticketCode: string, data: Partial<NewTicketForm>): Promise<SupportTicket> {
    const updateData: any = {}
    
    if (data.title !== undefined) updateData.title = data.title
    if (data.category !== undefined) updateData.category = data.category
    if (data.description !== undefined) updateData.description = data.description

    const response = await apiClient.put(`${this.baseURL}${ticketCode}`, updateData)
    return response
  }

  /**
   * Eliminar ticket (solo administradores)
   */
  async deleteTicket(ticketCode: string): Promise<void> {
    await apiClient.delete(`${this.baseURL}${ticketCode}`)
  }

  /**
   * Cambiar estado de ticket (solo administradores)
   */
  async changeStatus(ticketCode: string, status: TicketStatusEnum): Promise<SupportTicket> {
    const response = await apiClient.patch(`${this.baseURL}${ticketCode}/status`, { status })
    return response
  }

  /**
   * Búsqueda avanzada de tickets
   */
  async searchTickets(
    filters: TicketSearch,
    skip: number = 0,
    limit: number = 20,
    // Align with backend field name
    sortBy: string = 'ticket_date',
    sortOrder: string = 'desc'
  ): Promise<SupportTicket[]> {
    const params = { 
      skip, 
      limit, 
      sort_by: sortBy, 
      sort_order: sortOrder 
    }
    
    const response = await apiClient.post(`${this.baseURL}search`, filters, { params })
    return response
  }

  /**
   * Contar tickets que coinciden con filtros
   */
  async countTickets(filters: TicketSearch = {}): Promise<number> {
    const response = await apiClient.get(`${this.baseURL}count`, { params: filters })
    return response.total
  }

  /**
   * Subir imagen a ticket
   */
  async uploadImage(ticketCode: string, file: File): Promise<string> {
    const formData = new FormData()
    formData.append('image', file)
    
    const response = await apiClient.post(
      `${this.baseURL}${ticketCode}/upload-image`, 
      formData,
      { headers: { 'Content-Type': 'multipart/form-data' } }
    )
    
    return (response as any).image_url
  }

  /**
   * Eliminar imagen de ticket
   */
  async deleteImage(ticketCode: string): Promise<void> {
    await apiClient.delete(`${this.baseURL}${ticketCode}/image`)
  }

  /**
   * Obtener siguiente consecutivo (consulta sin consumir)
   */
  async getNextConsecutive(): Promise<string> {
    // Correct backend endpoint name
    const response = await apiClient.get(`${this.baseURL}next-consecutive`)
    return (response as any).codigo_consecutivo
  }

  /**
   * Endpoint de prueba
   */
  async testConnection(): Promise<boolean> {
    try {
      const response = await apiClient.get(`${this.baseURL}test`)
      return (response as any).message === 'Tickets router funcionando correctamente'
    } catch {
      return false
    }
  }

  // ============= MÉTODOS DE UTILIDAD =============

  /**
   * Convertir filtros de UI a formato de API
   */
  private convertFiltersToSearch(filters: TicketFilters): TicketSearch {
    const search: TicketSearch = {}
    
    if (filters.status && filters.status !== 'all') {
      search.status = filters.status
    }
    
    if (filters.category && filters.category !== 'all') {
      search.category = filters.category
    }
    
    if (filters.search && filters.search.trim()) {
      search.search_text = filters.search.trim()
    }
    
    return search
  }

  /**
   * Búsqueda con filtros de UI simplificados
   */
  async searchWithFilters(
    filters: TicketFilters,
    skip: number = 0,
    limit: number = 20,
    sortBy: string = 'ticket_date',
    sortOrder: string = 'desc'
  ): Promise<SupportTicket[]> {
    const searchParams = this.convertFiltersToSearch(filters)
    return this.searchTickets(searchParams, skip, limit, sortBy, sortOrder)
  }

  /**
   * Validar imagen antes del upload
   */
  validateImage(file: File): { valid: boolean; error?: string } {
    // Validar tipo
    if (!file.type.startsWith('image/')) {
      return { valid: false, error: 'El archivo debe ser una imagen' }
    }

    // Validar tamaño (5MB)
    const maxSize = 5 * 1024 * 1024
    if (file.size > maxSize) {
      return { valid: false, error: 'La imagen no puede superar 5MB' }
    }

    // Validar extensión
    const allowedExtensions = ['.jpg', '.jpeg', '.png', '.gif', '.webp']
    const fileExtension = file.name.toLowerCase().substring(file.name.lastIndexOf('.'))
    if (!allowedExtensions.includes(fileExtension)) {
      return { valid: false, error: 'Formato no permitido. Use: JPG, PNG, GIF, WEBP' }
    }

    return { valid: true }
  }
}

// ✅ Instancia singleton del servicio
export const ticketsService = new TicketsService()
