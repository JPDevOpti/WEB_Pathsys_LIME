// API Response Types
export interface ApiResponse<T = any> {
  success: boolean
  data: T
  message?: string
  errors?: string[]
}

export interface PaginatedResponse<T = any> {
  data: T[]
  total: number
  page: number
  limit: number
  totalPages: number
}

export interface ApiError {
  message: string
  code?: string
  field?: string
}

// Request Types
export interface PaginationParams {
  page?: number
  limit?: number
  search?: string
  sortBy?: string
  sortOrder?: 'asc' | 'desc'
}

export interface FilterParams {
  entityId?: number
  pathologistId?: number
  testId?: number
  status?: string
  dateFrom?: string
  dateTo?: string
}

// HTTP Methods
export type HttpMethod = 'GET' | 'POST' | 'PUT' | 'DELETE' | 'PATCH'

// API Endpoints
export interface ApiEndpoint {
  method: HttpMethod
  url: string
  requiresAuth?: boolean
}