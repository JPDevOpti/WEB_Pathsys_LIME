export interface TestDetails {
  id: string
  pruebaCode: string
  pruebasName: string
  pruebasDescription?: string
  tiempo?: number
  isActive: boolean
  fechaCreacion?: string
  fechaActualizacion?: string
}

export interface TestSearchParams {
  query?: string
  activo?: boolean
  skip?: number
  limit?: number
}

export interface TestListResponse {
  pruebas: TestDetails[]
  total: number
  skip: number
  limit: number
  has_next: boolean
  has_prev: boolean
}

export interface TestOperationResult {
  success: boolean
  test?: TestDetails
  tests?: TestDetails[]
  message?: string
  error?: string
}

export interface TestSelectOption {
  value: string
  label: string
  description?: string
  time?: number
  test: TestDetails
}
