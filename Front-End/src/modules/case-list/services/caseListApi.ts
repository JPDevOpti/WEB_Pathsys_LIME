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
    entidad_info?: { id?: string; nombre?: string } // Corrección: id en lugar de codigo
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
  notas_adicionales?: Array<{
    fecha: string
    nota: string
    agregado_por?: string
  }>
  is_active?: boolean
  actualizado_por?: string
  resultado?: {
    metodo?: string[] | string // Array de strings según nuevo modelo backend
    resultado_macro?: string
    resultado_micro?: string
    diagnostico?: string
    fecha_resultado?: { $date?: string } | string
    diagnostico_cie10?: { codigo?: string; nombre?: string } | null
    diagnostico_cieo?: { codigo?: string; nombre?: string } | null
    observaciones?: string
  }
  patologo_asignado?: { codigo?: string; nombre?: string; firma?: string }
}

export interface BackendTest {
  pruebaCode: string
  pruebasName: string
  pruebasDescription?: string
  isActive?: boolean
}

const CASES_BASE = API_CONFIG.ENDPOINTS.CASES

export async function listCases(params: Record<string, any> = {}) {
  // Por defecto: traer 100 y ordenar por código desc en cliente (últimos 100)
  const baseParams = { skip: 0, limit: 100 }
  const requestParams = { ...baseParams, ...params }
  const data = await apiClient.get<BackendCase[]>(`${CASES_BASE}/`, { params: requestParams })
  const arr = (data as BackendCase[]) || []
  return arr.sort((a, b) => String(b.caso_code || '').localeCompare(String(a.caso_code || '')))
}

export async function listAllCases(params: Record<string, any> = {}) {
  // Traer TODOS los casos aplicando filtros, paginando en lotes de 1000 hasta agotar
  const all: BackendCase[] = []
  let skip = 0
  const limit = 1000
  while (true) {
    const batchParams = { skip, limit, ...params }
    const data = await apiClient.get<BackendCase[]>(`${CASES_BASE}/`, { params: batchParams })
    const arr = (data as BackendCase[]) || []
    if (arr.length === 0) break
    all.push(...arr)
    if (arr.length < limit) break
    skip += limit
  }
  // Ordenar por caso_code desc si no lo garantiza el backend
  return all.sort((a, b) => String(b.caso_code || '').localeCompare(String(a.caso_code || '')))
}

export async function searchCases(params: Record<string, any> = {}) {
  // Buscar en backend con filtros y traer TODOS los resultados (hasta agotar) usando skip/limit
  const all: BackendCase[] = []
  let skip = 0
  const limit = 1000
  while (true) {
    const batchParams = { skip, limit, ...params }
    const data = await apiClient.post<BackendCase[]>(`${CASES_BASE}/buscar`, batchParams, { params: { skip, limit, sort_field: 'caso_code', sort_direction: -1 } })
    const arr = (data as BackendCase[]) || []
    if (arr.length === 0) break
    all.push(...arr)
    if (arr.length < limit) break
    skip += limit
  }
  return all
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


