export interface PathologistAssignmentFormData {
  patologoId: string
  fechaAsignacion: string
}

export interface CaseModel {
  case_code?: string
  caso_code?: string
  state?: string
  estado?: string
  patient_info?: {
    name?: string
    patient_code?: string
    entity_info?: {
      name?: string
      nombre?: string
    }
  }
  assigned_pathologist?: {
    id?: string
    name?: string
  }
  patologo_asignado?: {
    nombre?: string
  }
  samples?: Array<{
    body_region?: string
    region_cuerpo?: string
  }>
}

export interface PathologistModel {
  id: string
  name: string
  patologo_code?: string
  codigo?: string
  code?: string
  documento?: string
  patologo_name?: string
  nombre?: string
}

export interface AssignmentResult {
  success: boolean
  message?: string
  assignment?: {
    pathologist?: PathologistModel
  }
}

export interface AssignmentEventData {
  codigoCaso: string
  patologo: string
}

