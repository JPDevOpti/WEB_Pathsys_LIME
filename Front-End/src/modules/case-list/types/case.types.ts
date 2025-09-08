export interface Patient {
  id: string
  dni: string
  fullName: string
  sex: string
  age: number
  entity: string
  attentionType: string
  notes?: string
  createdAt?: string
  updatedAt?: string
}

export interface Case {
  id: string
  caseCode?: string
  sampleType: string
  patient: Patient
  entity: string
  requester: string
  status: string
  receivedAt: string
  deliveredAt: string
  signedAt?: string  // Nueva: fecha de firma específica
  tests: string[]
  pathologist?: string
  notes?: string
  servicio?: string
  // Nuevo: prioridad del caso (Normal|Prioritario|Urgente)
  priority?: string
  // Campo para capturar días hábiles al completar el caso
  oportunidad?: number
  // Campo para registrar quién recibe el caso al ser entregado
  entregado_a?: string
  result?: {
    method?: string
    macro?: string
    micro?: string
    diagnosis?: string
    resultDate?: string
    observaciones?: string
    // Campos adicionales para diagnósticos
    diagnostico_cie10?: {
      codigo: string
      nombre: string
    } | null
    diagnostico_cieo?: {
      codigo: string
      nombre: string
    } | null
  }
  subsamples?: Array<{
    bodyRegion: string
    tests: Array<{ id: string; name: string; quantity: number }>
  }>
}

export interface Filters {
  searchQuery: string
  searchPathologist: string
  dateFrom: string // DD/MM/YYYY
  dateTo: string   // DD/MM/YYYY
  selectedEntity: string
  selectedStatus: string
  selectedTest: string
}

export type SortKey = keyof Pick<Case,
  'id' | 'caseCode' | 'status' | 'receivedAt' | 'deliveredAt'
>

export type SortOrder = 'asc' | 'desc'


