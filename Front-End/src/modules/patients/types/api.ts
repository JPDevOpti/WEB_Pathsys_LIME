export interface ApiResponse<T> {
  data: T
  message?: string
  status: number
}

export interface ApiError {
  message: string
  status: number
  details?: any
}

export interface PaginatedResponse<T> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface SearchParams {
  q?: string
  skip?: number
  limit?: number
  sort?: string
  order?: 'asc' | 'desc'
}

export interface PatientListParams extends SearchParams {
  search?: string
  gender?: string
  care_type?: string
  entity_name?: string
  municipality_code?: string
}

export interface AdvancedSearchParams {
  identification_type?: number
  identification_number?: string
  first_name?: string
  first_lastname?: string
  birth_date_start?: string
  birth_date_end?: string
  age_min?: number
  age_max?: number
  gender?: string
  municipality_code?: string
  subregion?: string
  entity_id?: string
  entity_name?: string
  care_type?: string
  created_at_start?: string
  created_at_end?: string
  skip?: number
  limit?: number
}

