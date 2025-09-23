import { apiClient } from '../../../core/config/axios.config'
import { API_CONFIG } from '../../../core/config/api.config'

export interface BackendCase {
  _id?: { $oid?: string } | string
  caso_code?: string
  case_code?: string
  paciente?: {
    paciente_code?: string
    nombre?: string
    edad?: number
    sexo?: string
    entidad_info?: { id?: string; nombre?: string }
    tipo_atencion?: string
    cedula?: string
    observaciones?: string
    fecha_actualizacion?: { $date?: string } | string
  }
  patient_info?: {
    patient_code?: string
    name?: string
    age?: number
    gender?: string
    entity_info?: { id?: string; name?: string }
    care_type?: string
    observations?: string
  }
  medico_solicitante?: { nombre?: string } | string
  requesting_physician?: string
  muestras?: Array<{
    region_cuerpo?: string
    pruebas?: Array<{ id?: string; nombre?: string; cantidad?: number }>
  }>
  samples?: Array<{
    body_region?: string
    tests?: Array<{ id?: string; name?: string; quantity?: number }>
  }>
  estado?: string
  state?: string
  servicio?: string
  service?: string
  priority?: string
  // Compatibilidad con backend (legacy + actual)
  fecha_creacion?: { $date?: string } | string
  created_at?: string
  fecha_entrega?: { $date?: string } | string
  fecha_ingreso?: { $date?: string } | string // legacy
  fecha_firma?: { $date?: string } | string | null
  fecha_actualizacion?: { $date?: string } | string
  updated_at?: string
  observaciones_generales?: string
  observations?: string
  notas_adicionales?: Array<{
    fecha: string
    nota: string
    agregado_por?: string
  }>
  additional_notes?: Array<{
    date: string
    note: string
  }>
  complementary_tests?: Array<{
    code?: string
    name?: string
    quantity?: number
    reason?: string
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
  result?: {
    method?: string[] | string
    macro_result?: string
    micro_result?: string
    diagnosis?: string
    updated_at?: { $date?: string } | string
    cie10_diagnosis?: { code?: string; name?: string } | null
    cieo_diagnosis?: { code?: string; name?: string } | null
    observations?: string
  }
  patologo_asignado?: { codigo?: string; nombre?: string; firma?: string }
  assigned_pathologist?: { id?: string; name?: string }
  delivered_to?: string
  delivered_at?: { $date?: string } | string
  business_days?: number
}

export interface BackendTest {
  pruebaCode: string
  pruebasName: string
  pruebasDescription?: string
  isActive?: boolean
}

const CASES_BASE = `${API_CONFIG.BASE_URL}${API_CONFIG.VERSION}/cases`

export async function listCases(params: Record<string, any> = {}) {
  // Usar los parámetros directamente ya que vienen con los nombres correctos del backend
  const data = await apiClient.get<BackendCase[]>(`${CASES_BASE}/`, { params })
  const arr = (data as BackendCase[]) || []
  return arr.sort((a, b) => String(b.caso_code || b.case_code || '').localeCompare(String(a.caso_code || a.case_code || '')))
}

export async function listAllCases(params: Record<string, any> = {}) {
  // Traer TODOS los casos aplicando filtros, paginando en lotes de 1000 hasta agotar
  const all: BackendCase[] = []
  let skip = 0
  const limit = 1000
  while (true) {
    const batchParams = { 
      skip, 
      limit, 
      search: params.query,
      pathologist: params.patologo_nombre,
      entity: params.entidad_nombre,
      state: params.estado,
      test: params.prueba,
      date_from: params.fecha_ingreso_desde,
      date_to: params.fecha_ingreso_hasta
    }
    const data = await apiClient.get<BackendCase[]>(`${CASES_BASE}/`, { params: batchParams })
    const arr = (data as BackendCase[]) || []
    if (arr.length === 0) break
    all.push(...arr)
    if (arr.length < limit) break
    skip += limit
  }
  // Ordenar por caso_code desc si no lo garantiza el backend
  return all.sort((a, b) => String(b.caso_code || b.case_code || '').localeCompare(String(a.caso_code || a.case_code || '')))
}

export async function searchCases(params: Record<string, any> = {}) {
  // Usar el mismo endpoint de listado con filtros
  return await listCases(params)
}

export async function getCaseById(idOrCode: string) {
  // El nuevo backend expone detalle por código de caso
  const data = await apiClient.get<BackendCase>(`${CASES_BASE}/${encodeURIComponent(idOrCode)}`)
  return data as BackendCase
}

export async function listTests(): Promise<BackendTest[]> {
  const data = await apiClient.get<BackendTest[]>(`${API_CONFIG.ENDPOINTS.TESTS}/`)
  return data as BackendTest[]
}