import { computed, onMounted, ref, watch, onUnmounted } from 'vue'
import type { Case, Filters, SortKey, SortOrder } from '../types/case.types'
import { listCases, searchCases, listTests, type BackendCase, type BackendTest } from '../services/caseListApi'
import { getDefaultDateRange } from '../utils/dateUtils'
import { useCasesStore } from '@/stores/cases.store'

const normalize = (text: string): string => (text || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim()

const toYYYYMMDD = (dateStr: string): string => {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toISOString().split('T')[0]
}

const ddmmyyyyToISO = (dateStr: string): string => {
  if (!dateStr) return ''
  const [dd, mm, yyyy] = dateStr.split('/');
  if (!dd || !mm || !yyyy) return ''
  return `${yyyy}-${mm.padStart(2, '0')}-${dd.padStart(2, '0')}`
}

export function useCaseList() {
  const cases = ref<Case[]>([])
  const isLoading = ref(false)
  const error = ref<string | null>(null)

  const defaultDates = getDefaultDateRange()
  const casesStore = useCasesStore()
  
  const filters = ref<Filters>({
    searchQuery: '',
    searchPathologist: '',
    dateFrom: defaultDates.dateFrom,
    dateTo: defaultDates.dateTo,
    selectedEntity: '',
    selectedStatus: '',
    selectedTest: ''
  })

  const sortKey = ref<SortKey>('caseCode')
  const sortOrder = ref<SortOrder>('desc')
  const currentPage = ref(1)
  const itemsPerPage = ref(10)
  const selectedCaseIds = ref<string[]>([])
  const selectedCase = ref<Case | null>(null)

  const loadCases = async (fullSearch: boolean = false) => {
    isLoading.value = true
    error.value = null
    try {
      const testsCatalog = new Map<string, string>()
      try {
        const tests: BackendTest[] = await listTests()
        tests.forEach(t => {
          if (t.isActive !== false) testsCatalog.set(t.pruebaCode, t.pruebasName)
        })
      } catch (e) {
      }

      const serverParams: Record<string, any> = { skip: 0 }
      serverParams.limit = fullSearch ? 100000 : 100
      
      if (filters.value.searchQuery) serverParams.search = filters.value.searchQuery
      if (filters.value.searchPathologist) serverParams.pathologist = filters.value.searchPathologist
      if (filters.value.selectedEntity) serverParams.entity = filters.value.selectedEntity
      if (filters.value.selectedStatus) serverParams.state = filters.value.selectedStatus
      if (filters.value.selectedTest) serverParams.test = filters.value.selectedTest
      if (filters.value.dateFrom) serverParams.date_from = ddmmyyyyToISO(filters.value.dateFrom)
      if (filters.value.dateTo) serverParams.date_to = ddmmyyyyToISO(filters.value.dateTo)

      const data: BackendCase[] = fullSearch ? await searchCases(serverParams) : await listCases(serverParams)
      cases.value = data.map((bk) => transformBackendCase(bk, testsCatalog))
    } catch (e: any) {
      error.value = 'Error al cargar los casos'
      cases.value = []
    } finally {
      isLoading.value = false
    }
  }

  const transformBackendCase = (bk: BackendCase, testsCatalog: Map<string, string>): Case => {
    const getDate = (v: any): string => {
      if (!v) return ''
      if (typeof v === 'string') return v
      if (v?.$date) return v.$date
      return ''
    }
    
    const id = (typeof bk._id === 'string' ? bk._id : (bk._id as any)?.$oid) || bk.case_code || bk.caso_code || `case-${Math.random().toString(36).substr(2, 9)}`
    const receivedAt = getDate(bk.created_at || bk.fecha_creacion)
    const deliveredAt = getDate(bk.updated_at || bk.fecha_entrega)
    const signedAt = getDate(bk.fecha_firma)

    const flatTests: string[] = []
    const subsamples: Case['subsamples'] = []
    
    const samples: any[] = (bk.samples as any) || (bk.muestras as any) || []
    if (Array.isArray(samples)) {
      samples.forEach((m: any) => {
        const items: { id: string; name: string; quantity: number }[] = []
        const tests: any[] = (m.tests as any) || (m.pruebas as any) || []
        tests.forEach((p: any) => {
          const code = p.id || ''
          const name = p.name || p.nombre || testsCatalog.get(code) || ''
          const cantidad = p.quantity || p.cantidad || 1
          
          if (code) {
            const testString = name ? `${code} - ${name}` : code
            for (let i = 0; i < cantidad; i++) {
              flatTests.push(testString)
            }
          }
          
          items.push({ id: code, name: name || code, quantity: cantidad })
        })
        subsamples.push({ 
          bodyRegion: m.body_region || m.region_cuerpo || '', 
          tests: items 
        })
      })
    }

    const mapStatus = (s?: string): string => {
      const v = String(s || '').toLowerCase()
      if (v.includes('firmar')) return 'Por firmar'
      if (v.includes('entregar')) return 'Por entregar'
      if (v.includes('complet')) return 'Completado'
      if (v.includes('cambio')) return 'Por entregar'
      if (v.includes('pend') || !v) return 'En proceso'
      return s || 'En proceso'
    }

    const finalStatus = mapStatus(bk.state || bk.estado)
    const finalDeliveredAt = finalStatus === 'Por entregar' ? '' : deliveredAt

    const patientInfo: any = (bk.patient_info as any) || (bk.paciente as any) || {}
    const caseCode = bk.case_code || bk.caso_code || id
    const sampleType = (samples[0]?.body_region || samples[0]?.region_cuerpo || (patientInfo?.care_type || patientInfo?.tipo_atencion || ''))
    
    return {
      id,
      caseCode,
      sampleType,
      patient: {
        id: patientInfo?.patient_code || patientInfo?.paciente_code || '',
        dni: patientInfo?.patient_code || patientInfo?.paciente_code || patientInfo?.cedula || '',
        fullName: patientInfo?.name || patientInfo?.nombre || '',
        sex: patientInfo?.gender || patientInfo?.sexo || '',
        age: Number(patientInfo?.age || patientInfo?.edad || 0),
        entity: patientInfo?.entity_info?.name || patientInfo?.entidad_info?.nombre || '',
        attentionType: patientInfo?.care_type || patientInfo?.tipo_atencion || '',
        notes: patientInfo?.observations || patientInfo?.observaciones || '',
        createdAt: getDate(bk.created_at || bk.fecha_creacion),
        updatedAt: getDate(bk.updated_at || bk.fecha_actualizacion),
      },
      entity: patientInfo?.entity_info?.name || patientInfo?.entidad_info?.nombre || '',
      requester: bk.requesting_physician || (typeof bk.medico_solicitante === 'string' ? bk.medico_solicitante : (bk.medico_solicitante?.nombre || '')),
      status: finalStatus,
      receivedAt,
      deliveredAt: finalDeliveredAt,
      signedAt,
      tests: flatTests,
      pathologist: bk.assigned_pathologist?.name || bk.patologo_asignado?.nombre || '',
      patologo_asignado: bk.assigned_pathologist ? {
        codigo: bk.assigned_pathologist.id || '',
        nombre: bk.assigned_pathologist.name || '',
        firma: undefined
      } : (bk.patologo_asignado ? {
        codigo: bk.patologo_asignado.codigo || '',
        nombre: bk.patologo_asignado.nombre || '',
        firma: bk.patologo_asignado.firma
      } : undefined),
      notes: bk.observations || bk.observaciones_generales || '',
      servicio: bk.service || bk.servicio || '',
      // @ts-ignore
      priority: bk.priority || (bk as any).prioridad || (bk as any).prioridad_caso || 'Normal',
      // @ts-ignore
      business_days: bk.business_days || undefined,
      // @ts-ignore
      delivered_to: bk.delivered_to || undefined,
      // @ts-ignore
      delivered_at: getDate(bk.delivered_at),
      result: {
        method: Array.isArray(bk.result?.method) ? bk.result.method : (bk.result?.method ? [bk.result.method] : []) as string[],
        macro_result: bk.result?.macro_result || '',
        micro_result: bk.result?.micro_result || '',
        diagnosis: bk.result?.diagnosis || '',
        resultDate: getDate(bk.result?.updated_at),
        cie10_diagnosis: (bk.result?.cie10_diagnosis?.code && bk.result?.cie10_diagnosis?.name) ? { code: bk.result.cie10_diagnosis.code, name: bk.result.cie10_diagnosis.name } : null,
        cieo_diagnosis: (bk.result?.cieo_diagnosis?.code && bk.result?.cieo_diagnosis?.name) ? { code: bk.result.cieo_diagnosis.code, name: bk.result.cieo_diagnosis.name } : null,
        observations: bk.result?.observations || '',
      },
      subsamples,
      additional_notes: bk.additional_notes || [],
      complementary_tests: bk.complementary_tests || [],
    }
  }

  const filteredCases = computed(() => {
    let list = cases.value

    if (filters.value.searchQuery) {
      const q = normalize(filters.value.searchQuery)
      list = list.filter(c => normalize(c.id).includes(q) || normalize(c.caseCode || '').includes(q) || normalize(c.patient.dni).includes(q) || normalize(c.patient.fullName).includes(q))
    }

    if (filters.value.searchPathologist) {
      const q = normalize(filters.value.searchPathologist)
      list = list.filter(c => normalize(c.pathologist || '').includes(q))
    }

    if (filters.value.dateFrom) {
      const from = ddmmyyyyToISO(filters.value.dateFrom)
      list = list.filter(c => !!c.receivedAt && toYYYYMMDD(c.receivedAt) >= from)
    }
    if (filters.value.dateTo) {
      const to = ddmmyyyyToISO(filters.value.dateTo)
      list = list.filter(c => !!c.receivedAt && toYYYYMMDD(c.receivedAt) <= to)
    }

    if (filters.value.selectedEntity) {
      const q = normalize(filters.value.selectedEntity)
      list = list.filter(c => normalize(c.entity).includes(q))
    }

    if (filters.value.selectedStatus) {
      const q = normalize(filters.value.selectedStatus)
      list = list.filter(c => normalize(c.status).includes(q))
    }

    if (filters.value.selectedTest) {
      const q = normalize(filters.value.selectedTest)
      list = list.filter(c => c.tests.some(t => normalize(t).includes(q)))
    }

    list = [...list].sort((a, b) => {
      let aValue: string | Date = (a as any)[sortKey.value]
      let bValue: string | Date = (b as any)[sortKey.value]
      if (sortKey.value === 'receivedAt' || sortKey.value === 'deliveredAt') {
        aValue = new Date(aValue as string)
        bValue = new Date(bValue as string)
      }
      if (aValue < (bValue as any)) return sortOrder.value === 'asc' ? -1 : 1
      if (aValue > (bValue as any)) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })

    return list
  })

  const totalPages = computed(() => Math.ceil(filteredCases.value.length / itemsPerPage.value) || 1)
  const paginatedCases = computed(() => {
    const start = (currentPage.value - 1) * itemsPerPage.value
    const end = start + itemsPerPage.value
    return filteredCases.value.slice(start, end)
  })

  const isAllSelected = computed(() => {
    if (paginatedCases.value.length === 0) return false
    return paginatedCases.value.every(c => selectedCaseIds.value.includes(c.id))
  })

  const toggleSelectAll = () => {
    if (isAllSelected.value) {
      selectedCaseIds.value = selectedCaseIds.value.filter(id => !paginatedCases.value.some(c => c.id === id))
    } else {
      const newSelected = paginatedCases.value.map(c => c.id)
      selectedCaseIds.value = [...new Set([...selectedCaseIds.value, ...newSelected])]
    }
  }

  const toggleSelect = (id: string) => {
    if (!id || id.trim() === '') return
    const index = selectedCaseIds.value.indexOf(id)
    if (index === -1) {
      selectedCaseIds.value.push(id)
    } else {
      selectedCaseIds.value.splice(index, 1)
    }
  }

  const sortBy = (key: SortKey) => {
    if (sortKey.value === key) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = key
      sortOrder.value = 'asc'
    }
  }

  const applyBulkAction = (action: string, ids: string[]) => {
    cases.value = cases.value.map(c => {
      if (ids.includes(c.id)) {
        let newStatus = action
        if (action === 'en-proceso') newStatus = 'En proceso'
        if (action === 'por-firmar') newStatus = 'Por firmar'
        if (action === 'por-entregar') newStatus = 'Por entregar'
        if (action === 'completado') newStatus = 'Completado'
        if (action === 'requiere-cambios') newStatus = 'Por entregar'
        return { ...c, status: newStatus }
      }
      return c
    })
    selectedCaseIds.value = []
  }

  const showDetails = (c: Case) => {
    selectedCase.value = c
  }

  const closeDetails = () => {
    selectedCase.value = null
  }

  const validateCase = (c: Case) => {
    const idx = cases.value.findIndex(x => x.id === c.id)
    if (idx !== -1) cases.value[idx].status = 'Validado'
    if (selectedCase.value?.id === c.id) selectedCase.value.status = 'Validado'
  }

  const markAsCompleted = (c: Case) => {
    const idx = cases.value.findIndex(x => x.id === c.id)
    if (idx !== -1 && cases.value[idx].status === 'Por firmar') cases.value[idx].status = 'Completado'
    if (selectedCase.value?.id === c.id && selectedCase.value.status === 'Por firmar') selectedCase.value.status = 'Completado'
  }

  const clearFilters = () => {
    const defaultDates = getDefaultDateRange()
    filters.value = {
      searchQuery: '',
      searchPathologist: '',
      dateFrom: defaultDates.dateFrom,
      dateTo: defaultDates.dateTo,
      selectedEntity: '',
      selectedStatus: '',
      selectedTest: ''
    }
  }

  watch(filters, () => { currentPage.value = 1 }, { deep: true })
  watch(itemsPerPage, () => { currentPage.value = 1 })
  
  const handleCaseCreated = (_event: CustomEvent) => {
    loadCases()
  }
  
  watch(() => casesStore.needsRefresh, (needsRefresh) => {
    if (needsRefresh) {
      loadCases().then(() => {
        casesStore.markRefreshed()
      })
    }
  })
  
  watch(() => casesStore.lastUpdate, () => {
    loadCases()
  })
  
  onMounted(() => {
    loadCases()
    window.addEventListener('case-created', handleCaseCreated as EventListener)
  })
  
  onUnmounted(() => {
    window.removeEventListener('case-created', handleCaseCreated as EventListener)
  })

  return {
    cases,
    isLoading,
    error,
    filters,
    sortKey,
    sortOrder,
    currentPage,
    itemsPerPage,
    selectedCaseIds,
    selectedCase,
    filteredCases,
    paginatedCases,
    totalPages,
    isAllSelected,
    loadCases,
    toggleSelectAll,
    toggleSelect,
    sortBy,
    applyBulkAction,
    showDetails,
    closeDetails,
    validateCase,
    markAsCompleted,
    clearFilters,
    toYYYYMMDD,
    ddmmyyyyToISO,
    getDefaultDateRange,
  }
}


