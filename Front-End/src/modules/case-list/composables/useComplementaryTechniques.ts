import { ref, computed, watch } from 'vue'
import type { 
  TecnicaComplementaria, 
  FiltrosComplementaryTechniques,
  RespuestaComplementaryTechniques 
} from '../types/complementaryTechniques.types'
import { ComplementaryTechniquesService } from '../services/complementaryTechniques.service'

export function useComplementaryTechniques() {
  const tecnicas = ref<TecnicaComplementaria[]>([])
  const tecnicasComplementarias = ref<TecnicaComplementaria[]>([])
  const isLoading = ref(false)
  const error = ref('')
  const errorCarga = ref('')
  
  const filtros = ref<FiltrosComplementaryTechniques>({})
  const paginacion = ref({
    pagina: 1,
    elementosPorPagina: 10,
    total: 0
  })

  const sortKey = ref('codigo')
  const sortOrder = ref<'asc' | 'desc'>('desc')

  const tecnicasOrdenadas = computed(() => {
    return tecnicas.value.slice().sort((a, b) => {
      const getVal = (tecnica: TecnicaComplementaria) => {
        switch (sortKey.value) {
          case 'codigo': return tecnica.codigo.toLowerCase()
          case 'nombre': return tecnica.nombre.toLowerCase()
          case 'tipo': return tecnica.tipo.toLowerCase()
          case 'categoria': return tecnica.categoria.toLowerCase()
          case 'fechaCreacion': return new Date(tecnica.fechaCreacion).getTime()
          default: return tecnica.estado === 'Completado' ? 3 : tecnica.estado === 'Por entregar' ? 2 : 1
        }
      }
      
      const aVal = getVal(a)
      const bVal = getVal(b)
      
      const result = aVal < bVal ? -1 : aVal > bVal ? 1 : 0
      return sortOrder.value === 'asc' ? result : -result
    })
  })

  const totalPages = computed(() => 
    Math.max(1, Math.ceil(tecnicasOrdenadas.value.length / paginacion.value.elementosPorPagina))
  )

  const tecnicasPaginadas = computed(() => {
    const start = (paginacion.value.pagina - 1) * paginacion.value.elementosPorPagina
    return tecnicasOrdenadas.value.slice(start, start + paginacion.value.elementosPorPagina)
  })

  const cargarTecnicas = async () => {
    isLoading.value = true
    error.value = ''
    
    try {
      // TODO: Replace with actual API call
      await new Promise(resolve => setTimeout(resolve, 1000))
      
      // Mock data for now
      const mockData = [
        {
          id: '1',
          codigo: 'C2025-00001',
          nombre: 'Inmunohistoquímica CD20',
          descripcion: 'Técnica para detección de antígeno CD20 en tejidos linfoides',
          tipo: 'inmunohistoquimica',
          categoria: 'Linfoma',
          estado: 'En proceso' as const,
          fechaCreacion: '2024-01-15',
          fechaEntrega: '2024-01-18'
        },
        {
          id: '2',
          codigo: 'C2025-00002',
          nombre: 'Inmunohistoquímica Ki-67',
          descripcion: 'Técnica para evaluación de proliferación celular',
          tipo: 'inmunohistoquimica',
          categoria: 'Oncología',
          estado: 'Por entregar' as const,
          fechaCreacion: '2024-01-20',
          fechaEntrega: '2024-01-22'
        },
        {
          id: '3',
          codigo: 'C2025-00003',
          nombre: 'PCR para BCR-ABL',
          descripcion: 'Técnica molecular para detección de translocación BCR-ABL',
          tipo: 'molecular',
          categoria: 'Hematología',
          estado: 'Completado' as const,
          fechaCreacion: '2024-02-01',
          fechaEntrega: '2024-02-03'
        },
        {
          id: '4',
          codigo: 'C2025-00004',
          nombre: 'Inmunohistoquímica CD3',
          descripcion: 'Marcador para células T en tejidos linfoides',
          tipo: 'inmunohistoquimica',
          categoria: 'Linfoma',
          estado: 'En proceso' as const,
          fechaCreacion: '2024-01-25',
          fechaEntrega: '2024-01-28'
        },
        {
          id: '5',
          codigo: 'C2025-00005',
          nombre: 'Inmunohistoquímica CD79a',
          descripcion: 'Marcador para células B en tejidos linfoides',
          tipo: 'inmunohistoquimica',
          categoria: 'Linfoma',
          estado: 'Por entregar' as const,
          fechaCreacion: '2024-01-30',
          fechaEntrega: '2024-02-02'
        },
        {
          id: '6',
          codigo: 'C2025-00006',
          nombre: 'FISH para HER2',
          descripcion: 'Hibridación in situ fluorescente para amplificación de HER2',
          tipo: 'molecular',
          categoria: 'Oncología',
          estado: 'Completado' as const,
          fechaCreacion: '2024-02-05',
          fechaEntrega: '2024-02-08'
        },
        {
          id: '7',
          codigo: 'C2025-00007',
          nombre: 'Inmunohistoquímica p53',
          descripcion: 'Marcador tumoral para mutaciones en gen p53',
          tipo: 'inmunohistoquimica',
          categoria: 'Oncología',
          estado: 'En proceso' as const,
          fechaCreacion: '2024-02-10',
          fechaEntrega: '2024-02-13'
        },
        {
          id: '8',
          codigo: 'C2025-00008',
          nombre: 'PCR para JAK2 V617F',
          descripcion: 'Detección de mutación V617F en gen JAK2',
          tipo: 'molecular',
          categoria: 'Hematología',
          estado: 'Por entregar' as const,
          fechaCreacion: '2024-02-12',
          fechaEntrega: '2024-02-15'
        },
        {
          id: '9',
          codigo: 'C2025-00009',
          nombre: 'Inmunohistoquímica CD68',
          descripcion: 'Marcador para macrófagos y células del sistema mononuclear fagocítico',
          tipo: 'inmunohistoquimica',
          categoria: 'Inflamación',
          estado: 'Completado' as const,
          fechaCreacion: '2024-02-15',
          fechaEntrega: '2024-02-18'
        },
        {
          id: '10',
          codigo: 'C2025-00010',
          nombre: 'FISH para ALK',
          descripcion: 'Hibridación in situ fluorescente para rearreglo de ALK',
          tipo: 'molecular',
          categoria: 'Oncología',
          estado: 'En proceso' as const,
          fechaCreacion: '2024-02-18',
          fechaEntrega: '2024-02-21'
        },
        {
          id: '11',
          codigo: 'C2025-00011',
          nombre: 'Inmunohistoquímica CK7',
          descripcion: 'Citoqueratina 7 para diferenciación epitelial',
          tipo: 'inmunohistoquimica',
          categoria: 'Oncología',
          estado: 'Por entregar' as const,
          fechaCreacion: '2024-02-20',
          fechaEntrega: '2024-02-23'
        },
        {
          id: '12',
          codigo: 'C2025-00012',
          nombre: 'PCR para FLT3-ITD',
          descripcion: 'Detección de mutación ITD en gen FLT3',
          tipo: 'molecular',
          categoria: 'Hematología',
          estado: 'Completado' as const,
          fechaCreacion: '2024-02-22',
          fechaEntrega: '2024-02-25'
        },
        {
          id: '13',
          codigo: 'C2025-00013',
          nombre: 'Inmunohistoquímica CD117',
          descripcion: 'Marcador para células c-kit positivas',
          tipo: 'inmunohistoquimica',
          categoria: 'Oncología',
          estado: 'En proceso' as const,
          fechaCreacion: '2024-02-25',
          fechaEntrega: '2024-02-28'
        },
        {
          id: '14',
          codigo: 'C2025-00014',
          nombre: 'FISH para C-MYC',
          descripcion: 'Hibridación in situ fluorescente para amplificación de C-MYC',
          tipo: 'molecular',
          categoria: 'Linfoma',
          estado: 'Por entregar' as const,
          fechaCreacion: '2024-02-28',
          fechaEntrega: '2024-03-03'
        },
        {
          id: '15',
          codigo: 'C2025-00015',
          nombre: 'Inmunohistoquímica TTF-1',
          descripcion: 'Factor de transcripción tiroideo 1 para diagnóstico pulmonar',
          tipo: 'inmunohistoquimica',
          categoria: 'Oncología',
          estado: 'Completado' as const,
          fechaCreacion: '2024-03-01',
          fechaEntrega: '2024-03-04'
        }
      ]
      
      tecnicas.value = mockData
      tecnicasComplementarias.value = mockData
      paginacion.value.total = mockData.length
    } catch (err: any) {
      error.value = err.message || 'Error al cargar las técnicas complementarias'
      errorCarga.value = err.message || 'Error al cargar las técnicas complementarias'
    } finally {
      isLoading.value = false
    }
  }

  const aplicarFiltros = (nuevosFiltros: FiltrosComplementaryTechniques) => {
    filtros.value = { ...filtros.value, ...nuevosFiltros }
    paginacion.value.pagina = 1
    cargarTecnicas()
  }

  const limpiarFiltros = () => {
    filtros.value = {}
    paginacion.value.pagina = 1
    cargarTecnicas()
  }

  const cambiarPagina = (pagina: number) => {
    paginacion.value.pagina = pagina
  }

  const cambiarElementosPorPagina = (elementos: number) => {
    paginacion.value.elementosPorPagina = elementos
    paginacion.value.pagina = 1
  }

  const ordenarPor = (campo: string) => {
    if (sortKey.value === campo) {
      sortOrder.value = sortOrder.value === 'asc' ? 'desc' : 'asc'
    } else {
      sortKey.value = campo
      sortOrder.value = 'asc'
    }
  }

  const formatDate = (dateString: string) => {
    if (!dateString) return 'N/A'
    return new Date(dateString).toLocaleDateString('es-ES', { 
      day: '2-digit', 
      month: '2-digit', 
      year: 'numeric' 
    })
  }

  const statusClass = (tecnica: TecnicaComplementaria) => {
    switch (tecnica.estado) {
      case 'En proceso':
        return 'bg-blue-50 text-blue-700'
      case 'Por entregar':
        return 'bg-yellow-50 text-yellow-700'
      case 'Completado':
        return 'bg-green-50 text-green-700'
      default:
        return 'bg-gray-50 text-gray-700'
    }
  }

  return {
    tecnicas,
    tecnicasComplementarias,
    isLoading,
    error,
    errorCarga,
    filtros,
    paginacion,
    sortKey,
    sortOrder,
    tecnicasOrdenadas,
    tecnicasPaginadas,
    totalPages,
    cargarTecnicas,
    aplicarFiltros,
    limpiarFiltros,
    cambiarPagina,
    cambiarElementosPorPagina,
    ordenarPor,
    formatDate,
    statusClass
  }
}
