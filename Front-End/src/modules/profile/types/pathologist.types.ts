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
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  password: string // Contraseña para crear el usuario asociado
  firma: string
  observaciones: string
  isActive: boolean
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
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  firma: string
  observaciones: string
  isActive: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
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
}

export interface PathologistUpdateRequest {
  patologoName: string
  InicialesPatologo: string
  PatologoEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  password?: string
}

export interface PathologistUpdateResponse {
  id: string
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  observaciones: string
  isActive: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}
