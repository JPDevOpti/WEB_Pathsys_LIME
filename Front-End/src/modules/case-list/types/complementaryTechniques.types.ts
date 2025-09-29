export interface TecnicaComplementaria {
  id: string
  codigo: string
  nombre: string
  descripcion: string
  tipo: string
  categoria: string
  estado: 'En proceso' | 'Por entregar' | 'Completado'
  fechaCreacion: string
  fechaEntrega?: string
}

export interface FiltrosComplementaryTechniques {
  estado?: string
  tipo?: string
  categoria?: string
  busqueda?: string
}

export interface PaginacionComplementaryTechniques {
  pagina: number
  elementosPorPagina: number
  total: number
}

export interface RespuestaComplementaryTechniques {
  tecnicas: TecnicaComplementaria[]
  paginacion: PaginacionComplementaryTechniques
}

export interface CrearTecnicaComplementaria {
  nombre: string
  descripcion: string
  tipo: string
  categoria: string
}

export interface ActualizarTecnicaComplementaria extends Partial<CrearTecnicaComplementaria> {
  id: string
  estado?: 'En proceso' | 'Por entregar' | 'Completado'
  fechaEntrega?: string
}
