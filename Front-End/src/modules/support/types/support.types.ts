export interface SupportTicket {
  id: string
  title: string
  category: string
  description: string
  status: 'open' | 'in-progress' | 'resolved' | 'closed'
  createdAt: string
  attachments: TicketAttachment[]
}

export interface NewTicketForm {
  title: string
  category: string
  description: string
  attachments: TicketAttachment[]
}

export interface TicketAttachment {
  id: string
  fileName: string
  fileType: string
  fileSize: number
  previewUrl?: string
}



export type TicketCategory = 'bug' | 'feature' | 'question' | 'technical'
export type TicketStatus = 'open' | 'in-progress' | 'resolved' | 'closed'

export interface TicketFilters {
  status: TicketStatus | 'all'
  category: TicketCategory | 'all'
  search: string
}
