// ✅ NUEVOS ENUMS según planning
export enum TicketCategoryEnum {
  BUG = 'bug',
  FEATURE = 'feature',
  QUESTION = 'question', 
  TECHNICAL = 'technical'
}

export enum TicketStatusEnum {
  OPEN = 'open',
  IN_PROGRESS = 'in-progress',
  RESOLVED = 'resolved',
  CLOSED = 'closed'
}

// ✅ NUEVA INTERFAZ principal con campos en español
export interface SupportTicket {
  ticket_code: string                    // ✅ NUEVO - Identificador principal (T-YYYY-NNN)
  titulo: string                         // ✅ Renombrado de "title"
  categoria: TicketCategoryEnum          // ✅ Renombrado + enum
  descripcion: string                    // ✅ Renombrado de "description"  
  imagen?: string                        // ✅ NUEVO - Single image URL
  fecha_ticket: string                   // ✅ Renombrado de "createdAt"
  estado: TicketStatusEnum               // ✅ Renombrado + enum
  created_by?: string                    // ✅ NUEVO - ID del creador
}

// ✅ NUEVO FORMULARIO simplificado
export interface NewTicketForm {
  titulo: string                         // ✅ Renombrado de "title"
  categoria: TicketCategoryEnum          // ✅ Renombrado + enum
  descripcion: string                    // ✅ Renombrado de "description"
  imagen?: File                          // ✅ Simplificado - un solo archivo
}

// ✅ FILTROS actualizados
export interface TicketFilters {
  estado: TicketStatusEnum | 'all'       // ✅ Renombrado de "status"
  categoria: TicketCategoryEnum | 'all'  // ✅ Renombrado de "category"
  search: string
}

// ✅ INTERFACES adicionales para API
export interface TicketSearch {
  estado?: TicketStatusEnum
  categoria?: TicketCategoryEnum
  created_by?: string
  search_text?: string
  date_from?: string
  date_to?: string
}

export interface TicketStatusUpdate {
  estado: TicketStatusEnum
}

export interface ImageUploadResponse {
  image_url: string
  mensaje: string
}

// ✅ LEGACY TYPES para compatibilidad temporal
export type TicketCategory = 'bug' | 'feature' | 'question' | 'technical'
export type TicketStatus = 'open' | 'in-progress' | 'resolved' | 'closed'
