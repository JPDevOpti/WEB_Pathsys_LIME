import axios from 'axios'
import { API_CONFIG, buildApiUrl } from '@/core/config/api.config'

export class PdfService {
  static async getCasePdf(caseCode: string): Promise<Blob> {
    try {
      const url = buildApiUrl(`${API_CONFIG.ENDPOINTS.CASES}/${encodeURIComponent(caseCode)}/pdf`)
      const response = await axios.get(url, {
        responseType: 'blob',
        headers: { 'Accept': 'application/pdf' }
      })
      return response.data
    } catch (error) {
      console.error('Error al obtener PDF del caso:', error)
      throw new Error('No se pudo generar el PDF del caso')
    }
  }

  static async downloadCasePdf(caseCode: string): Promise<void> {
    try {
      const pdfBlob = await this.getCasePdf(caseCode)
      const url = window.URL.createObjectURL(pdfBlob)
      const link = document.createElement('a')
      link.href = url
      link.download = `caso-${caseCode}.pdf`
      document.body.appendChild(link)
      link.click()
      document.body.removeChild(link)
      window.URL.revokeObjectURL(url)
    } catch (error) {
      console.error('Error al descargar PDF:', error)
      throw error
    }
  }
}

