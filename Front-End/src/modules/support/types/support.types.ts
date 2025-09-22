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

// ✅ NUEVA INTERFAZ principal con campos en inglés (nuevo backend)
export interface SupportTicket {
  ticket_code: string                    // ✅ Identificador principal (T-YYYY-NNN)
  title: string                          // ✅ Campo en inglés del nuevo backend
  category: TicketCategoryEnum           // ✅ Campo en inglés del nuevo backend
  description: string                    // ✅ Campo en inglés del nuevo backend
  image?: string                         // ✅ Campo en inglés del nuevo backend
  ticket_date: string                    // ✅ Campo en inglés del nuevo backend
  status: TicketStatusEnum               // ✅ Campo en inglés del nuevo backend
  created_by?: string                    // ✅ ID del creador
}

// ✅ NUEVO FORMULARIO simplificado (campos en inglés para nuevo backend)
export interface NewTicketForm {
  title: string                          // ✅ Campo en inglés del nuevo backend
  category: TicketCategoryEnum           // ✅ Campo en inglés del nuevo backend
  description: string                    // ✅ Campo en inglés del nuevo backend
  image?: File                           // ✅ Campo en inglés del nuevo backend
}

// ✅ FILTROS actualizados (campos en inglés para nuevo backend)
export interface TicketFilters {
  status: TicketStatusEnum | 'all'       // ✅ Campo en inglés del nuevo backend
  category: TicketCategoryEnum | 'all'   // ✅ Campo en inglés del nuevo backend
  search: string
}

// ✅ INTERFACES adicionales para API (campos en inglés para nuevo backend)
export interface TicketSearch {
  status?: TicketStatusEnum
  category?: TicketCategoryEnum
  created_by?: string
  search_text?: string
  date_from?: string
  date_to?: string
}

export interface TicketStatusUpdate {
  status: TicketStatusEnum
}

export interface ImageUploadResponse {
  image_url: string
  mensaje: string
}

// ✅ LEGACY TYPES para compatibilidad temporal
export type TicketCategory = 'bug' | 'feature' | 'question' | 'technical'
export type TicketStatus = 'open' | 'in-progress' | 'resolved' | 'closed'
