import type { Case } from '../types/case.types'

export function useExcelExport() {
  async function exportCasesToExcel(cases: Case[]) {
    const data = cases.map(c => ({
      'ID Caso': c.id,
      'Tipo de Muestra': c.sampleType,
      'Paciente': c.patient.fullName,
      'Cédula': c.patient.dni,
      'Entidad': c.entity,
      'Médico': c.requester,
      'Estado': c.status,
      'Fecha Recepción': c.receivedAt,
  'Fecha Firma': c.deliveredAt || '',
      'Pruebas': c.tests.join(', ')
    }))
    const XLSX = await import('xlsx')
    const ws = XLSX.utils.json_to_sheet(data)
    const wb = XLSX.utils.book_new()
    XLSX.utils.book_append_sheet(wb, ws, 'Casos')
    XLSX.writeFile(wb, 'cases.xlsx')
  }

  return { exportCasesToExcel }
}


