import { computed, onMounted, ref, watch, onUnmounted } from 'vue'
import type { Case, Filters, SortKey, SortOrder } from '../types/case.types'
import { listCases, listTests, type BackendCase, type BackendTest } from '../services/caseListApi'
import { getDefaultDateRange } from '../utils/dateUtils'
import { useCasesStore } from '@/stores/cases.store'

function normalize(text: string): string {
  return (text || '').normalize('NFD').replace(/\p{Diacritic}/gu, '').toLowerCase().trim()
}

function toYYYYMMDD(dateStr: string): string {
  if (!dateStr) return ''
  const d = new Date(dateStr)
  return d.toISOString().split('T')[0]
}

function ddmmyyyyToISO(dateStr: string): string {
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
  
  // Store para sincronización
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

  async function loadCases() {
    isLoading.value = true
    error.value = null
    try {
      // cargar catálogo de pruebas para mapear nombres
      const testsCatalog = new Map<string, string>()
      try {
        const tests: BackendTest[] = await listTests()
        tests.forEach(t => {
          if (t.isActive !== false) testsCatalog.set(t.pruebaCode, t.pruebasName)
        })
      } catch (e) {
        // continuar sin catálogo
      }

      const data: BackendCase[] = await listCases()
      cases.value = data.map((bk) => transformBackendCase(bk, testsCatalog))
    } catch (e: any) {
      error.value = 'Error al cargar los casos'
      cases.value = []
    } finally {
      isLoading.value = false
    }
  }

  function transformBackendCase(bk: BackendCase, testsCatalog: Map<string, string>): Case {
    const getDate = (v: any): string => {
      if (!v) return ''
      if (typeof v === 'string') return v
      if (v?.$date) return v.$date
      return ''
    }
    
    const id = typeof bk._id === 'string' ? bk._id : 
               (bk._id as any)?.$oid || 
               bk.caso_code || 
               `case-${Math.random().toString(36).substr(2, 9)}`
    const receivedAt = getDate(bk.fecha_creacion)
    const deliveredAt = getDate(bk.fecha_entrega)  // Fecha de entrega real
    const signedAt = getDate(bk.fecha_firma)       // Fecha de firma específica

    // aplanar pruebas como "code - name" expandidas por cantidad
    const flatTests: string[] = []
    const subsamples: Case['subsamples'] = []
    if (Array.isArray(bk.muestras)) {
      bk.muestras.forEach((m) => {
        const items: { id: string; name: string; quantity: number }[] = []
        m.pruebas?.forEach((p) => {
          const code = p.id || ''
          const name = p.nombre || testsCatalog.get(code) || ''
          const cantidad = p.cantidad || 1
          
          // Expandir según cantidad para flatTests (para el agrupamiento en tabla)
          if (code) {
            const testString = name ? `${code} - ${name}` : code
            for (let i = 0; i < cantidad; i++) {
              flatTests.push(testString)
            }
          }
          
          // Para subsamples mantener la estructura con cantidad
          items.push({ id: code, name: name || code, quantity: cantidad })
        })
        subsamples.push({ bodyRegion: m.region_cuerpo || '', tests: items })
      })
    }

    const mapStatus = (s?: string): string => {
      const v = String(s || '').toLowerCase()
      if (v.includes('firmar')) return 'Por firmar'
      if (v.includes('entregar')) return 'Por entregar'
      if (v.includes('complet')) return 'Completado'
      if (v.includes('cambio')) return 'Por entregar' // Reemplazar "Requiere cambios" por "Por entregar"
      if (v.includes('pend') || !v) return 'En proceso'
      return s || 'En proceso'
    }

    const finalStatus = mapStatus(bk.estado)
    const finalDeliveredAt = finalStatus === 'Por entregar' ? '' : deliveredAt

    return {
      id,
      caseCode: bk.caso_code || id,
      sampleType: bk.muestras?.[0]?.region_cuerpo || (bk.paciente?.tipo_atencion || ''),
      patient: {
        // El backend actual usa paciente_code como identificador principal del paciente
        id: bk.paciente?.paciente_code || '',
        // Mostrar el código del paciente (antes cedula) en la columna de documento
        dni: bk.paciente?.paciente_code || bk.paciente?.cedula || '',
        fullName: bk.paciente?.nombre || '',
        sex: bk.paciente?.sexo || '',
        age: Number(bk.paciente?.edad || 0),
        entity: bk.paciente?.entidad_info?.nombre || '',
        attentionType: bk.paciente?.tipo_atencion || '',
        notes: bk.paciente?.observaciones || '',
        createdAt: getDate(bk.fecha_creacion),
        updatedAt: getDate(bk.fecha_actualizacion),
      },
      entity: bk.paciente?.entidad_info?.nombre || '',
      requester: typeof bk.medico_solicitante === 'string' ? bk.medico_solicitante : (bk.medico_solicitante?.nombre || ''),
      status: finalStatus,
      receivedAt,
      deliveredAt: finalDeliveredAt,
      signedAt,  // Nueva: fecha de firma específica
      tests: flatTests,
      pathologist: bk.patologo_asignado?.nombre || '',
      patologo_asignado: bk.patologo_asignado ? {
        codigo: bk.patologo_asignado.codigo || '',
        nombre: bk.patologo_asignado.nombre || '',
        firma: bk.patologo_asignado.firma
      } : undefined,
      notes: bk.observaciones_generales || '',
      servicio: bk.servicio || '',
      // Incorporar prioridad (campo nuevo en backend). Mantenemos compatibilidad aunque el tipo Case aún no lo tenga.
      // @ts-ignore
      priority: (bk as any).prioridad || (bk as any).prioridad_caso || 'Normal',
      // Campo oportunidad para días hábiles al completar
      oportunidad: (bk as any).oportunidad || undefined,
      // Campo entregado_a para registro de entrega
      entregado_a: (bk as any).entregado_a || undefined,
      result: {
        method: Array.isArray(bk.resultado?.metodo) 
          ? bk.resultado.metodo.join(', ') 
          : (bk.resultado?.metodo || ''),
        macro: bk.resultado?.resultado_macro || '',
        micro: bk.resultado?.resultado_micro || '',
        diagnosis: bk.resultado?.diagnostico || '',
        resultDate: getDate(bk.resultado?.fecha_resultado),
        diagnostico_cie10: (bk.resultado as any)?.diagnostico_cie10 || null,
        diagnostico_cieo: (bk.resultado as any)?.diagnostico_cieo || null,
        observaciones: (bk.resultado as any)?.observaciones || '',
      },
      subsamples,
    }
  }

  const filteredCases = computed(() => {
    let list = cases.value

    if (filters.value.searchQuery) {
      const q = normalize(filters.value.searchQuery)
      list = list.filter(c =>
        normalize(c.id).includes(q) ||
        normalize(c.caseCode || '').includes(q) ||
        normalize(c.patient.dni).includes(q) ||
        normalize(c.patient.fullName).includes(q)
      )
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

    // sort
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

  function toggleSelectAll() {
    if (isAllSelected.value) {
      // Deseleccionar todos los de la página actual
      selectedCaseIds.value = selectedCaseIds.value.filter(
        id => !paginatedCases.value.some(c => c.id === id)
      )
    } else {
      // Seleccionar todos los de la página actual
      const newSelected = paginatedCases.value.map(c => c.id)
      selectedCaseIds.value = [...new Set([...selectedCaseIds.value, ...newSelected])]
    }
  }

  function toggleSelect(id: string) {
    // Validar que el ID no esté vacío
    if (!id || id.trim() === '') {
      return
    }
    
    const index = selectedCaseIds.value.indexOf(id)
    if (index === -1) {
      selectedCaseIds.value.push(id)
    } else {
      selectedCaseIds.value.splice(index, 1)
    }
  }

  function sortBy(key: SortKey) {
    if (sortKey.value === key) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = key
      sortOrder.value = 'asc'
    }
  }

  function applyBulkAction(action: string, ids: string[]) {
    cases.value = cases.value.map(c => {
      if (ids.includes(c.id)) {
        let newStatus = action
        if (action === 'en-proceso') newStatus = 'En proceso'
        if (action === 'por-firmar') newStatus = 'Por firmar'
        if (action === 'por-entregar') newStatus = 'Por entregar'
        if (action === 'completado') newStatus = 'Completado'
        if (action === 'requiere-cambios') newStatus = 'Por entregar' // Eliminar estado "Requiere cambios"
        return { ...c, status: newStatus }
      }
      return c
    })
    selectedCaseIds.value = []
  }

  function showDetails(c: Case) {
    selectedCase.value = c
  }

  function closeDetails() {
    selectedCase.value = null
  }

  function validateCase(c: Case) {
    const idx = cases.value.findIndex(x => x.id === c.id)
    if (idx !== -1) cases.value[idx].status = 'Validado'
    if (selectedCase.value?.id === c.id) selectedCase.value.status = 'Validado'
  }

  function markAsCompleted(c: Case) {
    const idx = cases.value.findIndex(x => x.id === c.id)
    if (idx !== -1 && cases.value[idx].status === 'Por firmar') cases.value[idx].status = 'Completado'
    if (selectedCase.value?.id === c.id && selectedCase.value.status === 'Por firmar') selectedCase.value.status = 'Completado'
  }

  function clearFilters() {
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
  

  
  // Listener para detectar cuando se crea un nuevo caso
  const handleCaseCreated = (_event: CustomEvent) => {
    // Recargar la lista de casos para incluir el nuevo caso
    loadCases()
  }
  
  // Watcher para el store de casos
  watch(() => casesStore.needsRefresh, (needsRefresh) => {
    if (needsRefresh) {
      loadCases().then(() => {
        casesStore.markRefreshed()
      })
    }
  })
  
  // Watcher para el timestamp de última actualización
  watch(() => casesStore.lastUpdate, () => {
    // Recargar cuando se actualiza el timestamp
    loadCases()
  })
  
  onMounted(() => {
    loadCases()
    // Agregar listener para eventos de creación de casos
    window.addEventListener('case-created', handleCaseCreated as EventListener)
  })
  
  onUnmounted(() => {
    // Limpiar listener al desmontar el componente
    window.removeEventListener('case-created', handleCaseCreated as EventListener)
  })

  return {
    // state
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
    // derived
    filteredCases,
    paginatedCases,
    totalPages,
    isAllSelected,
    // actions
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
    // utils
    toYYYYMMDD,
    ddmmyyyyToISO,
    getDefaultDateRange,
  }
}


