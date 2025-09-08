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
  codigo: string
  nombre: string
}

export interface CasePaciente {
  paciente_code: string
  nombre: string
  edad: number
  sexo: string
  entidad_info: CaseEntidadInfo
  tipo_atencion: string
  observaciones: string
  fecha_actualizacion: string
}

export interface CasePrueba {
  id: string
  nombre: string
}

export interface CaseMuestra {
  region_cuerpo: string
  pruebas: CasePrueba[]
}

export interface CasePatologoAsignado {
  codigo: string
  nombre: string
}

export interface CaseDetails {
  _id: string
  caso_code: string
  paciente: CasePaciente
  medico_solicitante?: { nombre: string }
  muestras: CaseMuestra[]
  estado: string
  fecha_creacion: string
  fecha_firma: string | null
  fecha_actualizacion: string
  observaciones_generales?: string
  is_active: boolean
  patologo_asignado?: CasePatologoAsignado
  actualizado_por?: string
  entidad_info?: CaseEntidadInfo
  servicio?: string
  resultado?: {
    diagnostico?: string
    diagnostico_cie10?: { codigo: string; nombre: string } | null
    diagnostico_cieo?: { codigo: string; nombre: string } | null
    observaciones?: string | null
  }
}


