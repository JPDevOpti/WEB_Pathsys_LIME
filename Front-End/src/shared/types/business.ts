// Business Domain Types
export interface Pathologist {
  id: number
  name: string
  email: string
  specialization?: string
  active: boolean
}

export interface Entity {
  id: number
  name: string
  code: string
  municipality?: string
  active: boolean
}

export interface Test {
  id: number
  name: string
  code: string
  description?: string
  active: boolean
}

export interface Disease {
  id: number
  name: string
  code: string
  category?: string
}

export interface BodyRegion {
  id: number
  name: string
  code: string
}

export interface Municipality {
  id: number
  name: string
  code: string
  department?: string
}

export interface Patient {
  id: number
  firstName: string
  lastName: string
  documentNumber: string
  birthDate: string
  gender: 'M' | 'F'
  entityId: number
  municipalityId?: number
}

export interface Case {
  id: number
  patientId: number
  entityId: number
  testId: number
  pathologistId?: number
  status: 'pending' | 'in_progress' | 'completed' | 'approved'
  createdAt: string
  updatedAt: string
}