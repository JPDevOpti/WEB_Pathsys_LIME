export interface EntityFormModel {
  entityName: string
  entityCode: string
  notes: string
  isActive: boolean
}

export interface EntityCreateRequest {
  name: string
  entity_code: string
  notes: string
  is_active: boolean
}

export interface EntityCreateResponse {
  id: string
  name: string
  entity_code: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

export interface EntityCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface EntityFormValidation {
  isValid: boolean
  errors: {
    entityName?: string
    entityCode?: string
    notes?: string
  }
}

export interface EntityEditFormModel {
  id: string
  entityName: string
  entityCode: string
  notes: string
  isActive: boolean
}

export interface EntityUpdateRequest {
  name?: string
  entity_code?: string
  notes?: string
  is_active?: boolean
}

export interface EntityUpdateResponse {
  id: string
  name: string
  entity_code: string
  notes: string
  is_active: boolean
  created_at: string
  updated_at: string
}

export interface EntityEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface EntityEditFormValidation {
  isValid: boolean
  errors: {
    entityName?: string
    entityCode?: string
    notes?: string
  }
}
