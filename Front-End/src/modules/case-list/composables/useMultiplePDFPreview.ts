import type { Case } from '@/modules/case-list/types/case.types'

export function useMultiplePDFPreview() {
  
  /**
   * Abrir vista previa múltiple en nueva ventana
   */
  function previewMultipleCases(cases: Case[]) {
    if (!cases || cases.length === 0) {
      console.warn('No hay casos para previsualizar')
      return
    }

    try {
      // Crear URL con parámetros de los casos seleccionados
      const caseIds = cases.map(c => c.id).join(',')
      const url = `/preview-multiple?cases=${encodeURIComponent(caseIds)}`
      
      // Abrir en nueva ventana
      const newWindow = window.open(
        url, 
        'multiple-pdf-preview',
        'width=1200,height=900,scrollbars=yes,resizable=yes,status=yes,location=yes,menubar=yes,toolbar=yes'
      )

      if (newWindow) {
        newWindow.focus()
      } else {
        // Fallback si se bloquean las ventanas emergentes
        console.warn('No se pudo abrir la ventana emergente. Redirigiendo...')
        window.location.href = url
      }
    } catch (error) {
      console.error('Error abriendo vista previa múltiple:', error)
      throw error
    }
  }

  /**
   * Verificar si hay casos válidos para previsualizar
   */
  function canPreviewCases(cases: Case[]): boolean {
    return cases && cases.length > 0 && cases.every(c => c.id)
  }

  /**
   * Obtener estadísticas de los casos para previsualizar
   */
  function getCasesStats(cases: Case[]) {
    if (!cases || cases.length === 0) {
      return {
        total: 0,
        byStatus: {},
        byEntity: {},
        hasResults: 0
      }
    }

    const byStatus: Record<string, number> = {}
    const byEntity: Record<string, number> = {}
    let hasResults = 0

    cases.forEach(c => {
      // Contar por estado
      const status = c.status || 'Sin estado'
      byStatus[status] = (byStatus[status] || 0) + 1

      // Contar por entidad
      const entity = c.entity || 'Sin entidad'
      byEntity[entity] = (byEntity[entity] || 0) + 1

      // Contar casos con resultados
      if (c.result && (c.result.diagnosis || c.result.macro || c.result.micro)) {
        hasResults++
      }
    })

    return {
      total: cases.length,
      byStatus,
      byEntity,
      hasResults
    }
  }

  return {
    previewMultipleCases,
    canPreviewCases,
    getCasesStats
  }
}
