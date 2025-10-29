import Holidays from 'date-holidays'

const holidaysCache = new Map<number, Set<string>>()

export const formatISODate = (d: Date): string => {
  const y = d.getFullYear()
  const m = String(d.getMonth() + 1).padStart(2, '0')
  const dd = String(d.getDate()).padStart(2, '0')
  return `${y}-${m}-${dd}`
}

export const getColombiaHolidays = (year: number): Set<string> => {
  const cached = holidaysCache.get(year)
  if (cached) return cached
  const hd = new Holidays('CO')
  const arr = (hd.getHolidays(year) || []) as unknown as Array<{ date?: string; start?: string }>
  const set = new Set<string>()
  for (const h of arr) {
    const dateStr = (h.date || (h.start ? String(h.start).slice(0, 10) : '')) || ''
    if (dateStr) set.add(dateStr)
  }
  holidaysCache.set(year, set)
  return set
}

export const getHolidaysForRange = (start: Date, end: Date): Set<string> => {
  const startYear = start.getFullYear()
  const endYear = end.getFullYear()
  const result = new Set<string>()
  for (let y = startYear; y <= endYear; y++) {
    const set = getColombiaHolidays(y)
    set.forEach(d => result.add(d))
  }
  return result
}