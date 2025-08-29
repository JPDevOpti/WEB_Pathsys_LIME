import apiClient from '@/core/config/axios.config'
import { API_CONFIG, buildApiUrl } from '@/core/config/api.config'

export interface PatologoFirma {
  _id: {
    $oid: string
  }
  patologoName: string
  InicialesPatologo: string
  patologoCode: string
  PatologoEmail: string
  registro_medico: string
  isActive: boolean
  firma: string
  observaciones: string
  fecha_creacion: {
    $date: string
  }
  fecha_actualizacion: {
    $date: string
  }
  id: string
}

class SignatureService {
  private signatureCache = new Map<string, string>()

    /**
   * Obtiene la firma de un patólogo por su código
   */
  async getSignature(patologoCode: string): Promise<string | null> {
    try {
      // Verificar cache primero
      if (this.signatureCache.has(patologoCode)) {
        return this.signatureCache.get(patologoCode) || null
      }

      // Buscar en el backend
      const url = buildApiUrl(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${patologoCode}`)
      const response = await apiClient.get<any>(url)
      
      if (!response.ok) {
        if (response.status === 404) {
          return null
        }
        throw new Error(`HTTP error! status: ${response.status}`)
      }
      
      const patologo = response.data
      
      if (patologo && patologo.firma && patologo.firma.length > 0) {
        // Guardar en cache
        this.signatureCache.set(patologoCode, patologo.firma)
        return patologo.firma
      }
      
      return null
    } catch (error) {
      return null
    }
  }

  /**
   * Limpia el cache de firmas
   */
  clearCache(): void {
    this.signatureCache.clear()
  }

  /**
   * Obtiene múltiples firmas de una vez
   */
  async getMultipleFirmas(emails: string[]): Promise<Map<string, string>> {
    const firmas = new Map<string, string>()
    
    await Promise.all(
      emails.map(async (email) => {
        const firma = await this.getSignature(email)
        if (firma) {
          firmas.set(email, firma)
        }
      })
    )

    return firmas
  }
}

export const signatureService = new SignatureService()
