/**
 * Utilidades de formateo para el proyecto
 */

export const formatearNumero = (num: number): string => {
  return new Intl.NumberFormat('es-CO').format(num)
}

export const obtenerClasePorcentaje = (porcentaje: number): string => {
  return porcentaje >= 0 
    ? 'bg-green-50 text-green-600 hover:bg-green-100'
    : 'bg-red-50 text-red-600 hover:bg-red-100'
}
