import axios from 'axios'
import { API_CONFIG } from './api.config'

/**
 * Instancia configurada de Axios para la API
 */
class ApiClient {
  private instance: any

  constructor() {
    this.instance = axios.create({
      baseURL: import.meta.env.DEV ? API_CONFIG.VERSION : `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}`,
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
        try {
          // Log básico de request
          const method = (config.method || 'GET').toUpperCase()
          const url = `${config.baseURL || ''}${config.url || ''}`
          if (method === 'POST' || method === 'PUT' || method === 'PATCH') {
            console.debug(`➡️ [HTTP:${method}] ${url}`, { data: config.data })
          } else {
            console.debug(`➡️ [HTTP:${method}] ${url}`, { params: config.params })
          }
        } catch {}
        // Read token from either localStorage or sessionStorage to support rememberMe persistence
        const localToken = localStorage.getItem('auth_token')
        const sessionToken = sessionStorage.getItem('auth_token')
        const token = localToken || sessionToken
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`
          console.log('🔑 [AXIOS] Token found and added to request:', {
            source: localToken ? 'localStorage' : 'sessionStorage',
            tokenLength: token.length,
            url: config.url
          })
        } else {
          console.warn('⚠️ [AXIOS] No token found in storage for request:', config.url)
        }
        
        return config
      },
      (error: any) => {
        try { console.error('❌ [HTTP:request] Error preparando request', error) } catch {}
        return Promise.reject(error)
      }
    )

    // Response interceptor - manejo de errores globales
    this.instance.interceptors.response.use(
      (response: any) => {
        try {
          const { config, status } = response || {}
          const method = (config?.method || 'GET').toUpperCase()
          const url = `${config?.baseURL || ''}${config?.url || ''}`
          console.debug(`✅ [HTTP:${method} ${status}] ${url}`, { data: response?.data })
        } catch {}
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
              console.warn('Token expirado detectado en interceptor')
              // No forzar logout ni redirección aquí para evitar romper el flujo
              // Dejar que la UI o el store reaccionen (p.ej. escuchando 'auth-unauthorized')
              try { window.dispatchEvent(new CustomEvent('auth-unauthorized')) } catch {}
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
          try {
            const { config } = error.response
            const method = (config?.method || 'GET').toUpperCase()
            const url = `${config?.baseURL || ''}${config?.url || ''}`
            console.error(`🛑 [HTTP:${method} ${status}] ${url}`, { detail: errorMessage, data })
          } catch {}
        } else if (error.request) {
          // Error de red
          error.message = 'Error de conexión con el servidor'
          try { console.error('🛑 [HTTP] Error de red sin respuesta del servidor') } catch {}
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
