// Business Domain Constants
export const CASE_STATUS = {
  PENDING: 'pending',
  IN_PROGRESS: 'in_progress',
  COMPLETED: 'completed',
  APPROVED: 'approved',
  REJECTED: 'rejected'
} as const

export const CASE_STATUS_LABELS = {
  [CASE_STATUS.PENDING]: 'Pendiente',
  [CASE_STATUS.IN_PROGRESS]: 'En Progreso',
  [CASE_STATUS.COMPLETED]: 'Completado',
  [CASE_STATUS.APPROVED]: 'Aprobado',
  [CASE_STATUS.REJECTED]: 'Rechazado'
} as const

export const GENDER = {
  MALE: 'M',
  FEMALE: 'F'
} as const

export const GENDER_LABELS = {
  [GENDER.MALE]: 'Masculino',
  [GENDER.FEMALE]: 'Femenino'
} as const

export const USER_ROLES = {
  ADMIN: 'admin',
  PATHOLOGIST: 'pathologist',
  AUXILIARY: 'auxiliary',
  RESIDENT: 'resident',
  BILLING: 'billing',
  ENTITY: 'entity'
} as const

export const USER_ROLE_LABELS = {
  [USER_ROLES.ADMIN]: 'Administrador',
  [USER_ROLES.PATHOLOGIST]: 'Patólogo',
  [USER_ROLES.AUXILIARY]: 'Auxiliar',
  [USER_ROLES.RESIDENT]: 'Residente',
  [USER_ROLES.BILLING]: 'Facturación',
  [USER_ROLES.ENTITY]: 'Entidad'
} as const

export const PRIORITY_LEVELS = {
  LOW: 'low',
  MEDIUM: 'medium',
  HIGH: 'high',
  URGENT: 'urgent'
} as const

export const PRIORITY_LABELS = {
  [PRIORITY_LEVELS.LOW]: 'Baja',
  [PRIORITY_LEVELS.MEDIUM]: 'Media',
  [PRIORITY_LEVELS.HIGH]: 'Alta',
  [PRIORITY_LEVELS.URGENT]: 'Urgente'
} as const