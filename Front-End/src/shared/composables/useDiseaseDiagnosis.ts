import { ref, computed } from 'vue'
import type { Disease } from '../services/disease.service'

export function useDiseaseDiagnosis() {
  // Estado del diagnóstico
  const primaryDisease = ref<Disease | null>(null)

  // Computed properties
  const hasDisease = computed(() => !!primaryDisease.value)

  // Funciones para manejar el diagnóstico principal
  const setPrimaryDisease = (disease: Disease | null) => {
    primaryDisease.value = disease
  }

  const clearPrimaryDisease = () => {
    primaryDisease.value = null
  }

  // Función para limpiar todo el diagnóstico
  const clearDiagnosis = () => {
    primaryDisease.value = null
  }

  // Función para formatear el diagnóstico para el reporte
  const formatDiagnosisForReport = (): string => {
    if (primaryDisease.value) {
      return `${primaryDisease.value.codigo} - ${primaryDisease.value.nombre}`
    }
    return ''
  }

  // Función para obtener el diagnóstico en formato estructurado
  const getDiagnosisData = () => {
    return {
      primary: primaryDisease.value,
      formatted: formatDiagnosisForReport()
    }
  }

  // Función para validar el diagnóstico
  const validateDiagnosis = (): { isValid: boolean; errors: string[] } => {
    const errors: string[] = []

    if (!primaryDisease.value) {
      errors.push('Debe seleccionar un diagnóstico')
    }

    return {
      isValid: errors.length === 0,
      errors
    }
  }

  return {
    // Estado
    primaryDisease,
    
    // Computed
    hasDisease,
    
    // Funciones principales
    setPrimaryDisease,
    clearPrimaryDisease,
    clearDiagnosis,
    formatDiagnosisForReport,
    getDiagnosisData,
    validateDiagnosis
  }
}
