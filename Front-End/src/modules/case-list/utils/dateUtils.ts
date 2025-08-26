// Función utilitaria para obtener fechas por defecto
export function getDefaultDateRange() {
  const today = new Date()
  const tomorrow = new Date(today)
  tomorrow.setDate(tomorrow.getDate() + 1) // Día siguiente
  
  const currentYear = today.getFullYear()
  const firstDayOfYear = new Date(currentYear, 0, 1) // 1 de enero del año actual
  
  const formatDate = (date: Date): string => {
    const day = date.getDate().toString().padStart(2, '0')
    const month = (date.getMonth() + 1).toString().padStart(2, '0')
    const year = date.getFullYear()
    return `${day}/${month}/${year}`
  }
  
  return {
    dateFrom: formatDate(firstDayOfYear),
    dateTo: formatDate(tomorrow) // Hasta mañana para incluir casos de hoy
  }
}