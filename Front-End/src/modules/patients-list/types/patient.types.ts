// Enums según la documentación del backend
export enum IdentificationType {
  CC = 1,           // Cédula de Ciudadanía
  CE = 2,           // Cédula de Extranjería
  TI = 3,           // Tarjeta de Identidad
  PA = 4,           // Pasaporte
  RC = 5,           // Registro Civil
  DE = 6,           // Documento Extranjero
  NIT = 7,          // NIT
  CD = 8,           // Carnet Diplomático
  SC = 9            // Salvoconducto
}

export type Gender = 'Masculino' | 'Femenino'
export type CareType = 'Ambulatorio' | 'Hospitalizado'

// Interfaz principal del paciente (coincide con PatientResponse del backend)
export interface Patient {
  id: string
  patient_code: string
  identification_type: IdentificationType
  identification_number: string
  first_name: string
  second_name?: string
  first_lastname: string
  second_lastname?: string
  birth_date: string
  gender: Gender
  location: {
    municipality_code: string
    municipality_name: string
    subregion: string
    address?: string
  }
  entity_info: {
    id: string
    name: string
  }
  care_type: CareType
  observations?: string
  created_at: string
  updated_at: string
  
  // Propiedades computadas (no vienen del backend)
  full_name?: string
  age?: number
}

export interface PatientCase {
  id: string
  caseCode?: string
  sampleType: string
  status: string
  receivedAt: string
  deliveredAt?: string
  signedAt?: string
  tests: string[]
  pathologist?: string
  requester: string
  entity: string
  priority?: string
}

// Filtros de búsqueda (coincide con /search/advanced del backend)
export interface PatientFilters {
  // Búsqueda general
  search?: string
  
  // Filtros de identificación
  identification_type?: IdentificationType
  identification_number?: string
  
  // Filtros de nombre
  first_name?: string
  first_lastname?: string
  
  // Filtros de fecha de nacimiento
  birth_date_from?: string
  birth_date_to?: string
  
  // Filtros de ubicación
  municipality_code?: string
  municipality_name?: string
  subregion?: string
  
  // Filtros de edad
  age_min?: number
  age_max?: number
  
  // Filtros de entidad y atención
  entity?: string
  gender?: Gender
  care_type?: CareType
  
  // Filtros de fecha de creación
  date_from?: string
  date_to?: string
  
  // Paginación
  skip?: number
  limit?: number
}

export type PatientSortKey = keyof Pick<Patient, 'patient_code' | 'identification_number' | 'first_name' | 'first_lastname' | 'birth_date' | 'gender' | 'care_type' | 'created_at' | 'updated_at'>
export type SortOrder = 'asc' | 'desc'

export interface PatientStats {
  total: number
  byEntity: Record<string, number>
  byGender: Record<string, number>
  byCareType: Record<string, number>
  byAgeGroup: Record<string, number>
}

// Helpers para conversión de tipos
export const getIdentificationTypeLabel = (type: IdentificationType): string => {
  const labels: Record<IdentificationType, string> = {
    [IdentificationType.CC]: 'CC',
    [IdentificationType.CE]: 'CE',
    [IdentificationType.TI]: 'TI',
    [IdentificationType.PA]: 'Pasaporte',
    [IdentificationType.RC]: 'RC',
    [IdentificationType.DE]: 'Doc. Extranjero',
    [IdentificationType.NIT]: 'NIT',
    [IdentificationType.CD]: 'Carnet Dip.',
    [IdentificationType.SC]: 'Salvoconducto'
  }
  return labels[type] || 'Desconocido'
}

export const getGenderLabel = (gender: Gender): string => {
  return gender === 'Masculino' ? 'M' : 'F'
}