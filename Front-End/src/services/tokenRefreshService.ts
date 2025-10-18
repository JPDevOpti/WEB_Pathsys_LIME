import { apiClient } from '@/core/config/axios.config'

export interface TokenRefreshResponse {
  access_token: string
  token_type: string
  expires_in: number
}

/**
 * Service to handle automatic token refresh
 */
export class TokenRefreshService {
  private static refreshPromise: Promise<TokenRefreshResponse> | null = null

  /**
   * Refresh the current user's access token
   */
  static async refreshToken(): Promise<TokenRefreshResponse> {
    // Prevent multiple simultaneous refresh requests
    if (this.refreshPromise) {
      return this.refreshPromise
    }

    this.refreshPromise = this.performRefresh()
    
    try {
      const result = await this.refreshPromise
      return result
    } finally {
      this.refreshPromise = null
    }
  }

  /**
   * Perform the actual token refresh API call
   */
  private static async performRefresh(): Promise<TokenRefreshResponse> {
    try {
      const response = await apiClient.post('/auth/refresh')
      
      return response.data as TokenRefreshResponse
    } catch (error: any) {
      console.error('❌ [TOKEN REFRESH] Failed to refresh token:', error)
      throw error
    }
  }

  /**
   * Check if a token is close to expiration (within 15 minutes)
   */
  static isTokenNearExpiration(token: string): boolean {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // Convert to milliseconds
      const now = Date.now()
      const fifteenMinutes = 15 * 60 * 1000 // 15 minutes in milliseconds
      
      return (exp - now) <= fifteenMinutes
    } catch (error) {
      console.error('Error checking token expiration:', error)
      return true // Assume expired if we can't parse
    }
  }

  /**
   * Get the time remaining until token expiration in minutes
   */
  static getTokenTimeRemaining(token: string): number {
    try {
      const payload = JSON.parse(atob(token.split('.')[1]))
      const exp = payload.exp * 1000 // Convert to milliseconds
      const now = Date.now()
      
      return Math.max(0, Math.floor((exp - now) / (60 * 1000))) // Return minutes
    } catch (error) {
      console.error('Error calculating token time remaining:', error)
      return 0
    }
  }
}