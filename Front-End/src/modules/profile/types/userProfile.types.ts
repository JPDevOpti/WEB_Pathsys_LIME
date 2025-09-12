export type UserRole = 'admin' | 'patologo' | 'residente' | 'auxiliar' | 'facturacion'

export type DocumentType = 'CC' | 'CE' | 'PP'

export interface RoleSpecificData {
  // Campos clínicos alineados al backend
  iniciales?: string
  registroMedico?: string
  firmaUrl?: string
  observaciones?: string
}

export interface UserProfile {
  id: string
  firstName: string
  lastName: string
  email: string
  phone?: string
  document: string
  documentType: DocumentType
  role: UserRole
  avatar?: string
  isActive: boolean
  lastLogin?: Date
  createdAt: Date
  updatedAt: Date
  roleSpecificData?: RoleSpecificData
}

export interface ActionItem {
  id: string
  label: string
  icon: string
  action: () => void
  isEnabled: boolean
  variant?: 'primary' | 'secondary' | 'danger'
}

export interface ProfileFormData {
  firstName: string
  lastName: string
  email: string
  phone: string
  document: string
  documentType: DocumentType
}

export interface ValidationError {
  field: string
  message: string
}

export interface ProfileEditState {
  isLoading: boolean
  hasChanges: boolean
  errors: ValidationError[]
  originalData: ProfileFormData
  currentData: ProfileFormData
}

export type ProfileEditPayload =
  | {
      role: 'patologo'
      patologoName: string
      InicialesPatologo?: string
      PatologoEmail: string
      registro_medico: string
      password?: string
      observaciones?: string
    }
  | {
      role: 'residente'
      residenteName: string
      InicialesResidente?: string
      ResidenteEmail: string
      registro_medico: string
      password?: string
      observaciones?: string
    }
  | {
      role: 'auxiliar'
      auxiliarName: string
      auxiliarCode: string
      AuxiliarEmail: string
      password?: string
      observaciones?: string
    }
  | {
      role: 'facturacion'
      facturacionName: string
      facturacionCode: string
      FacturacionEmail: string
      password?: string
      observaciones?: string
    }
  | {
      role: 'admin'
      firstName: string
      lastName: string
      email: string
    }