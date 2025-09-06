// Configuración de la API del Backend
export const API_CONFIG = {
  // URL base de la API
  BASE_URL: (import.meta as any).env?.VITE_API_BASE_URL || 'http://localhost:8000',
  
  // Versión de la API
  VERSION: '/api/v1',
  
  // Timeout para las peticiones (en ms)
  TIMEOUT: 30000,
  
  // Headers por defecto
  DEFAULT_HEADERS: {
    'Content-Type': 'application/json',
    'Accept': 'application/json',
  },
  
  // Endpoints principales
  ENDPOINTS: {
    CASES: '/casos',
    TESTS: '/pruebas',
    ENTITIES: '/entidades',
    PATHOLOGISTS: '/patologos',
    PATIENTS: '/pacientes',
    RESIDENTS: '/residentes',  
    AUXILIARIES: '/auxiliares', 
    AUTH: {
      LOGIN: '/auth/login',
      LOGOUT: '/auth/logout',
      REFRESH: '/auth/refresh',
    },
    CASOS: {
      TEST: '/casos/test',
      ESTADISTICAS_PRUEBAS: '/casos/estadisticas-pruebas-mensual',
      DETALLE_PRUEBA: '/casos/detalle-prueba',
      PATOLOGOS_POR_PRUEBA: '/casos/patologos-por-prueba',
      ESTADISTICAS_ENTIDADES: '/casos/estadisticas-entidades-mensual',
      DETALLE_ENTIDAD: '/casos/detalle-entidad',
      PATOLOGOS_POR_ENTIDAD: '/casos/patologos-por-entidad',
    },
  },
  
  // Configuración de reintentos
  RETRY: {
    MAX_ATTEMPTS: 3,
    DELAY: 1000, // ms
  },
  
  // Configuración de caché
  CACHE: {
    ENABLED: true,
    TTL: 5 * 60 * 1000, // 5 minutos
  }
}

// Función para construir URLs completas
export function buildApiUrl(endpoint: string): string {
  return `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}${endpoint}`
}

// Función para obtener headers con autenticación
export function getAuthHeaders(token?: string): Record<string, string> {
  const headers: Record<string, string> = { ...API_CONFIG.DEFAULT_HEADERS }
  
  if (token) {
    headers['Authorization'] = `Bearer ${token}`
  }
  
  return headers
}

/**
 * Estados disponibles para casos
 */
export const CASE_STATES = {
  PENDING: 'En proceso',
  IN_PROCESS: 'En proceso', 
  COMPLETED: 'Completado',
  // DELIVERED antes era 'Por entregar' ahora se mapea a 'Requiere cambios'
  DELIVERED: 'Requiere cambios',
  CANCELLED: 'cancelado',
  TO_SIGN: 'Por firmar'
} as const

/**
 * Tipos de atención disponibles
 */
export const ATTENTION_TYPES = {
  AMBULATORY: 'Ambulatorio',
  HOSPITALIZED: 'Hospitalizado', 
  EMERGENCY: 'Urgencias',
  PRIVATE: 'Particular'
} as const

/**
 * Opciones de sexo disponibles
 */
export const GENDER_OPTIONS = {
  MALE: 'Masculino',
  FEMALE: 'Femenino',
  OTHER: 'Otro'
} as const
