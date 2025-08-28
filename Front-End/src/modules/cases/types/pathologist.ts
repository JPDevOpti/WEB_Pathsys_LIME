export interface FormPathologistInfo {
  id: string
  nombre: string
  iniciales?: string
  documento: string
  email: string
  medicalLicense: string
  isActive: boolean
}

export interface PathologistAssignmentData {
  caseId: string
  pathologistId: string
  fechaAsignacion: string
  observaciones?: string
}

export interface PathologistAssignmentState {
  isAssigned: boolean
  assignedDate?: string
  pathologist?: FormPathologistInfo
}

export interface PathologistFormData {
  patologoId: string
  fechaAsignacion: string
}

export interface PathologistFormErrors {
  patologoId: string[]
  fechaAsignacion: string[]
}

export interface PathologistAssignmentResult {
  success: boolean
  assignment?: PathologistAssignmentState
  message?: string
}
