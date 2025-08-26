import { computed } from 'vue'

export function useAuthValidation() {
  /**
   * Valida si el email tiene un formato válido
   */
  const isValidEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

  /**
   * Valida si la contraseña cumple con los requisitos mínimos
   */
  const isValidPassword = (password: string): boolean => {
    return password.length >= 6
  }

  /**
   * Valida el formulario completo de login
   */
  const validateLoginForm = (email: string, password: string) => {
    const errors: string[] = []

    if (!email) {
      errors.push('El correo electrónico es requerido')
    } else if (!isValidEmail(email)) {
      errors.push('Por favor ingresa un correo electrónico válido')
    }

    if (!password) {
      errors.push('La contraseña es requerida')
    } else if (!isValidPassword(password)) {
      errors.push('La contraseña debe tener al menos 6 caracteres')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  /**
   * Obtiene el mensaje de error para un campo específico
   */
  const getFieldError = (field: string, value: string): string => {
    switch (field) {
      case 'email':
        if (!value) return 'El correo electrónico es requerido'
        if (!isValidEmail(value)) return 'Por favor ingresa un correo electrónico válido'
        break
      case 'password':
        if (!value) return 'La contraseña es requerida'
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