// Component Props Types
export interface BaseButtonProps {
  variant?: 'primary' | 'secondary' | 'danger' | 'success'
  size?: 'sm' | 'md' | 'lg'
  disabled?: boolean
  loading?: boolean
}

export interface FormInputProps {
  modelValue?: string | number
  type?: 'text' | 'email' | 'password' | 'number'
  placeholder?: string
  disabled?: boolean
  required?: boolean
  error?: string
}

export interface ModalProps {
  show: boolean
  title?: string
  size?: 'sm' | 'md' | 'lg' | 'xl'
  closable?: boolean
}

export interface CardProps {
  title?: string
  loading?: boolean
  padding?: boolean
}

export interface NotificationProps {
  type: 'success' | 'error' | 'warning' | 'info'
  message: string
  duration?: number
  closable?: boolean
}