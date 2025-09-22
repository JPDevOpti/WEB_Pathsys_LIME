// Types for auxiliary management in Profile module

// UI form model (camelCase for Vue forms)
export interface AuxiliaryFormModel {
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  password: string
  observaciones: string
  isActive: boolean
}

// Backend request (snake_case)
export interface AuxiliaryCreateRequest {
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  password: string // Contraseña para crear el usuario asociado
  observaciones: string
  is_active: boolean
}

// Backend creation response (snake_case)
export interface AuxiliaryCreateResponse {
  id: string
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

// UI state for create flow
export interface AuxiliaryCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Validation result for create form
export interface AuxiliaryFormValidation {
  isValid: boolean
  errors: {
    auxiliarName?: string
    auxiliarCode?: string
    AuxiliarEmail?: string
    password?: string
    observaciones?: string
  }
}

// UI form model for edition
export interface AuxiliaryEditFormModel {
  id: string
  auxiliarName: string
  auxiliarCode: string
  AuxiliarEmail: string
  observaciones: string
  isActive: boolean
  password?: string
  passwordConfirm?: string
}

// Backend update request (snake_case)
export interface AuxiliaryUpdateRequest {
  auxiliar_name: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  password?: string
}

// Backend update response (snake_case)
export interface AuxiliaryUpdateResponse {
  id: string
  auxiliar_name: string
  auxiliar_code: string
  auxiliar_email: string
  observaciones: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// Validation result for edition form
export interface AuxiliaryEditFormValidation {
  isValid: boolean
  errors: {
    auxiliarName?: string
    auxiliarCode?: string
    AuxiliarEmail?: string
    observaciones?: string
    password?: string
    passwordConfirm?: string
  }
}

// UI state for edition flow
export interface AuxiliaryEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}
