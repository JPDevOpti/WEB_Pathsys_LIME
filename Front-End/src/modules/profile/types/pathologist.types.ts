// Pathologist-specific types for the profile module

// Creation form model (frontend camelCase)
export interface PathologistFormModel {
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  password: string
  observaciones: string
  isActive: boolean
  firma: string // Default empty
}

// Backend request to create a pathologist (snake_case)
export interface PathologistCreateRequest {
  pathologist_name: string
  initials: string
  pathologist_code: string
  pathologist_email: string
  medical_license: string
  password: string // Associated user password
  signature: string
  observations: string
  is_active: boolean
}

// Backend request to create an auth user
export interface UserCreateRequest {
  email: string
  password: string
  nombre: string
  rol: string
  activo: boolean
}

// Backend response after creating a pathologist
export interface PathologistCreateResponse {
  id: string
  pathologist_name: string
  initials: string
  pathologist_code: string
  pathologist_email: string
  medical_license: string
  signature: string
  observations: string
  is_active: boolean
  created_at: string
  updated_at?: string
}

// Backend response after creating an auth user
export interface UserCreateResponse {
  id: string
  email: string
  nombre: string
  rol: string
  activo: boolean
  fecha_creacion?: string
}

// Creation operation state (UI feedback)
export interface PathologistCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Client-side form validation result
export interface PathologistFormValidation {
  isValid: boolean
  errors: {
    patologoName?: string
    InicialesPatologo?: string
    patologoCode?: string
    PatologoEmail?: string
    registro_medico?: string
    password?: string
    observaciones?: string
  }
}

// Edition (frontend edit form model)
export interface PathologistEditFormModel {
  id: string
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  password?: string
  passwordConfirm?: string
}

export interface PathologistUpdateRequest {
  pathologist_name: string
  initials: string
  pathologist_email: string
  medical_license: string
  observations: string
  is_active: boolean
  password?: string
}

export interface PathologistUpdateResponse {
  id: string
  pathologist_name: string
  initials: string
  pathologist_code: string
  pathologist_email: string
  medical_license: string
  observations: string
  is_active: boolean
  created_at: string
  updated_at: string
}
