// Resident types: form models, API requests/responses, validation, and state management

// Frontend form model for resident creation
export interface ResidentFormModel {
  residenteName: string
  InicialesResidente: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  password: string
  observaciones: string
  isActive: boolean
}

// Backend API request for creating a new resident
export interface ResidentCreateRequest {
  resident_name: string
  initials: string
  resident_code: string
  resident_email: string
  medical_license: string
  password: string
  observations: string
  is_active: boolean
}

// Backend API response for resident creation
export interface ResidentCreateResponse {
  id: string
  resident_name: string
  initials: string
  resident_code: string
  resident_email: string
  medical_license: string
  observations: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

// State management for resident creation operations
export interface ResidentCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Form validation result for resident creation
export interface ResidentFormValidation {
  isValid: boolean
  errors: {
    residenteName?: string
    InicialesResidente?: string
    residenteCode?: string
    ResidenteEmail?: string
    registro_medico?: string
    password?: string
    observaciones?: string
  }
}

// Frontend form model for resident editing
export interface ResidentEditFormModel {
  id: string
  residenteName: string
  InicialesResidente: string
  residenteCode: string
  ResidenteEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  password?: string
  passwordConfirm?: string
}

// Backend API request for updating a resident
export interface ResidentUpdateRequest {
  resident_name: string
  initials: string
  resident_email: string
  medical_license: string
  observations: string
  is_active: boolean
  password?: string
}

// Backend API response for resident update
export interface ResidentUpdateResponse {
  id: string
  resident_name: string
  initials: string
  resident_code: string
  resident_email: string
  medical_license: string
  observations: string
  is_active: boolean
  created_at: string
  updated_at: string
}

// State management for resident editing operations
export interface ResidentEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Form validation result for resident editing
export interface ResidentEditFormValidation {
  isValid: boolean
  errors: {
    residenteName?: string
    InicialesResidente?: string
    residenteCode?: string
    ResidenteEmail?: string
    registro_medico?: string
    observaciones?: string
  }
}
