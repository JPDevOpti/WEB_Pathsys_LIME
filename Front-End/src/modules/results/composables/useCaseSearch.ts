import { ref, computed } from 'vue'
import casesApiService from '@/modules/cases/services/casesApi.service'
import { usePermissions } from '@/shared/composables/usePermissions'
import { useAuthStore } from '@/stores/auth.store'

export function useCaseSearch() {
  const codigoCaso = ref('')
  const isLoadingSearch = ref(false)
  const casoEncontrado = ref(false)
  const searchError = ref('')
  const casoInfo = ref<any>(null)

  const { isPatologo } = usePermissions()
  const authStore = useAuthStore()

  // Función helper para obtener el nombre del usuario actual
  const getCurrentUserName = (): string | null => {
    if (!authStore.user) return null
    
    let userName = authStore.user.nombre || null

    if (!userName) {
      userName = authStore.user.email
    }
    
    return userName
  }

  // Función helper para obtener el nombre del patólogo asignado
  const getAssignedPathologistName = (caseData: any): string | null => {
    if (!caseData?.patologo_asignado) return null
    
    const pathologistName = caseData.patologo_asignado.nombre || null
    
    return pathologistName
  }

  const handleCodigoChange = (value: string) => {
    // Solo números y guión
    value = value.replace(/[^\d-]/g, '')
    // Máximo 10 chars
    value = value.slice(0, 10)
    // Insertar guión después de 4 dígitos
    if (value.length >= 4 && !value.includes('-')) {
      value = value.slice(0, 4) + '-' + value.slice(4)
    }
    // Evitar múltiples guiones
    const parts = value.split('-')
    if (parts.length > 2) {
      value = parts[0] + '-' + parts.slice(1).join('')
    }
    // Asegurar guión en posición 4
    if (value.includes('-') && value.indexOf('-') !== 4) {
      const digits = value.replace(/-/g, '')
      if (digits.length >= 4) {
        value = digits.slice(0, 4) + '-' + digits.slice(4, 9)
      } else {
        value = digits
      }
    }
    codigoCaso.value = value
  }

  /**
   * Maneja la entrada de solo números en el campo de código de caso
   */
  const keydownHandler = (event: KeyboardEvent) => {
    // Permitir teclas de control (backspace, delete, tab, escape, enter, etc.)
    if (event.key === 'Backspace' || event.key === 'Delete' || event.key === 'Tab' || 
        event.key === 'Escape' || event.key === 'Enter' || event.key === 'ArrowLeft' || 
        event.key === 'ArrowRight' || event.key === 'Home' || event.key === 'End') {
      return true
    }
    
    // Permitir combinaciones de teclas para copiar y pegar
    if ((event.ctrlKey || event.metaKey) && (event.key === 'c' || event.key === 'v' || event.key === 'a')) {
      return true
    }
    
    // Permitir números y guión
    if (/[0-9-]/.test(event.key)) {
      return true
    }
    
    // Bloquear todas las demás teclas
    event.preventDefault()
    return false
  }

  /**
   * Maneja el evento de pegar desde el portapapeles
   */
  const handlePaste = (event: ClipboardEvent) => {
    event.preventDefault()
    const pastedText = event.clipboardData?.getData('text') || ''
    
    // Filtrar solo números y guiones del texto pegado
    const filteredText = pastedText.replace(/[^\d-]/g, '')
    
    if (filteredText) {
      // Aplicar el mismo formato que handleCodigoChange
      let formattedText = filteredText.slice(0, 10)
      
      // Insertar guión después de 4 dígitos si no existe
      if (formattedText.length >= 4 && !formattedText.includes('-')) {
        formattedText = formattedText.slice(0, 4) + '-' + formattedText.slice(4)
      }
      
      // Evitar múltiples guiones
      const parts = formattedText.split('-')
      if (parts.length > 2) {
        formattedText = parts[0] + '-' + parts.slice(1).join('')
      }
      
      // Asegurar guión en posición 4
      if (formattedText.includes('-') && formattedText.indexOf('-') !== 4) {
        const digits = formattedText.replace(/-/g, '')
        if (digits.length >= 4) {
          formattedText = digits.slice(0, 4) + '-' + digits.slice(4, 9)
        } else {
          formattedText = digits
        }
      }
      
      codigoCaso.value = formattedText
    }
  }

  const buscarCaso = async (): Promise<any> => {
    if (!codigoCaso.value.trim()) {
      searchError.value = 'Por favor, ingrese un código de caso'
      return null
    }
    
    isLoadingSearch.value = true
    searchError.value = ''
    casoEncontrado.value = false
    
    try {
      const data = await casesApiService.getCaseByCode(codigoCaso.value.trim())
      
      // Validar permisos para patólogos
      if (isPatologo.value && authStore.user) {
        const nombrePatologoAsignado = getAssignedPathologistName(data)
        const nombreUsuario = getCurrentUserName()
        
        if (!nombrePatologoAsignado) {
          throw new Error('Este caso no tiene un patólogo asignado.')
        }
        
        if (!nombreUsuario) {
          throw new Error('No se pudo identificar tu nombre de usuario. Contacta al administrador.')
        }
        
        if (nombrePatologoAsignado !== nombreUsuario) {
          throw new Error('No tienes permisos para acceder a este caso. Solo puedes acceder a casos donde estés asignado como patólogo.')
        }
      }
      
      casoInfo.value = data
      casoEncontrado.value = true
      return data
    } catch (error: any) {
      casoEncontrado.value = false
      casoInfo.value = null
      searchError.value = error.message || 'Error al buscar el caso'
      return null
    } finally {
      isLoadingSearch.value = false
    }
  }

  const limpiarBusqueda = () => {
    codigoCaso.value = ''
    casoEncontrado.value = false
    searchError.value = ''
    casoInfo.value = null
  }

  const ejecutarBusquedaAutomatica = async (sampleId: string) => {
    if (!sampleId) return
    
    // Simular que se escribió el código en el buscador
    codigoCaso.value = sampleId
    
    // Ejecutar la búsqueda automáticamente
    return await buscarCaso()
  }

  // Computed para validar si el código tiene formato válido
  const isValidCodeFormat = computed(() => {
    return /^\d{4}-\d{5}$/.test(codigoCaso.value)
  })

  // Computed para saber si se puede buscar
  const canSearch = computed(() => {
    return codigoCaso.value.trim().length > 0 && !isLoadingSearch.value
  })

  return {
    // Estado
    codigoCaso,
    isLoadingSearch,
    casoEncontrado,
    searchError,
    casoInfo,
    
    // Computed
    isValidCodeFormat,
    canSearch,
    
    // Métodos
    handleCodigoChange,
    keydownHandler,
    handlePaste,
    buscarCaso,
    limpiarBusqueda,
    ejecutarBusquedaAutomatica,
    
    // Helpers
    getCurrentUserName,
    getAssignedPathologistName
  }
}
