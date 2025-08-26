/**
 * Utilidad para probar la conexión con el backend
 */

import { apiClient } from '@/core/config/axios.config'
import { API_CONFIG } from '@/core/config/api.config'

export async function testBackendConnection() {
  try {
    // Test 1: Health check (si existe)
    try {
      await apiClient.get('/health')
    } catch (healthError) {
      // Health check no disponible
    }

    // Test 2: Estadísticas de casos
    try {
      await apiClient.get('/casos/estadisticas')
    } catch (casosError) {
      console.error('❌ Error en estadísticas de casos:', casosError)
    }

    // Test 3: Estadísticas de pacientes
    try {
      await apiClient.get('/pacientes/estadisticas')
    } catch (pacientesError) {
      console.error('❌ Error en estadísticas de pacientes:', pacientesError)
    }

    // Test 4: Lista de casos
    try {
      await apiClient.get('/casos/', { 
        params: { limite: 5 } 
      })
    } catch (casosListError) {
      console.error('❌ Error en lista de casos:', casosListError)
    }

  } catch (error) {
    console.error('💥 Error general de conexión:', error)
  }
}

// Función para probar desde la consola del navegador
(window as any).testBackendConnection = testBackendConnection