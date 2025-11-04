export interface TestGroup {
  type: 'LOW_COMPLEXITY_IHQ' | 'HIGH_COMPLEXITY_IHQ' | 'SPECIAL_IHQ' | 'HISTOCHEMISTRY'
  tests: Array<{
    code: string
    quantity: number
    name?: string
  }>
  observations?: string
}

export interface UnreadCase {
  id: string
  caseCode: string // Formato: TC2025-00001
  isSpecialCase?: boolean // Indica si es caso especial (laboratorio externo)
  // Datos del paciente (opcionales para casos especiales)
  documentType?: string // CC, TI, CE, PA, RC
  patientDocument?: string
  firstName?: string
  secondName?: string
  firstLastName?: string
  secondLastName?: string
  patientName?: string // Nombre completo concatenado
  // Entidad
  entityCode?: string
  entityName?: string
  institution?: string // Nombre de la institución (derivado de entityName)
  notes?: string // Notas especiales
  // Pruebas (nuevo formato con testGroups)
  testGroups?: TestGroup[]
  // Tipos de pruebas (formato antiguo - retrocompatibilidad)
  lowComplexityIHQ?: string
  lowComplexityPlates?: number
  highComplexityIHQ?: string
  highComplexityPlates?: number
  specialIHQ?: string
  specialPlates?: number
  histochemistry?: string
  histochemistryPlates?: number
  // Placas y entrega
  numberOfPlates?: number
  deliveredTo?: string
  deliveryDate?: string
  // Recepción
  entryDate?: string
  receivedBy?: string
  // Estado y metadatos
  status?: string
  elaboratedBy?: string
  receipt?: string
  createdAt?: string
  updatedAt?: string
}

export interface UnreadCaseFilters {
  searchQuery: string // Búsqueda por código, documento o nombre
  dateFrom: string
  dateTo: string
  selectedInstitution: string
  selectedTestType: string // Tipo de prueba
  selectedStatus: string
}

export interface Column {
  key: string
  label: string
  class?: string
}

export type TestType = 
  | 'low_complexity' 
  | 'high_complexity' 
  | 'special' 
  | 'histochemistry'
  | 'all'

export const TEST_TYPE_LABELS: Record<TestType, string> = {
  low_complexity: 'Inmunohistoquímicas de Baja Complejidad',
  high_complexity: 'Inmunohistoquímicas de Alta Complejidad',
  special: 'Inmunohistoquímicas Especiales',
  histochemistry: 'Histoquímicas',
  all: 'Todas'
}

export const STATUS_OPTIONS = [
  { value: '', label: 'Todos' },
  { value: 'En proceso', label: 'En proceso' },
  { value: 'Completado', label: 'Completado' }
]

export const TEST_TYPE_OPTIONS = [
  { value: '', label: 'Todas las pruebas' },
  { value: 'low_complexity', label: 'IHQ Baja Complejidad' },
  { value: 'high_complexity', label: 'IHQ Alta Complejidad' },
  { value: 'special', label: 'IHQ Especiales' },
  { value: 'histochemistry', label: 'Histoquímicas' }
]

export interface UnreadCaseListResponse {
  items: UnreadCase[]
  total: number
  page: number
  limit: number
}

export interface UnreadCaseListParams {
  page?: number
  limit?: number
  searchQuery?: string
  selectedInstitution?: string
  selectedTestType?: string
  selectedStatus?: string
  dateFrom?: string
  dateTo?: string
  sortKey?: string
  sortOrder?: 'asc' | 'desc'
}

export type UnreadCaseCreatePayload = Omit<UnreadCase, 'id' | 'createdAt' | 'updatedAt'>

export type UnreadCaseUpdatePayload = Partial<UnreadCaseCreatePayload>

export interface BulkMarkDeliveredPayload {
  caseCodes: string[]
  deliveredTo: string
  deliveryDate?: string
}
