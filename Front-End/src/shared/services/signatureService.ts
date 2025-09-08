import apiClient from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export interface PatologoSignatureResponse {
  patologo_code: string
  firma: string | null
}

/**
 * Servicio específico para obtener firmas de patólogos usando el endpoint dedicado
 */
class SignatureService {
  private signatureCache = new Map<string, string>()

  /**
   * Obtiene solo la firma de un patólogo por su código usando el endpoint específico
   * @param patologoCode - Código del patólogo
   * @returns Promise con la firma o null si no existe
   */
  async getSignature(patologoCode: string): Promise<string | null> {
    try {
      console.log(`SignatureService - obteniendo firma para patólogo: ${patologoCode}`)
      
      // Verificar cache primero
      if (this.signatureCache.has(patologoCode)) {
        const cachedSignature = this.signatureCache.get(patologoCode) || null
        console.log(`SignatureService - firma encontrada en cache para ${patologoCode}`)
        return cachedSignature
      }

      // Usar el nuevo endpoint específico para firmas
      const response = await apiClient.get<PatologoSignatureResponse>(
        `${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${patologoCode}/firma`
      )
      
      console.log(`SignatureService - respuesta del endpoint firma:`, response)
      
      // Extraer los datos de la respuesta de axios
      const data = (response as any).data || response
      const firma = data.firma
      
      if (firma && firma.length > 0) {
        // Guardar en cache
        this.signatureCache.set(patologoCode, firma)
        console.log(`SignatureService - firma encontrada y guardada en cache para ${patologoCode}`)
        return firma
      }
      
      console.log(`SignatureService - no se encontró firma para patólogo ${patologoCode}`)
      return null
      
    } catch (error: any) {
      console.warn(`SignatureService - error obteniendo firma para patólogo ${patologoCode}:`, error)
      
      // Si es un 404, el patólogo no existe o no tiene firma
      if (error.response?.status === 404) {
        console.warn(`SignatureService - patólogo ${patologoCode} no encontrado o sin firma`)
        return null
      }
      
      // Para otros errores, retornamos null pero logueamos el error
      console.error(`SignatureService - error inesperado:`, error)
      return null
    }
  }

  /**
   * Obtiene la respuesta completa del endpoint de firma (incluye código y firma)
   * @param patologoCode - Código del patólogo
   * @returns Promise con la respuesta completa o null
   */
  async getSignatureData(patologoCode: string): Promise<PatologoSignatureResponse | null> {
    try {
      console.log(`SignatureService - obteniendo datos de firma para patólogo: ${patologoCode}`)
      
      const response = await apiClient.get<PatologoSignatureResponse>(
        `${API_CONFIG.ENDPOINTS.PATHOLOGISTS}/${patologoCode}/firma`
      )
      
      const data = (response as any).data || response
      console.log(`SignatureService - datos de firma obtenidos para ${patologoCode}:`, data)
      
      return data
    } catch (error: any) {
      console.warn(`SignatureService - error obteniendo datos de firma para patólogo ${patologoCode}:`, error)
      return null
    }
  }

  /**
   * Limpia el cache de firmas
   */
  clearCache(): void {
    this.signatureCache.clear()
    console.log('SignatureService - cache de firmas limpiado')
  }

  /**
   * Obtiene múltiples firmas de una vez
   */
  async getMultipleSignatures(patologoCodes: string[]): Promise<Map<string, string>> {
    const firmas = new Map<string, string>()
    
    await Promise.all(
      patologoCodes.map(async (code) => {
        const firma = await this.getSignature(code)
        if (firma) {
          firmas.set(code, firma)
        }
      })
    )

    return firmas
  }
}

export const signatureService = new SignatureService()
