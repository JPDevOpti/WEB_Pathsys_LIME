export interface CaseApprovalPatient {
  id: string
  fullName: string
  age?: number
  sex?: string
  attentionType?: string
  entity?: string
}

export interface CaseApprovalTest {
  id: string
  name?: string
  quantity: number
}

export interface CaseApprovalSubsample {
  bodyRegion?: string
  tests: CaseApprovalTest[]
}

export interface CaseApprovalResultDiagnosisCode {
  codigo: string
  nombre: string
}

export interface CaseApprovalResult {
  method?: string
  macro?: string
  micro?: string
  diagnosis?: string
  diagnostico_cie10?: CaseApprovalResultDiagnosisCode
  diagnostico_cieo?: CaseApprovalResultDiagnosisCode
}

export interface CaseApprovalDetails {
  id: string
  caseCode?: string
  status?: string
  patient?: CaseApprovalPatient
  pathologist?: string
  receivedAt?: string
  deliveredAt?: string
  subsamples?: CaseApprovalSubsample[]
  result?: CaseApprovalResult
  newAssignedTests?: CaseApprovalTest[]
  description?: string
  createdAt?: string
  updatedAt?: string
}
