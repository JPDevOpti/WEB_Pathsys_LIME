import axios from 'axios'
import { API_CONFIG } from './api.config'

/**
 * Instancia configurada de Axios para la API
 */
class ApiClient {
  private instance: any

  constructor() {
    this.instance = axios.create({
      baseURL: `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}`,
      timeout: API_CONFIG.TIMEOUT,
      headers: API_CONFIG.DEFAULT_HEADERS,
      // Configuración para manejar redirects
      maxRedirects: 5,
      validateStatus: function (status: number) {
        // Considerar successful los códigos 2xx y 3xx
        return status >= 200 && status < 400
      }
    })

    this.setupInterceptors()
  }

  /**
   * Configurar interceptors para requests y responses
   */
  private setupInterceptors(): void {
    // Request interceptor - agregar token de autenticación
    this.instance.interceptors.request.use(
      (config: any) => {
        const token = localStorage.getItem('auth_token')
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
        }
        
        return config
      },
      (error: any) => {
        return Promise.reject(error)
      }
    )

    // Response interceptor - manejo de errores globales
    this.instance.interceptors.response.use(
      (response: any) => {
        return response
      },
      (error: any) => {
        // Manejo específico de errores HTTP
        if (error.response) {
          const { status, data } = error.response
          
          switch (status) {
            case 307:
            case 308:
              // Redirects permanentes/temporales - debería ser manejado automáticamente
              break
              
            case 401:
              // Token expirado o inválido - manejar de forma más suave
              console.warn('Token expirado detectado en interceptor')
              // No hacer logout inmediato, dejar que el store lo maneje
              break
              
            case 403:
              break
              
            case 404:
              break
              
            case 422:
              // Error de validación - devolver detalles
              break
              
            case 500:
              break
              
            default:
              break
          }
          
          // Normalizar el mensaje de error
          const errorMessage = data?.detail || data?.message || `Error HTTP ${status}`
          error.message = errorMessage
        } else if (error.request) {
          // Error de red
          error.message = 'Error de conexión con el servidor'
        }
        
        return Promise.reject(error)
      }
    )
  }

  /**
   * Métodos HTTP
   */
  async get<T = any>(url: string, config?: any): Promise<T> {
    const response = await this.instance.get(url, config) as { data: T }
    return response.data
  }

  async post<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.post(url, data, config) as { data: T }
    return response.data
  }

  async put<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.put(url, data, config) as { data: T }
    return response.data
  }

  async patch<T = any>(url: string, data?: any, config?: any): Promise<T> {
    const response = await this.instance.patch(url, data, config) as { data: T }
    return response.data
  }

  async delete<T = any>(url: string, config?: any): Promise<T> {
    const response = await this.instance.delete(url, config) as { data: T }
    return response.data
  }

  /**
   * Obtener la instancia de Axios para usos específicos
   */
  getAxiosInstance(): any {
    return this.instance
  }
}

// Exportar instancia singleton
export const apiClient = new ApiClient()
export default apiClient
