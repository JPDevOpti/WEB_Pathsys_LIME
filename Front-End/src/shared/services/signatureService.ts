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
  async getPatologoFirma(patologoCode: string): Promise<string | null> {
    try {
      // Verificar cache primero
      if (this.signatureCache.has(patologoCode)) {
        console.log('Firma encontrada en cache para código:', patologoCode)
        return this.signatureCache.get(patologoCode) || null
      }

      console.log('Buscando firma para patólogo con código:', patologoCode)
      const url = buildApiUrl(`${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${patologoCode}`)
      console.log('URL completa:', url)

      // Buscar el patólogo por código
      const response = await apiClient.get<any>(url)

      console.log('Respuesta completa del servidor:', response)

      const patologo = response as PatologoFirma | undefined

      console.log('Patólogo encontrado:', patologo)
      console.log('Campo firma del patólogo:', patologo?.firma)

      if (patologo && patologo.firma) {
        console.log('Firma encontrada para patólogo código:', patologoCode, 'Tamaño:', patologo.firma.length)
        // Guardar en cache
        this.signatureCache.set(patologoCode, patologo.firma)
        return patologo.firma
      }

      console.log('No se encontró firma para patólogo código:', patologoCode)
      console.log('Patólogo existe:', !!patologo)
      console.log('Campo firma existe:', !!patologo?.firma)
      console.log('Tipo de firma:', typeof patologo?.firma)
      return null
    } catch (error) {
      console.error('Error al obtener firma del patólogo:', error)
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
        const firma = await this.getPatologoFirma(email)
        if (firma) {
          firmas.set(email, firma)
        }
      })
    )

    return firmas
  }
}

export const signatureService = new SignatureService()
