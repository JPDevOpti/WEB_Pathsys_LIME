/**
 * Tipos específicos para la gestión de patólogos en el módulo profile
 */

/**
 * Modelo del formulario de creación de patólogos
 */
export interface PathologistFormModel {
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  password: string
  observaciones: string
  isActive: boolean
  firma: string // Por defecto vacío
}

/**
 * Request para crear un nuevo patólogo (colección patólogos)
 */
export interface PathologistCreateRequest {
  pathologist_name: string
  initials: string
  pathologist_code: string
  pathologist_email: string
  medical_license: string
  password: string // Contraseña para crear el usuario asociado
  signature: string
  observations: string
  is_active: boolean
}

/**
 * Request para crear un usuario (colección auth)
 */
export interface UserCreateRequest {
  email: string
  password: string
  nombre: string
  rol: string
  activo: boolean
}

/**
 * Response de creación de patólogo
 */
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

/**
 * Response de creación de usuario
 */
export interface UserCreateResponse {
  id: string
  email: string
  nombre: string
  rol: string
  activo: boolean
  fecha_creacion?: string
}

/**
 * Estado de la operación de creación
 */
export interface PathologistCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

/**
 * Resultado de validación del formulario
 */
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

// Edición
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
