import { apiClient } from '../../../core/config/axios.config'
import { API_CONFIG } from '../../../core/config/api.config'

export interface BackendCase {
  _id?: { $oid?: string } | string
  caso_code?: string
  paciente?: {
    paciente_code?: string
    nombre?: string
    edad?: number
    sexo?: string
    entidad_info?: { codigo?: string; nombre?: string }
    tipo_atencion?: string
    cedula?: string
    observaciones?: string
    fecha_actualizacion?: { $date?: string } | string
  }
  medico_solicitante?: { nombre?: string } | string
  muestras?: Array<{
    region_cuerpo?: string
    pruebas?: Array<{ id?: string; nombre?: string; cantidad?: number }>
  }>
  estado?: string
  servicio?: string
  // Compatibilidad con backend (legacy + actual)
  fecha_creacion?: { $date?: string } | string
  fecha_entrega?: { $date?: string } | string
  fecha_ingreso?: { $date?: string } | string // legacy
  fecha_firma?: { $date?: string } | string | null
  fecha_actualizacion?: { $date?: string } | string
  observaciones_generales?: string
  is_active?: boolean
  actualizado_por?: string
  resultado?: {
    metodo?: string
    resultado_macro?: string
    resultado_micro?: string
    diagnostico?: string
    fecha_resultado?: { $date?: string } | string
  }
  patologo_asignado?: { codigo?: string; nombre?: string }
}

export interface BackendTest {
  pruebaCode: string
  pruebasName: string
  pruebasDescription?: string
  isActive?: boolean
}

const CASES_BASE = API_CONFIG.ENDPOINTS.CASES

export async function listCases(params: Record<string, any> = {}) {
  // Función para obtener TODOS los casos, no solo los primeros 1000
  const allCases: BackendCase[] = []
  let skip = 0
  const limit = 1000 // Máximo permitido por el backend
  
  while (true) {
    const requestParams = {
      skip,
      limit,
      ...params
    }
    
    const data = await apiClient.get<BackendCase[]>(`${CASES_BASE}/`, { params: requestParams })

    if (!data || (data as BackendCase[]).length === 0) {
      break // No hay más casos
    }
    
    allCases.push(...(data as BackendCase[]))
    
    // Si recibimos menos casos que el límite, significa que llegamos al final
    if ((data as BackendCase[]).length < limit) {
      break
    }
    
    skip += limit
  }
  
  return allCases
}

export async function getCaseById(idOrCode: string) {
  // El backend expone detalle por código de caso
  const data = await apiClient.get<BackendCase>(`${CASES_BASE}/caso-code/${encodeURIComponent(idOrCode)}`)
  return data as BackendCase
}

export async function listTests(): Promise<BackendTest[]> {
  const data = await apiClient.get<BackendTest[]>(`${API_CONFIG.ENDPOINTS.TESTS}/`)
  return data as BackendTest[]
}


