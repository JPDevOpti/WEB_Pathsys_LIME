import { computed } from 'vue'

export function useAuthValidation() {
  /**
   * Validates if the email has a valid format
   */
  const isValidEmail = (email: string): boolean => {
    return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email)
  }

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

    if (!email) {
      errors.push('Email is required')
    } else if (!isValidEmail(email)) {
      errors.push('Please enter a valid email address')
    }

    if (!password) {
      errors.push('Password is required')
    } else if (!isValidPassword(password)) {
      errors.push('Password must have at least 6 characters')
    }

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
        if (!value) return 'Email is required'
        if (!isValidEmail(value)) return 'Please enter a valid email address'
        break
      case 'password':
        if (!value) return 'Password is required'
        if (!isValidPassword(value)) return 'Password must have at least 6 characters'
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