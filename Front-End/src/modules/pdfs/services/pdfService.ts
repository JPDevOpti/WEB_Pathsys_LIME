import axios from 'axios'

const API_BASE_URL = import.meta.env.VITE_API_BASE_URL || 'http://localhost:8000'

export class PdfService {
  static async getCasePdf(caseCode: string): Promise<Blob> {
    try {
      const response = await axios.get(`${API_BASE_URL}/api/v1/casos/caso-code/${caseCode}/pdf`, {
        responseType: 'blob',
        headers: {
          'Accept': 'application/pdf'
        }
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

