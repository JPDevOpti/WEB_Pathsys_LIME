import { computed, onMounted, ref, watch } from 'vue'
import type { Patient, PatientFilters, PatientSortKey, SortOrder, PatientCase, IdentificationType } from '../types/patient.types'
import { 
  listPatients, 
  searchPatientsAdvanced,
  getPatientByCode,
  getPatientCases,
  type BackendPatient
} from '../services/patientListApi'
import { calculateAge } from '../utils/dateUtils'

/**
 * Normaliza texto para búsquedas (elimina acentos y convierte a minúsculas)
 */
const normalize = (text: string): string => 
  (text || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim()

/**
 * Transforma un paciente del backend al formato del frontend
 */
const transformBackendPatient = (bk: BackendPatient): Patient => {
  // Obtener ID
  const id = typeof bk._id === 'string' ? bk._id : (bk._id as any)?.$oid || bk.id || bk.patient_code
  
  // Construir nombre completo
  const fullName = [
    bk.first_name,
    bk.second_name,
    bk.first_lastname,
    bk.second_lastname
  ].filter(Boolean).join(' ').trim()
  
  // Calcular edad
  const age = calculateAge(bk.birth_date)
  
  return {
    id,
    patient_code: bk.patient_code,
    identification_type: bk.identification_type as IdentificationType,
    identification_number: bk.identification_number,
    first_name: bk.first_name,
    second_name: bk.second_name,
    first_lastname: bk.first_lastname,
    second_lastname: bk.second_lastname,
    birth_date: bk.birth_date,
    gender: bk.gender,
    location: {
      municipality_code: bk.location.municipality_code,
      municipality_name: bk.location.municipality_name,
      subregion: bk.location.subregion,
      address: bk.location.address
    },
    entity_info: {
      id: bk.entity_info.id,
      name: bk.entity_info.name
    },
    care_type: bk.care_type,
    observations: bk.observations,
    created_at: bk.created_at,
    updated_at: bk.updated_at,
    
    // Propiedades computadas
    full_name: fullName,
    age: age
  }
}

export function usePatientList() {
  // Estado
  const patients = ref<Patient[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  // Filtros (inicializados vacíos)
  const filters = ref<PatientFilters>({
    search: '',
    entity: '',
    gender: undefined,
    care_type: undefined,
    date_from: '',
    date_to: '',
    skip: 0,
    limit: 100
  })

  // Ordenamiento y paginación
  const sortKey = ref<PatientSortKey>('created_at')
  const sortOrder = ref<SortOrder>('desc')
  const currentPage = ref(1)
  const itemsPerPage = ref(10)
  
  // Selección
  const selectedPatientIds = ref<string[]>([])
  const selectedPatient = ref<Patient | null>(null)
  const selectedPatientCases = ref<PatientCase[]>([])

  /**
   * Carga pacientes desde el backend
   * Si hasFilters es true, usa búsqueda avanzada, sino listado simple
   */
  const loadPatients = async (forceAdvancedSearch: boolean = false) => {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null
    
    try {
      // Determinar si hay filtros aplicados
      const hasFilters = !!(
        filters.value.search ||
        filters.value.identification_type ||
        filters.value.identification_number ||
        filters.value.first_name ||
        filters.value.first_lastname ||
        filters.value.birth_date_from ||
        filters.value.birth_date_to ||
        filters.value.municipality_code ||
        filters.value.municipality_name ||
        filters.value.subregion ||
        filters.value.age_min ||
        filters.value.age_max ||
        filters.value.entity ||
        filters.value.gender ||
        filters.value.care_type ||
        filters.value.date_from ||
        filters.value.date_to
      )

      let data: BackendPatient[] = []
      let total = 0

      if (forceAdvancedSearch || hasFilters) {
        const result = await searchPatientsAdvanced(filters.value)
        data = result.patients
        total = result.total
      } else {
        data = await listPatients(filters.value)
        total = data.length
      }

      // Transformar datos
      patients.value = data.map(transformBackendPatient)
      totalCount.value = total
    } catch (e: any) {
      console.error('Error al cargar pacientes:', e)
      error.value = e.message || 'Error al cargar los pacientes'
      patients.value = []
      totalCount.value = 0
    } finally {
      isLoading.value = false
    }
  }

  /**
   * Pacientes ordenados (sorting client-side)
   */
  const sortedPatients = computed(() => {
    const list = [...patients.value]
    
    list.sort((a, b) => {
      let aVal: any = a[sortKey.value]
      let bVal: any = b[sortKey.value]
      
      // Manejo especial para fechas
      if (sortKey.value === 'created_at' || sortKey.value === 'updated_at' || sortKey.value === 'birth_date') {
        aVal = aVal ? new Date(aVal).getTime() : 0
        bVal = bVal ? new Date(bVal).getTime() : 0
      }
      
      // Manejo especial para números
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
      }
      
      // Manejo especial para strings
      if (typeof aVal === 'string' && typeof bVal === 'string') {
        aVal = normalize(aVal)
        bVal = normalize(bVal)
      }
      
      if (aVal < bVal) return sortOrder.value === 'asc' ? -1 : 1
      if (aVal > bVal) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })
    
    return list
  })

  /**
   * Paginación client-side
   */
  const paginatedPatients = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return sortedPatients.value.slice(start, end)
  })

  const totalPages = computed(() => {
    return Math.ceil(sortedPatients.value.length / itemsPerPage.value)
  })

  const isAllSelected = computed(() => {
    return paginatedPatients.value.length > 0 && 
           paginatedPatients.value.every(patient => selectedPatientIds.value.includes(patient.id))
  })

  /**
   * Acciones de selección
   */
  const toggleSelectAll = () => {
    if (isAllSelected.value) {
      selectedPatientIds.value = selectedPatientIds.value.filter(id => 
        !paginatedPatients.value.some(patient => patient.id === id)
      )
    } else {
      const newIds = paginatedPatients.value.map(patient => patient.id)
      selectedPatientIds.value = [...new Set([...selectedPatientIds.value, ...newIds])]
    }
  }

  const toggleSelect = (patientId: string) => {
    const index = selectedPatientIds.value.indexOf(patientId)
    if (index > -1) {
      selectedPatientIds.value.splice(index, 1)
    } else {
      selectedPatientIds.value.push(patientId)
    }
  }

  /**
   * Ordenamiento
   */
  const sortBy = (key: string) => {
    // Cast string to PatientSortKey - validate it's a valid key
    const validKeys: PatientSortKey[] = [
      'patient_code',
      'identification_number', 
      'first_name',
      'first_lastname',
      'birth_date',
      'gender',
      'care_type',
      'created_at',
      'updated_at'
    ]
    
    if (!validKeys.includes(key as PatientSortKey)) {
      console.warn(`Invalid sort key: ${key}`)
      return
    }
    
    const typedKey = key as PatientSortKey
    
    if (sortKey.value === typedKey) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = typedKey
      sortOrder.value = 'asc'
    }
  }

  /**
   * Mostrar detalles de un paciente
   */
  const showDetails = async (patient: Patient) => {
    selectedPatient.value = patient
    
    try {
      const cases = await getPatientCases(patient.patient_code)
      selectedPatientCases.value = cases.map((c: any) => ({
        id: c.id || c._id,
        caseCode: c.case_code || c.caso_code,
        sampleType: c.sample_type || c.tipo_muestra || '',
        status: c.status || c.estado || '',
        receivedAt: c.received_at || c.fecha_creacion || '',
        deliveredAt: c.delivered_at || c.fecha_entrega || '',
        signedAt: c.signed_at || c.fecha_firma || '',
        tests: c.tests || [],
        pathologist: c.pathologist || c.patologo || '',
        requester: c.requester || c.medico_solicitante || '',
        entity: c.entity || c.entidad || '',
        priority: c.priority || c.prioridad || 'Normal'
      }))
    } catch (e) {
      console.error('Error al cargar casos:', e)
      selectedPatientCases.value = []
    }
  }

  const closeDetails = () => {
    selectedPatient.value = null
    selectedPatientCases.value = []
  }

  /**
   * Watchers
   */
  watch(currentPage, () => {
    // Al cambiar de página, scroll arriba
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })

  /**
   * Auto-cargar al montar
   */
  onMounted(() => {
    loadPatients()
  })

  return {
    // Estado
    patients,
    isLoading,
    error,
    totalCount,
    filters,
    sortKey,
    sortOrder,
    currentPage,
    itemsPerPage,
    selectedPatientIds,
    selectedPatient,
    selectedPatientCases,
    
    // Computed
    sortedPatients,
    paginatedPatients,
    totalPages,
    isAllSelected,
    
    // Acciones
    loadPatients,
    toggleSelectAll,
    toggleSelect,
    sortBy,
    showDetails,
    closeDetails
  }
}
