import { computed, onMounted, ref, watch } from 'vue'
import type { Patient, PatientFilters, PatientSortKey, SortOrder, PatientCase, IdentificationType } from '../types/patient.types'
import { 
  searchPatients,
  getPatientCases,
  type BackendPatient
} from '../services/patientListApi'
import { calculateAge } from '../utils/dateUtils'

const normalize = (text: string): string => 
  (text || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim()

const transformBackendPatient = (bk: BackendPatient): Patient => {
  const id = typeof bk._id === 'string' ? bk._id : (bk._id as any)?.$oid || bk.id || bk.patient_code
  
  const fullName = [
    bk.first_name,
    bk.second_name,
    bk.first_lastname,
    bk.second_lastname
  ].filter(Boolean).join(' ').trim()
  
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
    location: bk.location ? {
      municipality_code: bk.location.municipality_code,
      municipality_name: bk.location.municipality_name,
      subregion: bk.location.subregion,
      address: bk.location.address
    } : {
      municipality_code: '',
      municipality_name: '',
      subregion: '',
      address: ''
    },
    entity_info: {
      id: bk.entity_info.id,
      name: bk.entity_info.name
    },
    care_type: bk.care_type,
    observations: bk.observations,
    created_at: bk.created_at,
    updated_at: bk.updated_at,
    full_name: fullName,
    age: age
  }
}

export function usePatientList() {
  const patients = ref<Patient[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)
  const totalCount = ref(0)

  const filters = ref<PatientFilters>({
    search: undefined,
    entity: undefined,
    gender: undefined,
    care_type: undefined,
    municipality_code: undefined,
    municipality_name: undefined,
    subregion: undefined,
    date_from: undefined,
    date_to: undefined,
    skip: 0,
    limit: 100
  })

  const sortKey = ref<PatientSortKey>('created_at')
  const sortOrder = ref<SortOrder>('desc')
  const currentPage = ref(1)
  const itemsPerPage = ref(10)
  
  const selectedPatientIds = ref<string[]>([])
  const selectedPatient = ref<Patient | null>(null)
  const selectedPatientCases = ref<PatientCase[]>([])

  const loadPatients = async () => {
    if (isLoading.value) return

    isLoading.value = true
    error.value = null
    
    try {
      const result = await searchPatients(filters.value)
      patients.value = result.patients.map(transformBackendPatient)
      totalCount.value = result.total
    } catch (e: any) {
      error.value = e.message || 'Error al cargar los pacientes'
      patients.value = []
      totalCount.value = 0
    } finally {
      isLoading.value = false
    }
  }

  const sortedPatients = computed(() => {
    const list = [...patients.value]
    
    list.sort((a, b) => {
      let aVal: any = a[sortKey.value]
      let bVal: any = b[sortKey.value]
      
      if (sortKey.value === 'created_at' || sortKey.value === 'updated_at' || sortKey.value === 'birth_date') {
        aVal = aVal ? new Date(aVal).getTime() : 0
        bVal = bVal ? new Date(bVal).getTime() : 0
      }
      
      if (typeof aVal === 'number' && typeof bVal === 'number') {
        return sortOrder.value === 'asc' ? aVal - bVal : bVal - aVal
      }
      
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

  const sortBy = (key: string) => {
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

  const showDetails = async (patient: Patient) => {
    selectedPatient.value = patient
    
    try {
      const cases = await getPatientCases(patient.patient_code)
      selectedPatientCases.value = cases.map((c: any) => ({
        _id: c._id,
        id: c.id || c._id,
        case_code: c.case_code,
        state: c.state,
        priority: c.priority,
        assigned_pathologist: c.assigned_pathologist,
        created_at: c.created_at,
        updated_at: c.updated_at,
        caseCode: c.case_code || c.caso_code,
        sampleType: c.sample_type || c.tipo_muestra || '',
        status: c.status || c.estado || c.state || '',
        receivedAt: c.received_at || c.fecha_creacion || c.created_at || '',
        deliveredAt: c.delivered_at || c.fecha_entrega || '',
        signedAt: c.signed_at || c.fecha_firma || '',
        tests: c.tests || [],
        pathologist: c.pathologist || c.patologo || c.assigned_pathologist?.name || '',
        requester: c.requester || c.medico_solicitante || '',
        entity: c.entity || c.entidad || ''
      }))
    } catch (e: any) {
      error.value = e?.message || 'Error al cargar los casos del paciente'
      selectedPatientCases.value = []
    }
  }

  const closeDetails = () => {
    selectedPatient.value = null
    selectedPatientCases.value = []
  }

  watch(currentPage, () => {
    window.scrollTo({ top: 0, behavior: 'smooth' })
  })

  onMounted(() => {
    loadPatients()
  })

  return {
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
    sortedPatients,
    paginatedPatients,
    totalPages,
    isAllSelected,
    loadPatients,
    toggleSelectAll,
    toggleSelect,
    sortBy,
    showDetails,
    closeDetails
  }
}
