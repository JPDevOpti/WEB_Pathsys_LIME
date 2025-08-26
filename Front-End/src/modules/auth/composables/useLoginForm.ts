import { ref, computed } from 'vue'
import { useAuthStore } from '@/stores/auth.store'
import { useAuthValidation } from './useAuthValidation'
import type { LoginRequest } from '../types/auth.types'

export function useLoginForm() {
  const authStore = useAuthStore()
  const { validateLoginForm, isValidEmail, isValidPassword } = useAuthValidation()

  const email = ref('')
  const password = ref('')
  const rememberMe = ref(false)
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const emailError = computed(() => {
    if (!email.value) return ''
    if (!isValidEmail(email.value)) {
      return 'Por favor ingresa un correo electrónico válido'
    }
    return ''
  })

  const passwordError = computed(() => {
    if (!password.value) return ''
    if (!isValidPassword(password.value)) {
      return 'La contraseña debe tener al menos 6 caracteres'
    }
    return ''
  })

  const isFormValid = computed(() => {
    return email.value && 
           password.value && 
           isValidEmail(email.value) && 
           isValidPassword(password.value)
  })

  const handleSubmit = async (): Promise<boolean> => {
    if (!isFormValid.value) {
      error.value = 'Por favor completa todos los campos correctamente'
      return false
    }

    isLoading.value = true
    error.value = null

    try {
      const credentials: LoginRequest = {
        email: email.value,
        password: password.value
      }

      const success = await authStore.login(credentials)
      
      if (success) {
        // Limpiar formulario
        resetForm()
        return true
      } else {
        error.value = authStore.error || 'Error al iniciar sesión'
        return false
      }
    } catch (err) {
      error.value = 'Error de conexión. Verifica tu conexión a internet.'
      return false
    } finally {
      isLoading.value = false
    }
  }

  const resetForm = () => {
    email.value = ''
    password.value = ''
    rememberMe.value = false
    error.value = null
  }

  const loadSavedData = () => {
    const savedEmail = localStorage.getItem('saved_email')
    const savedRememberMe = localStorage.getItem('saved_remember_me')
    
    if (savedEmail) {
      email.value = savedEmail
    }
    
    if (savedRememberMe === 'true') {
      rememberMe.value = true
    }
  }

  const saveData = () => {
    if (rememberMe.value) {
      localStorage.setItem('saved_email', email.value)
      localStorage.setItem('saved_remember_me', 'true')
    } else {
      localStorage.removeItem('saved_email')
      localStorage.removeItem('saved_remember_me')
    }
  }

  return {
    email,
    password,
    rememberMe,
    isLoading,
    error,
    emailError,
    passwordError,
    isFormValid,
    handleSubmit,
    resetForm,
    loadSavedData,
    saveData
  }
} 