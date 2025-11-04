export interface Patient {
  id: string
  fullName: string
  document: string
  age: number
  entity?: string
  entityCode?: string
  sexo?: string
  tipoAtencion?: string
  observaciones?: string
  pruebasAnteriores?: PruebaAnterior[]
}

export interface PruebaAnterior {
  id: string
  codigo: string
  nombre: string
  fecha: string
  estado: string
  resultado?: string
}

export interface Sample {
  id: string
  type: string
  collectedAt: string
  status: 'pending' | 'in-progress' | 'finalized'
  patientId: string
}

export interface Template {
  id: string
  name: string
  description?: string
  content: string
}

export interface Attachment {
  id: string
  fileName: string
  fileType: string
  sizeKb: number
}

export interface ResultDraft {
  sampleId: string
  templateId?: string
  content: string
  attachments: Attachment[]
  lastSavedAt?: string
}

export interface PreviewData {
  html: string
}


// Datos completos del caso (mock realista)
export interface CaseEntidadInfo {
  id: string
  name: string
}

export interface CasePaciente {
  patient_code: string
  name: string
  age: number
  gender: string
  entity_info: CaseEntidadInfo
  care_type: string
  observations: string
  updated_at: string
}

export interface CasePrueba {
  id: string
  name: string
}

export interface CaseMuestra {
  body_region: string
  tests: CasePrueba[]
}

export interface CasePatologoAsignado {
  id: string
  name: string
}

export interface CaseDetails {
  _id: string
  case_code: string
  patient_info: CasePaciente
  requesting_physician?: string
  samples: CaseMuestra[]
  state: string
  created_at: string
  updated_at: string
  signed_at?: string
  observations?: string
  active?: boolean
  assigned_pathologist?: CasePatologoAsignado
  updated_by?: string
  entity_info?: CaseEntidadInfo
  service?: string
  result?: {
    diagnosis?: string
    macro_result?: string
    micro_result?: string
    observations?: string | null
    cie10_diagnosis?: {
      code: string
      name: string
      id?: string
    }
    cieo_diagnosis?: {
      code: string
      name: string
      id?: string
    }
    diagnostico_cie10?: {
      codigo: string
      nombre: string
      id?: string
    }
    diagnostico_cieo?: {
      codigo: string
      nombre: string
      id?: string
    }
  }
}


