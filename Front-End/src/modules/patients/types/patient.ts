// Enums para tipos de identificación
export enum IdentificationType {
  CEDULA_CIUDADANIA = 1,
  CEDULA_EXTRANJERIA = 2,
  TARJETA_IDENTIDAD = 3,
  PASAPORTE = 4,
  REGISTRO_CIVIL = 5,
  DOCUMENTO_EXTRANJERO = 6,
  NIT = 7,
  CARNET_DIPLOMATICO = 8,
  SALVOCONDUCTO = 9
}

// Enums para género y tipo de atención
export type Gender = 'Masculino' | 'Femenino'
export type CareType = 'Ambulatorio' | 'Hospitalizado'

// Interfaces para ubicación
export interface Location {
  municipality_code: string
  municipality_name: string
  subregion: string
  address: string
}

// Interfaces para información de entidad
export interface EntityInfo {
  id: string
  name: string
}

// Interface principal para datos del paciente
export interface PatientData {
  patient_code: string
  identification_type: IdentificationType
  identification_number: string
  first_name: string
  second_name?: string
  first_lastname: string
  second_lastname?: string
  birth_date: string
  age?: number
  gender: Gender
  location?: Location
  entity_info: EntityInfo
  care_type: CareType
  observations?: string
  created_at?: string
  updated_at?: string
}

// Interface para crear paciente
export interface CreatePatientRequest {
  identification_type: IdentificationType
  identification_number: string
  first_name: string
  second_name?: string
  first_lastname: string
  second_lastname?: string
  birth_date: string
  gender: Gender
  location?: Location
  entity_info: EntityInfo
  care_type: CareType
  observations?: string
}

// Interface para actualizar paciente
export interface UpdatePatientRequest {
  first_name?: string
  second_name?: string
  first_lastname?: string
  second_lastname?: string
  birth_date?: string
  gender?: Gender
  location?: Partial<Location>
  entity_info?: Partial<EntityInfo>
  care_type?: CareType
  observations?: string
}

// Interface para cambio de identificación
export interface ChangeIdentificationRequest {
  new_identification_type: IdentificationType
  new_identification_number: string
}

// Interface para búsqueda de pacientes
export interface PatientSearchParams {
  identification_type?: IdentificationType
  identification_number?: string
  first_name?: string
  first_lastname?: string
  birth_date_start?: string
  birth_date_end?: string
  age_min?: number
  age_max?: number
  gender?: Gender
  municipality_code?: string
  subregion?: string
  entity_id?: string
  entity_name?: string
  care_type?: CareType
  created_at_start?: string
  created_at_end?: string
  skip?: number
  limit?: number
}

// Interface para resultados de búsqueda
export interface PatientSearchResult {
  patient_code: string
  identification_type: IdentificationType
  identification_number: string
  full_name: string
  age: number
  gender: Gender
  entity_name: string
  care_type: CareType
  municipality_name: string
  created_at: string
}

// Interface para datos del formulario
export interface PatientFormData {
  identification_type: IdentificationType | ''
  identification_number: string
  first_name: string
  second_name: string
  first_lastname: string
  second_lastname: string
  birth_date: string
  gender: Gender | ''
  municipality_code: string
  municipality_name: string
  subregion: string
  address: string
  entity_id: string
  entity_name: string
  care_type: CareType | ''
  observations: string
}

// Interface para errores de validación
export interface PatientValidationErrors {
  identification_type?: string[]
  identification_number?: string[]
  first_name?: string[]
  second_name?: string[]
  first_lastname?: string[]
  second_lastname?: string[]
  birth_date?: string[]
  gender?: string[]
  location?: {
    municipality_code?: string[]
    municipality_name?: string[]
    subregion?: string[]
    address?: string[]
  }
  entity_info?: {
    id?: string[]
    name?: string[]
  }
  care_type?: string[]
  observations?: string[]
}

// Interface para respuesta de conteo
export interface PatientCountResponse {
  total: number
}

// Utilidades para nombres de tipos de identificación
export const IDENTIFICATION_TYPE_NAMES: Record<IdentificationType, string> = {
  [IdentificationType.CEDULA_CIUDADANIA]: 'Cédula de Ciudadanía',
  [IdentificationType.CEDULA_EXTRANJERIA]: 'Cédula de Extranjería',
  [IdentificationType.TARJETA_IDENTIDAD]: 'Tarjeta de Identidad',
  [IdentificationType.PASAPORTE]: 'Pasaporte',
  [IdentificationType.REGISTRO_CIVIL]: 'Registro Civil',
  [IdentificationType.DOCUMENTO_EXTRANJERO]: 'Documento Extranjero',
  [IdentificationType.NIT]: 'NIT',
  [IdentificationType.CARNET_DIPLOMATICO]: 'Carnet Diplomático',
  [IdentificationType.SALVOCONDUCTO]: 'Salvoconducto'
}
