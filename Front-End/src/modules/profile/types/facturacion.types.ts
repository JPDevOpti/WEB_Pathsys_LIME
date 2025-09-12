// Tipos para el módulo de facturación

// Formulario de creación
export interface FacturacionFormModel {
  facturacionName: string
  facturacionCode: string
  FacturacionEmail: string
  password: string
  observaciones: string
  isActive: boolean
}

// Request para crear facturación
export interface FacturacionCreateRequest {
  facturacion_name: string
  facturacion_code: string
  facturacion_email: string
  password: string // Contraseña para crear el usuario asociado
  observaciones: string
  is_active: boolean
}

// Response de creación
export interface FacturacionCreateResponse {
  id: string
  facturacion_name: string
  facturacion_code: string
  facturacion_email: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion?: string
}

// Estado de creación
export interface FacturacionCreationState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

// Validación del formulario
export interface FacturacionFormValidation {
  isValid: boolean
  errors: {
    facturacionName?: string
    facturacionCode?: string
    FacturacionEmail?: string
    password?: string
    observaciones?: string
  }
}

// Edición
export interface FacturacionEditFormModel {
  id: string
  facturacionName: string
  facturacionCode: string
  FacturacionEmail: string
  observaciones: string
  isActive: boolean
  password?: string
}

export interface FacturacionUpdateRequest {
  facturacion_name: string
  facturacion_email: string
  observaciones: string
  is_active: boolean
  password?: string
}

export interface FacturacionUpdateResponse {
  id: string
  facturacion_name: string
  facturacion_code: string
  facturacion_email: string
  observaciones: string
  is_active: boolean
  fecha_creacion: string
  fecha_actualizacion: string
}

export interface FacturacionEditionState {
  isLoading: boolean
  isSuccess: boolean
  error: string
  successMessage: string
}

export interface FacturacionEditFormValidation {
  isValid: boolean
  errors: {
    facturacionName?: string
    facturacionCode?: string
    FacturacionEmail?: string
    observaciones?: string
  }
}
