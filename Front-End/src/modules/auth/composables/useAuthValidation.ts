import { computed } from 'vue'

export function useAuthValidation() {
  /**
   * Validates if the email has a valid format
   */
  const isValidEmail = (email: string): boolean => /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)

  /**
   * Validates if the password meets minimum requirements
   */
  const isValidPassword = (password: string): boolean => {
    return password.length >= 6
  }

  /**
   * Validates the complete login form
   */
  const validateLoginForm = (email: string, password: string) => {
    const errors: string[] = []

    if (!email) errors.push('El correo es obligatorio')
    else if (!isValidEmail(email)) errors.push('Ingrese un correo electrónico válido')

    if (!password) errors.push('La contraseña es obligatoria')
    else if (!isValidPassword(password)) errors.push('La contraseña debe tener al menos 6 caracteres')

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * Gets the error message for a specific field
   */
  const getFieldError = (field: string, value: string): string => {
    switch (field) {
      case 'email':
        if (!value) return 'El correo es obligatorio'
        if (!isValidEmail(value)) return 'Ingrese un correo electrónico válido'
        break
      case 'password':
        if (!value) return 'La contraseña es obligatoria'
        if (!isValidPassword(value)) return 'La contraseña debe tener al menos 6 caracteres'
        break
    }
    return ''
  }

  return {
    isValidEmail,
    isValidPassword,
    validateLoginForm,
    getFieldError
  }
} 