import { ref, computed } from 'vue'
import { complementaryTechniquesListService } from '../services/ctl.service'
import type { ComplementaryTechniqueListItem as TecnicaComplementaria } from '../types/ctl.types'

export function useComplementaryTechniques() {
  const tecnicasComplementarias = ref<TecnicaComplementaria[]>([])
  const isLoading = ref(false)
  const errorCarga = ref<string | null>(null)

  // Keys allowed for sorting in the list component
  type SortableKey = 'codigo' | 'nombre' | 'estado' | 'fechaCreacion' | 'fechaEntrega'
  const ALLOWED_SORT_KEYS: readonly SortableKey[] = ['codigo', 'nombre', 'estado', 'fechaCreacion', 'fechaEntrega']

  const sortKey = ref<SortableKey>('fechaCreacion')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  const paginacion = ref({
    pagina: 1,
    elementosPorPagina: 10,
    total: 0
  })

  const sortedTechniques = computed(() => {
    const data = [...tecnicasComplementarias.value]
    const key = sortKey.value
    return data.sort((a, b) => {
      let av: string | number = ''
      let bv: string | number = ''
      if (key === 'fechaCreacion' || key === 'fechaEntrega') {
        av = a[key] ? new Date(a[key] as string).getTime() : 0
        bv = b[key] ? new Date(b[key] as string).getTime() : 0
      } else {
        av = (a[key] ?? '') as string
        bv = (b[key] ?? '') as string
      }
      if (av < bv) return sortOrder.value === 'asc' ? -1 : 1
      if (av > bv) return sortOrder.value === 'asc' ? 1 : -1
      return 0
    })
  })

  const totalPages = computed(() => {
    const perPage = paginacion.value.elementosPorPagina
    return perPage > 0 ? Math.max(1, Math.ceil(paginacion.value.total / perPage)) : 1
  })

  const tecnicasPaginadas = computed(() => {
    const start = (paginacion.value.pagina - 1) * paginacion.value.elementosPorPagina
    const end = start + paginacion.value.elementosPorPagina
    return sortedTechniques.value.slice(start, end)
  })

  const cargarTecnicas = async () => {
    isLoading.value = true
    errorCarga.value = null
    try {
      const lista = await complementaryTechniquesListService.list()
      tecnicasComplementarias.value = lista as TecnicaComplementaria[]
      paginacion.value.total = tecnicasComplementarias.value.length
      // Reset page if out of range
      if (paginacion.value.pagina > totalPages.value) paginacion.value.pagina = totalPages.value
    } catch (e: any) {
      errorCarga.value = e?.message || 'Error al cargar técnicas complementarias'
    } finally {
      isLoading.value = false
    }
  }

  const ordenarPor = (key: string) => {
    const normalized = ALLOWED_SORT_KEYS.includes(key as SortableKey) ? (key as SortableKey) : 'fechaCreacion'
    if (sortKey.value === normalized) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = normalized
      sortOrder.value = 'asc'
    }
  }

  const formatDate = (iso?: string) => {
    if (!iso) return 'N/A'
    const d = new Date(iso)
    const dd = String(d.getDate()).padStart(2, '0')
    const mm = String(d.getMonth() + 1).padStart(2, '0')
    const yyyy = d.getFullYear()
    return `${dd}/${mm}/${yyyy}`
  }

  const statusClass = (t: TecnicaComplementaria) => {
    switch ((t.estado || '').toLowerCase()) {
      case 'pendiente':
        return 'bg-yellow-100 text-yellow-800 ring-yellow-200'
      case 'entregada':
        return 'bg-green-100 text-green-800 ring-green-200'
      case 'rechazada':
        return 'bg-red-100 text-red-800 ring-red-200'
      default:
        return 'bg-gray-100 text-gray-800 ring-gray-200'
    }
  }

  const cambiarPagina = (pagina: number) => {
    const p = Math.max(1, Math.min(pagina, totalPages.value))
    paginacion.value.pagina = p
  }

  const cambiarElementosPorPagina = (cantidad: number) => {
    paginacion.value.elementosPorPagina = Math.max(1, cantidad)
    // readjust current page bounds
    if (paginacion.value.pagina > totalPages.value) paginacion.value.pagina = totalPages.value
  }

  return {
    tecnicasComplementarias,
    isLoading,
    errorCarga,
    sortKey,
    sortOrder,
    tecnicasPaginadas,
    totalPages,
    paginacion,
    cargarTecnicas,
    ordenarPor,
    formatDate,
    statusClass,
    cambiarPagina,
    cambiarElementosPorPagina
  }
}