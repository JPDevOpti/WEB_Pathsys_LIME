export interface TecnicaComplementaria {
  id: string
  codigo: string
  nombre: string
  descripcion?: string
  estado: string
  fechaCreacion: string
  fechaEntrega?: string | null
}

export type ComplementaryTechniqueListItem = TecnicaComplementaria


