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
  signedAt?: string
  tests: string[]
  pathologist?: string
  patologo_asignado?: {
    codigo: string
    nombre: string
    firma?: string
  }
  notes?: string
  servicio?: string
  priority?: string
  business_days?: number
  delivered_to?: string
  delivered_at?: string
  result?: {
    method?: string[]
    macro_result?: string
    micro_result?: string
    diagnosis?: string
    resultDate?: string
    observations?: string
    cie10_diagnosis?: { code: string; name: string } | null
    cieo_diagnosis?: { code: string; name: string } | null
  }
  subsamples?: Array<{
    bodyRegion: string
    tests: Array<{ id: string; name: string; quantity: number }>
  }>
  additional_notes?: Array<{ date: string; note: string }>
  complementary_tests?: Array<{ code?: string; name?: string; quantity?: number; reason?: string }>
}

export interface Filters {
  searchQuery: string
  searchPathologist: string
  dateFrom: string
  dateTo: string
  selectedEntity: string
  selectedStatus: string
  selectedTest: string
}

export type SortKey = keyof Pick<Case, 'id' | 'caseCode' | 'status' | 'receivedAt' | 'deliveredAt'>
export type SortOrder = 'asc' | 'desc'


