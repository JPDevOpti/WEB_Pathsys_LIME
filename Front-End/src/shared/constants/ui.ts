// UI Constants
export const BUTTON_VARIANTS = {
  PRIMARY: 'primary',
  SECONDARY: 'secondary',
  DANGER: 'danger',
  SUCCESS: 'success'
} as const

export const BUTTON_SIZES = {
  SMALL: 'sm',
  MEDIUM: 'md',
  LARGE: 'lg'
} as const

export const MODAL_SIZES = {
  SMALL: 'sm',
  MEDIUM: 'md',
  LARGE: 'lg',
  EXTRA_LARGE: 'xl'
} as const

export const NOTIFICATION_TYPES = {
  SUCCESS: 'success',
  ERROR: 'error',
  WARNING: 'warning',
  INFO: 'info'
} as const

export const INPUT_TYPES = {
  TEXT: 'text',
  EMAIL: 'email',
  PASSWORD: 'password',
  NUMBER: 'number',
  DATE: 'date'
} as const

// Default values
export const DEFAULT_PAGINATION = {
  PAGE: 1,
  LIMIT: 10,
  MAX_LIMIT: 100
} as const

export const DEFAULT_NOTIFICATION_DURATION = 5000 // 5 seconds